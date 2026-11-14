# -*- coding: utf-8 -*-
"""10.19-r3: typed, non-persistent CompanyTemplates draft rendering."""
from __future__ import annotations

import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path

import company_template_draft as draft
import company_template_store as store


def _person(identity, name, position=""):
    return {
        "entity_type": "employee",
        "id": identity,
        "name": name,
        "position": position,
        "label": name + ((" — " + position) if position else ""),
    }


def _vehicle(identity, plate, name):
    return {
        "entity_type": "vehicle",
        "id": identity,
        "plate": plate,
        "name": name,
        "vin": "VIN%05d" % identity,
        "label": "%s · %s" % (plate, name),
    }


def _template(undeclared=False):
    trailing = " / {{missing.field}}" if undeclared else ""
    return {
        "format": "taxo.template.v1",
        "template_id": "instructions.draft-test",
        "title": "Чернетка {{order.number}}",
        "description": "Для {{company.name}}",
        "document_kind": "instruction",
        "scenario": "draft",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {
                "name": "company.name",
                "type": "text",
                "required": True,
                "label": "Підприємство",
            },
            {
                "name": "document.date",
                "type": "date",
                "required": True,
                "label": "Дата документа",
            },
            {
                "name": "order.number",
                "type": "integer",
                "required": True,
                "label": "Номер",
            },
            {
                "name": "employee.person",
                "type": "person_ref",
                "required": True,
                "label": "Працівник",
            },
            {
                "name": "vehicle.item",
                "type": "vehicle_ref",
                "required": False,
                "label": "Транспорт",
            },
            {
                "name": "assignment.pairs",
                "type": "pairs",
                "required": True,
                "label": "Пари водій–ТЗ",
            },
            {
                "name": "briefing.participants",
                "type": "participants",
                "required": False,
                "label": "Учасники",
            },
            {
                "name": "instruction.sections",
                "type": "sections",
                "required": False,
                "label": "Розділи",
            },
            {
                "name": "report.rows",
                "type": "table_rows",
                "required": True,
                "label": "Рядки звіту",
            },
        ],
        "blocks": [
            {
                "id": "heading",
                "type": "heading",
                "level": 1,
                "text": "Інструкція №{{order.number}} від {{document.date}}",
            },
            {
                "id": "body",
                "type": "paragraph",
                "text": (
                    "{{company.name}} / {{employee.person}} / "
                    "{{vehicle.item}}" + trailing
                ),
            },
            {
                "id": "pairs",
                "type": "dynamic_table",
                "columns": ["Працівник", "ТЗ"],
                "rows": [],
                "data_source": "assignment.pairs",
            },
            {
                "id": "report",
                "type": "dynamic_table",
                "columns": ["Поле", "Значення"],
                "rows": [],
                "data_source": "report.rows",
            },
            {
                "id": "participants",
                "type": "paragraph",
                "text": "Учасники:\n{{briefing.participants}}",
            },
            {
                "id": "sections",
                "type": "paragraph",
                "text": "Розділи:\n{{instruction.sections}}",
            },
        ],
        "appendices": [
            {
                "id": "annex",
                "title": "Додаток до №{{order.number}}",
                "blocks": [
                    {
                        "id": "annex-body",
                        "type": "paragraph",
                        "text": "Дата: {{document.date}}",
                    }
                ],
            }
        ],
    }


