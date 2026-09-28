# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1067_features as r7

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentActionLayoutR7Tests(unittest.TestCase):
    def test_wrapped_rows_keep_every_control_once_and_in_order(self):
        widths = [145, 105, 110, 135, 85, 150]
        rows = r7.compute_wrapped_rows(widths, 620, gap=6)
        flattened = [index for row in rows for index in row]
        self.assertEqual(flattened, list(range(len(widths))))
        self.assertGreater(len(rows), 1)
        for row in rows:
            used = sum(widths[index] for index in row) + 6 * max(0, len(row) - 1)
            self.assertLessEqual(used, 620)

    def test_narrower_window_never_uses_fewer_rows(self):
        widths = [145, 105, 110, 135, 85, 150]
        wide = r7.compute_wrapped_rows(widths, 900)
        narrow = r7.compute_wrapped_rows(widths, 520)
        self.assertGreaterEqual(len(narrow), len(wide))
        self.assertGreater(len(narrow), 1)

    def test_all_document_actions_are_preserved(self):
        self.assertEqual(
            r7.DOCUMENT_ACTION_LABELS,
            (
                "Додати документ",
                "Редагувати",
                "Архівувати",
                "Відкрити копію",
                "Оновити",
                "Показувати архів",
            ),
        )


class R7IntegrationTests(unittest.TestCase):
    def test_r7_layer_identity_remains_historical(self):
        self.assertEqual(r7.APP_VERSION, "10.6-r7")

    def test_r7_is_installed_after_r6_and_remains_in_runtime_chain(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1066_features import install as install_v1066", source)
        self.assertIn("from v1067_features import install as install_v1067", source)
        self.assertIn("App = install_v1066(core, App)", source)
        self.assertIn("App = install_v1067(core, App)", source)
        self.assertLess(source.index("App = install_v1066(core, App)"), source.index("App = install_v1067(core, App)"))

    def test_start_package_requires_r7_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1067_features.py", workflow)

    def test_base_document_window_keeps_actions_state_and_scrollbars(self):
        source = (ROOT / "vehicle_documents.py").read_text("utf-8")
        start = source.index("class VehicleDocumentsWindow")
        block = source[start:source.index("    def _selected_id", start)]
        for label in r7.DOCUMENT_ACTION_LABELS:
            self.assertIn(f'text="{label}"', block)
        self.assertIn("self.show_archived = tk.BooleanVar(value=False)", source)
        self.assertIn('orient="vertical", command=self.tree.yview', block)
        self.assertIn('orient="horizontal", command=self.tree.xview', block)
        self.assertIn("xscrollcommand=xbar.set", block)

    def test_r7_patches_layout_only_not_document_business_rules(self):
        source = (ROOT / "v1067_features.py").read_text("utf-8")
        self.assertIn("original_build = cls._build", source)
        self.assertIn("control.pack_forget()", source)
        self.assertIn("controls[index].grid(", source)
        self.assertIn('frame.bind("<Configure>"', source)
        self.assertNotIn("sqlite3", source)
        self.assertNotIn("archive_current_document_slot", source)
        self.assertNotIn("copy_document_file", source)
        self.assertNotIn("ensure_vehicle_documents_schema", source)


if __name__ == "__main__":
    unittest.main()
