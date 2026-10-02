# -*- coding: utf-8 -*-
"""Taxo 10.5-r6 — usable registry working data and 2026 Diia reconciliation UX."""
from __future__ import annotations

from datetime import date
from tkinter import simpledialog

import military_accounting_2026 as military
import military_transport_statement as transport_statement
import personnel_registry as personnel
import registry_working_data as working
import vehicle_reconciliation as reconciliation
import vehicle_registry
from v1045_features import _selected_employee_id
from v1048_features import _alive, _find_button, _walk, _configure_window

APP_VERSION = "10.5-r6"
LEGAL_PERSONNEL_2026 = (
    "Порядок №1487 зі змінами постанови КМУ №812 від 10.06.2026, чинними з 27.06.2026"
)
DIIA_METHOD = "Портал Дія"


def _copy_to_clipboard(widget, text):
    widget.clipboard_clear()
    widget.clipboard_append(str(text or ""))
    try:
        widget.update()
    except Exception:
        pass


def _name(employee):
    return " ".join(
        str(employee.get(key) or "").strip()
        for key in ("last_name", "first_name", "middle_name")
        if str(employee.get(key) or "").strip()
    )


def install(core, base_app):
    if getattr(core, "_TAXO_1056_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1056App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            con = core.db()
            try:
                working.ensure_personnel_schema(con)
                working.ensure_vehicle_schema(con)
                con.commit()
            finally:
                con.close()
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_r6_actions()

        def _install_r6_actions(self):
            root = getattr(self, "personnel_overview_page", None)
            if _alive(root) and not getattr(self, "_r6_personnel_registry_action", False):
                anchor = _find_button(root, "Оригінал держреєстру") or _find_button(root, "Реєстр документів")
                if anchor is not None:
                    core.ttk.Button(
                        anchor.master,
                        text="Військові дані / Дія",
                        command=self.open_employee_military_working_data,
                    ).pack(side="right", padx=(8, 0))
                    self._r6_personnel_registry_action = True

            vehicle_root = getattr(self, "tab_vehicles", None)
            if _alive(vehicle_root):
                military_button = _find_button(vehicle_root, "Військово-транспортний облік")
                if military_button is not None:
                    military_button.configure(
                        text="Відомість ТЦК 20.06 / 20.12",
                        command=self.open_military_transport_statement,
                    )

        # ------------------------------------------------------------------
        # Personnel: imported data becomes normal editable working data.
        # ------------------------------------------------------------------
        def open_employee_military_working_data(self):
            employee_id = _selected_employee_id(self)
            if employee_id is None:
                core.messagebox.showinfo("Військові дані", "Виберіть працівника у реєстрі.", parent=self)
                return

            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Військові дані / Дія — робоча картка Taxo", 1180, 760)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)

            title_var = core.tk.StringVar(value="")
            source_var = core.tk.StringVar(value="")
            core.ttk.Label(body, textvariable=title_var, style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "Ліворуч зберігаються робочі дані Taxo: їх можна редагувати й копіювати у документи. "
                    "Оригінальний державний витяг лишається окремим незмінним знімком. Редагування тут НЕ змінює Реєстр «Оберіг» або дані на Порталі Дія."
                ),
                wraplength=1130, justify="left",
            ).pack(anchor="w", pady=(4, 4))
            core.ttk.Label(body, textvariable=source_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

            frame = core.ttk.Frame(body)
            frame.pack(fill="both", expand=True)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            cols = ("group", "field", "value")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
            for key, label, width in (
                ("group", "Група", 160),
                ("field", "Поле", 360),
                ("value", "Робоче значення Taxo", 580),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")

            row_map = {}

            def refresh(select_iid=None):
                for iid in tree.get_children(""):
                    tree.delete(iid)
                row_map.clear()
                con = core.db()
                try:
                    data = working.employee_working_data(con, employee_id)
                finally:
                    con.close()
                title_var.set("Військові дані / Дія — %s" % (data["name"] or "Працівник"))
                source = data["last_source_name"] or "ручні/локальні дані"
                verified = data["last_verified_at"] or "—"
                source_var.set("Останнє джерело реєстру: %s · перевірено/імпортовано: %s" % (source, verified))
                counter = 0
                for field in working.PERSONAL_FIELDS:
                    counter += 1
                    iid = "p:%s" % field
                    row_map[iid] = ("personal", field)
                    tree.insert(
                        "", "end", iid=iid,
                        values=("Особисті дані", personnel.EMPLOYEE_FIELD_LABELS.get(field, field), data["personal"].get(field, "") or "—"),
                    )
                for field in working.MILITARY_FIELDS:
                    counter += 1
                    iid = "m:%s" % field
                    row_map[iid] = ("military", field)
                    tree.insert(
                        "", "end", iid=iid,
                        values=("Військовий облік", personnel.MILITARY_FIELD_LABELS.get(field, field), data["military"].get(field, "") or "—"),
                    )
                if select_iid and select_iid in tree.get_children(""):
                    tree.selection_set(select_iid)
                    tree.focus(select_iid)
                    tree.see(select_iid)

            def selected():
                sel = tree.selection()
                if not sel:
                    core.messagebox.showinfo("Військові дані", "Виберіть поле.", parent=win)
                    return None
                iid = sel[0]
                return iid, row_map[iid], tree.item(iid, "values")

            def edit_selected():
                item = selected()
                if item is None:
                    return
                iid, (scope, field), values = item
                current = "" if values[2] == "—" else values[2]
                label = values[1]
                value = simpledialog.askstring(
                    "Редагувати робоче поле",
                    "%s:\n\nЦе змінить лише робочі дані Taxo, а не державний реєстр." % label,
                    initialvalue=current,
                    parent=win,
                )
                if value is None:
                    return
                con = core.db()
                try:
                    if scope == "personal":
                        working.save_employee_working_data(con, employee_id, personal_values={field: value})
                    else:
                        working.save_employee_working_data(con, employee_id, military_values={field: value})
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Військові дані", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh(iid)

            def copy_selected():
                item = selected()
                if item is None:
                    return
                value = item[2][2]
                _copy_to_clipboard(win, "" if value == "—" else value)

            def copy_all():
                con = core.db()
                try:
                    text = working.employee_copy_text(con, employee_id)
                finally:
                    con.close()
                _copy_to_clipboard(win, text)

            controls = core.ttk.Frame(body)
            controls.pack(fill="x", pady=(8, 0))
            core.ttk.Button(controls, text="Редагувати поле", style="Accent.TButton", command=edit_selected).pack(side="left")
            core.ttk.Button(controls, text="Копіювати значення", command=copy_selected).pack(side="left", padx=6)
            core.ttk.Button(controls, text="Копіювати всю картку", command=copy_all).pack(side="left", padx=6)
            core.ttk.Button(controls, text="Оригінал держреєстру", command=self.open_employee_registry_raw_snapshot).pack(side="left", padx=6)
            core.ttk.Button(controls, text="Закрити", command=win.destroy).pack(side="right")
            tree.bind("<Double-1>", lambda _e: edit_selected())
            refresh()
            win.transient(self)

        # ------------------------------------------------------------------
        # Vehicle «Шлях»: editable working copy + immutable last snapshot.
        # ------------------------------------------------------------------
        def open_selected_vehicle_registry_data(self):
            vehicle = self.selected_vehicle() if hasattr(self, "selected_vehicle") else None
            if vehicle is None:
                core.messagebox.showinfo("Транспорт", "Виберіть транспортний засіб.", parent=self)
                return
            vehicle_id = int(vehicle["id"])
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Дані «Шлях» — робоча картка Taxo", 1240, 740)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)
            title_var = core.tk.StringVar(value="")
            source_var = core.tk.StringVar(value="")
            core.ttk.Label(body, textvariable=title_var, style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "«Робоче Taxo» можна редагувати й копіювати у документи. «Останній витяг» — незмінний знімок того, що прийшло з «Шлях». "
                    "Після ручної правки наступна звірка покаже різницю; історія реєстру не переписується."
                ),
                wraplength=1180, justify="left",
            ).pack(anchor="w", pady=(4, 4))
            core.ttk.Label(body, textvariable=source_var, style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

            frame = core.ttk.Frame(body)
            frame.pack(fill="both", expand=True)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            cols = ("field", "working", "registry", "state", "decision")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
            for key, label, width in (
                ("field", "Поле", 270),
                ("working", "Робоче Taxo", 260),
                ("registry", "Останній витяг «Шлях»", 260),
                ("state", "Стан", 160),
                ("decision", "Рішення", 210),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")
            for state, color in (
                (reconciliation.STATE_MATCH, "#0B5D1E"),
                (reconciliation.STATE_FILL, "#005B96"),
                (reconciliation.STATE_DIFFERENCE, "#7A5B00"),
                (reconciliation.STATE_CRITICAL, "#8A1C1C"),
                (reconciliation.STATE_UNAVAILABLE, "#666666"),
            ):
                tree.tag_configure(state, foreground=color)

            rows = {}

            def refresh(select_field=None):
                for iid in tree.get_children(""):
                    tree.delete(iid)
                rows.clear()
                con = core.db()
                try:
                    data = working.vehicle_working_data(con, vehicle_id)
                finally:
                    con.close()
                title_var.set("Дані «Шлях» — %s" % (data["plate"] or data["name"] or "ТЗ"))
                source_var.set(
                    "Останній файл: %s · звірено/імпортовано: %s" % (
                        data["last_source_name"] or "—", data["last_verified_at"] or "—"
                    )
                )
                for row in data["fields"]:
                    field = row["field"]
                    rows[field] = row
                    state_label = reconciliation.STATE_LABELS.get(row["state"], row["state"] or "Не звірялося")
                    decision_label = reconciliation.DECISION_LABELS.get(row["decision"], row["decision"] or "—")
                    tree.insert(
                        "", "end", iid=field,
                        values=(row["label"], row["working_value"] or "—", row["registry_value"] or "—", state_label, decision_label),
                        tags=((row["state"],) if row["state"] else ()),
                    )
                if select_field and select_field in tree.get_children(""):
                    tree.selection_set(select_field)
                    tree.focus(select_field)
                    tree.see(select_field)

            def selected_field():
                sel = tree.selection()
                if not sel:
                    core.messagebox.showinfo("Дані «Шлях»", "Виберіть поле.", parent=win)
                    return None
                return sel[0]

            def edit_selected():
                field = selected_field()
                if field is None:
                    return
                row = rows[field]
                value = simpledialog.askstring(
                    "Редагувати робоче поле ТЗ",
                    "%s:\n\nОригінальний витяг «Шлях» не змінюється." % row["label"],
                    initialvalue=row["working_value"], parent=win,
                )
                if value is None:
                    return
                if field in reconciliation.CRITICAL_FIELDS and value.strip() != row["working_value"]:
                    if not core.messagebox.askyesno(
                        "Ідентифікаційне поле",
                        "Ви змінюєте %s. Продовжити? Наступна звірка окремо покаже відповідність реєстру." % row["label"],
                        parent=win,
                    ):
                        return
                con = core.db()
                try:
                    working.save_vehicle_working_value(con, vehicle_id, field, value)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Дані «Шлях»", str(exc), parent=win)
                    return
                finally:
                    con.close()
                try:
                    self.load_vehicles()
                except Exception:
                    pass
                refresh(field)

            def accept_registry():
                field = selected_field()
                if field is None:
                    return
                row = rows[field]
                if not row["registry_value"]:
                    core.messagebox.showinfo("Дані «Шлях»", "У останньому витягу для цього поля немає значення.", parent=win)
                    return
                if field in reconciliation.CRITICAL_FIELDS:
                    if not core.messagebox.askyesno(
                        "Прийняти реєстрове значення",
                        "Прийняти реєстрове значення для ідентифікаційного поля %s?" % row["label"],
                        parent=win,
                    ):
                        return
                con = core.db()
                try:
                    reconciliation.accept_registry_value(con, vehicle_id, field, note="Прийнято з робочої картки 10.5-r6")
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Дані «Шлях»", str(exc), parent=win)
                    return
                finally:
                    con.close()
                try:
                    self.load_vehicles()
                except Exception:
                    pass
                refresh(field)

            def copy_selected():
                field = selected_field()
                if field is None:
                    return
                _copy_to_clipboard(win, rows[field]["working_value"])

            def copy_all():
                con = core.db()
                try:
                    text = working.vehicle_copy_text(con, vehicle_id)
                finally:
                    con.close()
                _copy_to_clipboard(win, text)

            controls = core.ttk.Frame(body)
            controls.pack(fill="x", pady=(8, 0))
            core.ttk.Button(controls, text="Редагувати робоче поле", style="Accent.TButton", command=edit_selected).pack(side="left")
            core.ttk.Button(controls, text="Прийняти з витягу", command=accept_registry).pack(side="left", padx=6)
            core.ttk.Button(controls, text="Копіювати значення", command=copy_selected).pack(side="left", padx=6)
            core.ttk.Button(controls, text="Копіювати всі дані", command=copy_all).pack(side="left", padx=6)
            core.ttk.Button(controls, text="Закрити", command=win.destroy).pack(side="right")
            tree.bind("<Double-1>", lambda _e: edit_selected())
            refresh()
            win.transient(self)

        # ------------------------------------------------------------------
        # Personnel military-accounting: Diia/cabinet is the normal 2026 path.
        # ------------------------------------------------------------------
        def open_military_accounting_overview(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Персональний військовий облік — Дія / Оберіг", 1120, 700)
            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Персональний військовий облік — Дія / Оберіг", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    LEGAL_PERSONNEL_2026 + ". За наявності технічної можливості звіряння з обліковими відомостями ТЦК виконується засобами Порталу Дія "
                    "або через кабінет персонального обліку. Паперовий/особистий маршрут лишається резервним, коли електронний спосіб технічно недоступний."
                ),
                wraplength=1060, justify="left",
            ).pack(anchor="w", pady=(4, 12))

            con = core.db()
            try:
                working.ensure_personnel_schema(con)
                military.ensure_schema_on_connection(con)
                annual = military.annual_reconciliation_status(con, today=date.today())
                last_import = con.execute(
                    "SELECT * FROM employee_registry_imports ORDER BY imported_at DESC,id DESC LIMIT 1"
                ).fetchone()
                open_actions = military.list_actions(con, status=military.STATUS_OPEN)
            finally:
                con.close()

            data_box = core.ttk.LabelFrame(body, text="1. Дані з Дії / Реєстру «Оберіг»", padding=12)
            data_box.pack(fill="x", pady=(0, 10))
            if last_import is None:
                data_text = "У Taxo ще немає імпортованого витягу."
            else:
                data_text = "Останній імпорт: %s · файл: %s" % (last_import["imported_at"], last_import["source_name"])
            core.ttk.Label(data_box, text=data_text, style="Subtitle.TLabel").pack(anchor="w")
            core.ttk.Label(
                data_box,
                text=(
                    "Імпорт потрібен для наповнення робочих карток Taxo і підготовки документів. Він не є окремою «квартальною вимогою». "
                    "Робочі значення можна редагувати; оригінальний витяг зберігається окремо."
                ),
                style="Muted.TLabel", wraplength=1010, justify="left",
            ).pack(anchor="w", pady=(3, 0))

            official_box = core.ttk.LabelFrame(body, text="2. Щорічне офіційне звіряння", padding=12)
            official_box.pack(fill="x", pady=(0, 10))
            official_state = "зафіксовано" if annual["has_authority_reconciliation"] else "ще не зафіксовано у журналі Taxo"
            docs_state = "зафіксовано" if annual["has_document_reconciliation"] else "ще не зафіксовано"
            core.ttk.Label(
                official_box,
                text="%s: звіряння з Дія/кабінетом/ТЦК — %s; звіряння з військово-обліковими документами працівників — %s."
                     % (annual["year"], official_state, docs_state),
                style="Subtitle.TLabel", wraplength=1010, justify="left",
            ).pack(anchor="w")
            core.ttk.Label(
                official_box,
                text=(
                    "Фінальна звірка не позначається виконаною автоматично після імпорту XLSX. У журнал Taxo вноситься фактично завершене звіряння, "
                    "підписане/зафіксоване у Дії або кабінеті персонального обліку."
                ),
                wraplength=1010, justify="left",
            ).pack(anchor="w", pady=(4, 0))

            actions_box = core.ttk.LabelFrame(body, text="3. Поточні дії", padding=12)
            actions_box.pack(fill="both", expand=True)
            core.ttk.Label(
                actions_box,
                text="Відкритих контрольних дій: %d" % len(open_actions),
                style="Subtitle.TLabel",
            ).pack(anchor="w")
            core.ttk.Label(
                actions_box,
                text=(
                    "Taxo веде строки і журнал як допоміжний контроль. Подання/звіряння виконується у державному електронному сервісі; Taxo не імітує відправлення до ТЦК."
                ),
                wraplength=1010, justify="left",
            ).pack(anchor="w", pady=(4, 10))
            buttons = core.ttk.Frame(actions_box)
            buttons.pack(fill="x")
            core.ttk.Button(buttons, text="Журнал звірянь Дія / ТЦК", command=self.open_official_reconciliation_log).pack(side="left", padx=(0, 8))
            core.ttk.Button(buttons, text="Дії та строки", command=self.open_military_actions_journal).pack(side="left", padx=4)
            core.ttk.Button(buttons, text="Закрити", command=win.destroy).pack(side="right")
            win.transient(self)

        def open_official_reconciliation_log(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Журнал щорічних звірянь — Дія / ТЦК", 1160, 700)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Журнал фактично проведених звірянь", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "За наявності технічної можливості звіряння з ТЦК проводиться засобами Порталу Дія або кабінету персонального обліку. "
                    "Запис тут створюйте після фактичного завершення процедури. Сам імпорт XLSX не ставить відмітку «звірено»."
                ),
                wraplength=1100, justify="left",
            ).pack(anchor="w", pady=(3, 8))

            labels = military.RECONCILIATION_LABELS
            label_to_kind = {label: kind for kind, label in labels.items()}
            form = core.ttk.Frame(body)
            form.pack(fill="x", pady=(0, 8))
            date_var = core.tk.StringVar(value=date.today().isoformat())
            kind_var = core.tk.StringVar(value=labels.get(military.RECONCILIATION_DIIA, military.RECONCILIATION_DIIA))
            method_var = core.tk.StringVar(value=DIIA_METHOD)
            authority_var = core.tk.StringVar(value="")
            ref_var = core.tk.StringVar(value="")
            for col, (label, var, width) in enumerate((
                ("Дата (YYYY-MM-DD)", date_var, 14),
                ("Вид", kind_var, 38),
                ("Спосіб", method_var, 22),
                ("ТЦК / орган", authority_var, 24),
                ("Реквізит / № заяви", ref_var, 22),
            )):
                core.ttk.Label(form, text=label).grid(row=0, column=col, sticky="w", padx=(0, 8))
                if label == "Вид":
                    widget = core.ttk.Combobox(form, textvariable=var, state="readonly", width=width, values=tuple(labels.values()))
                else:
                    widget = core.ttk.Entry(form, textvariable=var, width=width)
                widget.grid(row=1, column=col, sticky="ew", padx=(0, 8))
                form.columnconfigure(col, weight=1 if col >= 2 else 0)

            frame = core.ttk.Frame(body)
            frame.pack(fill="both", expand=True)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            cols = ("date", "kind", "method", "authority", "reference")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings")
            for key, label, width in (
                ("date", "Дата", 105),
                ("kind", "Вид", 330),
                ("method", "Спосіб", 170),
                ("authority", "Орган", 240),
                ("reference", "Реквізит", 200),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sy.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")

            def refresh():
                for iid in tree.get_children(""):
                    tree.delete(iid)
                con = core.db()
                try:
                    rows = military.reconciliation_history(con)
                finally:
                    con.close()
                for row in rows:
                    tree.insert(
                        "", "end",
                        values=(
                            row["reconciliation_date"], labels.get(row["kind"], row["kind"]),
                            row["method"] or "—", row["authority"] or "—", row["reference"] or "—",
                        ),
                    )

            def add_record():
                kind = label_to_kind.get(kind_var.get(), kind_var.get())
                try:
                    con = core.db()
                    try:
                        military.record_official_reconciliation(
                            con, date_var.get(), kind, method_var.get(), authority_var.get(), reference=ref_var.get()
                        )
                        con.commit()
                    finally:
                        con.close()
                except Exception as exc:
                    core.messagebox.showerror("Журнал звірянь", str(exc), parent=win)
                    return
                refresh()

            controls = core.ttk.Frame(body)
            controls.pack(fill="x", pady=(8, 0))
            core.ttk.Button(controls, text="Додати фактичне звіряння", style="Accent.TButton", command=add_record).pack(side="left")
            core.ttk.Button(controls, text="Закрити", command=win.destroy).pack(side="right")
            refresh()
            win.transient(self)

        # ------------------------------------------------------------------
        # Enterprise military-transport report is the primary vehicle UX.
        # ------------------------------------------------------------------
        def open_military_transport_statement(self):
            result = super().open_military_transport_statement()
            win = getattr(self, "_military_transport_statement_window", None)
            if not _alive(win):
                return result
            try:
                win.title("Відомість ТЦК — транспорт підприємства (20.06 / 20.12)")
            except Exception:
                pass
            for widget in _walk(win):
                try:
                    if widget.winfo_class() not in ("TLabel", "Label"):
                        continue
                    text = str(widget.cget("text") or "")
                    if text == "Відомість по власному транспорту":
                        widget.configure(text="Відомість ТЦК по власних / балансових транспортних засобах")
                    elif text.startswith(transport_statement.FORM_REFERENCE):
                        widget.configure(
                            text=(
                                transport_statement.FORM_REFERENCE
                                + ". Це звіт підприємства, а не облік військової частини. "
                                  "За чинним Положенням №1921 інформація за цією формою подається двічі на рік — до 20 червня та 20 грудня, "
                                  "а також у передбачених Положенням випадках за запитом."
                            )
                        )
                except Exception:
                    pass
            return result

    Taxo1056App.__name__ = "App"
    Taxo1056App.__qualname__ = "App"
    core.App = Taxo1056App
    core._TAXO_1056_INSTALLED = True
    return Taxo1056App
