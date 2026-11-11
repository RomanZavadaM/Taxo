# -*- coding: utf-8 -*-
"""Printable paper-first briefing and driver training forms with a workspace catalog.

Generated documents are drafts. No signature, briefing attendance or admission
decision is inferred from the presence of a generated file.
"""
from __future__ import annotations

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


from paper_document_store import (
    CATALOG_NAME, catalog_dir, _safe, _index, list_documents,
    save_document, document_path, open_file,
)
NOTICE = "ПІДГОТОВЛЕНИЙ БЛАНК. ДРУК НЕ ПІДТВЕРДЖУЄ ПРОВЕДЕННЯ ЧИ ПІДПИСАННЯ."
TRAINING_SECTIONS = (
    "I. Робота на внутрішній території підприємства",
    "II. Робота на лінії (маршруті)",
    "III. Контрольна поїздка",
)


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


