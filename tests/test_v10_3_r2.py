# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R2AttestationPlanFact(unittest.TestCase):
    def test_version_is_r2(self):
        self.assertEqual(main.APP_VERSION,"10.3-r2")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.3-r2")
        self.assertEqual(
            start_archive_stem("10.3-r2"),
            "Taxo_v10_3_candidate_r2_START",
        )

    def test_prepare_ahead_current_attestation_is_preserved(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn("is_current=(ga <= reference_moment < gb)",source)
        self.assertIn("ПОТОЧНИЙ — ПІДГОТУВАТИ",source)
        self.assertIn("Підготувати бланк ДО початку роботи",source)
        self.assertNotIn(
            "Період не може закінчуватися у майбутньому за плановим графіком",
            source,
        )

    def test_fact_change_revises_existing_form_not_small_duplicate(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('"kind":"adjust"',source)
        self.assertIn("Не створювати окремий бланк на залишок",source)
        self.assertIn("_update_attestation_record(",source)
        self.assertIn("Попередні файли будуть збережені в архіві",source)

    def test_attestation_edit_syncs_work_but_not_driving(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn("_sync_attestation_boundaries_to_worklog(",source)
        self.assertIn("_sync_new_attestation_boundaries_to_worklog(",source)
        self.assertIn("Змінює тільки межу РОБОТИ; час керування/маршруту не переписує.",source)

    def test_multiple_reasons_can_remain_separate(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn("сусідні частини з однаковою позицією",source.lower())
        self.assertIn("_attestation_activity_for_calendar_day",source)
        self.assertIn("day_type==\"Лікарняний\"",source)
        self.assertIn("day_type==\"Відпустка\"",source)


if __name__=="__main__":
    unittest.main()
