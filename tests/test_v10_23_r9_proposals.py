# -*- coding: utf-8 -*-
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from document_import_inventory import build_inventory
from document_import_batch_store import persist_inventory_batch
from document_import_proposals import (
    PROPOSAL_FORMAT,
    RULESET_VERSION,
    build_proposal_preview,
    proposal_json,
)


class DocumentImportProposalsR9Tests(unittest.TestCase):
    def setUp(self):
        self.source_tmp = tempfile.TemporaryDirectory()
        self.workspace_tmp = tempfile.TemporaryDirectory()
        self.source = Path(self.source_tmp.name)
        self.workspace = Path(self.workspace_tmp.name)

    def tearDown(self):
        self.source_tmp.cleanup()
        self.workspace_tmp.cleanup()

    def _persist(self, batch_id, inventory=None):
        if inventory is None:
            inventory = build_inventory(self.source, batch_id=batch_id)
        return persist_inventory_batch(self.workspace, inventory)

    def _proposal_map(self, row):
        return {item["field"]: item for item in row["proposals"]}

    def test_clear_hints_are_deterministic_and_do_not_need_source(self):
        folder = self.source / "Кадрові"
        folder.mkdir()
        path = folder / "Наказ №12 від 21.11.2026.docx"
        path.write_bytes(b"immutable-source")
        saved = self._persist("r9-clear")
        manifest_before = saved["manifest"].read_bytes()
        report_before = saved["report"].read_bytes()

        # r9 must work from the verified managed batch, not by re-opening source.
        shutil.rmtree(self.source)

        first = build_proposal_preview(self.workspace, "r9-clear")
        second = build_proposal_preview(self.workspace, "r9-clear")

        self.assertEqual(first, second)
        self.assertEqual(proposal_json(first), proposal_json(second))
        self.assertEqual(first["format"], PROPOSAL_FORMAT)
        self.assertEqual(first["ruleset"], RULESET_VERSION)
        self.assertTrue(first["read_only"])
        self.assertEqual(len(first["records"]), 1)

        row = first["records"][0]
        proposals = self._proposal_map(row)
        self.assertEqual(proposals["document_date"]["value"], "2026-11-21")
        self.assertEqual(proposals["document_number"]["value"], "12")
        self.assertEqual(proposals["document_kind"]["value"], "order")
        self.assertEqual(proposals["category"]["value"], "Кадрові")
        self.assertEqual(row["review_state"], "proposed")
        self.assertEqual(row["ambiguities"], [])
        self.assertTrue(row["candidate_id"].startswith("cand-"))
        self.assertEqual(len(row["sha256"]), 64)

        self.assertEqual(saved["manifest"].read_bytes(), manifest_before)
        self.assertEqual(saved["report"].read_bytes(), report_before)

    def test_multiple_dates_are_reported_not_guessed(self):
        path = self.source / "Наказ №7 01.01.2026 02.01.2026.docx"
        path.write_text("x", encoding="utf-8")
        self._persist("r9-dates")

        preview = build_proposal_preview(self.workspace, "r9-dates")
        row = preview["records"][0]
        proposals = self._proposal_map(row)

        self.assertNotIn("document_date", proposals)
        self.assertEqual(proposals["document_number"]["value"], "7")
        self.assertEqual(row["review_state"], "needs_review")
        self.assertEqual(row["ambiguities"][0]["field"], "document_date")
        self.assertEqual(
            row["ambiguities"][0]["candidates"],
            ["2026-01-01", "2026-01-02"],
        )

    def test_existing_structured_metadata_is_never_overwritten(self):
        path = self.source / "Охорона праці Наказ №11 21.11.2026.docx"
        path.write_text("x", encoding="utf-8")
        inventory = build_inventory(self.source, batch_id="r9-existing")
        row = inventory["files"][0]
        row["document_date"] = "2025-01-02"
        row["document_number"] = "EXISTING"
        row["document_kind"] = "instruction"
        row["category"] = "Кадрові"
        self._persist("r9-existing", inventory)

        preview = build_proposal_preview(self.workspace, "r9-existing")
        result = preview["records"][0]
        fields = {item["field"] for item in result["proposals"]}

        self.assertFalse(
            {"document_date", "document_number", "document_kind", "category"}
            & fields
        )
        self.assertIn("title", fields)
        self.assertEqual(result["review_state"], "needs_review")

    def test_plain_digits_are_not_treated_as_document_number(self):
        path = self.source / "Наказ 2026 15 final.docx"
        path.write_text("x", encoding="utf-8")
        self._persist("r9-no-number")

        row = build_proposal_preview(
            self.workspace, "r9-no-number"
        )["records"][0]
        proposals = self._proposal_map(row)

        self.assertNotIn("document_number", proposals)
        self.assertEqual(proposals["document_kind"]["value"], "order")

    def test_source_path_is_not_used_as_a_classification_command(self):
        path = self.source / "neutral-file.txt"
        path.write_text("x", encoding="utf-8")
        inventory = build_inventory(self.source, batch_id="r9-source-path")
        inventory["files"][0]["source_path"] = (
            "/pretend/Кадрові/Наказ №99 01.01.2025.docx"
        )
        self._persist("r9-source-path", inventory)

        row = build_proposal_preview(
            self.workspace, "r9-source-path"
        )["records"][0]
        fields = {item["field"] for item in row["proposals"]}

        self.assertEqual(fields, {"title"})
        self.assertEqual(row["review_state"], "needs_review")

    def test_conflicting_category_keywords_require_review(self):
        folder = self.source / "Кадрові" / "Охорона праці"
        folder.mkdir(parents=True)
        path = folder / "Наказ №3 21.11.2026.docx"
        path.write_text("x", encoding="utf-8")
        self._persist("r9-category-conflict")

        row = build_proposal_preview(
            self.workspace, "r9-category-conflict"
        )["records"][0]
        proposals = self._proposal_map(row)

        self.assertNotIn("category", proposals)
        self.assertEqual(row["review_state"], "needs_review")
        category_ambiguity = [
            item for item in row["ambiguities"]
            if item["field"] == "category"
        ][0]
        self.assertEqual(
            category_ambiguity["candidates"],
            ["Кадрові", "Охорона праці"],
        )

    def test_invalid_calendar_date_is_not_proposed(self):
        path = self.source / "Наказ №5 31.02.2026.docx"
        path.write_text("x", encoding="utf-8")
        self._persist("r9-invalid-date")

        row = build_proposal_preview(
            self.workspace, "r9-invalid-date"
        )["records"][0]
        proposals = self._proposal_map(row)

        self.assertNotIn("document_date", proposals)
        self.assertEqual(proposals["document_number"]["value"], "5")

    def test_missing_batch_fails_closed(self):
        with self.assertRaises(ValueError):
            build_proposal_preview(self.workspace, "missing")

    def test_proposal_json_rejects_non_proposal_payload(self):
        with self.assertRaises(ValueError):
            proposal_json({"format": "other", "read_only": True})


if __name__ == "__main__":
    unittest.main()
