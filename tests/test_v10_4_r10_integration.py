# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Taxo104R10IntegrationTests(unittest.TestCase):
    def test_runtime_identity_is_r10(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        main = (ROOT / "main.py").read_text("utf-8")
        self.assertIn("Version: 10.4-r10", version)
        self.assertIn('APP_VERSION = "10.4-r10"', main)

    def test_r10_layer_is_outermost_after_r9_military_accounting(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v10410_features import install as install_v10410", entry)
        self.assertIn("App = install_v10410(", entry)
        self.assertIn("install_military_accounting_ui(", entry)
        layer = (ROOT / "v10410_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.4-r10"', layer)
        self.assertIn("install_military_transport_ui", layer)

    def test_vehicle_ui_keeps_three_controls_conceptually_separate(self):
        ui = (ROOT / "military_transport_ui.py").read_text("utf-8")
        self.assertIn("Військово-транспортний облік", ui)
        self.assertIn("не замінює «Шлях»", ui)
        self.assertIn("контроль страхування/реєстрації/діагностики", ui)
        self.assertIn("не автоматичне порушення", ui)

    def test_worklog_marks_r10_active_and_r9_immutable(self):
        worklog = (ROOT / "WORKLOG.md").read_text("utf-8")
        self.assertIn("Active revision:** Taxo `10.4-r10`", worklog)
        self.assertIn("Latest issued fast-test revision:** Taxo `10.4-r9`", worklog)
        self.assertIn("після видачі r10 наступний кодовий крок — тільки `10.5-r1`", worklog)

    def test_r10_does_not_claim_unknown_is_violation(self):
        model = (ROOT / "military_transport_2026.py").read_text("utf-8")
        self.assertIn('"violation": False', model)
        self.assertIn("Missing information is a clarification state", model)
        self.assertNotIn("import vehicle_registry", model)
        self.assertNotIn("import vehicle_documents", model)


if __name__ == "__main__":
    unittest.main()
