# -*- coding: utf-8 -*-
"""Taxo 10.4-r3 safety fixes for driver schedule planning.

The 8-hour no-tachograph bulk action is intentionally non-destructive:
it may create missing weekday rows, but it never rewrites an existing driver
plan, route, exact clock interval or work segment.
"""
from datetime import datetime

APP_VERSION = "10.4-r3"


def _record_value(record, key, default=""):
    if record is None:
        return default
    try:
        if key in record.keys():
            return record[key]
    except Exception:
        pass
    if isinstance(record, dict):
        return record.get(key, default)
    return default


def fill_empty_no_tacho_days(core, con, driver_id, driver, year, month):
    """Create only genuinely empty weekday plans for one driver.

    Existing worklog rows are immutable for this bulk operation.  Personnel
    absences are skipped as well so the helper cannot hide a known non-work day
    under a newly-created 8-hour plan.
    """
    y, m = int(year), int(month)
    ym = f"{y:04d}-{m:02d}"
    existing = {
        row["work_date"]
        for row in con.execute(
            "SELECT work_date FROM worklog WHERE driver_id=? AND substr(work_date,1,7)=?",
            (int(driver_id), ym),
        ).fetchall()
    }

    absence_dates = set()
    override_types = set(getattr(core, "TAXO_NONWORK_OVERRIDE_TYPES", set()) or ())
    if override_types:
        employee = con.execute(
            "SELECT id FROM employees WHERE driver_id=? ORDER BY active DESC,id LIMIT 1",
            (int(driver_id),),
        ).fetchone()
        if employee:
            for row in con.execute(
                "SELECT work_date,day_type FROM employee_time_entries "
                "WHERE employee_id=? AND substr(work_date,1,7)=?",
                (employee["id"], ym),
            ).fetchall():
                if str(row["day_type"] or "") in override_types:
                    absence_dates.add(row["work_date"])

    added = 0
    skipped_existing = 0
    skipped_absence = 0
    for work_day in core.month_dates(y, m):
        if work_day.weekday() >= 5 or not core.driver_employed_on(driver, work_day):
            continue
        iso = work_day.isoformat()
        if iso in existing:
            skipped_existing += 1
            continue
        if iso in absence_dates:
            skipped_absence += 1
            continue
        con.execute(
            """INSERT INTO worklog(
                   driver_id,work_date,day_type,start_time,end_time,
                   work_start_time,work_end_time,work_hours,driving_hours,
                   route_name,route_id,template_id,shift_type,accounting_mode
               ) VALUES(?,?,?,'','','','',8,0,'',NULL,NULL,'Безперервна',?)""",
            (int(driver_id), iso, "Робота", core.WORK_MODE_NO_TACHO),
        )
        added += 1

    return {
        "added": added,
        "skipped_existing": skipped_existing,
        "skipped_absence": skipped_absence,
    }


def install(core, base_app):
    """Install 10.4-r3 runtime identity and schedule-safety behavior."""
    if getattr(core, "_TAXO_1043_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    original_day_view = core.driver_day_view
    original_monthly_cell = core._monthly_shift_cell

    def driver_day_view(*args, **kwargs):
        state = original_day_view(*args, **kwargs)
        if (
            state.get("explicit_worklog")
            and not state.get("suppressed_plan")
            and state.get("day_type") == "Робота"
            and not state.get("bands")
            and int(state.get("work_minutes") or 0) > 0
        ):
            state["status_label"] = (
                f"План {core.minutes_hhmm(state['work_minutes'])} · час зміни не задано"
            )
        return state

    def monthly_shift_cell(row, segments):
        value = original_monthly_cell(row, segments)
        if row is None or segments:
            return value
        if str(_record_value(row, "day_type", "") or "").strip() != "Робота":
            return value
        start = str(_record_value(row, "start_time", "") or "").strip()
        end = str(_record_value(row, "end_time", "") or "").strip()
        if start or end:
            return value
        minutes = core.hours_value_to_minutes(_record_value(row, "work_hours", 0))
        return f"{core.minutes_hhmm(minutes)}\nбез часу" if minutes > 0 else value

    core.driver_day_view = driver_day_view
    core._monthly_shift_cell = monthly_shift_cell

    def replace_about_command(app):
        try:
            menu_name = app.cget("menu")
            if not menu_name:
                return
            menubar = app.nametowidget(menu_name)
            end = menubar.index("end")
            if end is None:
                return
            for index in range(end + 1):
                if menubar.type(index) != "cascade" or menubar.entrycget(index, "label") != "Довідка":
                    continue
                submenu = app.nametowidget(menubar.entrycget(index, "menu"))
                sub_end = submenu.index("end")
                if sub_end is None:
                    return
                for sub_index in range(sub_end + 1):
                    if submenu.type(sub_index) == "command" and submenu.entrycget(sub_index, "label") == "Про програму":
                        submenu.entryconfigure(
                            sub_index,
                            command=lambda: core.messagebox.showinfo(
                                f"Taxo {core.APP_VERSION}",
                                "Облік роботи водіїв, табелів, шляхових листів, "
                                "бланків підтвердження діяльності та аналогових тахокарт.\n\n"
                                f"Taxo {core.APP_VERSION}.\n"
                                f"{core.COPYRIGHT_NOTICE}\n{core.LICENSE_LABEL}",
                                parent=app,
                            ),
                        )
                        return
        except core.tk.TclError:
            return

    class Taxo1043App(base_app):
        def build_menu(self):
            result = super().build_menu()
            replace_about_command(self)
            return result

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title(f"Taxo {core.APP_VERSION} — Працівники, графіки та шляхівки")

        def autofill(self):
            if not self.driver_id:
                core.messagebox.showwarning("Увага", "Спочатку виберіть водія.", parent=self)
                return

            y, m = int(self.year_var.get()), int(self.month_var.get())
            driver = self.driver_by_id(self.driver_id)
            if not driver or not any(core.driver_employed_on(driver, d) for d in core.month_dates(y, m)):
                core.messagebox.showwarning(
                    "Увага", "Водій ще не був прийнятий на роботу в обраному місяці.", parent=self
                )
                return

            if not core.messagebox.askyesno(
                "Заповнити порожні робочі дні",
                f"Заповнити ТІЛЬКИ ПОРОЖНІ будні {m:02d}.{y} як «Без тахо — стандартні 8 год»?\n\n"
                "Існуючі графіки, маршрути, точний час, часові частини та ручні записи НЕ змінюються.",
                parent=self,
            ):
                return

            con = core.db()
            try:
                result = fill_empty_no_tacho_days(core, con, self.driver_id, driver, y, m)
                con.commit()
            finally:
                con.close()

            self.refresh_month()
            if hasattr(self, "refresh_schedule"):
                self.refresh_schedule()
            core.messagebox.showinfo(
                "Заповнення завершено",
                f"Додано нових днів: {result['added']}.\n"
                f"Пропущено вже запланованих: {result['skipped_existing']}.\n"
                f"Пропущено днів відсутності: {result['skipped_absence']}.\n\n"
                "Жоден існуючий графік не змінено.",
                parent=self,
            )

    Taxo1043App.__name__ = "App"
    Taxo1043App.__qualname__ = "App"
    core.App = Taxo1043App
    core._TAXO_1043_INSTALLED = True
    return Taxo1043App
