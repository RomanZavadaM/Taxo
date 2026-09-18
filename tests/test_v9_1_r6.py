# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from personnel_v91 import (
    NONWORK_OVERRIDE_TYPES,
    collect_personnel_week_balance,
)
from work_regime import (
    REGIME_SIX_DAY,
    REGIME_SUMMARIZED,
    PERIOD_MONTH,
    day_norm_minutes,
    ensure_schema,
    preset_six_day_24,
    preset_six_day_36,
    preset_six_day_40,
    save_regime,
    validate_regime,
)


class FakeCore:
    def __init__(self, path):
        self.path = Path(path)

    def db(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    @staticmethod
    def employee_employed_on(employee, target_date):
        start = employee["employment_date"] or ""
        end = employee["dismissal_date"] or ""
        return (not start or target_date >= date.fromisoformat(start)) and (
            not end or target_date <= date.fromisoformat(end)
        )

    @staticmethod
    def employee_name(employee):
        return " ".join(
            x for x in (
                employee["last_name"], employee["first_name"], employee["middle_name"]
            ) if x
        )

    @staticmethod
    def _driver_plan_minutes_for_day(con, driver_id, target_date):
        return 0

    @staticmethod
    def _employee_shift_minutes_for_day(con, employee_id, target_date):
        return 0, None, False

    @staticmethod
    def hours_value_to_minutes(value):
        return int(round(float(value or 0) * 60))

    def employee_day_time(self, con, employee_id, target_date):
        entry = con.execute(
            "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
            (employee_id, target_date.isoformat()),
        ).fetchone()
        norm, _regime = day_norm_minutes(con, employee_id, target_date)
        if entry and entry["day_type"] in NONWORK_OVERRIDE_TYPES:
            return {
                "day_type": entry["day_type"],
                "planned_minutes": 0,
                "actual_minutes": 0,
                "source": "відсутність",
                "notes": entry["notes"] or "",
                "manual": True,
            }
        return {
            "day_type": "Робота" if norm else "Вихідний",
            "planned_minutes": norm,
            "actual_minutes": norm if norm else 0,
            "source": "режим",
            "notes": "",
            "manual": False,
        }


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            personnel_no TEXT DEFAULT '',
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            position TEXT DEFAULT '',
            employment_date TEXT DEFAULT '',
            dismissal_date TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1,
            driver_id INTEGER
        );
        CREATE TABLE employee_roles(
            employee_id INTEGER NOT NULL,
            role TEXT NOT NULL
        );
        CREATE TABLE employee_time_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            day_type TEXT NOT NULL DEFAULT 'Робота',
            planned_hours REAL,
            actual_hours REAL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT '',
            UNIQUE(employee_id,work_date)
        );
        """
    )
    con.execute(
        """INSERT INTO employees(
            id,personnel_no,last_name,first_name,middle_name,position,
            employment_date,dismissal_date,active,driver_id
        ) VALUES(1,'001','Тестовий','Працівник','','Інженер','2026-01-01','',1,NULL)"""
    )
    con.execute("INSERT INTO employee_roles(employee_id,role) VALUES(1,'Інше')")
    con.commit()
    con.close()


class TestWorkRegimeLawModel(unittest.TestCase):
    def test_six_day_presets_are_not_eight_hours(self):
        days40, week40 = preset_six_day_40()
        days36, week36 = preset_six_day_36()
        days24, week24 = preset_six_day_24()
        self.assertEqual(sum(days40), 40 * 60)
        self.assertEqual(max(days40[:6]), 7 * 60)
        self.assertEqual(days40[5], 5 * 60)
        self.assertEqual(sum(days36), 36 * 60)
        self.assertEqual(max(days36[:6]), 6 * 60)
        self.assertEqual(sum(days24), 24 * 60)
        self.assertEqual(max(days24[:6]), 4 * 60)

    def test_six_day_40_rejects_eight_hour_day(self):
        bad = (480, 384, 384, 384, 384, 384, 0)  # totals 40:00
        errors, _warnings = validate_regime(
            REGIME_SIX_DAY, 40 * 60, bad
        )
        self.assertTrue(errors)
        self.assertTrue(any("7:00" in item for item in errors))

    def test_weekly_balance_reduces_norm_for_vacation_by_that_days_norm(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "db.sqlite3"
            make_db(db_path)
            core = FakeCore(db_path)
            ensure_schema(core)
            con = core.db()
            days, weekly = preset_six_day_40()
            save_regime(
                con,
                employee_id=1,
                effective_from=date(2026, 9, 1),
                effective_to=None,
                regime_type=REGIME_SIX_DAY,
                accounting_period="week",
                weekly_norm_minutes=weekly,
                weekday_minutes=days,
                notes="6-денний 40 год",
            )
            con.execute(
                """INSERT INTO employee_time_entries(
                    employee_id,work_date,day_type,planned_hours,actual_hours,
                    notes,created_at,updated_at
                ) VALUES(1,'2026-09-16','Основна щорічна відпустка',0,NULL,'','x','x')"""
            )
            con.commit()
            con.close()

            data = collect_personnel_week_balance(
                core, date(2026, 9, 16), active_only=True
            )
            row = data["employees"][0]
            self.assertEqual(row["base_norm"], 40 * 60)
            self.assertEqual(row["absence_reduction"], 7 * 60)
            self.assertEqual(row["adjusted_norm"], 33 * 60)
            self.assertEqual(row["actual"], 33 * 60)
            self.assertEqual(row["difference"], 0)

            con = core.db()
            saturday_norm, _ = day_norm_minutes(con, 1, date(2026, 9, 19))
            con.close()
            self.assertEqual(saturday_norm, 5 * 60)

    def test_summarized_weekly_difference_is_marked_informational(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "db.sqlite3"
            make_db(db_path)
            core = FakeCore(db_path)
            ensure_schema(core)
            con = core.db()
            save_regime(
                con,
                employee_id=1,
                effective_from=date(2026, 1, 1),
                effective_to=None,
                regime_type=REGIME_SUMMARIZED,
                accounting_period=PERIOD_MONTH,
                weekly_norm_minutes=40 * 60,
                weekday_minutes=(480,480,480,480,480,0,0),
                notes="Підсумований облік",
            )
            con.commit()
            con.close()
            data = collect_personnel_week_balance(
                core, date(2026, 9, 16), active_only=True
            )
            row = data["employees"][0]
            self.assertTrue(row["summarized"])
            self.assertIn("надурочні", row["note"].lower())


if __name__ == "__main__":
    unittest.main()
