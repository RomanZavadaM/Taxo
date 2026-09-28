# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1069_features as r9

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentHeaderLayoutR9Tests(unittest.TestCase):
    def test_wide_header_keeps_labels_on_one_row(self):
        self.assertEqual(r9.header_layout(260, 300, 700), "wide")

    def test_narrow_header_stacks_summary(self):
        self.assertEqual(r9.header_layout(320, 420, 700), "stacked")

    def test_summary_wrap_tracks_available_width_with_safe_bounds(self):
        self.assertEqual(r9.header_wraplength(220), 240)
        self.assertEqual(r9.header_wraplength(600), 584)
        self.assertEqual(r9.header_wraplength(1200), 900)


class R9IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_10_6_r9(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        main = (ROOT / "main.py").read_text("utf-8")
        self.assertIn("Version: 10.6-r9", version)
        self.assertIn('APP_VERSION = "10.6-r9"', main)
        self.assertEqual(r9.APP_VERSION, "10.6-r9")

    def test_r9_is_outermost_and_r8_remains_in_runtime_chain(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1068_features import install as install_v1068", source)
        self.assertIn("from v1069_features import install as install_v1069", source)
        self.assertIn("App = install_v1068(core, App)", source)
        self.assertIn("App = install_v1069(core, App)", source)
        self.assertLess(source.index("App = install_v1068(core, App)"), source.index("App = install_v1069(core, App)"))

    def test_start_package_requires_r9_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1069_features.py", workflow)

    def test_base_header_keeps_same_summary_variable_and_document_logic(self):
        source = (ROOT / "vehicle_documents.py").read_text("utf-8")
        start = source.index("class VehicleDocumentsWindow")
        block = source[start:source.index("    def _selected_id", start)]
        self.assertIn('self.summary_var = tk.StringVar(value="")', block)
        self.assertIn('textvariable=self.summary_var', block)
        self.assertIn("self.load()", block)
        self.assertIn('orient="horizontal", command=self.tree.xview', block)

    def test_r9_patches_header_only_without_business_logic(self):
        source = (ROOT / "v1069_features.py").read_text("utf-8")
        self.assertIn("result = original_build(self)", source)
        self.assertIn("vehicle_label.pack_forget()", source)
        self.assertIn("summary_label.grid(row=1", source)
        self.assertIn('frame.bind("<Configure>"', source)
        self.assertNotIn("con.execute", source)
        self.assertNotIn("vehicle_document_summary", source)
        self.assertNotIn("archive_current_document_slot", source)


if __name__ == "__main__":
    unittest.main()
