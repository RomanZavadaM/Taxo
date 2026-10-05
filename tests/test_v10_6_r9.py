# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1069_features as r9

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentHeaderLayoutR9Tests(unittest.TestCase):
    def test_wide_header_keeps_single_row(self):
        metrics = r9.header_layout_metrics(280, 320, 900)
        self.assertFalse(metrics["stacked"])
        self.assertEqual(metrics["wraplength"], 0)
        self.assertEqual(metrics["gap"], 12)

    def test_narrow_header_stacks_and_wraps_summary(self):
        metrics = r9.header_layout_metrics(360, 560, 820)
        self.assertTrue(metrics["stacked"])
        self.assertEqual(metrics["wraplength"], 760)

    def test_summary_wrap_tracks_available_width_with_bounds(self):
        narrow = r9.header_layout_metrics(200, 900, 420)
        medium = r9.header_layout_metrics(200, 900, 620)
        wide = r9.header_layout_metrics(200, 1200, 1200)
        self.assertEqual(narrow["wraplength"], 408)
        self.assertLess(narrow["wraplength"], medium["wraplength"])
        self.assertEqual(wide["wraplength"], 760)


class R9IntegrationTests(unittest.TestCase):
    def test_r9_layer_keeps_historical_identity_after_later_revision(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        main = (ROOT / "main.py").read_text("utf-8")
        self.assertEqual(r9.APP_VERSION, "10.6-r9")
        self.assertRegex(version, r"Version: 10\.(?:6-r(?:9|10)|[7-9]-r\d+|1\d-r\d+)")
        self.assertRegex(main, r'APP_VERSION = "10\.(?:6-r(?:9|10)|[7-9]-r\d+|1\d-r\d+)"')

    def test_r9_is_before_any_later_outer_layer_and_r8_remains_in_runtime_chain(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1068_features import install as install_v1068", source)
        self.assertIn("from v1069_features import install as install_v1069", source)
        self.assertIn("App = install_v1068(core, App)", source)
        self.assertIn("App = install_v1069(core, App)", source)
        self.assertLess(source.index("App = install_v1068(core, App)"), source.index("App = install_v1069(core, App)"))

    def test_start_package_requires_r9_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1069_features.py", workflow)

    def test_base_header_keeps_summary_source_and_document_table(self):
        source = (ROOT / "vehicle_documents.py").read_text("utf-8")
        start = source.index("class VehicleDocumentsWindow")
        end = source.index("    def _selected_id", start)
        block = source[start:end]
        self.assertIn("self.summary_var = tk.StringVar(value=\"\")", block)
        self.assertIn("textvariable=self.summary_var", block)
        self.assertIn("self.tree = ttk.Treeview", block)
        self.assertIn('orient="horizontal", command=self.tree.xview', block)

    def test_r9_patches_header_layout_only(self):
        source = (ROOT / "v1069_features.py").read_text("utf-8")
        self.assertIn("original_build = cls._build", source)
        self.assertIn("result = original_build(self)", source)
        self.assertIn('frame.bind("<Configure>"', source)
        self.assertIn("summary.configure(", source)
        self.assertIn("title.grid(", source)
        self.assertNotIn("sqlite3", source)
        self.assertNotIn("archive_current_document_slot", source)
        self.assertNotIn("copy_document_file", source)
        self.assertNotIn("ensure_vehicle_documents_schema", source)


if __name__ == "__main__":
    unittest.main()
