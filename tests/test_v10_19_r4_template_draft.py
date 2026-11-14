# -*- coding: utf-8 -*-
"""10.19-r4: typed facts render an in-memory CompanyTemplates preview."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import company_template_draft as draft
import company_template_store as store


def _template(extra_placeholder=False):
    tail = " {{unknown.field}}" if extra_placeholder else ""
    return {
        "format": "taxo.template.v1",
        "template_id": "orders.typed-draft-test",
        "title": "Наказ {{order.no}}",
        "description": "Чернетка {{company.name}}",
        "document_kind": "order",
        "scenario": "typed-preview",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {
                "name": "company.name",
                "type": "text",
                "required": True,
                "label": "Назва підприємства",
            },
            {
                "name": "order.date",
                "type": "date",
                "required": True,
                "label": "Дата наказу",
            },
            {
                "name": "order.no",
                "type": "integer",
                "required": True,
                "label": "Номер наказу",
            },
            {
                "name": "driver",
                "type": "person_ref",
                "required": True,
                "label": "Водій",
            },
            {
                "name": "vehicle",
                "type": "vehicle_ref",
                "required": False,
                "label": "Транспортний засіб",
            },
            {
                "name": "assignment.pairs",
                "type": "pairs",
                "required": True,
                "label": "Пари водій–ТЗ",
            },
            {
                "name": "participants",
                "type": "participants",
                "required": False,
                "label": "Учасники",
            },
            {
                "name": "sections",
                "type": "sections",
                "required": False,
                "label": "Розділи",
            },
            {
                "name": "table.rows",
                "type": "table_rows",
                "required": False,
                "label": "Додаткова таблиця",
            },
        ],
        "blocks": [
            {
                "id": "heading",
                "type": "heading",
                "level": 1,
                "text": "Наказ № {{order.no}}",
            },
            {
                "id": "intro",
                "type": "paragraph",
                "text": (
                    "{{company.name}} · {{order.date}} · "
                    "{{driver.name}} · {{driver.position}} · "
                    "{{vehicle.plate}}" + tail
                ),
            },
            {
                "id": "pairs",
                "type": "dynamic_table",
                "data_source": "assignment.pairs",
                "columns": ["Водій", "Транспортний засіб"],
            },
            {
                "id": "participants",
                "type": "dynamic_table",
                "data_source": "participants",
                "columns": ["Учасник"],
            },
            {
                "id": "extra-table",
                "type": "dynamic_table",
                "data_source": "table.rows",
                "columns": ["A", "B"],
            },
            {
                "id": "sections",
                "type": "paragraph",
                "text": "{{sections}}",
            },
        ],
        "appendices": [
            {
                "id": "annex",
                "title": "Додаток до наказу № {{order.no}}",
                "blocks": [
                    {
                        "id": "annex-text",
                        "type": "paragraph",
                        "text": "Водій: {{driver.name}}",
                    }
                ],
            }
        ],
    }


def _write_vendor_library(root, template=None):
    root.mkdir(parents=True)
    data = template if template is not None else _template()
    path = "catalog/orders/typed-draft-test.json"
    target = root / path
    target.parent.mkdir(parents=True)
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    target.write_bytes(raw)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.typed-draft.synthetic",
        "package_version": "1.0.0",
        "publisher": "Synthetic fixture",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": data["template_id"],
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
        json.dumps(manifest, ensure_ascii=False),
        encoding="utf-8",
    )


def _person(identity, name, position=""):
    return {
        "entity_type": "employee",
        "id": identity,
        "name": name,
        "position": position,
        "personnel_no": "T-%d" % identity,
    }


def _vehicle(identity, plate, name):
    return {
        "entity_type": "vehicle",
        "id": identity,
        "plate": plate,
        "name": name,
        "vin": "VIN%05d" % identity,
        "garage_no": "",
    }


class TypedCompanyTemplateDraftR4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "Work"
        self.work.mkdir()
        self.vendor = self.work / "TemplateLibrary"
        _write_vendor_library(self.vendor)
        self.summary = store.create_company_copy(
            self.work, "10.19-r4", "orders.typed-draft-test", "v1"
        )
        self.driver = _person(11, "Петренко Іван", "водій")
        self.vehicle = _vehicle(21, "AA1234BB", "DAF XF")

    def facts(self):
        return {
            "company.name": "ТОВ «Тест»",
            "order.date": date(2026, 11, 14),
            "order.no": 17,
            "driver": self.driver,
            "vehicle": self.vehicle,
            "assignment.pairs": [
                {"person": self.driver, "vehicle": self.vehicle},
                {
                    "person": _person(12, "Коваль Петро", "водій"),
                    "vehicle": _vehicle(22, "BC5678CE", "MAN TGX"),
                },
            ],
            "participants": [
                self.driver,
                _person(12, "Коваль Петро", "водій"),
            ],
            "sections": [
                "Перший структурований розділ.",
                "Другий структурований розділ.",
            ],
            "table.rows": [
                ["значення 1", 2],
                ["значення 3", date(2026, 12, 1)],
            ],
        }

    def test_revision_identity_is_r4(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            "Version: 10.19-r4",
        )
        self.assertIn(
            'APP_VERSION = "10.19-r4"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.19-r4",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_typed_facts_render_structurally(self):
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, self.facts()
        )
        self.assertEqual(result.title, "Наказ 17")
        for phrase in (
            "ТОВ «Тест»",
            "14.11.2026",
            "Петренко Іван",
            "водій",
            "AA1234BB",
            "DAF XF",
            "Коваль Петро",
            "BC5678CE",
            "Перший структурований розділ.",
            "Другий структурований розділ.",
            "01.12.2026",
            "ДОДАТОК: Додаток до наказу № 17",
        ):
            self.assertIn(phrase, result.content)

        pairs = result.rendered_template["blocks"][2]["rows"]
        self.assertEqual(len(pairs), 2)
        self.assertEqual(len(pairs[0]), 2)
        participants = result.rendered_template["blocks"][3]["rows"]
        self.assertEqual(len(participants), 2)
        table_rows = result.rendered_template["blocks"][4]["rows"]
        self.assertEqual(table_rows[0], ["значення 1", "2"])
        self.assertEqual(table_rows[1], ["значення 3", "01.12.2026"])

    def test_preview_does_not_write_template_database_or_archive(self):
        before = {
            path.relative_to(self.work): path.read_bytes()
            for path in self.work.rglob("*") if path.is_file()
        }
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, self.facts()
        )
        self.assertTrue(result.content)
        after = {
            path.relative_to(self.work): path.read_bytes()
            for path in self.work.rglob("*") if path.is_file()
        }
        self.assertEqual(before, after)
        self.assertFalse((self.work / "Data").exists())
        self.assertFalse((self.work / "DocumentArchive").exists())

    def test_required_missing_field_is_visible_error(self):
        facts = self.facts()
        facts.pop("company.name")
        with self.assertRaisesRegex(ValueError, "Назва підприємства"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_wrong_types_are_rejected(self):
        facts = self.facts()
        facts["order.no"] = True
        with self.assertRaisesRegex(ValueError, "Номер наказу"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

        facts = self.facts()
        facts["order.date"] = "14.11.2026"
        with self.assertRaisesRegex(ValueError, "Дата наказу"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

        facts = self.facts()
        facts["driver"] = {"name": "Без ID"}
        with self.assertRaisesRegex(ValueError, "Водій"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_extra_fact_is_rejected_instead_of_silently_ignored(self):
        facts = self.facts()
        facts["secret.extra"] = "не оголошено"
        with self.assertRaisesRegex(ValueError, "невідомі поля"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_unknown_placeholder_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td) / "Work"
            work.mkdir()
            _write_vendor_library(
                work / "TemplateLibrary",
                _template(extra_placeholder=True),
            )
            summary = store.create_company_copy(
                work, "10.19-r4", "orders.typed-draft-test", "v1"
            )
            with self.assertRaisesRegex(ValueError, "невідоме поле"):
                draft.prepare_company_template_draft(
                    work, summary.company_template_id, self.facts()
                )

    def test_dynamic_table_width_mismatch_is_rejected(self):
        facts = self.facts()
        facts["table.rows"] = [["only-one-cell"]]
        with self.assertRaisesRegex(ValueError, "Кількість клітинок"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_source_revision_and_sha_are_carried_to_draft(self):
        current = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, self.facts()
        )
        self.assertEqual(result.source_sha256, current.content_sha256)
        self.assertEqual(result.edit_revision, current.edit_revision)
        self.assertEqual(
            result.company_template_id,
            self.summary.company_template_id,
        )

    def test_variable_contract_is_read_only(self):
        variables = draft.list_draft_variables(
            self.work, self.summary.company_template_id
        )
        by_name = {item.name: item for item in variables}
        self.assertEqual(by_name["company.name"].variable_type, "text")
        self.assertTrue(by_name["company.name"].required)
        self.assertEqual(by_name["assignment.pairs"].variable_type, "pairs")
        self.assertEqual(by_name["driver"].variable_type, "person_ref")


if __name__ == "__main__":
    unittest.main()
