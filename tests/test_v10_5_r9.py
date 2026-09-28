# -*- coding: utf-8 -*-
import re
import tempfile
import unittest
from pathlib import Path

import fitz
import waybill
import v1059_features as r9

ROOT = Path(__file__).resolve().parents[1]


class OffRouteWaybillR9Tests(unittest.TestCase):
    def test_default_label_is_region_trip_and_is_editable_text(self):
        self.assertEqual(r9.OFF_ROUTE_DEFAULT_LABEL, "по області")
        self.assertEqual(r9.normalize_off_route_label("  міжобласна   поїздка  "), "міжобласна поїздка")
        self.assertEqual(r9.normalize_off_route_label("по місту"), "по місту")
        self.assertEqual(r9.normalize_off_route_label("одноразове замовлення"), "одноразове замовлення")

    def test_off_route_row_uses_schedule_but_does_not_require_catalog_route(self):
        source = {
            "worklog_id": 17,
            "route": "101 / Регулярний",
            "route_id": 101,
            "start_location": "А",
            "end_location": "Б",
            "start_direction": "outbound",
            "outbound_stop_count": 12,
            "return_stop_count": 11,
            "planned_departure": "06:30",
            "planned_return": "15:10",
            "work_hours": 8.0,
            "driving_hours": 6.5,
            "planned_distance_km": 240,
        }
        prepared = r9.prepare_off_route_row(source, "по області")
        self.assertIsNone(prepared["route_id"])
        self.assertEqual(prepared["route"], "по області")
        self.assertEqual(prepared["planned_departure"], "06:30")
        self.assertEqual(prepared["planned_return"], "15:10")
        self.assertEqual(prepared["work_hours"], 8.0)
        self.assertEqual(prepared["driving_hours"], 6.5)
        self.assertIsNone(prepared["planned_distance_km"])
        self.assertEqual(source["route_id"], 101, "helper must not rewrite the source row")

    def test_front_payload_keeps_schedule_times_and_removes_fake_route_points(self):
        payload = {
            "route": "old",
            "start_location": "А",
            "end_location": "Б",
            "start_direction": "outbound",
            "outbound_stops": [{"stop_name": "A"}],
            "return_stops": [{"stop_name": "B"}],
            "planned_departure": "06:30",
            "planned_return": "15:10",
            "planned_duty_time": "08:00",
            "planned_route_time": "06:30",
            "planned_distance_km": 200,
        }
        prepared = r9.prepare_off_route_front_payload(payload, "по місту")
        self.assertEqual(prepared["route"], "по місту")
        self.assertEqual(prepared["start_location"], "")
        self.assertEqual(prepared["end_location"], "")
        self.assertEqual(prepared["start_direction"], "")
        self.assertEqual(prepared["outbound_stops"], [])
        self.assertEqual(prepared["return_stops"], [])
        self.assertEqual(prepared["planned_departure"], "06:30")
        self.assertEqual(prepared["planned_return"], "15:10")
        self.assertEqual(prepared["planned_duty_time"], "08:00")
        self.assertIsNone(prepared["planned_distance_km"])

    def test_reverse_side_is_not_filled_for_off_route_work(self):
        payload = {
            "start_direction": "outbound",
            "outbound_stops": [{"stop_name": "A"}],
            "return_stops": [{"stop_name": "B"}],
            "doctor_1": "Лікар",
            "doctor_2": "Лікар 2",
            "mechanic_1": "Механік",
            "mechanic_2": "Механік 2",
            "odometer_start": 1000,
            "odometer_end": 1120,
            "distance_km": 120,
            "planned_distance_km": 125,
            "planned_duty_time": "08:00",
        }
        prepared = r9.prepare_blank_reverse_payload(payload)
        self.assertEqual(prepared["start_direction"], "")
        self.assertEqual(prepared["outbound_stops"], [])
        self.assertEqual(prepared["return_stops"], [])
        self.assertEqual(prepared["doctor_1"], "")
        self.assertEqual(prepared["doctor_2"], "")
        self.assertEqual(prepared["mechanic_1"], "")
        self.assertEqual(prepared["mechanic_2"], "")
        self.assertIsNone(prepared["odometer_start"])
        self.assertIsNone(prepared["odometer_end"])
        self.assertIsNone(prepared["distance_km"])
        self.assertEqual(prepared["planned_duty_time"], "08:00")

    def test_off_route_pdf_keeps_front_schedule_and_leaves_reverse_dynamic_data_blank(self):
        payload = {
            "waybill_series": "ТЕСТ",
            "waybill_no": "0099",
            "date": "28.09.2026",
            "work_date": "2026-09-28",
            "driver": "Тестовий Водій",
            "vehicle": "АА0001АА",
            "route": "старий маршрут",
            "start_location": "НЕ_ДРУКУВАТИ_СТАРТ",
            "end_location": "НЕ_ДРУКУВАТИ_ФІНІШ",
            "start_direction": "outbound",
            "planned_departure": "06:30",
            "planned_return": "15:10",
            "planned_duty_time": "08:00",
            "planned_route_time": "06:30",
            "outbound_stops": [{"stop_name": "НЕ_ДРУКУВАТИ_ЗУПИНКА"}],
            "return_stops": [{"stop_name": "НЕ_ДРУКУВАТИ_НАЗАД"}],
            "doctor_1": "НЕ_ДРУКУВАТИ_ЛІКАР",
            "mechanic_1": "НЕ_ДРУКУВАТИ_МЕХАНІК",
            "odometer_start": 111111,
            "odometer_end": 222222,
            "distance_km": 333333,
            "planned_distance_km": 444444,
        }
        clean = r9.prepare_off_route_front_payload(payload, "по області")
        original_page_two = waybill._page_two

        def blank_reverse(canvas, data):
            return original_page_two(canvas, r9.prepare_blank_reverse_payload(data))

        waybill._page_two = blank_reverse
        try:
            with tempfile.TemporaryDirectory() as folder:
                target = Path(folder) / "off_route.pdf"
                waybill.build_waybill_pdf(None, target, clean)
                self.assertTrue(target.exists())
                doc = fitz.open(target)
                try:
                    self.assertEqual(doc.page_count, 2)
                    front = doc[0].get_text()
                    reverse = doc[1].get_text()
                    self.assertIn("по області", front)
                    self.assertIn("06:30", front)
                    self.assertIn("15:10", front)
                    for forbidden in (
                        "НЕ_ДРУКУВАТИ_СТАРТ",
                        "НЕ_ДРУКУВАТИ_ФІНІШ",
                        "НЕ_ДРУКУВАТИ_ЗУПИНКА",
                        "НЕ_ДРУКУВАТИ_НАЗАД",
                        "НЕ_ДРУКУВАТИ_ЛІКАР",
                        "НЕ_ДРУКУВАТИ_МЕХАНІК",
                        "111111",
                        "222222",
                        "333333",
                        "444444",
                    ):
                        self.assertNotIn(forbidden, reverse)
                finally:
                    doc.close()
        finally:
            waybill._page_two = original_page_two

    def test_feature_does_not_change_tachograph_or_plan_fact_sources(self):
        source = (ROOT / "v1059_features.py").read_text(encoding="utf-8")
        lower = source.lower()
        self.assertNotIn("update worklog", lower)
        self.assertNotIn("accounting_mode=", lower)
        self.assertIn("плановий час", lower)
        self.assertIn("тахограф", lower)


class R9IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_r9_or_later(self):
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8")
        match = re.search(r"Version:\s+(\d+)\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (10, 5, 9))
        source = (ROOT / "v1059_features.py").read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "10.5-r9"', source)

    def test_r9_remains_in_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1059_features import install as install_v1059", entry)
        self.assertIn("install_v1059(", entry)
        self.assertIn("install_v1058(", entry)

    def test_start_package_requires_r9_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text(encoding="utf-8")
        self.assertIn("v1059_features.py", workflow)

    def test_ui_exposes_explicit_off_route_action(self):
        source = (ROOT / "v1059_features.py").read_text(encoding="utf-8")
        self.assertIn('text="Поза маршрутом…"', source)
        self.assertIn("OFF_ROUTE_DEFAULT_LABEL = \"по області\"", source)
        self.assertIn("simpledialog.askstring", source)
        self.assertIn("route_id=NULL", source)


if __name__ == "__main__":
    unittest.main()
