import tempfile
import unittest
from datetime import date
from pathlib import Path


_temporary_home = Path(tempfile.mkdtemp(prefix="taxo_v870_r6_"))
_original_path_home = Path.home
Path.home = classmethod(lambda cls: _temporary_home)
try:
    import fitz
    import main
    import waybill
finally:
    Path.home = _original_path_home


class V870R6Tests(unittest.TestCase):
    def setUp(self):
        main.init_db()

    def _employee(self, con, name="Табельний"):
        now="2026-09-15T10:00:00"
        return con.execute(
            "INSERT INTO employees(last_name,first_name,position,active,created_at) VALUES(?,?,?,1,?)",
            (name,"Працівник","Механік",now),
        ).lastrowid

    def test_schema_contains_daily_timesheet_and_odometer_history(self):
        con=main.db()
        try:
            tables={row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn("employee_time_entries",tables)
            self.assertIn("vehicle_odometer_readings",tables)
            columns={row[1] for row in con.execute("PRAGMA table_info(waybills)")}
            self.assertTrue({"odometer_start","odometer_end","distance_km"} <= columns)
        finally:
            con.close()

    def test_staff_night_shift_is_split_between_calendar_days(self):
        con=main.db()
        try:
            employee_id=self._employee(con,"Нічний")
            con.execute("""INSERT INTO employee_shifts(employee_id,role,work_date,shift_no,start_time,end_day_offset,
                end_time,planned_hours,status) VALUES(?,?,?,?,?,?,?,?,?)""",
                (employee_id,"Механік","2026-09-14",1,"22:00",1,"06:00",8.0,"planned"))
            con.commit()
            first=main.employee_day_time(con,employee_id,date(2026,9,14))
            second=main.employee_day_time(con,employee_id,date(2026,9,15))
            self.assertEqual(first["planned_minutes"],120)
            self.assertEqual(second["planned_minutes"],360)
        finally:
            con.close()

    def test_manual_timesheet_fact_overrides_automatic_fact_only(self):
        con=main.db()
        try:
            employee_id=self._employee(con,"Фактичний")
            now="2026-09-15T10:00:00"
            con.execute("""INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at)
                VALUES(?,?,?,?,?,?,?)""",(employee_id,"2026-09-15","Інша робота",None,7.5,"ремонт",now))
            con.commit()
            row=main.employee_day_time(con,employee_id,"2026-09-15")
            self.assertEqual(row["planned_minutes"],0)
            self.assertEqual(row["actual_minutes"],450)
            self.assertEqual(row["day_type"],"Інша робота")
            self.assertTrue(row["manual"])
        finally:
            con.close()

    def test_optional_odometer_history_and_nonblocking_warnings(self):
        self.assertIsNone(main.parse_optional_odometer(""))
        self.assertEqual(main.parse_optional_odometer("123 456"),123456)
        with self.assertRaises(ValueError):
            main.parse_optional_odometer("12,5")
        con=main.db()
        try:
            now="2026-09-15T10:00:00"
            vehicle_id=con.execute("INSERT INTO vehicles(name,active,created_at) VALUES(?,1,?)",("Автобус r6",now)).lastrowid
            driver_id=con.execute("INSERT INTO drivers(last_name,first_name,active,created_at) VALUES(?,?,1,?)",("Водій","r6",now)).lastrowid
            worklog_id=con.execute("INSERT INTO worklog(driver_id,work_date,vehicle_id) VALUES(?,?,?)",(driver_id,"2026-09-15",vehicle_id)).lastrowid
            main.save_waybill_odometer_readings(con,worklog_id,vehicle_id,driver_id,"2026-09-15",120000,120275,
                "2026-09-15T08:00:00","2026-09-15T18:00:00")
            con.commit()
            self.assertEqual(main.get_waybill_odometer_readings(con,worklog_id),(120000,120275))
            self.assertEqual(con.execute("SELECT COUNT(*) FROM vehicle_odometer_readings WHERE source_type='waybill'").fetchone()[0],2)
            warnings=main.odometer_consistency_warnings(con,vehicle_id,119900,119800,"2026-09-16T08:00:00")
            self.assertGreaterEqual(len(warnings),2)
        finally:
            con.close()

    def test_waybill_prints_optional_odometer_values(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"waybill-r6.pdf"
            waybill.build_waybill_pdf(None,target,{
                "waybill_no":"000128","date":"15.09.2026","work_date":"2026-09-15",
                "odometer_start":120000,"odometer_end":120275,"distance_km":275,
            })
            doc=fitz.open(target)
            text="\n".join(page.get_text() for page in doc)
            self.assertIn("поч. 120000 км",text)
            self.assertIn("кін. 120275 км",text)
            self.assertIn("пробіг 275 км",text)
            doc.close()


if __name__ == "__main__":
    unittest.main()
