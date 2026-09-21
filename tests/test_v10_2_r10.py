# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo102R10AttestationReconcile(unittest.TestCase):
    def test_version_is_r10_or_later(self):
        current=version_from_file(ROOT/"VERSION.txt")
        self.assertEqual(main.APP_VERSION,current)
        self.assertRegex(current,r"^(?:10\.2-r10|10\.3-r(?:[1-9]|10))$")
        self.assertEqual(
            start_archive_stem("10.2-r10"),
            "Taxo_v10_2_candidate_r10_START",
        )

    def test_partial_overlap_is_reconciliation_not_extra_blank(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('"kind":"adjust"',source)
        self.assertIn('f"УТОЧНИТИ БЛАНК №{att_id}"',source)
        self.assertIn('"attestation_id":int(att_id)',source)
        self.assertIn('"old_from":ast',source)
        self.assertIn('"old_to":aen',source)
        self.assertIn(
            "Не створювати окремий бланк на залишок",
            source,
        )

    def test_adjustment_reuses_existing_revision_mechanism(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn(
            "out=self._update_attestation_record(\n"
            "                    att_id,period_from,period_to,activity_no,place",
            source,
        )
        self.assertIn(
            "Попередні файли будуть збережені в архіві.",
            source,
        )
        self.assertIn(
            'action_bar,text="Сформувати / уточнити бланк"',
            source,
        )

    def test_adjustment_cannot_be_loaded_as_new_blank(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn(
            'if r.get("kind")=="adjust":\n'
            '            messagebox.showinfo(',
            source,
        )
        self.assertIn(
            "Щоб не створити дубль",
            source,
        )

    def test_no_fixed_minute_tolerance_is_used(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertNotIn("ATT_GAP_TOLERANCE",source)
        self.assertNotIn("40 * 60",source)
        self.assertNotIn("timedelta(minutes=40)",source)


if __name__=="__main__":
    unittest.main()
