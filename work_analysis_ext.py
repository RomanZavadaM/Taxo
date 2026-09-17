# -*- coding: utf-8 -*-
"""Taxo v8.70 r10 — additions to the single-driver work-time analysis.

This module keeps the large historical ``main.py`` stable while extending its
public analysis screen with:
- one-click generation/opening of the current №340 PDF protocol;
- an hourly per-driver weekly balance alongside the existing 60 h work-time
  and 56 h driving checks.
"""
from datetime import date, timedelta
from pathlib import Path

WORK_WEEK_LIMIT_MIN = 60 * 60
DRIVING_WEEK_LIMIT_MIN = 56 * 60


def signed_minutes_hhmm(value):
    """Format a signed minute balance as +HH:MM / -HH:MM."""
    minutes = int(round(value or 0))
    sign = "+" if minutes >= 0 else "-"
    minutes = abs(minutes)
    return f"{sign}{minutes // 60:02d}:{minutes % 60:02d}"


def week_balance_rows_from_totals(week_totals):
    """Convert {monday: {work, drive}} totals to user-facing balance rows."""
    rows = []
    for monday in sorted(week_totals):
        values = week_totals[monday]
        work_min = int(round(values.get("work", 0) or 0))
        drive_min = int(round(values.get("drive", 0) or 0))
        rows.append({
            "start": monday,
            "end": monday + timedelta(days=6),
            "work_min": work_min,
            "work_limit_min": WORK_WEEK_LIMIT_MIN,
            "work_balance_min": WORK_WEEK_LIMIT_MIN - work_min,
            "drive_min": drive_min,
            "drive_limit_min": DRIVING_WEEK_LIMIT_MIN,
            "drive_balance_min": DRIVING_WEEK_LIMIT_MIN - drive_min,
        })
    return rows


def collect_week_balances(app, core):
    """Rebuild exact weekly work/driving totals for the currently selected driver."""
    if not getattr(app, "driver_id", None):
        return []

    year = int(app.year_var.get())
    month = int(app.month_var.get())
    month_start = date(year, month, 1)
    month_end = core.month_dates(year, month)[-1]
    range_start = month_start - timedelta(days=month_start.weekday())
    range_end = month_end + timedelta(days=6 - month_end.weekday())

    con = core.db()
    try:
        rows = con.execute(
            "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date",
            (app.driver_id, range_start.isoformat(), range_end.isoformat()),
        ).fetchall()
        seg_map = app._analysis_segments_map(con, rows)
        week_totals = {}
        for row in rows:
            work_date = date.fromisoformat(row["work_date"])
            work_min, drive_min, _ = app._row_minutes_exact(row, seg_map.get(row["id"], []))
            monday = work_date - timedelta(days=work_date.weekday())
            total = week_totals.setdefault(monday, {"work": 0, "drive": 0})
            total["work"] += work_min
            total["drive"] += drive_min
    finally:
        con.close()

    # Show every calendar week intersecting the selected month, including zero rows.
    monday = range_start
    while monday <= range_end:
        week_totals.setdefault(monday, {"work": 0, "drive": 0})
        monday += timedelta(days=7)
    return week_balance_rows_from_totals(week_totals)


def weekly_balance_report_items(data, minutes_hhmm):
    """Structured report section shared by the on-screen protocol and its PDF."""
    balances = data.get("week_balances") or []
    items = [
        ("heading", "ТИЖНЕВИЙ ПОГОДИННИЙ БАЛАНС — 60:00 РОБОТА / 56:00 КЕРУВАННЯ"),
        (
            "note",
            "56:00 — це тижневий ліміт саме КЕРУВАННЯ. Загальний робочий час "
            "показується окремо з балансом до 60:00; середня норма 48:00/тиждень "
            "за 4 календарні місяці контролюється окремим показником.",
        ),
    ]
    if not balances:
        items.append(("note", "• Немає даних для тижневого погодинного балансу."))
        return items

    for row in balances:
        over = row["work_balance_min"] < 0 or row["drive_balance_min"] < 0
        kind = "error" if over else "ok"
        items.append((
            kind,
            f"• {row['start'].strftime('%d.%m.%Y')}–{row['end'].strftime('%d.%m.%Y')}: "
            f"робота {minutes_hhmm(row['work_min'])}, баланс до 60:00 "
            f"{signed_minutes_hhmm(row['work_balance_min'])}; "
            f"керування {minutes_hhmm(row['drive_min'])}, баланс до 56:00 "
            f"{signed_minutes_hhmm(row['drive_balance_min'])}.",
        ))
    return items


