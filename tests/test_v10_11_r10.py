import unittest
from pathlib import Path

import main


ROOT = Path(__file__).resolve().parents[1]


class PersonnelReportFlowR10Tests(unittest.TestCase):
    def test_r10_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 11, 10))
        current = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        self.assertTrue(current.startswith("Version: "))
        self.assertEqual(key(current[len("Version: "):]), key(main.APP_VERSION))

    def test_all_personnel_report_uses_one_format_selector_and_one_save_action(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn('all_report_kind=tk.StringVar(value="PDF — для друку")', source)
        self.assertIn('values=("PDF — для друку","Excel — для редагування")', source)
        self.assertIn('text="Зберегти…"', source)
        self.assertNotIn('text="PDF звіт — весь персонал"', source)
        self.assertNotIn('text="Excel звіт — весь персонал"', source)

    def test_all_personnel_report_filename_is_explicit(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn(
            'Табель_робочого_часу_{start.year}-{start.month:02d}_усі-працівники{suffix}',
            source,
        )


if __name__ == "__main__":
    unittest.main()
