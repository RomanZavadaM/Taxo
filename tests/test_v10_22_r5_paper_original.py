# -*- coding: utf-8 -*-
"""10.22-r10: explicit paper confirmation, corrections and catalog display."""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from docx import Document
from paper_document_store import save_docx_bytes, list_documents
from document_vault_store import register_prepared_revision
from paper_original_confirmation import (
    list_paper_original_states, set_paper_original_state,
)
from document_catalog import read_sources


class PaperOriginalConfirmationR5Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        document = Document()
        document.add_paragraph("Документ для підписання")
        data = io.BytesIO()
        document.save(data)
        contents = data.getvalue()
        saved = save_docx_bytes(
            self.root, contents, "Інструкція", "Паперовий підпис",
            "2026-11-18",
            metadata={
                "origin": "prepared_snapshot",
                "document_status": "prepared",
                "prepared_snapshot_id": "pd-" + "4" * 32,
                "company_template_id": "ct-" + "5" * 32,
                "template_revision": 1,
                "template_source_sha256": "a" * 64,
                "content_sha256": hashlib.sha256(contents).hexdigest(),
            },
        )
        source = next(item for item in list_documents(self.root) if item["file"] == saved.name)
        self.record = register_prepared_revision(self.root, source["id"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_mark_signed_without_scan_and_show_in_catalog(self):
        self.assertEqual(list_paper_original_states(self.root), {})
        state = set_paper_original_state(self.root, self.record.vault_id, True, "2026-11-17")
        self.assertTrue(state.signed)
        self.assertEqual(state.signed_date, "2026-11-17")
        row = next(item for item in read_sources(self.root)["rows"] if item["vault_id"] == self.record.vault_id)
        self.assertTrue(row["paper_original_signed"])
        self.assertEqual(row["paper_original_state"], "Підписано: 2026-11-17")
        self.assertEqual(row["paper_scan_count"], 0)

    def test_unmark_keeps_history_and_does_not_change_scan(self):
        set_paper_original_state(self.root, self.record.vault_id, True, "2026-11-17")
        set_paper_original_state(self.root, self.record.vault_id, False)
        state = list_paper_original_states(self.root)[self.record.vault_id]
        self.assertFalse(state.signed)
        path = self.root / "Data" / "DocumentVault" / "paper_original_events.json"
        self.assertEqual(len(__import__("json").loads(path.read_text("utf-8"))["events"]), 2)
        row = next(item for item in read_sources(self.root)["rows"] if item["vault_id"] == self.record.vault_id)
        self.assertEqual(row["paper_original_state"], "Не позначено")

    def test_invalid_date_and_unknown_id_fail_without_writing(self):
        with self.assertRaises(ValueError):
            set_paper_original_state(self.root, self.record.vault_id, True, "2026-14-99")
        with self.assertRaises(ValueError):
            set_paper_original_state(self.root, "vd-" + "0" * 32, True, "2026-11-17")
        self.assertFalse((self.root / "Data" / "DocumentVault" / "paper_original_events.json").exists())

    def test_corrupt_history_is_not_silently_overwritten(self):
        path = self.root / "Data" / "DocumentVault" / "paper_original_events.json"
        path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(ValueError):
            set_paper_original_state(self.root, self.record.vault_id, True, "2026-11-17")
        self.assertEqual(path.read_text("utf-8"), "{invalid")


if __name__ == "__main__":
    unittest.main()
