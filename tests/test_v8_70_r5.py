import inspect
import tempfile
import unittest
from datetime import date
from pathlib import Path
import re

from release_naming import version_from_file


_temporary_home = tempfile.TemporaryDirectory()
_original_path_home = Path.home
Path.home = classmethod(lambda cls: Path(_temporary_home.name))
try:
    import fitz
    import main
    import tachograph
    import waybill
finally:
    Path.home = _original_path_home


class V870R5Tests(unittest.TestCase):
    def setUp(self):
        main.init_db()

    def test_new_database_schema_and_default_number_pool(self):
        con = main.db()
        try:
            tables = {row[0] for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            self.assertTrue({
                "employees", "employee_roles", "employee_shifts",
                "waybill_number_pools", "waybill_events",
            } <= tables)
            stop_columns = {row[1] for row in con.execute("PRAGMA table_info(route_stops)")}
            self.assertTrue({
                "point_type", "arrival_day_offset", "departure_day_offset",
            } <= stop_columns)
            waybill_columns = {row[1] for row in con.execute("PRAGMA table_info(waybills)")}
            self.assertIn("work_end_date", waybill_columns)
            driver_columns = {row[1] for row in con.execute("PRAGMA table_info(drivers)")}
            self.assertIn("driver_end_date", driver_columns)
            pool = con.execute(
                "SELECT mode,status FROM waybill_number_pools ORDER BY id LIMIT 1"
            ).fetchone()
            self.assertEqual((pool["mode"], pool["status"]), ("auto", "active"))
            self.assertEqual(con.execute("PRAGMA quick_check").fetchone()[0], "ok")
        finally:
            con.close()

    def test_employee_register_and_route_editor_are_exposed(self):
        self.assertIn("Реєстр усіх працівників", inspect.getsource(main.App.build_drivers))
        self.assertIn("Пули серій і номерів", inspect.getsource(main.App.build_company))
        route_source = inspect.getsource(main.App.route_catalog_form)
        self.assertIn("Точка початку роботи", route_source)
        self.assertIn("arrival_day_offset", route_source)
        self.assertIn("departure_day_offset", route_source)
        self.assertIn("Вставити список", route_source)
        self.assertIn("Назви ← прямий", route_source)
        self.assertIn("Швидко вставити обидва напрямки", route_source)
        employee_source = inspect.getsource(main.App.employee_form)
        self.assertIn("Завершити роль водія", employee_source)
        self.assertNotIn("знімається лише після завершення", employee_source)
        self.assertIn("необов'язково", employee_source)

    def test_quick_schedule_infers_midnight_and_waybill_date_range(self):
        rows=main.parse_route_schedule_text(
            "Львів АС;-;22:40;Автостанція;\n"
            "Стрий АС;23:55;00:40;Автостанція;\n"
            "Ужгород АС;05:35;-;Нічліг;",
            0,
        )
        self.assertEqual(rows[1]["arrival_day_offset"],0)
        self.assertEqual(rows[1]["departure_day_offset"],1)
        self.assertEqual(rows[2]["arrival_day_offset"],1)
        self.assertEqual(
            main.waybill_date_range_label(date(2026,9,14),date(2026,9,15)),
            "14.09.2026 - 15.09.2026",
        )
        self.assertEqual(
            main.waybill_time_label(date(2026,9,14),1,"14:20"),
            "15.09.2026 14:20",
        )

    def test_two_column_route_paste_is_the_simple_default(self):
        rows=main.parse_route_schedule_text(
            "Львів АС-2\t22:40\nСтрий АС\t23:55\nУжгород АС\t05:35",
            0,
        )
        self.assertEqual(rows[0]["arrival_time"], "")
        self.assertEqual(rows[0]["departure_time"], "22:40")
        self.assertEqual(rows[1]["arrival_time"], "23:55")
        self.assertEqual(rows[1]["departure_time"], "23:55")
        self.assertEqual(rows[2]["arrival_day_offset"], 1)
        self.assertEqual(rows[2]["arrival_time"], "05:35")
        self.assertEqual(rows[2]["departure_time"], "")

        outbound=main.parse_route_schedule_text("А\t20:00\nБ\t23:00",0)
        last=max(
            int(row[key])*1440+main.time_to_minutes(row[time_key])
            for row in outbound
            for key,time_key in (("arrival_day_offset","arrival_time"),("departure_day_offset","departure_time"))
            if row[time_key]
        )
        returning=main.parse_route_schedule_text("Б\t05:00\nА\t08:00",last//1440,last)
        self.assertEqual(returning[0]["departure_day_offset"],1)

    def test_finishing_driver_role_preserves_employee_and_history(self):
        con=main.db()
        try:
            now="2026-09-14T12:00:00"
            driver_id=con.execute(
                "INSERT INTO drivers(last_name,first_name,active,created_at) VALUES(?,?,1,?)",
                ("Тестовий","Водій",now),
            ).lastrowid
            employee_id=con.execute(
                "INSERT INTO employees(last_name,first_name,active,driver_id,created_at) VALUES(?,?,1,?,?)",
                ("Тестовий","Водій",driver_id,now),
            ).lastrowid
            con.executemany(
                "INSERT INTO employee_roles(employee_id,role) VALUES(?,?)",
                ((employee_id,"Водій"),(employee_id,"Механік")),
            )
            worklog_id=con.execute(
                "INSERT INTO worklog(driver_id,work_date) VALUES(?,?)",
                (driver_id,"2026-09-01"),
            ).lastrowid
            main.finish_driver_role(con,employee_id,driver_id,"2026-09-14")
            con.commit()
            self.assertEqual(con.execute("SELECT active FROM employees WHERE id=?",(employee_id,)).fetchone()[0],1)
            driver=con.execute("SELECT active,driver_end_date FROM drivers WHERE id=?",(driver_id,)).fetchone()
            self.assertEqual((driver["active"],driver["driver_end_date"]),(0,"2026-09-14"))
            roles={row[0] for row in con.execute("SELECT role FROM employee_roles WHERE employee_id=?",(employee_id,))}
            self.assertEqual(roles,{"Механік"})
            self.assertIsNotNone(con.execute("SELECT id FROM worklog WHERE id=?",(worklog_id,)).fetchone())
        finally:
            con.close()

    def test_waybill_pdf_is_two_page_vector_a4(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "waybill.pdf"
            data = {
                "waybill_series": "АААТ",
                "waybill_no": "000127",
                "date": "14.09.2026 - 15.09.2026",
                "work_date": "2026-09-14",
                "planned_departure": "14.09.2026\n22:40",
                "planned_return": "15.09.2026\n14:20",
                "route": "401 / Нічний маршрут",
                "start_location": "Львів АС-8",
                "end_location": "Ужгород АС",
                "start_direction": "outbound",
                "outbound_stops": [{
                    "stop_name": "Стрий АС",
                    "point_type": "Автостанція",
                    "arrival_day_offset": 0,
                    "arrival_time": "23:55",
                    "departure_day_offset": 1,
                    "departure_time": "00:40",
                }],
                "return_stops": [{
                    "stop_name": "Ужгород АС",
                    "point_type": "Нічліг",
                    "arrival_day_offset": 1,
                    "arrival_time": "05:35",
                    "departure_day_offset": 1,
                    "departure_time": "07:10",
                }],
            }
            waybill.build_waybill_pdf(None, target, data)
            doc = fitz.open(target)
            self.assertEqual(doc.page_count, 2)
            text = "\n".join(page.get_text() for page in doc)
            self.assertIn("Прямий напрямок", text)
            self.assertIn("Зворотний напрямок", text)
            self.assertIn("14.09.2026 - 15.09.2026", text)
            self.assertIn("15.09.2026", text)
            self.assertNotIn("D+1", text)
            self.assertIn("Нічліг", text)
            self.assertIn("14.09.2026 - 15.09.2026", text)
            self.assertFalse(any(page.get_images(full=True) for page in doc))
            doc.close()

    def test_tachograph_database_remains_separate(self):
        tachograph.init_tacho_db()
        self.assertNotEqual(main.DB_PATH, tachograph.TACHO_DB)

    def test_build_workflows_cover_windows_and_both_macos_architectures(self):
        root = Path(__file__).resolve().parents[1]
        windows = (root / ".github/workflows/build-windows-v8.70.yml").read_text("utf-8")
        macos = (root / ".github/workflows/build-macos-v8.70.yml").read_text("utf-8")
        current = version_from_file(root / "VERSION.txt")
        match = re.fullmatch(r"9\.1 candidate r(\d+(?:\.\d+)*)", current)
        self.assertIsNotNone(match)
        revision = match.group(1).replace(".", "_")
        prefix = f"Taxo_v9_1_candidate_r{revision}"
        self.assertIn(f"{prefix}_Setup_Windows_x64.exe", windows)
        self.assertIn(f"{prefix}_Windows_x64_Portable.zip", windows)
        self.assertIn("$build = 'false'", windows)
        self.assertIn("runner: macos-15", macos)
        self.assertIn("runner: macos-15-intel", macos)
        self.assertIn("Database unexpectedly bundled", windows)
        self.assertIn("Database unexpectedly bundled", macos)


if __name__ == "__main__":
    unittest.main()
