# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import tkinter as tk
import unittest
from datetime import date
from pathlib import Path
from tkinter import ttk
from unittest import mock

import function_registry
import main


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button_by_text(root, text):
    for widget in walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == text:
                return widget
        except Exception:
            pass
    return None


class _PlanToFactHarness(main.App):
    def __init__(self):
        tk.Tk.__init__(self)

    def _company_name_value(self):
        return "Ізольований тест"

    def employee_full_name(self, row):
        return " ".join(
            value for value in (
                row["last_name"], row["first_name"], row["middle_name"]
            ) if value
        ).strip()


class PlanToFactReachabilityR10Tests(unittest.TestCase):
    def test_identity_is_10_12_r10(self):
        self.assertEqual(main.APP_VERSION, "10.12-r10")

    def test_registry_requires_plan_to_fact_runtime_smoke(self):
        routes = {route.function_id: route for route in function_registry.FUNCTION_ROUTES}
        self.assertIn("timesheet.plan_to_fact", routes)
        self.assertTrue(routes["timesheet.plan_to_fact"].runtime_smoke)

    def test_live_button_copies_only_missing_fact_in_isolated_database(self):
        today = date.today()
        missing_day = today.replace(day=1)
        protected_day = today.replace(day=2)

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "plan_to_fact_isolated.sqlite3"
            con = sqlite3.connect(db_path)
            con.row_factory = sqlite3.Row
            con.executescript(
                """
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY,
                    driver_id INTEGER,
                    personnel_no TEXT,
                    last_name TEXT,
                    first_name TEXT,
                    middle_name TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    position TEXT DEFAULT '',
                    employment_date TEXT DEFAULT '',
                    dismissal_date TEXT DEFAULT ''
                );
                CREATE TABLE employee_roles (
                    employee_id INTEGER NOT NULL,
                    role TEXT NOT NULL
                );
                CREATE TABLE employee_time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    work_date TEXT NOT NULL,
                    day_type TEXT NOT NULL DEFAULT 'Робота',
                    planned_hours REAL,
                    actual_hours REAL,
                    overtime_hours REAL,
                    night_hours REAL,
                    evening_hours REAL,
                    weekend_holiday_hours REAL,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT DEFAULT '',
                    UNIQUE(employee_id, work_date)
                );
                """
            )
            con.execute(
                """INSERT INTO employees(
                       id,personnel_no,last_name,first_name,middle_name,active,
                       position,employment_date,dismissal_date
                   ) VALUES(1,'T-001','Тестовий','Працівник','Один',1,
                            'Механік','2020-01-01','')"""
            )
            con.execute(
                "INSERT INTO employee_roles(employee_id,role) VALUES(1,'Механік')"
            )
            con.execute(
                """INSERT INTO employee_time_entries(
                       employee_id,work_date,day_type,planned_hours,actual_hours,
                       notes,created_at,updated_at
                   ) VALUES(1,?,'Робота',6.0,NULL,
                            'Зберегти плановий запис','t','t')""",
                (missing_day.isoformat(),),
            )
            con.execute(
                """INSERT INTO employee_time_entries(
                       employee_id,work_date,day_type,planned_hours,actual_hours,
                       notes,created_at,updated_at
                   ) VALUES(1,?,'Робота',5.0,7.25,
                            'Підтверджений факт','t','t')""",
                (protected_day.isoformat(),),
            )
            con.commit()
            con.close()

            def isolated_db():
                connection = sqlite3.connect(db_path)
                connection.row_factory = sqlite3.Row
                return connection

            def isolated_employee_day_time(connection, employee_id, target_date):
                if isinstance(target_date, str):
                    target_date = date.fromisoformat(target_date)
                row = connection.execute(
                    """SELECT * FROM employee_time_entries
                         WHERE employee_id=? AND work_date=?""",
                    (employee_id, target_date.isoformat()),
                ).fetchone()
                if row is None:
                    return {
                        "day_type": "Вихідний",
                        "planned_minutes": 0,
                        "actual_minutes": None,
                        "source": "—",
                        "notes": "",
                        "manual": False,
                    }
                planned = (
                    main.hours_value_to_minutes(row["planned_hours"])
                    if row["planned_hours"] is not None else 0
                )
                actual = (
                    main.hours_value_to_minutes(row["actual_hours"])
                    if row["actual_hours"] is not None else None
                )
                return {
                    "day_type": row["day_type"],
                    "planned_minutes": planned,
                    "actual_minutes": actual,
                    "source": "ізольований тест",
                    "notes": row["notes"],
                    "manual": True,
                }

            with mock.patch.object(main, "db", side_effect=isolated_db), \
                 mock.patch.object(
                     main, "employee_day_time", side_effect=isolated_employee_day_time
                 ), \
                 mock.patch.object(main.messagebox, "askyesno", return_value=True) as confirm, \
                 mock.patch.object(main.messagebox, "showinfo") as info, \
                 mock.patch.object(main.messagebox, "showwarning") as warning, \
                 mock.patch.object(main.messagebox, "showerror") as error:
                app = _PlanToFactHarness()
                app.geometry("1100x700")
                app.deiconify()
                try:
                    win = app.show_employee_timesheet()
                    app.update()

                    notebooks = [
                        widget for widget in walk(win)
                        if isinstance(widget, ttk.Notebook)
                    ]
                    self.assertEqual(len(notebooks), 1)
                    notebook = notebooks[0]
                    notebook.select(notebook.tabs()[1])
                    app.update()

                    button = button_by_text(win, "План → факт")
                    self.assertIsNotNone(button)
                    self.assertTrue(button.winfo_ismapped())

                    daily_tree = next(
                        widget for widget in walk(win)
                        if isinstance(widget, ttk.Treeview)
                        and widget.exists(missing_day.isoformat())
                        and widget.exists(protected_day.isoformat())
                    )
                    daily_tree.selection_set(
                        missing_day.isoformat(), protected_day.isoformat()
                    )
                    app.update()

                    button.invoke()
                    app.update()

                    self.assertTrue(confirm.called)
                    title, message = confirm.call_args.args[:2]
                    self.assertEqual(title, "План → факт")
                    self.assertIn(
                        "Уже наявний факт Taxo не змінюватиме.",
                        message,
                    )
                    self.assertFalse(warning.called)
                    self.assertFalse(error.called)

                    result_messages = [
                        call.args[1] for call in info.call_args_list
                        if len(call.args) >= 2 and call.args[0] == "План → факт"
                    ]
                    self.assertTrue(
                        any(
                            "Записано: 1." in message
                            and "Захищено існуючий факт: 1." in message
                            for message in result_messages
                        )
                    )
                finally:
                    app.destroy()

            con = isolated_db()
            missing = con.execute(
                """SELECT planned_hours,actual_hours,notes
                     FROM employee_time_entries
                    WHERE employee_id=1 AND work_date=?""",
                (missing_day.isoformat(),),
            ).fetchone()
            protected = con.execute(
                """SELECT planned_hours,actual_hours,notes
                     FROM employee_time_entries
                    WHERE employee_id=1 AND work_date=?""",
                (protected_day.isoformat(),),
            ).fetchone()
            con.close()

            self.assertEqual(missing["planned_hours"], 6.0)
            self.assertEqual(missing["actual_hours"], 6.0)
            self.assertEqual(missing["notes"], "Зберегти плановий запис")

            self.assertEqual(protected["planned_hours"], 5.0)
            self.assertEqual(protected["actual_hours"], 7.25)
            self.assertEqual(protected["notes"], "Підтверджений факт")


if __name__ == "__main__":
    unittest.main()