def extend_report_items(original_items, data, minutes_hhmm):
    """Insert the weekly balance before the detailed driving-break section."""
    section = weekly_balance_report_items(data, minutes_hhmm)
    insert_at = next(
        (
            index
            for index, item in enumerate(original_items)
            if item[0] == "heading" and item[1].startswith("ПЕРЕРВИ У КЕРУВАННІ")
        ),
        len(original_items),
    )
    return original_items[:insert_at] + section + original_items[insert_at:]


def analysis_pdf_default_path(output_dir, driver_name, data):
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in (driver_name or "Водій"))
    safe = safe.strip().replace(" ", "_") or "Водій"
    return Path(output_dir) / f"Аналіз_340_{safe}_{data['year']}_{data['month']:02d}.pdf"


def install(core):
    """Install r10 behavior into the imported main module and return the App class."""
    if getattr(core, "_WORK_ANALYSIS_R10_INSTALLED", False):
        return core.App

    base_app = core.App
    original_report_builder = core.build_work_analysis_report_items

    def extended_report_builder(data):
        return extend_report_items(
            original_report_builder(data), data, core.minutes_hhmm
        )

    core.build_work_analysis_report_items = extended_report_builder

    class ExtendedApp(base_app):
        def calculate_work_analysis(self):
            data = super().calculate_work_analysis()
            if data is not None:
                data["week_balances"] = collect_week_balances(self, core)
            return data

        def open_current_work_analysis_pdf(self):
            data = self.calculate_work_analysis()
            if data is None:
                core.messagebox.showwarning(
                    "Підсумки", "Спочатку виберіть водія.", parent=self
                )
                return

            driver = self.driver_by_id(self.driver_id)
            driver_name = self.driver_full_name(driver) if driver else self.work_driver_var.get()
            target = analysis_pdf_default_path(core.OUTPUT_DIR, driver_name, data)
            actual = core.write_output_file(
                lambda out: core.export_work_analysis_pdf(data, driver_name, out),
                target,
                parent=getattr(self, "_work_analysis_r10_win", self),
                kind="PDF аналізу №340",
                error_title="Помилка PDF",
            )
            if actual is not None:
                core.open_external(actual)

        def show_work_analysis(self):
            before = {str(widget) for widget in self.winfo_children()}
            result = super().show_work_analysis()

            created = [
                widget
                for widget in self.winfo_children()
                if str(widget) not in before and isinstance(widget, core.tk.Toplevel)
            ]
            analysis_win = next(
                (
                    widget
                    for widget in created
                    if widget.winfo_exists() and widget.title() == "Підсумки та контроль №340"
                ),
                None,
            )
            if analysis_win is None:
                return result

            self._work_analysis_r10_win = analysis_win
            head = next(
                (widget for widget in analysis_win.winfo_children() if isinstance(widget, core.ttk.Frame)),
                None,
            )
            title_frame = next(
                (widget for widget in head.winfo_children() if isinstance(widget, core.ttk.Frame)),
                None,
            ) if head is not None else None
            if title_frame is not None:
                core.ttk.Button(
                    title_frame,
                    text="Відкрити PDF",
                    command=self.open_current_work_analysis_pdf,
                ).pack(side="right", padx=(8, 0))
            return result

    ExtendedApp.__name__ = "App"
    ExtendedApp.__qualname__ = "App"
    core.App = ExtendedApp
    core._WORK_ANALYSIS_R10_INSTALLED = True
    return ExtendedApp
