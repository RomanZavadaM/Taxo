# -*- coding: utf-8 -*-
"""10.19-r4: typed facts create an in-memory preview draft only."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import company_template_draft as draft
import company_template_store as store


def _template():
    return {
        "format": "taxo.template.v1",
        "template_id": "orders.draft-test",
        "title": "Наказ {{company.name}}",
        "description": "Дата: {{order.date}}",
        "document_kind": "order",
        "scenario": "draft-preview",
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
                "label": "Дата наказу",
            },
            {
                "name": "order.number", "type": "integer", "required": True,
                "label": "Номер",
            },
            {
                "name": "manager", "type": "person_ref", "required": True,
                "label": "Керівник",
            },
            {
                "name": "assignment.rows", "type": "table_rows", "required": False,
                "label": "Водії та ТЗ",
            },
        ],
        "blocks": [
            {
                "id": "heading", "type": "heading", "level": 1,
                "text": "Наказ №{{order.number}}",
            },
            {
                "id": "body", "type": "paragraph",
                "text": "{{company.name}} · {{order.date}} · {{manager}}",
            },
            {
                "id": "pairs", "type": "dynamic_table",
                "data_source": "assignment.rows",
                "columns": ["Працівник", "Авто"],
                "rows": [],
            },
        ],
        "appendices": [
            {
                "id": "annex",
                "title": "Додаток до №{{order.number}}",
                "blocks": [{
                    "id": "annex-body", "type": "paragraph",
                    "text": "Підприємство: {{company.name}}",
                }],
            }
        ],
    }


def _write_library(root, template=None):
    template = template or _template()
    root.mkdir(parents=True)
    relative = "catalog/orders/draft-test.json"
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
            "template_id": template["template_id"],
            "revision_id": "v1",
            "category_id": "orders",
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


class CompanyTemplateDraftR4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "Work"
        self.work.mkdir()
        _write_library(self.work / "TemplateLibrary")
        self.summary = store.create_company_copy(
            self.work, "10.19-r4", "orders.draft-test", "v1"
        )

    def _facts(self):
        return {
            "company.name": "ТОВ «Приклад»",
            "order.date": date(2026, 11, 14),
            "order.number": 27,
            "manager": {"id": 8, "label": "Іван Петренко"},
            "assignment.rows": [
                ["Петро Водій", "AA 1234 BB"],
                ["Олена Водій", "BC 5678 CE"],
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

    def test_typed_scalar_and_table_facts_render_without_mutating_source(self):
        root = self.work / "CompanyTemplates"
        before = {
            p.relative_to(root): p.read_bytes()
            for p in root.rglob("*") if p.is_file()
        }
        result = draft.render_company_template_draft(
            self.work, self.summary.company_template_id, self._facts()
        )
        self.assertEqual(result.company_revision, 1)
        self.assertEqual(result.title, "Наказ ТОВ «Приклад»")
        for phrase in (
            "Наказ №27",
            "ТОВ «Приклад» · 14.11.2026 · Іван Петренко",
            "Петро Водій | AA 1234 BB",
            "Олена Водій | BC 5678 CE",
            "ДОДАТОК: Додаток до №27",
        ):
            self.assertIn(phrase, result.content)
        self.assertEqual(
            result.resolved_template["blocks"][2]["rows"][0],
            ["Петро Водій", "AA 1234 BB"],
        )
        after = {
            p.relative_to(root): p.read_bytes()
            for p in root.rglob("*") if p.is_file()
        }
        self.assertEqual(before, after)

    def test_missing_required_field_is_visible_error(self):
        facts = self._facts()
        facts.pop("order.date")
        with self.assertRaisesRegex(ValueError, "Дата наказу"):
            draft.render_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_wrong_type_is_visible_error(self):
        facts = self._facts()
        facts["order.number"] = "27"
        with self.assertRaisesRegex(ValueError, "Номер"):
            draft.render_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_unknown_fact_is_rejected(self):
        facts = self._facts()
        facts["secret.extra"] = "не дозволено"
        with self.assertRaisesRegex(ValueError, "немає у шаблоні"):
            draft.render_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_unknown_placeholder_is_rejected(self):
        template = _template()
        template["blocks"][1]["text"] = "{{undeclared.value}}"
        other = Path(self.temp.name) / "OtherWork"
        other.mkdir()
        _write_library(other / "TemplateLibrary", template)
        summary = store.create_company_copy(
            other, "10.19-r4", "orders.draft-test", "v1"
        )
        with self.assertRaisesRegex(ValueError, "невідоме поле"):
            draft.render_company_template_draft(
                other, summary.company_template_id, self._facts()
            )

    def test_complex_fact_cannot_be_inserted_as_scalar_text(self):
        template = _template()
        template["blocks"][1]["text"] = "{{assignment.rows}}"
        other = Path(self.temp.name) / "ComplexWork"
        other.mkdir()
        _write_library(other / "TemplateLibrary", template)
        summary = store.create_company_copy(
            other, "10.19-r4", "orders.draft-test", "v1"
        )
        with self.assertRaisesRegex(ValueError, "Структуроване поле"):
            draft.render_company_template_draft(
                other, summary.company_template_id, self._facts()
            )

    def test_table_width_must_match_columns(self):
        facts = self._facts()
        facts["assignment.rows"] = [["лише одна клітинка"]]
        with self.assertRaisesRegex(ValueError, "Кількість клітинок"):
            draft.render_company_template_draft(
                self.work, self.summary.company_template_id, facts
            )

    def test_fact_contract_lists_declared_types(self):
        fields = draft.list_draft_facts(
            self.work, self.summary.company_template_id
        )
        self.assertEqual(
            [(f.name, f.variable_type, f.required) for f in fields],
            [
                ("company.name", "text", True),
                ("order.date", "date", True),
                ("order.number", "integer", True),
                ("manager", "person_ref", True),
                ("assignment.rows", "table_rows", False),
            ],
        )

    def test_draft_module_has_no_execution_or_persistence_paths(self):
        source = Path(draft.__file__).read_text("utf-8")
        for marker in ("eval(", "exec(", "sqlite3", "subprocess", "os.replace"):
            self.assertNotIn(marker, source)
        self.assertNotIn("save_company_template", source)


if __name__ == "__main__":
    unittest.main()
