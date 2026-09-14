import inspect
import tempfile
import unittest
from datetime import date
from pathlib import Path


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


class V870R3Tests(unittest.TestCase):
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

    def test_waybill_pdf_is_two_page_vector_a4(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "waybill.pdf"
            data = {
                "waybill_series": "АААТ",
                "waybill_no": "000127",
                "date": "14.09.2026",
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
            self.assertIn("D+0→D+1", text)
            self.assertIn("Нічліг", text)
            self.assertFalse(any(page.get_images(full=True) for page in doc))
            doc.close()

    def test_tachograph_database_remains_separate(self):
        tachograph.init_tacho_db()
        self.assertNotEqual(main.DB_PATH, tachograph.TACHO_DB)

    def test_build_workflows_cover_windows_and_both_macos_architectures(self):
        root = Path(__file__).resolve().parents[1]
        windows = (root / ".github/workflows/build-windows-v8.70.yml").read_text("utf-8")
        macos = (root / ".github/workflows/build-macos-v8.70.yml").read_text("utf-8")
        self.assertIn("Taxo_v8_70_TEST_r3_Setup_Windows_x64.exe", windows)
        self.assertIn("Taxo_v8_70_TEST_r3_Windows_x64_Portable.zip", windows)
        self.assertIn("runner: macos-15", macos)
        self.assertIn("runner: macos-15-intel", macos)
        self.assertIn("Database unexpectedly bundled", windows)
        self.assertIn("Database unexpectedly bundled", macos)


if __name__ == "__main__":
    unittest.main()

