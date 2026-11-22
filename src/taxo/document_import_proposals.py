# -*- coding: utf-8 -*-
"""Read-only ANALYZE -> PROPOSE metadata hints for document import batches.

This layer consumes only the verified in-memory preview produced by r8. It does
not open source files, write to the persisted batch, register documents, or
apply any proposal.
"""
from __future__ import annotations

import json
import re
from datetime import date

from document_import_batch_preview import build_batch_preview


PROPOSAL_FORMAT = "taxo.document-import-proposals.v1"
RULESET_VERSION = "taxo.document-metadata-hints.v1"

_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_DATE_YMD = re.compile(
    r"(?<!\d)(20\d{2})[-_.](0[1-9]|1[0-2])[-_.]"
    r"(0[1-9]|[12]\d|3[01])(?!\d)"
)
_DATE_DMY = re.compile(
    r"(?<!\d)(0[1-9]|[12]\d|3[01])[.-]"
    r"(0[1-9]|1[0-2])[.-](20\d{2})(?!\d)"
)
_NUMBER = re.compile(
    r"(?<![0-9A-Za-zА-Яа-яІіЇїЄєҐґ])(?:№|no\.?|nº)\s*"
    r"([0-9]+(?:[-_/][0-9A-Za-zА-Яа-яІіЇїЄєҐґ]+)*)",
    re.IGNORECASE,
)
_SPACE = re.compile(r"\s+")

_KIND_RULES = (
    ("order", ("наказ", "order"), 0.98),
    ("instruction", ("інструкц", "instruction"), 0.95),
    ("waybill", ("шляхов", "waybill"), 0.95),
    ("protocol", ("протокол", "protocol"), 0.95),
    ("act", ("акт",), 0.90),
    ("certificate", ("довідк", "certificate"), 0.90),
)

_CATEGORY_RULES = (
    ("Кадрові", ("кадров",), 0.96),
    ("Сезонні заходи", ("сезон",), 0.92),
    ("Охорона праці", ("охорона праці", "occupational safety"), 0.98),
    (
        "Безпека дорожнього руху",
        ("безпека дорож", "безпеки дорож", "бдр", "road safety"),
        0.98,
    ),
    ("Пожежна безпека", ("пожеж", "fire safety"), 0.98),
    ("Експлуатаційні", ("експлуатац",), 0.90),
)


def _text(value):
    return str(value or "").strip()


def _fold(value):
    return _text(value).casefold()


def _identity(row):
    value = _text(row.get("candidate_id") or row.get("document_id"))
    if not value:
        raise ValueError("Inventory record не має стабільного identity")
    return value


def _verified_sha256(row):
    value = _text(row.get("sha256"))
    if not _SHA256.fullmatch(value):
        raise ValueError("Inventory record не має валідного SHA256")
    return value.casefold()


def _source_text(row):
    # Deliberately use strings already present in the verified manifest only.
    # source_path is not consulted and never becomes a filesystem command.
    return " / ".join(
        item for item in (
            _text(row.get("source_relpath")),
            _text(row.get("source_name")),
        ) if item
    )


def _valid_iso_date(year, month, day):
    try:
        return date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return None


def _date_candidates(text):
    values = set()
    for match in _DATE_YMD.finditer(text):
        value = _valid_iso_date(*match.groups())
        if value:
            values.add(value)
    for match in _DATE_DMY.finditer(text):
        day, month, year = match.groups()
        value = _valid_iso_date(year, month, day)
        if value:
            values.add(value)
    return sorted(values)


def _number_candidates(text):
    return sorted({_text(match.group(1)) for match in _NUMBER.finditer(text)})


def _keyword_hit(folded, needle):
    token = needle.casefold()
    # Very short labels/abbreviations must be separate words. This prevents
    # false positives such as "акт" inside "контракт".
    if token in {"акт", "бдр"}:
        return bool(
            re.search(
                r"(?<![0-9A-Za-zА-Яа-яІіЇїЄєҐґ])"
                + re.escape(token)
                + r"(?![0-9A-Za-zА-Яа-яІіЇїЄєҐґ])",
                folded,
            )
        )
    return token in folded


def _keyword_candidates(text, rules):
    folded = _fold(text)
    found = {}
    for value, needles, confidence in rules:
        if any(_keyword_hit(folded, needle) for needle in needles):
            found[value] = confidence
    return sorted(found.items(), key=lambda item: item[0].casefold())


def _title_hint(row):
    name = _text(row.get("source_name"))
    if not name:
        return ""
    stem = re.sub(r"\.[^.]+$", "", name)
    stem = stem.replace("_", " ")
    stem = _SPACE.sub(" ", stem).strip(" .-_")
    if len(re.findall(r"[A-Za-zА-Яа-яІіЇїЄєҐґ]", stem)) < 3:
        return ""
    return stem


