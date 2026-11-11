# -*- coding: utf-8 -*-
"""Документи транспортних засобів: копії, строки дії та контроль актуальності."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from workspace import paths_for, stored_path


DOCUMENT_TYPES = {
    "insurance": "Страховка",
    "additional_liability_insurance": "ДЦВ страхування",
    "inspection": "Протокол ОТК / перевірки технічного стану",
    "temporary_registration": "Тимчасовий реєстраційний документ",
    "registration_certificate": "Постійний техпаспорт / свідоцтво про реєстрацію",
    "tachograph_inspection_protocol": "Протокол перевірки тахографа",
}

# ДЦВ є додатковим, необов'язковим документом. Якщо він внесений,
# дата завершення може контролюватися, але його відсутність не створює
# попередження під час випуску шляхівки.
EXPIRY_REQUIRED = {"insurance", "inspection", "temporary_registration", "tachograph_inspection_protocol"}
OPTIONAL_DOCUMENT_TYPES = {"additional_liability_insurance"}
WARNING_DAYS = 30

ALLOWED_COPY_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def fit_window_to_screen(win, width, height, min_width=420, min_height=260):
    """Fit secondary vehicle-document windows to the usable screen area."""
    win.update_idletasks()
    screen_w = max(640, int(win.winfo_screenwidth()))
    screen_h = max(480, int(win.winfo_screenheight()))
    max_w = max(520, screen_w - 80)
    max_h = max(360, screen_h - 120)
    final_w = max(420, min(int(width), max_w))
    final_h = max(260, min(int(height), max_h))
    win.geometry(f"{final_w}x{final_h}")
    win.minsize(min(int(min_width), final_w), min(int(min_height), final_h))
    win.resizable(True, True)


def active_documents_of_type(con, vehicle_id, doc_type):
    return con.execute(
        """
        SELECT *
          FROM vehicle_documents
         WHERE vehicle_id=? AND doc_type=? AND COALESCE(archived,0)=0
         ORDER BY id DESC
        """,
        (int(vehicle_id), str(doc_type)),
    ).fetchall()


def best_current_document(con, vehicle_id, doc_type, today=None):
    """Choose the strongest current record when several documents coexist.

    Multiple active records of the same type are allowed. This matters for
    temporary registrations/talons and other situations where replacing one
    paper does not automatically invalidate another one.
    """
    rows = active_documents_of_type(con, vehicle_id, doc_type)
    if not rows:
        return None
    today = today or date.today()

    def key(row):
        status = document_status(doc_type, row["valid_until"], today=today)
        try:
            start = parse_date(row["valid_from"]) or date.min
        except ValueError:
            start = date.min
        return (status_rank(status), start, int(row["id"]))

    return max(rows, key=key)


def parse_date(value):
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.")


def iso_date(value):
    parsed = parse_date(value)
    return parsed.isoformat() if parsed else ""


def display_date(value):
    parsed = parse_date(value)
    return parsed.strftime("%d.%m.%Y") if parsed else ""


def document_status(doc_type, valid_until, today=None, warning_days=WARNING_DAYS):
    today = today or date.today()
    text = str(valid_until or "").strip()
    if not text:
        if doc_type in EXPIRY_REQUIRED:
            return "Немає дати дії"
        return "Актуальний"
    try:
        deadline = parse_date(text)
    except ValueError:
        return "Помилка дати"
    days = (deadline - today).days
    if days < 0:
        return "Прострочений"
    if days <= int(warning_days):
        return f"Закінчується: {days} дн."
    return "Актуальний"


def status_rank(status):
    value = str(status or "")
    if value == "Прострочений":
        return 0
    if value in ("Відсутній", "Немає дати дії", "Помилка дати"):
        return 1
    if value.startswith("Закінчується:"):
        return 2
    return 3


def ensure_vehicle_documents_schema(con):
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS vehicle_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
            doc_type TEXT NOT NULL,
            document_no TEXT DEFAULT '',
            issuer TEXT DEFAULT '',
            valid_from TEXT DEFAULT '',
            valid_until TEXT DEFAULT '',
            copy_path TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            archived INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_documents_vehicle
            ON vehicle_documents(vehicle_id, doc_type, archived, id);
        """
    )


