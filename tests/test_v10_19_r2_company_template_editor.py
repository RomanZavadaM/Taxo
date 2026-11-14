# -*- coding: utf-8 -*-
"""10.19-r2: editable, versioned CompanyTemplates copies."""
from __future__ import annotations

import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path

import company_template_editor_service as editor
import company_template_editor_ui
import company_template_store as store
import template_library_ui


def _vendor_template():
    return {
        "format": "taxo.template.v1",
        "template_id": "instructions.editor-test",
        "title": "Редагований тестовий шаблон",
        "description": "Опис шаблону",
        "document_kind": "instruction",
        "scenario": "editor",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {"name": "company.name", "type": "text", "required": True}
        ],
        "blocks": [
            {
                "id": "heading",
                "type": "heading",
                "level": 1,
                "text": "Інструкція",
            },
            {
                "id": "body",
                "type": "paragraph",
                "text": "Початковий великий текст {{company.name}}",
            },
            {
                "id": "list",
                "type": "numbered_list",
                "items": ["Перший пункт", "Другий пункт"],
            },
            {
                "id": "table",
                "type": "table",
                "columns": ["Колонка А", "Колонка Б"],
                "rows": [["А1", "Б1"]],
            },
        ],
        "appendices": [
            {
                "id": "annex",
                "title": "Додаток 1",
                "blocks": [
                    {
                        "id": "annex-body",
                        "type": "paragraph",
                        "text": "Текст додатка",
                    }
                ],
            }
        ],
    }


def _write_vendor_library(root):
    root.mkdir(parents=True)
    path = "catalog/instructions/editor-test.json"
    target = root / path
    target.parent.mkdir(parents=True)
    raw = json.dumps(_vendor_template(), ensure_ascii=False).encode("utf-8")
    target.write_bytes(raw)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.editor.synthetic",
        "package_version": "2.0.0",
        "publisher": "Synthetic fixture",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": "instructions.editor-test",
            "revision_id": "v1",
            "category_id": "instructions",
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
    return target


