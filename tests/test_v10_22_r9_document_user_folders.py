# -*- coding: utf-8 -*-
"""Regression: user folders are logical, atomic and restored by full backup."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import document_catalog
from document_library_collections import (
    catalog_document_key,
    collection_store_path,
    create_collection,
    document_collection_ids,
    move_collection,
    move_document,
    read_collection_state,
    rename_collection,
    set_document_collections,
)
from document_library_tree import collection_navigation_nodes
from workspace import create_workspace_backup_archive, restore_workspace_backup_archive


def row(identifier, source="order", vault_id=""):
    return {
        "key": (source, identifier, 0),
        "source": source,
        "sources": (source,),
        "source_id": identifier,
        "vault_id": vault_id,
        "date": "2026-11-19",
        "created_at": "2026-11-19T10:00:00",
        "kind": "Документ",
        "title": identifier,
        "number": identifier,
        "category": "Інше",
        "employee_refs": (),
        "vehicle_refs": (),
        "person": "",
        "entity_text": "",
    }


class DocumentUserFoldersR9Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name) / "workspace"
        self.workspace.mkdir()

    def test_version_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.24-r8\n")
        self.assertIn('APP_VERSION = "10.24-r8"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.24-r8", (root / "START.bat").read_text("utf-8"))

    def test_create_rename_nested_move_and_cycle_guard(self):
        parent = create_collection(self.workspace, "Для перевірок")
        child = create_collection(
            self.workspace, "Листопад", parent.collection_id
        )
        renamed = rename_collection(
            self.workspace, child.collection_id, "Листопад 2026"
        )
        self.assertEqual(renamed.name, "Листопад 2026")

        other = create_collection(self.workspace, "Архів")
        moved = move_collection(
            self.workspace, child.collection_id, other.collection_id
        )
        self.assertEqual(moved.parent_id, other.collection_id)

        with self.assertRaisesRegex(ValueError, "цикл"):
            move_collection(
                self.workspace, other.collection_id, child.collection_id
            )
        with self.assertRaisesRegex(ValueError, "вже є"):
            create_collection(self.workspace, "архів")

    def test_document_move_changes_only_logical_membership(self):
        first = create_collection(self.workspace, "Перша")
        second = create_collection(self.workspace, "Друга")
        document_key = "order:123"

        move_document(self.workspace, document_key, first.collection_id)
        self.assertEqual(
            document_collection_ids(self.workspace, document_key),
            (first.collection_id,),
        )
        move_document(self.workspace, document_key, second.collection_id)
        self.assertEqual(
            document_collection_ids(self.workspace, document_key),
            (second.collection_id,),
        )

        state = read_collection_state(self.workspace)
        self.assertEqual(len(state.memberships), 1)
        self.assertFalse(
            any(path.suffix.lower() in {".docx", ".pdf", ".jpg", ".png"}
                for path in self.workspace.rglob("*") if path.is_file())
        )

    def test_folder_key_survives_document_vault_registration(self):
        paper = row("abc123", source="paper")
        merged = dict(paper)
        merged["vault_id"] = "vd-" + "1" * 32
        standalone_vault = row(
            "vd-" + "1" * 32,
            source="vault",
            vault_id="vd-" + "1" * 32,
        )
        standalone_vault["source_document_id"] = "abc123"

        self.assertEqual(catalog_document_key(paper), "paper:abc123")
        self.assertEqual(catalog_document_key(merged), "paper:abc123")
        self.assertEqual(
            catalog_document_key(standalone_vault), "paper:abc123"
        )

        folder = create_collection(self.workspace, "Не губити")
        set_document_collections(
            self.workspace,
            catalog_document_key(paper),
            (folder.collection_id,),
        )
        snapshot = {
            "rows": [merged],
            "paper_status": "",
            "order_status": "",
        }
        state = read_collection_state(self.workspace)
        node = next(
            item for item in collection_navigation_nodes(snapshot, state)
            if item[0] == "collection:" + folder.collection_id
        )
        result = document_catalog.paginate_sources(
            snapshot, library_filter=node[4]
        )
        self.assertEqual(result["total"], 1)

    def test_document_can_be_in_several_folders_and_tree_filters_before_paging(self):
        parent = create_collection(self.workspace, "Рейси")
        child = create_collection(
            self.workspace, "Міжнародні", parent.collection_id
        )
        second = create_collection(self.workspace, "Для директора")

        a = row("101")
        b = row("102")
        c = row("vd-source", source="vault", vault_id="vd-" + "1" * 32)
        key_a = catalog_document_key(a)
        key_b = catalog_document_key(b)
        key_c = catalog_document_key(c)
        set_document_collections(
            self.workspace, key_a, (child.collection_id, second.collection_id)
        )
        set_document_collections(
            self.workspace, key_b, (parent.collection_id,)
        )
        set_document_collections(
            self.workspace, key_c, (second.collection_id,)
        )

        snapshot = {
            "rows": [a, b, c],
            "paper_status": "",
            "order_status": "",
        }
        state = read_collection_state(self.workspace)
        nodes = collection_navigation_nodes(snapshot, state)
        by_id = {node[0]: node for node in nodes}
        parent_node = by_id["collection:" + parent.collection_id]
        second_node = by_id["collection:" + second.collection_id]
        self.assertEqual(parent_node[3], 2)
        self.assertEqual(second_node[3], 2)

        result = document_catalog.paginate_sources(
            snapshot, library_filter=second_node[4], page_size=1, page=0
        )
        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["rows"]), 1)

    def test_full_backup_restores_folders_and_memberships(self):
        folder = create_collection(self.workspace, "Резерв")
        set_document_collections(
            self.workspace, "paper:pd-123", (folder.collection_id,)
        )

        data = self.workspace / "Data"
        data.mkdir(exist_ok=True)
        db = data / "driver_worktime.sqlite3"
        con = sqlite3.connect(str(db))
        try:
            con.execute("CREATE TABLE probe(id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        archive = Path(self.tmp.name) / "full-backup.zip"
        create_workspace_backup_archive(
            self.workspace, archive, app_version="10.23-r1"
        )
        restored = Path(self.tmp.name) / "restored"
        restore_workspace_backup_archive(archive, restored)

        restored_state = read_collection_state(restored)
        self.assertEqual(
            [(item.collection_id, item.name) for item in restored_state.collections],
            [(folder.collection_id, "Резерв")],
        )
        self.assertEqual(
            document_collection_ids(restored, "paper:pd-123"),
            (folder.collection_id,),
        )

    def test_stale_atomic_temp_file_does_not_block_library(self):
        folder = create_collection(self.workspace, "Після збою")
        root = collection_store_path(self.workspace).parent
        (root / ("." + collection_store_path(self.workspace).name + "." + "a" * 32 + ".tmp")).write_text(
            "unfinished", "utf-8"
        )
        state = read_collection_state(self.workspace)
        self.assertEqual(
            [(item.collection_id, item.name) for item in state.collections],
            [(folder.collection_id, "Після збою")],
        )

    def test_damaged_index_fails_closed(self):
        folder = create_collection(self.workspace, "Контроль")
        path = collection_store_path(self.workspace)
        data = json.loads(path.read_text("utf-8"))
        data["collections"][0]["parent_id"] = folder.collection_id
        path.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
        with self.assertRaisesRegex(ValueError, "цикл"):
            read_collection_state(self.workspace)

    def test_ui_exposes_my_folders_without_physical_move_wording(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "taxo" / "document_catalog_ui.py"
        ).read_text("utf-8")
        for text in (
            '"Мої папки"',
            'text="Нова папка…"',
            'text="Перейменувати…"',
            'text="Розмістити документ…"',
            "set_document_collections(",
            "файл документа не переноситься і не копіюється",
        ):
            self.assertIn(text, source)


if __name__ == "__main__":
    unittest.main()