def archive_current_document_slot(con, vehicle_id, doc_type, keep_id=None, now=None):
    """Archive the previous current document of the same type only."""
    stamp = now or datetime.now().isoformat(timespec="seconds")
    params = [stamp, int(vehicle_id), str(doc_type)]
    sql = (
        "UPDATE vehicle_documents SET archived=1,updated_at=? "
        "WHERE vehicle_id=? AND COALESCE(archived,0)=0 AND doc_type=?"
    )
    if keep_id is not None:
        sql += " AND id<>?"
        params.append(int(keep_id))
    con.execute(sql, params)


def latest_documents(con, vehicle_id, today=None):
    """Return one effective current record per type without archiving siblings."""
    latest = {}
    for dtype in DOCUMENT_TYPES:
        row = best_current_document(con, vehicle_id, dtype, today=today)
        if row is not None:
            latest[dtype] = row
    return latest


def vehicle_document_summary(con, vehicle_id, today=None):
    """Return effective document requirements for one vehicle.

    Permanent registration certificate/technical passport is always required.
    A temporary registration document is an additional requirement only when
    the vehicle card marks it as required for that ownership/use arrangement.
    """
    latest = latest_documents(con, vehicle_id, today=today)
    vehicle = con.execute(
        "SELECT temporary_registration_required FROM vehicles WHERE id=?",
        (int(vehicle_id),),
    ).fetchone()
    temporary_required = bool(
        vehicle and int(vehicle["temporary_registration_required"] or 0)
    )

    required_types = [
        "insurance",
        "inspection",
        "registration_certificate",
        "tachograph_inspection_protocol",
    ]
    if temporary_required:
        required_types.append("temporary_registration")

    details = []
    for dtype in required_types:
        row = latest.get(dtype)
        status = "Відсутній" if row is None else document_status(
            dtype, row["valid_until"], today=today
        )
        details.append((dtype, DOCUMENT_TYPES[dtype], row, status))

    worst = min((status_rank(x[3]) for x in details), default=3)
    if worst <= 1:
        overall = "Проблема"
    elif worst == 2:
        overall = "Увага"
    else:
        overall = "Актуально"
    return overall, details

def vehicle_document_summary_text(con, vehicle_id, today=None):
    overall, details = vehicle_document_summary(con, vehicle_id, today=today)
    issues = [label for _dtype, label, _row, status in details if status_rank(status) < 3]
    return overall if not issues else f"{overall}: {', '.join(issues)}"


def vehicle_document_warning_lines(con, vehicle_id, today=None):
    """Human-readable current document issues for operational warnings."""
    _overall, details = vehicle_document_summary(con, vehicle_id, today=today)
    warnings = []
    for _dtype, label, row, status in details:
        if status_rank(status) >= 3:
            continue
        meta = []
        if row is not None and str(row["document_no"] or "").strip():
            meta.append(f"№ {row['document_no']}")
        if row is not None and str(row["valid_until"] or "").strip():
            meta.append(f"діє до {display_date(row['valid_until'])}")
        suffix = f" ({', '.join(meta)})" if meta else ""
        warnings.append(f"{label}: {status}{suffix}")
    return warnings



def _required_document_types(con, vehicle_id):
    vehicle = con.execute(
        "SELECT temporary_registration_required FROM vehicles WHERE id=?",
        (int(vehicle_id),),
    ).fetchone()
    temporary_required = bool(
        vehicle and int(vehicle["temporary_registration_required"] or 0)
    )
    required = [
        "insurance",
        "inspection",
        "registration_certificate",
        "tachograph_inspection_protocol",
    ]
    if temporary_required:
        required.append("temporary_registration")
    return required


def _document_validity_interval(row, doc_type):
    """Return an inclusive validity interval, or None for an unusable record.

    Older Taxo records may have an empty valid_from because that field was
    historically optional. For compatibility an empty start is treated as
    unknown/unbounded in operational checks. Expiry-controlled documents
    without valid_until never provide valid coverage.
    """
    try:
        start = parse_date(row["valid_from"]) if str(row["valid_from"] or "").strip() else date.min
        if str(row["valid_until"] or "").strip():
            end = parse_date(row["valid_until"])
        elif doc_type in EXPIRY_REQUIRED:
            return None
        else:
            end = date.max
    except ValueError:
        return None
    if end < start:
        return None
    return start, end


