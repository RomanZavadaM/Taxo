# -*- coding: utf-8 -*-
"""Taxo 9.1 candidate r3 — окремий модуль «Персонал».

Модуль:
- додає окремий верхній розділ «Персонал»;
- залишає стару вкладку водіїв як «Водії»;
- додає загальне масове планування робочих змін для будь-якого працівника;
- додає масове внесення відсутностей/відпусток у табель;
- надає PDF/XLSX табеля у форматі, наближеному до П-5 за наданим зразком;
- не видаляє історичні графіки при внесенні відсутності.
"""
from __future__ import annotations

import calendar
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from v91_features import (
    PATTERN_DAILY,
    PATTERN_WEEKDAYS,
    PATTERN_SELECTED,
    PATTERN_ALTERNATE,
    PATTERN_2_2,
    PATTERN_7_7,
    PATTERN_CUSTOM,
    PATTERNS,
    WEEKDAY_NAMES,
    parse_clock,
    shift_span_minutes,
    pattern_dates,
    widget_alive,
)


APP_VERSION = "9.1 candidate r3"
WINDOW_TITLE = f"Taxo {APP_VERSION} — персонал, водії, графіки та шляхівки"

# Типи, які в ручному табелі перекривають автоматичний робочий план.
# Старі значення «Відпустка»/«Лікарняний» лишаються сумісними.
ABSENCE_TYPES = (
    "Основна щорічна відпустка",
    "Щорічна додаткова відпустка",
    "Додаткова відпустка постраждалим внаслідок Чорнобильської катастрофи",
    "Додаткова оплачувана відпустка працівникам з дітьми",
    "Творча відпустка",
    "Додаткова відпустка у зв’язку з навчанням",
    "Відпустка без збереження зарплати у зв’язку з навчанням",
    "Відпустка без збереження зарплати в обов’язковому порядку",
    "Відпустка без збереження зарплати за згодою сторін",
    "Інші відпустки без збереження зарплати",
    "Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)",
    "Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство",
    "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років",
    "Відпустка для догляду за дитиною до 6 років",
    "Оплачувана тимчасова непрацездатність",
    "Неоплачувана тимчасова непрацездатність",
    "Відрядження",
    "Простій",
    "Прогул",
    "Страйк",
    "Інший невідпрацьований час",
    "Інші види неявок за колективними договорами",
    "Неявка з нез’ясованих причин",
    "Інша причина неявки",
)

P5_CODES = {
    "Робота": ("Р", "01", "Години роботи, передбачені колективним договором"),
    "Відрядження": ("ВД", "07", "Відрядження"),
    "Основна щорічна відпустка": ("В", "08", "Основна щорічна відпустка"),
    "Відпустка": ("В", "08", "Основна щорічна відпустка"),
    "Щорічна додаткова відпустка": ("Д", "09", "Щорічна додаткова відпустка"),
    "Додаткова відпустка постраждалим внаслідок Чорнобильської катастрофи": ("Ч", "10", "Додаткова відпустка, передбачена ст. 20, 21, 30 Закону України про статус і соціальний захист громадян, які постраждали внаслідок Чорнобильської катастрофи"),
    "Творча відпустка": ("ТВ", "11", "Творча відпустка"),
    "Додаткова відпустка у зв’язку з навчанням": ("Н", "12", "Додаткова відпустка у зв’язку з навчанням"),
    "Відпустка без збереження зарплати у зв’язку з навчанням": ("НБ", "13", "Відпустка без збереження зарплати у зв’язку з навчанням"),
    "Відпустка без збереження зарплати в обов’язковому порядку": ("ДБ", "14", "Додаткова відпустка без збереження зарплати в обов’язковому порядку"),
    "Додаткова оплачувана відпустка працівникам з дітьми": ("ДО", "15", "Додаткова оплачувана відпустка працівникам з дітьми"),
    "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років": ("ВП", "16", "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років"),
    "Відпустка для догляду за дитиною до 6 років": ("ДД", "17", "Відпустка для догляду за дитиною до 6 років"),
    "Відпустка без збереження зарплати за згодою сторін": ("НА", "18", "Відпустка без збереження зарплати за згодою сторін"),
    "Інші відпустки без збереження зарплати": ("БЗ", "19", "Інші відпустки без збереження зарплати"),
    "Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)": ("НД", "20", "Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)"),
    "Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство": ("НП", "21", "Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство"),
    "Інший невідпрацьований час": ("ІН", "22", "Інший невідпрацьований час"),
    "Простій": ("П", "23", "Простій"),
    "Прогул": ("ПР", "24", "Прогул"),
    "Страйк": ("С", "25", "Масові невиходи на роботу (страйки)"),
    "Оплачувана тимчасова непрацездатність": ("ТН", "26", "Оплачувана тимчасова непрацездатність"),
    "Лікарняний": ("ТН", "26", "Оплачувана тимчасова непрацездатність"),
    "Неоплачувана тимчасова непрацездатність": ("НН", "27", "Неоплачувана тимчасова непрацездатність"),
    "Неявка з нез’ясованих причин": ("НЗ", "28", "Неявка з нез’ясованих причин"),
    "Інші види неявок за колективними договорами": ("ІВ", "29", "Інші види неявок за колективними договорами"),
    "Інша причина неявки": ("І", "30", "Інші причини неявок"),
}

# Повна таблиця умовних позначень із наданого користувачем зразка П-5.
# Вона окрема від P5_CODES, бо не всі види робочого часу зараз є окремими
# типами дня у Taxo, але у друкованій формі легенда має бути повною.
P5_LEGEND = (
    ("Години роботи, передбачені колдоговором", "Р", "01"),
    ("Години роботи працівників, яким встановлено неповний робочий день (тиждень) згідно з законодавством", "РС", "02"),
    ("Вечірні години роботи", "ВЧ", "03"),
    ("Нічні години роботи", "РН", "04"),
    ("Надурочні години роботи", "НУ", "05"),
    ("Години роботи у вихідні та святкові дні", "РВ", "06"),
    ("Відрядження", "ВД", "07"),
    ("Основна щорічна відпустка", "В", "08"),
    ("Щорічна додаткова відпустка", "Д", "09"),
    ("Додаткова відпустка постраждалим внаслідок Чорнобильської катастрофи", "Ч", "10"),
    ("Творча відпустка", "ТВ", "11"),
    ("Додаткова відпустка у зв’язку з навчанням", "Н", "12"),
    ("Відпустка без збереження заробітної плати у зв’язку з навчанням", "НБ", "13"),
    ("Додаткова відпустка без збереження заробітної плати в обов’язковому порядку", "ДБ", "14"),
    ("Додаткова оплачувана відпустка працівникам, які мають дітей", "ДО", "15"),
    ("Відпустка у зв’язку з вагітністю і пологами / догляд за дитиною до 3 років", "ВП", "16"),
    ("Відпустка для догляду за дитиною до досягнення нею 6-річного віку", "ДД", "17"),
    ("Відпустка без збереження заробітної плати за згодою сторін", "НА", "18"),
    ("Інші відпустки без збереження заробітної плати (на період припинення виконання робіт)", "БЗ", "19"),
    ("Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)", "НД", "20"),
    ("Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство", "НП", "21"),
    ("Інший невідпрацьований час, передбачений законодавством", "ІН", "22"),
    ("Простої", "П", "23"),
    ("Прогули", "ПР", "24"),
    ("Масові невиходи на роботу (страйки)", "С", "25"),
    ("Оплачувана тимчасова непрацездатність", "ТН", "26"),
    ("Неоплачувана тимчасова непрацездатність", "НН", "27"),
    ("Неявки з нез’ясованих причин", "НЗ", "28"),
    ("Інші види неявок, передбачені колективними договорами, угодами", "ІВ", "29"),
    ("Інші причини неявок", "І", "30"),
)

