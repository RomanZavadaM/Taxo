# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1068_features as r8

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentFormLayoutR8Tests(unittest.TestCase):
    def test_short_form_uses_compact_vertical_metrics(self):
        metrics = r8.form_layout_metrics(580, 520)
        self.assertTrue(metrics["compact"])
        self.assertEqual(metrics["field_pady"], 4)
        self.assertEqual(metrics["save_pady"], 8)
        self.assertEqual(metrics["notes_height"], 3)
        self.assertEqual(metrics["wraplength"], 370)

    def test_normal_form_keeps_original_vertical_metrics(self):
        metrics = r8.form_layout_metrics(720, 650)
        self.assertFalse(metrics["compact"])
        self.assertEqual(metrics["field_pady"], 7)
        self.assertEqual(metrics["save_pady"], 16)
        self.assertEqual(metrics["notes_height"], 4)
        self.assertEqual(metrics["wraplength"], 510)

    def test_explanation_wrap_tracks_width_with_safe_bounds(self):
        narrow = r8.form_layout_metrics(420, 600)
        medium = r8.form_layout_metrics(580, 600)
        wide = r8.form_layout_metrics(1000, 600)
        self.assertEqual(narrow["wraplength"], 240)
        self.assertLess(narrow["wraplength"], medium["wraplength"])
        self.assertEqual(wide["wraplength"], 520)


class R8IntegrationTests(unittest.TestCase):
    def test_r8_layer_identity_remains_historical(self):
        self.assertEqual(r8.APP_VERSION, "10.6-r8")

    def test_r8_is_installed_after_r7_and_remains_in_runtime_chain(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1067_features import install as install_v1067", source)
        self.assertIn("from v1068_features import install as install_v1068", source)
        self.assertIn("App = install_v1067(core, App)", source)
        self.assertIn("App = install_v1068(core, App)", source)
        self.assertLess(source.index("App = install_v1067(core, App)"), source.index("App = install_v1068(core, App)"))

    def test_start_package_requires_r8_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1068_features.py", workflow)

    def test_base_form_keeps_document_business_rules_and_save_action(self):
        source = (ROOT / "vehicle_documents.py").read_text("utf-8")
        start = source.index("    def _form(self, row=None):")
        end = source.index("    def archive_document", start)
        block = source[start:end]
        self.assertIn("EXPIRY_REQUIRED", block)
        self.assertIn("valid_until < valid_from", block)
        self.assertIn("copy_document_file(", block)
        self.assertIn("archive_current_document_slot(", block)
        self.assertIn('text="Зберегти", command=save', block)

    def test_r8_wraps_existing_form_without_reimplementing_save_logic(self):
        source = (ROOT / "v1068_features.py").read_text("utf-8")
        self.assertIn("result = original_form(self, row)", source)
        self.assertIn('win.bind("<Configure>"', source)
        self.assertIn("notes.configure(height=metrics[\"notes_height\"])", source)
        self.assertNotIn("con.execute", source)
        self.assertNotIn("copy_document_file(", source)
        self.assertNotIn("archive_current_document_slot(", source)


if __name__ == "__main__":
    unittest.main()