def document_coverage_for_period(con, vehicle_id, doc_type, period_start, period_end):
    """Check continuous active-document coverage for an inclusive trip period."""
    start = period_start if isinstance(period_start, date) else parse_date(period_start)
    end = period_end if isinstance(period_end, date) else parse_date(period_end)
    if start is None or end is None:
        raise ValueError("Період рейсу має містити дату початку і завершення.")
    if end < start:
        raise ValueError("Дата завершення рейсу не може бути раніше дати початку.")

    rows = active_documents_of_type(con, vehicle_id, doc_type)
    intervals = []
    for row in rows:
        interval = _document_validity_interval(row, doc_type)
        if interval is None:
            continue
        valid_from, valid_until = interval
        if valid_until < start or valid_from > end:
            continue
        intervals.append((valid_from, valid_until, row))
    intervals.sort(key=lambda item: (item[0], item[1], int(item[2]["id"])))

    cursor = start
    used = []
    for valid_from, valid_until, row in intervals:
        if valid_until < cursor:
            continue
        if valid_from > cursor:
            break
        used.append(row)
        if valid_until >= end:
            status = document_status(doc_type, row["valid_until"], today=start)
            return True, row, status, used
        cursor = date.fromordinal(valid_until.toordinal() + 1)

    chosen = used[-1] if used else (intervals[0][2] if intervals else None)
    return False, chosen, "Не діє весь рейс", used


def vehicle_document_summary_for_period(con, vehicle_id, period_start, period_end):
    """Required vehicle-document state for the complete trip period."""
    start = period_start if isinstance(period_start, date) else parse_date(period_start)
    end = period_end if isinstance(period_end, date) else parse_date(period_end)
    details = []
    for dtype in _required_document_types(con, vehicle_id):
        covered, row, status, _used = document_coverage_for_period(
            con, vehicle_id, dtype, start, end
        )
        if row is None:
            status = "Відсутній"
        elif not covered:
            status = "Не діє весь рейс"
        details.append((dtype, DOCUMENT_TYPES[dtype], row, status))

    worst = min((status_rank(item[3]) for item in details), default=3)
    overall = "Проблема" if worst <= 1 else ("Увага" if worst == 2 else "Актуально")
    return overall, details


def vehicle_document_warning_lines_for_period(con, vehicle_id, period_start, period_end):
    """Operational warnings using the full planned trip date range."""
    start = period_start if isinstance(period_start, date) else parse_date(period_start)
    end = period_end if isinstance(period_end, date) else parse_date(period_end)
    _overall, details = vehicle_document_summary_for_period(con, vehicle_id, start, end)
    warnings = []
    for _dtype, label, row, status in details:
        if status_rank(status) >= 3:
            continue
        meta = []
        if row is not None and str(row["document_no"] or "").strip():
            meta.append(f"№ {row['document_no']}")
        if row is not None and str(row["valid_from"] or "").strip():
            meta.append(f"з {display_date(row['valid_from'])}")
        if row is not None and str(row["valid_until"] or "").strip():
            meta.append(f"до {display_date(row['valid_until'])}")
        meta.append(f"рейс {start.strftime('%d.%m.%Y')}–{end.strftime('%d.%m.%Y')}")
        warnings.append(f"{label}: {status} ({', '.join(meta)})")
    return warnings

def control_rows(con, active_only=True, today=None):
    sql = "SELECT * FROM vehicles"
    if active_only:
        sql += " WHERE active=1"
    sql += " ORDER BY active DESC,name,plate"
    vehicles = con.execute(sql).fetchall()
    rows = []
    for vehicle in vehicles:
        _overall, details = vehicle_document_summary(con, vehicle["id"], today=today)
        vehicle_name = " — ".join(
            x for x in (vehicle["name"], vehicle["plate"], vehicle["make_model"]) if str(x or "").strip()
        )
        for dtype, label, doc, status in details:
            rows.append(
                {
                    "vehicle_id": vehicle["id"],
                    "vehicle": vehicle_name,
                    "doc_type": dtype,
                    "type_label": label,
                    "document_no": "" if doc is None else (doc["document_no"] or ""),
                    "valid_until": "" if doc is None else (doc["valid_until"] or ""),
                    "status": status,
                    "copy_path": "" if doc is None else (doc["copy_path"] or ""),
                    "rank": status_rank(status),
                }
            )
    rows.sort(key=lambda x: (x["rank"], x["vehicle"].casefold(), x["type_label"].casefold()))
    return rows



