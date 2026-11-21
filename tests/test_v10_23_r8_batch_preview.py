# -*- coding: utf-8 -*-
import json
import tempfile
import unittest
from pathlib import Path

from document_import_inventory import build_inventory
from document_import_batch_store import persist_inventory_batch
from document_import_batch_preview import build_batch_preview


class DocumentBatchPreviewR8Tests(unittest.TestCase):
    def setUp(self):
        self.source_tmp = tempfile.TemporaryDirectory()
        self.workspace_tmp = tempfile.TemporaryDirectory()
        self.source = Path(self.source_tmp.name)
        self.workspace = Path(self.workspace_tmp.name)

    def tearDown(self):
        self.source_tmp.cleanup()
        self.workspace_tmp.cleanup()

    def _persist(self, batch_id="r8"):
        inventory = build_inventory(self.source, batch_id=batch_id)
        return persist_inventory_batch(self.workspace, inventory)

    def test_preview_is_read_only_and_deterministic(self):
        (self.source / "b.txt").write_text("b", encoding="utf-8")
        (self.source / "a.txt").write_text("a", encoding="utf-8")
        before = {
            p.name: p.read_bytes()
            for p in self.source.iterdir() if p.is_file()
        }
        self._persist("deterministic")

        first = build_batch_preview(
            self.workspace, "deterministic", "source_asc"
        )
        second = build_batch_preview(
            self.workspace, "deterministic", "source_asc"
        )

        self.assertEqual(first, second)
        self.assertTrue(first["read_only"])
        self.assertEqual(
            [r["source_name"] for r in first["records"]],
            ["a.txt", "b.txt"],
        )
        self.assertEqual(
            before,
            {
                p.name: p.read_bytes()
                for p in self.source.iterdir() if p.is_file()
            },
        )

    def test_date_desc_puts_missing_dates_last(self):
        for name in ("new.txt", "old.txt", "missing.txt"):
            (self.source / name).write_text(name, encoding="utf-8")
        saved = self._persist("dates")
        data = json.loads(saved["manifest"].read_text("utf-8"))
        rows = {row["source_name"]: row for row in data["files"]}
        rows["new.txt"]["document_date"] = "2026-11-21"
        rows["old.txt"]["document_date"] = "2024-01-02"
        rows["missing.txt"]["document_date"] = ""
        self._rewrite_batch(saved, data)

        preview = build_batch_preview(self.workspace, "dates", "date_desc")

        self.assertEqual(
            [r["source_name"] for r in preview["records"]],
            ["new.txt", "old.txt", "missing.txt"],
        )

    def test_number_sort_is_natural_and_empty_last(self):
        for name in ("2.txt", "10.txt", "none.txt"):
            (self.source / name).write_text(name, encoding="utf-8")
        saved = self._persist("numbers")
        data = json.loads(saved["manifest"].read_text("utf-8"))
        rows = {row["source_name"]: row for row in data["files"]}
        rows["2.txt"]["document_number"] = "2-A"
        rows["10.txt"]["document_number"] = "10-A"
        rows["none.txt"]["document_number"] = ""
        self._rewrite_batch(saved, data)

        preview = build_batch_preview(
            self.workspace, "numbers", "number_asc"
        )

        self.assertEqual(
            [r["source_name"] for r in preview["records"]],
            ["2.txt", "10.txt", "none.txt"],
        )

    def test_category_unknown_is_last(self):
        for name in ("a.txt", "b.txt", "u.txt"):
            (self.source / name).write_text(name, encoding="utf-8")
        saved = self._persist("categories")
        data = json.loads(saved["manifest"].read_text("utf-8"))
        rows = {row["source_name"]: row for row in data["files"]}
        rows["a.txt"]["category"] = "Кадрові"
        rows["b.txt"]["category"] = "Експлуатаційні"
        rows["u.txt"]["category"] = "Не визначено"
        self._rewrite_batch(saved, data)

        preview = build_batch_preview(
            self.workspace, "categories", "category_asc"
        )

        self.assertEqual(preview["records"][-1]["source_name"], "u.txt")

    def test_unknown_inventory_format_fails_closed(self):
        (self.source / "one.txt").write_text("one", encoding="utf-8")
        saved = self._persist("future")
        data = json.loads(saved["manifest"].read_text("utf-8"))
        data["format"] = "taxo.document-inventory.v999"
        self._rewrite_batch(saved, data)

        with self.assertRaises(ValueError):
            build_batch_preview(self.workspace, "future")

    def test_missing_or_malformed_batch_fails_closed(self):
        with self.assertRaises(ValueError):
            build_batch_preview(self.workspace, "missing")

        (self.source / "one.txt").write_text("one", encoding="utf-8")
        saved = self._persist("broken")
        saved["report"].write_text("{not-json", encoding="utf-8")
        with self.assertRaises(ValueError):
            build_batch_preview(self.workspace, "broken")

    def _rewrite_batch(self, saved, inventory):
        import hashlib
        from document_import_batch_store import (
            BATCH_FORMAT,
            _canonical_json_bytes,
        )

        manifest_payload = _canonical_json_bytes(inventory)
        saved["manifest"].write_bytes(manifest_payload)
        report = json.loads(saved["report"].read_text("utf-8"))
        report["format"] = BATCH_FORMAT
        report["manifest_sha256"] = hashlib.sha256(
            manifest_payload
        ).hexdigest()
        saved["report"].write_bytes(_canonical_json_bytes(report))


if __name__ == "__main__":
    unittest.main()
