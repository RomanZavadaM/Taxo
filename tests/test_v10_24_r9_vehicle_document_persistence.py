# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

import workspace
from vehicle_documents import (
    document_copy_state,
    ensure_vehicle_documents_schema,
    store_document_copy,
)


class TestTaxo1024R9VehicleDocumentPersistence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_r9_vehicle_docs_")
        self.base = Path(self.temp.name)
        self.root = self.base / "Workspace"
        self.paths = workspace.ensure_workspace(self.root)
        con = sqlite3.connect(str(self.paths["main_db"]))
        con.row_factory = sqlite3.Row
        con.execute(
            """
            CREATE TABLE vehicles(
                id INTEGER PRIMARY KEY,
                name TEXT DEFAULT '',
                plate TEXT DEFAULT '',
                make_model TEXT DEFAULT '',
                temporary_registration_required INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            )
            """
        )
        con.execute(
            "INSERT INTO vehicles(id,name,plate) VALUES(1,'Тестове авто','TEST-01')"
        )
        ensure_vehicle_documents_schema(con)
        con.commit()
        con.close()

    def tearDown(self):
        self.temp.cleanup()

    def _source(self, name="inspection.pdf", payload=b"%PDF-1.4\nvehicle inspection\n"):
        path = self.base / name
        path.write_bytes(payload)
        return path

    def _insert(self, stored, archived=0):
        con = sqlite3.connect(str(self.paths["main_db"]))
        con.row_factory = sqlite3.Row
        ensure_vehicle_documents_schema(con)
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,issuer,valid_from,valid_until,
                copy_path,source_path,copy_sha256,copy_size,notes,
                archived,created_at,updated_at
            ) VALUES(1,'inspection','OTK-001','СТО','2026-11-01','2027-11-01',
                     ?,?,?,?,'',?,'2026-11-27T12:00:00','2026-11-27T12:00:00')
            """,
            (
                stored["copy_path"],
                stored["source_path"],
                stored["copy_sha256"],
                stored["copy_size"],
                int(archived),
            ),
        )
        row_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.commit()
        row = con.execute(
            "SELECT * FROM vehicle_documents WHERE id=?", (row_id,)
        ).fetchone()
        con.close()
        return row_id, row

    def test_new_attachment_has_taxo_owned_copy_source_and_integrity(self):
        source = self._source()
        stored = store_document_copy(self.root, 1, "inspection", source)
        self.assertTrue(stored["copy_path"].startswith("workspace://Data/VehicleDocuments/"))
        self.assertEqual(Path(stored["source_path"]), source.resolve())
        self.assertGreater(stored["copy_size"], 0)
        self.assertEqual(len(stored["copy_sha256"]), 64)

        _row_id, row = self._insert(stored)
        state = document_copy_state(row, self.root, verify_hash=True)
        self.assertEqual(state["state"], "available")
        self.assertTrue(state["managed"])
        self.assertEqual(state["sha256"], stored["copy_sha256"])
        self.assertEqual(state["path"].read_bytes(), source.read_bytes())

    def test_nonempty_db_path_never_means_file_exists(self):
        source = self._source()
        stored = store_document_copy(self.root, 1, "inspection", source)
        _row_id, row = self._insert(stored)
        managed = workspace.resolved_path(row["copy_path"], self.root)
        managed.unlink()

        state = document_copy_state(row, self.root, verify_hash=False)
        self.assertEqual(state["state"], "missing")
        self.assertEqual(state["label"], "Файл втрачено")
        self.assertTrue(row["copy_path"])

    def test_archive_backup_restore_keeps_copy_and_provenance(self):
        source = self._source(payload=b"%PDF-1.4\narchived inspection\n")
        stored = store_document_copy(self.root, 1, "inspection", source)
        row_id, _row = self._insert(stored, archived=1)

        archive = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "full.zip",
            app_version="10.24-r9",
            include_vehicle_documents=True,
        )
        manifest = workspace.validate_workspace_backup_archive(archive)
        self.assertTrue(manifest["includes"]["vehicle_documents"])
        self.assertEqual(manifest["verified_vehicle_document_files"], 1)

        restored = self.base / "Restored"
        restored_paths = workspace.restore_workspace_backup_archive(archive, restored)
        con = sqlite3.connect(str(restored_paths["main_db"]))
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT * FROM vehicle_documents WHERE id=?", (row_id,)
        ).fetchone()
        con.close()

        self.assertEqual(int(row["archived"]), 1)
        self.assertEqual(row["source_path"], str(source.resolve()))
        state = document_copy_state(row, restored, verify_hash=True)
        self.assertEqual(state["state"], "available")
        self.assertEqual(state["path"].read_bytes(), source.read_bytes())

    def test_selected_full_backup_refuses_unrecoverable_missing_copy(self):
        source = self._source()
        stored = store_document_copy(self.root, 1, "inspection", source)
        _row_id, row = self._insert(stored)
        workspace.resolved_path(row["copy_path"], self.root).unlink()
        source.unlink()

        with self.assertRaisesRegex(ValueError, "неповні або пошкоджені"):
            workspace.create_workspace_backup_archive(
                self.root,
                self.base / "broken-full.zip",
                app_version="10.24-r9",
                include_vehicle_documents=True,
            )

        core = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "core.zip",
            app_version="10.24-r9",
            include_vehicle_documents=False,
        )
        manifest = workspace.validate_workspace_backup_archive(core)
        self.assertFalse(manifest["includes"]["vehicle_documents"])

    def test_selected_backup_recovers_legacy_external_reference(self):
        source = self._source(
            name="legacy-otk.pdf",
            payload=b"%PDF-1.4\nlegacy external inspection\n",
        )
        con = sqlite3.connect(str(self.paths["main_db"]))
        con.row_factory = sqlite3.Row
        ensure_vehicle_documents_schema(con)
        con.execute(
            """
            INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,valid_until,copy_path,
                archived,created_at,updated_at
            ) VALUES(1,'inspection','LEGACY','2027-12-31',?,1,
                     '2026-01-01T00:00:00','2026-01-01T00:00:00')
            """,
            (str(source.resolve()),),
        )
        con.commit()
        con.close()

        archive = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "legacy-full.zip",
            app_version="10.24-r9",
            include_vehicle_documents=True,
        )
        manifest = workspace.validate_workspace_backup_archive(archive)
        self.assertEqual(manifest["recovered_vehicle_document_files"], 1)
        self.assertEqual(manifest["verified_vehicle_document_files"], 1)

        restored = self.base / "LegacyRestored"
        restored_paths = workspace.restore_workspace_backup_archive(archive, restored)
        con = sqlite3.connect(str(restored_paths["main_db"]))
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT * FROM vehicle_documents WHERE document_no='LEGACY'"
        ).fetchone()
        con.close()
        self.assertTrue(row["copy_path"].startswith("workspace://Data/VehicleDocuments/"))
        self.assertEqual(row["source_path"], str(source.resolve()))
        state = document_copy_state(row, restored, verify_hash=True)
        self.assertEqual(state["state"], "available")
        self.assertEqual(state["path"].read_bytes(), source.read_bytes())

    def test_tampered_managed_copy_is_detected(self):
        source = self._source()
        stored = store_document_copy(self.root, 1, "inspection", source)
        _row_id, row = self._insert(stored)
        path = workspace.resolved_path(row["copy_path"], self.root)
        path.write_bytes(b"changed")

        state = document_copy_state(row, self.root, verify_hash=True)
        self.assertEqual(state["state"], "damaged")
        with self.assertRaisesRegex(ValueError, "неповні або пошкоджені"):
            workspace.create_workspace_backup_archive(
                self.root,
                self.base / "tampered-full.zip",
                app_version="10.24-r9",
                include_vehicle_documents=True,
            )


if __name__ == "__main__":
    unittest.main()
