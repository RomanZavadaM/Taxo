# -*- coding: utf-8 -*-
import re
import unittest
from pathlib import Path

import v1062_features as r2

ROOT = Path(__file__).resolve().parents[1]


class NonRegularWaybillR2Tests(unittest.TestCase):
    def test_day_without_catalog_route_is_nonregular_candidate(self):
        self.assertTrue(r2.is_nonregular_waybill_candidate({"route_id": None}))
        self.assertTrue(r2.is_nonregular_waybill_candidate({"route_id": 0, "route": "по області"}))

    def test_real_catalog_route_keeps_regular_validation(self):
        self.assertFalse(r2.is_nonregular_waybill_candidate({"route_id": 751}))
        self.assertFalse(r2.is_nonregular_waybill_candidate(None))

    def test_vehicle_label_is_human_readable(self):
        self.assertEqual(
            r2.vehicle_choice_label({
                "id": 7,
                "name": "Автобус",
                "make_model": "ЕТАЛОН А-079.54",
                "plate": "ВС9622ЕН",
                "garage_no": "12",
            }),
            "ЕТАЛОН А-079.54 / ВС9622ЕН / гар. № 12",
        )

    def test_standard_issue_action_routes_missing_route_to_nonregular_dialog(self):
        source = (ROOT / "v1062_features.py").read_text(encoding="utf-8")
        self.assertIn("if is_nonregular_waybill_candidate(row):", source)
        self.assertIn("return self.issue_selected_nonregular_waybill(row)", source)
        self.assertIn("return super().issue_selected_waybill()", source)

    def test_vehicle_can_be_selected_during_nonregular_issue(self):
        source = (ROOT / "v1062_features.py").read_text(encoding="utf-8")
        self.assertIn('text="Автобус:"', source)
        self.assertIn("Combobox", source)
        self.assertIn("UPDATE worklog SET vehicle_id=?, vehicle=?", source)
        self.assertIn("COALESCE(active,1)=1", source)

    def test_nonregular_trip_description_is_editable_and_defaults_to_region(self):
        source = (ROOT / "v1062_features.py").read_text(encoding="utf-8")
        self.assertIn('text="Поїздка / замовник:"', source)
        self.assertIn("OFF_ROUTE_DEFAULT_LABEL", source)
        self.assertIn("по місту", source)
        self.assertIn("міжобласна", source)
        self.assertIn("розвозка", source)

    def test_nonregular_issue_reuses_r9_blank_reverse_renderer(self):
        source = (ROOT / "v1062_features.py").read_text(encoding="utf-8")
        self.assertIn("return self._issue_off_route_waybill(row, route_label)", source)
        legacy = (ROOT / "v1059_features.py").read_text(encoding="utf-8")
        self.assertIn("prepare_blank_reverse_payload", legacy)
        self.assertIn("waybill_module._page_two = blank_reverse_page", legacy)

    def test_plan_fact_boundary_is_preserved(self):
        source = (ROOT / "v1062_features.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("fact_work_start_time", source)
        self.assertNotIn("fact_work_end_time", source)
        self.assertNotIn("update tachograph", source)
        self.assertIn("планове призначення автобуса", source)


class AboutLayoutR2Tests(unittest.TestCase):
    def test_about_footer_is_compacted_and_window_can_resize(self):
        source = (ROOT / "v1062_features.py").read_text(encoding="utf-8")
        self.assertIn("win.resizable(True, True)", source)
        self.assertIn('if "Закрити" in texts(frame):', source)
        self.assertIn("frame.configure(padding=(12, 4, 12, 6))", source)
        self.assertIn("canvases[0].configure(height=82)", source)
        self.assertIn("winfo_screenheight() - 70", source)


class R2IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_10_6_r2(self):
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8")
        match = re.search(r"Version:\s+(\d+)\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match)
        self.assertEqual(tuple(map(int, match.groups())), (10, 6, 2))
        feature = (ROOT / "v1062_features.py").read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "10.6-r2"', feature)

    def test_r2_is_outermost_and_r1_remains_in_chain(self):
        entry = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1062_features import install as install_v1062", entry)
        self.assertIn("App = install_v1062(", entry)
        self.assertIn("install_v1061(", entry)
        self.assertLess(entry.index("App = install_v1062("), entry.index("install_v1061("))

    def test_start_package_requires_r2_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text(encoding="utf-8")
        self.assertIn("v1062_features.py", workflow)


if __name__ == "__main__":
    unittest.main()
