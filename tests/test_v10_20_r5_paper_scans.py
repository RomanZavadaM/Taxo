# -*- coding: utf-8 -*-
import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from docx import Document

from document_vault_paper_scans import (
    list_paper_scans,
    load_paper_scan,
    paper_scan_root,
    register_paper_scan,
)
from document_vault_store import (
    list_document_vault,
    register_prepared_revision,
)
from paper_document_store import list_documents, save_docx_bytes
from workspace import (
    create_workspace_backup_archive,
    restore_workspace_backup_archive,
)


class DocumentVaultPaperScanR5Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.workspace = self.base / "Work"
        self.workspace.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _docx_bytes(text="Документ"):
        document = Document()
        document.add_paragraph(text)
        stream = io.BytesIO()
        document.save(stream)
        return stream.getvalue()

    def _vault_document(self):
        payload = self._docx_bytes()
        metadata = {
            "origin": "prepared_snapshot",
            "document_status": "prepared",
            "prepared_snapshot_id": "pd-" + "1" * 32,
            "company_template_id": "ct-" + "2" * 32,
            "template_revision": 3,
            "template_source_sha256": "a" * 64,
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        }
        path = save_docx_bytes(
            self.workspace,
            payload,
            "Інструкція",
            "Безпека руху",
            "2026-11-16",
            metadata=metadata,
        )
        row = next(
            item for item in list_documents(self.workspace)
            if item["file"] == path.name
        )
        return register_prepared_revision(self.workspace, row["id"])

    def _scan(self, name="scan.pdf", payload=None):
        if payload is None:
            payload = b"%PDF-1.4\nsynthetic paper scan\n%%EOF\n"
        path = self.base / name
        path.write_bytes(payload)
        return path, payload

    def test_version_identity_is_r5(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.24-r2\n",
        )
        self.assertIn(
            'APP_VERSION = "10.24-r2"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.24-r2", start)
        self.assertIn("document_vault_paper_scans.py", start)

    def test_scan_is_copied_and_linked_to_exact_document(self):
        vault = self._vault_document()
        source, payload = self._scan()

        record = register_paper_scan(
            self.workspace, vault.vault_id, source
        )

        self.assertEqual(record.vault_id, vault.vault_id)
        self.assertEqual(record.role, "paper_scan")
        self.assertEqual(record.media_type, "application/pdf")
        self.assertEqual(record.size_bytes, len(payload))
        self.assertEqual(record.sha256, hashlib.sha256(payload).hexdigest())
        stored = load_paper_scan(self.workspace, record.attachment_id)
        self.assertEqual(stored.path.read_bytes(), payload)
        self.assertNotEqual(stored.path.resolve(), source.resolve())
        self.assertEqual(len(list_paper_scans(self.workspace, vault.vault_id)), 1)

    def test_supported_scan_types_are_checked_by_content(self):
        vault = self._vault_document()
        samples = (
            ("one.pdf", b"%PDF-1.7\nscan", "application/pdf"),
            ("two.jpg", b"\xff\xd8\xff\xe0scan", "image/jpeg"),
            ("three.png", b"\x89PNG\r\n\x1a\nscan", "image/png"),
            ("four.tiff", b"II*\x00scan", "image/tiff"),
        )
        for name, payload, expected_media in samples:
            source, _ = self._scan(name, payload)
            record = register_paper_scan(
                self.workspace, vault.vault_id, source
            )
            self.assertEqual(record.media_type, expected_media)
        self.assertEqual(
            len(list_paper_scans(self.workspace, vault.vault_id)), 4
        )

    def test_fake_extension_is_rejected(self):
        vault = self._vault_document()
        source, _ = self._scan("fake.pdf", b"not a pdf")
        with self.assertRaisesRegex(ValueError, "не схожий"):
            register_paper_scan(self.workspace, vault.vault_id, source)
        self.assertEqual(list_paper_scans(self.workspace, vault.vault_id), ())

    def test_same_scan_is_not_added_twice(self):
        vault = self._vault_document()
        source, _ = self._scan()
        register_paper_scan(self.workspace, vault.vault_id, source)
        with self.assertRaisesRegex(ValueError, "уже додано"):
            register_paper_scan(self.workspace, vault.vault_id, source)
        self.assertEqual(len(list_paper_scans(self.workspace)), 1)

    def test_scan_does_not_make_document_signed(self):
        vault = self._vault_document()
        source, _ = self._scan()
        register_paper_scan(self.workspace, vault.vault_id, source)

        current = next(
            item for item in list_document_vault(self.workspace)
            if item.vault_id == vault.vault_id
        )
        self.assertEqual(current.status, "ready")
        index = json.loads(
            (paper_scan_root(self.workspace) / "index.json").read_text("utf-8")
        )
        encoded = json.dumps(index, ensure_ascii=False).casefold()
        self.assertNotIn("signed", encoded)
        self.assertNotIn("signature", encoded)
        self.assertNotIn("verification", encoded)

    def test_scan_tampering_is_detected_without_hiding_document(self):
        vault = self._vault_document()
        source, _ = self._scan()
        record = register_paper_scan(self.workspace, vault.vault_id, source)
        stored = load_paper_scan(self.workspace, record.attachment_id)
        stored.path.write_bytes(b"%PDF-1.4\nchanged\n")

        with self.assertRaisesRegex(ValueError, "розмір|цілісність"):
            list_paper_scans(self.workspace)
        self.assertEqual(
            [item.vault_id for item in list_document_vault(self.workspace)],
            [vault.vault_id],
        )

    def test_orphan_scan_file_is_detected(self):
        vault = self._vault_document()
        source, _ = self._scan()
        register_paper_scan(self.workspace, vault.vault_id, source)
        orphan = (
            paper_scan_root(self.workspace)
            / "objects"
            / "ff"
            / ("va-" + "f" * 32 + ".pdf")
        )
        orphan.parent.mkdir(exist_ok=True)
        orphan.write_bytes(b"%PDF-1.4\norphan")
        with self.assertRaisesRegex(ValueError, "без індексу"):
            list_paper_scans(self.workspace)

    def test_scan_requires_existing_vault_document(self):
        source, _ = self._scan()
        with self.assertRaisesRegex(ValueError, "не знайдено|Спочатку"):
            register_paper_scan(
                self.workspace, "vd-" + "f" * 32, source
            )

    def test_full_backup_restores_scan_bytes_and_link(self):
        vault = self._vault_document()
        source, payload = self._scan()
        scan = register_paper_scan(
            self.workspace, vault.vault_id, source
        )

        data = self.workspace / "Data"
        data.mkdir(exist_ok=True)
        db = data / "driver_worktime.sqlite3"
        con = sqlite3.connect(str(db))
        try:
            con.execute("CREATE TABLE backup_probe(id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        archive = self.base / "backup.zip"
        create_workspace_backup_archive(
            self.workspace, archive, app_version="10.21-r7"
        )
        restored = self.base / "Restored"
        restore_workspace_backup_archive(archive, restored)

        restored_scan = load_paper_scan(restored, scan.attachment_id)
        self.assertEqual(restored_scan.path.read_bytes(), payload)
        self.assertEqual(restored_scan.record.vault_id, vault.vault_id)
        self.assertEqual(len(list_document_vault(restored)), 1)


if __name__ == "__main__":
    unittest.main()
