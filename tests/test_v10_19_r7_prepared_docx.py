# -*- coding: utf-8 -*-
"""10.19-r7: DOCX export renders only from an immutable prepared snapshot."""
from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

from docx import Document

from company_template_draft import CompanyTemplateDraft
from company_template_facts import DraftVariable
import company_template_draft_preview_ui
import prepared_document_docx as docx_export
import prepared_document_store as store


def _draft(block_type="paragraph"):
    rendered = {
        "format": "taxo.template.v1",
        "template_id": "orders.docx-export-test",
        "title": "Наказ № 17",
        "document_kind": "order",
        "scenario": "prepared-docx",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [],
        "blocks": [
            {"id": "h", "type": "heading", "level": 1, "text": "НАКАЗ № 17"},
            {"id": "p", "type": block_type, "text": "ТОВ «Тест» · Петренко Іван"},
            {"id": "list", "type": "numbered_list", "items": ["Перший пункт", "Другий пункт"]},
            {
                "id": "pairs",
                "type": "dynamic_table",
                "data_source": "assignment.pairs",
                "columns": ["Водій", "Транспортний засіб"],
                "rows": [
                    ["Петренко Іван", "AA1234BB"],
                    ["Коваль Петро", "BC5678CE"],
                ],
            },
            {"id": "signature", "type": "signature_placeholder", "text": "Керівник"},
        ],
        "appendices": [
            {
                "id": "a1",
                "title": "Додаток 1",
                "blocks": [{"id": "ap", "type": "paragraph", "text": "Текст додатка"}],
            }
        ],
    }
    return CompanyTemplateDraft(
        company_template_id="ct-" + ("a" * 32),
        source_sha256="b" * 64,
        edit_revision=7,
        title="Наказ № 17",
        content="НАКАЗ № 17\n\nТОВ «Тест» · Петренко Іван",
        variables=(
            DraftVariable(
                name="company.name",
                label="Підприємство",
                variable_type="text",
                required=True,
            ),
        ),
        normalized_facts={"company.name": "ТОВ «Тест»"},
        rendered_template=rendered,
    )


