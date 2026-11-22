# -*- coding: utf-8 -*-
"""10.23-r1: structured employee/vehicle navigation in the document catalog."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import document_catalog


def row(identifier, *, employees=(), vehicles=()):
    employee_refs = tuple(("employee:%d" % key, label) for key, label in employees)
    vehicle_refs = tuple(("vehicle:%d" % key, label) for key, label in vehicles)
    labels = [label for _key, label in employee_refs + vehicle_refs]
    return {
        "key": ("order", identifier, 0),
        "source": "order",
        "sources": ("order",),
        "source_id": identifier,
        "source_label": "Наказ",
        "date": "2026-11-18",
        "created_at": "2026-11-18T10:00:00",
        "number": str(identifier),
        "kind": "Наказ",
        "title": "Документ " + str(identifier),
        "person": "; ".join(labels),
        "employee_refs": employee_refs,
        "vehicle_refs": vehicle_refs,
        "entity_text": " ".join(labels),
        "category": document_catalog.CATEGORY_OPERATIONAL,
        "revision_label": "",
        "file_state": "",
        "vault_id": "",
        "paper_scan_count": 0,
        "paper_scan_state": "—",
    }


class DocumentEntityFilterR2Tests(unittest.TestCase):
    def snapshot(self):
        return {
            "rows": [
                row(1, employees=((10, "Іваненко Іван · таб. № 001"),),
                    vehicles=((20, "BC0010AA · MAN · Taxo #20"),)),
                row(2, employees=((11, "Іваненко Іван · таб. № 002"),),
                    vehicles=((21, "BC0020AA · Mercedes · Taxo #21"),)),
                row(3, employees=((10, "Іваненко Іван · таб. № 001"),)),
            ],
            "paper_status": "",
            "vault_status": "",
            "paper_scan_status": "",
            "order_status": "",
        }

    def test_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.23-r9\n")
        self.assertIn('APP_VERSION = "10.23-r9"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.23-r9", (root / "START.bat").read_text("utf-8"))

    def test_employee_filter_uses_stable_id_not_name(self):
        result = document_catalog.paginate_sources(
            self.snapshot(), employee_filter="employee:10"
        )
        self.assertEqual([item["source_id"] for item in result["rows"]], [1, 3])

    def test_vehicle_filter_uses_stable_id(self):
        result = document_catalog.paginate_sources(
            self.snapshot(), vehicle_filter="vehicle:21"
        )
        self.assertEqual([item["source_id"] for item in result["rows"]], [2])

    def test_employee_and_vehicle_filters_combine_before_paging(self):
        result = document_catalog.paginate_sources(
            self.snapshot(),
            employee_filter="employee:10",
            vehicle_filter="vehicle:20",
            page_size=1,
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["pages"], 1)
        self.assertEqual(result["rows"][0]["source_id"], 1)

    def test_available_choices_keep_same_names_distinct(self):
        result = document_catalog.paginate_sources(self.snapshot())
        self.assertEqual(
            [key for key, _label in result["available_employees"]],
            ["employee:10", "employee:11"],
        )

    def test_structured_entities_are_searchable(self):
        result = document_catalog.paginate_sources(
            self.snapshot(), text_filter="BC0020AA"
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source_id"], 2)

    def test_order_reader_collects_frozen_entities_and_assignment_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "Data"
            data.mkdir()
            db = data / "driver_worktime.sqlite3"
            con = sqlite3.connect(db)
            try:
                con.executescript(
                    """
                    CREATE TABLE operations_orders(
                        id INTEGER PRIMARY KEY,
                        order_date TEXT,order_no TEXT,order_type TEXT,
                        subject TEXT,order_series TEXT,created_at TEXT
                    );
                    CREATE TABLE employees(
                        id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,
                        middle_name TEXT,personnel_no TEXT
                    );
                    CREATE TABLE vehicles(
                        id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT
                    );
                    CREATE TABLE vehicle_driver_assignments(
                        id INTEGER PRIMARY KEY,order_id INTEGER,vehicle_id INTEGER,
                        employee_id INTEGER,sequence_no INTEGER
                    );
                    CREATE TABLE operations_order_entities(
                        id INTEGER PRIMARY KEY,order_id INTEGER,entity_type TEXT,
                        entity_id INTEGER,snapshot_json TEXT,sequence_no INTEGER
                    );
                    """
                )
                con.executemany(
                    "INSERT INTO operations_orders VALUES(?,?,?,?,?,?,?)",
                    [
                        (1, "2026-11-18", "1", "vehicle_assignment",
                         "Закріплення", "work", "2026-11-18T08:00:00"),
                        (2, "2026-11-18", "2", "road_safety",
                         "БДР", "work", "2026-11-18T09:00:00"),
                    ],
                )
                con.execute("INSERT INTO employees VALUES(1,'Іваненко','Іван','','001')")
                con.execute("INSERT INTO vehicles VALUES(10,'Автобус 10','BC0010AA','MAN Lion')")
                con.execute("INSERT INTO vehicle_driver_assignments VALUES(1,1,10,1,1)")
                con.execute(
                    "INSERT INTO operations_order_entities VALUES(1,2,'employee',2,?,1)",
                    (json.dumps({"name": "Петренко Петро", "personnel_no": "002"}, ensure_ascii=False),),
                )
                con.execute(
                    "INSERT INTO operations_order_entities VALUES(2,2,'vehicle',20,?,2)",
                    (json.dumps({"plate": "BC0020AA", "name": "Mercedes"}, ensure_ascii=False),),
                )
                con.commit()
            finally:
                con.close()

            rows, status = document_catalog._read_orders(root)

        by_id = {item["source_id"]: item for item in rows}
        self.assertEqual(status, "Накази: 2.")
        self.assertEqual(by_id[1]["employee_refs"][0][0], "employee:1")
        self.assertIn("таб. № 001", by_id[1]["employee_refs"][0][1])
        self.assertEqual(by_id[1]["vehicle_refs"][0][0], "vehicle:10")
        self.assertIn("BC0010AA", by_id[1]["person"])
        self.assertEqual(by_id[2]["employee_refs"][0][0], "employee:2")
        self.assertIn("Петренко Петро", by_id[2]["entity_text"])
        self.assertEqual(by_id[2]["vehicle_refs"][0][0], "vehicle:20")

    def test_old_database_without_relation_tables_still_opens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "Data"
            data.mkdir()
            db = data / "driver_worktime.sqlite3"
            con = sqlite3.connect(db)
            try:
                con.execute(
                    """CREATE TABLE operations_orders(
                        id INTEGER PRIMARY KEY,order_date TEXT,order_no TEXT,
                        order_type TEXT,subject TEXT,created_at TEXT
                    )"""
                )
                con.execute(
                    "INSERT INTO operations_orders VALUES(1,'2026-11-18','1','generic','Старий наказ','2026-11-18')"
                )
                con.commit()
            finally:
                con.close()
            rows, status = document_catalog._read_orders(root)
        self.assertEqual(status, "Накази: 1.")
        self.assertEqual(rows[0]["employee_refs"], ())
        self.assertEqual(rows[0]["vehicle_refs"], ())

    def test_ui_exposes_employee_and_vehicle_filters(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn('text="Працівник / ТЗ:"', source)
        self.assertIn('all_employees_label = "Усі працівники"', source)
        self.assertIn('all_vehicles_label = "Усі ТЗ"', source)
        self.assertIn("employee_filter=employee_filter", source)
        self.assertIn("vehicle_filter=vehicle_filter", source)
        self.assertIn("win._taxo_catalog_employee_filter_box", source)
        self.assertIn("win._taxo_catalog_vehicle_filter_box", source)


if __name__ == "__main__":
    unittest.main()
