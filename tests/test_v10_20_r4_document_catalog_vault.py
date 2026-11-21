# -*- coding: utf-8 -*-
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import document_catalog as catalog
from document_vault_store import DocumentVaultRecord


class DocumentCatalogVaultR4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        folder = self.workspace / "Data" / "PaperDocuments"
        folder.mkdir(parents=True)
        (folder / "prepared.docx").write_bytes(b"synthetic")
        (folder / "index.json").write_text(
            json.dumps([{
                "id": "doc-exact",
                "date": "2026-11-16",
                "created_at": "2026-11-16T10:00:00+00:00",
                "kind": "Інструкція",
                "title": "Безпека руху",
                "file": "prepared.docx",
                "prepared_snapshot_id": "pd-" + "1" * 32,
                "company_template_id": "ct-" + "2" * 32,
                "document_family_id": "family-" + "3" * 32,
                "document_revision": 2,
                "content_sha256": "b" * 64,
            }], ensure_ascii=False),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def vault_record(source_document_id="doc-exact", *, vault_id=None, title="Безпека руху"):
        return DocumentVaultRecord(
            vault_id=vault_id or ("vd-" + "4" * 32),
            title=title,
            kind="Інструкція",
            document_date="2026-11-16",
            status="ready",
            created_at="2026-11-16T11:00:00+00:00",
            source_document_id=source_document_id,
            prepared_snapshot_id="pd-" + "1" * 32,
            document_family_id="family-" + "3" * 32,
            document_revision=2,
            company_template_id="ct-" + "2" * 32,
            template_revision=4,
            template_source_sha256="a" * 64,
            content_sha256="b" * 64,
            original_name="prepared.docx",
            storage_key="objects/44/vd-" + "4" * 32 + ".docx",
            size_bytes=1234,
        )

    def test_exact_paper_and_vault_identity_is_one_logical_row(self):
        record = self.vault_record()
        with mock.patch.object(catalog, "list_document_vault", return_value=(record,)):
            result = catalog.read_catalog(self.workspace)
            self.assertEqual(result["total"], 1)
            row = result["rows"][0]
            self.assertEqual(row["source"], "paper")
            self.assertEqual(row["sources"], ("paper", "vault"))
            self.assertEqual(row["source_label"], "Word + сховище")
            self.assertEqual(row["vault_id"], record.vault_id)
            self.assertIn("копія у сховищі", row["file_state"])

            only_vault = catalog.paginate_sources(
                catalog.read_sources(self.workspace),
                source_filter="vault",
            )
            self.assertEqual(only_vault["total"], 1)
            self.assertEqual(only_vault["rows"][0]["source_id"], "doc-exact")

    def test_same_title_and_date_do_not_merge_without_exact_source_id(self):
        other = self.vault_record(
            "doc-other",
            vault_id="vd-" + "5" * 32,
        )
        with mock.patch.object(catalog, "list_document_vault", return_value=(other,)):
            result = catalog.read_catalog(self.workspace)
        self.assertEqual(result["total"], 2)
        sources = {row["source"] for row in result["rows"]}
        self.assertEqual(sources, {"paper", "vault"})
        vault = next(row for row in result["rows"] if row["source"] == "vault")
        self.assertEqual(vault["source_label"], "Сховище")
        self.assertEqual(vault["source_document_id"], "doc-other")

    def test_damaged_vault_does_not_hide_paper_document(self):
        with mock.patch.object(
            catalog,
            "list_document_vault",
            side_effect=ValueError("пошкоджений індекс"),
        ):
            result = catalog.read_catalog(self.workspace)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["rows"][0]["source"], "paper")
        self.assertIn("Помилка сховища документів", result["vault_status"])
        self.assertIn("пошкоджений індекс", result["vault_status"])

    def test_vault_filter_keeps_standalone_vault_records(self):
        record = self.vault_record(
            "missing-paper",
            vault_id="vd-" + "6" * 32,
            title="Окремий архівний запис",
        )
        with mock.patch.object(catalog, "list_document_vault", return_value=(record,)):
            snapshot = catalog.read_sources(self.workspace)
            result = catalog.paginate_sources(snapshot, source_filter="vault")
        self.assertEqual(result["total"], 1)
        row = result["rows"][0]
        self.assertEqual(row["source"], "vault")
        self.assertEqual(row["source_label"], "Сховище")
        self.assertEqual(row["title"], "Окремий архівний запис")

    def test_r4_identity_and_catalog_ui_labels(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.23-r7\n",
        )
        self.assertIn(
            'APP_VERSION = "10.23-r7"',
            (root / "main.py").read_text("utf-8"),
        )
        ui = (root / "src" / "taxo" / "document_catalog_ui.py").read_text("utf-8")
        self.assertIn('"У сховищі": "vault"', ui)
        self.assertIn('"Джерело"', ui)
        self.assertIn("Word + сховище", (root / "src" / "taxo" / "document_catalog.py").read_text("utf-8"))
        self.assertNotIn("DocumentVault", ui.split('text="Сховище:', 1)[1].split("\n", 1)[0])


if __name__ == "__main__":
    unittest.main()
