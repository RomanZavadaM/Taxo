# -*- coding: utf-8 -*-
"""Taxo 10.10-r9: driver schedule parity and absence wrapper regression."""
import unittest
from datetime import date

import personnel_month_schedule_r8 as schedule
import v1096_personnel_balance as balance
from test_v10_10_r8 import make_db, CoreStub


class DriverScheduleParityTests(unittest.TestCase):
    def setUp(self):
        self.con = make_db()
        self.con.execute("UPDATE employees SET position='Водій автотранспортних засобів' WHERE id=3")
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_driver_with_real_position_does_not_receive_second_plan(self):
        result = schedule.apply_simple_month_plan(CoreStub, self.con, [3], 2026, 11)
        self.assertEqual(result["added"], 0)
        self.assertGreater(result["skipped_driver"], 0)
        count = self.con.execute("SELECT COUNT(*) FROM employee_shifts WHERE employee_id=3").fetchone()[0]
        self.assertEqual(count, 0)

    def test_driver_days_follow_worklog_not_personnel_shift(self):
        self.con.executemany(
            "INSERT INTO worklog(driver_id,work_date,day_type) VALUES(?,?,?)",
            [(33, "2026-11-02", "Вихідний"),
             (33, "2026-11-14", "Робота"),
             (33, "2026-11-15", "Робота"),
             (33, "2026-11-16", "Робота")]
        )
        self.con.execute(
            """INSERT INTO employee_shifts(employee_id,role,work_date,shift_no,
                      start_time,end_time,planned_hours)
               VALUES(3,'Водій автотранспортних засобів','2026-11-02',1,'08:00','17:00',8)"""
        )
        class Core(CoreStub):
            @staticmethod
            def _driver_plan_minutes_for_day(con, driver_id, day):
                return 0
        grid = schedule.collect_month_schedule(
            Core, self.con, 2026, 11, [3], view=schedule.VIEW_EMPLOYEE
        )
        self.assertEqual(grid["employees"][0]["cells"][1], "Вих")
        self.assertEqual(grid["employees"][0]["cells"][13:16], ["Р", "Р", "Р"])
        self.assertEqual(grid["internal_notes"], [])

    def test_absence_wrapper_accepts_six_argument_call(self):
        employee = self.con.execute("SELECT * FROM employees WHERE id=1").fetchone()
        core = object()
        called = []
        def original(*args):
            called.append(args)
            return 17
        wrapped = balance._safe_absence_adjustment(core, original)
        got = wrapped(core, self.con, employee, date(2026, 11, 2), None, 480)
        self.assertEqual(got, 17)
        self.assertEqual(len(called[0]), 6)
        self.assertIs(called[0][0], core)


if __name__ == "__main__":
    unittest.main()
