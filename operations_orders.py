# -*- coding: utf-8 -*-
"""Taxo 10.7-r2 — експлуатація, накази та закріплення водіїв.

Модуль зберігає наказ як структурований факт. Друкований PDF є представленням,
а не єдиним джерелом даних. Це дозволяє повторно використовувати чинне
закріплення водія у відомостях та інших документах на конкретну дату.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

APP_VERSION = "10.7-r2"

ORDER_DRAFT = "draft"
ORDER_APPROVED = "approved"
ORDER_CANCELLED = "cancelled"
ORDER_STATUS_LABELS = {
    ORDER_DRAFT: "Чернетка",
    ORDER_APPROVED: "Затверджено",
    ORDER_CANCELLED: "Скасовано",
}

TYPE_VEHICLE_ASSIGNMENT = "vehicle_assignment"
TYPE_STORAGE = "vehicle_storage"
TYPE_WORKTIME = "summarized_worktime"
TYPE_REST_PLACES = "driver_rest_places"
TYPE_DRIVER_TRAINING = "driver_training"
TYPE_SAFETY_TRAINING = "safety_training"
TYPE_GENERIC = "generic"

ORDER_TYPE_LABELS = {
    TYPE_VEHICLE_ASSIGNMENT: "Закріплення транспортних засобів за водіями",
    TYPE_STORAGE: "Зберігання транспортних засобів",
    TYPE_WORKTIME: "Організація / підсумований облік робочого часу",
    TYPE_REST_PLACES: "Місця відпочинку водіїв",
    TYPE_DRIVER_TRAINING: "Спеціальна підготовка / стажування водіїв",
    TYPE_SAFETY_TRAINING: "Охорона праці / пожежна безпека",
    TYPE_GENERIC: "Інший наказ з експлуатації",
}

DEFAULT_SUBJECTS = {
    TYPE_VEHICLE_ASSIGNMENT: "Про закріплення автотранспортних засобів",
    TYPE_STORAGE: "Про зберігання транспортних засобів на території підприємства",
    TYPE_WORKTIME: "Про організацію обліку робочого часу",
    TYPE_REST_PLACES: "Про встановлення місць для відпочинку водіїв та зберігання автобусів",
    TYPE_DRIVER_TRAINING: "Про спеціальну підготовку та стажування водіїв",
    TYPE_SAFETY_TRAINING: "Про проведення занять та перевірку знань з охорони праці",
    TYPE_GENERIC: "",
}

DEFAULT_PREAMBLES = {
    TYPE_VEHICLE_ASSIGNMENT: "Для виконання виробничих завдань по перевезенню пасажирів на маршрутах підприємства —",
    TYPE_STORAGE: "З метою впорядкування експлуатації та зберігання транспортних засобів підприємства —",
    TYPE_WORKTIME: "З метою впорядкування режиму та обліку робочого часу працівників підприємства —",
    TYPE_REST_PLACES: "З метою організації відпочинку водіїв та зберігання автобусів під час виконання маршрутів —",
    TYPE_DRIVER_TRAINING: "З метою забезпечення належної підготовки та стажування водіїв підприємства —",
    TYPE_SAFETY_TRAINING: "З метою організації навчання та перевірки знань працівників підприємства —",
    TYPE_GENERIC: "",
}


def _day(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        return date.today().isoformat()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text[:10], fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР або РРРР-ММ-ДД.")


def display_day(value):
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text[:10]).strftime("%d.%m.%Y")
    except Exception:
        return text


def ensure_schema_on_connection(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS operations_settings (
            id INTEGER PRIMARY KEY CHECK(id=1),
            operations_responsible_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            military_transport_responsible_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            order_place TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS operations_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_type TEXT NOT NULL,
            order_no TEXT NOT NULL,
            order_date TEXT NOT NULL,
            place TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            preamble TEXT DEFAULT '',
            body_text TEXT DEFAULT '',
            control_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            approved_at TEXT DEFAULT '',
            cancelled_at TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(order_no, order_date)
        );
        CREATE INDEX IF NOT EXISTS idx_operations_orders_date
            ON operations_orders(order_date DESC,id DESC);

        CREATE TABLE IF NOT EXISTS vehicle_driver_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES operations_orders(id) ON DELETE CASCADE,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
            valid_from TEXT NOT NULL,
            valid_until TEXT DEFAULT '',
            sequence_no INTEGER NOT NULL DEFAULT 1,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(order_id, vehicle_id, employee_id, valid_from)
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_driver_assignments_active
            ON vehicle_driver_assignments(vehicle_id,valid_from,valid_until,employee_id);

        CREATE TABLE IF NOT EXISTS military_statement_approvals (
            report_date TEXT PRIMARY KEY,
            responsible_employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
            fingerprint TEXT NOT NULL,
            row_count INTEGER NOT NULL DEFAULT 0,
            approved_at TEXT NOT NULL,
            note TEXT DEFAULT ''
        );
    """)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "INSERT OR IGNORE INTO operations_settings(id,updated_at) VALUES(1,?)",
        (now,),
    )


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def settings(con):
    ensure_schema_on_connection(con)
    row = con.execute("SELECT * FROM operations_settings WHERE id=1").fetchone()
    return row


