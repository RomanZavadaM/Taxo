# -*- coding: utf-8 -*-
import json
import tempfile
import unittest
from pathlib import Path

from document_import_inventory import build_inventory
from document_import_batch_store import (
    MANIFEST_NAME,
    REPORT_NAME,
    persist_inventory_batch,
    read_inventory_batch,
)


class DocumentInventoryBatchStoreR7Tests(unittest.TestCase):
    def setUp(self):
        self.source_tmp = tempfile.TemporaryDirectory()
        self.workspace_tmp = tempfile.TemporaryDirectory()
        self.source = Path(self.source_tmp.name)
        self.workspace = Path(self.workspace_tmp.name)

    def tearDown(self):
        self.source_tmp.cleanup()
        self.workspace_tmp.cleanup()

    def _source_snapshot(self):
        rows = {}
        for path in sorted(self.source.rglob("*")):
            if path.is_file() and not path.is_symlink():
                rows[path.relative_to(self.source).as_posix()] = (
                    path.read_bytes(),
                    path.stat().st_mtime_ns,
                )
        return rows

    def test_persist_writes_only_workspace_and_keeps_source_unchanged(self):
        (self.source / "one.txt").write_text("one", encoding="utf-8")
        (self.source / "copy.txt").write_text("one", encoding="utf-8")
        before = self._source_snapshot()
        inventory = build_inventory(self.source, batch_id="batch-r7")

        saved = persist_inventory_batch(self.workspace, inventory)

        self.assertFalse(saved["reused"])
        self.assertEqual(before, self._source_snapshot())
        self.assertTrue(saved["manifest"].is_file())
        self.assertTrue(saved["report"].is_file())
        self.assertEqual(saved["manifest"].name, MANIFEST_NAME)
        self.assertEqual(saved["report"].name, REPORT_NAME)
        loaded = read_inventory_batch(self.workspace, "batch-r7")
        self.assertEqual(
            loaded["inventory"]["summary"],
            inventory["summary"],
        )
        self.assertEqual(
            loaded["report"]["manifest_sha256"],
            __import__("hashlib").sha256(
                saved["manifest"].read_bytes()
            ).hexdigest(),
        )

    def test_same_batch_same_content_is_idempotent(self):
        (self.source / "one.txt").write_text("one", encoding="utf-8")
        inventory = build_inventory(self.source, batch_id="same-batch")
        first = persist_inventory_batch(self.workspace, inventory)
        manifest_before = first["manifest"].read_bytes()
        report_before = first["report"].read_bytes()

        second = persist_inventory_batch(self.workspace, inventory)

        self.assertTrue(second["reused"])
        self.assertEqual(manifest_before, second["manifest"].read_bytes())
        self.assertEqual(report_before, second["report"].read_bytes())

    def test_same_batch_different_content_fails_closed(self):
        target = self.source / "one.txt"
        target.write_text("one", encoding="utf-8")
        first_inventory = build_inventory(
            self.source, batch_id="conflict"
        )
        first = persist_inventory_batch(
            self.workspace, first_inventory
        )
        manifest_before = first["manifest"].read_bytes()

        target.write_text("changed", encoding="utf-8")
        second_inventory = build_inventory(
            self.source, batch_id="conflict"
        )

        with self.assertRaises(ValueError):
            persist_inventory_batch(
                self.workspace, second_inventory
            )
        self.assertEqual(manifest_before, first["manifest"].read_bytes())

    def test_rejects_batch_store_inside_source_archive(self):
        source = self.source
        workspace = source / "TaxoWorkspace"
        (source / "doc.txt").write_text("doc", encoding="utf-8")
        inventory = build_inventory(source, batch_id="inside-source")

        with self.assertRaises(ValueError):
            persist_inventory_batch(workspace, inventory)

        self.assertFalse(
            (workspace / "Data" / "DocumentLibrary").exists()
        )

    def test_rejects_path_traversal_batch_id(self):
        (self.source / "doc.txt").write_text("doc", encoding="utf-8")
        inventory = build_inventory(
            self.source, batch_id="../outside"
        )

        with self.assertRaises(ValueError):
            persist_inventory_batch(self.workspace, inventory)

    def test_manifest_tamper_is_detected(self):
        (self.source / "doc.txt").write_text("doc", encoding="utf-8")
        inventory = build_inventory(
            self.source, batch_id="tamper"
        )
        saved = persist_inventory_batch(
            self.workspace, inventory
        )
        data = json.loads(saved["manifest"].read_text("utf-8"))
        data["summary"]["files"] = 999
        saved["manifest"].write_text(
            json.dumps(data), encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            read_inventory_batch(self.workspace, "tamper")


if __name__ == "__main__":
    unittest.main()
