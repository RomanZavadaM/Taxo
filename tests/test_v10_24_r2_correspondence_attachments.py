# -*- coding: utf-8 -*-
import hashlib
import io
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from docx import Document

import workspace
from correspondence_attachments import (
    add_correspondence_file,
    attachment_root,
    link_correspondence_document,
    list_correspondence_attachments,
    list_removed_correspondence_attachments,
    load_correspondence_file,
    remove_correspondence_attachment,
)
from correspondence_registry import get_correspondence
from correspondence_service import register_incoming, register_outgoing
from document_vault_store import register_prepared_revision
from paper_document_store import list_documents, save_docx_bytes


class CorrespondenceAttachmentsR2Tests(unittest.TestCase):
    def test_candidate_identity_and_start_guard(self):
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
        self.assertIn("correspondence_attachments.py", start)
        self.assertEqual(
            (root / ".release" / "full-current").read_text("utf-8"),
            "10.24-r2\n",
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "work"
        workspace.ensure_workspace(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def _incoming(self, subject="Incoming"):
        return register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="ТОВ Тест",
            subject=subject,
        )

    def _outgoing(self, subject="Outgoing"):
        return register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="ТОВ Адресат",
            subject=subject,
        )

    def _pdf(self, name="letter.pdf", payload=None):
        if payload is None:
            payload = b"%PDF-1.7\ncontrolled correspondence attachment\n%%EOF\n"
        path = self.base / name
        path.write_bytes(payload)
        return path, payload

    @staticmethod
    def _docx_bytes(text="Controlled document"):
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
            "template_revision": 1,
            "template_source_sha256": "a" * 64,
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        }
        path = save_docx_bytes(
            self.root,
            payload,
            "Лист",
            "Готовий лист",
            "2026-11-22",
            metadata=metadata,
        )
        row = next(
            item for item in list_documents(self.root)
            if item["file"] == path.name
        )
        return register_prepared_revision(self.root, row["id"])

    def test_file_attachment_is_immutable_and_does_not_change_letter_state(self):
        outgoing = self._outgoing()
        source, payload = self._pdf()

        record = add_correspondence_file(
            self.root, outgoing.correspondence_id, source
        )
        stored = load_correspondence_file(self.root, record.attachment_id)

        self.assertEqual(record.correspondence_id, outgoing.correspondence_id)
        self.assertEqual(record.original_name, "letter.pdf")
        self.assertEqual(record.media_type, "application/pdf")
        self.assertEqual(record.size_bytes, len(payload))
        self.assertEqual(record.sha256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(stored.path.read_bytes(), payload)
        self.assertNotEqual(stored.path.resolve(), source.resolve())

        unchanged = get_correspondence(self.root, outgoing.correspondence_id)
        self.assertEqual(unchanged.status, "registered")
        self.assertEqual(unchanged.sent_date, "")

    def test_same_bytes_are_stored_once_but_can_link_two_letters(self):
        first = self._incoming("One")
        second = self._incoming("Two")
        source, _ = self._pdf()

        a = add_correspondence_file(
            self.root, first.correspondence_id, source
        )
        b = add_correspondence_file(
            self.root, second.correspondence_id, source
        )

        self.assertNotEqual(a.attachment_id, b.attachment_id)
        self.assertEqual(a.sha256, b.sha256)
        self.assertEqual(a.storage_key, b.storage_key)
        objects = list((attachment_root(self.root) / "objects").rglob("*.*"))
        self.assertEqual(len(objects), 1)

    def test_same_active_file_cannot_be_added_twice_to_same_letter(self):
        incoming = self._incoming()
        source, _ = self._pdf()
        add_correspondence_file(
            self.root, incoming.correspondence_id, source
        )
        with self.assertRaisesRegex(ValueError, "уже додано"):
            add_correspondence_file(
                self.root, incoming.correspondence_id, source
            )

    def test_fake_extension_is_rejected_without_store_mutation(self):
        incoming = self._incoming()
        source, _ = self._pdf("fake.pdf", b"not a pdf")
        with self.assertRaisesRegex(ValueError, "не відповідає"):
            add_correspondence_file(
                self.root, incoming.correspondence_id, source
            )
        self.assertEqual(
            list_correspondence_attachments(
                self.root, incoming.correspondence_id
            ),
            (),
        )

    def test_docx_supported_but_macro_payload_is_rejected(self):
        incoming = self._incoming()
        good = self.base / "good.docx"
        good.write_bytes(self._docx_bytes("Добрий DOCX"))
        stored = add_correspondence_file(
            self.root, incoming.correspondence_id, good
        )
        self.assertEqual(
            stored.media_type,
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document",
        )

        bad = self.base / "macro.docx"
        with zipfile.ZipFile(str(bad), "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
            archive.writestr("word/document.xml", "<w:document/>")
            archive.writestr("word/vbaProject.bin", b"macro")
        with self.assertRaisesRegex(ValueError, "макрос"):
            add_correspondence_file(
                self.root, incoming.correspondence_id, bad
            )

    def test_document_link_requires_existing_vault_and_copies_no_bytes(self):
        incoming = self._incoming()
        vault = self._vault_document()

        linked = link_correspondence_document(
            self.root,
            incoming.correspondence_id,
            "vault:" + vault.vault_id,
            "Контрольований лист",
        )

        self.assertEqual(linked.source_kind, "document_ref")
        self.assertEqual(linked.document_ref, "vault:" + vault.vault_id)
        self.assertEqual(linked.size_bytes, 0)
        self.assertFalse((attachment_root(self.root) / "objects").exists())

        with self.assertRaisesRegex(ValueError, "відсутній DocumentVault"):
            link_correspondence_document(
                self.root,
                incoming.correspondence_id,
                "vault:vd-" + "f" * 32,
            )

    def test_remove_is_history_only_and_preserves_immutable_bytes(self):
        incoming = self._incoming()
        source, payload = self._pdf()
        record = add_correspondence_file(
            self.root, incoming.correspondence_id, source
        )
        stored_path = load_correspondence_file(
            self.root, record.attachment_id
        ).path

        removed = remove_correspondence_attachment(
            self.root, record.attachment_id
        )

        self.assertEqual(removed.history.action, "removed")
        self.assertEqual(
            list_correspondence_attachments(
                self.root, incoming.correspondence_id
            ),
            (),
        )
        history = list_removed_correspondence_attachments(
            self.root, incoming.correspondence_id
        )
        self.assertEqual(len(history), 1)
        self.assertTrue(stored_path.is_file())
        self.assertEqual(stored_path.read_bytes(), payload)
        with self.assertRaisesRegex(ValueError, "прибрано"):
            load_correspondence_file(self.root, record.attachment_id)
        with self.assertRaisesRegex(ValueError, "вже прибрано"):
            remove_correspondence_attachment(
                self.root, record.attachment_id
            )

    def test_removed_bytes_are_still_integrity_checked(self):
        incoming = self._incoming()
        source, _ = self._pdf()
        record = add_correspondence_file(
            self.root, incoming.correspondence_id, source
        )
        path = load_correspondence_file(
            self.root, record.attachment_id
        ).path
        remove_correspondence_attachment(
            self.root, record.attachment_id
        )
        path.write_bytes(b"%PDF-1.7\ntampered\n")

        with self.assertRaisesRegex(ValueError, "розмір|цілісність"):
            list_removed_correspondence_attachments(
                self.root, incoming.correspondence_id
            )

    def test_orphan_object_fails_closed(self):
        incoming = self._incoming()
        source, _ = self._pdf()
        add_correspondence_file(
            self.root, incoming.correspondence_id, source
        )
        orphan = (
            attachment_root(self.root)
            / "objects"
            / "ff"
            / (("f" * 64) + ".pdf")
        )
        orphan.parent.mkdir(exist_ok=True)
        orphan.write_bytes(b"%PDF-1.7\norphan\n")

        with self.assertRaisesRegex(ValueError, "без індексу"):
            list_correspondence_attachments(self.root)

    def test_full_backup_restores_registry_attachments_history_and_next_number(self):
        data = self.root / "Data"
        db = data / "driver_worktime.sqlite3"
        con = sqlite3.connect(str(db))
        try:
            con.execute("CREATE TABLE backup_probe(id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        incoming = self._incoming()
        source, payload = self._pdf()
        attachment = add_correspondence_file(
            self.root, incoming.correspondence_id, source
        )
        remove_correspondence_attachment(
            self.root, attachment.attachment_id
        )

        archive = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "backup.zip",
            app_version="10.24-r2",
        )
        restored = self.base / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        restored_letter = get_correspondence(
            restored, incoming.correspondence_id
        )
        self.assertEqual(
            restored_letter.registration_number, "Вх. № 0001/2026"
        )
        history = list_removed_correspondence_attachments(
            restored, incoming.correspondence_id
        )
        self.assertEqual(len(history), 1)
        record = history[0].record
        stored_path = attachment_root(restored).joinpath(
            *record.storage_key.split("/")
        )
        self.assertEqual(stored_path.read_bytes(), payload)

        second = register_incoming(
            restored,
            registration_date="2026-11-22",
            correspondent="ТОВ Другий",
            subject="Second",
        )
        self.assertEqual(second.registration_number, "Вх. № 0002/2026")

    def test_unknown_correspondence_and_unsafe_ref_fail_before_write(self):
        source, _ = self._pdf()
        with self.assertRaisesRegex(ValueError, "не знайдено"):
            add_correspondence_file(
                self.root, "cr-" + "f" * 32, source
            )
        incoming = self._incoming()
        with self.assertRaisesRegex(ValueError, "Некоректне посилання"):
            link_correspondence_document(
                self.root,
                incoming.correspondence_id,
                "../../outside.docx",
            )


if __name__ == "__main__":
    unittest.main()