class PreparedDocumentDocxR7Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / "Work"
        self.work.mkdir()

    def test_revision_identity_accepts_r7_and_r8(self):
        root = Path(__file__).resolve().parents[1]
        self.assertIn(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            ("Version: 10.19-r7", "Version: 10.19-r8", "Version: 10.19-r9", "Version: 10.19-r10", "Version: 10.20-r1", "Version: 10.20-r2", "Version: 10.20-r3", "Version: 10.20-r4", "Version: 10.20-r5", "Version: 10.20-r6", "Version: 10.21-r7", "Version: 10.24-r6"),
        )
        self.assertTrue(
            any(v in (root / "main.py").read_text("utf-8") for v in (
                'APP_VERSION = "10.19-r7"', 'APP_VERSION = "10.19-r8"',
                'APP_VERSION = "10.19-r9"',
                'APP_VERSION = "10.19-r10"',
                'APP_VERSION = "10.20-r1"',
                'APP_VERSION = "10.20-r2"',
                'APP_VERSION = "10.20-r3"',
                'APP_VERSION = "10.20-r4"',
                'APP_VERSION = "10.20-r5"',
                'APP_VERSION = "10.20-r6"',
                'APP_VERSION = "10.24-r6"',
            ))
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertTrue(
            "Taxo 10.19-r7" in start
            or "Taxo 10.19-r8" in start
            or "Taxo 10.19-r9" in start
            or "Taxo 10.19-r10" in start
            or "Taxo 10.20-r1" in start
            or "Taxo 10.20-r2" in start
            or "Taxo 10.20-r3" in start
            or "Taxo 10.20-r4" in start
            or "Taxo 10.20-r5" in start
            or "Taxo 10.20-r6" in start
            or "Taxo 10.21-r7" in start
            or "Taxo 10.24-r6" in start
        )
        self.assertIn("prepared_document_docx.py", start)

    def test_docx_uses_committed_snapshot_and_preserves_provenance(self):
        summary = store.create_prepared_snapshot(self.work, _draft())
        item = self.work / "Data" / "PreparedDocuments" / "items" / summary.file_name
        before = item.read_bytes()
        target = self.root / "prepared.docx"

        result = docx_export.export_prepared_snapshot_docx(
            self.work, summary.snapshot_id, target
        )
        self.assertEqual(result, target)
        self.assertTrue(target.is_file())
        self.assertEqual(item.read_bytes(), before)

        document = Document(str(target))
        body = "\n".join(p.text for p in document.paragraphs)
        self.assertIn("НАКАЗ № 17", body)
        self.assertIn("ТОВ «Тест» · Петренко Іван", body)
        self.assertIn("Перший пункт", body)
        self.assertIn("Додаток 1", body)
        self.assertIn("Текст додатка", body)
        self.assertEqual(document.tables[0].cell(1, 0).text, "Петренко Іван")
        self.assertEqual(document.tables[0].cell(2, 1).text, "BC5678CE")

        provenance = document.core_properties.comments
        self.assertIn(summary.snapshot_id, provenance)
        self.assertIn("ct-" + ("a" * 32), provenance)
        self.assertIn("edit revision 7", provenance)
        self.assertIn("b" * 64, provenance)
        footer = document.sections[0].footer.paragraphs[0].text
        self.assertIn(summary.snapshot_id, footer)
        self.assertIn("b" * 64, footer)

    def test_export_refuses_existing_target_without_explicit_overwrite(self):
        summary = store.create_prepared_snapshot(self.work, _draft())
        target = self.root / "existing.docx"
        target.write_bytes(b"do-not-overwrite")
        with self.assertRaises(FileExistsError):
            docx_export.export_prepared_snapshot_docx(
                self.work, summary.snapshot_id, target
            )
        self.assertEqual(target.read_bytes(), b"do-not-overwrite")

    def test_unknown_snapshot_block_fails_without_partial_output(self):
        summary = store.create_prepared_snapshot(
            self.work, _draft(block_type="unsupported_block")
        )
        target = self.root / "invalid.docx"
        with self.assertRaisesRegex(ValueError, "Непідтримуваний тип"):
            docx_export.export_prepared_snapshot_docx(
                self.work, summary.snapshot_id, target
            )
        self.assertFalse(target.exists())

    def test_renderer_never_reloads_company_template_or_touches_final_flows(self):
        source = inspect.getsource(docx_export)
        for marker in (
            "company_template_store",
            "load_company_template",
            "create_order(",
            "create_briefing",
            "pypdf",
            "reportlab",
            "print(",
        ):
            self.assertNotIn(marker, source)
        self.assertIn("load_prepared_snapshot", source)

    def test_preview_enables_docx_only_after_snapshot_commit(self):
        source = inspect.getsource(company_template_draft_preview_ui)
        self.assertIn('"Експорт DOCX…"', source)
        self.assertIn("export_prepared_snapshot_docx", source)
        self.assertIn("Taxo-prepared-document-docx-export", source)
        self.assertIn('state="disabled"', source)
        self.assertIn('state["snapshot_id"] = payload.snapshot_id', source)
        self.assertLess(
            source.index("filedialog.asksaveasfilename"),
            source.index('name="Taxo-prepared-document-docx-export"'),
        )
        worker_tail = source[source.index("        def worker():"):]
        self.assertNotIn(".get()", worker_tail)
        self.assertNotIn("StringVar(", worker_tail)

    def test_prepared_docx_logic_stays_out_of_main(self):
        import main
        source = inspect.getsource(main)
        for marker in (
            "prepared_document_docx",
            "export_prepared_snapshot_docx",
            "build_prepared_snapshot_docx",
        ):
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