def _proposal(field, value, confidence, reason):
    return {
        "field": field,
        "value": value,
        "ai_confidence": round(float(confidence), 2),
        "ai_reason": reason,
        "ai_model_or_rule": RULESET_VERSION,
    }


def _ambiguity(field, candidates, reason):
    return {
        "field": field,
        "candidates": list(candidates),
        "reason": reason,
        "rule": RULESET_VERSION,
    }


def _single_or_ambiguity(
    row, field, candidates, confidence, reason, ambiguities
):
    if _text(row.get(field)):
        return None
    if len(candidates) == 1:
        return _proposal(field, candidates[0], confidence, reason)
    if len(candidates) > 1:
        ambiguities.append(
            _ambiguity(
                field,
                candidates,
                "Знайдено кілька різних значень; автоматичний вибір заборонено",
            )
        )
    return None


def _keyword_proposal(row, field, candidates, ambiguities):
    if _text(row.get(field)):
        return None
    if len(candidates) == 1:
        value, confidence = candidates[0]
        return _proposal(
            field,
            value,
            confidence,
            "Явний ключовий термін у назві/шляху verified manifest",
        )
    if len(candidates) > 1:
        ambiguities.append(
            _ambiguity(
                field,
                [value for value, _confidence in candidates],
                "Знайдено кілька різних явних класифікацій; вибір потребує людини",
            )
        )
    return None


def _review_state(proposals, ambiguities):
    if ambiguities:
        return "needs_review"
    structured = [
        item for item in proposals
        if item["field"] in {
            "document_date",
            "document_number",
            "document_kind",
            "category",
        }
    ]
    if not structured:
        return "needs_review"
    if any(item["ai_confidence"] < 0.80 for item in structured):
        return "needs_review"
    return "proposed"


def _analyze_row(batch_id, row):
    identity = _identity(row)
    digest = _verified_sha256(row)
    source_text = _source_text(row)
    proposals = []
    ambiguities = []

    item = _single_or_ambiguity(
        row,
        "document_date",
        _date_candidates(source_text),
        0.92,
        "Єдина валідна календарна дата у назві/шляху verified manifest",
        ambiguities,
    )
    if item:
        proposals.append(item)

    item = _single_or_ambiguity(
        row,
        "document_number",
        _number_candidates(source_text),
        0.95,
        "Єдиний номер з явним маркером №/No у назві/шляху verified manifest",
        ambiguities,
    )
    if item:
        proposals.append(item)

    item = _keyword_proposal(
        row,
        "document_kind",
        _keyword_candidates(source_text, _KIND_RULES),
        ambiguities,
    )
    if item:
        proposals.append(item)

    item = _keyword_proposal(
        row,
        "category",
        _keyword_candidates(source_text, _CATEGORY_RULES),
        ambiguities,
    )
    if item:
        proposals.append(item)

    # title is deliberately descriptive only. It never upgrades review_state
    # and is not treated as a legally significant document attribute.
    if not _text(row.get("title")) and not _text(row.get("subject")):
        title = _title_hint(row)
        if title:
            proposals.append(
                _proposal(
                    "title",
                    title,
                    0.60,
                    "Чернетка назви лише з імені файла; потребує перевірки",
                )
            )

    return {
        "import_batch_id": _text(batch_id),
        "candidate_id": identity,
        "sha256": digest,
        "source_relpath": _text(row.get("source_relpath")),
        "source_name": _text(row.get("source_name")),
        "review_state": _review_state(proposals, ambiguities),
        "proposals": proposals,
        "ambiguities": ambiguities,
    }


def build_proposal_preview(workspace_root, batch_id):
    """Return deterministic read-only ANALYZE -> PROPOSE results for a batch."""
    preview = build_batch_preview(workspace_root, batch_id, "source_asc")
    records = [
        _analyze_row(preview["import_batch_id"], row)
        for row in preview["records"]
    ]
    return {
        "format": PROPOSAL_FORMAT,
        "read_only": True,
        "ruleset": RULESET_VERSION,
        "import_batch_id": preview["import_batch_id"],
        "source_root": preview["source_root"],
        "records": records,
        "summary": {
            "records": len(records),
            "proposed_records": sum(
                row["review_state"] == "proposed" for row in records
            ),
            "needs_review_records": sum(
                row["review_state"] == "needs_review" for row in records
            ),
            "field_proposals": sum(
                len(row["proposals"]) for row in records
            ),
            "ambiguity_records": sum(
                bool(row["ambiguities"]) for row in records
            ),
        },
    }


def proposal_json(preview):
    """Return byte-stable machine-readable JSON for an unchanged preview."""
    if preview.get("format") != PROPOSAL_FORMAT:
        raise ValueError("Несумісний формат proposal preview")
    if preview.get("read_only") is not True:
        raise ValueError("Proposal preview не позначено read-only")
    return json.dumps(
        preview,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
