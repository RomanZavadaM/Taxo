# -*- coding: utf-8 -*-
"""Printable paper-first briefing and driver training forms with a workspace catalog.

Generated documents are drafts. No signature, briefing attendance or admission
decision is inferred from the presence of a generated file.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from paper_documents_lock import paper_documents_lock

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


CATALOG_NAME = "index.json"
NOTICE = "ПІДГОТОВЛЕНИЙ БЛАНК. ДРУК НЕ ПІДТВЕРДЖУЄ ПРОВЕДЕННЯ ЧИ ПІДПИСАННЯ."
TRAINING_SECTIONS = (
    "I. Робота на внутрішній території підприємства",
    "II. Робота на лінії (маршруті)",
    "III. Контрольна поїздка",
)


def catalog_dir(workspace_root):
    """Everything including files and catalog is inside full-workspace backup."""
    return Path(workspace_root) / "Data" / "PaperDocuments"


def _safe(value, limit=45):
    return re.sub(r"[^\w\-]+", "_", str(value or "").strip(), flags=re.UNICODE).strip("_")[:limit] or "документ"


def _doc():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(2)
    section.right_margin = Cm(1.5)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    return doc


def _title(doc, value):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(str(value))
    run.bold = True
    run.font.size = Pt(13)


def _line(doc, label, value=""):
    doc.add_paragraph("%s %s" % (label, str(value or "").strip()))


def _table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for i, title in enumerate(headers):
        table.rows[0].cells[i].text = title
    for row in rows:
        cells = table.add_row().cells
        for i, cell in enumerate(row):
            cells[i].text = str(cell or "")
    return table


def build_briefing_docx(prepared):
    """Program followed by an unsigned, printable attendance/signature sheet."""
    doc = _doc()
    _title(doc, "ПРОГРАМА ІНСТРУКТАЖУ")
    _line(doc, "Напрям:", prepared["direction"])
    _line(doc, "Вид:", prepared["kind"])
    _line(doc, "Дата:", prepared["day"].strftime("%d.%m.%Y"))
    _line(doc, "Тема:", prepared["topic"])
    if prepared.get("reason"):
        _line(doc, "Підстава:", prepared["reason"])
    _line(doc, "Нормативний орієнтир:", prepared.get("source_note"))
    doc.add_heading("Зміст інструктажу", level=2)
    for paragraph in (prepared.get("program_text") or "").splitlines():
        doc.add_paragraph(paragraph or " ")
    doc.add_page_break()
    _title(doc, "ЛИСТ ОЗНАЙОМЛЕННЯ З ІНСТРУКТАЖЕМ")
    _line(doc, "Напрям / вид:", "%s / %s" % (prepared["direction"], prepared["kind"]))
    _line(doc, "Тема:", prepared["topic"])
    _line(doc, "Дата:", prepared["day"].strftime("%d.%m.%Y"))
    rows = prepared.get("people_records") or ()
    if rows:
        people = [(r.get("name", ""), r.get("personnel_no", "")) for r in rows]
    else:
        people = [(name, "") for name in prepared["people"]]
    _table(doc,
           ("№", "Прізвище, ім'я", "Таб. №", "Підпис працівника", "Підпис інструктора"),
           ((i, name, number, "________________", "________________")
            for i, (name, number) in enumerate(people, 1)))
    doc.add_paragraph("Інструктаж провів(ла): _________________________  Підпис: __________")
    doc.add_paragraph(NOTICE)
    return doc


def build_training_docx(data):
    """Editable driver internship / control-drive sheet (Order No. 975, Annex 3)."""
    doc = _doc()
    _title(doc, "ЛИСТ СТАЖУВАННЯ ВОДІЯ")
    doc.add_paragraph("За структурою додатка 3 до Порядку, затвердженого наказом № 975 від 05.08.2008.")
    for label, key in (
        ("Наказ № / дата:", "order"),
        ("Водій-стажист:", "driver"),
        ("Табельний №:", "personnel_no"),
        ("Посвідчення (серія, №, категорії):", "licence"),
        ("Водійський стаж із року:", "experience_since"),
        ("Транспортний засіб (марка / модель / номер):", "vehicle"),
        ("Водій-інструктор:", "instructor"),
        ("Період стажування:", "period"),
        ("Запланований обсяг, год:", "hours"),
        ("Вид:", "training_kind"),
    ):
        _line(doc, label, data.get(key, ""))
    doc.add_paragraph("Фактичний перебіг стажування (заповнювати за реально виконаною роботою).")
    for section in TRAINING_SECTIONS:
        doc.add_heading(section, level=2)
        _table(doc,
            ("Дата", "Початок", "Кінець", "Години", "Маршрут", "Пробіг", "Підпис інструктора"),
            (("", "", "", "", "", "", "") for _ in range(4)))
    doc.add_heading("Зауваження щодо роботи стажиста", level=2)
    doc.add_paragraph("________________________________________________________________________")
    doc.add_paragraph("________________________________________________________________________")
    _line(doc, "Підпис стажиста:", "________________")
    _line(doc, "Підпис водія-інструктора:", "________________")
    doc.add_heading("Висновок / рішення про допуск", level=2)
    doc.add_paragraph("Допустити / не допустити до роботи на ______________________________")
    doc.add_paragraph("Посадова особа з БДР __________________  підпис __________  дата ________")
    doc.add_paragraph("Водій-інструктор ______________________  підпис __________  дата ________")
    doc.add_paragraph("Ознайомлений керівник водія ___________  підпис __________  дата ________")
    doc.add_paragraph(NOTICE)
    return doc


def _index(root):
    path = catalog_dir(root) / CATALOG_NAME
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Невірний формат реєстру документів")
    return data


def list_documents(root, text_filter=""):
    records = _index(root)
    needle = str(text_filter or "").casefold().strip()
    if needle:
        records = [row for row in records if needle in " ".join(
            str(row.get(k, "")) for k in ("title", "kind", "date", "person")
        ).casefold()]
    return sorted(records, key=lambda row: row["created_at"], reverse=True)


def save_document(root, doc, kind, title, day, person=""):
    """Serialize paper-document updates with backup/transfer in this process."""
    with paper_documents_lock(root):
        return _save_document_locked(root, doc, kind, title, day, person)


def _save_document_locked(root, doc, kind, title, day, person=""):
    """Never overwrite earlier documents; index is atomically replaced."""
    folder = catalog_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    records = _index(root)
    doc_id = uuid.uuid4().hex
    filename = "%s_%s_%s.docx" % (_safe(kind), _safe(day), doc_id[:12])
    target = folder / filename
    with tempfile.NamedTemporaryFile(suffix=".docx", dir=str(folder), delete=False) as f:
        pending = Path(f.name)
    try:
        doc.save(str(pending))
        os.replace(str(pending), str(target))
    finally:
        if pending.exists():
            pending.unlink()
    record = {
        "id": doc_id, "kind": str(kind), "title": str(title),
        "date": str(day), "person": str(person),
        "file": filename, "created_at": datetime.now(timezone.utc).isoformat(),
        "paper_signed": False,
    }
    records.append(record)
    fd, temp_path = tempfile.mkstemp(dir=str(folder), suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(records, stream, ensure_ascii=False, indent=2)
        os.replace(temp_path, str(folder / CATALOG_NAME))
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    return target


def document_path(root, record):
    filename = record.get("file", "")
    if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".docx"):
        raise ValueError("Небезпечне ім'я файла у реєстрі")
    return catalog_dir(root) / filename

def open_file(path):
    """Open the actual editable DOCX using the OS default document handler."""
    import subprocess
    import sys
    path = str(Path(path).resolve())
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
