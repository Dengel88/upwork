# Zero-Hallucination 90-Appliance AI Production Control Center

**Live Interactive Demo:** [https://dengel88.github.io/upwork/appliance-90-pipeline/](https://dengel88.github.io/upwork/appliance-90-pipeline/)  
**Architect:** Ayman K. | Synndicate AI (*Lead AI Systems Architect & Generative Media Producer*)

---

## Executive Overview

Standard prompt-only image/video generation (raw Midjourney or unmasked image-to-video) fails on household appliances: it melts rotary dials, garbles LED display digits, alters stainless-steel/matte finishes, and warps brand logos.

This repository powers our **Zero-Hallucination Hybrid ComfyUI + IC-Light + n8n Batch Production Pipeline** engineered specifically for **90 Household Appliance SKUs** (delivering **450+ 4K lifestyle images** and **90 × 10-second 1080p/4K commercial videos** within a structured 60-day schedule).

### Core Technical Architecture (5-Stage Pixel-Lock Pipeline)

1. **Sub-Pixel Alpha Segmentation (`SAM2 + BiRefNet 2048px`)**: Separates the product chassis, glass panels, physical rotary knobs, digital LED displays, and brand badges into deterministic alpha layers.
2. **3D Geometry Lock (`ControlNet Depth-Anything-V2 + Canny Pro`)**: Generates bespoke UK/European modern kitchen, utility room, and architectural studio environments around the product without altering its silhouette by a single pixel.
3. **Physically Based Relighting (`IC-Light + HDRI Specular Reflection Pass`)**: Wraps natural window daylight, warm under-cabinet LEDs, and countertop reflections onto brushed steel, chrome, and matte plastic surfaces while locking the true Pantone/sRGB base albedo (`Delta-E < 1.2`).
4. **Deterministic Pixel-Overlay Composite Pass**: Re-projects the original sharp CAD/studio typography, silkscreened control labels, LED icons, and brand badges at native 4K resolution (`Masked SSIM >= 0.985`).
5. **10-Second Hero Video Generation (`Kling 3.0 Pro / Seedance + 3D Planar Track Lock`)**: Generates smooth orbital camera motion and subtle environmental life (steam wisps, sunlight shifts, water droplets) while rigid-body locking the appliance geometry.

---

## Repository Structure

- `index.html` — Zero-build interactive **90-Appliance AI Production Control Center** (SKU Geometry Lock Inspector, Automated SSIM/Delta-E Quality Gate Calculator, 60-Day Batch Milestone Tracker, and ComfyUI/n8n JSON Workflow Exporter).
- `pipeline_validator.py` — Deterministic Python QA engine calculating masked SSIM, CIE76 Color `Delta-E`, Canny Edge IoU, and 90-SKU milestone unit economics.
- `comfy_n8n_workflow.json` — Exportable n8n + ComfyUI API batch orchestration schema.
- `test_pipeline_validator.py` — Automated unit test suite verifying color accuracy gates and 90-SKU milestone math.
- `PROPOSAL.md` — Tailored fixed-price milestone proposal (`$7,800` total / `$86.67` per SKU, starting with a `$75` 1-SKU Paid Pilot).

## Running Automated Verification

```bash
python -m unittest test_pipeline_validator.py -v
python pipeline_validator.py
```