NONWORK_OVERRIDE_TYPES = set(ABSENCE_TYPES) | {"Відпустка", "Лікарняний", "Вихідний", "Відпочинок"}

# Групи підсумкових колонок праворуч, як у наданому зразку П-5.
P5_ABSENCE_GROUPS = (
    ("8-10", {"08", "09", "10"}),
    ("11-15,17,22", {"11", "12", "13", "14", "15", "17", "22"}),
    ("18", {"18"}),
    ("19", {"19"}),
    ("20", {"20"}),
    ("21", {"21"}),
    ("23", {"23"}),
    ("24", {"24"}),
    ("25", {"25"}),
    ("26-27", {"26", "27"}),
    ("28-30", {"28", "29", "30"}),
)


def p5_code(day_type: str):
    return P5_CODES.get(str(day_type or "").strip(), ("", "", ""))


def _safe_hours_to_minutes(core, value):
    if value is None:
        return None
    return core.hours_value_to_minutes(value)


def _employee_label(row):
    full = " ".join(str(row[k] or "").strip() for k in ("last_name", "first_name", "middle_name") if str(row[k] or "").strip())
    personnel = str(row["personnel_no"] or "").strip()
    position = str(row["position"] or "").strip()
    prefix = f"{personnel} | " if personnel else ""
    suffix = f" — {position}" if position else ""
    return prefix + full + suffix


def _all_employee_rows(core, active_only=False):
    con = core.db()
    sql = """SELECT e.*,GROUP_CONCAT(er.role, ', ') roles
             FROM employees e
             LEFT JOIN employee_roles er ON er.employee_id=e.id"""
    if active_only:
        sql += " WHERE e.active=1"
    sql += " GROUP BY e.id ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name"
    rows = con.execute(sql).fetchall()
    con.close()
    return rows


def _employee_role_choices(row):
    roles = []
    raw = str(row["roles"] or "") if "roles" in row.keys() else ""
    for item in raw.split(","):
        item = item.strip()
        if item and item not in roles:
            roles.append(item)
    position = str(row["position"] or "").strip()
    if position and position not in roles:
        roles.append(position)
    if not roles:
        roles.append("Працівник")
    return roles


def collect_p5_data(core, year, month, active_only=True):
    y, m = int(year), int(month)
    days = core.month_dates(y, m)
    employees = _all_employee_rows(core, active_only=active_only)
    con = core.db()
    company = con.execute("SELECT * FROM company WHERE id=1").fetchone()
    out = []
    for employee in employees:
        if not any(core.employee_employed_on(employee, d) for d in days):
            continue
        cells = []
        work_days = 0
        work_minutes = 0
        missing_fact = 0
        absence_counts = {label: 0 for label, _codes in P5_ABSENCE_GROUPS}
        overtime_minutes = 0
        for d in days:
            if not core.employee_employed_on(employee, d):
                cells.append({"code": "", "hours": None, "day_type": "—", "missing": False})
                continue
            row = core.employee_day_time(con, employee["id"], d)
            dtype = str(row["day_type"] or "")
            code, numeric, _label = p5_code(dtype)
            actual = row["actual_minutes"]
            planned = row["planned_minutes"]
            if dtype in NONWORK_OVERRIDE_TYPES:
                hours = actual if actual not in (None, 0) else None
                # A non-zero actual on an absence day is deliberately visible as conflict.
                if hours:
                    missing_fact += 1
            elif actual is not None and actual > 0:
                hours = int(actual)
                code = "РВ" if d.weekday() >= 5 else "Р"
                numeric = "06" if d.weekday() >= 5 else "01"
                work_days += 1
                work_minutes += int(actual)
            elif planned > 0:
                hours = None
                code = "?"
                numeric = ""
                missing_fact += 1
            else:
                hours = None
                # Ordinary weekend / empty day is not annual-leave code «В».
                code = "" if dtype in ("Вихідний", "Відпочинок", "") else code

            if numeric:
                for label, codes in P5_ABSENCE_GROUPS:
                    if numeric in codes:
                        absence_counts[label] += 1
                        break

            if employee["driver_id"]:
                wl = con.execute(
                    "SELECT overtime_hours FROM worklog WHERE driver_id=? AND work_date=?",
                    (employee["driver_id"], d.isoformat()),
                ).fetchone()
                if wl:
                    overtime_minutes += core.hours_value_to_minutes(wl["overtime_hours"] or 0)

            cells.append({
                "code": code,
                "numeric": numeric,
                "hours": hours,
                "day_type": dtype,
                "missing": code == "?",
            })
        out.append({
            "employee_id": employee["id"],
            "personnel_no": employee["personnel_no"] or "",
            "name": core.employee_name(employee),
            "position": employee["position"] or employee["roles"] or "",
            "gender": "",  # у поточній БД поле не ведеться
            "cells": cells,
            "work_days": work_days,
            "work_minutes": work_minutes,
            "overtime_minutes": overtime_minutes,
            "night_minutes": 0,
            "holiday_minutes": 0,
            "absence_counts": absence_counts,
            "missing_fact": missing_fact,
            "tariff_rate": "",  # у поточній БД поле не ведеться
        })
    con.close()
    return {"year": y, "month": m, "days": days, "employees": out, "company": company}


def _report_font(core):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font = "Helvetica"
    font_path = next((p for p in core.report_font_candidates() if os.path.exists(p)), None)
    if font_path:
        try:
            if "TaxoP5Font" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("TaxoP5Font", font_path))
            if "TaxoP5FontBold" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("TaxoP5FontBold", font_path))
            font = "TaxoP5Font"
        except Exception:
            pass
    return font