def save_settings(con, *, operations_responsible_employee_id=None,
                  military_transport_responsible_employee_id=None, order_place=""):
    ensure_schema_on_connection(con)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """UPDATE operations_settings
              SET operations_responsible_employee_id=?,
                  military_transport_responsible_employee_id=?,
                  order_place=?,updated_at=?
            WHERE id=1""",
        (
            int(operations_responsible_employee_id) if operations_responsible_employee_id else None,
            int(military_transport_responsible_employee_id) if military_transport_responsible_employee_id else None,
            str(order_place or "").strip(), now,
        ),
    )


def employee_name(con, employee_id):
    if not employee_id:
        return ""
    row = con.execute(
        "SELECT last_name,first_name,middle_name FROM employees WHERE id=?",
        (int(employee_id),),
    ).fetchone()
    if row is None:
        return ""
    return " ".join(str(row[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(row[k] or "").strip())


def list_employee_choices(con, active_only=True):
    sql = "SELECT id,last_name,first_name,middle_name,position,active FROM employees"
    if active_only:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY last_name,first_name,middle_name,id"
    result = []
    for row in con.execute(sql).fetchall():
        name = " ".join(str(row[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(row[k] or "").strip())
        position = str(row["position"] or "").strip()
        result.append({"id": int(row["id"]), "name": name, "position": position,
                       "label": name + ((" — " + position) if position else "")})
    return result


def list_vehicle_choices(con, active_only=False):
    sql = "SELECT id,name,plate,make_model,active FROM vehicles"
    if active_only:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY COALESCE(plate,''),name,id"
    result = []
    for row in con.execute(sql).fetchall():
        plate = str(row["plate"] or "").strip()
        name = str(row["make_model"] or row["name"] or "").strip()
        label = " · ".join(x for x in (plate, name) if x) or ("ТЗ #%d" % int(row["id"]))
        result.append({"id": int(row["id"]), "name": name, "plate": plate, "label": label})
    return result


def create_order(con, *, order_type, order_no, order_date, place="", subject="",
                 preamble="", body_text="", control_employee_id=None, note=""):
    ensure_schema_on_connection(con)
    if order_type not in ORDER_TYPE_LABELS:
        raise ValueError("Невідомий тип наказу.")
    number = str(order_no or "").strip()
    if not number:
        raise ValueError("Вкажіть номер наказу.")
    day = _day(order_date)
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO operations_orders(
               order_type,order_no,order_date,place,subject,preamble,body_text,
               control_employee_id,status,note,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            order_type, number, day, str(place or "").strip(),
            str(subject or DEFAULT_SUBJECTS.get(order_type, "")).strip(),
            str(preamble or DEFAULT_PREAMBLES.get(order_type, "")).strip(),
            str(body_text or "").strip(),
            int(control_employee_id) if control_employee_id else None,
            ORDER_DRAFT, str(note or "").strip(), now, now,
        ),
    )
    return int(cur.lastrowid)


def list_orders(con, limit=1000):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT o.*,e.last_name,e.first_name,e.middle_name
             FROM operations_orders o
             LEFT JOIN employees e ON e.id=o.control_employee_id
            ORDER BY o.order_date DESC,o.id DESC LIMIT ?""",
        (int(limit),),
    ).fetchall()


def get_order(con, order_id):
    ensure_schema_on_connection(con)
    return con.execute("SELECT * FROM operations_orders WHERE id=?", (int(order_id),)).fetchone()


def add_vehicle_assignment(con, order_id, vehicle_id, employee_id, *, valid_from,
                           valid_until="", sequence_no=None, note=""):
    ensure_schema_on_connection(con)
    order = get_order(con, order_id)
    if order is None:
        raise ValueError("Наказ не знайдено.")
    if order["order_type"] != TYPE_VEHICLE_ASSIGNMENT:
        raise ValueError("Закріплення ТЗ можна додавати лише до наказу про закріплення.")
    start = _day(valid_from)
    end = _day(valid_until) if valid_until else ""
    if end and end < start:
        raise ValueError("Дата завершення не може бути раніше дати початку.")
    if sequence_no is None:
        row = con.execute(
            "SELECT COALESCE(MAX(sequence_no),0)+1 AS n FROM vehicle_driver_assignments WHERE order_id=?",
            (int(order_id),),
        ).fetchone()
        sequence_no = int(row["n"])
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO vehicle_driver_assignments(
               order_id,vehicle_id,employee_id,valid_from,valid_until,sequence_no,note,created_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (int(order_id), int(vehicle_id), int(employee_id), start, end,
         int(sequence_no), str(note or "").strip(), now),
    )
    return int(cur.lastrowid)


def delete_vehicle_assignment(con, assignment_id):
    con.execute("DELETE FROM vehicle_driver_assignments WHERE id=?", (int(assignment_id),))


def order_assignments(con, order_id):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT a.*,v.name AS vehicle_name,v.plate,v.make_model,
                  e.last_name,e.first_name,e.middle_name,e.position
             FROM vehicle_driver_assignments a
             JOIN vehicles v ON v.id=a.vehicle_id
             JOIN employees e ON e.id=a.employee_id
            WHERE a.order_id=?
            ORDER BY a.sequence_no,a.id""",
        (int(order_id),),
    ).fetchall()


def active_driver_assignments(con, vehicle_id, on_date=None):
    ensure_schema_on_connection(con)
    day = _day(on_date or date.today())
    return con.execute(
        """SELECT a.*,o.order_no,o.order_date,
                  e.last_name,e.first_name,e.middle_name,e.birth_date,
                  e.actual_address,e.registered_address,
                  m.military_specialty,m.military_rank
             FROM vehicle_driver_assignments a
             JOIN operations_orders o ON o.id=a.order_id AND o.status='approved'
             JOIN employees e ON e.id=a.employee_id
             LEFT JOIN employee_military_profile m ON m.employee_id=e.id
            WHERE a.vehicle_id=?
              AND a.valid_from<=?
              AND (COALESCE(a.valid_until,'')='' OR a.valid_until>=?)
            ORDER BY a.sequence_no,a.id""",
        (int(vehicle_id), day, day),
    ).fetchall()


def approve_order(con, order_id):
    ensure_schema_on_connection(con)
    row = get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    if row["order_type"] == TYPE_VEHICLE_ASSIGNMENT:
        if not order_assignments(con, order_id):
            raise ValueError("До наказу про закріплення не додано жодного ТЗ/водія.")
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE operations_orders SET status=?,approved_at=?,updated_at=? WHERE id=?",
        (ORDER_APPROVED, now, now, int(order_id)),
    )


def cancel_order(con, order_id):
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE operations_orders SET status=?,cancelled_at=?,updated_at=? WHERE id=?",
        (ORDER_CANCELLED, now, now, int(order_id)),
    )


