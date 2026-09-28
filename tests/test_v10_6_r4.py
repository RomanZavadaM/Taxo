# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1064_features as r4

ROOT = Path(__file__).resolve().parents[1]


class WaybillActionLayoutR4Tests(unittest.TestCase):
    def test_wrapped_rows_keep_every_action_once_and_in_order(self):
        widths = [75, 190, 105, 135, 125, 120, 145, 130, 185]
        rows = r4.compute_wrapped_rows(widths, 700, gap=6)
        self.assertGreater(len(rows), 1)
        flattened = [index for row in rows for index in row]
        self.assertEqual(flattened, list(range(len(widths))))
        for row in rows:
            used = sum(widths[index] for index in row) + 6 * max(0, len(row) - 1)
            self.assertLessEqual(used, 700)

    def test_narrower_window_never_uses_fewer_rows(self):
        widths = [90, 190, 110, 135, 125, 125, 150, 135, 190]
        wide = r4.compute_wrapped_rows(widths, 1000)
        narrow = r4.compute_wrapped_rows(widths, 560)
        self.assertGreaterEqual(len(narrow), len(wide))
        self.assertGreater(len(narrow), 1)

    def test_all_existing_waybill_commands_are_preserved(self):
        self.assertEqual(
            r4.WAYBILL_ACTION_LABELS,
            (
                "Оновити",
                "Сформувати / видати PDF",
                "Відкрити PDF",
                "Перегляд у Taxo",
                "Анулювати номер",
                "Папка шляхівок",
                "Спідометр / пробіг",
                "Історія пробігу",
                "Зміни лікаря/механіка",
            ),
        )


class R4IntegrationTests(unittest.TestCase):
    def test_r4_layer_identity_remains_historical(self):
        self.assertEqual(r4.APP_VERSION, "10.6-r4")

    def test_r4_is_outermost_and_r3_remains_in_runtime_chain(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1064_features import install as install_v1064", source)
        self.assertIn("from v1063_features import install as install_v1063", source)
        self.assertIn("App = install_v1063(", source)
        self.assertIn("App = install_v1064(core, App)", source)
        self.assertLess(source.index("App = install_v1063("), source.index("App = install_v1064(core, App)"))

    def test_start_package_requires_r4_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1064_features.py", workflow)

    def test_runtime_reflows_existing_buttons_without_reparenting(self):
        source = (ROOT / "v1064_features.py").read_text("utf-8")
        self.assertIn('button.pack_forget()', source)
        self.assertIn('buttons[index].grid(', source)
        self.assertIn('frame.bind("<Configure>"', source)
        self.assertIn('win.bind("<Configure>"', source)
        self.assertIn('wraplength=max(360, width - 40)', source)

    def test_base_waybill_table_keeps_both_scrollbars(self):
        source = (ROOT / "main.py").read_text("utf-8")
        start = source.index("def show_waybills_for_schedule")
        block = source[start:source.index("def refresh_waybill_issue_list", start)]
        self.assertIn('orient="vertical",command=self.waybill_tree.yview', block)
        self.assertIn('orient="horizontal",command=self.waybill_tree.xview', block)
        self.assertIn('xscrollcommand=x.set', block)

    def test_ui_only_layer_does_not_touch_business_data_sources(self):
        source = (ROOT / "v1064_features.py").read_text("utf-8")
        self.assertNotIn("sqlite3", source)
        self.assertNotIn("build_waybill_pdf", source)
        self.assertNotIn("worklog", source)
        self.assertNotIn("odometer", source.lower())


if __name__ == "__main__":
    unittest.main()