def export_p5_pdf(core, year, month, out_path, active_only=True):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics

    data = collect_p5_data(core, year, month, active_only)
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(str(out_path), pagesize=(page_w, page_h))
    font = _report_font(core)
    bold = font
    company = (data["company"]["name"] if data["company"] else "") or ""

    def text(x, y, value, size=6, align="left", font_name=None):
        c.setFont(font_name or font, size)
        s = str(value or "")
        if align == "center":
            c.drawCentredString(x, y, s)
        elif align == "right":
            c.drawRightString(x, y, s)
        else:
            c.drawString(x, y, s)

    # Page 1: header + legend
    text(24, page_h - 26, company, 10, "left")
    text(page_w / 2, page_h - 44, "ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ", 12, "center")
    text(page_w - 24, page_h - 24, "Форма за структурою наданого зразка П-5", 6, "right")
    first = data["days"][0].strftime("%d.%m.%Y")
    last = data["days"][-1].strftime("%d.%m.%Y")
    text(page_w - 24, page_h - 38, f"Звітний період: {first} — {last}", 7, "right")

    legend = [(letter, numeric, label) for label, letter, numeric in P5_LEGEND]
    col_gap = 20
    x0 = 24
    total_w = page_w - 48
    col_w = (total_w - col_gap) / 2
    row_h = 17
    top = page_h - 78
    from reportlab.pdfbase.pdfmetrics import stringWidth

    def wrapped_lines(value, size, max_w):
        words = str(value).split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if not cur or stringWidth(trial, font, size) <= max_w:
                cur = trial
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines or [""]

    half = (len(legend) + 1) // 2
    for col in range(2):
        subset = legend[col * half:(col + 1) * half]
        x = x0 + col * (col_w + col_gap)
        y = top
        c.setLineWidth(.5)
        for letter, numeric, label in subset:
            lines = wrapped_lines(label, 5.2, col_w - 58)
            h = max(row_h, 7 + len(lines) * 6)
            c.rect(x, y - h, col_w, h)
            c.line(x + col_w - 56, y - h, x + col_w - 56, y)
            c.line(x + col_w - 28, y - h, x + col_w - 28, y)
            for i, ln in enumerate(lines):
                text(x + 3, y - 8 - i * 6, ln, 5.2)
            text(x + col_w - 42, y - h / 2 - 2, letter, 6.5, "center")
            text(x + col_w - 14, y - h / 2 - 2, numeric, 6.5, "center")
            y -= h
    c.showPage()

    # Page 2+: timesheet table
    employees = data["employees"]
    per_page = 18
    chunks = [employees[i:i + per_page] for i in range(0, len(employees), per_page)] or [[]]
    for page_index, chunk in enumerate(chunks):
        margin = 12
        top_y = page_h - 16
        text(margin, top_y, company, 7)
        text(page_w / 2, top_y, f"ТАБЕЛЬ — {core.month_name_ua(data['month']).upper()} {data['year']}", 9, "center")
        top_y -= 16

        fixed = [18, 49, 18, 98]
        day_w = 10.0
        summary = [22, 28, 22, 22, 22]
        abs_w = [13.2] * len(P5_ABSENCE_GROUPS)
        widths = fixed + [day_w] * len(data["days"]) + summary + abs_w + [30]
        table_w = sum(widths)
        scale = min(1.0, (page_w - 2 * margin) / table_w)
        widths = [w * scale for w in widths]
        header_h = 48
        row_h = 24

        x_positions = [margin]
        for w in widths:
            x_positions.append(x_positions[-1] + w)
        y_header_bottom = top_y - header_h
        c.setStrokeColor(colors.black)
        c.setLineWidth(.35)

        labels = ["№", "Таб. №", "Ст.", "ПІБ, посада"]
        for i, label in enumerate(labels):
            c.rect(x_positions[i], y_header_bottom, widths[i], header_h)
            text(x_positions[i] + widths[i]/2, y_header_bottom + header_h/2 - 2, label, 4.6, "center")

        base = len(fixed)
        for j, d in enumerate(data["days"]):
            idx = base + j
            c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
            text(x_positions[idx] + widths[idx]/2, y_header_bottom + 28, f"{d.day:02d}", 4.5, "center")
            text(x_positions[idx] + widths[idx]/2, y_header_bottom + 17, WEEKDAY_NAMES[d.weekday()], 4.1, "center")

        idx = base + len(data["days"])
        sum_labels = ["дні", "год.", "НУ", "РН", "РВ"]
        for label, w in zip(sum_labels, summary):
            c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
            text(x_positions[idx] + widths[idx]/2, y_header_bottom + 20, label, 4.2, "center")
            idx += 1
        for label, _codes in P5_ABSENCE_GROUPS:
            c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
            c.saveState()
            c.translate(x_positions[idx] + widths[idx]/2 + 1, y_header_bottom + 3)
            c.rotate(90)
            c.setFont(font, 3.8)
            c.drawString(0, 0, label)
            c.restoreState()
            idx += 1
        c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
        text(x_positions[idx] + widths[idx]/2, y_header_bottom + 17, "Оклад", 4.2, "center")

        y = y_header_bottom
        page_work_days = page_work_min = 0
        for n, emp in enumerate(chunk, start=page_index * per_page + 1):
            y -= row_h
            values = [n, emp["personnel_no"], emp["gender"], f"{emp['name']}\n{emp['position']}"]
            for i, value in enumerate(values):
                c.rect(x_positions[i], y, widths[i], row_h)
                if i == 3:
                    parts = str(value).split("\n")
                    text(x_positions[i] + 2, y + 14, parts[0], 4.7)
                    if len(parts) > 1:
                        text(x_positions[i] + 2, y + 6, parts[1], 4.0)
                else:
                    text(x_positions[i] + widths[i]/2, y + 9, value, 4.7, "center")

            for j, cell in enumerate(emp["cells"]):
                pos = base + j
                c.rect(x_positions[pos], y, widths[pos], row_h)
                if cell["code"]:
                    text(x_positions[pos] + widths[pos]/2, y + 14, cell["code"], 4.5, "center")
                if cell["hours"] is not None:
                    hours = core.minutes_hhmm(cell["hours"]).replace(":00", "")
                    text(x_positions[pos] + widths[pos]/2, y + 5, hours, 4.5, "center")
            pos = base + len(data["days"])
            summary_vals = [
                emp["work_days"],
                core.minutes_hhmm(emp["work_minutes"]),
                core.minutes_hhmm(emp["overtime_minutes"]) if emp["overtime_minutes"] else "",
                "",
                "",
            ]
            for value in summary_vals:
                c.rect(x_positions[pos], y, widths[pos], row_h)
                text(x_positions[pos] + widths[pos]/2, y + 9, value, 4.4, "center"); pos += 1
            for label, _codes in P5_ABSENCE_GROUPS:
                c.rect(x_positions[pos], y, widths[pos], row_h)
                value = emp["absence_counts"][label]
                text(x_positions[pos] + widths[pos]/2, y + 9, value if value else "", 4.4, "center"); pos += 1
            c.rect(x_positions[pos], y, widths[pos], row_h)
            text(x_positions[pos] + widths[pos]/2, y + 9, emp["tariff_rate"], 4.2, "center")
            page_work_days += emp["work_days"]
            page_work_min += emp["work_minutes"]

        y -= row_h
        c.rect(margin, y, sum(widths[:4]), row_h)
        text(margin + 2, y + 9, "Всього на сторінці", 5.0)
        pos = 4
        # Blank day totals: report totals are shown in summary columns.
        for _ in data["days"]:
            c.rect(x_positions[pos], y, widths[pos], row_h); pos += 1
        totals = [page_work_days, core.minutes_hhmm(page_work_min), "", "", ""]
        for value in totals:
            c.rect(x_positions[pos], y, widths[pos], row_h)
            text(x_positions[pos] + widths[pos]/2, y + 9, value, 4.5, "center"); pos += 1
        while pos < len(widths):
            c.rect(x_positions[pos], y, widths[pos], row_h); pos += 1

        text(margin, 18, "«?» = є план роботи, але факт ще не внесено. Поля статі та окладу не заповнюються, бо ці реквізити зараз не ведуться в Taxo.", 4.8)
        c.showPage()

    c.save()
    return data


