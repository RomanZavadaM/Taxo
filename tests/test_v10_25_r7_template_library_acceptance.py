# -*- coding: utf-8 -*-
"""10.25-r7 regression for template-library UX and briefing paper output."""
from __future__ import annotations

import hashlib
import inspect
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taxo"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import briefing_preparation
import company_template_store
import paper_documents
import template_library_service
import template_library_ui


def _write_library(workspace):
    root = Path(workspace) / "TemplateLibrary"
    rel = "catalog/training/program.json"
    target = root / rel
    target.parent.mkdir(parents=True)
    template = {
        "format": "taxo.template.v1",
        "template_id": "training.synthetic-r7",
        "title": "Синтетична програма r7",
        "document_kind": "instruction_program",
        "scenario": "briefing-program",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {
                "name": "company_name",
                "label": "Назва підприємства",
                "type": "text",
                "required": True,
            }
        ],
        "blocks": [
            {"id": "body", "type": "paragraph", "text": "Текст програми."}
        ],
    }
    raw = json.dumps(template, ensure_ascii=False).encode("utf-8")
    target.write_bytes(raw)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.synthetic-r7",
        "package_version": "1.0.0",
        "publisher": "Synthetic fixture",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": "training.synthetic-r7",
            "revision_id": "v1",
            "category_id": "training-programs",
            "path": rel,
        }],
        "files": [{
            "path": rel,
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )


class TemplateLibraryAcceptanceR7Test(unittest.TestCase):
    def test_existing_copy_is_resolved_instead_of_becoming_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_library(workspace)
            created = company_template_store.create_company_copy(
                workspace, "10.25-r6", "training.synthetic-r7", "v1"
            )
            found = company_template_store.find_company_template_by_source(
                workspace, "training.synthetic-r7", "v1"
            )
            self.assertIsNotNone(found)
            self.assertEqual(found.company_template_id, created.company_template_id)

    def test_library_uses_human_document_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_library(workspace)
            view = template_library_service.inspect_workspace_library(
                workspace, "10.25-r6"
            )
            self.assertEqual(view.rows[0].kind, "Навчальна програма")

    def test_library_ui_has_direct_edit_and_fill_workflow(self):
        source = inspect.getsource(template_library_ui.open_template_library)
        self.assertIn("Створити власну копію", source)
        self.assertIn("Заповнити поля / підготувати", source)
        self.assertIn("find_workspace_company_copy", source)
        self.assertIn("open_company_template_editor", source)
        self.assertIn("open_company_template_draft_form", source)

    def test_preparation_keeps_position_and_human_revision(self):
        prepared = briefing_preparation.prepare_list(
            "Охорона праці",
            "Повторний",
            "28.11.2026",
            "Повторний інструктаж",
            ["Іваненко Іван"],
            people_records=[{
                "id": 7,
                "name": "Іваненко Іван",
                "position": "Водій автобуса",
                "personnel_no": "1234567890",
            }],
            program_text="1. Безпечна робота.",
            template_id="bp-secret:r4",
            program_revision="r4",
        )
        self.assertEqual(prepared["program_revision"], "r4")
        self.assertEqual(prepared["people_records"][0]["position"], "Водій автобуса")

    def test_briefing_docx_is_a4_and_signature_sheet_uses_position(self):
        prepared = {
            "direction": "Охорона праці",
            "kind": "Повторний",
            "day": date(2026, 11, 28),
            "topic": "Повторний інструктаж",
            "reason": "",
            "program_text": "1. Безпечна робота.",
            "template_id": "internal-program:r4",
            "program_revision": "r4",
            "source_note": "Локальна програма",
            "approved_by": "Директор Петро Петренко",
            "people": ("Іваненко Іван",),
            "people_records": ({
                "name": "Іваненко Іван",
                "position": "Водій автобуса",
                "personnel_no": "1234567890",
            },),
        }
        doc = paper_documents.build_briefing_docx(prepared)
        section = doc.sections[0]
        self.assertAlmostEqual(section.page_width.cm, 21.0, places=1)
        self.assertAlmostEqual(section.page_height.cm, 29.7, places=1)
        text = "\n".join(p.text for p in doc.paragraphs)
        self.assertIn("Редакція програми: r4", text)
        self.assertNotIn("internal-program:r4", text)
        table_text = "\n".join(
            cell.text for row in doc.tables[0].rows for cell in row.cells
        )
        self.assertIn("Посада", table_text)
        self.assertIn("Водій автобуса", table_text)
        self.assertNotIn("Таб. №", table_text)
        self.assertNotIn("1234567890", table_text)


if __name__ == "__main__":
    unittest.main()
