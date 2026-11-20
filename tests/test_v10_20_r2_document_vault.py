# -*- coding: utf-8 -*-
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from docx import Document

from document_vault_store import (
    document_vault_root,
    list_document_vault,
    load_document_vault_object,
    register_prepared_revision,
)
from paper_document_store import list_documents, save_docx_bytes


class DocumentVaultCoreR2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _docx_bytes(text):
        document = Document()
        document.add_paragraph(text)
        stream = io.BytesIO()
        document.save(stream)
        return stream.getvalue()

    def _initial_revision(self, text="Перша редакція"):
        payload = self._docx_bytes(text)
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
        return row, payload

    def _next_revision(self, previous, text="Друга редакція"):
        payload = self._docx_bytes(text)
        metadata = {
            "origin": "edited_docx",
            "document_status": "prepared",
            "prepared_snapshot_id": previous["prepared_snapshot_id"],
            "company_template_id": previous["company_template_id"],
            "template_revision": previous["template_revision"],
            "template_source_sha256": previous["template_source_sha256"],
            "document_family_id": previous["document_family_id"],
            "document_revision": previous["document_revision"] + 1,
            "previous_document_id": previous["id"],
            "content_sha256": hashlib.sha256(payload).hexdigest(),
        }
        path = save_docx_bytes(
            self.workspace,
            payload,
            previous["kind"],
            previous["title"],
            previous["date"],
            metadata=metadata,
        )
        row = next(
            item for item in list_documents(self.workspace)
            if item["file"] == path.name
        )
        return row, payload

    def test_version_identity_allows_current_r3(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.23-r5\n",
        )
        self.assertIn(
            'APP_VERSION = "10.23-r5"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.23-r5",
            (root / "START.bat").read_text("utf-8"),
        )

    def test_existing_paper_documents_are_not_auto_migrated(self):
        self._initial_revision()
        self.assertEqual(list_document_vault(self.workspace), ())
        self.assertFalse(document_vault_root(self.workspace).exists())

    def test_exact_prepared_revision_is_registered_with_provenance(self):
        source, payload = self._initial_revision()
        record = register_prepared_revision(self.workspace, source["id"])

        self.assertEqual(record.status, "ready")
        self.assertEqual(record.source_document_id, source["id"])
        self.assertEqual(
            record.prepared_snapshot_id, source["prepared_snapshot_id"]
        )
        self.assertEqual(
            record.document_family_id, source["document_family_id"]
        )
        self.assertEqual(record.document_revision, 1)
        self.assertEqual(record.content_sha256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(len(list_document_vault(self.workspace)), 1)

        stored = load_document_vault_object(
            self.workspace, record.vault_id
        )
        self.assertEqual(stored.payload, payload)
        self.assertEqual(stored.path.read_bytes(), payload)
        self.assertEqual(
            stored.path.parents[2], document_vault_root(self.workspace)
        )

    def test_two_word_revisions_remain_two_exact_vault_objects(self):
        first, first_payload = self._initial_revision()
        second, second_payload = self._next_revision(first)

        first_vault = register_prepared_revision(
            self.workspace, first["id"], status="archived"
        )
        second_vault = register_prepared_revision(
            self.workspace, second["id"], status="ready"
        )

        self.assertNotEqual(first_vault.vault_id, second_vault.vault_id)
        self.assertEqual(first_vault.document_family_id, second_vault.document_family_id)
        self.assertEqual((first_vault.document_revision, second_vault.document_revision), (1, 2))
        self.assertEqual(
            load_document_vault_object(
                self.workspace, first_vault.vault_id
            ).payload,
            first_payload,
        )
        self.assertEqual(
            load_document_vault_object(
                self.workspace, second_vault.vault_id
            ).payload,
            second_payload,
        )

    def test_duplicate_source_revision_is_rejected(self):
        source, _payload = self._initial_revision()
        register_prepared_revision(self.workspace, source["id"])
        with self.assertRaisesRegex(ValueError, "вже є"):
            register_prepared_revision(self.workspace, source["id"])
        self.assertEqual(len(list_document_vault(self.workspace)), 1)

    def test_registration_does_not_infer_signature_state(self):
        source, _payload = self._initial_revision()
        register_prepared_revision(
            self.workspace, source["id"], status="archived"
        )
        index = json.loads(
            (document_vault_root(self.workspace) / "index.json").read_text(
                "utf-8"
            )
        )
        encoded = json.dumps(index, ensure_ascii=False).casefold()
        self.assertNotIn("signed", encoded)
        self.assertNotIn("signature", encoded)
        self.assertNotIn("paper_signed", encoded)

    def test_invalid_status_creates_no_vault(self):
        source, _payload = self._initial_revision()
        with self.assertRaisesRegex(ValueError, "ready або archived"):
            register_prepared_revision(
                self.workspace, source["id"], status="signed"
            )
        self.assertFalse(document_vault_root(self.workspace).exists())

    def test_object_tampering_is_detected(self):
        source, _payload = self._initial_revision()
        record = register_prepared_revision(self.workspace, source["id"])
        stored = load_document_vault_object(
            self.workspace, record.vault_id
        )
        stored.path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "розмір|цілісність"):
            list_document_vault(self.workspace)

    def test_unindexed_object_is_rejected(self):
        source, _payload = self._initial_revision()
        record = register_prepared_revision(self.workspace, source["id"])
        extra_id = "vd-" + "f" * 32
        extra = (
            document_vault_root(self.workspace)
            / "objects"
            / "ff"
            / (extra_id + ".docx")
        )
        extra.parent.mkdir(exist_ok=True)
        extra.write_bytes(b"orphan")
        with self.assertRaisesRegex(ValueError, "без індексу"):
            list_document_vault(self.workspace)

    def test_index_cannot_claim_a_different_source_revision(self):
        source, _payload = self._initial_revision()
        register_prepared_revision(self.workspace, source["id"])
        index_path = document_vault_root(self.workspace) / "index.json"
        data = json.loads(index_path.read_text("utf-8"))
        data["items"][0]["source"]["content_sha256"] = "b" * 64
        index_path.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "не збігається"):
            list_document_vault(self.workspace)


if __name__ == "__main__":
    unittest.main()