def export_p5_xlsx(core, year, month, out_path, active_only=True):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    data = collect_p5_data(core, year, month, active_only)
    wb = Workbook()
    ws = wb.active
    ws.title = "Табель П-5"
    legend_ws = wb.create_sheet("Умовні позначення")
    company = (data["company"]["name"] if data["company"] else "") or ""

    thin = Side(style="thin", color="333333")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    header_fill = PatternFill("solid", fgColor="D9E6F2")
    conflict_fill = PatternFill("solid", fgColor="FFF2CC")

    day_start_col = 5
    summary_start = day_start_col + len(data["days"])
    abs_start = summary_start + 5
    last_col = abs_start + len(P5_ABSENCE_GROUPS)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    ws.cell(1, 1, company)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    ws.cell(2, 1, f"ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ — {core.month_name_ua(data['month']).upper()} {data['year']}")
    for row in (1, 2):
        ws.cell(row, 1).font = Font(bold=True, size=13 if row == 2 else 11)
        ws.cell(row, 1).alignment = Alignment(horizontal="center")

    fixed_headers = ["№", "Табельний номер", "Стать", "ПІБ, посада"]
    for col, label in enumerate(fixed_headers, 1):
        c = ws.cell(4, col, label); c.font = Font(bold=True); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for j, d in enumerate(data["days"], day_start_col):
        c = ws.cell(4, j, f"{d.day:02d}\n{WEEKDAY_NAMES[d.weekday()]}")
        c.font = Font(bold=True, size=8); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    summary_headers = ["Роб. дні", "Години", "Надур.", "Нічні", "Вих./святк."]
    for off, label in enumerate(summary_headers):
        c = ws.cell(4, summary_start + off, label); c.font = Font(bold=True, size=8); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for off, (label, _codes) in enumerate(P5_ABSENCE_GROUPS):
        c = ws.cell(4, abs_start + off, label); c.font = Font(bold=True, size=7); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", text_rotation=90, wrap_text=True)
    c = ws.cell(4, last_col, "Оклад / тарифна ставка")
    c.font = Font(bold=True, size=8); c.fill = header_fill; c.border = border
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    row = 5
    for seq, emp in enumerate(data["employees"], 1):
        code_row = row
        hour_row = row + 1
        for col, value in enumerate([seq, emp["personnel_no"], emp["gender"], f"{emp['name']}\n{emp['position']}"], 1):
            ws.merge_cells(start_row=code_row, start_column=col, end_row=hour_row, end_column=col)
            c = ws.cell(code_row, col, value); c.border = border
            c.alignment = Alignment(horizontal="left" if col == 4 else "center", vertical="center", wrap_text=True)

        for j, cell in enumerate(emp["cells"], day_start_col):
            cc = ws.cell(code_row, j, cell["code"])
            hc = ws.cell(hour_row, j, (cell["hours"] / 60.0) if cell["hours"] is not None else None)
            for cell_obj in (cc, hc):
                cell_obj.border = border
                cell_obj.alignment = Alignment(horizontal="center", vertical="center")
            if cell["missing"]:
                cc.fill = conflict_fill
        first_letter = get_column_letter(day_start_col)
        last_letter = get_column_letter(day_start_col + len(data["days"]) - 1)
        # Формули працюють на нижньому (годинному) рядку.
        ws.cell(code_row, summary_start, "дні")
        ws.cell(hour_row, summary_start, f"=COUNT({first_letter}{hour_row}:{last_letter}{hour_row})")
        ws.cell(code_row, summary_start + 1, "год.")
        ws.cell(hour_row, summary_start + 1, f"=SUM({first_letter}{hour_row}:{last_letter}{hour_row})")
        ws.cell(hour_row, summary_start + 2, emp["overtime_minutes"] / 60.0 if emp["overtime_minutes"] else None)
        ws.cell(hour_row, summary_start + 3, None)
        ws.cell(hour_row, summary_start + 4, None)
        for col in range(summary_start, summary_start + 5):
            for rr in (code_row, hour_row):
                ws.cell(rr, col).border = border
                ws.cell(rr, col).alignment = Alignment(horizontal="center", vertical="center")

        code_range = f"{first_letter}{code_row}:{last_letter}{code_row}"
        for off, (_label, codes) in enumerate(P5_ABSENCE_GROUPS):
            formula = "+".join(f'COUNTIF({code_range},"{letter}")' for dtype, (letter, num, _desc) in P5_CODES.items() if num in codes and letter)
            # Deduplicate repeated legacy aliases such as «Відпустка»/«Лікарняний».
            unique_letters = []
            for dtype, (letter, num, _desc) in P5_CODES.items():
                if num in codes and letter and letter not in unique_letters:
                    unique_letters.append(letter)
            formula = "+".join(f'COUNTIF({code_range},"{letter}")' for letter in unique_letters) or "0"
            ws.merge_cells(start_row=code_row, start_column=abs_start + off, end_row=hour_row, end_column=abs_start + off)
            cell = ws.cell(code_row, abs_start + off, f"={formula}")
            cell.border = border; cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells(start_row=code_row, start_column=last_col, end_row=hour_row, end_column=last_col)
        ws.cell(code_row, last_col, emp["tariff_rate"]).border = border
        row += 2

    # Total row
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
    ws.cell(row, 1, "Всього")
    for col in range(1, last_col + 1):
        ws.cell(row, col).border = border
    ws.cell(row, summary_start, f"=SUM({get_column_letter(summary_start)}6:{get_column_letter(summary_start)}{row-1})")
    ws.cell(row, summary_start + 1, f"=SUM({get_column_letter(summary_start+1)}6:{get_column_letter(summary_start+1)}{row-1})")

    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 7
    ws.column_dimensions["D"].width = 30
    for col in range(day_start_col, day_start_col + len(data["days"])):
        ws.column_dimensions[get_column_letter(col)].width = 4.1
    for col in range(summary_start, last_col + 1):
        ws.column_dimensions[get_column_letter(col)].width = 7.5
    ws.row_dimensions[4].height = 72
    ws.freeze_panes = "E5"
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:4"
    ws.print_area = f"A1:{get_column_letter(last_col)}{row}"

    legend_ws.append(["Умовне позначення", "Буквений код", "Цифровий код"])
    for label, letter, numeric in P5_LEGEND:
        legend_ws.append([label, letter, numeric])
    for row_cells in legend_ws.iter_rows():
        for c in row_cells:
            c.border = border; c.alignment = Alignment(vertical="top", wrap_text=True)
    for c in legend_ws[1]:
        c.font = Font(bold=True); c.fill = header_fill
    legend_ws.column_dimensions["A"].width = 85
    legend_ws.column_dimensions["B"].width = 16
    legend_ws.column_dimensions["C"].width = 16
    legend_ws.page_setup.orientation = "landscape"
    legend_ws.page_setup.paperSize = legend_ws.PAPERSIZE_A4
    legend_ws.page_setup.fitToWidth = 1
    legend_ws.sheet_properties.pageSetUpPr.fitToPage = True

    wb.save(str(out_path))
    return data


