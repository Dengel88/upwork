"""Выравнивание скорости камеры (time remap) по оптическому потоку.

python retime.py OUT.mp4 W H TARGET_SEC clip1.mp4 clip2.mp4 ...
Клипы — с высокой частотой кадров (после FPS Boost), стыкуются встык (общие ключевые кадры).
Время в выходе распределяется пропорционально смеси «как было» и «постоянная скорость камеры»,
поэтому паузы на стыках сжимаются, быстрые участки слегка растягиваются.
"""
import subprocess, sys, json
import cv2, numpy as np

out, W, H, T = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
clips = sys.argv[5:]
OUT_FPS = 24
A = 0.8            # доля «постоянной скорости» в распределении времени
MAX_UP, MAX_DOWN = 8.0, 1.0   # макс. ускорение / замедление (1.0 = без замедления, интерполяция не нужна)
HEAD, TAIL = 0.25, 0.7        # сек в начале/конце, где темп не трогаем (мягкий старт и финальная пауза)

def frames(path):
    cap = cv2.VideoCapture(path)
    while True:
        ok, f = cap.read()
        if not ok: break
        yield f
    cap.release()

# 1) поток по всем кадрам подряд (стык: первый кадр следующего клипа = последний предыдущего -> пропускаем дубль)
fps_s = cv2.VideoCapture(clips[0]).get(cv2.CAP_PROP_FPS)
flow, prev, n = [], None, 0
for ci, c in enumerate(clips):
    for j, f in enumerate(frames(c)):
        if ci > 0 and j == 0:
            continue
        g = cv2.cvtColor(cv2.resize(f, (384, 216)), cv2.COLOR_BGR2GRAY)
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 21, 3, 5, 1.2, 0)
            mag = np.linalg.norm(fl, axis=2)
            gx, gy = cv2.Sobel(prev, cv2.CV_32F, 1, 0), cv2.Sobel(prev, cv2.CV_32F, 0, 1)
            edge = np.hypot(gx, gy) > 40          # только текстурные пиксели (корпус, кромки), не серый фон
            flow.append(float(mag[edge].mean()) if edge.sum() > 200 else float(np.median(mag)))
        prev = g; n += 1
flow = np.array(flow)
flow = np.convolve(flow, np.ones(5) / 5, mode="same")  # сглаживание
m = flow.mean()
cost = (1 - A) + A * flow / m                        # «время» на каждый исходный интервал
cost = np.clip(cost, 1 / MAX_UP, MAX_DOWN)
head, tail = int(HEAD * fps_s), int(TAIL * fps_s)
cost[:head] = np.maximum(cost[:head], 1.0)
cost[-tail:] = 1.0
# защищённые участки (сек исходника): PROTECT="9.0-10.4:1.0,12.7-13.5:0.6" — темп не быстрее заданного
import os
for spec in filter(None, os.environ.get("PROTECT", "").split(",")):
    rng, floor = spec.split(":"); a, b = map(float, rng.split("-"))
    i0, i1 = int(a * fps_s), int(b * fps_s)
    cost[i0:i1] = np.maximum(cost[i0:i1], float(floor))
# ускоряемые участки: FAST="15.3-15.8:0.4" — темп не медленнее заданного (проскочить проблемную фазу)
for spec in filter(None, os.environ.get("FAST", "").split(",")):
    rng, ceil_ = spec.split(":"); a, b = map(float, rng.split("-"))
    i0, i1 = int(a * fps_s), int(b * fps_s)
    cost[i0:i1] = np.minimum(cost[i0:i1], float(ceil_))
cost = np.convolve(cost, np.ones(7) / 7, mode="same")
C = np.concatenate([[0], np.cumsum(cost)])
if T <= 0:                      # естественная длительность после сжатия пауз
    T = C[-1] / fps_s
