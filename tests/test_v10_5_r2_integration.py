# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Taxo105R2IntegrationTests(unittest.TestCase):
    def test_r2_layer_remains_in_install_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1051_features import install as install_v1051", entry)
        self.assertIn("from v1052_features import install as install_v1052", entry)
        self.assertIn("install_v1052(", entry)
        self.assertIn("install_v1051(", entry)
        self.assertLess(entry.index("install_v1052("), entry.index("install_v1051("))

    def test_r2_historical_metadata_remains_immutable(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10_5_r2.md").read_text("utf-8")
        feature = (ROOT / "v1052_features.py").read_text("utf-8")
        self.assertIn("Taxo 10.5-r2", notes)
        self.assertIn("покомпонентна звірка ТЗ з «Шлях»", notes)
        self.assertIn("порожнє/відсутнє поле «Шлях» ніколи не очищає Taxo", notes)
        self.assertIn('APP_VERSION = "10.5-r2"', feature)

    def test_start_guard_requires_r2_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("vehicle_reconciliation.py", workflow)
        self.assertIn("v1052_features.py", workflow)
        self.assertIn("v1051_features.py", workflow)

    def test_r1_checkpoint_remains_historical(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10_5_r1.md").read_text("utf-8")
        self.assertIn("Taxo 10.5-r1", notes)
        self.assertIn("d7e5a730767ebc17e6935b2d3f25208a9f151c16", notes)
        self.assertIn("10.5-r1` після видачі immutable", notes)

    def test_r2_boundary_keeps_registry_separate_from_other_vehicle_controls(self):
        model = (ROOT / "vehicle_reconciliation.py").read_text("utf-8")
        ui = (ROOT / "v1052_features.py").read_text("utf-8")
        self.assertNotIn("vehicle_documents", model)
        self.assertNotIn("military_transport", model)
        self.assertIn("Локальні документи ТЗ і військово-транспортний облік — окремі контури", ui)


if __name__ == "__main__":
    unittest.main()