def install(core, base_app):
    if getattr(core, "_TAXO_PERSONNEL_R3_INSTALLED", False):
        return core.App

    original_employee_day_time = core.employee_day_time

    def employee_day_time_with_absence(con, employee_id, target_date):
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        entry = con.execute(
            "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
            (employee_id, target_date.isoformat()),
        ).fetchone()
        if entry and str(entry["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
            actual = (
                core.hours_value_to_minutes(entry["actual_hours"])
                if entry["actual_hours"] is not None else 0
            )
            return {
                "day_type": entry["day_type"],
                "planned_minutes": 0,
                "actual_minutes": actual,
                "source": "масова/ручна відсутність",
                "notes": entry["notes"] or "",
                "manual": True,
            }
        return original_employee_day_time(con, employee_id, target_date)

    core.employee_day_time = employee_day_time_with_absence
    core.TAXO_NONWORK_OVERRIDE_TYPES = set(NONWORK_OVERRIDE_TYPES)

    class PersonnelApp(base_app):
        def build_ui(self):
            super().build_ui()
            nb = self.main_notebook
            try:
                nb.tab(self.tab_drivers, text="Водії")
            except core.tk.TclError:
                pass
            self.tab_personnel = core.ttk.Frame(nb)
            nb.insert(1, self.tab_personnel, text="Персонал")
            self._build_personnel_section()

            # Numeric tab indexes became unstable after adding «Персонал».
            # Keep a label-based preference from r3 onward.
            def remember_section(_event=None):
                try:
                    current = nb.select()
                    core.set_setting("main_last_tab_label_r3", nb.tab(current, "text"))
                except Exception:
                    pass
            nb.bind("<<NotebookTabChanged>>", remember_section, add="+")
            saved_label = core.get_setting("main_last_tab_label_r3", "")
            if saved_label:
                try:
                    for index in range(nb.index("end")):
                        if nb.tab(index, "text") == saved_label:
                            nb.select(index)
                            break
                except core.tk.TclError:
                    pass

        def build_menu(self):
            result = super().build_menu()
            try:
                menu_name = self.cget("menu")
                menubar = self.nametowidget(menu_name)
                sections = None
                end = menubar.index("end")
                for index in range((end or -1) + 1):
                    if menubar.type(index) == "cascade" and menubar.entrycget(index, "label") == "Розділи":
                        sections = self.nametowidget(menubar.entrycget(index, "menu"))
                        break
                if sections is not None:
                    sections.insert_command(1, label="Персонал", accelerator="Alt+2", command=lambda: self.show_tab(self.tab_personnel))
                    # Після додавання нового верхнього розділу зсуваємо підписи
                    # Alt+... так, щоб вони відповідали фактичним індексам вкладок.
                    menu_end = sections.index("end")
                    for item_index in range((menu_end or -1) + 1):
                        if sections.type(item_index) == "command":
                            sections.entryconfigure(item_index, accelerator=f"Alt+{item_index+1}")
                    self.bind_all(
                        "<Alt-Key-9>",
                        lambda _event: (self.main_notebook.select(8), "break")[1],
                        add="+",
                    )
            except Exception:
                pass
            return result

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title(WINDOW_TITLE)

        def _build_personnel_section(self):
            root = self.tab_personnel
            book = core.ttk.Notebook(root)
            book.pack(fill="both", expand=True, padx=8, pady=8)
            overview = core.ttk.Frame(book)
            planning = core.ttk.Frame(book)
            timesheet = core.ttk.Frame(book)
            reports = core.ttk.Frame(book)
            book.add(overview, text="Реєстр")
            book.add(planning, text="Планування")
            book.add(timesheet, text="Табель")
            book.add(reports, text="Звіти")

            # Реєстр
            bar = core.ttk.Frame(overview, padding=8); bar.pack(fill="x")
            core.ttk.Button(bar, text="Відкрити картки працівників", command=self.show_employee_registry).pack(side="left", padx=3)
            core.ttk.Button(bar, text="Оновити", command=self._refresh_personnel_overview).pack(side="left", padx=3)
            frame = core.ttk.Frame(overview); frame.pack(fill="both", expand=True, padx=8, pady=(0,8))
            frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
            cols = ("personnel","name","position","roles","employment","status")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings")
            self.personnel_overview_tree = tree
            for key,label,width in (
                ("personnel","Таб. №",90),("name","ПІБ",290),("position","Посада",190),
                ("roles","Спеціальні ролі",190),("employment","Прийнятий",100),("status","Стан",90),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
            sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
            tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
            self._refresh_personnel_overview()

            # Планування
            panel = core.ttk.Frame(planning, padding=16); panel.pack(fill="x")
            core.ttk.Label(panel, text="Планування персоналу", font=("TkDefaultFont", 13, "bold")).pack(anchor="w")
            core.ttk.Label(
                panel,
                text="Робочі зміни плануються для будь-якого працівника. Відсутності вносяться інтервалом і перекривають автоматичний план у табелі, не видаляючи історичний графік.",
                foreground="gray", wraplength=950, justify="left"
            ).pack(anchor="w", pady=(4,12))
            core.ttk.Button(panel, text="Робочі зміни — масово…", command=self.show_general_personnel_shift_planner).pack(anchor="w", pady=4)
            core.ttk.Button(panel, text="Відпустки / лікарняні / інші відсутності…", command=self.show_personnel_absence_planner).pack(anchor="w", pady=4)
            core.ttk.Button(panel, text="Лікар / механік для випуску на лінію…", command=self.show_dispatch_month_planner).pack(anchor="w", pady=4)

            # Табель
            tpanel = core.ttk.Frame(timesheet, padding=16); tpanel.pack(fill="x")
            core.ttk.Label(tpanel, text="Табель персоналу", font=("TkDefaultFont",13,"bold")).pack(anchor="w")
            core.ttk.Label(tpanel, text="Щоденний табель, місячний баланс, ручний факт і контроль відсутнього факту.", foreground="gray").pack(anchor="w", pady=(4,12))
            core.ttk.Button(tpanel, text="Відкрити табель персоналу", command=self.show_employee_timesheet).pack(anchor="w", pady=4)
            core.ttk.Button(tpanel, text="Масово внести відсутність…", command=self.show_personnel_absence_planner).pack(anchor="w", pady=4)

            # Звіти
            rpanel = core.ttk.Frame(reports, padding=16); rpanel.pack(fill="x")
            now = date.today()
            self.personnel_report_month = core.tk.StringVar(value=str(now.month))
            self.personnel_report_year = core.tk.StringVar(value=str(now.year))
            self.personnel_report_active = core.tk.BooleanVar(value=True)
            row = core.ttk.Frame(rpanel); row.pack(fill="x")
            core.ttk.Label(row,text="Місяць").pack(side="left")
            core.ttk.Spinbox(row,textvariable=self.personnel_report_month,from_=1,to=12,width=5).pack(side="left",padx=(4,10))
            core.ttk.Label(row,text="Рік").pack(side="left")
            core.ttk.Spinbox(row,textvariable=self.personnel_report_year,from_=2020,to=2100,width=7).pack(side="left",padx=(4,10))
            core.ttk.Checkbutton(row,text="Тільки активні працівники",variable=self.personnel_report_active).pack(side="left",padx=10)
            core.ttk.Label(rpanel,text="Табель П-5 — за структурою наданого зразка: умовні позначення, 1–31 число, відпрацьований час і причини неявок.",foreground="gray",wraplength=980,justify="left").pack(anchor="w",pady=(12,8))
            b = core.ttk.Frame(rpanel); b.pack(fill="x")
            core.ttk.Button(b,text="Табель П-5 — PDF",command=lambda:self._save_p5("pdf")).pack(side="left",padx=(0,5))
            core.ttk.Button(b,text="Табель П-5 — Excel",command=lambda:self._save_p5("xlsx")).pack(side="left",padx=5)
            core.ttk.Button(b,text="Звичайний місячний табель",command=self.show_employee_timesheet).pack(side="left",padx=(16,5))

        def _refresh_personnel_overview(self):
            tree = getattr(self, "personnel_overview_tree", None)
            if not widget_alive(tree):
                return
            for item in tree.get_children(): tree.delete(item)
            for row in _all_employee_rows(core, active_only=False):
                tree.insert("", "end", values=(
                    row["personnel_no"] or "",
                    core.employee_name(row),
                    row["position"] or "",
                    row["roles"] or "",
                    core.fmt_date(row["employment_date"]),
                    "Працює" if row["active"] else "Звільнений",
                ))

        def _active_employee_map(self):
            rows = _all_employee_rows(core, active_only=True)
            return {_employee_label(row): row for row in rows}

        def show_general_personnel_shift_planner(self):
            existing = getattr(self, "_personnel_shift_win", None)
            if widget_alive(existing):
                existing.lift(); return
            win = core.tk.Toplevel(self); self._personnel_shift_win = win
            win.title("Масове планування робочих змін персоналу")
            core.fit_window_to_screen(win, 980, 720, 780, 560)
            body = core.ttk.Frame(win, padding=10); body.pack(fill="both", expand=True)
            body.columnconfigure(1, weight=1); body.rowconfigure(11, weight=1)

            employees = self._active_employee_map()
            employee_var = core.tk.StringVar(value=next(iter(employees), ""))
            role_var = core.tk.StringVar()
            start_var = core.tk.StringVar(value=date.today().replace(day=1).strftime("%d.%m.%Y"))
            last = date.today().replace(day=calendar.monthrange(date.today().year,date.today().month)[1])
            end_var = core.tk.StringVar(value=last.strftime("%d.%m.%Y"))
            pattern_var = core.tk.StringVar(value=PATTERN_WEEKDAYS)
            shift_var = core.tk.StringVar(value="I")
            start_time = core.tk.StringVar(value="08:00")
            end_time = core.tk.StringVar(value="17:00")
            end_day = core.tk.StringVar(value="0")
            location = core.tk.StringVar()
            note = core.tk.StringVar(value="Місячний план персоналу")
            replace = core.tk.BooleanVar(value=False)
            cycle_work = core.tk.StringVar(value="2")
            cycle_rest = core.tk.StringVar(value="2")
            weekdays = [core.tk.BooleanVar(value=(i<5)) for i in range(7)]

            def field(row,label,var,calendar_btn=False):
                core.ttk.Label(body,text=label).grid(row=row,column=0,sticky="w",pady=4,padx=(0,8))
                core.ttk.Entry(body,textvariable=var).grid(row=row,column=1,sticky="ew",pady=4)
                if calendar_btn: core.calendar_button(body,var).grid(row=row,column=2,sticky="w",padx=4)

            core.ttk.Label(body,text="Працівник").grid(row=0,column=0,sticky="w",pady=4)
            emp_combo=core.ttk.Combobox(body,textvariable=employee_var,values=list(employees),state="readonly")
            emp_combo.grid(row=0,column=1,sticky="ew",pady=4)
            core.ttk.Label(body,text="Роль / посада").grid(row=1,column=0,sticky="w",pady=4)
            role_combo=core.ttk.Combobox(body,textvariable=role_var,state="readonly")
            role_combo.grid(row=1,column=1,sticky="ew",pady=4)
            field(2,"Період з",start_var,True); field(3,"Період до",end_var,True)
            core.ttk.Label(body,text="Схема").grid(row=4,column=0,sticky="w",pady=4)
            core.ttk.Combobox(body,textvariable=pattern_var,values=PATTERNS,state="readonly").grid(row=4,column=1,sticky="w",pady=4)

            times=core.ttk.Frame(body); times.grid(row=5,column=0,columnspan=3,sticky="ew",pady=4)
            for label,var,width in (("Зміна",shift_var,5),("Початок",start_time,8),("D+",end_day,4),("Кінець",end_time,8),("Місце",location,20)):
                core.ttk.Label(times,text=label).pack(side="left",padx=(0,3))
                if label=="Зміна":
                    core.ttk.Combobox(times,textvariable=var,values=("I","II"),state="readonly",width=width).pack(side="left",padx=(0,10))
                elif label=="D+":
                    core.ttk.Spinbox(times,textvariable=var,from_=0,to=7,width=width).pack(side="left",padx=(0,10))
                else:
                    core.ttk.Entry(times,textvariable=var,width=width).pack(side="left",padx=(0,10))

            wf=core.ttk.Frame(body); wf.grid(row=6,column=0,columnspan=3,sticky="w",pady=4)
            core.ttk.Label(wf,text="Дні тижня").pack(side="left",padx=(0,6))
            for i,label in enumerate(WEEKDAY_NAMES):
                core.ttk.Checkbutton(wf,text=label,variable=weekdays[i]).pack(side="left")

            cycle=core.ttk.Frame(body); cycle.grid(row=7,column=0,columnspan=3,sticky="w",pady=4)
            core.ttk.Label(cycle,text="Власний цикл: робота").pack(side="left")
            core.ttk.Spinbox(cycle,textvariable=cycle_work,from_=1,to=31,width=4).pack(side="left",padx=4)
            core.ttk.Label(cycle,text="дн. / відпочинок").pack(side="left")
            core.ttk.Spinbox(cycle,textvariable=cycle_rest,from_=1,to=31,width=4).pack(side="left",padx=4)
            core.ttk.Label(cycle,text="дн.").pack(side="left")

            field(8,"Примітка",note)
            core.ttk.Checkbutton(body,text="Замінювати існуючий ПЛАН цього працівника (факт не змінювати)",variable=replace).grid(row=9,column=0,columnspan=3,sticky="w",pady=4)

            tree=core.ttk.Treeview(body,columns=("date","action","current"),show="headings")
            for k,l,w in (("date","Дата",95),("action","Дія",220),("current","Поточне / конфлікт",520)):
                tree.heading(k,text=l); tree.column(k,width=w,anchor="w")
            sy=core.ttk.Scrollbar(body,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=sy.set)
            tree.grid(row=11,column=0,columnspan=2,sticky="nsew",pady=(8,0)); sy.grid(row=11,column=2,sticky="ns",pady=(8,0))

            def refresh_roles(_event=None):
                emp=employees.get(employee_var.get())
                choices=_employee_role_choices(emp) if emp else []
                role_combo["values"]=choices
                if role_var.get() not in choices: role_var.set(choices[0] if choices else "")

            def parse():
                emp=employees.get(employee_var.get())
                if not emp: raise ValueError("Виберіть працівника.")
                start=datetime.strptime(start_var.get().strip(),"%d.%m.%Y").date()
                end=datetime.strptime(end_var.get().strip(),"%d.%m.%Y").date()
                wd=[i for i,v in enumerate(weekdays) if v.get()]
                dates=pattern_dates(
                    start,end,pattern_var.get(),weekdays=wd,
                    work_days=int(cycle_work.get()),rest_days=int(cycle_rest.get())
                )
                if pattern_var.get()==PATTERN_SELECTED and not wd: raise ValueError("Виберіть дні тижня.")
                dplus=int(end_day.get()); minutes=shift_span_minutes(start_time.get(),end_time.get(),dplus)
                return emp,dates,dplus,minutes

            def evaluate(show_error=True):
                try:
                    emp,dates,dplus,minutes=parse()
                except Exception as exc:
                    if show_error: core.messagebox.showerror("Планування",str(exc),parent=win)
                    return None,[]
                con=core.db(); rows=[]
                for d in dates:
                    if not core.employee_employed_on(emp,d):
                        rows.append((d,"Поза періодом роботи","")); continue
                    absence=con.execute(
                        "SELECT day_type,notes FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (emp["id"],d.isoformat())
                    ).fetchone()
                    if absence and str(absence["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
                        rows.append((d,"Відсутність — не планувати",f"{absence['day_type']} · {absence['notes'] or ''}")); continue
                    own=con.execute("""SELECT * FROM employee_shifts WHERE employee_id=? AND role=? AND work_date=? AND shift_no=? ORDER BY id""",
                                    (emp["id"],role_var.get(),d.isoformat(),1 if shift_var.get()=="I" else 2)).fetchall()
                    if any(r["actual_hours"] is not None for r in own):
                        rows.append((d,"Факт — не змінювати","")); continue
                    if own and not replace.get():
                        rows.append((d,"Вже заплановано — пропустити",f"{own[0]['start_time']}–{own[0]['end_time']}")); continue
                    # Any overlapping shift of the same employee (even another role) is conflict.
                    any_rows=con.execute("SELECT * FROM employee_shifts WHERE employee_id=? AND work_date BETWEEN ? AND ?",
                                         (emp["id"],(d-timedelta(days=1)).isoformat(),(d+timedelta(days=1)).isoformat())).fetchall()
                    start_dt=datetime.combine(d,datetime.min.time())+timedelta(minutes=parse_clock(start_time.get()))
                    end_dt=datetime.combine(d+timedelta(days=dplus),datetime.min.time())+timedelta(minutes=parse_clock(end_time.get()))
                    conflict=None
                    for rr in any_rows:
                        if own and rr["id"] in {x["id"] for x in own}: continue
                        base=date.fromisoformat(rr["work_date"])
                        rs=datetime.combine(base,datetime.min.time())+timedelta(minutes=parse_clock(rr["start_time"]))
                        re=datetime.combine(base+timedelta(days=int(rr["end_day_offset"] or 0)),datetime.min.time())+timedelta(minutes=parse_clock(rr["end_time"]))
                        if start_dt < re and rs < end_dt: conflict=rr; break
                    if conflict:
                        rows.append((d,"Конфлікт з іншою зміною",f"{conflict['role']} {conflict['start_time']}–{conflict['end_time']}")); continue
                    rows.append((d,"Замінити план" if own else "Додати",""))
                con.close(); return (emp,dates,dplus,minutes),rows

            def preview():
                for x in tree.get_children(): tree.delete(x)
                _plan,rows=evaluate()
                for d,a,curr in rows: tree.insert("","end",values=(d.strftime("%d.%m.%Y"),a,curr))

            def apply():
                plan,rows=evaluate()
                if not plan: return
                writable=[x for x in rows if x[1] in ("Додати","Замінити план")]
                if not writable:
                    core.messagebox.showinfo("Планування","Немає дат для запису.",parent=win); return
                if not core.messagebox.askyesno("Планування",f"Записати {len(writable)} змін(и)?",parent=win): return
                emp,dates,dplus,minutes=plan; con=core.db(); added=0; skipped=0
                now_note=note.get().strip()
                for d,action,_curr in rows:
                    if action not in ("Додати","Замінити план"): skipped+=1; continue
                    absence=con.execute(
                        "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (emp["id"],d.isoformat())
                    ).fetchone()
                    if absence and str(absence["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
                        skipped+=1; continue
                    own=con.execute("SELECT * FROM employee_shifts WHERE employee_id=? AND role=? AND work_date=? AND shift_no=?",
                                    (emp["id"],role_var.get(),d.isoformat(),1 if shift_var.get()=="I" else 2)).fetchall()
                    if any(r["actual_hours"] is not None for r in own): skipped+=1; continue
                    if own and replace.get():
                        con.executemany("DELETE FROM employee_shifts WHERE id=? AND actual_hours IS NULL",[(r["id"],) for r in own])
                    elif own:
                        skipped+=1; continue
                    try:
                        con.execute("""INSERT INTO employee_shifts(employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,location,planned_hours,actual_hours,status,notes)
                                      VALUES(?,?,?,?,?,?,?,?,?,NULL,'planned',?)""",
                                    (emp["id"],role_var.get(),d.isoformat(),1 if shift_var.get()=="I" else 2,start_time.get(),dplus,end_time.get(),location.get().strip(),minutes/60.0,now_note))
                        added+=1
                    except Exception:
                        skipped+=1
                con.commit(); con.close(); preview()
                core.messagebox.showinfo("Планування",f"Записано: {added}. Пропущено: {skipped}.",parent=win)

            buttons=core.ttk.Frame(body); buttons.grid(row=10,column=0,columnspan=3,sticky="ew")
            core.ttk.Button(buttons,text="Переглянути",command=preview).pack(side="left",padx=3)
            core.ttk.Button(buttons,text="Застосувати",command=apply).pack(side="left",padx=3)
            emp_combo.bind("<<ComboboxSelected>>",refresh_roles)
            refresh_roles(); preview()

        def show_personnel_absence_planner(self):
            existing=getattr(self,"_personnel_absence_win",None)
            if widget_alive(existing): existing.lift(); return
            win=core.tk.Toplevel(self); self._personnel_absence_win=win
            win.title("Масове внесення відпусток / лікарняних / відсутностей")
            core.fit_window_to_screen(win,980,700,760,540)
            body=core.ttk.Frame(win,padding=10); body.pack(fill="both",expand=True)
            body.columnconfigure(1,weight=1); body.rowconfigure(8,weight=1)
            employees=self._active_employee_map()
            employee_var=core.tk.StringVar(value=next(iter(employees),""))
            dtype=core.tk.StringVar(value=ABSENCE_TYPES[0])
            start_var=core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            end_var=core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            notes=core.tk.StringVar()
            replace=core.tk.BooleanVar(value=False)

            core.ttk.Label(body,text="Працівник").grid(row=0,column=0,sticky="w",pady=5)
            core.ttk.Combobox(body,textvariable=employee_var,values=list(employees),state="readonly").grid(row=0,column=1,sticky="ew",pady=5)
            core.ttk.Label(body,text="Вид відсутності").grid(row=1,column=0,sticky="w",pady=5)
            core.ttk.Combobox(body,textvariable=dtype,values=ABSENCE_TYPES,state="readonly").grid(row=1,column=1,sticky="ew",pady=5)
            for row,label,var in ((2,"Період з",start_var),(3,"Період до",end_var),(4,"Примітка",notes)):
                core.ttk.Label(body,text=label).grid(row=row,column=0,sticky="w",pady=5)
                core.ttk.Entry(body,textvariable=var).grid(row=row,column=1,sticky="ew",pady=5)
                if row in (2,3): core.calendar_button(body,var).grid(row=row,column=2,sticky="w",padx=4)
            core.ttk.Checkbutton(body,text="Замінювати існуючий ручний запис, якщо в ньому немає фактичних годин",variable=replace).grid(row=5,column=0,columnspan=3,sticky="w",pady=5)
            code_label=core.tk.StringVar()
            core.ttk.Label(body,textvariable=code_label,foreground="gray").grid(row=6,column=0,columnspan=3,sticky="w",pady=(0,5))

            tree=core.ttk.Treeview(body,columns=("date","before","action"),show="headings")
            for k,l,w in (("date","Дата",100),("before","Було",520),("action","Результат",250)):
                tree.heading(k,text=l); tree.column(k,width=w,anchor="w")
            sy=core.ttk.Scrollbar(body,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=sy.set)
            tree.grid(row=8,column=0,columnspan=2,sticky="nsew"); sy.grid(row=8,column=2,sticky="ns")

            def selected_period():
                emp=employees.get(employee_var.get())
                if not emp: raise ValueError("Виберіть працівника.")
                a=datetime.strptime(start_var.get().strip(),"%d.%m.%Y").date()
                b=datetime.strptime(end_var.get().strip(),"%d.%m.%Y").date()
                if b<a: raise ValueError("Кінцева дата раніше початкової.")
                return emp,[a+timedelta(days=i) for i in range((b-a).days+1)]

            def evaluate(show_error=True):
                try: emp,dates=selected_period()
                except Exception as exc:
                    if show_error: core.messagebox.showerror("Відсутність",str(exc),parent=win)
                    return None,[]
                con=core.db(); rows=[]
                for d in dates:
                    if not core.employee_employed_on(emp,d):
                        rows.append((d,"поза періодом роботи","Пропустити")); continue
                    current=original_employee_day_time(con,emp["id"],d)
                    entry=con.execute("SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",(emp["id"],d.isoformat())).fetchone()
                    if current["actual_minutes"] not in (None,0):
                        rows.append((d,f"{current['day_type']}; факт {core.minutes_hhmm(current['actual_minutes'])}","Є факт — ручне рішення")); continue
                    if entry and not replace.get():
                        rows.append((d,f"{entry['day_type']} — {entry['notes'] or ''}","Вже є ручний запис — пропустити")); continue
                    before=f"{current['day_type']}; план {core.minutes_hhmm(current['planned_minutes'])}"
                    rows.append((d,before,"Замінити ручний запис" if entry else "Додати відсутність"))
                con.close(); return (emp,dates),rows

            def preview(_event=None):
                code,num,_=p5_code(dtype.get()); code_label.set(f"Код П-5: {code or '—'} / {num or '—'}")
                for x in tree.get_children(): tree.delete(x)
                _plan,rows=evaluate(show_error=False)
                for d,before,action in rows: tree.insert("","end",values=(d.strftime("%d.%m.%Y"),before,action))

            def apply():
                plan,rows=evaluate()
                if not plan: return
                writable=[x for x in rows if x[2] in ("Додати відсутність","Замінити ручний запис")]
                if not writable:
                    core.messagebox.showinfo("Відсутність","Немає дат для запису.",parent=win); return
                if not core.messagebox.askyesno("Відсутність",f"Записати «{dtype.get()}» на {len(writable)} дн.?",parent=win): return
                emp,_dates=plan; con=core.db(); now=datetime.now().isoformat(timespec="seconds"); added=0
                for d,_before,action in rows:
                    if action not in ("Додати відсутність","Замінити ручний запис"): continue
                    current=original_employee_day_time(con,emp["id"],d)
                    if current["actual_minutes"] not in (None,0): continue
                    entry=con.execute("SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",(emp["id"],d.isoformat())).fetchone()
                    if entry and not replace.get(): continue
                    note_text=notes.get().strip()
                    con.execute("""INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at,updated_at)
                                   VALUES(?,?,?,0,0,?,?,?)
                                   ON CONFLICT(employee_id,work_date) DO UPDATE SET
                                     day_type=excluded.day_type,planned_hours=0,actual_hours=0,
                                     notes=excluded.notes,updated_at=excluded.updated_at""",
                                (emp["id"],d.isoformat(),dtype.get(),note_text,now,now))
                    added+=1
                con.commit(); con.close(); preview()
                core.messagebox.showinfo("Відсутність",f"Записано днів: {added}. Робочі графіки фізично не видалялися.",parent=win)

            btn=core.ttk.Frame(body); btn.grid(row=7,column=0,columnspan=3,sticky="ew",pady=5)
            core.ttk.Button(btn,text="Переглянути",command=preview).pack(side="left",padx=3)
            core.ttk.Button(btn,text="Застосувати",command=apply).pack(side="left",padx=3)
            dtype.trace_add("write",lambda *_args:preview())
            preview()

        def _duty_staff_for_interval(self, start_dt, end_dt, location="", con=None):
            """Лікар/механік для шляхівки з урахуванням табельної відсутності."""
            own = con is None
            if own:
                con = core.db()
            from_date=(start_dt.date()-timedelta(days=7)).isoformat()
            rows=con.execute(
                """SELECT sh.*,e.last_name||' '||e.first_name||
                          CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name
                   FROM employee_shifts sh
                   JOIN employees e ON e.id=sh.employee_id
                   WHERE sh.work_date BETWEEN ? AND ? AND e.active=1
                     AND sh.role IN ('Лікар','Механік')
                   ORDER BY sh.work_date,sh.start_time""",
                (from_date,end_dt.date().isoformat()),
            ).fetchall()
            result={"doctor_1":"","doctor_2":"","mechanic_1":"","mechanic_2":""}
            ranked=[]
            for row in rows:
                base=datetime.strptime(row["work_date"],"%Y-%m-%d")
                row_start=base+timedelta(minutes=parse_clock(row["start_time"]))
                row_end=base+timedelta(days=int(row["end_day_offset"] or 0),minutes=parse_clock(row["end_time"]))
                if row_end <= start_dt or row_start >= end_dt:
                    continue
                # Any absence day touched by the staffing interval suppresses
                # this assignment operationally, while the historical shift remains.
                cursor=row_start.date()
                unavailable=False
                while cursor <= row_end.date():
                    entry=con.execute(
                        "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (row["employee_id"],cursor.isoformat()),
                    ).fetchone()
                    if entry and str(entry["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
                        unavailable=True
                        break
                    cursor += timedelta(days=1)
                if unavailable:
                    continue
                exact_location=1 if location and (row["location"] or "").strip().casefold()==location.strip().casefold() else 0
                ranked.append((exact_location,row_start,row))
            if own:
                con.close()
            for _match,_start,row in sorted(ranked,key=lambda x:(x[0],x[1]),reverse=True):
                prefix="doctor" if row["role"]=="Лікар" else "mechanic"
                key=f"{prefix}_{row['shift_no']}"
                if not result[key]:
                    result[key]=row["full_name"]
            return result

        def _save_p5(self, kind):
            try:
                month=int(self.personnel_report_month.get()); year=int(self.personnel_report_year.get())
                if not 1<=month<=12: raise ValueError
            except Exception:
                core.messagebox.showerror("Табель П-5","Перевірте місяць і рік.",parent=self); return
            suffix=".xlsx" if kind=="xlsx" else ".pdf"
            filename=f"Табель_П5_{year}_{month:02d}{suffix}"
            path=core.filedialog.asksaveasfilename(
                parent=self,title="Зберегти табель П-5",initialdir=str(core.OUTPUT_DIR),
                initialfile=filename,defaultextension=suffix,
                filetypes=[("Excel","*.xlsx")] if kind=="xlsx" else [("PDF","*.pdf")],
            )
            if not path: return
            writer=(lambda out:export_p5_xlsx(core,year,month,out,self.personnel_report_active.get())) if kind=="xlsx" else (lambda out:export_p5_pdf(core,year,month,out,self.personnel_report_active.get()))
            actual=core.write_output_file(writer,path,parent=self,kind="Excel табеля П-5" if kind=="xlsx" else "PDF табеля П-5",error_title="Табель П-5")
            if actual is not None:
                core.messagebox.showinfo("Табель П-5",f"Файл створено:\n{actual}",parent=self)

    PersonnelApp.__name__="App"
    PersonnelApp.__qualname__="App"
    core.App=PersonnelApp
    core._TAXO_PERSONNEL_R3_INSTALLED=True
    return PersonnelApp