def _write_library(root, template=None):
    template = template or _template()
    root.mkdir(parents=True)
    relative = "catalog/instructions/draft-test.json"
    target = root / relative
    target.parent.mkdir(parents=True)
    raw = json.dumps(template, ensure_ascii=False).encode("utf-8")
    target.write_bytes(raw)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.draft.synthetic",
        "package_version": "3.0.0",
        "publisher": "Synthetic fixture",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": "instructions.draft-test",
            "revision_id": "v1",
            "category_id": "instructions",
            "path": relative,
        }],
        "files": [{
            "path": relative,
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )


def _facts():
    driver = _person(11, "Іваненко Іван", "водій")
    vehicle = _vehicle(21, "ВС 1234 АА", "MAN")
    return {
        "company.name": "ТОВ «Тест»",
        "document.date": "2026-11-14",
        "order.number": 42,
        "employee.person": driver,
        "vehicle.item": vehicle,
        "assignment.pairs": [
            {"person": driver, "vehicle": vehicle},
            {
                "person": _person(12, "Петренко Петро"),
                "vehicle": _vehicle(22, "ВС 5678 ВВ", "DAF"),
            },
        ],
        "briefing.participants": [
            driver,
            _person(12, "Петренко Петро"),
        ],
        "instruction.sections": [
            {"title": "1. Загальні положення", "text": "Безпечна робота."},
            "2. Дії перед виїздом",
        ],
        "report.rows": [
            ["Пробіг", 125],
            ["Допуск", True],
        ],
    }


class CompanyTemplateDraftR3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "Work"
        self.work.mkdir()
        _write_library(self.work / "TemplateLibrary")
        self.summary = store.create_company_copy(
            self.work, "10.19-r3", "instructions.draft-test", "v1"
        )

    def test_revision_identity_is_10_19_r3(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            "Version: 10.19-r3",
        )
        self.assertIn(
            'APP_VERSION = "10.19-r3"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.19-r3",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_required_fields_fail_explicitly(self):
        with self.assertRaisesRegex(ValueError, "обов'язкові поля"):
            draft.prepare_company_template_draft(
                self.work,
                self.summary.company_template_id,
                {"company.name": "ТОВ «Тест»"},
            )

    def test_scalar_facts_are_typed_and_rendered(self):
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, _facts()
        )
        self.assertEqual(result.title, "Чернетка 42")
        self.assertIn("Інструкція №42 від 14.11.2026", result.preview_text)
        self.assertIn("ТОВ «Тест»", result.preview_text)
        self.assertIn("Іваненко Іван — водій", result.preview_text)
        self.assertIn("ВС 1234 АА · MAN", result.preview_text)
        fact_map = {item.name: item for item in result.facts}
        self.assertEqual(fact_map["document.date"].snapshot, "2026-11-14")
        self.assertEqual(fact_map["order.number"].snapshot, 42)

    def test_dynamic_sources_become_concrete_static_tables(self):
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, _facts()
        )
        pairs = result.template["blocks"][2]
        report = result.template["blocks"][3]
        self.assertEqual(pairs["type"], "table")
        self.assertNotIn("data_source", pairs)
        self.assertEqual(
            pairs["rows"],
            [
                ["Іваненко Іван — водій", "ВС 1234 АА · MAN"],
                ["Петренко Петро", "ВС 5678 ВВ · DAF"],
            ],
        )
        self.assertEqual(report["type"], "table")
        self.assertEqual(
            report["rows"],
            [["Пробіг", "125"], ["Допуск", "Так"]],
        )
        self.assertNotIn("Таблиця заповнюється з даних", result.preview_text)

    def test_optional_missing_values_are_visible_not_silently_blank(self):
        facts = _facts()
        del facts["vehicle.item"]
        del facts["briefing.participants"]
        del facts["instruction.sections"]
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, facts
        )
        self.assertIn("⟦не заповнено: Транспорт⟧", result.preview_text)
        self.assertIn(
            "Не заповнено необов'язкове поле: Транспорт",
            result.warnings,
        )

    def test_person_vehicle_and_pair_snapshots_keep_stable_ids(self):
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, _facts()
        )
        facts = {item.name: item.snapshot for item in result.facts}
        self.assertEqual(facts["employee.person"]["id"], 11)
        self.assertEqual(facts["vehicle.item"]["id"], 21)
        self.assertEqual(facts["assignment.pairs"][0]["person"]["id"], 11)
        self.assertEqual(facts["assignment.pairs"][0]["vehicle"]["id"], 21)

    def test_draft_is_side_effect_free_for_company_storage(self):
        current = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        root = self.work / "CompanyTemplates"
        before_index = (root / "index.json").read_bytes()
        before_files = {
            path.name: path.read_bytes()
            for path in (root / "items").iterdir()
            if path.is_file()
        }
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, _facts()
        )
        after_files = {
            path.name: path.read_bytes()
            for path in (root / "items").iterdir()
            if path.is_file()
        }
        self.assertEqual((root / "index.json").read_bytes(), before_index)
        self.assertEqual(after_files, before_files)
        self.assertEqual(result.template_sha256, current.content_sha256)
        self.assertEqual(result.edit_revision, current.edit_revision)

    def test_rendered_copy_does_not_mutate_loaded_template(self):
        before = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        before_template = json.dumps(
            before.template, ensure_ascii=False, sort_keys=True
        )
        result = draft.prepare_company_template_draft(
            self.work, self.summary.company_template_id, _facts()
        )
        after = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        self.assertEqual(
            json.dumps(after.template, ensure_ascii=False, sort_keys=True),
            before_template,
        )
        self.assertEqual(after.template["blocks"][2]["type"], "dynamic_table")
        self.assertEqual(result.template["blocks"][2]["type"], "table")

    def test_unknown_fact_is_rejected_instead_of_ignored(self):
        facts = _facts()
        facts["typo.field"] = "x"
        with self.assertRaisesRegex(ValueError, "Невідомі поля"):
            draft.prepare_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_wrong_typed_values_are_rejected(self):
        cases = [
            ("document.date", "14/11/2026"),
            ("order.number", True),
            ("employee.person", "Іваненко"),
            ("vehicle.item", {"id": 1, "entity_type": "employee", "name": "X"}),
            ("assignment.pairs", ["Іваненко — MAN"]),
            ("report.rows", [["a"], ["b", "c"]]),
        ]
        for key, value in cases:
            with self.subTest(field=key):
                facts = _facts()
                facts[key] = value
                with self.assertRaises(ValueError):
                    draft.prepare_company_template_draft(
                        self.work, self.summary.company_template_id, facts
                    )

    def test_undeclared_placeholder_fails(self):
        other = Path(self.temp.name) / "Other"
        other.mkdir()
        _write_library(other / "TemplateLibrary", _template(undeclared=True))
        summary = store.create_company_copy(
            other, "10.19-r3", "instructions.draft-test", "v1"
        )
        with self.assertRaisesRegex(ValueError, "неоголошене поле"):
            draft.prepare_company_template_draft(
                other, summary.company_template_id, _facts()
            )

    def test_engine_contains_no_db_write_or_code_execution_path(self):
        source = inspect.getsource(draft)
        for forbidden in (
            "sqlite3",
            ".execute(",
            ".commit(",
            "subprocess",
            "eval(",
            "exec(",
            "os.system",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("copy.deepcopy", source)
        self.assertIn("render_template_text", source)


if __name__ == "__main__":
    unittest.main()
