# -*- coding: utf-8 -*-
"""r10: logical document folders can move and archive without losing data."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from document_library_collections import (
    archive_collection,
    collection_store_path,
    create_collection,
    document_collection_ids,
    move_collection,
    read_collection_state,
    restore_collection,
    set_document_collections,
)
from document_library_tree import collection_navigation_nodes
from workspace import create_workspace_backup_archive, restore_workspace_backup_archive


class R10DocumentFolderManagementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name) / "workspace"
        self.workspace.mkdir()

    def test_move_subtree_preserves_ids_and_document_placement(self):
        a = create_collection(self.workspace, "A")
        child = create_collection(self.workspace, "Child", a.collection_id)
        b = create_collection(self.workspace, "B")
        set_document_collections(self.workspace, "order:42", (child.collection_id,))
        original = collection_store_path(self.workspace).read_bytes()

        moved = move_collection(self.workspace, a.collection_id, b.collection_id)
        self.assertEqual(moved.parent_id, b.collection_id)
        state = read_collection_state(self.workspace)
        self.assertEqual(
            {x.collection_id: x.parent_id for x in state.collections}[child.collection_id],
            a.collection_id,
        )
        self.assertEqual(
            document_collection_ids(self.workspace, "order:42"), (child.collection_id,)
        )
        self.assertNotEqual(original, collection_store_path(self.workspace).read_bytes())

        with self.assertRaisesRegex(ValueError, "цикл"):
            move_collection(self.workspace, b.collection_id, child.collection_id)

    def test_archive_and_restore_subtree_keep_memberships(self):
        parent = create_collection(self.workspace, "One")
        child = create_collection(self.workspace, "Two", parent.collection_id)
        unrelated = create_collection(self.workspace, "Other")
        set_document_collections(self.workspace, "paper:abc", (child.collection_id,))
        set_document_collections(self.workspace, "order:1", (unrelated.collection_id,))

        archived = archive_collection(self.workspace, parent.collection_id)
        self.assertEqual(set(archived), {parent.collection_id, child.collection_id})
        state = read_collection_state(self.workspace)
        by_id = {x.collection_id: x for x in state.collections}
        self.assertTrue(by_id[parent.collection_id].archived_at)
        self.assertTrue(by_id[child.collection_id].archived_at)
        self.assertFalse(by_id[unrelated.collection_id].archived_at)
        self.assertEqual(
            document_collection_ids(self.workspace, "paper:abc"), (child.collection_id,)
        )
        nodes = collection_navigation_nodes({"rows": []}, state)
        self.assertNotIn("collection:" + parent.collection_id, {node[0] for node in nodes})

        restored = restore_collection(self.workspace, parent.collection_id)
        self.assertEqual(set(restored), set(archived))
        state = read_collection_state(self.workspace)
        self.assertTrue(all(not x.archived_at for x in state.collections))
        self.assertIn(
            "collection:" + child.collection_id,
            {node[0] for node in collection_navigation_nodes({"rows": []}, state)},
        )
        self.assertEqual(document_collection_ids(self.workspace, "paper:abc"),
                         (child.collection_id,))

    def test_archived_parents_reject_new_folders_or_moves(self):
        archived = create_collection(self.workspace, "Archive")
        other = create_collection(self.workspace, "Live")
        archive_collection(self.workspace, archived.collection_id)
        before = collection_store_path(self.workspace).read_bytes()
        with self.assertRaisesRegex(ValueError, "архівної"):
            create_collection(self.workspace, "New", archived.collection_id)
        with self.assertRaisesRegex(ValueError, "архівної"):
            move_collection(self.workspace, other.collection_id, archived.collection_id)
        with self.assertRaisesRegex(ValueError, "відновіть"):
            move_collection(self.workspace, archived.collection_id, other.collection_id)
        self.assertEqual(before, collection_store_path(self.workspace).read_bytes())

    def test_archived_folder_rejects_new_document_placement(self):
        archived = create_collection(self.workspace, "Archive")
        set_document_collections(
            self.workspace, "paper:abc", (archived.collection_id,)
        )
        archive_collection(self.workspace, archived.collection_id)
        before = collection_store_path(self.workspace).read_bytes()
        with self.assertRaisesRegex(ValueError, "відновіть"):
            set_document_collections(
                self.workspace, "order:100", (archived.collection_id,)
            )
        self.assertEqual(before, collection_store_path(self.workspace).read_bytes())
        self.assertEqual(
            document_collection_ids(self.workspace, "paper:abc"),
            (archived.collection_id,),
        )

    def test_reject_restore_child_below_archived_parent(self):
        parent = create_collection(self.workspace, "Parent")
        child = create_collection(self.workspace, "Child", parent.collection_id)
        archive_collection(self.workspace, parent.collection_id)
        before = collection_store_path(self.workspace).read_bytes()
        with self.assertRaisesRegex(ValueError, "батьківську"):
            restore_collection(self.workspace, child.collection_id)
        self.assertEqual(before, collection_store_path(self.workspace).read_bytes())

    def test_backup_restores_archived_metadata_and_placements(self):
        parent = create_collection(self.workspace, "Archive")
        child = create_collection(self.workspace, "Old", parent.collection_id)
        set_document_collections(self.workspace, "paper:xyz", (child.collection_id,))
        archive_collection(self.workspace, parent.collection_id)
        data = self.workspace / "Data"
        con = sqlite3.connect(str(data / "driver_worktime.sqlite3"))
        try:
            con.execute("CREATE TABLE probe (id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()
        target = Path(self.tmp.name) / "backup.zip"
        create_workspace_backup_archive(self.workspace, target, app_version="10.22-r10")
        restored = Path(self.tmp.name) / "restored"
        restore_workspace_backup_archive(target, restored)
        state = read_collection_state(restored)
        self.assertEqual(len([x for x in state.collections if x.archived_at]), 2)
        self.assertEqual(
            document_collection_ids(restored, "paper:xyz"), (child.collection_id,)
        )
        restore_collection(restored, parent.collection_id)
        self.assertTrue(all(not x.archived_at for x in read_collection_state(restored).collections))

    def test_empty_folder_is_selectable_and_addable_from_full_catalog(self):
        folder = create_collection(self.workspace, "Порожня папка")
        all_rows = [{
            "source": "paper",
            "source_id": "doc-123",
            "date": "2026-11-19",
            "title": "Наказ",
        }]
        snapshot = {"rows": all_rows}
        state = read_collection_state(self.workspace)
        nodes = collection_navigation_nodes(snapshot, state)
        target = next(
            item for item in nodes
            if item[0] == "collection:" + folder.collection_id
        )
        self.assertEqual(target[3], 0)
        self.assertEqual(target[4][0], "collection")

        # The UI picker must read snapshot rows, not the empty filtered page.
        from document_library_collections import catalog_document_key
        key = catalog_document_key(snapshot["rows"][0])
        set_document_collections(self.workspace, key, (folder.collection_id,))
        nodes = collection_navigation_nodes(snapshot, read_collection_state(self.workspace))
        target = next(
            item for item in nodes
            if item[0] == "collection:" + folder.collection_id
        )
        self.assertEqual(target[3], 1)
        self.assertIn(key, target[4][2])

    def test_ui_picker_keeps_folder_selected_and_explains_action(self):
        source = (
            Path(__file__).resolve().parents[1] / "src" / "taxo"
            / "document_catalog_ui.py"
        ).read_text("utf-8")
        self.assertIn("def add_document_to_selected_folder():", source)
        self.assertIn('for item in snapshot.get("rows", ()):', source)
        self.assertIn("Додати документ у цю папку…", source)
        self.assertIn("Додати у папку", source)
        self.assertIn('active_filter[1] == value[1]', source)
        self.assertIn('state["drawing_library_tree"] = True', source)
        self.assertIn('state["library_filter"] = ("collection", created.collection_id, ())', source)

    def test_ui_exposes_explicit_and_reversible_folder_actions(self):
        source = (
            Path(__file__).resolve().parents[1] / "src" / "taxo"
            / "document_catalog_ui.py"
        ).read_text("utf-8")
        for text in (
            "Перемістити папку…",
            "Архівувати папку…",
            "Відновити з архіву…",
            "move_collection(workspace_root",
            "archive_collection(workspace_root",
            "restore_collection(workspace_root",
            "Документи, скани та їхнє розміщення НЕ видаляються.",
        ):
            self.assertIn(text, source)


if __name__ == "__main__":
    unittest.main()
