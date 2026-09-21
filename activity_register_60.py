# -*- coding: utf-8 -*-
"""Taxo v8.70 r11 — 60-day minute-by-minute driver activity register.

The report intentionally separates recorded facts from calculated coverage.
Every minute in the requested 60 calendar days is represented. Missing source
information is rendered as ``Невизначено`` instead of being silently converted
to rest.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path
import os

PERIOD_DAYS = 60
MINUTES_PER_DAY = 24 * 60
RAW_REST = "__ТАХО_ВІДПОЧИНОК__"

SUMMARY_KEYS = (
    "Керування",
    "Інша робота",
    "Готовність",
    "Перерва",
    "Відпочинок",
    "Відсутність",
    "Невизначено",
)


def hhmm_minutes(minutes):
    value = max(0, int(minutes or 0))
    return f"{value // 60:02d}:{value % 60:02d}"


def parse_clock(value):
    raw = (value or "").strip()
    if not raw:
        return None
    parts = raw.split(":")
    if len(parts) != 2:
        return None
    try:
        hh = int(parts[0]); mm = int(parts[1])
    except ValueError:
        return None
    if hh == 24 and mm == 0:
        return 1440
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        return None
    return hh * 60 + mm


def span_datetimes(base_day, start_value, end_value):
    """Return a minute-aligned half-open [start,end) span, including midnight wrap."""
    sm = parse_clock(start_value); em = parse_clock(end_value)
    if sm is None or em is None:
        return None
    s_day = base_day + timedelta(days=1 if sm == 1440 else 0)
    e_day = base_day + timedelta(days=1 if em == 1440 else 0)
    sm %= 1440; em %= 1440
    start_dt = datetime.combine(s_day, time(sm // 60, sm % 60))
    end_dt = datetime.combine(e_day, time(em // 60, em % 60))
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt, end_dt


def new_grid(start_day, end_day):
    grid = {}
    current = start_day
    while current <= end_day:
        grid[current] = [None] * MINUTES_PER_DAY
        current += timedelta(days=1)
    return grid


def _cell(activity, source, priority, note="", vehicle=""):
    return {
        "activity": activity,
        "source": source,
        "priority": int(priority),
        "note": (note or "").strip(),
        "vehicle": (vehicle or "").strip(),
    }


def assign_minute(cells, minute, activity, source, priority, note="", vehicle=""):
    if not (0 <= minute < MINUTES_PER_DAY):
        return
    existing = cells[minute]
    if existing is None or int(priority) >= int(existing.get("priority", 0)):
        cells[minute] = _cell(activity, source, priority, note, vehicle)


def assign_span(grid, start_dt, end_dt, activity, source, priority, note="", vehicle=""):
    """Assign an activity to every covered minute, clipped to the report grid."""
    if end_dt <= start_dt:
        return
    for day, cells in grid.items():
        day_start = datetime.combine(day, time.min)
        day_end = day_start + timedelta(days=1)
        left = max(start_dt, day_start)
        right = min(end_dt, day_end)
        if right <= left:
            continue
        first = max(0, int((left - day_start).total_seconds() // 60))
        last = min(1440, int((right - day_start).total_seconds() // 60))
        for minute in range(first, last):
            assign_minute(cells, minute, activity, source, priority, note, vehicle)


def vehicle_label(row):
    if row is None:
        return ""
    name = (row["name"] or "").strip() if "name" in row.keys() else ""
    plate = (row["plate"] or "").strip() if "plate" in row.keys() else ""
    model = (row["make_model"] or "").strip() if "make_model" in row.keys() else ""
    primary = " — ".join(x for x in (name, plate) if x)
    return primary or model


def _activity_from_day_type(day_type):
    value = (day_type or "").strip()
    if value in ("Вихідний", "Відпочинок"):
        return "Відпочинок"
    if value in ("Відпустка", "Лікарняний"):
        return "Відсутність"
    if value == "Доступний":
        return "Готовність"
    if value == "Інша робота":
        return "Інша робота"
    return None


def _activity_from_segment(activity_type):
    value = (activity_type or "").strip().lower()
    if "керув" in value:
        return "Керування"
    if "доступ" in value or "готов" in value:
        return "Готовність"
    if "відпоч" in value or "вихід" in value:
        return "Відпочинок"
    if "відпуст" in value or "лікар" in value:
        return "Відсутність"
    return "Інша робота"


def _activity_from_attestation(activity_no):
    return {
        14: "Відсутність",
        15: "Відсутність",
        16: "Відпочинок",
        17: "Керування",
        18: "Інша робота",
        19: "Готовність",
    }.get(int(activity_no or 0), "Невизначено")


def _tacho_activity(value):
    raw = (value or "").strip().lower()
    if "керув" in raw:
        return "Керування"
    if "інша" in raw or "робот" in raw:
        return "Інша робота"
    if "готов" in raw or "доступ" in raw:
        return "Готовність"
    if "відпоч" in raw:
        return RAW_REST
    return "Невизначено"


def apply_main_database(core, grid, driver_id, start_day, end_day):
    """Overlay worklog, work segments and activity attestations."""
    con = core.db()
    day_types = {}
    warnings = {d: [] for d in grid}
    try:
        vehicles = {r["id"]: vehicle_label(r) for r in con.execute("SELECT * FROM vehicles").fetchall()}
        query_start = (start_day - timedelta(days=1)).isoformat()
        rows = con.execute(
            "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date",
            (driver_id, query_start, end_day.isoformat()),
        ).fetchall()
        ids = [r["id"] for r in rows]
        segments = {}
        if ids:
            marks = ",".join("?" for _ in ids)
            for s in con.execute(
                f"SELECT * FROM work_segments WHERE worklog_id IN ({marks}) ORDER BY worklog_id,segment_no",
                ids,
            ).fetchall():
                segments.setdefault(s["worklog_id"], []).append(s)

        for row in rows:
            base_day = date.fromisoformat(row["work_date"])
            if base_day in grid:
                day_types[base_day] = (row["day_type"] or "").strip()
                day_activity = _activity_from_day_type(row["day_type"])
                if day_activity:
                    assign_span(
                        grid,
                        datetime.combine(base_day, time.min),
                        datetime.combine(base_day + timedelta(days=1), time.min),
                        day_activity,
                        f"Табель: {row['day_type']}",
                        25,
                        row["notes"] or "",
                        row["vehicle"] or "",
                    )

            row_segments = segments.get(row["id"], [])
            source_items = row_segments or [row]
            any_timed = False
            vlabel = (row["vehicle"] or "").strip()
            if not vlabel and "vehicle_id" in row.keys() and row["vehicle_id"]:
                vlabel = vehicles.get(row["vehicle_id"], "")

            for item in source_items:
                activity_type = item["activity_type"] if "activity_type" in item.keys() else row["day_type"]
                drive_start = item["start_time"] if "start_time" in item.keys() else row["start_time"]
                drive_end = item["end_time"] if "end_time" in item.keys() else row["end_time"]
                note = item["note"] if "note" in item.keys() else row["notes"]

                # 10.3-r2: plan is the default fact, but sparse fact_* overrides
                # take precedence in factual registers. For split shifts the
                # outer factual boundary clips/extends only the edge parts.
                if row_segments:
                    work_spans = core._worklog_effective_work_intervals(row, row_segments)
                    # Apply them once per worklog, not once per segment.
                    if item is source_items[0]:
                        for begin, finish in work_spans:
                            any_timed = True
                            assign_span(
                                grid, begin, finish,
                                _activity_from_segment(activity_type),
                                "Факт роботи" if core._worklog_has_fact_override(row)
                                else "Табель / план = факт",
                                65 if core._worklog_has_fact_override(row) else 60,
                                note, vlabel,
                            )
                else:
                    work_spans = core._worklog_effective_work_intervals(row, [])
                    for begin, finish in work_spans:
                        any_timed = True
                        assign_span(
                            grid, begin, finish,
                            _activity_from_segment(activity_type),
                            "Факт роботи" if core._worklog_has_fact_override(row)
                            else "Табель / план = факт",
                            65 if core._worklog_has_fact_override(row) else 60,
                            note, vlabel,
                        )
                drive_span = span_datetimes(base_day, drive_start, drive_end)
                if drive_span:
                    any_timed = True
                    assign_span(
                        grid, drive_span[0], drive_span[1],
                        "Керування", "Табель / межі керування", 70, note, vlabel,
                    )

            if base_day in warnings and (row["day_type"] or "") == "Робота" and not any_timed:
                hours = float(row["work_hours"] or 0)
                if hours > 0:
                    warnings[base_day].append(
                        f"У табелі є {hours:g} год роботи, але немає часових меж — хвилини не можна розмістити точно."
                    )

        # Confirmation-of-activities forms are exact dated intervals and are useful
        # for filling periods without a tachograph chart.
        atts = con.execute(
            "SELECT * FROM attestations WHERE driver_id=? AND COALESCE(status,'active')='active' ORDER BY id",
            (driver_id,),
        ).fetchall()
        for row in atts:
            begin = core.parse_attestation_period(row["period_from"])
            finish = core.parse_attestation_period(row["period_to"])
            if begin is None or finish is None or finish <= begin:
                continue
            activity = _activity_from_attestation(row["activity_no"])
            label = core.ACTIVITIES.get(int(row["activity_no"]), f"№{row['activity_no']}") if hasattr(core, "ACTIVITIES") else f"№{row['activity_no']}"
            assign_span(
                grid, begin, finish, activity,
                f"Бланк підтвердження №{row['activity_no']}: {label}",
                50,
            )
    finally:
        con.close()
    return day_types, warnings


def apply_tachograph_database(core, grid, driver_id, start_day, end_day):
    """Overlay tachograph intervals. Manual operator confirmation has top priority."""
    try:
        import tachograph
    except Exception:
        return
    try:
        tachograph.configure_workspace(core.DATA_ROOT)
        con = tachograph.tdb()
    except Exception:
        return

    main_con = core.db()
    try:
        vehicles = {r["id"]: vehicle_label(r) for r in main_con.execute("SELECT * FROM vehicles").fetchall()}
    finally:
        main_con.close()

    try:
        discs = con.execute(
            "SELECT * FROM discs WHERE driver_id=? AND disc_date BETWEEN ? AND ? ORDER BY disc_date,id",
            (driver_id, (start_day - timedelta(days=1)).isoformat(), end_day.isoformat()),
        ).fetchall()
        for disc in discs:
            try:
                base_day = date.fromisoformat((disc["disc_date"] or "").strip())
            except ValueError:
                continue
            rows = con.execute(
                "SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min,id", (disc["id"],)
            ).fetchall()
            for row in rows:
                start_min = int(row["start_min"] or 0) % 1440
                end_min = int(row["end_min"] or 0) % 1440
                if start_min == end_min:
                    continue
                begin = datetime.combine(base_day, time(start_min // 60, start_min % 60))
                finish_day = base_day + timedelta(days=1 if end_min <= start_min else 0)
                finish = datetime.combine(finish_day, time(end_min // 60, end_min % 60))
                source_mode = (row["source"] or "auto").strip().lower()
                manual = source_mode == "manual"
                source = "ТАХО — підтверджено вручну" if manual else "ТАХО — авто-кандидат"
                scan = (disc["scan_name"] or "").strip()
                if scan:
                    source += f" ({scan})"
                vlabel = vehicles.get(disc["vehicle_id"], "") if disc["vehicle_id"] else ""
                assign_span(
                    grid, begin, finish, _tacho_activity(row["activity"]), source,
                    100 if manual else 80,
                    row["note"] or "", vlabel,
                )
    finally:
        con.close()


def classify_and_fill(grid):
    """Make every day a full 24 h timeline without hiding data quality.

    - explicit tachograph rest inside the day's active envelope becomes a break;
    - explicit tachograph rest outside the envelope remains rest;
    - uncovered minutes inside an observed work envelope become a calculated break;
    - uncovered minutes outside an observed work envelope become calculated rest;
    - a day with no observed activity remains undefined unless another explicit
      source (day type / attestation) already covers it.
    """
    active_names = {"Керування", "Інша робота", "Готовність"}
    for _day, cells in grid.items():
        active = [i for i, cell in enumerate(cells) if cell and cell["activity"] in active_names]
        first = active[0] if active else None
        last = active[-1] if active else None

        for minute, cell in enumerate(cells):
            if cell and cell["activity"] == RAW_REST:
                inside = first is not None and first <= minute <= last
                cell = dict(cell)
                cell["activity"] = "Перерва" if inside else "Відпочинок"
                suffix = "роль у межах зміни визначено розрахунково"
                cell["note"] = "; ".join(x for x in (cell.get("note", ""), suffix) if x)
                cells[minute] = cell

        if first is not None:
            for minute in range(MINUTES_PER_DAY):
                if cells[minute] is not None:
                    continue
                if first <= minute <= last:
                    cells[minute] = _cell(
                        "Перерва", "Розраховано з меж активності", 10,
                        "Проміжок між зафіксованими активностями",
                    )
                else:
                    cells[minute] = _cell(
                        "Відпочинок", "Розраховано поза межами активності", 10,
                        "Поза першою/останньою зафіксованою активністю дня",
                    )

        for minute in range(MINUTES_PER_DAY):
            if cells[minute] is None:
                cells[minute] = _cell("Невизначено", "Немає достатніх даних", 0)


def compress_day(cells):
    rows = []
    start = 0
    current = cells[0]

    def key(cell):
        return (
            cell.get("activity", "Невизначено"),
            cell.get("source", ""),
            cell.get("vehicle", ""),
            cell.get("note", ""),
        )

    current_key = key(current)
    for minute in range(1, MINUTES_PER_DAY + 1):
        next_key = key(cells[minute]) if minute < MINUTES_PER_DAY else None
        if next_key == current_key:
            continue
        rows.append({
            "start_min": start,
            "end_min": minute,
            "duration_min": minute - start,
            "activity": current["activity"],
            "source": current.get("source", ""),
            "vehicle": current.get("vehicle", ""),
            "note": current.get("note", ""),
        })
        if minute < MINUTES_PER_DAY:
            start = minute
            current = cells[minute]
            current_key = next_key
    return rows


def summarize_day(cells):
    totals = {name: 0 for name in SUMMARY_KEYS}
    for cell in cells:
        name = cell.get("activity", "Невизначено")
        if name not in totals:
            name = "Невизначено"
        totals[name] += 1
    totals["Відомо"] = MINUTES_PER_DAY - totals["Невизначено"]
    totals["Покриття"] = 100.0 * totals["Відомо"] / MINUTES_PER_DAY
    return totals


def collect_activity_register(core, driver_id, end_day, period_days=PERIOD_DAYS):
    end_day = end_day if isinstance(end_day, date) else date.fromisoformat(str(end_day))
    start_day = end_day - timedelta(days=int(period_days) - 1)
    grid = new_grid(start_day, end_day)
    day_types, warnings = apply_main_database(core, grid, int(driver_id), start_day, end_day)
    apply_tachograph_database(core, grid, int(driver_id), start_day, end_day)
    classify_and_fill(grid)

    con = core.db()
    try:
        driver = con.execute("SELECT * FROM drivers WHERE id=?", (int(driver_id),)).fetchone()
    finally:
        con.close()
    if driver is None:
        raise ValueError("Водія не знайдено")
    driver_name = " ".join(
        x for x in (driver["last_name"], driver["first_name"], driver["middle_name"]) if (x or "").strip()
    )

    days = []
    current = start_day
    overall = {name: 0 for name in SUMMARY_KEYS}
    while current <= end_day:
        summary = summarize_day(grid[current])
        for name in SUMMARY_KEYS:
            overall[name] += summary[name]
        days.append({
            "date": current,
            "day_type": day_types.get(current, ""),
            "summary": summary,
            "intervals": compress_day(grid[current]),
            "warnings": warnings.get(current, []),
        })
        current += timedelta(days=1)

    return {
        "driver_id": int(driver_id),
        "driver_name": driver_name,
        "start_day": start_day,
        "end_day": end_day,
        "period_days": int(period_days),
        "days": days,
        "overall": overall,
        "generated_at": datetime.now(),
    }


def _clock_label(minute):
    minute = int(minute)
    if minute >= 1440:
        return "24:00"
    return f"{minute // 60:02d}:{minute % 60:02d}"


def export_activity_register_pdf(core, data, out_path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from xml.sax.saxutils import escape

    font_name = "Helvetica"
    font_path = next((p for p in core.report_font_candidates() if os.path.exists(p)), None)
    if font_path:
        try:
            if "Activity60Font" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("Activity60Font", font_path))
            font_name = "Activity60Font"
        except Exception:
            pass

    page_size = landscape(A4)
    doc = SimpleDocTemplate(
        str(out_path), pagesize=page_size,
        leftMargin=22, rightMargin=22, topMargin=25, bottomMargin=26,
        title="60-денний реєстр діяльності водія",
    )
    title = ParagraphStyle("activity-title", fontName=font_name, fontSize=14, leading=17, alignment=TA_CENTER, spaceAfter=7)
    h2 = ParagraphStyle("activity-h2", fontName=font_name, fontSize=9.5, leading=12, spaceBefore=6, spaceAfter=4)
    body = ParagraphStyle("activity-body", fontName=font_name, fontSize=7.5, leading=9.5, alignment=TA_LEFT)
    tiny = ParagraphStyle("activity-tiny", fontName=font_name, fontSize=6.4, leading=7.6, alignment=TA_LEFT)

    story = [
        Paragraph("РЕЄСТР ДІЯЛЬНОСТІ ВОДІЯ З ПОХВИЛИННИМ ПОКРИТТЯМ", title),
        Paragraph(
            f"Водій: <b>{escape(data['driver_name'])}</b> &nbsp;&nbsp;&nbsp; "
            f"Період: <b>{data['start_day'].strftime('%d.%m.%Y')}–{data['end_day'].strftime('%d.%m.%Y')}</b> "
            f"({data['period_days']} календарних днів)", body,
        ),
        Spacer(1, 4),
        Paragraph(
            "Документ показує суцільну 24-годинну шкалу кожної доби. Джерело вказується для кожного інтервалу. "
            "«Розраховано» означає похідну класифікацію між/поза зафіксованими активностями; "
            "«Невизначено» означає, що наявних даних недостатньо для достовірного визначення діяльності.",
            body,
        ),
        Spacer(1, 7),
        Paragraph("Зведений табель за 60 днів", h2),
    ]

    summary_header = ["Дата", "Вид дня", "Керув.", "Інша роб.", "Готовн.", "Перерва", "Відпоч.", "Відсутн.", "Невизн.", "Покриття"]
    summary_rows = [summary_header]
    for day in data["days"]:
        s = day["summary"]
        summary_rows.append([
            day["date"].strftime("%d.%m.%Y"), day["day_type"],
            hhmm_minutes(s["Керування"]), hhmm_minutes(s["Інша робота"]),
            hhmm_minutes(s["Готовність"]), hhmm_minutes(s["Перерва"]),
            hhmm_minutes(s["Відпочинок"]), hhmm_minutes(s["Відсутність"]),
            hhmm_minutes(s["Невизначено"]), f"{s['Покриття']:.0f}%",
        ])
    summary_table = Table(summary_rows, repeatRows=1, colWidths=[52, 66, 42, 47, 43, 45, 45, 47, 45, 43])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,0), 6.7),
        ("FONTSIZE", (0,1), (-1,-1), 6.2),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9e2f3")),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#777777")),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))
    story.append(summary_table)
    story.append(PageBreak())
    story.append(Paragraph("Детальний журнал інтервалів", title))

    for day in data["days"]:
        s = day["summary"]
        warning = ""
        if day["warnings"]:
            warning = " &nbsp; <b>Увага:</b> " + escape("; ".join(day["warnings"]))
        story.append(Paragraph(
            f"<b>{day['date'].strftime('%d.%m.%Y')}</b> — "
            f"керування {hhmm_minutes(s['Керування'])}, інша робота {hhmm_minutes(s['Інша робота'])}, "
            f"готовність {hhmm_minutes(s['Готовність'])}, перерви {hhmm_minutes(s['Перерва'])}, "
            f"відпочинок {hhmm_minutes(s['Відпочинок'])}, невизначено {hhmm_minutes(s['Невизначено'])}. "
            f"Контроль доби: <b>24:00</b>.{warning}", h2,
        ))

        rows = [["Від", "До", "Трив.", "Активність", "Джерело", "ТЗ", "Примітка"]]
        for item in day["intervals"]:
            rows.append([
                _clock_label(item["start_min"]), _clock_label(item["end_min"]),
                hhmm_minutes(item["duration_min"]), item["activity"],
                Paragraph(escape(item["source"]), tiny),
                Paragraph(escape(item["vehicle"]), tiny),
                Paragraph(escape(item["note"]), tiny),
            ])
        table = Table(rows, repeatRows=1, colWidths=[34,34,38,72,180,85,235])
        table_style = [
            ("FONTNAME", (0,0), (-1,-1), font_name),
            ("FONTSIZE", (0,0), (3,-1), 6.5),
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9e2f3")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#888888")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ALIGN", (0,1), (2,-1), "CENTER"),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ]
        for row_index, item in enumerate(day["intervals"], start=1):
            if item["activity"] == "Невизначено":
                table_style.append(("BACKGROUND", (0,row_index), (-1,row_index), colors.HexColor("#fce8e6")))
            elif item["source"].startswith("Розраховано"):
                table_style.append(("BACKGROUND", (0,row_index), (-1,row_index), colors.HexColor("#fff7d6")))
        table.setStyle(TableStyle(table_style))
        story.append(table)
        story.append(Spacer(1, 7))

    def footer(canvas, _doc):
        canvas.saveState()
        try:
            canvas.setFont(font_name, 6.5)
        except Exception:
            canvas.setFont("Helvetica", 6.5)
        canvas.drawString(22, 12, f"Taxo — реєстр діяльності, сформовано {data['generated_at'].strftime('%d.%m.%Y %H:%M')}")
        canvas.drawRightString(page_size[0] - 22, 12, f"Сторінка {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def default_output_path(core, data):
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in data["driver_name"]).strip().replace(" ", "_")
    name = (
        f"Реєстр_діяльності_60днів_{safe}_"
        f"{data['start_day'].strftime('%Y-%m-%d')}_{data['end_day'].strftime('%Y-%m-%d')}.pdf"
    )
    return Path(core.OUTPUT_DIR) / "ActivityRegisters" / name


def _walk_widgets(root):
    for child in root.winfo_children():
        yield child
        yield from _walk_widgets(child)


def install(core, base_app):
    """Extend the r10 App with the standalone 60-day activity document."""
    if getattr(core, "_ACTIVITY_REGISTER_R11_INSTALLED", False):
        return core.App

    class ExtendedActivityApp(base_app):
        def build_work(self):
            result = super().build_work()
            target_bar = None
            for widget in _walk_widgets(self.tab_work):
                try:
                    if isinstance(widget, core.ttk.Button) and widget.cget("text") == "Підсумки / контроль":
                        target_bar = widget.master
                        break
                except Exception:
                    continue
            if target_bar is not None:
                exists = False
                for child in target_bar.winfo_children():
                    try:
                        exists = exists or child.cget("text") == "Реєстр 60 днів"
                    except Exception:
                        pass
                if not exists:
                    core.ttk.Button(
                        target_bar,
                        text="Реєстр 60 днів",
                        command=self.show_activity_register_60,
                    ).pack(side="left", padx=4)
            return result

        def show_activity_register_60(self):
            if not getattr(self, "driver_id", None):
                core.messagebox.showwarning("Реєстр 60 днів", "Спочатку виберіть водія.", parent=self)
                return

            win = core.tk.Toplevel(self)
            win.title("Реєстр діяльності водія за 60 днів")
            win.resizable(False, False)
            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)
            core.ttk.Label(
                body,
                text="Окремий PDF: 60 календарних днів, 24:00 кожної доби, інтервали з точністю до хвилини.",
                wraplength=560,
                justify="left",
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))

            end_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            period_var = core.tk.StringVar()
            core.ttk.Label(body, text="Кінцева дата").grid(row=1, column=0, sticky="w", pady=5)
            core.ttk.Entry(body, textvariable=end_var, width=16).grid(row=1, column=1, sticky="w", padx=6)
            if hasattr(core, "calendar_button"):
                core.calendar_button(body, end_var).grid(row=1, column=2, sticky="w")
            core.ttk.Label(body, textvariable=period_var, foreground="gray").grid(row=2, column=0, columnspan=3, sticky="w", pady=(0,10))

            def resolve_period(show_error=False):
                try:
                    end_day = datetime.strptime(end_var.get().strip(), "%d.%m.%Y").date()
                except ValueError:
                    if show_error:
                        core.messagebox.showerror("Дата", "Вкажіть кінцеву дату у форматі ДД.ММ.РРРР.", parent=win)
                    return None
                start_day = end_day - timedelta(days=PERIOD_DAYS - 1)
                period_var.set(f"Період: {start_day.strftime('%d.%m.%Y')}–{end_day.strftime('%d.%m.%Y')} ({PERIOD_DAYS} днів)")
                return end_day

            def generate(open_after=True):
                end_day = resolve_period(show_error=True)
                if end_day is None:
                    return
                try:
                    data = collect_activity_register(core, self.driver_id, end_day, PERIOD_DAYS)
                except Exception as exc:
                    core._append_error_log("60-денний реєстр діяльності", exc)
                    core.messagebox.showerror("Реєстр 60 днів", f"Не вдалося зібрати дані:\n{exc}", parent=win)
                    return
                target = default_output_path(core, data)
                actual = core.write_output_file(
                    lambda out: export_activity_register_pdf(core, data, out),
                    target,
                    parent=win,
                    kind="PDF реєстру діяльності",
                    error_title="Помилка PDF",
                )
                if actual is not None:
                    if open_after:
                        core.open_document(win, actual, external_opener=core.open_external)
                    else:
                        core.messagebox.showinfo("Реєстр 60 днів", f"PDF створено:\n{actual}", parent=win)

            end_var.trace_add("write", lambda *_: resolve_period(False))
            resolve_period(False)
            buttons = core.ttk.Frame(body)
            buttons.grid(row=3, column=0, columnspan=3, sticky="e", pady=(6,0))
            core.ttk.Button(buttons, text="Зберегти PDF", command=lambda: generate(False)).pack(side="left", padx=4)
            core.ttk.Button(buttons, text="Сформувати й відкрити PDF", command=lambda: generate(True)).pack(side="left", padx=4)
            core.ttk.Button(buttons, text="Закрити", command=win.destroy).pack(side="left", padx=(12,0))
            try:
                win.transient(self); win.grab_set()
            except Exception:
                pass

    ExtendedActivityApp.__name__ = "App"
    ExtendedActivityApp.__qualname__ = "App"
    core.App = ExtendedActivityApp
    core._ACTIVITY_REGISTER_R11_INSTALLED = True
    return ExtendedActivityApp