def statement_fingerprint(report_date, company, rows):
    payload = {
        "report_date": _day(report_date),
        "company": {
            key: str((company or {}).get(key) or "").strip()
            for key in ("name", "address", "phone", "email", "signer_name", "signer_position")
        },
        "rows": [dict(row) for row in rows],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def approve_military_statement(con, report_date, company, rows, responsible_employee_id, note=""):
    ensure_schema_on_connection(con)
    employee_id = int(responsible_employee_id or 0)
    if not employee_id or con.execute("SELECT 1 FROM employees WHERE id=?", (employee_id,)).fetchone() is None:
        raise ValueError("Не вибрано відповідального за військово-транспортний обов'язок.")
    day = _day(report_date)
    fingerprint = statement_fingerprint(day, company, rows)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """INSERT INTO military_statement_approvals(
               report_date,responsible_employee_id,fingerprint,row_count,approved_at,note
           ) VALUES(?,?,?,?,?,?)
           ON CONFLICT(report_date) DO UPDATE SET
               responsible_employee_id=excluded.responsible_employee_id,
               fingerprint=excluded.fingerprint,row_count=excluded.row_count,
               approved_at=excluded.approved_at,note=excluded.note""",
        (day, employee_id, fingerprint, len(rows), now, str(note or "").strip()),
    )
    return fingerprint


