# -*- coding: utf-8 -*-
"""10.18-r8: literal, safe template preview with no edit or document generation."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from template_library_preview import _render, load_template_preview
from template_library_preview_ui import open_template_preview
import template_library_preview


def _template():
    return {
        "format": "taxo.template.v1", "template_id": "orders.preview-test",
        "title": "Тест без персональних даних", "document_kind": "order",
        "scenario": "preview", "language": "uk", "status": "proposed",
        "legal_review": "requires_review", "source_refs": [],
        "variables": [{"name": "company.name", "type": "text",
                       "required": True, "label": "Назва підприємства"}],
        "blocks": [
            {"id": "heading", "type": "heading", "level": 1, "text": "Наказ"},
            {"id": "intro", "type": "paragraph",
             "text": "Назва: {{company.name}}"},
            {"id": "list", "type": "numbered_list",
             "items": ["Перший пункт", "Другий пункт"]},
            {"id": "table", "type": "table",
             "columns": ["А", "Б"], "rows": [["один", "два"]]},
            {"id": "dynamic", "type": "dynamic_table",
             "data_source": "vehicle_pairs", "columns": ["Водій", "Авто"]},
            {"id": "signature", "type": "signature_placeholder",
             "text": "Підпис керівника"},
        ],
        "appendices": [
            {"id": "annex", "title": "Додаток №1",
             "blocks": [{"id": "annex-text", "type": "paragraph",
                         "text": "Текст додатка"}]},
        ],
    }


def _write_package(root, template=None):
    data = template if template is not None else _template()
    path = "catalog/orders/preview-test.json"
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    target.write_bytes(payload)
    manifest = {
        "format": "taxo.template-catalog.v1", "package_id": "taxo.preview.synthetic",
        "package_version": "0.1.0", "publisher": "Regression fixture",
        "minimum_taxo_version": "10.18-r5", "language": "uk",
        "items": [{"template_id": data["template_id"], "revision_id": "v1",
                   "category_id": "orders", "path": path}],
        "files": [{"path": path, "size_bytes": len(payload),
                   "sha256": hashlib.sha256(payload).hexdigest()}],
    }
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return target


class TemplateLibraryPreviewR8Tests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "TemplateLibrary"
        self.root.mkdir()

    def test_text_fields_tables_and_appendices_not_evaluated(self):
        _write_package(self.root)
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        preview = load_template_preview(
            self.root, "10.18-r8", "orders.preview-test", "v1"
        )
        for phrase in ("Наказ", "Перший пункт", "Другий пункт", "А | Б",
                       "один | два", "Таблиця заповнюється", "Підпис керівника",
                       "Додаток №1", "Текст додатка", "{{company.name}}"):
            self.assertIn(phrase, preview.content)
        self.assertEqual(preview.legal_review, "requires_review")
        self.assertEqual(preview.variables[0].name, "company.name")
        self.assertTrue(preview.variables[0].required)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes()
                                  for p in self.root.rglob("*") if p.is_file()})

    def test_preview_rejects_changed_hash(self):
        p = _write_package(self.root)
        p.write_text("corrupted", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_template_preview(self.root, "10.18-r8", "orders.preview-test", "v1")

    def test_missing_revision_rejected(self):
        _write_package(self.root)
        with self.assertRaises(ValueError):
            load_template_preview(self.root, "10.18-r8", "orders.preview-test", "v2")

    def test_traversal_in_requested_identity_cannot_open_unlisted_file(self):
        _write_package(self.root)
        with self.assertRaises(ValueError):
            load_template_preview(self.root, "10.18-r8", "../../other", "v1")

    def test_depth_limit_in_renderer(self):
        block = {"id": "leaf", "type": "paragraph", "text": "test"}
        for _ in range(template_library_preview.MAX_BLOCK_DEPTH + 2):
            block = {"id": "parent", "type": "paragraph", "text": "parent",
                     "children": [block]}
        t = _template()
        t["blocks"] = [block]
        with self.assertRaises(ValueError):
            _render(t)

    def test_long_form_content_is_not_truncated_under_limit(self):
        t = _template()
        t["blocks"] = [{"id": "long-text", "type": "paragraph",
                        "text": "Рядок " * 14000}]
        rendered = _render(t)
        self.assertGreater(len(rendered), 50000)
        self.assertEqual(rendered.count("Рядок"), 14000)

    def test_preview_gui_is_readonly_and_has_two_tabs_and_close(self):
        import inspect
        src = inspect.getsource(open_template_preview)
        for value in ('"Текст та додатки"', '"Поля для заповнення"',
                      '"Закрити"', '"WM_DELETE_WINDOW"', 'state="disabled"',
                      "threading.Thread", "_PREVIEW_READER_SLOT"):
            self.assertIn(value, src)
        self.assertNotIn("exec(", src)
        self.assertNotIn("eval(", src)

    def test_no_private_catalog_documents_in_public_fixtures(self):
        import inspect
        src = inspect.getsource(template_library_preview)
        self.assertNotIn("roman_mmg2lw7", src)
        self.assertNotIn("transport-docs-catalog", src)


if __name__ == "__main__":
    unittest.main()
