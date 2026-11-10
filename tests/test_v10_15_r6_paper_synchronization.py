# -*- coding: utf-8 -*-
"""Exercise paper-document writes and backup with controlled thread barriers."""
import json
import tempfile
import threading
import unittest
from pathlib import Path

import paper_documents as paper
import workspace
from paper_documents_lock import paper_documents_lock


class _Document:
    def __init__(self, payload, entered=None, proceed=None):
        self.payload = payload
        self.entered = entered
        self.proceed = proceed

    def save(self, target):
        if self.entered:
            self.entered.set()
            if not self.proceed.wait(10):
                raise RuntimeError("test barrier timed out")
        Path(target).write_bytes(self.payload)


class PaperDocumentSynchronizationTests(unittest.TestCase):
    def test_two_writers_keep_both_records_and_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "workspace"
            entered, proceed = threading.Event(), threading.Event()
            errors = []
            def save(doc, title):
                try:
                    paper.save_document(root, doc, "test", title, "2026-11-10")
                except Exception as exc:
                    errors.append(exc)

            first = threading.Thread(target=save, args=(_Document(b"one", entered, proceed), "one"))
            second = threading.Thread(target=save, args=(_Document(b"two"), "two"))
            first.start()
            self.assertTrue(entered.wait(5))
            second.start()
            try:
                self.assertFalse((root / "Data/PaperDocuments/index.json").exists())
            finally:
                proceed.set()
                first.join(10)
                second.join(10)
            self.assertFalse(first.is_alive() or second.is_alive())
            self.assertEqual(errors, [])
            records = paper.list_documents(root)
            self.assertEqual({r["title"] for r in records}, {"one", "two"})
            self.assertEqual({paper.document_path(root, r).read_bytes() for r in records}, {b"one", b"two"})

    def test_backup_waits_for_inflight_paper_write_and_copies_complete_record(self):
        with tempfile.TemporaryDirectory() as td:
            root, stage = Path(td) / "workspace", Path(td) / "backup"
            stage.mkdir()
            entered, proceed, backup_started, backup_done = (threading.Event() for _ in range(4))
            errors = []
            def save():
                try:
                    paper.save_document(root, _Document(b"document", entered, proceed),
                                        "test", "complete", "2026-11-10")
                except Exception as exc:
                    errors.append(exc)
            def backup():
                backup_started.set()
                try:
                    workspace._copy_backup_payload(root, stage)
                except Exception as exc:
                    errors.append(exc)
                finally:
                    backup_done.set()
            writer = threading.Thread(target=save)
            copier = threading.Thread(target=backup)
            writer.start()
            self.assertTrue(entered.wait(5))
            copier.start()
            self.assertTrue(backup_started.wait(5))
            try:
                self.assertFalse(backup_done.wait(0.2), "backup bypassed the paper-document lock")
            finally:
                proceed.set()
                writer.join(10)
                copier.join(10)
            self.assertFalse(writer.is_alive() or copier.is_alive())
            self.assertEqual(errors, [])
            records = json.loads((stage / "Data/PaperDocuments/index.json").read_text("utf-8"))
            self.assertEqual(len(records), 1)
            self.assertEqual((stage / "Data/PaperDocuments" / records[0]["file"]).read_bytes(), b"document")

    def test_equivalent_paths_share_lock(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIs(paper_documents_lock(td), paper_documents_lock(Path(td) / "."))


if __name__ == "__main__":
    unittest.main()
