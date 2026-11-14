# -*- coding: utf-8 -*-
"""10.19-r1: separate user-owned template copies and backup coverage."""
from __future__ import annotations

import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path

import company_template_store as store
import template_library_service
import template_library_ui
import workspace


def _vendor_template():
    return {
        "format": "taxo.template.v1",
        "template_id": "orders.company-copy-test",
        "title": "Тестовий наказ для копії",
        "document_kind": "order",
        "scenario": "assignment",
        "language": "uk",
        "status": "proposed",
        "source_refs": [],
        "variables": [
            {"name": "company.name", "type": "text", "required": True}
        ],
        "blocks": [
            {
                "id": "body",
                "type": "paragraph",
                "text": "Початковий текст {{company.name}}",
            }
        ],
    }


def _write_vendor_library(root):
    root.mkdir(parents=True)
    path = "catalog/orders/company-copy-test.json"
    target = root / path
    target.parent.mkdir(parents=True)
    raw = json.dumps(_vendor_template(), ensure_ascii=False).encode("utf-8")
    target.write_bytes(raw)
    manifest = {
        "format": "taxo.template-catalog.v1",
        "package_id": "taxo.templates.synthetic",
        "package_version": "1.2.3",
        "publisher": "Synthetic fixture",
        "minimum_taxo_version": "10.18-r5",
        "language": "uk",
        "items": [{
            "template_id": "orders.company-copy-test",
            "revision_id": "v1",
            "category_id": "orders",
            "path": path,
        }],
        "files": [{
            "path": path,
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False),
        encoding="utf-8",
    )
    return target


class CompanyTemplatesR1Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "Work"
        self.work.mkdir()
        self.vendor = self.work / "TemplateLibrary"
        self.vendor_file = _write_vendor_library(self.vendor)

    def test_revision_identity_is_10_19_r1(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8").strip(),
            "Version: 10.19-r1",
        )
        self.assertIn(
            'APP_VERSION = "10.19-r1"',
            (root / "main.py").read_text("utf-8"),
        )

    def test_missing_company_storage_is_read_only(self):
        self.assertEqual(store.list_company_templates(self.work), ())
        self.assertFalse((self.work / "CompanyTemplates").exists())

    def test_copy_is_separate_and_preserves_vendor_bytes(self):
        before = self.vendor_file.read_bytes()
        summary = store.create_company_copy(
            self.work, "10.19-r1", "orders.company-copy-test", "v1"
        )
        self.assertEqual(before, self.vendor_file.read_bytes())
        self.assertEqual(
            summary.based_on_template_id, "orders.company-copy-test"
        )
        self.assertEqual(summary.based_on_revision_id, "v1")
        self.assertEqual(store.list_company_templates(self.work), (summary,))
        copied = json.loads(
            (
                self.work / "CompanyTemplates" / "items" / summary.file_name
            ).read_text("utf-8")
        )
        self.assertEqual(
            copied["template"]["blocks"][0]["text"],
            "Початковий текст {{company.name}}",
        )
        self.assertEqual(copied["based_on"]["package_version"], "1.2.3")
        self.assertEqual(
            copied["based_on"]["sha256"],
            hashlib.sha256(before).hexdigest(),
        )

    def test_same_revision_is_not_accidentally_copied_twice(self):
        store.create_company_copy(
            self.work, "10.19-r1", "orders.company-copy-test", "v1"
        )
        with self.assertRaises(ValueError):
            store.create_company_copy(
                self.work, "10.19-r1", "orders.company-copy-test", "v1"
            )
        self.assertEqual(len(store.list_company_templates(self.work)), 1)

    def test_tampered_company_copy_is_detected(self):
        summary = store.create_company_copy(
            self.work, "10.19-r1", "orders.company-copy-test", "v1"
        )
        path = self.work / "CompanyTemplates" / "items" / summary.file_name
        path.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            store.list_company_templates(self.work)

    def test_backup_payload_contains_both_template_zones(self):
        store.create_company_copy(
            self.work, "10.19-r1", "orders.company-copy-test", "v1"
        )
        target = Path(self.temp.name) / "BackupStage"
        target.mkdir()
        workspace._copy_backup_payload(self.work, target)
        self.assertTrue(
            (target / "TemplateLibrary" / "manifest.json").is_file()
        )
        self.assertTrue(
            (target / "CompanyTemplates" / "index.json").is_file()
        )

    def test_backup_refuses_symlink_inside_template_storage(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = self.vendor / "linked.txt"
        try:
            link.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks not supported in this environment")
        target = Path(self.temp.name) / "UnsafeBackupStage"
        target.mkdir()
        with self.assertRaises(ValueError):
            workspace._copy_backup_payload(self.work, target)

    def test_service_and_ui_keep_storage_out_of_main(self):
        service_source = inspect.getsource(template_library_service)
        ui_source = inspect.getsource(template_library_ui)
        import main
        main_source = inspect.getsource(main)
        self.assertIn("create_workspace_company_copy", service_source)
        self.assertIn("Створити власну копію", ui_source)
        self.assertIn("Taxo-company-template-copy", ui_source)
        self.assertNotIn("def create_company_copy", main_source)
        self.assertNotIn("CompanyTemplates", main_source)


if __name__ == "__main__":
    unittest.main()
