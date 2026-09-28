# -*- coding: utf-8 -*-
import re
import unittest
from pathlib import Path

import v1061_features as r1

ROOT = Path(__file__).resolve().parents[1]


class VehicleRegistryFilterR1Tests(unittest.TestCase):
    def test_filter_hides_only_inactive_rows(self):
        self.assertTrue(r1.vehicle_row_visible("Так", True))
        self.assertTrue(r1.vehicle_row_visible(1, True))
        self.assertFalse(r1.vehicle_row_visible("Ні", True))
        self.assertFalse(r1.vehicle_row_visible(0, True))
        self.assertFalse(r1.vehicle_row_visible("inactive", True))

    def test_unchecked_filter_shows_all_rows(self):
        for value in ("Так", "Ні", 1, 0, True, False, "inactive"):
            self.assertTrue(r1.vehicle_row_visible(value, False))

    def test_filter_is_on_by_default_and_refreshes_list(self):
        source = (ROOT / "v1061_features.py").read_text(encoding="utf-8")
        self.assertIn("vehicle_hide_inactive = core.tk.BooleanVar(value=True)", source)
        self.assertIn('text="Сховати неактивні автомобілі"', source)
        self.assertIn("command=self.load_vehicles", source)
        self.assertIn('tree.set(item, "active")', source)
        self.assertIn("tree.delete(item)", source)

    def test_filter_placement_does_not_depend_on_old_add_vehicle_caption(self):
        source = (ROOT / "v1061_features.py").read_text(encoding="utf-8")
        self.assertIn('"Оновити" in button_labels', source)
        self.assertIn("len(button_labels) >= 4", source)
        self.assertIn("Defensive fallback", source)

    def test_filter_does_not_mutate_vehicle_database(self):
        source = (ROOT / "v1061_features.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("update vehicles", source)
        self.assertNotIn("delete from vehicles", source)
        self.assertNotIn("insert into vehicles", source)


class R1IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_10_6_r1(self):
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8")
        match = re.search(r"Version:\s+(\d+)\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match)
        self.assertEqual(tuple(map(int, match.groups())), (10, 6, 1))
        feature = (ROOT / "v1061_features.py").read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "10.6-r1"', feature)

    def test_r1_is_outermost_and_r10_remains_in_chain(self):
        entry = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1061_features import install as install_v1061", entry)
        self.assertIn("App = install_v1061(", entry)
        self.assertIn("install_v10510(", entry)
        self.assertLess(entry.index("App = install_v1061("), entry.index("install_v10510("))

    def test_start_package_requires_r1_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text(encoding="utf-8")
        self.assertIn("v1061_features.py", workflow)


if __name__ == "__main__":
    unittest.main()
