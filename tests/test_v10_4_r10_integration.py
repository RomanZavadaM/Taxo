# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Taxo104R10IntegrationTests(unittest.TestCase):
    def test_r10_historical_identity_remains_immutable(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10_4_r10.md").read_text("utf-8")
        layer = (ROOT / "v10410_features.py").read_text("utf-8")
        self.assertIn("Taxo 10.4-r10", notes)
        self.assertIn("0f7944ad3f86bb6ee8ad19b40cfb2b38d924b934", notes)
        self.assertIn('APP_VERSION = "10.4-r10"', layer)

    def test_r10_layer_remains_in_install_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v10410_features import install as install_v10410", entry)
        self.assertIn("install_v10410(", entry)
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

    def test_r10_release_records_rollover_to_10_5_r1(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10_4_r10.md").read_text("utf-8")
        self.assertIn("10.4-r10` після видачі є immutable", notes)
        self.assertIn("Наступний кодовий крок — тільки `10.5-r1`", notes)
        self.assertIn("36351811271", notes)
        self.assertIn("10942183754", notes)

    def test_r10_does_not_claim_unknown_is_violation(self):
        model = (ROOT / "military_transport_2026.py").read_text("utf-8")
        self.assertIn('"violation": False', model)
        self.assertIn("Missing information is a clarification state", model)
        self.assertNotIn("import vehicle_registry", model)
        self.assertNotIn("import vehicle_documents", model)


if __name__ == "__main__":
    unittest.main()