def _document_effective_start(row):
    text = str(row["valid_from"] or "").strip()
    if text:
        try:
            return parse_date(text)
        except ValueError:
            pass
    created = str(row["created_at"] or "").strip()[:10]
    if created:
        try:
            return date.fromisoformat(created)
        except ValueError:
            pass
    return date.min


def document_for_date(con, vehicle_id, doc_type, target_date):
    """Return the document record that was effective/latest known on target_date.

    Archived rows are intentionally included so historical reports do not
    silently substitute today's replacement document.
    """
    target = target_date if isinstance(target_date, date) else parse_date(target_date)
    rows = con.execute(
        """
        SELECT *
          FROM vehicle_documents
         WHERE vehicle_id=? AND doc_type=?
         ORDER BY id DESC
        """,
        (int(vehicle_id), str(doc_type)),
    ).fetchall()
    candidates = [
        row for row in rows
        if _document_effective_start(row) <= target
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (_document_effective_start(row), int(row["id"])),
    )


def vehicle_document_summary_at_date(con, vehicle_id, target_date):
    target = target_date if isinstance(target_date, date) else parse_date(target_date)
    vehicle = con.execute(
        "SELECT temporary_registration_required FROM vehicles WHERE id=?",
        (int(vehicle_id),),
    ).fetchone()
    temporary_required = bool(
        vehicle and int(vehicle["temporary_registration_required"] or 0)
    )
    required_types = [
        "insurance",
        "inspection",
        "registration_certificate",
        "tachograph_inspection_protocol",
    ]
    if temporary_required:
        required_types.append("temporary_registration")

    details = []
    for dtype in required_types:
        row = document_for_date(con, vehicle_id, dtype, target)
        status = (
            "Відсутній"
            if row is None
            else document_status(dtype, row["valid_until"], today=target)
        )
        details.append((dtype, DOCUMENT_TYPES[dtype], row, status))

    worst = min((status_rank(item[3]) for item in details), default=3)
    overall = "Проблема" if worst <= 1 else ("Увага" if worst == 2 else "Актуально")
    return overall, details


def vehicle_document_report_rows(con, target_date, active_only=True):
    """Flat report rows for all vehicles on a selected historical date."""
    target = target_date if isinstance(target_date, date) else parse_date(target_date)
    sql = "SELECT * FROM vehicles"
    if active_only:
        sql += " WHERE active=1"
    sql += " ORDER BY active DESC,name,plate,id"
    vehicles = con.execute(sql).fetchall()
    result = []
    for vehicle in vehicles:
        overall, details = vehicle_document_summary_at_date(
            con, vehicle["id"], target
        )
        label = _vehicle_label(vehicle)
        for dtype, type_label, doc, status in details:
            result.append({
                "vehicle_id": vehicle["id"],
                "vehicle": label,
                "vehicle_active": bool(vehicle["active"]),
                "overall": overall,
                "doc_type": dtype,
                "type_label": type_label,
                "document_no": "" if doc is None else (doc["document_no"] or ""),
                "issuer": "" if doc is None else (doc["issuer"] or ""),
                "valid_from": "" if doc is None else (doc["valid_from"] or ""),
                "valid_until": "" if doc is None else (doc["valid_until"] or ""),
                "status": status,
                "copy": bool(doc and (doc["copy_path"] or "").strip()),
                "notes": "" if doc is None else (doc["notes"] or ""),
                "rank": status_rank(status),
            })
    return result


def _reportlab_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        r"C:\\Windows\\Fonts\\arial.ttf",
        r"C:\\Windows\\Fonts\\calibri.ttf",
        str(Path.home() / "Library/Fonts/Arial.ttf"),
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            name = "TaxoVehicleDocs"
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, candidate))
            return name
    return "Helvetica"