class CompanyTemplateEditorR2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "Work"
        self.work.mkdir()
        self.vendor = self.work / "TemplateLibrary"
        self.vendor_file = _write_vendor_library(self.vendor)
        self.summary = store.create_company_copy(
            self.work, "10.19-r2", "instructions.editor-test", "v1"
        )

    def test_revision_identity_is_10_19_r2(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            "Version: 10.19-r2",
        )
        self.assertIn(
            'APP_VERSION = "10.19-r2"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.19-r2",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_editor_exposes_text_not_structure(self):
        model = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        keys = {item.key for item in model.fields}
        self.assertIn("description", keys)
        self.assertIn("blocks/1/text", keys)
        self.assertIn("blocks/2/items/0", keys)
        self.assertIn("blocks/3/rows/0/1", keys)
        self.assertIn("appendices/0/title", keys)
        self.assertIn("appendices/0/blocks/0/text", keys)
        self.assertNotIn("template_id", keys)
        self.assertNotIn("variables/0/name", keys)
        self.assertNotIn("blocks/0/type", keys)

    def test_save_creates_new_revision_and_preserves_vendor(self):
        vendor_before = self.vendor_file.read_bytes()
        first = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        values = {field.key: field.value for field in first.fields}
        values["blocks/1/text"] = "Змінений текст підприємства"
        saved = editor.save_editor_model(
            self.work,
            first.company_template_id,
            first.expected_sha256,
            "Власна інструкція підприємства",
            values,
        )
        self.assertEqual(saved.edit_revision, 2)
        self.assertNotEqual(saved.expected_sha256, first.expected_sha256)
        self.assertEqual(self.vendor_file.read_bytes(), vendor_before)

        current = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        self.assertEqual(current.title, "Власна інструкція підприємства")
        self.assertEqual(
            current.template["blocks"][1]["text"],
            "Змінений текст підприємства",
        )
        self.assertEqual(current.template["template_id"], "instructions.editor-test")
        self.assertEqual(current.template["variables"][0]["name"], "company.name")

    def test_large_instruction_text_is_not_truncated(self):
        model = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        values = {field.key: field.value for field in model.fields}
        large = ("Великий текст інструктажу. " * 12000).strip()
        self.assertGreater(len(large), 200000)
        values["blocks/1/text"] = large
        saved = editor.save_editor_model(
            self.work,
            model.company_template_id,
            model.expected_sha256,
            model.title,
            values,
        )
        reloaded = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        body = next(
            field.value for field in reloaded.fields
            if field.key == "blocks/1/text"
        )
        self.assertEqual(body, large)
        self.assertEqual(saved.edit_revision, 2)

    def test_second_editor_cannot_silently_overwrite_first(self):
        first = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        second = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        first_values = {field.key: field.value for field in first.fields}
        first_values["blocks/1/text"] = "Перше збереження"
        editor.save_editor_model(
            self.work,
            first.company_template_id,
            first.expected_sha256,
            first.title,
            first_values,
        )

        second_values = {field.key: field.value for field in second.fields}
        second_values["blocks/1/text"] = "Не має перезаписати"
        with self.assertRaises(ValueError):
            editor.save_editor_model(
                self.work,
                second.company_template_id,
                second.expected_sha256,
                second.title,
                second_values,
            )
        current = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        self.assertEqual(current.template["blocks"][1]["text"], "Перше збереження")

    def test_previous_revision_file_is_preserved(self):
        before = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        before_path = (
            self.work / "CompanyTemplates" / "items" / before.summary.file_name
        )
        before_bytes = before_path.read_bytes()
        model = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        values = {field.key: field.value for field in model.fields}
        values["blocks/0/text"] = "Нова назва у тексті"
        editor.save_editor_model(
            self.work,
            model.company_template_id,
            model.expected_sha256,
            model.title,
            values,
        )
        current = store.load_company_template(
            self.work, self.summary.company_template_id
        )
        self.assertNotEqual(current.summary.file_name, before.summary.file_name)
        self.assertTrue(before_path.is_file())
        self.assertEqual(before_path.read_bytes(), before_bytes)
        current_path = (
            self.work / "CompanyTemplates" / "items" / current.summary.file_name
        )
        data = json.loads(current_path.read_text("utf-8"))
        self.assertEqual(data["edit_revision"], 2)
        self.assertEqual(
            data["previous_revision"]["file"], before.summary.file_name
        )
        self.assertEqual(
            data["previous_revision"]["sha256"],
            hashlib.sha256(before_bytes).hexdigest(),
        )

    def test_unknown_editor_key_cannot_change_structure(self):
        model = editor.load_editor_model(
            self.work, self.summary.company_template_id
        )
        values = {field.key: field.value for field in model.fields}
        values["blocks/0/type"] = "page_break"
        with self.assertRaises(ValueError):
            editor.save_editor_model(
                self.work,
                model.company_template_id,
                model.expected_sha256,
                model.title,
                values,
            )

    def test_editor_ui_has_save_cancel_x_warning_and_workers(self):
        source = inspect.getsource(company_template_editor_ui)
        for phrase in (
            '"Зберегти"',
            '"Скасувати"',
            '"WM_DELETE_WINDOW"',
            '"Незбережені зміни"',
            "Taxo-company-template-save",
            "Taxo-company-template-editor-load",
            "fit_window_to_screen",
        ):
            self.assertIn(phrase, source)
        self.assertIn("Власні шаблони", inspect.getsource(template_library_ui))
        self.assertNotIn("exec(", source)
        self.assertNotIn("eval(", source)

    def test_editor_logic_does_not_move_into_main(self):
        import main
        source = inspect.getsource(main)
        self.assertNotIn("def save_company_template", source)
        self.assertNotIn("CompanyTemplates", source)
        self.assertNotIn("company_template_editor", source)


if __name__ == "__main__":
    unittest.main()
