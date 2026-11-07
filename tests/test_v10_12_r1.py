import unittest
from pathlib import Path

import main


ROOT = Path(__file__).resolve().parents[1]


class PersonnelSelectedScheduleEntryR1Tests(unittest.TestCase):
    def test_r1_identity_is_historical_anchor(self):
        def key(value):
            base, _, rev = str(value).partition("-r")
            major, minor = (int(part) for part in base.split(".", 1))
            return major, minor, int(rev or 0)

        self.assertGreaterEqual(key(main.APP_VERSION), (10, 12, 1))
        current = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        self.assertTrue(current.startswith("Version: "))
        self.assertEqual(key(current[len("Version: "):]), key(main.APP_VERSION))

    def test_personnel_planning_has_permanent_selected_schedule_action(self):
        source = (ROOT / "src/taxo/personnel_v91.py").read_text(encoding="utf-8")
        anchor = 'primary, text="Робочі зміни персоналу — масово…"'
        action = 'primary, text="Простий місячний графік…"'
        self.assertIn(anchor, source)
        self.assertIn(action, source)
        self.assertIn("open_simple_month_schedule_r8", source)
        self.assertLess(source.index(anchor), source.index(action))

    def test_legacy_injector_does_not_duplicate_existing_button(self):
        source = (ROOT / "src/taxo/personnel_month_schedule_r8.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'str(widget.cget("text")) == "Простий місячний графік…"', source
        )
        self.assertIn("self._simple_schedule_r8_installed = True", source)

    def test_selected_schedule_still_has_employee_multiselect_and_exports(self):
        source = (ROOT / "src/taxo/personnel_month_schedule_r8.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('selectmode="extended"', source)
        self.assertIn('text="PDF для вибраних працівників"', source)
        self.assertIn('text="Excel для вибраних працівників"', source)


if __name__ == "__main__":
    unittest.main()
