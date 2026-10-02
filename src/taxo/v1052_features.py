# -*- coding: utf-8 -*-
"""Taxo 10.5-r2 — field-level «Шлях» reconciliation UI."""
from __future__ import annotations

import vehicle_reconciliation as reconciliation
import vehicle_registry

APP_VERSION = "10.5-r2"


def _text(value):
    return str(value or "").strip()


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _configure_window(core, win, title, width=1220, height=760):
    win.title(title)
    try:
        core.fit_window_to_screen(win, width, height, min(width, 820), min(height, 540))
    except Exception:
        win.geometry("%dx%d" % (width, height))
        win.minsize(min(width, 820), min(height, 540))
    try:
        core.configure_toplevel(win, title=title, minsize=(min(width, 820), min(height, 540)))
    except Exception:
        pass


def _row_status_label(status):
    return {
        "no_changes": "Відповідає",
        "fill": "Можна доповнити",
        "difference": "Є розбіжності",
        "critical": "Критичний конфлікт",
        "new_registry": "Нове в реєстрі",
        "local_only": "Є лише в Taxo",
    }.get(status, status)


def install(core, base_app):
    if getattr(core, "_TAXO_1052_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1052App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            reconciliation.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def _sync_shlyakh_field_state(self, preview):
            con = core.db()
            try:
                count = reconciliation.sync_preview_state(con, preview)
                con.commit()
                return count
            except Exception:
                con.rollback()
                raise
            finally:
                con.close()

        def _show_shlyakh_preview(self, preview):
            """Replace the r8 row-only preview with row + per-field reconciliation."""
            try:
                self._sync_shlyakh_field_state(preview)
            except Exception as exc:
                core.messagebox.showerror("Реєстр «Шлях»", str(exc), parent=self)
                return

            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Звірка ТЗ з реєстром «Шлях» — по полях", 1360, 820)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)

            plan = preview["plan"]
            parsed = preview["parsed"]
            new_count = sum(1 for row in plan if row["status"] == "new_registry")
            conflict_count = sum(1 for row in plan if row["status"] == "critical")
            core.ttk.Label(body, text="Ліцензійний реєстр «Шлях» — покомпонентна звірка", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=("Файл: %s  ·  рядків: %d  ·  нових ТЗ: %d  ·  критичних конфліктів: %d"
                      % (parsed["source_name"], len(plan), new_count, conflict_count)),
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(3, 5))
            core.ttk.Label(
                body,
                text=("Ліворуч — ТЗ, праворуч — кожне поле окремо. Зелений = відповідає; синій = можна доповнити; "
                      "жовтий = розбіжність; червоний = критичний ідентифікаційний конфлікт; сірий = реєстр цього поля не підтверджує. "
                      "Порожнє або відсутнє у витягу значення ніколи не очищає Taxo."),
                wraplength=1300, justify="left",
            ).pack(anchor="w", pady=(0, 8))

            pane = core.ttk.Panedwindow(body, orient="horizontal")
            pane.pack(fill="both", expand=True)
            left = core.ttk.Frame(pane, padding=(0, 0, 6, 0))
            right = core.ttk.Frame(pane, padding=(6, 0, 0, 0))
            pane.add(left, weight=2)
            pane.add(right, weight=3)

            left.rowconfigure(1, weight=1)
            left.columnconfigure(0, weight=1)
            core.ttk.Label(left, text="Транспортні засоби", style="SubTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 5))
            vehicle_tree = core.ttk.Treeview(
                left, columns=("state", "vehicle", "key", "registry"), show="headings", selectmode="browse"
            )
            for key, label, width in (
                ("state", "Стан", 135), ("vehicle", "ТЗ", 250),
                ("key", "Ключ", 70), ("registry", "Статус «Шлях»", 125),
            ):
                vehicle_tree.heading(key, text=label)
                vehicle_tree.column(key, width=width, anchor="w")
            vy = core.ttk.Scrollbar(left, orient="vertical", command=vehicle_tree.yview)
            vehicle_tree.configure(yscrollcommand=vy.set)
            vehicle_tree.grid(row=1, column=0, sticky="nsew")
            vy.grid(row=1, column=1, sticky="ns")
            for idx, row in enumerate(plan):
                vehicle_tree.insert(
                    "", "end", iid="p:%d" % idx,
                    values=(
                        _row_status_label(row["status"]), row["vehicle_name"], row["match_quality"],
                        row["item"].get("registry_status", "") or "—",
                    ), tags=(row["status"],),
                )
            for idx, row in enumerate(preview.get("local_only") or []):
                vehicle_tree.insert(
                    "", "end", iid="l:%d" % idx,
                    values=("Є лише в Taxo", row["vehicle_name"], "—", "—"), tags=("local_only",),
                )
            vehicle_tree.tag_configure("no_changes", foreground="#0B5D1E")
            vehicle_tree.tag_configure("fill", foreground="#005B96")
            vehicle_tree.tag_configure("new_registry", foreground="#005B96")
            vehicle_tree.tag_configure("difference", foreground="#7A5B00")
            vehicle_tree.tag_configure("critical", foreground="#8A1C1C")
            vehicle_tree.tag_configure("local_only", foreground="#666666")

            right.rowconfigure(2, weight=1)
            right.columnconfigure(0, weight=1)
            field_title = core.tk.StringVar(value="Поля — виберіть ТЗ")
            core.ttk.Label(right, textvariable=field_title, style="SubTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 3))
            field_hint = core.tk.StringVar(value="Рішення зберігаються між квартальними витягами.")
            core.ttk.Label(right, textvariable=field_hint, style="Muted.TLabel", wraplength=720, justify="left").grid(row=1, column=0, sticky="ew", pady=(0, 5))
            field_frame = core.ttk.Frame(right)
            field_frame.grid(row=2, column=0, sticky="nsew")
            field_frame.rowconfigure(0, weight=1)
            field_frame.columnconfigure(0, weight=1)
            fields = core.ttk.Treeview(
                field_frame, columns=("field", "taxo", "registry", "state", "decision"),
                show="headings", selectmode="browse",
            )
            for key, label, width in (
                ("field", "Поле", 210), ("taxo", "Taxo", 190), ("registry", "«Шлях»", 190),
                ("state", "Стан", 145), ("decision", "Рішення", 205),
            ):
                fields.heading(key, text=label)
                fields.column(key, width=width, anchor="w")
            fy = core.ttk.Scrollbar(field_frame, orient="vertical", command=fields.yview)
            fx = core.ttk.Scrollbar(field_frame, orient="horizontal", command=fields.xview)
            fields.configure(yscrollcommand=fy.set, xscrollcommand=fx.set)
            fields.grid(row=0, column=0, sticky="nsew")
            fy.grid(row=0, column=1, sticky="ns")
            fx.grid(row=1, column=0, sticky="ew")
            fields.tag_configure(reconciliation.STATE_MATCH, foreground="#0B5D1E")
            fields.tag_configure(reconciliation.STATE_FILL, foreground="#005B96")
            fields.tag_configure(reconciliation.STATE_DIFFERENCE, foreground="#7A5B00")
            fields.tag_configure(reconciliation.STATE_CRITICAL, foreground="#8A1C1C")
            fields.tag_configure(reconciliation.STATE_UNAVAILABLE, foreground="#666666")

            selected_vehicle_id = {"value": None}

            def load_fields(vehicle_id):
                selected_vehicle_id["value"] = vehicle_id
                for item_id in fields.get_children(""):
                    fields.delete(item_id)
                if vehicle_id is None:
                    return
                con = core.db()
                try:
                    rows = reconciliation.current_fields(con, vehicle_id=vehicle_id)
                finally:
                    con.close()
                for row in rows:
                    decision = reconciliation.DECISION_LABELS.get(row["decision"], row["decision"] or "—")
                    fields.insert(
                        "", "end", iid=row["field_name"],
                        values=(
                            vehicle_registry.FIELD_LABELS.get(row["field_name"], row["field_name"]),
                            row["local_value"] or "—", row["registry_value"] or "—",
                            reconciliation.STATE_LABELS.get(row["state"], row["state"]), decision,
                        ), tags=(row["state"],),
                    )

            def vehicle_selected(_event=None):
                selection = vehicle_tree.selection()
                if not selection:
                    return
                iid = selection[0]
                if iid.startswith("l:"):
                    idx = int(iid.split(":", 1)[1])
                    row = preview["local_only"][idx]
                    field_title.set("Поля — %s" % row["vehicle_name"])
                    field_hint.set("Є у Taxo, але немає у цьому витягу. Нічого не видаляється і не деактивується.")
                    load_fields(None)
                    return
                idx = int(iid.split(":", 1)[1])
                row = plan[idx]
                field_title.set("Поля — %s" % row["vehicle_name"])
                if row["vehicle_id"] is None:
                    field_hint.set("Нова/конфліктна картка: спочатку потрібно однозначно зіставити або створити ТЗ.")
                    load_fields(None)
                else:
                    field_hint.set("VIN і державний номер — ідентифікаційні поля; їх розбіжність виділяється червоним і потребує явного рішення.")
                    load_fields(int(row["vehicle_id"]))

            vehicle_tree.bind("<<TreeviewSelect>>", vehicle_selected)
            if vehicle_tree.get_children(""):
                first = vehicle_tree.get_children("")[0]
                vehicle_tree.selection_set(first)
                vehicle_tree.focus(first)
                vehicle_selected()

            decision_bar = core.ttk.Frame(right)
            decision_bar.grid(row=3, column=0, sticky="ew", pady=(8, 0))

            def chosen_field():
                vehicle_id = selected_vehicle_id["value"]
                selection = fields.selection()
                if vehicle_id is None or not selection:
                    core.messagebox.showinfo("Звірка «Шлях»", "Виберіть ТЗ і конкретне поле.", parent=win)
                    return None, None
                return vehicle_id, selection[0]

            def set_field_decision(decision):
                vehicle_id, field_name = chosen_field()
                if vehicle_id is None:
                    return
                con = core.db()
                try:
                    reconciliation.set_decision(con, vehicle_id, field_name, decision)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Звірка «Шлях»", str(exc), parent=win)
                    return
                finally:
                    con.close()
                load_fields(vehicle_id)

            def accept_field():
                vehicle_id, field_name = chosen_field()
                if vehicle_id is None:
                    return
                if field_name in reconciliation.CRITICAL_FIELDS:
                    if not core.messagebox.askyesno(
                        "Ідентифікаційне поле",
                        "Це ідентифікаційне поле ТЗ. Прийняти значення державного реєстру в Taxo?",
                        parent=win,
                    ):
                        return
                con = core.db()
                try:
                    reconciliation.accept_registry_value(con, vehicle_id, field_name)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Звірка «Шлях»", str(exc), parent=win)
                    return
                finally:
                    con.close()
                try:
                    self.load_vehicles()
                except Exception:
                    pass
                load_fields(vehicle_id)

            def show_history():
                vehicle_id, field_name = chosen_field()
                if vehicle_id is None:
                    return
                con = core.db()
                try:
                    rows = reconciliation.history(con, vehicle_id, field_name)
                finally:
                    con.close()
                hist = core.tk.Toplevel(win)
                _configure_window(core, hist, "Історія рішення — %s" % vehicle_registry.FIELD_LABELS.get(field_name, field_name), 960, 520)
                frame = core.ttk.Frame(hist, padding=10)
                frame.pack(fill="both", expand=True)
                tree = core.ttk.Treeview(frame, columns=("date", "state", "decision", "taxo", "registry", "note"), show="headings")
                for key, label, width in (
                    ("date", "Дата", 155), ("state", "Стан", 130), ("decision", "Рішення", 190),
                    ("taxo", "Taxo", 150), ("registry", "«Шлях»", 150), ("note", "Примітка", 260),
                ):
                    tree.heading(key, text=label); tree.column(key, width=width, anchor="w")
                tree.pack(fill="both", expand=True)
                for row in rows:
                    tree.insert("", "end", values=(
                        row["created_at"], reconciliation.STATE_LABELS.get(row["state"], row["state"]),
                        reconciliation.DECISION_LABELS.get(row["decision"], row["decision"]),
                        row["local_value"] or "—", row["registry_value"] or "—", row["note"] or "—",
                    ))

            core.ttk.Button(decision_bar, text="Прийняти реєстр", command=accept_field).pack(side="left", padx=(0, 4))
            core.ttk.Button(decision_bar, text="Залишити Taxo", command=lambda: set_field_decision(reconciliation.DECISION_KEEP_TAXO)).pack(side="left", padx=4)
            core.ttk.Button(decision_bar, text="Виправити у реєстрі", command=lambda: set_field_decision(reconciliation.DECISION_FIX_REGISTRY)).pack(side="left", padx=4)
            core.ttk.Button(decision_bar, text="Відкласти", command=lambda: set_field_decision(reconciliation.DECISION_DEFER)).pack(side="left", padx=4)
            core.ttk.Button(decision_bar, text="Історія поля", command=show_history).pack(side="left", padx=4)

            bottom = core.ttk.LabelFrame(body, text="Масове безпечне застосування / нові картки", padding=(8, 6))
            bottom.pack(fill="x", pady=(9, 0))
            mode_var = core.tk.StringVar(value=vehicle_registry.IMPORT_FILL_EMPTY)
            create_var = core.tk.BooleanVar(value=True)
            mode_row = core.ttk.Frame(bottom); mode_row.pack(fill="x")
            for value, label in (
                (vehicle_registry.IMPORT_COMPARE, "Лише звірити"),
                (vehicle_registry.IMPORT_FILL_EMPTY, "Доповнити порожні"),
                (vehicle_registry.IMPORT_UPDATE, "Оновити непорожні + доповнити"),
            ):
                core.ttk.Radiobutton(mode_row, text=label, variable=mode_var, value=value).pack(side="left", padx=(0, 12))
            core.ttk.Checkbutton(bottom, text="Створити відсутні картки ТЗ після підтвердження", variable=create_var).pack(anchor="w", pady=(4, 0))
            action_row = core.ttk.Frame(bottom); action_row.pack(fill="x", pady=(6, 0))

            def apply_import():
                mode = mode_var.get()
                create_new = bool(create_var.get() and mode != vehicle_registry.IMPORT_COMPARE)
                warning = (
                    "Режим: %s\nСтворити нові ТЗ: %s.\n\n"
                    "Порожні/відсутні значення не очищають Taxo. «Знятий з обліку» не вимикає ТЗ."
                    % (vehicle_registry.IMPORT_MODE_LABELS[mode], "так" if create_new else "ні")
                )
                if mode == vehicle_registry.IMPORT_UPDATE:
                    warning += "\n\nУВАГА: цей режим замінить усі непорожні розбіжні поля даними реєстру. Для вибіркового рішення використовуйте кнопки праворуч."
                if not core.messagebox.askyesno("Застосувати дані «Шлях»?", warning, parent=win):
                    return
                try:
                    result = vehicle_registry.apply_registry_import(core, preview, mode=mode, create_new=create_new)
                    fresh = vehicle_registry.preview_registry_import(core, preview["path"])
                    self._sync_shlyakh_field_state(fresh)
                except Exception as exc:
                    core.messagebox.showerror("Реєстр «Шлях»", str(exc), parent=win)
                    return
                try:
                    self.load_vehicles()
                except Exception:
                    pass
                try:
                    self._refresh_shlyakh_quarter_status()
                except Exception:
                    pass
                core.messagebox.showinfo(
                    "Звірку «Шлях» завершено",
                    "Рядків: %d\nЗіставлено: %d\nСтворено: %d\nОновлено: %d\nКритичних: %d\nЄ лише в Taxo: %d"
                    % (result["total"], result["matched"], result["created"], result["updated"], result["conflicts"], result["local_only"]),
                    parent=win,
                )
                win.destroy()

            core.ttk.Button(action_row, text="Закрити", command=win.destroy).pack(side="right", padx=(6, 0))
            core.ttk.Button(action_row, text="Виконати звірку", style="Accent.TButton", command=apply_import).pack(side="right")
            win.transient(self)

        def open_selected_vehicle_registry_data(self):
            vehicle = self.selected_vehicle() if hasattr(self, "selected_vehicle") else None
            if vehicle is None:
                core.messagebox.showinfo("Транспорт", "Виберіть транспортний засіб.", parent=self)
                return
            con = core.db()
            try:
                reconciliation.ensure_schema_on_connection(con)
                rows = reconciliation.current_fields(con, vehicle_id=vehicle["id"])
                current = vehicle_registry.vehicle_registry_data(con, vehicle["id"])
            finally:
                con.close()
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Дані «Шлях» — %s" % (vehicle["plate"] or vehicle["name"]), 1120, 680)
            core.ttk.Label(
                win,
                text="Реєстрові/ліцензійні дані та останній стан покомпонентної звірки. Локальні документи ТЗ і військово-транспортний облік — окремі контури.",
                wraplength=1060, justify="left",
            ).pack(anchor="w", padx=12, pady=(12, 6))
            frame = core.ttk.Frame(win); frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
            tree = core.ttk.Treeview(frame, columns=("field", "taxo", "registry", "state", "decision"), show="headings")
            for key, label, width in (
                ("field", "Поле", 250), ("taxo", "Taxo", 220), ("registry", "Останній витяг", 220),
                ("state", "Стан", 155), ("decision", "Рішення", 220),
            ):
                tree.heading(key, text=label); tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sy.set)
            tree.grid(row=0, column=0, sticky="nsew"); sy.grid(row=0, column=1, sticky="ns")
            by_field = {row["field_name"]: row for row in rows}
            for field_name, label in vehicle_registry.FIELD_LABELS.items():
                row = by_field.get(field_name)
                if row is None:
                    tree.insert("", "end", values=(label, (current or {}).get(field_name, "") or "—", "—", "Не звірялося", "—"))
                    continue
                tree.insert("", "end", values=(
                    label, row["local_value"] or "—", row["registry_value"] or "—",
                    reconciliation.STATE_LABELS.get(row["state"], row["state"]),
                    reconciliation.DECISION_LABELS.get(row["decision"], row["decision"] or "—"),
                ), tags=(row["state"],))
            tree.tag_configure(reconciliation.STATE_MATCH, foreground="#0B5D1E")
            tree.tag_configure(reconciliation.STATE_FILL, foreground="#005B96")
            tree.tag_configure(reconciliation.STATE_DIFFERENCE, foreground="#7A5B00")
            tree.tag_configure(reconciliation.STATE_CRITICAL, foreground="#8A1C1C")
            tree.tag_configure(reconciliation.STATE_UNAVAILABLE, foreground="#666666")
            win.transient(self)

    core._TAXO_1052_INSTALLED = True
    core.App = Taxo1052App
    return Taxo1052App