def export_vehicle_document_report_pdf(rows, target_date, out_path, company_name=""):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    target = target_date if isinstance(target_date, date) else parse_date(target_date)
    font = _reportlab_font()
    doc = SimpleDocTemplate(
        str(out_path), pagesize=landscape(A4),
        leftMargin=16, rightMargin=16, topMargin=16, bottomMargin=16,
    )
    title_style = ParagraphStyle(
        "title", fontName=font, fontSize=13, leading=16, alignment=TA_CENTER,
    )
    small = ParagraphStyle("small", fontName=font, fontSize=7, leading=8.5)
    story = []
    if str(company_name or "").strip():
        story.append(Paragraph(str(company_name).strip(), title_style))
    story.append(Paragraph(
        f"Стан документів транспортних засобів на {target.strftime('%d.%m.%Y')}",
        title_style,
    ))
    story.append(Spacer(1, 8))
    table_data = [[
        "Автомобіль", "Загальний стан", "Документ", "№ / серія",
        "Від", "Діє до", "Стан", "Копія"
    ]]
    for row in rows:
        table_data.append([
            Paragraph(str(row["vehicle"]), small),
            Paragraph(str(row["overall"]), small),
            Paragraph(str(row["type_label"]), small),
            Paragraph(str(row["document_no"]), small),
            display_date(row["valid_from"]),
            display_date(row["valid_until"]),
            Paragraph(str(row["status"]), small),
            "Є" if row["copy"] else "Немає",
        ])
    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[120, 62, 155, 75, 55, 55, 92, 42],
    )
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324D")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#8A949E")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (4, 1), (7, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
    ]))
    story.append(table)
    doc.build(story)


def export_vehicle_document_report_xlsx(rows, target_date, out_path, company_name=""):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    target = target_date if isinstance(target_date, date) else parse_date(target_date)
    wb = Workbook()
    ws = wb.active
    ws.title = "Документи авто"
    ws.append([str(company_name or "").strip()])
    ws.append([f"Стан документів транспортних засобів на {target.strftime('%d.%m.%Y')}"])
    headers = [
        "Автомобіль", "В експлуатації", "Загальний стан", "Документ",
        "№ / серія", "Ким видано / страхова", "Дата від", "Діє до",
        "Стан", "Копія", "Примітка",
    ]
    ws.append(headers)
    for row in rows:
        ws.append([
            row["vehicle"],
            "Так" if row["vehicle_active"] else "Ні",
            row["overall"],
            row["type_label"],
            row["document_no"],
            row["issuer"],
            display_date(row["valid_from"]),
            display_date(row["valid_until"]),
            row["status"],
            "Є" if row["copy"] else "Немає",
            row["notes"],
        ])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    for cell in ws[1] + ws[2]:
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal="center")
    for cell in ws[3]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="E9EEF4")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=4):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    widths = [30, 14, 16, 36, 18, 28, 13, 13, 22, 10, 36]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:K{max(3, ws.max_row)}"
    wb.save(str(out_path))

def _safe_name(value):
    text = re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄє._ -]+", "_", str(value or "").strip())
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text or "document"


def copy_document_file(data_root, vehicle_id, doc_type, source):
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    if source.suffix.lower() not in ALLOWED_COPY_EXTENSIONS:
        allowed = ", ".join(sorted(ext.upper().lstrip(".") for ext in ALLOWED_COPY_EXTENSIONS))
        raise ValueError(f"Непідтримуваний формат копії. Дозволено: {allowed}.")
    root = paths_for(data_root)["vehicle_documents"] / str(int(vehicle_id)) / str(doc_type)
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target = root / f"{stamp}_{_safe_name(source.name)}"
    shutil.copy2(source, target)
    return stored_path(target, data_root)


def open_external(path):
    target = str(path)
    if os.name == "nt":
        os.startfile(target)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])


def _vehicle_label(vehicle):
    return " — ".join(
        x for x in (vehicle["name"], vehicle["plate"], vehicle["make_model"]) if str(x or "").strip()
    )

def open_vehicle_documents(parent, db_factory, data_root, vehicle, on_change=None):
    """Compatibility entry point; the window implementation lives in vehicle_documents_ui."""
    from vehicle_documents_ui import open_vehicle_documents as open_ui

    return open_ui(
        parent,
        db_factory,
        data_root,
        vehicle,
        on_change=on_change,
    )


def open_vehicle_document_control(parent, db_factory, data_root, on_open_vehicle=None):
    """Compatibility entry point for the vehicle-document control window."""
    from vehicle_documents_ui import open_vehicle_document_control as open_ui

    return open_ui(
        parent,
        db_factory,
        data_root,
        on_open_vehicle=on_open_vehicle,
    )


def __getattr__(name):
    """Keep the historical VehicleDocumentsWindow import available lazily."""
    if name == "VehicleDocumentsWindow":
        from vehicle_documents_ui import VehicleDocumentsWindow

        return VehicleDocumentsWindow
    raise AttributeError(name)
