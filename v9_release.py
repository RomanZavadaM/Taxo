# -*- coding: utf-8 -*-
"""Taxo 9.0 UI/report refinements.

Adds editable report formation dates to the two driver-control PDFs and lets the
operator switch driver directly inside the single-driver №340 / 60-hour balance
window.  The 60-day minute activity register from v8.70 r11 remains intact.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import os

from activity_register_60 import (
    PERIOD_DAYS,
    collect_activity_register,
    default_output_path as activity_default_output_path,
    export_activity_register_pdf,
)
from work_analysis_ext import analysis_pdf_default_path


def parse_report_date(value):
    """Parse the UI DD.MM.YYYY formation date."""
    return datetime.strptime((value or "").strip(), "%d.%m.%Y").date()


def report_datetime(report_date, now=None):
    """Use the chosen calendar date while keeping the actual generation time."""
    now = now or datetime.now()
    return datetime.combine(report_date, now.time().replace(microsecond=0))


def _walk_widgets(root):
    for child in root.winfo_children():
        yield child
        yield from _walk_widgets(child)


def _driver_choices(core, app):
    con = core.db()
    try:
        rows = con.execute(
            "SELECT * FROM drivers ORDER BY last_name,first_name,middle_name,id"
        ).fetchall()
    finally:
        con.close()

    mapping = {}
    current_label = ""
    for row in rows:
        label = app.driver_full_name(row)
        if label in mapping:
            label = f"{label} [ID {row['id']}]"
        mapping[label] = row["id"]
        if row["id"] == getattr(app, "driver_id", None):
            current_label = label
    return mapping, current_label


def stamp_work_analysis_pdf(core, path, report_date):
    """Compatibility no-op kept for the v9 call chain.

    Since 10.2-r9 the formation date is rendered directly by
    main.export_work_analysis_pdf() using ReportLab. This avoids reopening and
    rewriting the PDF with PyMuPDF/fitz.
    """
    return Path(path)


def install(core, base_app):
    """Install Taxo 9.0 behavior on top of the r11 application class."""
    if getattr(core, "_TAXO_V9_INSTALLED", False):
        return core.App

    class Taxo9App(base_app):
        def _v9_report_date(self, raw_value, parent, title="Дата формування"):
            try:
                return parse_report_date(raw_value)
            except ValueError:
                core.messagebox.showerror(
                    title,
                    "Вкажіть дату у форматі ДД.ММ.РРРР.",
                    parent=parent,
                )
                return None

        def _v9_write_work_analysis_pdf(self, target, parent):
            report_raw = getattr(
                self,
                "_v9_analysis_report_date",
                date.today().strftime("%d.%m.%Y"),
            )
            report_date = self._v9_report_date(report_raw, parent)
            if report_date is None:
                return None

            data = self.calculate_work_analysis()
            if data is None:
                core.messagebox.showwarning(
                    "Підсумки", "Спочатку виберіть водія.", parent=parent
                )
                return None
            data["report_date"] = report_date

            driver = self.driver_by_id(self.driver_id)
            driver_name = (
                self.driver_full_name(driver)
                if driver
                else self.work_driver_var.get()
            )

            def writer(out):
                core.export_work_analysis_pdf(data, driver_name, out)
                stamp_work_analysis_pdf(core, out, report_date)

            return core.write_output_file(
                writer,
                target,
                parent=parent,
                kind="PDF аналізу №340",
                error_title="Помилка PDF",
            )

        def open_current_work_analysis_pdf(self):
            data = self.calculate_work_analysis()
            if data is None:
                core.messagebox.showwarning(
                    "Підсумки", "Спочатку виберіть водія.", parent=self
                )
                return
            driver = self.driver_by_id(self.driver_id)
            driver_name = (
                self.driver_full_name(driver)
                if driver
                else self.work_driver_var.get()
            )
            target = analysis_pdf_default_path(core.OUTPUT_DIR, driver_name, data)
            parent = getattr(self, "_work_analysis_r10_win", self)
            actual = self._v9_write_work_analysis_pdf(target, parent)
            if actual is not None:
                core.open_external(actual)

        def _v9_save_work_analysis_pdf(self, parent):
            data = self.calculate_work_analysis()
            if data is None:
                core.messagebox.showwarning(
                    "Підсумки", "Спочатку виберіть водія.", parent=parent
                )
                return
            driver = self.driver_by_id(self.driver_id)
            driver_name = (
                self.driver_full_name(driver)
                if driver
                else self.work_driver_var.get()
            )
            default = analysis_pdf_default_path(core.OUTPUT_DIR, driver_name, data).name
            path = core.filedialog.asksaveasfilename(
                parent=parent,
                title="Зберегти аналіз у PDF",
                initialdir=str(core.OUTPUT_DIR),
                initialfile=default,
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
            )
            if not path:
                return
            actual = self._v9_write_work_analysis_pdf(Path(path), parent)
            if actual is not None:
                core.messagebox.showinfo("PDF", f"Збережено:\n{actual}", parent=parent)

        def show_work_analysis(self):
            before = {str(widget) for widget in self.winfo_children()}
            result = super().show_work_analysis()

            created = [
                widget
                for widget in self.winfo_children()
                if str(widget) not in before
                and isinstance(widget, core.tk.Toplevel)
                and widget.winfo_exists()
            ]
            win = next(
                (w for w in created if w.title() == "Підсумки та контроль №340"),
                getattr(self, "_work_analysis_r10_win", None),
            )
            if win is None or not win.winfo_exists():
                return result

            self._work_analysis_r10_win = win
            if not hasattr(self, "_v9_analysis_report_date"):
                self._v9_analysis_report_date = date.today().strftime("%d.%m.%Y")

            head = next(
                (w for w in win.winfo_children() if isinstance(w, core.ttk.Frame)),
                None,
            )
            if head is None:
                return result

            controls = core.ttk.Frame(head)
            controls.pack(fill="x", pady=(6, 0))

            mapping, current_label = _driver_choices(core, self)
            driver_var = core.tk.StringVar(value=current_label)
            core.ttk.Label(controls, text="Водій:").pack(side="left")
            combo = core.ttk.Combobox(
                controls,
                textvariable=driver_var,
                values=list(mapping.keys()),
                state="readonly",
                width=34,
            )
            combo.pack(side="left", padx=(4, 12))

            core.ttk.Label(controls, text="Дата формування:").pack(side="left")
            report_var = core.tk.StringVar(value=self._v9_analysis_report_date)
            core.ttk.Entry(controls, textvariable=report_var, width=12).pack(
                side="left", padx=(4, 2)
            )
            if hasattr(core, "calendar_button"):
                core.calendar_button(controls, report_var).pack(side="left", padx=(0, 8))

            def remember_report_date(*_args):
                self._v9_analysis_report_date = report_var.get().strip()

            report_var.trace_add("write", remember_report_date)

            def switch_driver(_event=None):
                did = mapping.get(driver_var.get())
                if not did or did == getattr(self, "driver_id", None):
                    return
                self._v9_analysis_report_date = report_var.get().strip()
                self.driver_id = did
                try:
                    self.work_driver_var.set(driver_var.get().split(" [ID ", 1)[0])
                except Exception:
                    pass
                try:
                    win.destroy()
                finally:
                    self.after_idle(self.show_work_analysis)

            combo.bind("<<ComboboxSelected>>", switch_driver)

            for widget in _walk_widgets(win):
                try:
                    if isinstance(widget, core.ttk.Button) and widget.cget("text") == "Зберегти PDF":
                        widget.configure(command=lambda w=win: self._v9_save_work_analysis_pdf(w))
                except Exception:
                    pass
            return result

        def show_activity_register_60(self):
            if not getattr(self, "driver_id", None):
                core.messagebox.showwarning(
                    "Реєстр 60 днів", "Спочатку виберіть водія.", parent=self
                )
                return

            win = core.tk.Toplevel(self)
            win.title("Реєстр діяльності водія за 60 днів")
            win.resizable(False, False)
            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)
            core.ttk.Label(
                body,
                text=(
                    "Окремий PDF: 60 календарних днів, 24:00 кожної доби, "
                    "інтервали з точністю до хвилини."
                ),
                wraplength=600,
                justify="left",
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

            end_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            report_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            period_var = core.tk.StringVar()

            core.ttk.Label(body, text="Кінцева дата періоду").grid(row=1, column=0, sticky="w", pady=5)
            core.ttk.Entry(body, textvariable=end_var, width=16).grid(row=1, column=1, sticky="w", padx=6)
            if hasattr(core, "calendar_button"):
                core.calendar_button(body, end_var).grid(row=1, column=2, sticky="w")

            core.ttk.Label(body, text="Дата формування").grid(row=2, column=0, sticky="w", pady=5)
            core.ttk.Entry(body, textvariable=report_var, width=16).grid(row=2, column=1, sticky="w", padx=6)
            if hasattr(core, "calendar_button"):
                core.calendar_button(body, report_var).grid(row=2, column=2, sticky="w")

            core.ttk.Label(body, textvariable=period_var, foreground="gray").grid(
                row=3, column=0, columnspan=3, sticky="w", pady=(0, 10)
            )

            def resolve_period(show_error=False):
                try:
                    end_day = parse_report_date(end_var.get())
                except ValueError:
                    if show_error:
                        core.messagebox.showerror(
                            "Дата",
                            "Вкажіть кінцеву дату у форматі ДД.ММ.РРРР.",
                            parent=win,
                        )
                    return None
                start_day = end_day - core.timedelta(days=PERIOD_DAYS - 1)
                period_var.set(
                    f"Період: {start_day.strftime('%d.%m.%Y')}–{end_day.strftime('%d.%m.%Y')} "
                    f"({PERIOD_DAYS} днів)"
                )
                return end_day

            def generate(open_after=True):
                end_day = resolve_period(show_error=True)
                if end_day is None:
                    return
                report_date = self._v9_report_date(report_var.get(), win)
                if report_date is None:
                    return
                try:
                    data = collect_activity_register(
                        core, self.driver_id, end_day, PERIOD_DAYS
                    )
                    data["generated_at"] = report_datetime(report_date)
                    data["report_date"] = report_date
                except Exception as exc:
                    core._append_error_log("60-денний реєстр діяльності", exc)
                    core.messagebox.showerror(
                        "Реєстр 60 днів",
                        f"Не вдалося зібрати дані:\n{exc}",
                        parent=win,
                    )
                    return
                target = activity_default_output_path(core, data)
                actual = core.write_output_file(
                    lambda out: export_activity_register_pdf(core, data, out),
                    target,
                    parent=win,
                    kind="PDF реєстру діяльності",
                    error_title="Помилка PDF",
                )
                if actual is not None:
                    if open_after:
                        core.open_external(actual)
                    else:
                        core.messagebox.showinfo(
                            "Реєстр 60 днів", f"PDF створено:\n{actual}", parent=win
                        )

            end_var.trace_add("write", lambda *_: resolve_period(False))
            resolve_period(False)
            buttons = core.ttk.Frame(body)
            buttons.grid(row=4, column=0, columnspan=3, sticky="e", pady=(6, 0))
            core.ttk.Button(buttons, text="Зберегти PDF", command=lambda: generate(False)).pack(side="left", padx=4)
            core.ttk.Button(buttons, text="Сформувати й відкрити PDF", command=lambda: generate(True)).pack(side="left", padx=4)
            core.ttk.Button(buttons, text="Закрити", command=win.destroy).pack(side="left", padx=(12, 0))
            try:
                win.transient(self)
                win.grab_set()
            except Exception:
                pass

    Taxo9App.__name__ = "App"
    Taxo9App.__qualname__ = "App"
    core.App = Taxo9App
    core._TAXO_V9_INSTALLED = True
    return Taxo9App