C = C / C[-1] * T
# 2) для каждого выходного кадра — дробная позиция в исходнике (без выбрасывания кадров -> без дёрганья)
nout = int(round(T * OUT_FPS))
pos = np.interp(np.arange(nout) / OUT_FPS, C, np.arange(n))   # C[i] — время исходного кадра i
pos = np.clip(pos, 0, n - 1)
sp = np.diff(pos)
print(json.dumps({"src_frames": n, "src_fps": fps_s, "out_frames": nout, "T": round(T, 3),
                  "speed_min": round(float(sp.min()), 2), "speed_max": round(float(sp.max()), 2)}))
np.save(out + ".pos.npy", pos)
# 3) запись: смешивание двух соседних кадров по дробной части (ускорение только на медленных участках -> двоения нет)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                        "-s", f"{W}x{H}", "-r", str(OUT_FPS), "-i", "-", "-an", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                       stdin=subprocess.PIPE)
def all_frames():
    for ci, c in enumerate(clips):
        for j, f in enumerate(frames(c)):
            if ci > 0 and j == 0:
                continue
            if (f.shape[1], f.shape[0]) != (W, H):
                f = cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA)
            yield f
_fcache = {}
def flow_interp(a, b, fr, key):
    """Промежуточный кадр по оптическому потоку (без двоения контуров, как при простом смешивании)."""
    if key not in _fcache:
        _fcache.clear()
        sw = 960; sh = int(H * sw / W)
        ga = cv2.cvtColor(cv2.resize(a, (sw, sh), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        gb = cv2.cvtColor(cv2.resize(b, (sw, sh), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        f_ab = cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 4, 25, 4, 5, 1.2, 0)
        f_ba = cv2.calcOpticalFlowFarneback(gb, ga, None, 0.5, 4, 25, 4, 5, 1.2, 0)
        sc = W / sw
        up = lambda f: cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR) * sc
        _fcache[key] = (up(f_ab), up(f_ba))
    f_ab, f_ba = _fcache[key]
    fr = np.float32(fr)
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    # пиксель промежуточного кадра: из a назад на fr*поток(a->b), из b назад на (1-fr)*поток(b->a)
    wa = cv2.remap(a, gx - fr * f_ab[..., 0], gy - fr * f_ab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.remap(b, gx - (1 - fr) * f_ba[..., 0], gy - (1 - fr) * f_ba[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(wa, 1 - fr, wb, fr, 0)

src = all_frames(); gi = 0; cur = next(src); nxt = next(src, None); k = 0
for p in pos:
    i = int(np.floor(p)); fr = p - i
    while gi < i and nxt is not None:
        cur, nxt = nxt, next(src, None); gi += 1
    if nxt is None or fr < 0.08:
        img = cur
    elif fr > 0.92:
        img = nxt
    else:
        img = flow_interp(cur, nxt, fr, gi)
    # цифровой наезд на деталь по времени ИСХОДНИКА: DZOOM="8.0-14.0:0.10:0.40:0.35" — масштаб 1→1+amt→1 (синус), центр в долях кадра
    dz = os.environ.get("DZOOM")
    if dz:
        rng, amt, cx, cy = dz.split(":"); a0, a1 = map(float, rng.split("-"))
        ts = p / fps_s
        if a0 < ts < a1:
            u = (ts - a0) / (a1 - a0)
            s = 1 + float(amt) * np.sin(np.pi * u) ** 2
            M = cv2.getRotationMatrix2D((W * float(cx), H * float(cy)), 0, s)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    # финальный дрейф камеры: END_DRIFT="1.6:0.03" — последние 1.6 с лёгкий наезд до +3% (без мёртвой паузы)
    ed = os.environ.get("END_DRIFT")
    if ed:
        dur, amt = map(float, ed.split(":"))
        t = k / OUT_FPS; t0 = T - dur
        if t > t0:
            u = min(1.0, (t - t0) / dur); u = u * u * (3 - 2 * u)
            s = 1 + amt * u
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4)
    enc.stdin.write(img.tobytes()); k += 1
enc.stdin.close(); enc.wait()
print("written", k, "frames")
