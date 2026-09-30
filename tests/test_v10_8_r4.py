# -*- coding: utf-8 -*-
import sqlite3
import unittest
from pathlib import Path

import vehicle_maintenance as maint

ROOT = Path(__file__).resolve().parents[1]


class StoirCoreTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT,active INTEGER DEFAULT 1);
            CREATE TABLE vehicle_odometer_readings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                driver_id INTEGER,
                work_date TEXT,
                reading_at TEXT,
                reading_km INTEGER,
                source_type TEXT,
                worklog_id INTEGER,
                notes TEXT DEFAULT ''
            );
            INSERT INTO vehicles VALUES(1,'Богдан','BC 0001 AA','A092',1);
            """
        )
        maint.ensure_schema_on_connection(self.con)
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_regulation_102_default_bus_intervals(self):
        profile = maint.get_profile(self.con, 1)
        self.assertEqual(profile['to1_interval_km'], 5000)
        self.assertEqual(profile['to2_interval_km'], 20000)

    def test_truck_based_profile_uses_4000_16000(self):
        maint.save_profile(self.con, 1, profile_kind=maint.PROFILE_TRUCK_BASED)
        self.con.commit()
        profile = maint.get_profile(self.con, 1)
        self.assertEqual(profile['to1_interval_km'], 4000)
        self.assertEqual(profile['to2_interval_km'], 16000)

    def test_custom_profile_requires_explicit_intervals(self):
        with self.assertRaises(ValueError):
            maint.save_profile(self.con, 1, profile_kind=maint.PROFILE_CUSTOM)
        maint.save_profile(self.con, 1, profile_kind=maint.PROFILE_CUSTOM,
                           to1_interval_km=12000, to2_interval_km=24000,
                           source_kind='manufacturer', source_note='Заводська документація')
        self.con.commit()
        profile = maint.get_profile(self.con, 1)
        self.assertEqual(profile['to1_interval_km'], 12000)
        self.assertEqual(profile['source_kind'], 'manufacturer')

    def test_latest_odometer_is_used_as_current_fact(self):
        self.con.execute("INSERT INTO vehicle_odometer_readings(vehicle_id,reading_at,reading_km,source_type) VALUES(1,'2026-09-29T18:00:00',100000,'waybill_end')")
        self.con.execute("INSERT INTO vehicle_odometer_readings(vehicle_id,reading_at,reading_km,source_type) VALUES(1,'2026-09-30T18:00:00',100420,'waybill_end')")
        self.con.commit()
        row = maint.latest_odometer(self.con, 1)
        self.assertEqual(row['reading_km'], 100420)

    def test_next_due_comes_from_last_service_plus_interval(self):
        due = maint.next_due_by_mileage(100420, 97000, 5000)
        self.assertEqual(due['due_odometer_km'], 102000)
        self.assertEqual(due['remaining_km'], 1580)

    def test_unknown_last_service_does_not_invent_plan(self):
        self.assertIsNone(maint.next_due_by_mileage(100420, None, 5000))

    def test_statuses(self):
        self.assertEqual(maint.maintenance_status(1500,1000),'ok')
        self.assertEqual(maint.maintenance_status(700,1000),'due_soon')
        self.assertEqual(maint.maintenance_status(-1,1000),'overdue')
        self.assertEqual(maint.maintenance_status(None,1000),'unknown')

    def test_plan_links_waybill_mileage_and_service_events(self):
        self.con.execute("INSERT INTO vehicle_odometer_readings(vehicle_id,reading_at,reading_km,source_type) VALUES(1,'2026-09-30T18:00:00',100420,'waybill_end')")
        maint.record_event(self.con,1,maint.MAINTENANCE_TO1,'20.09.2026',odometer_km=97000,description='ТО-1')
        maint.record_event(self.con,1,maint.MAINTENANCE_TO2,'01.08.2026',odometer_km=82000,description='ТО-2')
        self.con.commit()
        plan=maint.vehicle_plan(self.con,1)
        self.assertEqual(plan['current_odometer_km'],100420)
        self.assertEqual(plan['to1']['due']['due_odometer_km'],102000)
        self.assertEqual(plan['to2']['due']['due_odometer_km'],102000)


class R4IntegrationTests(unittest.TestCase):
    def test_otk_keeps_existing_database_key_but_uses_legal_name(self):
        text=(ROOT/'vehicle_documents.py').read_text('utf-8')
        self.assertIn('"inspection": "Протокол ОТК / перевірки технічного стану"',text)
        self.assertIn('"inspection"',text)

    def test_runtime_installs_r4_outermost(self):
        text=(ROOT/'taxo_app.py').read_text('utf-8')
        self.assertIn('from v1084_features import install as install_v1084',text)
        self.assertIn('App = install_v1084(core, App)',text)
        self.assertLess(text.index('App = install_v1083(core, App)'),text.index('App = install_v1084(core, App)'))

    def test_current_version_is_r4(self):
        self.assertIn('10.8-r4',(ROOT/'VERSION.txt').read_text('utf-8'))
        self.assertIn('APP_VERSION = "10.8-r4"',(ROOT/'main.py').read_text('utf-8'))

    def test_stoir_is_separate_workspace_with_four_tabs(self):
        text=(ROOT/'vehicle_maintenance_ui.py').read_text('utf-8')
        for label in ('Огляд','Пробіг / одометр','ТО і ремонти','Технічний контроль (ОТК)'):
            self.assertIn(label,text)
        self.assertNotIn('book.add(orders_tab',text)

    def test_start_package_guards_r4_runtime(self):
        text=(ROOT/'START.bat').read_text('ascii')
        for name in ('v1084_features.py','vehicle_maintenance.py','vehicle_maintenance_ui.py'):
            self.assertIn(name,text)


if __name__ == '__main__':
    unittest.main()
