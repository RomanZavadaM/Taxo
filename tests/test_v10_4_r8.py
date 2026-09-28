# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook

import employee_reminders as reminders
import personnel_registry
import vehicle_registry
from v1048_features import _create_unmatched_employees


class TempCore:
    def __init__(self, db_path):
        self.db_path = str(db_path)

    def db(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con


def make_base_db(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            plate TEXT DEFAULT '',
            make_model TEXT DEFAULT '',
            year INTEGER,
            notes TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT ''
        );
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_no TEXT DEFAULT '',
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            position TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            tariff_rate REAL,
            phone TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            dismissal_date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1,
            driver_id INTEGER UNIQUE REFERENCES drivers(id) ON DELETE SET NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    con.commit()
    con.close()


def make_shlyakh_xlsx(path, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Транспортні засоби"
    ws.append(["Транспортні засоби ліцензійної справи"])
    ws.append([
        "Вид", "№ ТЗ", "Перевізник", "Статус", "Vin-код автомобіля",
        "Марка", "Модель", "Повна маса, кг", "ЄВРО",
        "Euro згідно сертифікату ЄКМТ",
        "Початок дії сертифікату ЄКМТ", "№ сертифікату ЄКМТ",
    ])
    for row in rows:
        ws.append(row)
    wb.save(path)


class VehicleRegistryR8Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "taxo.sqlite3"
        make_base_db(self.db_path)
        self.core = TempCore(self.db_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_real_layout_parser_and_fields(self):
        src = self.root / "shlyakh.xlsx"
        make_shlyakh_xlsx(src, [[
            "Автобус", "ВС1234АА", "12345678 ТОВ Тест", "На обліку",
            "WVWZZZ12345678901", "MAN", "Lion", 18000, "EURO-5", "EURO-5", "01.01.2026", "ECMT-1",
        ]])
        parsed = vehicle_registry.parse_registry_file(src)
        self.assertEqual(parsed["source_kind"], vehicle_registry.SOURCE_KIND)
        self.assertEqual(len(parsed["rows"]), 1)
        row = parsed["rows"][0]
        self.assertEqual(row["plate"], "ВС1234АА")
        self.assertEqual(row["vin"], "WVWZZZ12345678901")
        self.assertEqual(row["gross_mass_kg"], "18000")
        self.assertEqual(row["registry_carrier_edrpou"], "12345678")
        self.assertEqual(row["ecmt_valid_from"], "2026-01-01")

    def test_plate_normalization_handles_ukrainian_lookalikes(self):
        self.assertEqual(vehicle_registry.normalize_plate("ВС 1234 АА"), "BC1234AA")
        self.assertEqual(vehicle_registry.normalize_plate("BC1234AA"), "BC1234AA")

    def test_vin_has_priority_and_conflicting_plate_is_critical(self):
        con = self.core.db()
        vehicle_registry.ensure_schema_on_connection(con)
        now = datetime.now().isoformat(timespec="seconds")
        con.execute("INSERT INTO vehicles(name,plate,make_model,active,created_at,vin) VALUES(?,?,?,?,?,?)",
                    ("Bus A", "AA1111AA", "MAN A", 1, now, "VIN00000000000001"))
        con.execute("INSERT INTO vehicles(name,plate,make_model,active,created_at,vin) VALUES(?,?,?,?,?,?)",
                    ("Bus B", "BB2222BB", "MAN B", 1, now, "VIN00000000000002"))
        con.commit()
        parsed = {"rows":[{
            "plate":"BB2222BB", "vin":"VIN00000000000001", "make":"MAN", "model":"A",
            "registry_status":"На обліку", "source_row":3,
        }]}
        plan = vehicle_registry.plan_import_rows(con, parsed)
        con.close()
        self.assertEqual(plan[0]["status"], "critical")

    def test_fill_update_and_empty_source_never_clear_local(self):
        src = self.root / "shlyakh.xlsx"
        make_shlyakh_xlsx(src, [[
            "Автобус", "AA1111AA", "12345678 ТОВ Тест", "На обліку",
            "VIN00000000000001", "MAN", "RegistryModel", "18000", "EURO-5", "", "", "",
        ]])
        con = self.core.db()
        vehicle_registry.ensure_schema_on_connection(con)
        now = datetime.now().isoformat(timespec="seconds")
        con.execute(
            """INSERT INTO vehicles(name,plate,make_model,active,created_at,vin,make,model,euro_class,ecmt_certificate_no)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            ("Bus", "AA1111AA", "MAN LocalModel", 1, now, "VIN00000000000001", "MAN", "LocalModel", "EURO-4", "LOCAL-CERT"),
        )
        con.commit(); con.close()

        preview = vehicle_registry.preview_registry_import(self.core, src)
        vehicle_registry.apply_registry_import(self.core, preview, mode=vehicle_registry.IMPORT_FILL_EMPTY)
        con = self.core.db(); row = con.execute("SELECT * FROM vehicles").fetchone(); con.close()
        self.assertEqual(row["model"], "LocalModel")
        self.assertEqual(row["euro_class"], "EURO-4")
        self.assertEqual(row["gross_mass_kg"], "18000")
        self.assertEqual(row["ecmt_certificate_no"], "LOCAL-CERT")

        preview = vehicle_registry.preview_registry_import(self.core, src)
        vehicle_registry.apply_registry_import(self.core, preview, mode=vehicle_registry.IMPORT_UPDATE)
        con = self.core.db(); row = con.execute("SELECT * FROM vehicles").fetchone(); con.close()
        self.assertEqual(row["model"], "RegistryModel")
        self.assertEqual(row["euro_class"], "EURO-5")
        self.assertEqual(row["ecmt_certificate_no"], "LOCAL-CERT")

    def test_create_new_vehicle_does_not_follow_registry_removed_status(self):
        src = self.root / "shlyakh.xlsx"
        make_shlyakh_xlsx(src, [[
            "Автобус", "AA3333AA", "12345678 ТОВ Тест", "Знятий з обліку",
            "VIN00000000000003", "Setra", "S", "19000", "EURO-6", "", "", "",
        ]])
        preview = vehicle_registry.preview_registry_import(self.core, src)
        result = vehicle_registry.apply_registry_import(
            self.core, preview, mode=vehicle_registry.IMPORT_FILL_EMPTY, create_new=True
        )
        self.assertEqual(result["created"], 1)
        con = self.core.db(); row = con.execute("SELECT * FROM vehicles").fetchone(); con.close()
        self.assertEqual(row["active"], 1)
        self.assertEqual(row["registry_status"], "Знятий з обліку")
        self.assertEqual(row["vin"], "VIN00000000000003")

    def test_local_only_vehicle_is_preserved(self):
        src = self.root / "shlyakh.xlsx"
        make_shlyakh_xlsx(src, [[
            "Автобус", "AA1111AA", "12345678 ТОВ Тест", "На обліку",
            "VIN00000000000001", "MAN", "A", "18000", "EURO-5", "", "", "",
        ]])
        con = self.core.db(); vehicle_registry.ensure_schema_on_connection(con)
        now = datetime.now().isoformat(timespec="seconds")
        con.execute("INSERT INTO vehicles(name,plate,make_model,active,created_at,vin) VALUES(?,?,?,?,?,?)",
                    ("Only local", "CC9999CC", "Local", 1, now, "VINLOCAL000000001"))
        con.commit(); con.close()
        preview = vehicle_registry.preview_registry_import(self.core, src)
        self.assertEqual(len(preview["local_only"]), 1)
        vehicle_registry.apply_registry_import(self.core, preview, mode=vehicle_registry.IMPORT_UPDATE)
        con = self.core.db(); row = con.execute("SELECT active,name FROM vehicles WHERE plate='CC9999CC'").fetchone(); con.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["active"], 1)
        self.assertEqual(row["name"], "Only local")

    def test_quarter_status_uses_calendar_quarter(self):
        con = self.core.db(); vehicle_registry.ensure_schema_on_connection(con)
        con.execute(
            """INSERT INTO vehicle_registry_imports(source_kind,source_name,file_sha256,imported_at,mode,total_rows)
               VALUES(?,?,?,?,?,?)""",
            (vehicle_registry.SOURCE_KIND,"x.xlsx","sha","2026-07-01T09:00:00","compare",0),
        )
        con.commit()
        q3 = vehicle_registry.registry_quarter_status(con, today=date(2026,9,30))
        q4 = vehicle_registry.registry_quarter_status(con, today=date(2026,10,1))
        con.close()
        self.assertTrue(q3["current"])
        self.assertFalse(q4["current"])


class EmployeeRegistryCreationR8Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "taxo.sqlite3"
        make_base_db(self.db_path)
        self.core = TempCore(self.db_path)
        con = self.core.db(); personnel_registry.ensure_schema_on_connection(con); con.commit(); con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_missing_employee_from_registry_without_driver_role(self):
        src = self.root / "employees.xlsx"
        wb = Workbook(); ws = wb.active
        ws.append(["Прізвище","Імʼя","По батькові","Стать","Дата народження","РНОКПП","Серія паспорту","Номер паспорту","Номер ID-картки","Статус","Примітка"])
        ws.append(["Тестенко","Олена","Іванівна","Ж","15.10.1990","1234567890","","","123456789","Військовозобов'язаний",""])
        wb.save(src)
        preview = personnel_registry.preview_registry_import(self.core, src)
        self.assertEqual(preview["plan"][0]["status"], "unmatched")
        created = _create_unmatched_employees(self.core, preview)
        self.assertEqual(created, 1)
        con = self.core.db()
        employee = con.execute("SELECT * FROM employees").fetchone()
        drivers = con.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
        military = con.execute("SELECT * FROM employee_military_profile WHERE employee_id=?", (employee["id"],)).fetchone()
        con.close()
        self.assertEqual(employee["birth_date"], "1990-10-15")
        self.assertEqual(employee["rnokpp"], "1234567890")
        self.assertEqual(employee["id_card_number"], "123456789")
        self.assertIsNone(employee["driver_id"])
        self.assertEqual(drivers, 0)
        self.assertIsNotNone(military)


class BirthdayReminderR8Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "taxo.sqlite3"
        make_base_db(self.db_path)
        self.core = TempCore(self.db_path)
        con = self.core.db(); personnel_registry.ensure_schema_on_connection(con); reminders.ensure_schema_on_connection(con)
        now = datetime.now().isoformat(timespec="seconds")
        for last, first, born in (
            ("П'ять","Днів","1990-10-02"),
            ("Один","День","1985-09-28"),
            ("Сьогодні","Свято","1980-09-27"),
            ("Далеко","Потім","1988-11-20"),
        ):
            con.execute("INSERT INTO employees(last_name,first_name,birth_date,active,created_at) VALUES(?,?,?,1,?)",
                        (last,first,born,now))
        con.commit(); con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_exact_5_1_0_triggers(self):
        con = self.core.db()
        due = reminders.due_birthday_reminders(con, today=date(2026,9,27))
        con.close()
        self.assertEqual(sorted(item["trigger_days"] for item in due), [0,1,5])

    def test_popup_dedupes_for_same_day(self):
        today = date(2026,9,27)
        con = self.core.db()
        first = reminders.unseen_due_birthday_reminders(con, today=today)
        reminders.mark_reminders_shown(con, first, today=today, now=datetime(2026,9,27,8,0,0))
        con.commit()
        second = reminders.unseen_due_birthday_reminders(con, today=today)
        con.close()
        self.assertEqual(len(first), 3)
        self.assertEqual(second, [])

    def test_feb29_reminder_uses_feb28_without_changing_birth_date(self):
        born = reminders.parse_birth_date("2000-02-29")
        self.assertEqual(reminders.birthday_in_year(born, 2025), date(2025,2,28))
        self.assertEqual(born, date(2000,2,29))


if __name__ == "__main__":
    unittest.main()
