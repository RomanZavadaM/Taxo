# -*- coding: utf-8 -*-
"""10.18-r5: read-only offline template-library contract and integrity tests.

No real employee/company document or network resource is used. Tests create
temporary synthetic packages and assert that reading never writes to them.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import template_library_reader as library


def _template():
    return {
        "format": "taxo.template.v1",
        "template_id": "orders.vehicle-assignment",
        "title": "Тестовий наказ",
        "document_kind": "order",
        "scenario": "assignment",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [{
            "name": "company.name", "type": "text", "required": True,
        }],
        "blocks": [{
            "id": "one", "type": "paragraph", "text": "Тест без персональних даних.",
        }],
    }


def _write_package(root, *, template=None, overrides=None):
    template = template if template is not None else _template()
    item_path = "catalog/orders/assignment.json"
    payload = json.dumps(template, ensure_ascii=False, sort_keys=True).encode("utf-8")
    target = root / item_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.uk.general",
        "package_version": "1.0.0",
        "publisher": "Synthetic test publisher",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": template["template_id"], "revision_id": "rev-1",
            "category_id": "orders", "path": item_path,
        }],
        "files": [{
            "path": item_path, "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }],
    }
    manifest.update(overrides or {})
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return target


class ReadOnlyTemplateLibraryR5Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "TemplateLibrary"

    def test_default_is_inside_workspace_not_executable(self):
        self.assertEqual(
            library.default_library_root(Path(self.tmp.name)),
            self.root,
        )

    def test_missing_library_no_write(self):
        result = library.inspect_library(self.root, "10.18-r5")
        self.assertEqual(result.status, "NOT_INSTALLED")
        self.assertFalse(self.root.exists())

    def test_valid_synthetic_catalog_and_read_only(self):
        self.root.mkdir()
        _write_package(self.root)
        before = {
            p.relative_to(self.root).as_posix(): p.read_bytes()
            for p in self.root.rglob("*") if p.is_file()
        }
        result = library.inspect_library(self.root, "10.18-r5")
        self.assertEqual(result.status, "AVAILABLE")
        self.assertEqual(result.package_version, "1.0.0")
        self.assertEqual(len(result.templates), 1)
        self.assertEqual(result.templates[0].category_id, "orders")
        after = {
            p.relative_to(self.root).as_posix(): p.read_bytes()
            for p in self.root.rglob("*") if p.is_file()
        }
        self.assertEqual(before, after)

    def test_older_taxo_incompatible(self):
        self.root.mkdir()
        _write_package(self.root)
        self.assertEqual(library.inspect_library(self.root, "10.18-r4").status, "INCOMPATIBLE")

    def test_tampered_template_is_damaged(self):
        self.root.mkdir()
        path = _write_package(self.root)
        path.write_text("changed", encoding="utf-8")
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_duplicate_json_key_rejected(self):
        self.root.mkdir()
        _write_package(self.root)
        (self.root / "manifest.json").write_text(
            '{"format":"taxo.template-catalog.v1","format":"taxo.template-catalog.v1"}',
            encoding="utf-8",
        )
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_manifest_duplicate_paths_rejected(self):
        self.root.mkdir()
        _write_package(self.root)
        data = json.loads((self.root / "manifest.json").read_text("utf-8"))
        data["files"].append(dict(data["files"][0]))
        (self.root / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_traversal_path_rejected(self):
        self.root.mkdir()
        _write_package(self.root)
        data = json.loads((self.root / "manifest.json").read_text("utf-8"))
        data["files"][0]["path"] = "../secret.json"
        (self.root / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_missing_file_is_damaged(self):
        self.root.mkdir()
        path = _write_package(self.root)
        path.unlink()
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_executable_visible_when_rejected(self):
        self.root.mkdir()
        t = _template()
        t["blocks"][0]["visible_when"] = "__import__('os').system('bad')"
        _write_package(self.root, template=t)
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_revision_collision_rejected(self):
        self.root.mkdir()
        _write_package(self.root)
        data = json.loads((self.root / "manifest.json").read_text("utf-8"))
        data["items"].append(dict(data["items"][0]))
        (self.root / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")

    def test_no_application_or_storage_side_effect(self):
        import inspect
        source = inspect.getsource(library)
        for marker in ("sqlite3", "subprocess", "os.system(", ".mkdir(", ".write_text(",
                       ".write_bytes(", "exec(", "eval("):
            self.assertNotIn(marker, source)

    def test_symlink_in_installed_catalog_rejected(self):
        self.root.mkdir()
        path = _write_package(self.root)
        outside = Path(self.tmp.name) / "outside.json"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        try:
            path.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks not supported in this environment")
        self.assertEqual(library.inspect_library(self.root, "10.18-r5").status, "DAMAGED")


if __name__ == "__main__":
    unittest.main()
