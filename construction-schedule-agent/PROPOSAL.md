Working prototype of your Construction Schedule Monitoring Agent (pre-loaded with a 20-activity schedule + CSV upload):
https://dengel88.github.io/upwork/construction-schedule-agent/

Hi,

I built a working prototype of your Construction Schedule Monitoring Agent so you can test the deterministic schedule math and the executive report output directly in your browser:
https://dengel88.github.io/upwork/construction-schedule-agent/

You can switch delay thresholds (3 days, 5 days, critical path float <= 0), inspect the baseline vs. updated variance table, and export the report to Excel (.csv) or PDF.

Answers to your application questions:

1. Have you built a Microsoft Copilot Studio agent that integrates with Power Automate?
Yes. In Microsoft 365 environments, I use Copilot Studio as the chat/upload interface and trigger Power Automate flows that pass uploaded files from SharePoint/OneDrive to a deterministic script (Office Scripts or an Azure Function in Python) before returning the structured JSON summary back to Copilot Studio.

2. Have you developed AI workflows that process Excel data and generate structured reports?
Yes. Most of our reporting agents follow the same rule you highlighted in your brief: deterministic code handles all Excel parsing, date comparisons, and variance math first, and the LLM only writes the narrative commentary from that verified JSON. The output is then formatted into clean Excel, Word, or PDF reports.

3. How would you identify critical path changes without relying on an LLM for calculations?
In our Python/TypeScript schedule engine (which you can inspect in the demo and GitHub repo: https://github.com/Dengel88/upwork/tree/main/construction-schedule-agent), we parse planned/updated start and finish dates, durations, predecessor links, and Total Float directly from the schedule export.
- Any activity where `Updated_Total_Float <= 0` (or where float drops below your near-critical threshold, e.g., <= 3 days) is flagged deterministically.
- We compare the Baseline Critical Path IDs against the Updated Critical Path IDs to detect path shifts, float erosion (`Float_Delta = Updated_Float - Baseline_Float`), and downstream duration compression (when a contractor shortens a later task's duration to hide an upstream delay).
- We also run deterministic schedule-hygiene checks for missing predecessors (open ends), out-of-sequence progress, and invalid forecast dates.

4. Which LLM and Microsoft technologies would you recommend for this project, and why?
- For calculations: Python (via Azure Functions) or TypeScript Office Scripts triggered by Power Automate. Python with `pandas`/`openpyxl` is slightly more flexible if you plan to support complex Primavera P6 / MS Project Excel exports with multi-predecessor strings like `A1020FS+5d`.
- For the agent & LLM: Microsoft Copilot Studio + Power Automate connected to Azure OpenAI (GPT-4o) or Claude 3.5 Sonnet. Everything stays inside your Microsoft tenant, and the LLM receives a strict JSON schema so the 7 report sections are always consistent.
- If you want something even simpler and cheaper to maintain than Copilot Studio licensing, we can also host the standalone web app shown in the demo link above inside your private Azure environment.

5. Can you demonstrate a previously developed working AI agent?
Yes, please test the live prototype built specifically for your scope here:
https://dengel88.github.io/upwork/construction-schedule-agent/

Pricing & Timeline (Fixed-Price POC: $450, 5 days)
Since the core deterministic variance engine and 7-section report generator are already working in the prototype above, I propose a $450 fixed-price POC split into 3 simple milestones ($150 each: 1. calibrating the Excel parser to your sample schedules, 2. connecting Power Automate / Copilot Studio and report exports, 3. testing and handover session).

Best,
Ayman
