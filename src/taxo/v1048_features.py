# -*- coding: utf-8 -*-
"""Taxo 10.4-r8 — state-registry enrichment, «Шлях» and employee reminders."""
from __future__ import annotations

from datetime import date, datetime

import employee_reminders as reminders
import personnel_registry as personnel_registry
import vehicle_registry

APP_VERSION = "10.4-r8"


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _find_button(root, text):
    if not _alive(root):
        return None
    for widget in _walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == text:
                return widget
        except Exception:
            pass
    return None


def _text(value):
    return str(value or "").strip()


def _configure_window(core, win, title, width=1100, height=720):
    win.title(title)
    try:
        core.fit_window_to_screen(win, width, height, min(width, 760), min(height, 500))
    except Exception:
        win.geometry("%dx%d" % (width, height))
        win.minsize(min(width, 760), min(height, 500))
    try:
        core.configure_toplevel(win, title=title, minsize=(min(width, 760), min(height, 500)))
    except Exception:
        pass


def _vehicle_status_label(status):
    return {
        "no_changes": "Відповідає",
        "fill": "Доповнити",
        "difference": "Розбіжність",
        "critical": "Критичний конфлікт",
        "new_registry": "Нове в реєстрі",
        "local_only": "Є лише в Taxo",
    }.get(status, status)


def _employee_status_label(status):
    return {
        "update": "Оновити / доповнити",
        "no_changes": "Відповідає",
        "unmatched": "Нова картка",
        "ambiguous": "Неоднозначно",
        "conflict": "Конфлікт",
        "local_only": "Є лише в Taxo",
    }.get(status, status)


