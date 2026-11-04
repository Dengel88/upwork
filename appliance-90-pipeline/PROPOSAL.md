Live interactive 90-SKU pipeline prototype I built for your brief:
https://dengel88.github.io/upwork/appliance-90-pipeline/

Hi,

The main challenge with generating 4 to 6 lifestyle photos and a 10-second video across 90 household appliances is keeping the physical product details intact. If you run raw appliance photos through standard image-to-video or diffusion models, rotary knobs warp, LED displays blur, and printed logos shift as the camera moves.

I put together an interactive prototype at the link above to show how I solve this using an automated ComfyUI + n8n + Kling 3.0 workflow.

How our pipeline keeps every control panel, logo, and finish accurate across 90 products:

1. Exact product mask separation (SAM2 + BiRefNet): We isolate the appliance body, control dials, displays, and brand badges into locked alpha masks before generating the kitchen or utility room scene.
2. Geometry-locked environments (FLUX.1-dev + Dual ControlNet Depth/Canny): We generate realistic UK/European home interiors around the exact product perspective so proportions never change.
3. Natural relighting (IC-Light): Countertop shadows and reflections wrap onto stainless steel, glass, and matte plastic while preserving the real product color (CIE Delta-E under 1.2).
4. Deterministic pixel-lock composite pass: Before final export, our script composites the original sharp control-panel text, buttons, and logo back over the relit chassis. AI never overwrites your brand markings.
5. 10-second camera motion (Kling 3.0 Pro / Seedance + planar tracking): Smooth camera pushes and subtle background motion (steam, natural window light) while keeping the appliance geometry locked across all frames.

Fixed-Price Proposal: $7,800 total ($86.67 per SKU for all 90 products)

Because our n8n + ComfyUI batch workflow handles masking, relighting, and QA checks automatically, I can deliver all 90 products (450+ 4K lifestyle images and 90 x 10s videos) within your 2-month timeline for $7,800 fixed price, broken into clear milestones:

- Milestone 1 (Paid 1-SKU Pilot - $75, Days 1-3): Send 1 appliance photo. I will deliver 5 lifestyle images + 1 x 10s video so you can check the sharpness of the controls, logos, and lighting before starting the full batch.
- Milestone 2 (Batch 1: 22 products - $1,925, Days 4-17): 110 lifestyle images + 22 x 10s videos.
- Milestone 3 (Batch 2: 23 products - $1,950, Days 18-31): 115 lifestyle images + 23 x 10s videos.
- Milestone 4 (Batch 3: 22 products - $1,925, Days 32-45): 110 lifestyle images + 22 x 10s videos.
- Milestone 5 (Batch 4: 22 products - $1,925, Days 46-60): 110 lifestyle images + 22 x 10s videos + ComfyUI/n8n workflow files.

Feel free to send over one product photo and I can run a test sample for you right away.

Best,
Ayman
