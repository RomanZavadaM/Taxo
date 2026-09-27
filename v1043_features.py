# -*- coding: utf-8 -*-
"""Taxo 10.4-r3 safety fixes for driver schedules and company requisites.

The 8-hour no-tachograph bulk action is intentionally non-destructive:
it may create missing weekday rows, but it never rewrites an existing driver
plan, route, exact clock interval or work segment.

10.4-r3 also makes ЄДРПОУ a canonical company requisite.  The old P-5-only
setting is migrated automatically and kept compatible, while P-5 and the
waybill corner stamp read the same company value.
"""
from datetime import datetime

APP_VERSION = "10.4-r3"
EDRPOU_SETTING_KEY = "company_edrpou"


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


def _ensure_company_edrpou_schema(core):
    con = core.db()
    try:
        cols = {row[1] for row in con.execute("PRAGMA table_info(company)").fetchall()}
        if "edrpou" not in cols:
            con.execute("ALTER TABLE company ADD COLUMN edrpou TEXT DEFAULT ''")
        row = con.execute("SELECT edrpou FROM company WHERE id=1").fetchone()
        current = str((row["edrpou"] if row else "") or "").strip()
        legacy = con.execute(
            "SELECT value FROM app_settings WHERE key=?", (EDRPOU_SETTING_KEY,)
        ).fetchone()
        legacy_value = str((legacy[0] if legacy else "") or "").strip()
        if not current and legacy_value:
            con.execute("UPDATE company SET edrpou=? WHERE id=1", (legacy_value,))
        con.commit()
    finally:
        con.close()


def company_edrpou(core):
    try:
        con = core.db()
        try:
            row = con.execute("SELECT edrpou FROM company WHERE id=1").fetchone()
            return str((row["edrpou"] if row else "") or "").strip()
        finally:
            con.close()
    except Exception:
        return ""


def fill_empty_no_tacho_days(core, con, driver_id, driver, year, month):
    """Create only genuinely empty weekday plans for one driver.

    Existing worklog rows are immutable for this bulk operation. Personnel
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
    """Install 10.4-r3 runtime identity, schedule safety and ЄДРПОУ flow."""
    if getattr(core, "_TAXO_1043_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    original_init_db = core.init_db
    original_get_setting = core.get_setting
    original_set_setting = core.set_setting
    original_day_view = core.driver_day_view
    original_monthly_cell = core._monthly_shift_cell

    def init_db(*args, **kwargs):
        result = original_init_db(*args, **kwargs)
        _ensure_company_edrpou_schema(core)
        return result

    def get_setting(key, default=""):
        if key == EDRPOU_SETTING_KEY:
            value = company_edrpou(core)
            return value if value else original_get_setting(key, default)
        return original_get_setting(key, default)

    def set_setting(key, value):
        if key == EDRPOU_SETTING_KEY:
            value = str(value or "").strip()
            try:
                con = core.db()
                try:
                    cols = {row[1] for row in con.execute("PRAGMA table_info(company)").fetchall()}
                    if "edrpou" not in cols:
                        con.execute("ALTER TABLE company ADD COLUMN edrpou TEXT DEFAULT ''")
                    con.execute("UPDATE company SET edrpou=? WHERE id=1", (value,))
                    con.commit()
                finally:
                    con.close()
            finally:
                # Keep the legacy app_setting for backward compatibility with
                # older candidate binaries that may still open the same data.
                original_set_setting(key, value)
            return
        original_set_setting(key, value)

    core.init_db = init_db
    core.get_setting = get_setting
    core.set_setting = set_setting

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

    # P-5 already has an official ЄДРПОУ line. Make its exporter fall back to
    # the central company requisite even when called without the reports UI.
    try:
        import personnel_v91 as personnel
        original_p5_pdf = personnel.export_p5_pdf
        original_p5_xlsx = personnel.export_p5_xlsx

        def export_p5_pdf(*args, **kwargs):
            if not str(kwargs.get("edrpou", "") or "").strip():
                kwargs["edrpou"] = company_edrpou(core)
            return original_p5_pdf(*args, **kwargs)

        def export_p5_xlsx(*args, **kwargs):
            if not str(kwargs.get("edrpou", "") or "").strip():
                kwargs["edrpou"] = company_edrpou(core)
            return original_p5_xlsx(*args, **kwargs)

        personnel.export_p5_pdf = export_p5_pdf
        personnel.export_p5_xlsx = export_p5_xlsx
    except Exception:
        pass

    # The waybill renderer receives a plain data mapping. Add the central
    # requisite only for the corner-stamp rendering, without changing address
    # or other stored company fields.
    try:
        import waybill
        original_corner_stamp = waybill._corner_stamp

        def corner_stamp(c, x, y, w, h, data):
            payload = dict(data or {})
            edrpou = str(payload.get("company_edrpou", "") or "").strip() or company_edrpou(core)
            if edrpou:
                line = f"ЄДРПОУ: {edrpou}"
                email = str(payload.get("company_email", "") or "").strip()
                payload["company_email"] = "\n".join(v for v in (email, line) if v)
            return original_corner_stamp(c, x, y, w, h, payload)

        waybill._corner_stamp = corner_stamp
    except Exception:
        pass

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

        def build_company(self):
            result = super().build_company()
            if "edrpou" in getattr(self, "company_vars", {}):
                return result

            parent = None
            try:
                stack = list(self.tab_company.winfo_children())
                while stack:
                    widget = stack.pop(0)
                    stack.extend(widget.winfo_children())
                    try:
                        if widget.winfo_class() in {"TLabel", "Label"} and str(widget.cget("text")) == "Посада підписанта":
                            parent = widget.master
                            break
                    except core.tk.TclError:
                        pass
            except core.tk.TclError:
                parent = None

            if parent is not None:
                rows = []
                for child in parent.winfo_children():
                    try:
                        info = child.grid_info()
                        if info and str(info.get("row", "")).isdigit():
                            rows.append(int(info["row"]))
                    except core.tk.TclError:
                        pass
                row = max(rows, default=-1) + 1
                var = core.tk.StringVar(value=company_edrpou(core))
                self.company_vars["edrpou"] = var
                core.ttk.Label(parent, text="ЄДРПОУ").grid(
                    row=row, column=0, sticky="w", padx=8, pady=5
                )
                core.ttk.Entry(parent, textvariable=var, width=44).grid(
                    row=row, column=1, sticky="ew", padx=8, pady=5
                )
            return result

        def save_company(self, *args, **kwargs):
            result = super().save_company(*args, **kwargs)
            var = getattr(self, "company_vars", {}).get("edrpou")
            if var is not None:
                value = var.get().strip()
                core.set_setting(EDRPOU_SETTING_KEY, value)
                report_var = getattr(self, "personnel_report_edrpou", None)
                if report_var is not None:
                    report_var.set(value)
            return result

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title(f"Taxo {core.APP_VERSION} — Працівники, графіки та шляхівки")
            report_var = getattr(self, "personnel_report_edrpou", None)
            if report_var is not None:
                report_var.set(company_edrpou(core))

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
