import unittest
from sales_call_auditor import audit_sales_call, parse_speaker_turns


SAMPLE_HIGH_PERFORMING_CALL = """
Closer: Hey Lachlan, excited to dive in. Why now—what is the main goal for your income over the next 12 months, and what has kept you stuck in your 9-to-5?
Prospect: Honestly I'm tired of working 50 hours a week in Brisbane with capped pay. How fast can I launch once I'm inside, and do we use Australian suppliers?
Closer: Great question—we set up your local AU supplier fast-track during Week 1 onboarding so you can launch your first test campaign this week while keeping momentum.
Prospect: The $6,000 investment is high for my current cash flow, and I also need to talk to my wife tonight.
Closer: I completely understand. Aside from the cash flow, if we solved the payment plan structure together so it fits your monthly budget, would your wife support you building an asset with our ROI milestone guarantee?
Prospect: Yeah, if we use the split payment plan she'd be on board. Let's get the enrollment link ready.
Closer: Awesome, sending the enrollment link and our cohort onboarding pack right now!
"""

SAMPLE_WEAK_CALL = """
Closer: Let me explain all 14 modules of Ecom Warrior Academy for the next twenty minutes because our curriculum has hundreds of videos and templates and weekly coaching calls and discord channels.
Prospect: I tried dropshipping before and got burned, plus I work a full-time job with no time. Also what happens after I enroll?
Closer: Yeah our videos are really good so you can watch them whenever you want. Anyway let me know next month if you want to join.
"""


class TestSalesCallAuditor(unittest.TestCase):
    def test_parse_speaker_turns(self):
        turns = parse_speaker_turns(SAMPLE_HIGH_PERFORMING_CALL)
        self.assertEqual(len(turns), 7)
        self.assertEqual(turns[0]["role"], "closer")
        self.assertEqual(turns[1]["role"], "prospect")

    def test_high_performing_call_scoring(self):
        result = audit_sales_call(
            SAMPLE_HIGH_PERFORMING_CALL,
            call_id="EWA-101",
            prospect_name="Lachlan M.",
            closer_name="Jordan T.",
        )
        self.assertGreaterEqual(result.overall_score, 75)
        self.assertGreaterEqual(result.objection_handling_score, 85)
        categories = {o.category for o in result.detected_objections}
        self.assertIn("price", categories)
        self.assertIn("spouse_partner", categories)
        self.assertTrue(all(o.resolved_by_closer for o in result.detected_objections))
        self.assertIn("Hot Pipeline", result.recommended_ghl_stage)

    def test_weak_call_flags_missed_buying_signal_and_unresolved_objections(self):
        result = audit_sales_call(
            SAMPLE_WEAK_CALL,
            call_id="EWA-102",
            prospect_name="Sarah K.",
            closer_name="Dave R.",
        )
        self.assertLess(result.overall_score, 70)
        self.assertGreater(len(result.missed_buying_signals), 0)
        self.assertTrue(result.ghl_webhook_payload["automation_actions"]["notify_sales_manager_slack"])


if __name__ == "__main__":
    unittest.main()
