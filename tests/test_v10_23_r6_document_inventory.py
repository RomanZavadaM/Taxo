# -*- coding: utf-8 -*-
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from document_import_inventory import build_inventory, inventory_json


class DocumentInventoryDryRunR6Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _snapshot(self):
        rows = {}
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and not path.is_symlink():
                rows[path.relative_to(self.root).as_posix()] = (
                    path.read_bytes(),
                    path.stat().st_mtime_ns,
                )
        return rows

    def test_inventory_is_read_only_and_manifest_is_machine_readable(self):
        (self.root / "Наказ №10.pdf").write_bytes(b"%PDF-test")
        sub = self.root / "2025"
        sub.mkdir()
        (sub / "лист.txt").write_text("hello", encoding="utf-8")
        before = self._snapshot()

        report = build_inventory(self.root, batch_id="batch-test")
        after = self._snapshot()

        self.assertEqual(before, after)
        self.assertTrue(report["read_only"])
        self.assertEqual(report["import_batch_id"], "batch-test")
        self.assertEqual(report["summary"]["files"], 2)
        self.assertEqual(report["summary"]["errors"], 0)
        parsed = json.loads(inventory_json(report))
        self.assertEqual(parsed["format"], "taxo.document-inventory.v1")
        for row in parsed["files"]:
            self.assertTrue(row["candidate_id"].startswith("cand-"))
            self.assertEqual(len(row["sha256"]), 64)
            self.assertEqual(row["review_state"], "inventory")
            self.assertIsNone(row["ai_confidence"])
            self.assertIn("source_relpath", row)
            self.assertIn("mime_type", row)

    def test_exact_duplicates_use_sha256_but_are_not_deleted(self):
        payload = b"same-document"
        (self.root / "a.docx").write_bytes(payload)
        (self.root / "copy.docx").write_bytes(payload)
        (self.root / "other.docx").write_bytes(b"different")
        before = self._snapshot()

        report = build_inventory(self.root, batch_id="dupes")

        self.assertEqual(before, self._snapshot())
        self.assertEqual(report["summary"]["files"], 3)
        self.assertEqual(report["summary"]["exact_duplicate_groups"], 1)
        self.assertEqual(report["summary"]["exact_duplicate_files"], 2)
        group = report["exact_duplicate_groups"][0]
        self.assertEqual(
            group["sha256"], hashlib.sha256(payload).hexdigest()
        )
        self.assertEqual(len(group["candidate_ids"]), 2)
        rows = {
            row["source_relpath"]: row for row in report["files"]
        }
        self.assertEqual(rows["a.docx"]["duplicate_of"], "")
        self.assertEqual(
            rows["copy.docx"]["duplicate_of"],
            rows["a.docx"]["candidate_id"],
        )
        self.assertTrue((self.root / "a.docx").exists())
        self.assertTrue((self.root / "copy.docx").exists())

    def test_repeat_scan_keeps_candidate_identity_for_unchanged_files(self):
        (self.root / "one.txt").write_text("one", encoding="utf-8")
        first = build_inventory(self.root, batch_id="first")
        second = build_inventory(self.root, batch_id="second")

        self.assertNotEqual(first["import_batch_id"], second["import_batch_id"])
        self.assertEqual(
            first["files"][0]["candidate_id"],
            second["files"][0]["candidate_id"],
        )
        self.assertEqual(
            first["files"][0]["sha256"],
            second["files"][0]["sha256"],
        )

    def test_changed_file_becomes_a_new_candidate(self):
        target = self.root / "one.txt"
        target.write_text("one", encoding="utf-8")
        first = build_inventory(self.root, batch_id="before")
        target.write_text("two", encoding="utf-8")
        second = build_inventory(self.root, batch_id="after")

        self.assertNotEqual(
            first["files"][0]["candidate_id"],
            second["files"][0]["candidate_id"],
        )
        self.assertNotEqual(
            first["files"][0]["sha256"],
            second["files"][0]["sha256"],
        )

    def test_symlinks_are_not_followed(self):
        outside = self.root.parent / (self.root.name + "_outside.txt")
        outside.write_text("outside", encoding="utf-8")
        link = self.root / "external-link.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable")
        try:
            report = build_inventory(self.root, batch_id="links")
            self.assertEqual(report["summary"]["files"], 0)
            self.assertEqual(report["skipped_symlinks"], ["external-link.txt"])
            self.assertEqual(outside.read_text("utf-8"), "outside")
        finally:
            try:
                outside.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
