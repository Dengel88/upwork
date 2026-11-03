import unittest
from pipeline_validator import (
    ApplianceSKU,
    calculate_delta_e,
    evaluate_sku_quality_gate,
    calculate_batch_schedule,
)


class TestAppliancePipelineValidator(unittest.TestCase):
    def test_delta_e_identical_colors(self):
        self.assertEqual(calculate_delta_e((210, 215, 220), (210, 215, 220)), 0.0)

    def test_delta_e_sub_threshold_stainless_steel(self):
        de = calculate_delta_e((212, 216, 220), (213, 216, 219))
        self.assertLess(de, 1.2)

    def test_passing_sku_quality_gate(self):
        sku = ApplianceSKU(
            sku_id="SKU-001",
            name="Brushed Steel Espresso Machine",
            category="Countertop",
            reference_rgb=(212, 216, 220),
            rendered_rgb=(213, 216, 219),
            masked_ssim=0.993,
            edge_canny_iou=0.985,
            logo_ocr_match=0.998,
            control_panel_pixel_locked=True,
        )
        res = evaluate_sku_quality_gate(sku)
        self.assertTrue(res.passed)
        self.assertEqual(len(res.failure_reasons), 0)

    def test_failing_sku_warped_knobs_or_color_shift(self):
        sku = ApplianceSKU(
            sku_id="SKU-FAIL",
            name="Hallucinated Appliance Test",
            category="Countertop",
            reference_rgb=(212, 216, 220),
            rendered_rgb=(180, 195, 230),
            masked_ssim=0.912,
            edge_canny_iou=0.920,
            logo_ocr_match=0.850,
            control_panel_pixel_locked=False,
        )
        res = evaluate_sku_quality_gate(sku)
        self.assertFalse(res.passed)
        self.assertEqual(len(res.failure_reasons), 5)

    def test_batch_schedule_90_skus(self):
        sched = calculate_batch_schedule()
        self.assertEqual(sched["total_skus"], 90)
        self.assertEqual(sched["total_stills"], 450)
        self.assertEqual(sched["total_videos"], 90)
        self.assertEqual(sched["fixed_price_usd"], 7800.0)
        self.assertEqual(sched["price_per_sku_usd"], 86.67)
        total_milestone_usd = sum(m["amount_usd"] for m in sched["milestones"])
        self.assertEqual(total_milestone_usd, 7800.0)
        total_milestone_skus = sum(m["skus"] for m in sched["milestones"])
        self.assertEqual(total_milestone_skus, 90)


if __name__ == "__main__":
    unittest.main()
