import tempfile
import unittest
from pathlib import Path


_temporary_home = tempfile.TemporaryDirectory()
_original_path_home = Path.home
Path.home = classmethod(lambda cls: Path(_temporary_home.name))
try:
    from pypdf import PdfReader
    import main
    import waybill
finally:
    Path.home = _original_path_home


class V870R7Tests(unittest.TestCase):
    def setUp(self):
        main.init_db()

    def test_schema_keeps_planned_route_distance_and_waybill_snapshot(self):
        con=main.db()
        try:
            route_columns={row[1] for row in con.execute("PRAGMA table_info(routes)")}
            waybill_columns={row[1] for row in con.execute("PRAGMA table_info(waybills)")}
            self.assertIn("planned_distance_km",route_columns)
            self.assertIn("planned_distance_km",waybill_columns)
        finally:
            con.close()

    def test_optional_route_distance_and_odometer_forecast(self):
        self.assertIsNone(main.parse_optional_route_distance(""))
        self.assertEqual(main.parse_optional_route_distance("1 275"),1275)
        with self.assertRaises(ValueError):
            main.parse_optional_route_distance("0")
        with self.assertRaises(ValueError):
            main.parse_optional_route_distance("12,5")
        self.assertEqual(main.planned_odometer_end(120000,275),120275)
        self.assertIsNone(main.planned_odometer_end(None,275))
        self.assertIsNone(main.planned_odometer_end(120000,None))

    def test_plan_comparison_is_warning_only_and_uses_tolerance(self):
        con=main.db()
        try:
            now="2026-09-15T10:00:00"
            vehicle_id=con.execute(
                "INSERT INTO vehicles(name,active,created_at) VALUES(?,1,?)",
                ("Автобус r7",now),
            ).lastrowid
            close=main.odometer_consistency_warnings(
                con,vehicle_id,100000,100108,planned_distance_km=100,
            )
            far=main.odometer_consistency_warnings(
                con,vehicle_id,100000,100140,planned_distance_km=100,
            )
            self.assertFalse(any("планового" in item for item in close))
            self.assertTrue(any("планового 100 км" in item for item in far))
        finally:
            con.close()

    def test_waybill_prints_plan_separately_from_actual_mileage(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"waybill-r7.pdf"
            waybill.build_waybill_pdf(None,target,{
                "waybill_no":"000129","date":"15.09.2026","work_date":"2026-09-15",
                "odometer_start":120000,"odometer_end":120280,"distance_km":280,
                "planned_distance_km":275,
            })
            doc=PdfReader(target)
            text="\n".join((page.extract_text() or "") for page in doc.pages)
            
            self.assertIn("пробіг 280 км",text)
            self.assertIn("план 275 км",text)


if __name__ == "__main__":
    unittest.main()
