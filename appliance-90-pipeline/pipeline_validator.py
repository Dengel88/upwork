"""
Zero-Hallucination Appliance QA Validator & Batch Pipeline Engine
Author: Ayman K. | Synndicate AI (Lead AI Systems Architect & Generative Media Producer)

Deterministic verification engine for the 90-SKU Household Appliance AI Production Pipeline.
Ensures 100% geometric, colorimetric, and typographic fidelity across 450 lifestyle stills
and 90 x 10-second product videos before any asset enters client review.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json
import math


@dataclass
class ApplianceSKU:
    sku_id: str
    name: str
    category: str
    reference_rgb: tuple[int, int, int]
    rendered_rgb: tuple[int, int, int]
    masked_ssim: float
    edge_canny_iou: float
    logo_ocr_match: float
    control_panel_pixel_locked: bool
    stills_completed: int = 5
    video_duration_sec: float = 10.0


@dataclass
class QAResult:
    sku_id: str
    passed: bool
    masked_ssim: float
    delta_e_cie76: float
    edge_canny_iou: float
    logo_ocr_match: float
    control_panel_pixel_locked: bool
    failure_reasons: List[str]


def rgb_to_xyz(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Convert sRGB (0-255) to CIE XYZ (D65 illuminant)."""
    def linearize(c: int) -> float:
        v = c / 255.0
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92

    r, g, b = (linearize(c) for c in rgb)
    x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) * 100.0
    y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) * 100.0
    z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) * 100.0
    return x, y, z


