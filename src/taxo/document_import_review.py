# -*- coding: utf-8 -*-
"""Explicit REVIEW decisions for document-import proposals.

Review state is stored separately from immutable inventory batches and source
files. This module never applies confirmed values to DocumentVault, the Taxo
database, or the source archive.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
from copy import deepcopy
from pathlib import Path

from document_import_proposals import (
    PROPOSAL_FORMAT,
    build_proposal_preview,
    proposal_json,
)


REVIEW_FORMAT = "taxo.document-import-review.v1"
REVIEW_FILE = "review.json"
_DECISIONS = {"confirm", "reject", "needs_review"}
_BATCH_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_WRITE_LOCK = threading.RLock()


def import_reviews_root(workspace_root):
    return Path(workspace_root) / "Data" / "DocumentLibrary" / "import_reviews"


def _text(value):
    return str(value or "").strip()


def _inside(child, parent):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def _proposal_sha256(preview):
    payload = proposal_json(preview).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _field_rows(proposal_record):
    rows = {}
    for item in proposal_record.get("proposals") or []:
        if not isinstance(item, dict):
            raise ValueError("Некоректна proposal-запис")
        field = _text(item.get("field"))
        if not field or field in rows:
            raise ValueError("Некоректне або повторне proposal field")
        rows[field] = {
            "field": field,
            "proposal": {
                "value": item.get("value"),
                "ai_confidence": item.get("ai_confidence"),
                "ai_reason": _text(item.get("ai_reason")),
                "ai_model_or_rule": _text(item.get("ai_model_or_rule")),
            },
            "candidates": [],
            "decision": "needs_review",
            "selected_value": None,
        }

    for item in proposal_record.get("ambiguities") or []:
        if not isinstance(item, dict):
            raise ValueError("Некоректна ambiguity-запис")
        field = _text(item.get("field"))
        candidates = item.get("candidates")
        if (
            not field
            or field in rows
            or not isinstance(candidates, list)
            or len(candidates) < 2
        ):
            raise ValueError("Некоректна ambiguity-запис")
        rows[field] = {
            "field": field,
            "proposal": None,
            "candidates": deepcopy(candidates),
            "decision": "needs_review",
            "selected_value": None,
        }

    return [rows[key] for key in sorted(rows, key=str.casefold)]


def _record_state(fields):
    if not fields:
        return "needs_review"
    if any(item.get("decision") == "needs_review" for item in fields):
        return "needs_review"
    return "reviewed"


def _refresh_summary(review):
    for row in review["records"]:
        row["review_state"] = _record_state(row["fields"])
    review["summary"] = {
        "records": len(review["records"]),
        "reviewed_records": sum(
            row["review_state"] == "reviewed" for row in review["records"]
        ),
        "needs_review_records": sum(
            row["review_state"] == "needs_review" for row in review["records"]
        ),
        "field_decisions": sum(
            len(row["fields"]) for row in review["records"]
        ),
        "confirmed_fields": sum(
            item["decision"] == "confirm"
            for row in review["records"] for item in row["fields"]
        ),
        "rejected_fields": sum(
            item["decision"] == "reject"
            for row in review["records"] for item in row["fields"]
        ),
    }
    return review


def _new_review(preview):
    if preview.get("format") != PROPOSAL_FORMAT:
        raise ValueError("Несумісний proposal format")
    if preview.get("read_only") is not True:
        raise ValueError("Proposal preview не позначено read-only")
    batch_id = _text(preview.get("import_batch_id"))
    if _BATCH_ID.fullmatch(batch_id) is None:
        raise ValueError("Некоректний import_batch_id")

    records = []
    seen = set()
    for proposal_record in preview.get("records") or []:
        if not isinstance(proposal_record, dict):
            raise ValueError("Некоректний proposal record")
        candidate_id = _text(proposal_record.get("candidate_id"))
        digest = _text(proposal_record.get("sha256")).casefold()
        if not candidate_id or candidate_id in seen:
            raise ValueError("Некоректний або повторний candidate_id")
        if _SHA256.fullmatch(digest) is None:
            raise ValueError("Proposal record не має валідного SHA256")
        seen.add(candidate_id)
        fields = _field_rows(proposal_record)
        records.append({
            "candidate_id": candidate_id,
            "sha256": digest,
            "source_relpath": _text(proposal_record.get("source_relpath")),
            "source_name": _text(proposal_record.get("source_name")),
            "review_state": _record_state(fields),
            "fields": fields,
        })

    review = {
        "format": REVIEW_FORMAT,
        "applies_changes": False,
        "import_batch_id": batch_id,
        "proposal_format": preview["format"],
        "proposal_ruleset": _text(preview.get("ruleset")),
        "proposal_sha256": _proposal_sha256(preview),
        "source_root": _text(preview.get("source_root")),
        "records": records,
        "summary": {},
    }
    return _refresh_summary(review)


def build_review_queue(workspace_root, batch_id):
    """Build REVIEW queue from the exact current r9 proposal preview.

    If a persisted review exists, its decisions are restored only when the
    proposal fingerprint, candidate identity, file hash, and fields still match.
    """
    preview = build_proposal_preview(workspace_root, batch_id)
    fresh = _new_review(preview)
    path = review_file(workspace_root, fresh["import_batch_id"])
    if not path.exists():
        return fresh
    saved = _read_review_file(path)
    _validate_saved_against_fresh(saved, fresh)
    return saved


def _find_record(review, candidate_id):
    target = _text(candidate_id)
    for row in review.get("records") or []:
        if _text(row.get("candidate_id")) == target:
            return row
    raise ValueError("Candidate не знайдено у review queue")


def _find_field(record, field):
    target = _text(field)
    for item in record.get("fields") or []:
        if _text(item.get("field")) == target:
            return item
    raise ValueError("Field не знайдено у review queue")


def set_review_decision(
    review,
    candidate_id,
    field,
    decision,
    selected_value=None,
):
    """Return a copy with one explicit user decision changed.

    confirm accepts the exact proposal value, or one candidate from an
    ambiguity record. reject and needs_review never carry a selected value.
    """
    if review.get("format") != REVIEW_FORMAT:
        raise ValueError("Несумісний review format")
    if review.get("applies_changes") is not False:
        raise ValueError("Review state не може APPLY зміни")
    decision = _text(decision)
    if decision not in _DECISIONS:
        raise ValueError("Невідоме review decision")

    result = deepcopy(review)
    record = _find_record(result, candidate_id)
    item = _find_field(record, field)

    if decision == "confirm":
        proposal = item.get("proposal")
        candidates = item.get("candidates") or []
        if proposal is not None:
            expected = proposal.get("value")
            if selected_value is None:
                selected = expected
            elif selected_value != expected:
                raise ValueError(
                    "Можна підтвердити лише точне запропоноване значення"
                )
            else:
                selected = selected_value
        else:
            if selected_value is None or selected_value not in candidates:
                raise ValueError(
                    "Для ambiguity треба явно вибрати один із кандидатів"
                )
            selected = selected_value
        item["decision"] = "confirm"
        item["selected_value"] = selected
    else:
        if selected_value is not None:
            raise ValueError(
                "reject/needs_review не приймає selected_value"
            )
        item["decision"] = decision
        item["selected_value"] = None

    return _refresh_summary(result)


def review_file(workspace_root, batch_id):
    batch_id = _text(batch_id)
    if _BATCH_ID.fullmatch(batch_id) is None:
        raise ValueError("Некоректний import_batch_id")
    return import_reviews_root(workspace_root) / batch_id / REVIEW_FILE


def _validate_review_structure(review):
    if not isinstance(review, dict) or review.get("format") != REVIEW_FORMAT:
        raise ValueError("Несумісний review format")
    if review.get("applies_changes") is not False:
        raise ValueError("Review state не може APPLY зміни")
    batch_id = _text(review.get("import_batch_id"))
    if _BATCH_ID.fullmatch(batch_id) is None:
        raise ValueError("Некоректний import_batch_id")
    if review.get("proposal_format") != PROPOSAL_FORMAT:
        raise ValueError("Review посилається на несумісний proposal format")
    if _SHA256.fullmatch(_text(review.get("proposal_sha256"))) is None:
        raise ValueError("Review не має proposal fingerprint")
    if not isinstance(review.get("records"), list):
        raise ValueError("Review не містить records")

    identities = set()
    for row in review["records"]:
        if not isinstance(row, dict):
            raise ValueError("Некоректний review record")
        identity = _text(row.get("candidate_id"))
        digest = _text(row.get("sha256"))
        if not identity or identity in identities:
            raise ValueError("Некоректний або повторний candidate_id")
        if _SHA256.fullmatch(digest) is None:
            raise ValueError("Review record не має валідного SHA256")
        identities.add(identity)
        fields = row.get("fields")
        if not isinstance(fields, list):
            raise ValueError("Review record не містить fields")
        names = set()
        for item in fields:
            if not isinstance(item, dict):
                raise ValueError("Некоректний review field")
            field = _text(item.get("field"))
            if not field or field in names:
                raise ValueError("Некоректний або повторний review field")
            names.add(field)
            decision = _text(item.get("decision"))
            if decision not in _DECISIONS:
                raise ValueError("Некоректне review decision")
            if decision == "confirm" and item.get("selected_value") is None:
                raise ValueError("Confirmed field не має selected_value")
            if (
                decision != "confirm"
                and item.get("selected_value") is not None
            ):
                raise ValueError(
                    "Непідтверджене field не може мати selected_value"
                )
    return batch_id


def _canonical_json_bytes(data):
    return (
        json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _read_review_file(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Review state не знайдено або пошкоджено")
    try:
        review = json.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Пошкоджений review state") from exc
    _validate_review_structure(review)
    return _refresh_summary(review)


def _validate_saved_against_fresh(saved, fresh):
    _validate_review_structure(saved)
    if saved["import_batch_id"] != fresh["import_batch_id"]:
        raise ValueError("Review має невірний batch ID")
    if saved["proposal_sha256"] != fresh["proposal_sha256"]:
        raise ValueError(
            "Proposal змінився; старі review-рішення не можна підхопити"
        )
    if saved["proposal_ruleset"] != fresh["proposal_ruleset"]:
        raise ValueError("Review має іншу версію ruleset")
    if len(saved["records"]) != len(fresh["records"]):
        raise ValueError("Review не відповідає поточному proposal")
    fresh_by_id = {row["candidate_id"]: row for row in fresh["records"]}
    for row in saved["records"]:
        current = fresh_by_id.get(row["candidate_id"])
        if current is None or row["sha256"] != current["sha256"]:
            raise ValueError("Review identity/hash не відповідає proposal")
        saved_fields = [item["field"] for item in row["fields"]]
        current_fields = [item["field"] for item in current["fields"]]
        if saved_fields != current_fields:
            raise ValueError("Review fields не відповідають proposal")
        for old, new in zip(row["fields"], current["fields"]):
            if (
                old.get("proposal") != new.get("proposal")
                or old.get("candidates") != new.get("candidates")
            ):
                raise ValueError("Review content не відповідає proposal")
    return True


def persist_review_state(workspace_root, review):
    """Atomically persist REVIEW decisions outside immutable import_batches."""
    batch_id = _validate_review_structure(review)
    source_root = Path(_text(review.get("source_root"))).expanduser()
    if not source_root.is_absolute():
        raise ValueError("Review не містить абсолютного source root")

    root = import_reviews_root(workspace_root).resolve()
    target_dir = root / batch_id
    target = target_dir / REVIEW_FILE
    if _inside(root, source_root) or _inside(target_dir, source_root):
        raise ValueError(
            "Сховище review не може бути всередині source-архіву"
        )

    # Rebuild current proposals before writing. This prevents persisting
    # decisions against a stale or different proposal set.
    current = _new_review(
        build_proposal_preview(workspace_root, batch_id)
    )
    _validate_saved_against_fresh(review, current)
    payload = _canonical_json_bytes(_refresh_summary(deepcopy(review)))

    with _WRITE_LOCK:
        data_dir = root.parent.parent
        library_dir = root.parent
        for path, label in (
            (data_dir, "Data"),
            (library_dir, "DocumentLibrary"),
            (root, "import_reviews"),
            (target_dir, batch_id),
        ):
            if path.exists() and (not path.is_dir() or path.is_symlink()):
                raise ValueError("Некоректне сховище %s" % label)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=False)

        temporary = target_dir / (
            ".%s.%s.tmp" % (REVIEW_FILE, uuid.uuid4().hex)
        )
        try:
            with temporary.open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(str(temporary), str(target))
        finally:
            if temporary.exists():
                temporary.unlink()
    return target
