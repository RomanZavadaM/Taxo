# -*- coding: utf-8 -*-
"""10.19-r6: immutable PreparedDocuments snapshots and backup coverage."""
from __future__ import annotations

import hashlib
import inspect
import json
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from company_template_draft import CompanyTemplateDraft
from company_template_facts import DraftVariable
import company_template_draft_form_ui
import company_template_draft_preview_ui
import prepared_document_store as store
import workspace


def _draft():
    variables = (
        DraftVariable(
            name="company.name",
            label="Підприємство",
            variable_type="text",
            required=True,
        ),
        DraftVariable(
            name="order.date",
            label="Дата",
            variable_type="date",
            required=True,
        ),
        DraftVariable(
            name="driver",
            label="Водій",
            variable_type="person_ref",
            required=True,
        ),
    )
    facts = {
        "company.name": "ТОВ «Тест»",
        "order.date": date(2026, 11, 14),
        "driver": {
            "entity_type": "employee",
            "id": 17,
            "name": "Петренко Іван",
            "position": "водій",
        },
    }
    rendered = {
        "format": "taxo.template.v1",
        "template_id": "orders.prepared-test",
        "title": "Підготовлений наказ",
        "document_kind": "order",
        "scenario": "prepared",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {
                "name": "company.name",
                "type": "text",
                "required": True,
            }
        ],
        "blocks": [
            {
                "id": "body",
                "type": "paragraph",
                "text": "ТОВ «Тест» / 14.11.2026 / Петренко Іван",
            }
        ],
    }
    return CompanyTemplateDraft(
        company_template_id="ct-" + ("a" * 32),
        source_sha256="b" * 64,
        edit_revision=4,
        title="Підготовлений наказ",
        content="ТОВ «Тест» / 14.11.2026 / Петренко Іван",
        variables=variables,
        normalized_facts=facts,
        rendered_template=rendered,
    )


def _make_main_db(work):
    data = work / "Data"
    data.mkdir(parents=True, exist_ok=True)
    path = data / "driver_worktime.sqlite3"
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE synthetic(id INTEGER PRIMARY KEY, note TEXT)")
        con.execute("INSERT INTO synthetic(note) VALUES('backup anchor')")
        con.commit()
    finally:
        con.close()
    return path


