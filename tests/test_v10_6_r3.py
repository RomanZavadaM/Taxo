# -*- coding: utf-8 -*-
import re
import tempfile
import unittest
from pathlib import Path

import fitz
import waybill
import v1059_features as r9
import v1063_features as r3

ROOT = Path(__file__).resolve().parents[1]


class NonRegularReverseFieldsR3Tests(unittest.TestCase):
    def test_only_regular_route_tables_are_removed(self):
        payload = {
            "start_direction": "outbound",
            "outbound_stops": [{"stop_name": "НЕ ДРУКУВАТИ ЗУПИНКУ"}],
            "return_stops": [{"stop_name": "НЕ ДРУКУВАТИ НАЗАД"}],
            "doctor_1": "Лікар Перша Зміна",
            "doctor_2": "Лікар Друга Зміна",
            "mechanic_1": "Механік Перша Зміна",
            "mechanic_2": "Механік Друга Зміна",
            "odometer_start": 101000,
            "odometer_end": 101145,
            "distance_km": 145,
            "planned_distance_km": None,
            "company_name": "Тестове АТП",
            "driver": "Водій Тестовий",
            "vehicle": "Автобус Тестовий",
        }
        prepared = r3.prepare_nonregular_reverse_payload(payload)
        self.assertEqual(prepared["start_direction"], "")
        self.assertEqual(prepared["outbound_stops"], [])
        self.assertEqual(prepared["return_stops"], [])
        for key in (
            "doctor_1", "doctor_2", "mechanic_1", "mechanic_2",
            "odometer_start", "odometer_end", "distance_km",
            "planned_distance_km", "company_name", "driver", "vehicle",
        ):
            self.assertEqual(prepared[key], payload[key], key)

    def test_all_declared_operational_fields_survive_nonregular_adapter(self):
        payload = {key: "VALUE:%s" % key for key in r3.PRESERVED_OPERATIONAL_FIELDS}
        payload.update({
            "start_direction": "return",
            "outbound_stops": [{"stop_name": "A"}],
            "return_stops": [{"stop_name": "B"}],
        })
        prepared = r3.prepare_nonregular_reverse_payload(payload)
        for key in r3.PRESERVED_OPERATIONAL_FIELDS:
            self.assertEqual(prepared[key], payload[key], key)

    def test_reverse_pdf_prints_staff_and_odometer_but_not_route_schedule(self):
        payload = {
            "waybill_series": "ТЕСТ",
            "waybill_no": "0100",
            "date": "28.09.2026",
            "work_date": "2026-09-28",
            "driver": "Водій Тестовий",
            "vehicle": "ВС0001АА",
            "route": "замовлення",
            "planned_departure": "08:00",
            "planned_return": "17:00",
            "start_direction": "outbound",
            "outbound_stops": [{"stop_name": "НЕ ДРУКУВАТИ ЗУПИНКУ"}],
            "return_stops": [{"stop_name": "НЕ ДРУКУВАТИ НАЗАД"}],
            "doctor_1": "Лікаренко Тест",
            "doctor_2": "",
            "mechanic_1": "Механіків Тест",
            "mechanic_2": "",
            "odometer_start": 101000,
            "odometer_end": 101145,
            "distance_km": 145,
            "planned_distance_km": None,
        }
        adapted = r3.prepare_nonregular_reverse_payload(payload)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "nonregular_r3.pdf"
            waybill.build_waybill_pdf(None, target, adapted)
            doc = fitz.open(target)
            try:
                self.assertEqual(doc.page_count, 2)
                reverse = doc[1].get_text()
                reverse_words = " ".join(reverse.split())
                self.assertIn("Лікаренко Тест", reverse_words)
                self.assertIn("Механіків Тест", reverse_words)
                self.assertIn("101000", reverse)
                self.assertIn("101145", reverse)
                self.assertIn("145", reverse)
                self.assertNotIn("НЕ ДРУКУВАТИ ЗУПИНКУ", reverse)
                self.assertNotIn("НЕ ДРУКУВАТИ НАЗАД", reverse)
            finally:
                doc.close()

    def test_historical_r9_helper_is_not_rewritten(self):
        historical = {
            "doctor_1": "старий тест",
            "mechanic_1": "старий тест",
            "odometer_start": 1,
            "outbound_stops": [{"stop_name": "A"}],
        }
        old = r9.prepare_blank_reverse_payload(historical)
        self.assertEqual(old["doctor_1"], "")
        self.assertEqual(old["mechanic_1"], "")
        self.assertIsNone(old["odometer_start"])
        self.assertEqual(old["outbound_stops"], [])

    def test_current_runtime_temporarily_replaces_r9_sanitizer_and_restores_it(self):
        source = (ROOT / "v1063_features.py").read_text(encoding="utf-8")
        self.assertIn("historical_sanitizer = r9.prepare_blank_reverse_payload", source)
        self.assertIn("r9.prepare_blank_reverse_payload = prepare_nonregular_reverse_payload", source)
        self.assertIn("finally:", source)
        self.assertIn("r9.prepare_blank_reverse_payload = historical_sanitizer", source)