def _create_unmatched_employees(core, preview):
    """Create only rows explicitly marked as unmatched in the preview.

    The function intentionally does not assign roles (including Driver).  It creates
    the employee card and fills every non-empty field that the registry actually
    supplied.  Ambiguous/conflicting rows are never created automatically.
    """
    parsed = preview["parsed"]
    now = datetime.now().isoformat(timespec="seconds")
    con = core.db()
    created = 0
    try:
        personnel_registry.ensure_schema_on_connection(con)
        for row_plan in preview["plan"]:
            if row_plan.get("status") != "unmatched":
                continue
            item = row_plan["item"]
            last = _text(item.get("last_name"))
            first = _text(item.get("first_name"))
            middle = _text(item.get("middle_name"))
            if not last or not first:
                continue

            rnokpp = _text(item.get("personal", {}).get("rnokpp"))
            if rnokpp:
                duplicate = con.execute("SELECT id FROM employees WHERE rnokpp=? LIMIT 1", (rnokpp,)).fetchone()
                if duplicate:
                    continue
            duplicate = con.execute(
                """SELECT id FROM employees
                   WHERE lower(trim(last_name))=lower(trim(?))
                     AND lower(trim(first_name))=lower(trim(?))
                     AND lower(trim(COALESCE(middle_name,'')))=lower(trim(?))
                   LIMIT 1""",
                (last, first, middle),
            ).fetchone()
            if duplicate:
                continue

            cur = con.execute(
                """INSERT INTO employees(last_name,first_name,middle_name,active,created_at)
                   VALUES(?,?,?,1,?)""",
                (last, first, middle, now),
            )
            employee_id = int(cur.lastrowid)
            personal = {k:_text(v) for k,v in item.get("personal", {}).items() if _text(v)}
            if personal:
                con.execute(
                    "UPDATE employees SET " + ", ".join(key + "=?" for key in personal) + " WHERE id=?",
                    list(personal.values()) + [employee_id],
                )
            con.execute("INSERT OR IGNORE INTO employee_military_profile(employee_id) VALUES(?)", (employee_id,))
            military = {k:_text(v) for k,v in item.get("military", {}).items() if _text(v)}
            if military:
                con.execute(
                    "UPDATE employee_military_profile SET "
                    + ", ".join(key + "=?" for key in military)
                    + ", last_source_kind=?,last_source_name=?,last_verified_at=?,updated_at=? WHERE employee_id=?",
                    list(military.values()) + [
                        parsed["source_kind"], parsed["source_name"], now, now, employee_id,
                    ],
                )
            else:
                con.execute(
                    """UPDATE employee_military_profile
                       SET last_source_kind=?,last_source_name=?,last_verified_at=?,updated_at=?
                       WHERE employee_id=?""",
                    (parsed["source_kind"], parsed["source_name"], now, now, employee_id),
                )
            for doc in item.get("documents", []):
                personnel_registry._upsert_document_hint(
                    con, employee_id, doc, parsed["source_kind"], parsed["source_name"], now
                )
            created += 1
        con.commit()
        return created
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def install(core, base_app):
    if getattr(core, "_TAXO_1048_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1048App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            vehicle_registry.ensure_schema(core)
            reminders.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_r8_actions()
            self.after(700, self._show_birthday_popup_if_due)

        # ------------------------------------------------------------------
        # Actions / buttons
        # ------------------------------------------------------------------
        def _install_r8_actions(self):
            if not getattr(self, "_r8_vehicle_actions_installed", False):
                anchor = _find_button(getattr(self, "tab_vehicles", None), "Контроль документів")
                if anchor is not None:
                    parent = anchor.master
                    self._shlyakh_button = core.ttk.Button(
                        parent, text="Реєстр «Шлях»: потрібне звіряння…",
                        command=self.import_shlyakh_registry,
                    )
                    self._shlyakh_button.pack(side="left", padx=4)
                    core.ttk.Button(
                        parent, text="Дані «Шлях»", command=self.open_selected_vehicle_registry_data
                    ).pack(side="left", padx=4)
                    self._r8_vehicle_actions_installed = True
                    self._refresh_shlyakh_quarter_status()

            if not getattr(self, "_r8_birthday_actions_installed", False):
                root = getattr(self, "personnel_overview_page", None)
                anchor = _find_button(root, "Новий працівник")
                if anchor is not None:
                    parent = anchor.master
                    self._birthday_button = core.ttk.Button(
                        parent, text="Дні народження", command=self.open_birthday_reminders
                    )
                    self._birthday_button.pack(side="right", padx=(8,0))
                    self._r8_birthday_actions_installed = True
                    self._refresh_birthday_button()

        # ------------------------------------------------------------------
        # Birthday reminders
        # ------------------------------------------------------------------
        def _refresh_birthday_button(self):
            button = getattr(self, "_birthday_button", None)
            if not _alive(button):
                return
            con = core.db()
            try:
                due = reminders.due_birthday_reminders(con, today=date.today())
            finally:
                con.close()
            button.configure(text="Дні народження (%d)" % len(due) if due else "Дні народження")

        def _show_birthday_popup_if_due(self):
            con = core.db()
            try:
                due = reminders.unseen_due_birthday_reminders(con, today=date.today())
                if due:
                    reminders.mark_reminders_shown(con, due, today=date.today())
                    con.commit()
            finally:
                con.close()
            self._refresh_birthday_button()
            if due:
                core.messagebox.showinfo(
                    "Нагадування — дні народження",
                    reminders.birthday_summary_text(due),
                    parent=self,
                )

        def open_birthday_reminders(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Дні народження працівників", 850, 560)
            head = core.ttk.Frame(win, padding=(12,10)); head.pack(fill="x")
            core.ttk.Label(head, text="Найближчі дні народження", style="Title.TLabel").pack(side="left")
            core.ttk.Label(
                win,
                text="Taxo нагадує за 5 днів, за 1 день і в день народження. Джерело дати — єдине поле картки працівника, у тому числі заповнене з держреєстру.",
                wraplength=800, justify="left",
            ).pack(fill="x", padx=12, pady=(0,8))
            frame = core.ttk.Frame(win); frame.pack(fill="both", expand=True, padx=12, pady=(0,12))
            frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
            cols = ("employee", "birth", "next", "days", "age")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings")
            for key,label,width in (
                ("employee","Працівник",300),("birth","Дата народження",120),
                ("next","Найближча дата",120),("days","Залишилось",120),("age","Виповниться",100),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sy.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns")
            con = core.db()
            try:
                rows = reminders.collect_birthdays(con, today=date.today(), max_days=30)
            finally:
                con.close()
            for row in rows:
                days = row["days_until"]
                when = "сьогодні" if days == 0 else ("завтра" if days == 1 else "%d дн." % days)
                tag = "today" if days == 0 else ("due" if days in (1,5) else "normal")
                tree.insert("","end",values=(
                    row["employee_name"],
                    datetime.fromisoformat(row["birth_date"]).strftime("%d.%m.%Y"),
                    datetime.fromisoformat(row["birthday_date"]).strftime("%d.%m.%Y"),
                    when,row["age"],
                ),tags=(tag,))
            tree.tag_configure("today",foreground="#8A1C1C")
            tree.tag_configure("due",foreground="#7A5B00")
            if not rows:
                tree.insert("","end",values=("Немає днів народження в найближчі 30 днів","","","",""))
            win.transient(self)

        # ------------------------------------------------------------------
        # Employee registry: create missing cards from the official extract
        # ------------------------------------------------------------------
        def _show_registry_import_preview(self, preview):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Звірка працівників з держреєстром", 1140, 730)
            body = core.ttk.Frame(win, padding=14); body.pack(fill="both", expand=True)
            parsed = preview["parsed"]; plan = preview["plan"]
            new_rows = sum(1 for row in plan if row["status"] == "unmatched")
            conflicts = sum(1 for row in plan if row["status"] in ("ambiguous","conflict"))
            core.ttk.Label(body, text="Державний реєстр працівників", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=("Файл: %s  ·  рядків: %d  ·  нових карток: %d  ·  конфліктних/неоднозначних: %d"
                      % (parsed["source_name"], len(plan), new_rows, conflicts)),
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(4,8))
            core.ttk.Label(
                body,
                text=("Реєстр використовується для автоматичного наповнення Taxo. Якщо офіційний витяг має поле, якого раніше не було в картці, Taxo зберігає його у розширеній моделі. "
                      "Відсутні у витягу локальні дані не видаляються."),
                wraplength=1080,justify="left",
            ).pack(anchor="w",pady=(0,8))

            mode_var = core.tk.StringVar(value=personnel_registry.IMPORT_FILL_EMPTY)
            create_var = core.tk.BooleanVar(value=True)
            modes = core.ttk.LabelFrame(body,text="Застосування",padding=(8,5)); modes.pack(fill="x",pady=(0,8))
            for value,label in (
                (personnel_registry.IMPORT_COMPARE,"Лише звірити — не змінювати Taxo"),
                (personnel_registry.IMPORT_FILL_EMPTY,"Доповнити — заповнити порожні поля"),
                (personnel_registry.IMPORT_UPDATE,"Оновити — прийняти непорожні дані реєстру + доповнити"),
            ):
                core.ttk.Radiobutton(modes,text=label,variable=mode_var,value=value).pack(anchor="w",pady=1)
            core.ttk.Checkbutton(
                modes, text="Створити відсутні картки працівників з даних реєстру (після підтвердження)",
                variable=create_var,
            ).pack(anchor="w",pady=(5,0))

            frame=core.ttk.Frame(body); frame.pack(fill="both",expand=True)
            frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            cols=("status","employee","match","changes","notes")
            tree=core.ttk.Treeview(frame,columns=cols,show="headings")
            for key,label,width in (
                ("status","Стан",150),("employee","Працівник",270),("match","Зіставлення",100),
                ("changes","Дані реєстру / зміни",400),("notes","Примітка",300),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
            sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
            tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
            for idx,row in enumerate(plan):
                fields = ", ".join(dict.fromkeys(change["label"] for change in row.get("changes",[])))
                if row["status"] == "unmatched":
                    supplied = list(row["item"].get("personal",{})) + list(row["item"].get("military",{}))
                    fields = ", ".join(personnel_registry.EMPLOYEE_FIELD_LABELS.get(x, personnel_registry.MILITARY_FIELD_LABELS.get(x,x)) for x in supplied if _text(row["item"].get("personal",{}).get(x) or row["item"].get("military",{}).get(x)))
                tree.insert("","end",iid=str(idx),values=(
                    _employee_status_label(row["status"]),row["employee_name"],row["match_quality"],fields or "—",
                    "; ".join(row.get("notes") or []) or "—",
                ),tags=(row["status"],))
            for row in preview.get("local_only",[]):
                tree.insert("","end",values=("Є лише в Taxo",row["employee_name"],"—","—",row["note"]),tags=("local_only",))
            tree.tag_configure("no_changes",foreground="#0B5D1E")
            tree.tag_configure("update",foreground="#7A5B00")
            tree.tag_configure("unmatched",foreground="#005B96")
            tree.tag_configure("ambiguous",foreground="#8A1C1C")
            tree.tag_configure("conflict",foreground="#8A1C1C")
            tree.tag_configure("local_only",foreground="#666666")
            actions=core.ttk.Frame(body); actions.pack(fill="x",pady=(10,0))

            def apply_import():
                mode = mode_var.get()
                will_create = bool(create_var.get() and mode != personnel_registry.IMPORT_COMPARE)
                if not core.messagebox.askyesno(
                    "Застосувати дані реєстру?",
                    ("Режим: %s\nСтворити відсутні картки: %s (%d).\n\n"
                     "Порожні/відсутні у витягу поля НЕ очищають Taxo. Конфліктні та неоднозначні записи не застосовуються автоматично. Продовжити?"
                     % (personnel_registry.IMPORT_MODE_LABELS[mode], "так" if will_create else "ні", new_rows)),
                    parent=win,
                ):
                    return
                try:
                    created = _create_unmatched_employees(core, preview) if will_create else 0
                    actual_preview = personnel_registry.preview_registry_import(core, preview["path"]) if created else preview
                    result = personnel_registry.apply_registry_import(core, actual_preview, mode=mode)
                except Exception as exc:
                    core.messagebox.showerror("Реєстр працівників",str(exc),parent=win); return
                refresh=getattr(self,"_refresh_personnel_overview",None)
                if callable(refresh): refresh()
                refresh_q=getattr(self,"_refresh_personnel_registry_quarter_status",None)
                if callable(refresh_q): refresh_q()
                self._refresh_birthday_button()
                core.messagebox.showinfo(
                    "Звірку завершено",
                    ("Створено нових карток: %d\nЗіставлено: %d\nЗмінено: %d\nПропущено: %d\nЄ лише в Taxo: %d"
                     % (created,result["matched"],result["updated"],result["skipped"],result["local_only"])),
                    parent=win,
                )
                win.destroy()

            core.ttk.Button(actions,text="Закрити",command=win.destroy).pack(side="right",padx=(6,0))
            core.ttk.Button(actions,text="Виконати звірку",style="Accent.TButton",command=apply_import).pack(side="right")
            win.transient(self)

        # ------------------------------------------------------------------
        # «Шлях» vehicle registry
        # ------------------------------------------------------------------
        def _refresh_shlyakh_quarter_status(self):
            button = getattr(self,"_shlyakh_button",None)
            if not _alive(button):
                return
            con=core.db()
            try:
                status=vehicle_registry.registry_quarter_status(con)
            finally:
                con.close()
            if status["current"]:
                button.configure(text="Реєстр «Шлях»: актуально %s…" % status["quarter"])
            else:
                button.configure(text="Реєстр «Шлях»: потрібне звіряння %s…" % status["quarter"])

        def import_shlyakh_registry(self):
            path=core.filedialog.askopenfilename(
                parent=self,title="Імпорт транспортних засобів з реєстру «Шлях»",
                filetypes=(("Excel / CSV","*.xlsx *.csv"),("Excel XLSX","*.xlsx"),("CSV","*.csv"),("Усі файли","*.*")),
            )
            if not path:
                return
            try:
                preview=vehicle_registry.preview_registry_import(core,path)
            except Exception as exc:
                core.messagebox.showerror("Реєстр «Шлях»",str(exc),parent=self); return
            self._show_shlyakh_preview(preview)

        def _show_shlyakh_preview(self,preview):
            win=core.tk.Toplevel(self)
            _configure_window(core,win,"Звірка ТЗ з реєстром «Шлях»",1220,760)
            body=core.ttk.Frame(win,padding=14); body.pack(fill="both",expand=True)
            plan=preview["plan"]; parsed=preview["parsed"]
            new_count=sum(1 for row in plan if row["status"]=="new_registry")
            diff_count=sum(1 for row in plan if row["status"]=="difference")
            conflict_count=sum(1 for row in plan if row["status"]=="critical")
            core.ttk.Label(body,text="Ліцензійний реєстр «Шлях»",style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,text=("Файл: %s  ·  рядків: %d  ·  нових ТЗ: %d  ·  розбіжностей: %d  ·  критичних конфліктів: %d"
                           % (parsed["source_name"],len(plan),new_count,diff_count,conflict_count)),
                style="Muted.TLabel",
            ).pack(anchor="w",pady=(4,8))
            core.ttk.Label(
                body,
                text=("Дані «Шлях» доповнюють робочу базу Taxo і показують, що держава знає про ліцензійну справу. "
                      "Вони не мають відношення до локального контролю страхування, техконтролю, техпаспортів чи тахографічних документів. "
                      "Якщо рядка/поля немає у витягу, локальні дані не видаляються."),
                wraplength=1160,justify="left",
            ).pack(anchor="w",pady=(0,8))
            mode_var=core.tk.StringVar(value=vehicle_registry.IMPORT_FILL_EMPTY)
            create_var=core.tk.BooleanVar(value=True)
            modes=core.ttk.LabelFrame(body,text="Застосування",padding=(8,5)); modes.pack(fill="x",pady=(0,8))
            for value,label in (
                (vehicle_registry.IMPORT_COMPARE,"Лише звірити — не змінювати Taxo"),
                (vehicle_registry.IMPORT_FILL_EMPTY,"Доповнити — заповнити порожні поля"),
                (vehicle_registry.IMPORT_UPDATE,"Оновити — прийняти непорожні дані «Шлях» + доповнити"),
            ):
                core.ttk.Radiobutton(modes,text=label,variable=mode_var,value=value).pack(anchor="w",pady=1)
            core.ttk.Checkbutton(
                modes,text="Створити відсутні картки ТЗ з даних «Шлях» (після підтвердження)",variable=create_var
            ).pack(anchor="w",pady=(5,0))

            frame=core.ttk.Frame(body); frame.pack(fill="both",expand=True)
            frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            cols=("state","vehicle","match","changes","registry_status","notes")
            tree=core.ttk.Treeview(frame,columns=cols,show="headings")
            for key,label,width in (
                ("state","Стан",150),("vehicle","ТЗ",260),("match","Ключ",90),
                ("changes","Поля / розбіжності",420),("registry_status","Статус «Шлях»",150),("notes","Примітка",300),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
            sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
            tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
            for idx,row in enumerate(plan):
                fields=", ".join(dict.fromkeys(change["label"] for change in row.get("changes",[])))
                if row["status"]=="new_registry":
                    fields=", ".join(vehicle_registry.FIELD_LABELS.get(k,k) for k,v in row["item"].items() if k in vehicle_registry.FIELD_LABELS and _text(v))
                tree.insert("","end",iid=str(idx),values=(
                    _vehicle_status_label(row["status"]),row["vehicle_name"],row["match_quality"],fields or "—",
                    row["item"].get("registry_status","") or "—","; ".join(row.get("notes") or []) or "—",
                ),tags=(row["status"],))
            for row in preview.get("local_only",[]):
                tree.insert("","end",values=("Є лише в Taxo",row["vehicle_name"],"—","—","—",row["note"]),tags=("local_only",))
            tree.tag_configure("no_changes",foreground="#0B5D1E")
            tree.tag_configure("fill",foreground="#005B96")
            tree.tag_configure("new_registry",foreground="#005B96")
            tree.tag_configure("difference",foreground="#7A5B00")
            tree.tag_configure("critical",foreground="#8A1C1C")
            tree.tag_configure("local_only",foreground="#666666")
            actions=core.ttk.Frame(body); actions.pack(fill="x",pady=(10,0))

            def apply_import():
                mode=mode_var.get(); create_new=bool(create_var.get() and mode!=vehicle_registry.IMPORT_COMPARE)
                if not core.messagebox.askyesno(
                    "Застосувати дані «Шлях»?",
                    ("Режим: %s\nСтворити нові картки ТЗ: %s (%d).\n\n"
                     "«Знятий з обліку» зберігається як окремий реєстровий статус і НЕ вимикає наявний ТЗ у Taxo. "
                     "Порожні/відсутні у витягу дані не очищають нашу базу. Продовжити?"
                     % (vehicle_registry.IMPORT_MODE_LABELS[mode],"так" if create_new else "ні",new_count)),
                    parent=win,
                ):
                    return
                try:
                    result=vehicle_registry.apply_registry_import(core,preview,mode=mode,create_new=create_new)
                except Exception as exc:
                    core.messagebox.showerror("Реєстр «Шлях»",str(exc),parent=win); return
                try: self.load_vehicles()
                except Exception: pass
                self._refresh_shlyakh_quarter_status()
                core.messagebox.showinfo(
                    "Звірку «Шлях» завершено",
                    ("Рядків: %d\nЗіставлено: %d\nСтворено ТЗ: %d\nОновлено: %d\nКритичних конфліктів: %d\nПропущено: %d\nЄ лише в Taxo: %d"
                     % (result["total"],result["matched"],result["created"],result["updated"],result["conflicts"],result["skipped"],result["local_only"])),
                    parent=win,
                )
                win.destroy()

            core.ttk.Button(actions,text="Закрити",command=win.destroy).pack(side="right",padx=(6,0))
            core.ttk.Button(actions,text="Виконати звірку",style="Accent.TButton",command=apply_import).pack(side="right")
            win.transient(self)

        def open_selected_vehicle_registry_data(self):
            vehicle = self.selected_vehicle() if hasattr(self,"selected_vehicle") else None
            if vehicle is None:
                core.messagebox.showinfo("Транспорт","Виберіть транспортний засіб.",parent=self); return
            con=core.db()
            try:
                data=vehicle_registry.vehicle_registry_data(con,vehicle["id"])
            finally:
                con.close()
            win=core.tk.Toplevel(self)
            _configure_window(core,win,"Дані «Шлях» — %s" % (vehicle["plate"] or vehicle["name"]),860,620)
            core.ttk.Label(
                win,text="Реєстрові / ліцензійні дані. Локальні документи ТЗ контролюються окремо.",
                wraplength=810,justify="left",
            ).pack(anchor="w",padx=12,pady=(12,6))
            frame=core.ttk.Frame(win); frame.pack(fill="both",expand=True,padx=12,pady=(0,12))
            frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            tree=core.ttk.Treeview(frame,columns=("field","value"),show="headings")
            tree.heading("field",text="Поле"); tree.heading("value",text="Значення Taxo")
            tree.column("field",width=320,anchor="w"); tree.column("value",width=500,anchor="w")
            sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=sy.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns")
            for field,label in vehicle_registry.FIELD_LABELS.items():
                tree.insert("","end",values=(label,(data or {}).get(field,"") or "—"))
            tree.insert("","end",values=("Останнє джерело",(data or {}).get("registry_last_source_name","") or "—"))
            verified=(data or {}).get("registry_last_verified_at","") or ""
            tree.insert("","end",values=("Останнє підтвердження",verified or "—"))
            win.transient(self)

    core._TAXO_1048_INSTALLED=True
    core.App=Taxo1048App
    return Taxo1048App