class PreparedDocumentR6Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / "Work"
        self.work.mkdir()

    def test_revision_identity_accepts_r6_and_r7(self):
        root = Path(__file__).resolve().parents[1]
        self.assertIn(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            ("Version: 10.19-r6", "Version: 10.19-r7", "Version: 10.19-r8", "Version: 10.19-r9", "Version: 10.19-r10", "Version: 10.20-r1", "Version: 10.20-r2", "Version: 10.20-r3", "Version: 10.20-r4"),
        )
        main_source = (root / "main.py").read_text("utf-8")
        self.assertTrue(
            'APP_VERSION = "10.19-r6"' in main_source
            or 'APP_VERSION = "10.19-r7"' in main_source
            or 'APP_VERSION = "10.19-r8"' in main_source
            or 'APP_VERSION = "10.19-r9"' in main_source
            or 'APP_VERSION = "10.19-r10"' in main_source
            or 'APP_VERSION = "10.20-r1"' in main_source
            or 'APP_VERSION = "10.20-r2"' in main_source
            or 'APP_VERSION = "10.20-r3"' in main_source
            or 'APP_VERSION = "10.20-r4"' in main_source
        )
        start_source = (root / "START.bat").read_text("utf-8")
        self.assertTrue(
            "Taxo 10.19-r6" in start_source
            or "Taxo 10.19-r7" in start_source
            or "Taxo 10.19-r8" in start_source
            or "Taxo 10.19-r9" in start_source
            or "Taxo 10.19-r10" in start_source
            or "Taxo 10.20-r1" in start_source
            or "Taxo 10.20-r2" in start_source
            or "Taxo 10.20-r3" in start_source
        )

    def test_missing_store_listing_has_no_write_side_effect(self):
        self.assertEqual(store.list_prepared_snapshots(self.work), ())
        self.assertFalse((self.work / "Data").exists())

    def test_create_list_load_preserves_exact_source_and_content(self):
        summary = store.create_prepared_snapshot(self.work, _draft())
        self.assertEqual(summary.company_template_id, "ct-" + ("a" * 32))
        self.assertEqual(summary.source_sha256, "b" * 64)
        self.assertEqual(summary.edit_revision, 4)
        self.assertEqual(store.list_prepared_snapshots(self.work), (summary,))

        loaded = store.load_prepared_snapshot(self.work, summary.snapshot_id)
        self.assertEqual(loaded.summary, summary)
        self.assertEqual(
            loaded.data["rendered_content"],
            "ТОВ «Тест» / 14.11.2026 / Петренко Іван",
        )
        self.assertEqual(
            loaded.data["rendered_template"]["blocks"][0]["text"],
            "ТОВ «Тест» / 14.11.2026 / Петренко Іван",
        )
        self.assertEqual(
            loaded.data["normalized_facts"]["order.date"],
            {"$taxo_type": "date", "value": "2026-11-14"},
        )
        self.assertEqual(loaded.data["normalized_facts"]["driver"]["id"], 17)

    def test_second_snapshot_never_overwrites_first_bytes(self):
        first = store.create_prepared_snapshot(self.work, _draft())
        first_path = (
            self.work / "Data" / "PreparedDocuments" / "items" / first.file_name
        )
        first_bytes = first_path.read_bytes()

        second = store.create_prepared_snapshot(self.work, _draft())
        self.assertNotEqual(first.snapshot_id, second.snapshot_id)
        self.assertNotEqual(first.file_name, second.file_name)
        self.assertEqual(first_path.read_bytes(), first_bytes)
        self.assertEqual(len(store.list_prepared_snapshots(self.work)), 2)

    def test_tampered_snapshot_is_detected(self):
        summary = store.create_prepared_snapshot(self.work, _draft())
        path = (
            self.work / "Data" / "PreparedDocuments" / "items" / summary.file_name
        )
        path.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "цілісність|розмір"):
            store.list_prepared_snapshots(self.work)

    def test_unindexed_item_is_detected(self):
        store.create_prepared_snapshot(self.work, _draft())
        items = self.work / "Data" / "PreparedDocuments" / "items"
        orphan = items / ("pd-" + ("f" * 32) + ".json")
        orphan.write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "індекс|без індексу"):
            store.list_prepared_snapshots(self.work)

    def test_index_failure_rolls_back_new_item(self):
        real_atomic = store._atomic_write
        calls = {"count": 0}

        def fail_index(path, payload):
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("synthetic index failure")
            return real_atomic(path, payload)

        with mock.patch.object(store, "_atomic_write", side_effect=fail_index):
            with self.assertRaises(OSError):
                store.create_prepared_snapshot(self.work, _draft())

        items = self.work / "Data" / "PreparedDocuments" / "items"
        self.assertTrue(items.is_dir())
        self.assertEqual(list(items.iterdir()), [])
        self.assertFalse(
            (self.work / "Data" / "PreparedDocuments" / "index.json").exists()
        )

    def test_store_has_no_update_or_delete_api(self):
        self.assertFalse(hasattr(store, "update_prepared_snapshot"))
        self.assertFalse(hasattr(store, "delete_prepared_snapshot"))
        source = inspect.getsource(store)
        self.assertNotIn("def update_prepared_snapshot", source)
        self.assertNotIn("def delete_prepared_snapshot", source)

    def test_full_backup_restore_preserves_snapshot_bytes_and_manifest_flag(self):
        _make_main_db(self.work)
        summary = store.create_prepared_snapshot(self.work, _draft())
        original = (
            self.work / "Data" / "PreparedDocuments" / "items" / summary.file_name
        ).read_bytes()

        archive = self.root / "prepared-backup.zip"
        workspace.create_workspace_backup_archive(
            self.work, archive, app_version="10.19-r6"
        )
        manifest = workspace.validate_workspace_backup_archive(archive)
        self.assertTrue(manifest["includes"]["prepared_documents"])

        restored = self.root / "Restored"
        workspace.restore_workspace_backup_archive(archive, restored)
        loaded = store.load_prepared_snapshot(restored, summary.snapshot_id)
        restored_bytes = (
            restored
            / "Data"
            / "PreparedDocuments"
            / "items"
            / loaded.summary.file_name
        ).read_bytes()
        self.assertEqual(restored_bytes, original)
        self.assertEqual(
            hashlib.sha256(restored_bytes).hexdigest(),
            summary.sha256,
        )

    def test_backup_rejects_symlink_inside_prepared_documents(self):
        _make_main_db(self.work)
        store.create_prepared_snapshot(self.work, _draft())
        outside = self.root / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = self.work / "Data" / "PreparedDocuments" / "linked.txt"
        try:
            link.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks not supported in this environment")

        archive = self.root / "unsafe.zip"
        with self.assertRaisesRegex(ValueError, "символічне посилання"):
            workspace.create_workspace_backup_archive(
                self.work, archive, app_version="10.19-r6"
            )

    def test_preview_save_action_is_snapshot_only_and_worker_has_no_tk_reads(self):
        source = inspect.getsource(company_template_draft_preview_ui)
        self.assertIn('"Зберегти підготовлену чернетку"', source)
        self.assertIn("create_prepared_snapshot", source)
        self.assertIn("Taxo-prepared-document-snapshot-save", source)
        self.assertIn('state="disabled"', source)
        self.assertNotIn("DocumentArchive", source)
        self.assertNotIn("write_file", source)
        self.assertNotIn("create_order(", source)
        self.assertNotIn("create_briefing", source)
        worker = source[source.index("        def worker():"):]
        self.assertNotIn(".get()", worker)
        self.assertNotIn("StringVar(", worker)

    def test_form_passes_services_to_snapshot_capable_preview(self):
        source = inspect.getsource(company_template_draft_form_ui)
        self.assertIn(
            "open_company_template_draft_preview(win, services, payload)",
            source,
        )

    def test_prepared_document_logic_stays_out_of_main(self):
        import main
        source = inspect.getsource(main)
        for marker in (
            "PreparedDocuments",
            "create_prepared_snapshot",
            "prepared_document_store",
            "prepared_document_codec",
        ):
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
