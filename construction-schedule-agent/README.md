# AI Construction Schedule Monitoring Agent (Deterministic CPM + Executive PM Reporter)

**Live Working POC Web Application:** [https://dengel88.github.io/upwork/construction-schedule-agent/](https://dengel88.github.io/upwork/construction-schedule-agent/)  
**Architect:** Ayman K. | Synndicate AI (*Lead AI Systems Architect*)

---

## Architecture Philosophy: Zero LLM Math, 100% Deterministic Schedule Logic

Relying on an LLM to subtract dates or calculate Critical Path Total Float leads to hallucinated variances. Our architecture strictly separates **Deterministic Schedule Math** from **Executive PM Narrative Generation**:

1. **Layer 1 — Ingestion & Data Hygiene Validator (Python / JS / Power Automate):**
   Parses exported Baseline and Current schedule updates from Primavera P6 (`.xer`/`.xlsx`), MS Project (`.xml`/`.xlsx`), or CSV. Automatically flags missing predecessor links (open-ended activities), out-of-sequence logic (successor starting before predecessor finishes), missing Total Float values, and past-due forecast dates prior to the Data Date.
2. **Layer 2 — 100% Deterministic CPM & Variance Engine (`schedule_cpm_engine.py`):**
   Computes exact Start Variance (days), Finish Variance (days), Duration Compression/Expansion, Total Float erosion (`Float <= 0` Critical Path tracking), and 30-Day Lookahead Milestone exposure using configurable user thresholds (`> 3 days`, `> 5 days`, etc.).
3. **Layer 3 — Grounded Executive PM Report Generator (Copilot Studio / Azure OpenAI / Claude):**
   Receives the verified JSON variance payload and formats the **7-Section Executive Construction Schedule Report** (Overall Schedule Health, Baseline vs. Current Comparison, Delayed Activities, 30-Day Lookahead Risks, Critical Path Shifts, Top 5 Project Risks, and Contractor Clarification Questions) with 1-click **Excel/CSV Export** and **Print/PDF Report**.

---

## Repository Structure

- `index.html` — Complete interactive **AI Construction Schedule Monitoring Agent** web app pre-loaded with a realistic 20-activity Commercial Medical Tower dataset, custom CSV uploader, interactive delay threshold controls, deterministic variance table, and 7-section Executive PM Report with Excel & PDF export.
- `schedule_cpm_engine.py` — Standalone Python deterministic schedule variance, critical path, and data hygiene engine.
- `test_schedule_agent.py` — Unit test suite verifying variance math, 30-day lookahead filtering, and open-logic detection.
- `PROPOSAL.md` — Tailored Fixed-Price POC proposal (`$450` Turnkey POC Milestone) answering all 5 client application questions directly.

## Running Unit Tests

```bash
python -m unittest test_schedule_agent.py -v
python schedule_cpm_engine.py
```
