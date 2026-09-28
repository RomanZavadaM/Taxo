# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1065_features as r5

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentReportLayoutR5Tests(unittest.TestCase):
    def test_group_rows_keep_order_and_wrap_when_narrow(self):
        widths = [310, 190, 245]
        wide = r5.compute_group_rows(widths, 900, gap=12)
        narrow = r5.compute_group_rows(widths, 560, gap=12)
        self.assertEqual([i for row in wide for i in row], [0, 1, 2])
        self.assertEqual([i for row in narrow for i in row], [0, 1, 2])
        self.assertGreater(len(narrow), len(wide))

    def test_filter_labels_are_complete(self):
        self.assertEqual(r5.REPORT_DATE_LABEL, "Стан документів на дату:")
        self.assertEqual(r5.REPORT_ACTIVE_LABEL, "Тільки авто в експлуатації")
        self.assertEqual(r5.REPORT_ISSUES_LABEL, "Тільки проблемні / попередження")


class R5IntegrationTests(unittest.TestCase):
    def test_r5_layer_identity_remains_historical(self):
        self.assertEqual(r5.APP_VERSION, "10.6-r5")

    def test_r5_is_installed_after_r4(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1064_features import install as install_v1064", source)
        self.assertIn("from v1065_features import install as install_v1065", source)
        self.assertIn("App = install_v1064(core, App)", source)
        self.assertIn("App = install_v1065(core, App)", source)
        self.assertLess(source.index("App = install_v1064(core, App)"), source.index("App = install_v1065(core, App)"))

    def test_start_package_requires_r5_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1065_features.py", workflow)

    def test_base_report_keeps_default_active_filter_and_both_scrollbars(self):
        source = (ROOT / "main.py").read_text("utf-8")
        start = source.index("def show_vehicle_documents_report")
        block = source[start:source.index("def ", start + 4)]
        self.assertIn("active_only=tk.BooleanVar(value=True)", block)
        self.assertIn('text="Тільки авто в експлуатації"', block)
        self.assertIn('text="Тільки проблемні / попередження"', block)
        self.assertIn('orient="vertical",command=tree.yview', block)
        self.assertIn('orient="horizontal",command=tree.xview', block)
        self.assertIn('xscrollcommand=xbar.set', block)

    def test_r5_reflows_existing_controls_without_business_logic(self):
        source = (ROOT / "v1065_features.py").read_text("utf-8")
        self.assertIn("widget.pack_forget()", source)
        self.assertIn("widget.grid(", source)
        self.assertIn('frame.bind("<Configure>"', source)
        self.assertNotIn("sqlite3", source)
        self.assertNotIn("vehicle_document_report_rows", source)
        self.assertNotIn("export_vehicle_document_report", source)


if __name__ == "__main__":
    unittest.main()
