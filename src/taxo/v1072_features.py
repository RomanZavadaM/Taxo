# -*- coding: utf-8 -*-
"""Taxo 10.7-r2 — «Експлуатація», накази і контроль відомості ТЦК."""
from __future__ import annotations

import re
import sys

import military_transport_statement as statement
import operations_orders as ops
import operations_orders_ui as operations_ui
import personnel_registry_lossless as personnel_lossless
import registry_working_data as working
from v1045_features import _selected_employee_id

APP_VERSION = "10.7-r2"


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _statement_day(win):
    for widget in _walk(win):
        try:
            if widget.winfo_class() in ("TEntry", "Entry"):
                value = str(widget.get() or "").strip()
                if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
                    return value
        except Exception:
            pass
    return ""


def _employee_full_name(row):
    if row is None:
        return ""
    return " ".join(
        str(row[key] or "").strip()
        for key in ("last_name", "first_name", "middle_name")
        if str(row[key] or "").strip()
    )


def _accept_all_latest_registry_values(con, employee_id):
    """Copy every non-empty canonical value from the latest imported snapshot.

    The immutable raw snapshot is not changed. This is the one-click counterpart
    to accepting fields one by one after an import from Diia / state registry.
    """
    working.ensure_personnel_schema(con)
    rows = personnel_lossless.latest_raw_snapshot(con, int(employee_id))
    personal = {}
    military = {}
    for row in rows:
        scope = str(row["canonical_scope"] or "")
        field = str(row["canonical_field"] or "")
        value = str(row["canonical_value"] or "").strip()
        if not field or not value:
            continue
        if scope == "personal" and field in working.PERSONAL_FIELDS:
            personal[field] = value
        elif scope == "military" and field in working.MILITARY_FIELDS:
            military[field] = value
    if not personal and not military:
        return 0
    working.save_employee_working_data(
        con, int(employee_id), personal_values=personal, military_values=military
    )
    return len(personal) + len(military)


def _install_statement_sources(core):
    if getattr(statement, "_taxo_v1072_sources", False):
        return
    base_workers = statement._workers_for_statement
    base_pdf = statement.export_statement_pdf
    base_xlsx = statement.export_statement_xlsx

    def workers_for_statement(con, vehicle_id, as_of):
        current = ops.active_driver_assignments(con, vehicle_id, as_of)
        if current:
            result = []
            for row in current:
                result.append({
                    "worker_name": "",
                    "last_name": row["last_name"],
                    "first_name": row["first_name"],
                    "middle_name": row["middle_name"],
                    "birth_date": row["birth_date"],
                    "actual_address": row["actual_address"],
                    "registered_address": row["registered_address"],
                    "military_specialty": row["military_specialty"],
                    "military_rank": row["military_rank"],
                })
            return result
        return base_workers(con, vehicle_id, as_of)

    def require_approval(report_date, company, rows):
        con = core.db()
        try:
            ok, approval = ops.military_statement_is_approved(con, report_date, company, rows)
        finally:
            con.close()
        if ok:
            return
        if approval is None:
            raise RuntimeError(
                "Перед формуванням затвердженої відомості її має підтвердити відповідальний "
                "за військово-транспортний обов'язок у вікні відомості."
            )
        raise RuntimeError(
            "Після останнього затвердження дані відомості змінилися. Перевірте їх і затвердіть повторно."
        )

    def export_pdf(path, report_date, company, rows, font_path=None):
        require_approval(report_date, company, rows)
        return base_pdf(path, report_date, company, rows, font_path=font_path)

    def export_xlsx(path, report_date, company, rows):
        require_approval(report_date, company, rows)
        return base_xlsx(path, report_date, company, rows)

    statement._workers_for_statement = workers_for_statement
    statement.export_statement_pdf = export_pdf
    statement.export_statement_xlsx = export_xlsx
    statement._taxo_v1072_sources = True