class WaybillPayloadAuditR3Tests(unittest.TestCase):
    def test_renderer_and_issuer_cover_all_auto_fields_except_manual_schedule_code(self):
        main_source = (ROOT / "main.py").read_text(encoding="utf-8")
        waybill_source = (ROOT / "waybill.py").read_text(encoding="utf-8")

        for key in (
            "company_name", "company_address", "company_phone", "company_fax", "company_email",
            "waybill_no", "waybill_series", "date", "work_date", "route", "vehicle", "driver",
            "driver_personnel_no", "transport_column", "brigade", "planned_departure", "planned_return",
            "start_location", "end_location", "start_direction", "planned_route_time", "planned_duty_time",
            "odometer_start", "odometer_end", "distance_km", "planned_distance_km",
            "doctor_1", "doctor_2", "mechanic_1", "mechanic_2", "outbound_stops", "return_stops",
        ):
            self.assertIn('"%s"' % key, main_source, key)
            self.assertRegex(waybill_source, r"data\.get\([\"']%s[\"']" % re.escape(key), key)

        # Поле графи 13 існує у бланку, але у моделі Taxo немає канонічного
        # schedule_code. Воно лишається порожнім замість вигаданого значення.
        self.assertIn('data.get("schedule_code", "")', waybill_source)
        self.assertNotIn('"schedule_code":', main_source)

    def test_reverse_manual_fact_columns_remain_blank_by_design(self):
        source = (ROOT / "waybill.py").read_text(encoding="utf-8")
        for label in (
            "Зауваження ДАІ",
            "Відмітки лінійного контролю",
            "Час і причина заїзду",
        ):
            self.assertIn(label, source)
        self.assertNotIn('data.get("traffic_police', source)
        self.assertNotIn('data.get("line_control', source)
        self.assertNotIn('data.get("garage_reason', source)


class R3IntegrationTests(unittest.TestCase):
    def test_candidate_identity_is_10_6_r3(self):
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8")
        match = re.search(r"Version:\s+(\d+)\.(\d+)-r(\d+)", version)
        self.assertIsNotNone(match)
        self.assertEqual(tuple(map(int, match.groups())), (10, 6, 3))
        feature = (ROOT / "v1063_features.py").read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "10.6-r3"', feature)

    def test_r3_is_outermost_and_r2_remains_in_chain(self):
        entry = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1063_features import install as install_v1063", entry)
        self.assertIn("App = install_v1063(", entry)
        self.assertIn("install_v1062(", entry)
        self.assertLess(entry.index("App = install_v1063("), entry.index("install_v1062("))

    def test_start_package_requires_r3_runtime(self):
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text(encoding="utf-8")
        self.assertIn("v1063_features.py", workflow)

    def test_effective_main_version_is_set_by_outer_layer(self):
        source = (ROOT / "v1063_features.py").read_text(encoding="utf-8")
        self.assertIn("core.APP_VERSION = APP_VERSION", source)


if __name__ == "__main__":
    unittest.main()