def military_statement_approval(con, report_date):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT a.*,e.last_name,e.first_name,e.middle_name,e.position
             FROM military_statement_approvals a
             LEFT JOIN employees e ON e.id=a.responsible_employee_id
            WHERE a.report_date=?""",
        (_day(report_date),),
    ).fetchone()


def military_statement_is_approved(con, report_date, company, rows):
    approval = military_statement_approval(con, report_date)
    if approval is None:
        return False, None
    current = statement_fingerprint(report_date, company, rows)
    return current == str(approval["fingerprint"] or ""), approval


def _font_path(preferred=None):
    candidates = [
        str(preferred or ""),
        r"C:\Windows\Fonts\times.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for item in candidates:
        if item and Path(item).exists():
            return item
    return ""


def export_order_pdf(path, order, assignments=(), company=None, control_name="", font_path=None):
    """Друк наказу у стилі наданих підприємством зразків."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    font_name = "Times-Roman"
    resolved = _font_path(font_path)
    if resolved:
        font_name = "TaxoOrder"
        try:
            pdfmetrics.registerFont(TTFont(font_name, resolved))
        except Exception:
            font_name = "Times-Roman"

    styles = getSampleStyleSheet()
    normal = ParagraphStyle("OrderNormal", parent=styles["Normal"], fontName=font_name,
                            fontSize=11.5, leading=15, alignment=TA_LEFT)
    center = ParagraphStyle("OrderCenter", parent=normal, alignment=TA_CENTER)
    title = ParagraphStyle("OrderTitle", parent=center, fontSize=15, leading=18, spaceAfter=2)
    bold_center = ParagraphStyle("OrderBoldCenter", parent=center, fontSize=12.5, leading=15)

    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            leftMargin=20*mm, rightMargin=18*mm,
                            topMargin=17*mm, bottomMargin=17*mm)
    company = company or {}
    company_name = str(company.get("name") or "").strip() or "Підприємство"
    signer_position = str(company.get("signer_position") or "").strip() or "Керівник"
    signer_name = str(company.get("signer_name") or "").strip()
    story = [
        Paragraph("<b>Н А К А З</b>", title),
        Paragraph("по %s" % company_name, center),
        Spacer(1, 7*mm),
    ]
    meta = Table([
        [display_day(order["order_date"]), "<b>№ %s</b>" % str(order["order_no"] or ""), str(order["place"] or "")],
    ], colWidths=[55*mm, 55*mm, 55*mm])
    meta.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 11.5),
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
    ]))
    story += [meta, Spacer(1, 8*mm)]
    subject = str(order["subject"] or "").strip()
    if subject:
        story += [Paragraph("<b>%s</b>" % subject, normal), Spacer(1, 5*mm)]
    preamble = str(order["preamble"] or "").strip()
    if preamble:
        story += [Paragraph(preamble, normal), Spacer(1, 6*mm)]
    story += [Paragraph("<b>Н А К А З У Ю:</b>", bold_center), Spacer(1, 5*mm)]

    if str(order["order_type"]) == TYPE_VEHICLE_ASSIGNMENT:
        first_from = display_day(assignments[0]["valid_from"]) if assignments else display_day(order["order_date"])
        story.append(Paragraph(
            "1. Закріпити з %s транспортні засоби підприємства за водіями згідно з наведеною таблицею:" % first_from,
            normal,
        ))
        data = [["№", "Транспортний засіб", "Держ. номер", "Водій"]]
        for idx, item in enumerate(assignments, 1):
            name = " ".join(str(item[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(item[k] or "").strip())
            vehicle = str(item["make_model"] or item["vehicle_name"] or "").strip()
            data.append([idx, vehicle, str(item["plate"] or "").strip(), name])
        table = Table(data, colWidths=[10*mm, 52*mm, 38*mm, 65*mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("FONTNAME", (0,0), (-1,-1), font_name),
            ("FONTSIZE", (0,0), (-1,-1), 10.5),
            ("GRID", (0,0), (-1,-1), 0.45, colors.black),
            ("ALIGN", (0,0), (-1,0), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story += [Spacer(1, 3*mm), table, Spacer(1, 5*mm)]
        control = str(control_name or "").strip()
        if control:
            story.append(Paragraph("2. Контроль за виконанням даного наказу покласти на %s." % control, normal))
    else:
        body = str(order["body_text"] or "").strip()
        if body:
            paragraphs = [p.strip() for p in body.split("\n") if p.strip()]
            for paragraph in paragraphs:
                story.append(Paragraph(paragraph, normal))
                story.append(Spacer(1, 2*mm))
        control = str(control_name or "").strip()
        if control:
            story.append(Paragraph("Контроль за виконанням даного наказу покласти на %s." % control, normal))

    story += [Spacer(1, 15*mm)]
    signature = Table([[signer_position, "________________", signer_name]], colWidths=[60*mm, 45*mm, 55*mm])
    signature.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 11.5),
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
    ]))
    story.append(signature)
    doc.build(story)
    return path
