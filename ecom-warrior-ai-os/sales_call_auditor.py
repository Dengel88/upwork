"""
Ecom Warrior Academy — AI Sales Call Intelligence & GoHighLevel Automation Engine
Author: Ayman K. | Synndicate AI (Lead AI Systems Architect)
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class ObjectionEvent:
    category: str  # "price", "spouse_partner", "time_bandwidth", "skepticism"
    quote: str
    resolved_by_closer: bool
    coaching_tip: str


@dataclass
class CallAuditResult:
    call_id: str
    prospect_name: str
    closer_name: str
    overall_score: int
    discovery_depth_score: int
    objection_handling_score: int
    urgency_framing_score: int
    closer_talk_ratio_pct: float
    detected_objections: List[ObjectionEvent] = field(default_factory=list)
    missed_buying_signals: List[str] = field(default_factory=list)
    recommended_ghl_stage: str = "Follow-Up - Nurture"
    ghl_webhook_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


OBJECTION_PATTERNS = {
    "price": [
        r"expensive",
        r"afford",
        r"capital",
        r"credit card",
        r"\$\d+",
        r"investment is high",
        r"cash flow",
    ],
    "spouse_partner": [
        r"wife",
        r"husband",
        r"partner",
        r"spouse",
        r"talk to my",
        r"run it by",
    ],
    "time_bandwidth": [
        r"busy",
        r"full-time job",
        r"no time",
        r"hours a week",
        r"kids",
        r"schedule",
    ],
    "skepticism": [
        r"tried dropshipping",
        r"burned before",
        r"saturated",
        r"does this still work in australia",
        r"guarantee",
    ],
}

BUYING_SIGNAL_PATTERNS = [
    r"how fast can i launch",
    r"what happens after i enroll",
    r"do i get 1-on-1",
    r"can i pay in installments",
    r"which mentor",
    r"australian suppliers",
]


def parse_speaker_turns(transcript: str) -> List[Dict[str, str]]:
    """Splits a transcript formatted as 'Closer: ...' / 'Prospect: ...' into structured turns."""
    turns: List[Dict[str, str]] = []
    for raw_line in transcript.strip().splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        speaker, text = line.split(":", 1)
        role = "closer" if speaker.strip().lower() in ("closer", "rep", "advisor") else "prospect"
        turns.append({"role": role, "speaker": speaker.strip(), "text": text.strip()})
    return turns


def audit_sales_call(
    transcript: str,
    call_id: str = "EWA-CALL-9042",
    prospect_name: str = "Lachlan M.",
    closer_name: str = "Jordan T.",
) -> CallAuditResult:
    """
    Deterministic + heuristic rubric scorer for high-ticket Ecom Warrior Academy enrollment calls.
    Computes talk-to-listen ratio, discovery depth, objection handling, and generates a GoHighLevel
    (GHL) webhook payload for automated SMS/Email follow-up sequences.
    """
    turns = parse_speaker_turns(transcript)
    if not turns:
        raise ValueError("Transcript must contain at least one valid 'Speaker: text' turn.")

    closer_words = sum(len(t["text"].split()) for t in turns if t["role"] == "closer")
    prospect_words = sum(len(t["text"].split()) for t in turns if t["role"] == "prospect")
    total_words = max(closer_words + prospect_words, 1)
    closer_talk_ratio_pct = round((closer_words / total_words) * 100.0, 1)

    # 1. Discovery Depth Score (checks whether closer asked open-ended pain/goal questions)
    closer_questions = [t["text"] for t in turns if t["role"] == "closer" and "?" in t["text"]]
    pain_keywords = ("why now", "goal", "income", "9-to-5", "stuck", "obstacle", "12 months", "dream")
    deep_questions = [
        q for q in closer_questions if any(k in q.lower() for k in pain_keywords)
    ]
    discovery_depth_score = min(100, 35 + len(closer_questions) * 10 + len(deep_questions) * 15)

    # 2. Detect Prospect Objections & Whether Closer Resolved Them in Next 2 Turns
    detected_objections: List[ObjectionEvent] = []
    for idx, turn in enumerate(turns):
        if turn["role"] != "prospect":
            continue
        lower_text = turn["text"].lower()
        for category, patterns in OBJECTION_PATTERNS.items():
            if any(re.search(pat, lower_text) for pat in patterns):
                subsequent_closer_text = " ".join(
                    t["text"].lower()
                    for t in turns[idx + 1 : idx + 4]
                    if t["role"] == "closer"
                )
                reframe_markers = (
                    "understand",
                    "isolate",
                    "aside from",
                    "if we solved",
                    "action taker",
                    "roi",
                    "payment plan",
                    "guarantee",
                    "together",
                )
                resolved = any(m in subsequent_closer_text for m in reframe_markers)
                coaching_map = {
                    "price": "Isolate price vs. confidence in ROI; anchor against 12-month cost of staying in current job.",
                    "spouse_partner": "Unpack whether spouse knows about the call; equip prospect with the 3-minute 'Partner Alignment Brief' before hanging up.",
                    "time_bandwidth": "Contrast 45 mins/day building an asset vs. 40 hrs/week trading time for wages.",
                    "skepticism": "Share verified Australian student case study with matching starting capital and work schedule.",
                }
                detected_objections.append(
                    ObjectionEvent(
                        category=category,
                        quote=turn["text"],
                        resolved_by_closer=resolved,
                        coaching_tip=coaching_map[category],
                    )
                )

    if not detected_objections:
        objection_handling_score = 88
    else:
        resolved_count = sum(1 for o in detected_objections if o.resolved_by_closer)
        objection_handling_score = int(
            45 + (resolved_count / len(detected_objections)) * 55
        )

    # 3. Buying signals
    missed_signals: List[str] = []
    for idx, turn in enumerate(turns):
        if turn["role"] == "prospect":
            for pat in BUYING_SIGNAL_PATTERNS:
                if re.search(pat, turn["text"].lower()):
                    next_closer = " ".join(
                        t["text"].lower() for t in turns[idx + 1 : idx + 3] if t["role"] == "closer"
                    )
                    if "enroll" not in next_closer and "start" not in next_closer and "link" not in next_closer:
                        missed_signals.append(turn["text"])

    # 4. Urgency Framing Score
    closer_corpus = " ".join(t["text"].lower() for t in turns if t["role"] == "closer")
    urgency_terms = ("cohort", "onboarding", "this week", "action", "momentum", "spot", "fast-track")
    urgency_hits = sum(1 for term in urgency_terms if term in closer_corpus)
    urgency_framing_score = min(100, 40 + urgency_hits * 15)

    # Talk ratio penalty if closer dominates (>65%)
    talk_penalty = max(0, int((closer_talk_ratio_pct - 60) * 0.8)) if closer_talk_ratio_pct > 60 else 0

    overall_score = max(
        0,
        min(
            100,
            int(
                discovery_depth_score * 0.35
                + objection_handling_score * 0.40
                + urgency_framing_score * 0.25
                - talk_penalty
            ),
        ),
    )

    primary_objection = detected_objections[0].category if detected_objections else "none"
    if overall_score >= 82 and all(o.resolved_by_closer for o in detected_objections):
        stage = "Hot Pipeline - Deposit / Enrollment Link Sent"
    elif primary_objection == "spouse_partner":
        stage = "Follow-Up - Partner Alignment Pack"
    elif primary_objections := [o.category for o in detected_objections if not o.resolved_by_closer]:
        stage = f"Objection Rescue - {primary_objections[0].replace('_', ' ').title()}"
    else:
        stage = "Follow-Up - 48h High-Ticket Nurture"

    sms_Draft = (
        f"Hey {prospect_name.split()[0]}, great chatting today with {closer_name}. "
        f"Put together the exact 90-day Australian store launch roadmap + {primary_objection.replace('_', ' ')} breakdown we discussed. "
        f"Check your inbox before our Thursday check-in!"
    )

    ghl_payload = {
        "event": "sales_call.audited",
        "call_id": call_id,
        "contact": {"name": prospect_name, "tags": [f"score:{overall_score}", f"obj:{primary_objection}"]},
        "closer": closer_name,
        "pipeline_stage": stage,
        "automation_actions": {
            "send_sms_draft": sms_Draft,
            "trigger_workflow_id": f"wf_ewa_{primary_objection}_rescue_v2",
            "notify_sales_manager_slack": overall_score < 68 or len(missed_signals) > 0,
        },
    }

    return CallAuditResult(
        call_id=call_id,
        prospect_name=prospect_name,
        closer_name=closer_name,
        overall_score=overall_score,
        discovery_depth_score=discovery_depth_score,
        objection_handling_score=objection_handling_score,
        urgency_framing_score=urgency_framing_score,
        closer_talk_ratio_pct=closer_talk_ratio_pct,
        detected_objections=detected_objections,
        missed_buying_signals=missed_signals,
        recommended_ghl_stage=stage,
        ghl_webhook_payload=ghl_payload,
    )