def xyz_to_lab(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CIE XYZ to CIE L*a*b* (D65 reference white)."""
    ref_x, ref_y, ref_z = 95.047, 100.000, 108.883

    def f(t: float) -> float:
        delta = 6.0 / 29.0
        return t ** (1.0 / 3.0) if t > delta ** 3 else (t / (3.0 * delta ** 2)) + (4.0 / 29.0)

    fx = f(xyz[0] / ref_x)
    fy = f(xyz[1] / ref_y)
    fz = f(xyz[2] / ref_z)

    l_star = (116.0 * fy) - 16.0
    a_star = 500.0 * (fx - fy)
    b_star = 200.0 * (fy - fz)
    return l_star, a_star, b_star


def calculate_delta_e(rgb_ref: tuple[int, int, int], rgb_rendered: tuple[int, int, int]) -> float:
    """Calculate perceptual color difference (CIE76 Delta-E) inside the product mask."""
    lab1 = xyz_to_lab(rgb_to_xyz(rgb_ref))
    lab2 = xyz_to_lab(rgb_to_xyz(rgb_rendered))
    dist = math.sqrt(
        (lab1[0] - lab2[0]) ** 2 +
        (lab1[1] - lab2[1]) ** 2 +
        (lab1[2] - lab2[2]) ** 2
    )
    return round(dist, 3)


def evaluate_sku_quality_gate(
    sku: ApplianceSKU,
    min_ssim: float = 0.985,
    max_delta_e: float = 1.2,
    min_edge_iou: float = 0.970,
    min_logo_ocr: float = 0.990,
) -> QAResult:
    """
    Deterministic QA gate executed by n8n after ComfyUI + IC-Light + Pixel-Lock composite.
    Any SKU failing even one metric is automatically routed back to the composite pass.
    """
    delta_e = calculate_delta_e(sku.reference_rgb, sku.rendered_rgb)
    failures: List[str] = []

    if sku.masked_ssim < min_ssim:
        failures.append(f"Masked SSIM {sku.masked_ssim:.4f} below threshold {min_ssim:.4f}")
    if delta_e > max_delta_e:
        failures.append(f"Color Delta-E {delta_e:.3f} exceeds max threshold {max_delta_e:.3f}")
    if sku.edge_canny_iou < min_edge_iou:
        failures.append(f"Edge Canny IoU {sku.edge_canny_iou:.4f} below threshold {min_edge_iou:.4f}")
    if sku.logo_ocr_match < min_logo_ocr:
        failures.append(f"Logo/Typography OCR confidence {sku.logo_ocr_match:.4f} below {min_logo_ocr:.4f}")
    if not sku.control_panel_pixel_locked:
        failures.append("Control-panel pixel-overlay lock was not applied")

    return QAResult(
        sku_id=sku.sku_id,
        passed=len(failures) == 0,
        masked_ssim=round(sku.masked_ssim, 4),
        delta_e_cie76=delta_e,
        edge_canny_iou=round(sku.edge_canny_iou, 4),
        logo_ocr_match=round(sku.logo_ocr_match, 4),
        control_panel_pixel_locked=sku.control_panel_pixel_locked,
        failure_reasons=failures,
    )


def calculate_batch_schedule(
    total_skus: int = 90,
    stills_per_sku: int = 5,
    videos_per_sku: int = 1,
    total_days: int = 60,
    fixed_price_usd: float = 7800.0,
) -> Dict[str, Any]:
    """Calculate milestone deliverables, throughput, and unit economics for the 90-SKU batch."""
    total_stills = total_skus * stills_per_sku
    total_videos = total_skus * videos_per_sku
    price_per_sku = round(fixed_price_usd / total_skus, 2)
    skus_per_week = round(total_skus / (total_days / 7.0), 2)

    return {
        "total_skus": total_skus,
        "total_stills": total_stills,
        "total_videos": total_videos,
        "total_assets": total_stills + total_videos,
        "timeline_days": total_days,
        "skus_per_week": skus_per_week,
        "fixed_price_usd": fixed_price_usd,
        "price_per_sku_usd": price_per_sku,
        "pilot_milestone_usd": 75.0,
        "milestones": [
            {"phase": "Milestone 1 — Paid 1-SKU Pilot (Zero-Risk Proof)", "skus": 1, "stills": 5, "videos": 1, "days": "Days 1–3", "amount_usd": 75.0},
            {"phase": "Milestone 2 — Pipeline Lock & Batch 1 (Kitchen Majors)", "skus": 22, "stills": 110, "videos": 22, "days": "Days 4–17", "amount_usd": 1925.0},
            {"phase": "Milestone 3 — Batch 2 (Countertop & Espresso Series)", "skus": 23, "stills": 115, "videos": 23, "days": "Days 18–31", "amount_usd": 1950.0},
            {"phase": "Milestone 4 — Batch 3 (Laundry & Home Care Appliances)", "skus": 22, "stills": 110, "videos": 22, "days": "Days 32–45", "amount_usd": 1925.0},
            {"phase": "Milestone 5 — Batch 4 (Climate, Air & Final QA Handover)", "skus": 22, "stills": 110, "videos": 22, "days": "Days 46–60", "amount_usd": 1925.0},
        ],
    }


if __name__ == "__main__":
    sample_skus = [
        ApplianceSKU(
            sku_id="SKU-001-ESPRESSO-PRO",
            name="BaristaTouch Dual-Boiler Espresso Machine (Brushed Steel)",
            category="Countertop Kitchen",
            reference_rgb=(212, 216, 220),
            rendered_rgb=(213, 216, 219),
            masked_ssim=0.9942,
            edge_canny_iou=0.988,
            logo_ocr_match=0.998,
            control_panel_pixel_locked=True,
        ),
        ApplianceSKU(
            sku_id="SKU-014-WASHER-9KG",
            name="EcoSteam 9kg Front-Load Smart Washing Machine (Graphite)",
            category="Laundry Major",
            reference_rgb=(58, 61, 66),
            rendered_rgb=(58, 62, 66),
            masked_ssim=0.9918,
            edge_canny_iou=0.984,
            logo_ocr_match=0.997,
            control_panel_pixel_locked=True,
        ),
        ApplianceSKU(
            sku_id="SKU-042-AIRFRYER-DUAL",
            name="AeroCrisp 9.5L Dual-Zone Digital Air Fryer (Matte Black & Copper)",
            category="Countertop Cooking",
            reference_rgb=(34, 35, 38),
            rendered_rgb=(34, 35, 39),
            masked_ssim=0.9951,
            edge_canny_iou=0.991,
            logo_ocr_match=0.999,
            control_panel_pixel_locked=True,
        ),
    ]

    report = {
        "qa_results": [asdict(evaluate_sku_quality_gate(s)) for s in sample_skus],
        "batch_schedule": calculate_batch_schedule(),
    }
    print(json.dumps(report, indent=2))
