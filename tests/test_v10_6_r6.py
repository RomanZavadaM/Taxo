# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1066_features as r6

ROOT = Path(__file__).resolve().parents[1]


class VehicleToolbarLayoutR6Tests(unittest.TestCase):
    def test_wrapped_rows_keep_every_control_once_and_in_order(self):
        widths = [95, 105, 105, 165, 190, 85, 225]
        rows = r6.compute_wrapped_rows(widths, 720, gap=6)
        flattened = [index for row in rows for index in row]
        self.assertEqual(flattened, list(range(len(widths))))
        self.assertGreater(len(rows), 1)
        for row in rows:
            used = sum(widths[index] for index in row) + 6 * max(0, len(row) - 1)
            self.assertLessEqual(used, 720)

    def test_narrower_toolbar_never_uses_fewer_rows(self):
        widths = [95, 105, 105, 165, 190, 85, 225]
        wide = r6.compute_wrapped_rows(widths, 1100)
        narrow = r6.compute_wrapped_rows(widths, 560)
        self.assertGreaterEqual(len(narrow), len(wide))
        self.assertGreater(len(narrow), 1)

    def test_all_vehicle_controls_are_preserved(self):
        self.assertEqual(
            r6.VEHICLE_ACTION_LABELS,
            (
                "Нове авто",
                "Редагувати",
                "Документи",
                "Контроль документів",
                "Вивести з експлуатації",
                "Оновити",
                "Сховати неактивні автомобілі",
            ),
        )


class R6IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_10_6_r6(self):
        version = (ROOT / "VERSION.txt").read_text("utf-8")
        main = (ROOT / "main.py").read_text("utf-8")
        self.assertIn("Version: 10.6-r6", version)
        self.assertIn('APP_VERSION = "10.6-r6"', main)
        self.assertEqual(r6.APP_VERSION, "10.6-r6")

    def test_r6_is_outermost_and_r5_remains_in_runtime_chain(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v1065_features import install as install_v1065", source)
        self.assertIn("from v1066_features import install as install_v1066", source)
        self.assertIn("App = install_v1065(core, App)", source)
        self.assertIn("App = install_v1066(core, App)", source)
        self.assertLess(source.index("App = install_v1065(core, App)"), source.index("App = install_v1066(core, App)"))

    def test_start_package_requires_r6_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v1066_features.py", workflow)

    def test_base_vehicle_toolbar_and_r1_filter_contract_are_preserved(self):
        main = (ROOT / "main.py").read_text("utf-8")
        start = main.index("def build_vehicles")
        block = main[start:main.index("def ", start + 4)]
        for label in r6.VEHICLE_ACTION_LABELS[:-1]:
            self.assertIn(f'text="{label}"', block)
        r1 = (ROOT / "v1061_features.py").read_text("utf-8")
        self.assertIn("self.vehicle_hide_inactive = core.tk.BooleanVar(value=True)", r1)
        self.assertIn('text="Сховати неактивні автомобілі"', r1)

    def test_r6_reflows_existing_controls_without_business_logic(self):
        source = (ROOT / "v1066_features.py").read_text("utf-8")
        self.assertIn("control.pack_forget()", source)
        self.assertIn("controls[index].grid(", source)
        self.assertIn('frame.bind("<Configure>"', source)
        self.assertNotIn("sqlite3", source)
        self.assertNotIn("db(", source)
        self.assertNotIn("vehicle_documents", source)


if __name__ == "__main__":
    unittest.main()
