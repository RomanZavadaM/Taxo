# -*- coding: utf-8 -*-
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from document_import_batch_store import persist_inventory_batch
from document_import_inventory import build_inventory
from document_import_review import (
    REVIEW_FORMAT,
    build_review_queue,
    persist_review_state,
    review_file,
    set_review_decision,
)


class DocumentImportReviewR10Tests(unittest.TestCase):
    def setUp(self):
        self.source_tmp = tempfile.TemporaryDirectory()
        self.workspace_tmp = tempfile.TemporaryDirectory()
        self.source = Path(self.source_tmp.name)
        self.workspace = Path(self.workspace_tmp.name)

    def tearDown(self):
        self.source_tmp.cleanup()
        self.workspace_tmp.cleanup()

    def _persist(self, batch_id):
        inventory = build_inventory(self.source, batch_id=batch_id)
        return persist_inventory_batch(self.workspace, inventory)

    def _field(self, review, field):
        row = review["records"][0]
        return [item for item in row["fields"] if item["field"] == field][0]

    def test_review_queue_defaults_to_needs_review_without_apply(self):
        folder = self.source / "Кадрові"
        folder.mkdir()
        (folder / "Наказ №12 21.11.2026.docx").write_bytes(b"source")
        saved = self._persist("r10-default")
        manifest_before = saved["manifest"].read_bytes()
        report_before = saved["report"].read_bytes()

        review = build_review_queue(self.workspace, "r10-default")

        self.assertEqual(review["format"], REVIEW_FORMAT)
        self.assertFalse(review["applies_changes"])
        self.assertEqual(review["summary"]["records"], 1)
        self.assertEqual(review["summary"]["reviewed_records"], 0)
        self.assertEqual(review["summary"]["needs_review_records"], 1)
        self.assertGreater(review["summary"]["field_decisions"], 0)
        self.assertTrue(
            all(
                item["decision"] == "needs_review"
                for item in review["records"][0]["fields"]
            )
        )
        self.assertEqual(saved["manifest"].read_bytes(), manifest_before)
        self.assertEqual(saved["report"].read_bytes(), report_before)

    def test_confirm_reject_persist_and_restore_after_source_removed(self):
        folder = self.source / "Кадрові"
        folder.mkdir()
        (folder / "Наказ №12 21.11.2026.docx").write_bytes(b"source")
        saved = self._persist("r10-persist")
        manifest_before = saved["manifest"].read_bytes()
        report_before = saved["report"].read_bytes()

        review = build_review_queue(self.workspace, "r10-persist")
        candidate = review["records"][0]["candidate_id"]
        review = set_review_decision(
            review, candidate, "document_number", "confirm"
        )
        review = set_review_decision(
            review, candidate, "title", "reject"
        )
        path = persist_review_state(self.workspace, review)

        self.assertEqual(
            path,
            self.workspace
            / "Data"
            / "DocumentLibrary"
            / "import_reviews"
            / "r10-persist"
            / "review.json",
        )
        self.assertTrue(path.is_file())
        self.assertNotIn("import_batches", path.parts)

        shutil.rmtree(self.source)
        restored = build_review_queue(self.workspace, "r10-persist")

        self.assertEqual(
            self._field(restored, "document_number")["decision"],
            "confirm",
        )
        self.assertEqual(
            self._field(restored, "document_number")["selected_value"],
            "12",
        )
        self.assertEqual(
            self._field(restored, "title")["decision"],
            "reject",
        )
        self.assertEqual(saved["manifest"].read_bytes(), manifest_before)
        self.assertEqual(saved["report"].read_bytes(), report_before)

    def test_ambiguity_requires_explicit_candidate(self):
        (self.source / "Наказ №7 01.01.2026 02.01.2026.docx").write_text(
            "x", encoding="utf-8"
        )
        self._persist("r10-ambiguity")
        review = build_review_queue(self.workspace, "r10-ambiguity")
        candidate = review["records"][0]["candidate_id"]
        date_field = self._field(review, "document_date")

        self.assertIsNone(date_field["proposal"])
        self.assertEqual(
            date_field["candidates"],
            ["2026-01-01", "2026-01-02"],
        )
        with self.assertRaises(ValueError):
            set_review_decision(
                review, candidate, "document_date", "confirm"
            )
        with self.assertRaises(ValueError):
            set_review_decision(
                review,
                candidate,
                "document_date",
                "confirm",
                "2026-03-01",
            )

        selected = set_review_decision(
            review,
            candidate,
            "document_date",
            "confirm",
            "2026-01-02",
        )
        self.assertEqual(
            self._field(selected, "document_date")["selected_value"],
            "2026-01-02",
        )

    def test_proposal_confirm_cannot_change_the_value(self):
        (self.source / "Наказ №7 21.11.2026.docx").write_text(
            "x", encoding="utf-8"
        )
        self._persist("r10-exact")
        review = build_review_queue(self.workspace, "r10-exact")
        candidate = review["records"][0]["candidate_id"]

        with self.assertRaises(ValueError):
            set_review_decision(
                review,
                candidate,
                "document_number",
                "confirm",
                "999",
            )

        confirmed = set_review_decision(
            review,
            candidate,
            "document_number",
            "confirm",
            "7",
        )
        self.assertEqual(
            self._field(confirmed, "document_number")["selected_value"],
            "7",
        )

    def test_reject_and_needs_review_never_accept_selected_value(self):
        (self.source / "Наказ №7.docx").write_text("x", encoding="utf-8")
        self._persist("r10-decisions")
        review = build_review_queue(self.workspace, "r10-decisions")
        candidate = review["records"][0]["candidate_id"]

        with self.assertRaises(ValueError):
            set_review_decision(
                review,
                candidate,
                "document_number",
                "reject",
                "7",
            )
        with self.assertRaises(ValueError):
            set_review_decision(
                review,
                candidate,
                "document_number",
                "needs_review",
                "7",
            )

    def test_record_becomes_reviewed_only_when_all_fields_decided(self):
        (self.source / "Наказ №7 21.11.2026.docx").write_text(
            "x", encoding="utf-8"
        )
        self._persist("r10-complete")
        review = build_review_queue(self.workspace, "r10-complete")
        candidate = review["records"][0]["candidate_id"]

        for item in list(review["records"][0]["fields"]):
            review = set_review_decision(
                review,
                candidate,
                item["field"],
                "reject",
            )

        self.assertEqual(review["records"][0]["review_state"], "reviewed")
        self.assertEqual(review["summary"]["reviewed_records"], 1)
        self.assertEqual(review["summary"]["needs_review_records"], 0)

    def test_stale_proposal_fingerprint_fails_closed(self):
        (self.source / "Наказ №7 21.11.2026.docx").write_text(
            "x", encoding="utf-8"
        )
        self._persist("r10-stale")
        review = build_review_queue(self.workspace, "r10-stale")
        path = persist_review_state(self.workspace, review)

        data = json.loads(path.read_text("utf-8"))
        data["proposal_sha256"] = "0" * 64
        path.write_text(
            json.dumps(data, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            build_review_queue(self.workspace, "r10-stale")

    def test_malformed_persisted_review_fails_closed(self):
        (self.source / "Наказ №7.docx").write_text("x", encoding="utf-8")
        self._persist("r10-broken")
        review = build_review_queue(self.workspace, "r10-broken")
        path = persist_review_state(self.workspace, review)
        path.write_text("{broken-json", encoding="utf-8")

        with self.assertRaises(ValueError):
            build_review_queue(self.workspace, "r10-broken")

    def test_missing_batch_fails_closed(self):
        with self.assertRaises(ValueError):
            build_review_queue(self.workspace, "missing")

    def test_review_file_rejects_bad_batch_id(self):
        with self.assertRaises(ValueError):
            review_file(self.workspace, "../bad")


if __name__ == "__main__":
    unittest.main()
