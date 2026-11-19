# -*- coding: utf-8 -*-
"""10.19-r5/r6: registry-backed fact-entry UI and prepared snapshot path."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import company_template_draft as draft
import company_template_draft_form_ui
import company_template_draft_preview_ui
import company_template_fact_choices as choices
import company_template_fact_codec as codec
import company_template_fact_widgets
import company_template_list_ui
import company_template_store as store


def _template():
    return {
        "format": "taxo.template.v1",
        "template_id": "orders.fact-ui-test",
        "title": "Чернетка № {{order.no}}",
        "document_kind": "order",
        "scenario": "fact-ui",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {
                "name": "company.name", "type": "text", "required": True,
                "label": "Підприємство",
            },
            {
                "name": "order.date", "type": "date", "required": True,
                "label": "Дата",
            },
            {
                "name": "order.no", "type": "integer", "required": True,
                "label": "Номер",
            },
            {
                "name": "driver", "type": "person_ref", "required": True,
                "label": "Водій",
            },
            {
                "name": "vehicle", "type": "vehicle_ref", "required": False,
                "label": "ТЗ",
            },
            {
                "name": "participants", "type": "participants",
                "required": False, "label": "Учасники",
            },
            {
                "name": "assignment.pairs", "type": "pairs",
                "required": False, "label": "Пари",
            },
            {
                "name": "sections", "type": "sections",
                "required": False, "label": "Розділи",
            },
            {
                "name": "table.rows", "type": "table_rows",
                "required": False, "label": "Таблиця",
            },
        ],
        "blocks": [
            {
                "id": "head", "type": "heading", "level": 1,
                "text": "{{company.name}} / {{order.no}} / {{order.date}}",
            },
            {
                "id": "person", "type": "paragraph",
                "text": "{{driver.name}} / {{vehicle.plate}}",
            },
            {
                "id": "participants", "type": "dynamic_table",
                "data_source": "participants", "columns": ["Учасник"],
            },
            {
                "id": "pairs", "type": "dynamic_table",
                "data_source": "assignment.pairs",
                "columns": ["Водій", "ТЗ"],
            },
        ],
    }


def _write_vendor_library(root):
    root.mkdir(parents=True)
    path = "catalog/orders/fact-ui-test.json"
    target = root / path
    target.parent.mkdir(parents=True)
    raw = json.dumps(_template(), ensure_ascii=False).encode("utf-8")
    target.write_bytes(raw)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.fact-ui.synthetic",
        "package_version": "1.0.0",
        "publisher": "Synthetic fixture",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": "orders.fact-ui-test",
            "revision_id": "v1",
            "category_id": "orders",
            "path": path,
        }],
        "files": [{
            "path": path,
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )


class _Workspace:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect_main_db(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con


class _Services:
    def __init__(self, db_path):
        self.workspace = _Workspace(db_path)


def _create_registry(path):
    con = sqlite3.connect(path)
    try:
        con.executescript(
            """
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY,
                last_name TEXT,
                first_name TEXT,
                middle_name TEXT,
                position TEXT,
                active INTEGER,
                personnel_no TEXT,
                rnokpp TEXT,
                driver_id INTEGER
            );
            CREATE TABLE employee_roles(
                employee_id INTEGER,
                role TEXT
            );
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT,
                plate TEXT,
                make_model TEXT,
                vin TEXT,
                garage_no TEXT,
                active INTEGER
            );
            INSERT INTO employees VALUES
                (1,'Петренко','Іван','','Водій',1,'T-1','1111111111',NULL),
                (2,'Коваль','Олена','','Механік',1,'T-2','2222222222',NULL),
                (3,'Неактивний','Працівник','','',0,'T-3','3333333333',NULL);
            INSERT INTO employee_roles VALUES
                (1,'Водій'),
                (2,'Механік');
            INSERT INTO vehicles VALUES
                (10,'','AA1234BB','DAF XF','VIN00010','',1),
                (11,'','BC5678CE','MAN TGX','VIN00011','',1),
                (12,'','OLD0000','Old Truck','VIN00012','',0);
            """
        )
        con.commit()
    finally:
        con.close()


class FactEntryUiR5Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / "Work"
        self.work.mkdir()
        _write_vendor_library(self.work / "TemplateLibrary")
        self.summary = store.create_company_copy(
            self.work, "10.19-r5", "orders.fact-ui-test", "v1"
        )
        self.db_path = self.root / "main.sqlite3"
        _create_registry(self.db_path)

    def test_revision_identity_accepts_r5_and_r6(self):
        root = Path(__file__).resolve().parents[1]
        self.assertIn(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            ("Version: 10.19-r5", "Version: 10.19-r6", "Version: 10.19-r7", "Version: 10.19-r8", "Version: 10.19-r9", "Version: 10.19-r10", "Version: 10.20-r1", "Version: 10.20-r2", "Version: 10.20-r3", "Version: 10.20-r4", "Version: 10.20-r5", "Version: 10.20-r6", "Version: 10.21-r7", "Version: 10.23-r1"),
        )
        main_source = (root / "main.py").read_text("utf-8")
        self.assertTrue(
            'APP_VERSION = "10.19-r5"' in main_source
            or 'APP_VERSION = "10.19-r6"' in main_source
            or 'APP_VERSION = "10.19-r7"' in main_source
            or 'APP_VERSION = "10.19-r8"' in main_source
            or 'APP_VERSION = "10.19-r9"' in main_source
            or 'APP_VERSION = "10.19-r10"' in main_source
            or 'APP_VERSION = "10.20-r1"' in main_source
            or 'APP_VERSION = "10.20-r2"' in main_source
            or 'APP_VERSION = "10.20-r3"' in main_source
            or 'APP_VERSION = "10.20-r4"' in main_source
            or 'APP_VERSION = "10.20-r5"' in main_source
            or 'APP_VERSION = "10.20-r6"' in main_source
            or 'APP_VERSION = "10.21-r7"' in main_source
            or 'APP_VERSION = "10.23-r1"' in main_source
        )
        start_source = (root / "START.bat").read_text("utf-8")
        self.assertTrue(
            "Taxo 10.19-r5" in start_source
            or "Taxo 10.19-r6" in start_source
            or "Taxo 10.19-r7" in start_source
            or "Taxo 10.19-r8" in start_source
            or "Taxo 10.19-r9" in start_source
            or "Taxo 10.19-r10" in start_source
            or "Taxo 10.20-r1" in start_source
            or "Taxo 10.20-r2" in start_source
            or "Taxo 10.20-r3" in start_source
            or "Taxo 10.20-r4" in start_source
            or "Taxo 10.20-r5" in start_source
            or "Taxo 10.20-r6" in start_source
            or "Taxo 10.21-r7" in start_source
            or "Taxo 10.23-r1" in start_source
        )

    def test_registry_catalog_reuses_stable_ids_and_is_read_only(self):
        before = self.db_path.read_bytes()
        catalog = choices.load_fact_choice_catalog(_Services(self.db_path))
        after = self.db_path.read_bytes()

        self.assertEqual(before, after)
        self.assertEqual(
            [(row.entity_id, row.snapshot["name"]) for row in catalog.employees],
            [(2, "Коваль Олена"), (1, "Петренко Іван")],
        )
        self.assertEqual([row.entity_id for row in catalog.drivers], [1])
        self.assertEqual(
            [row.entity_id for row in catalog.vehicles], [10, 11]
        )
        self.assertEqual(catalog.vehicles[0].snapshot["vin"], "VIN00010")

    def test_fact_codecs_are_explicit_and_structured(self):
        self.assertEqual(codec.parse_date("14.11.2026").isoformat(), "2026-11-14")
        self.assertEqual(codec.parse_date("2026-11-14").isoformat(), "2026-11-14")
        self.assertEqual(codec.parse_integer("17"), 17)
        self.assertEqual(
            codec.parse_sections("Перший\nрядок\n\nДругий"),
            ["Перший\nрядок", "Другий"],
        )
        self.assertEqual(
            codec.parse_table_rows("A\tB\nC\tD"),
            [["A", "B"], ["C", "D"]],
        )
        with self.assertRaises(ValueError):
            codec.parse_date("14/11/2026")
        with self.assertRaises(ValueError):
            codec.parse_integer("1.5")

    def test_pair_codec_uses_snapshots_and_blocks_exact_duplicate(self):
        catalog = choices.load_fact_choice_catalog(_Services(self.db_path))
        pair = codec.add_unique_pair(
            [], catalog.drivers[0], catalog.vehicles[0]
        )
        self.assertEqual(pair[0]["person"]["id"], 1)
        self.assertEqual(pair[0]["vehicle"]["id"], 10)
        with self.assertRaisesRegex(ValueError, "вже додана"):
            codec.add_unique_pair(
                pair, catalog.drivers[0], catalog.vehicles[0]
            )

    def test_pair_codec_blocks_one_driver_on_multiple_vehicles(self):
        catalog = choices.load_fact_choice_catalog(_Services(self.db_path))
        first = codec.add_unique_pair(
            [], catalog.drivers[0], catalog.vehicles[0]
        )
        with self.assertRaisesRegex(
            ValueError, "один водій|Один водій"
        ):
            codec.add_unique_pair(
                first, catalog.drivers[0], catalog.vehicles[1]
            )

    def test_pair_codec_allows_multiple_drivers_on_one_vehicle(self):
        catalog = choices.load_fact_choice_catalog(_Services(self.db_path))
        second_driver = choices.FactChoice(
            entity_type="employee",
            entity_id=99,
            label="Другий водій",
            snapshot={
                "entity_type": "employee",
                "id": 99,
                "name": "Другий Водій",
            },
        )
        pairs = codec.add_unique_pair(
            [], catalog.drivers[0], catalog.vehicles[0]
        )
        pairs = codec.add_unique_pair(
            pairs, second_driver, catalog.vehicles[0]
        )
        self.assertEqual(len(pairs), 2)
        self.assertEqual(
            [item["vehicle"]["id"] for item in pairs], [10, 10]
        )

    def test_exact_revision_guard_rejects_stale_form(self):
        definition = draft.load_draft_definition(
            self.work, self.summary.company_template_id
        )
        current = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        updated = copy.deepcopy(current.template)
        updated["title"] = "Змінена власна редакція"
        store.save_company_template(
            self.work,
            current.summary.company_template_id,
            current.content_sha256,
            updated["title"],
            updated,
        )

        facts = {
            "company.name": "ТОВ Тест",
            "order.date": "2026-11-14",
            "order.no": 17,
            "driver": {
                "entity_type": "employee",
                "id": 1,
                "name": "Петренко Іван",
            },
            "vehicle": None,
            "participants": [],
            "assignment.pairs": [],
            "sections": [],
            "table.rows": [],
        }
        with self.assertRaisesRegex(ValueError, "змінився"):
            draft.prepare_company_template_draft(
                self.work,
                self.summary.company_template_id,
                facts,
                expected_source_sha256=definition.source_sha256,
            )

    def test_form_collects_tk_values_before_render_worker(self):
        source = inspect.getsource(company_template_draft_form_ui)
        self.assertIn("facts = collect_facts()", source)
        self.assertIn("expected_source_sha256=definition.source_sha256", source)
        self.assertIn("Taxo-company-template-draft-render", source)
        worker = source[source.index("        def worker():"):]
        self.assertNotIn(".get()", worker)
        self.assertNotIn("StringVar(", worker)

    def test_all_r4_fact_types_have_r5_controls(self):
        source = inspect.getsource(company_template_fact_widgets)
        for typ in (
            '"text"', '"date"', '"integer"', '"person_ref"',
            '"vehicle_ref"', '"participants"', '"pairs"',
            '"sections"', '"table_rows"',
        ):
            self.assertIn(typ, source)
        self.assertIn('selectmode="extended"', source)
        self.assertIn('"Додати пару"', source)
        self.assertIn('"Прибрати вибрану"', source)

    def test_preview_content_stays_read_only_without_export_or_business_action(self):
        source = inspect.getsource(company_template_draft_preview_ui)
        self.assertIn('state="disabled"', source)
        self.assertIn('"Закрити"', source)
        self.assertIn("WM_DELETE_WINDOW", source)
        self.assertNotIn("write_file", source)
        self.assertNotIn("DocumentArchive", source)
        self.assertNotIn("create_order(", source)
        self.assertNotIn("create_briefing", source)

    def test_company_template_list_exposes_draft_action(self):
        source = inspect.getsource(company_template_list_ui)
        self.assertIn('"Підготувати чернетку"', source)
        self.assertIn("open_company_template_draft_form", source)

    def test_choice_adapter_performs_no_sql_write_calls(self):
        source = inspect.getsource(choices)
        for marker in (
            ".execute(",
            ".executemany(",
            ".executescript(",
            ".commit(",
            ".rollback(",
        ):
            self.assertNotIn(marker, source)

    def test_r5_logic_stays_out_of_main(self):
        import main
        source = inspect.getsource(main)
        for marker in (
            "def open_company_template_draft_form",
            "def load_fact_choice_catalog",
            "def prepare_company_template_draft",
            "company_template_fact_widgets",
        ):
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
