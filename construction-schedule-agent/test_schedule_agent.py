import unittest
from schedule_cpm_engine import ScheduleActivity, analyze_schedule_update


class TestConstructionScheduleEngine(unittest.TestCase):
    def setUp(self):
        self.activities = [
            ScheduleActivity(
                activity_id="A1000",
                wbs="1.0",
                name="Notice to Proceed & Mobilization",
                predecessors=[],
                baseline_start="2026-10-01",
                baseline_finish="2026-10-10",
                current_start="2026-10-01",
                current_finish="2026-10-10",
                percent_complete=100.0,
                total_float_days=0,
                is_milestone=True,
            ),
            ScheduleActivity(
                activity_id="A1010",
                wbs="2.1",
                name="Deep Foundation Caissons & Pile Caps",
                predecessors=["A1000"],
                baseline_start="2026-10-11",
                baseline_finish="2026-10-28",
                current_start="2026-10-14",
                current_finish="2026-11-08",
                percent_complete=70.0,
                total_float_days=-8,
                is_milestone=False,
            ),
            ScheduleActivity(
                activity_id="A1020",
                wbs="2.2",
                name="Substation Transformer Delivery (Open Logic Test)",
                predecessors=[],
                baseline_start="2026-11-01",
                baseline_finish="2026-11-20",
                current_start="2026-11-10",
                current_finish="2026-11-29",
                percent_complete=15.0,
                total_float_days=None,
                is_milestone=True,
            ),
        ]

    def test_deterministic_variance_calculation(self):
        res = analyze_schedule_update(self.activities, status_date_str="2026-11-04", delay_threshold_days=3)
        a1010 = next(a for a in res["activities"] if a["activity_id"] == "A1010")
        self.assertEqual(a1010["start_variance_days"], 3)
        self.assertEqual(a1010["finish_variance_days"], 11)
        self.assertEqual(a1010["duration_variance_days"], 8)
        self.assertTrue(a1010["is_delayed"])
        self.assertTrue(a1010["is_critical_path"])

    def test_lookahead_and_hygiene_flags(self):
        res = analyze_schedule_update(self.activities, status_date_str="2026-11-04", delay_threshold_days=3)
        self.assertEqual(res["delayed_activities_count"], 2)
        self.assertEqual(res["lookahead_30d_count"], 2)
        # A1020 should flag open-ended logic (missing predecessor) AND missing total float
        a1020 = next(a for a in res["activities"] if a["activity_id"] == "A1020")
        self.assertGreaterEqual(len(a1020["data_hygiene_flags"]), 2)


if __name__ == "__main__":
    unittest.main()