def install(core, base_app):
    if getattr(core, "_TAXO_1072_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION
    ops.ensure_schema(core)
    _install_statement_sources(core)

    class Taxo1072App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_operations_nav()

        def _install_operations_nav(self):
            if "Експлуатація" in getattr(self, "_nav_named_buttons", {}):
                return
            anchor = getattr(self, "_nav_named_buttons", {}).get("Маршрути")
            if not _alive(anchor):
                return
            parent = anchor.master
            icon = core.nav_photo(parent, "gear", 26)
            self._nav_icons["Експлуатація"] = icon

            def invoke(_event=None):
                self.open_operations_center()
                return "break"

            if sys.platform == "darwin":
                btn = core.tk.Label(
                    parent, image=icon, text="Експлуатація", compound="left", anchor="w",
                    takefocus=1, bg=core.PALETTE["sidebar"], fg="#FFFFFF",
                    relief="flat", bd=0, highlightthickness=0,
                    padx=16, pady=11, font=("TkDefaultFont",11,"bold"), cursor="pointinghand",
                )
                btn.bind("<Button-1>", invoke, add="+")
                btn.bind("<Return>", invoke, add="+")
                btn.bind("<space>", invoke, add="+")
            else:
                btn = core.tk.Button(
                    parent, image=icon, text="Експлуатація", compound="left",
                    command=self.open_operations_center, anchor="w",
                    bg=core.PALETTE["sidebar"], fg="#FFFFFF",
                    activebackground=core.PALETTE["blue_dark"], activeforeground="#FFFFFF",
                    relief="flat", bd=0, highlightthickness=0,
                    padx=16, pady=10, font=("TkDefaultFont",10,"bold"), cursor="hand2",
                )
            btn.pack(fill="x", before=anchor)
            self._nav_named_buttons["Експлуатація"] = btn

        def open_operations_center(self):
            return operations_ui.open_operations_center(self, core)

        def open_employee_military_working_data(self):
            employee_id = _selected_employee_id(self)
            before = set(self.winfo_children())
            result = super().open_employee_military_working_data()
            if employee_id is None:
                return result
            after = [child for child in self.winfo_children() if child not in before]
            candidates = [w for w in after if _alive(w)]
            if not candidates:
                candidates = [w for w in self.winfo_children() if _alive(w)]
            win = None
            for item in reversed(candidates):
                try:
                    if "Військові дані / Дія" in item.title():
                        win = item
                        break
                except Exception:
                    pass
            if win is None or getattr(win, "_taxo_v1072_accept_all", False):
                return result
            children = win.winfo_children()
            if not children:
                return result
            body = children[0]
            bar = core.ttk.Frame(body)
            bar.pack(fill="x", pady=(4, 0))

            def accept_all():
                if not core.messagebox.askyesno(
                    "Прийняти всі реквізити?",
                    "Підтягнути всі непорожні розпізнані реквізити з останнього імпортованого файлу у робочу картку Taxo?\n\n"
                    "Оригінальний імпортований знімок не змінюється.",
                    parent=win,
                ):
                    return
                con = core.db()
                try:
                    count = _accept_all_latest_registry_values(con, employee_id)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Військові дані", str(exc), parent=win)
                    return
                finally:
                    con.close()
                if count:
                    core.messagebox.showinfo(
                        "Військові дані",
                        "Підтягнуто реквізитів: %d.\nЗакрийте і повторно відкрийте картку для оновлення таблиці." % count,
                        parent=win,
                    )
                else:
                    core.messagebox.showinfo(
                        "Військові дані",
                        "В останньому імпорті немає нових розпізнаних реквізитів для масового перенесення.",
                        parent=win,
                    )

            core.ttk.Button(
                bar, text="Підтягнути всі реквізити з останнього імпорту",
                style="Accent.TButton", command=accept_all,
            ).pack(side="left")
            core.ttk.Label(
                bar,
                text="Без підтвердження кожного поля окремо.",
                style="Muted.TLabel",
            ).pack(side="left", padx=8)
            win._taxo_v1072_accept_all = True
            return result

        def open_military_transport_statement(self):
            result = super().open_military_transport_statement()
            win = getattr(self, "_military_transport_statement_window", None)
            if not _alive(win) or getattr(win, "_taxo_v1072_approval", False):
                return result
            children = win.winfo_children()
            if not children:
                return result
            body = children[0]
            approval_var = core.tk.StringVar(value="")
            bar = core.ttk.LabelFrame(body, text="Затвердження відповідальним", padding=(8,5))
            bar.pack(fill="x", pady=(8,0))
            core.ttk.Label(bar, textvariable=approval_var, style="Muted.TLabel").pack(side="left", fill="x", expand=True)

            def day_value():
                value = _statement_day(win)
                if not value:
                    raise ValueError("Не вдалося визначити дату відомості.")
                return value

            def refresh_approval():
                try:
                    day = day_value()
                except Exception as exc:
                    approval_var.set(str(exc))
                    return
                con = core.db()
                try:
                    cfg = ops.settings(con)
                    rows = statement.collect_statement_rows(con, day)
                    company = statement.company_details(con)
                    ok, approval = ops.military_statement_is_approved(con, day, company, rows)
                    responsible_id = cfg["military_transport_responsible_employee_id"] if cfg else None
                    responsible = ops.employee_name(con, responsible_id)
                finally:
                    con.close()
                if ok and approval is not None:
                    approval_var.set(
                        "Затверджено: %s · %s" % (
                            _employee_full_name(approval), str(approval["approved_at"] or "")
                        )
                    )
                elif approval is not None:
                    approval_var.set("Дані змінено після затвердження — потрібне повторне підтвердження.")
                elif responsible:
                    approval_var.set("Очікує затвердження: %s" % responsible)
                else:
                    approval_var.set("У «Експлуатація → Відповідальні» не вибрано відповідального.")

            def approve():
                try:
                    day = day_value()
                except Exception as exc:
                    core.messagebox.showerror("Відомість ТЦК", str(exc), parent=win)
                    return
                con = core.db()
                try:
                    cfg = ops.settings(con)
                    responsible_id = cfg["military_transport_responsible_employee_id"] if cfg else None
                    if not responsible_id:
                        raise ValueError("Спочатку виберіть відповідального у розділі «Експлуатація → Відповідальні».")
                    rows = statement.collect_statement_rows(con, day)
                    company = statement.company_details(con)
                    ops.approve_military_statement(con, day, company, rows, responsible_id)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Відомість ТЦК", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh_approval()

            core.ttk.Button(
                bar, text="Затвердити дані відомості",
                style="Accent.TButton", command=approve,
            ).pack(side="right", padx=(8,0))
            core.ttk.Button(bar, text="Оновити стан", command=refresh_approval).pack(side="right")
            refresh_approval()
            win._taxo_v1072_approval = True
            return result

    Taxo1072App.__name__ = "App"
    Taxo1072App.__qualname__ = "App"
    core.App = Taxo1072App
    core._TAXO_1072_INSTALLED = True
    return Taxo1072App
