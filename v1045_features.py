# -*- coding: utf-8 -*-
"""Taxo 10.4-r5: employee data center, registry import and document register UI."""
from __future__ import annotations

from pathlib import Path

import personnel_registry as registry

APP_VERSION = "10.4-r5"


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
    for widget in _walk(root):
        try:
            if widget.winfo_class() in ("TButton","Button") and str(widget.cget("text"))==text:
                return widget
        except Exception:
            pass
    return None


def _selected_employee_id(app):
    tree=getattr(app,"personnel_overview_tree",None)
    if not _alive(tree) or not tree.selection():
        return None
    try:
        return int(tree.selection()[0])
    except Exception:
        return None


def _source_label(kind):
    return {
        registry.SOURCE_DETAILED:"Відомості персонального обліку",
        registry.SOURCE_SUMMARY:"Відомості про працівників",
    }.get(kind,kind or "Невідоме джерело")


def _status_label(status):
    return {
        "update":"Оновити",
        "no_changes":"Без змін",
        "unmatched":"Не знайдено",
        "ambiguous":"Неоднозначно",
        "conflict":"Конфлікт",
    }.get(status,status)


def _match_label(kind):
    return {
        "rnokpp":"РНОКПП",
        "name":"ПІБ",
        "unmatched":"—",
        "ambiguous":"—",
        "conflict":"—",
    }.get(kind,kind or "—")


def _configure_window(core, win, title, width=980, height=680):
    win.title(title)
    win.geometry("%dx%d" % (width,height))
    win.minsize(min(width,760),min(height,520))
    try:
        core.configure_toplevel(win,title=title,minsize=(min(width,760),min(height,520)))
    except Exception:
        pass


def _kv_tree(core, parent):
    frame=core.ttk.Frame(parent)
    frame.pack(fill="both",expand=True,padx=10,pady=10)
    frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
    tree=core.ttk.Treeview(frame,columns=("field","value"),show="headings")
    tree.heading("field",text="Поле"); tree.heading("value",text="Значення")
    tree.column("field",width=310,anchor="w"); tree.column("value",width=610,anchor="w")
    sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
    sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
    tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
    tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
    return tree


def _fill_kv(tree, rows):
    for iid in tree.get_children():
        tree.delete(iid)
    for label,value in rows:
        tree.insert("","end",values=(label,value or "—"))


def _document_editor(app, core, employee_id, row=None, on_saved=None):
    win=core.tk.Toplevel(app)
    _configure_window(core,win,"Документ працівника",760,590)
    body=core.ttk.Frame(win,padding=14); body.pack(fill="both",expand=True)
    body.columnconfigure(1,weight=1)
    values={key:core.tk.StringVar(value="") for key in (
        "doc_type","series","number","issue_date","expiry_date","issuer","file_path"
    )}
    notes_var=core.tk.StringVar(value="")
    if row is not None:
        for key,var in values.items():
            try: var.set(row[key] or "")
            except Exception: pass
        try: notes_var.set(row["notes"] or "")
        except Exception: pass
    labels=(
        ("Тип документа","doc_type"),("Серія","series"),("Номер","number"),
        ("Дата видачі (ДД.ММ.РРРР)","issue_date"),("Чинний до (ДД.ММ.РРРР)","expiry_date"),
        ("Ким виданий","issuer"),("Файл / посилання","file_path"),
    )
    for r,(label,key) in enumerate(labels):
        core.ttk.Label(body,text=label).grid(row=r,column=0,sticky="nw",padx=(0,8),pady=5)
        if key=="doc_type":
            widget=core.ttk.Combobox(body,textvariable=values[key],values=registry.DOCUMENT_TYPES,state="normal")
        else:
            widget=core.ttk.Entry(body,textvariable=values[key])
        widget.grid(row=r,column=1,sticky="ew",pady=5)
        if key=="file_path":
            def choose_file():
                path=core.filedialog.askopenfilename(parent=win,title="Виберіть файл документа")
                if path: values["file_path"].set(path)
            core.ttk.Button(body,text="…",width=4,command=choose_file).grid(row=r,column=2,padx=(5,0),pady=5)
    core.ttk.Label(body,text="Примітка").grid(row=len(labels),column=0,sticky="nw",padx=(0,8),pady=5)
    notes=core.tk.Text(body,height=6,wrap="word")
    notes.grid(row=len(labels),column=1,columnspan=2,sticky="nsew",pady=5)
    notes.insert("1.0",notes_var.get())
    body.rowconfigure(len(labels),weight=1)
    buttons=core.ttk.Frame(body); buttons.grid(row=len(labels)+1,column=0,columnspan=3,sticky="ew",pady=(12,0))

    def save():
        payload={key:var.get() for key,var in values.items()}
        payload["notes"]=notes.get("1.0","end-1c")
        payload["source_kind"]=(row["source_kind"] if row is not None and "source_kind" in row.keys() else "manual") or "manual"
        payload["source_name"]=(row["source_name"] if row is not None and "source_name" in row.keys() else "") or ""
        con=core.db()
        try:
            registry.save_employee_document(con,employee_id,payload,row["id"] if row is not None else None)
            con.commit()
        except Exception as exc:
            con.rollback(); core.messagebox.showerror("Документ",str(exc),parent=win); return
        finally:
            con.close()
        win.destroy()
        if callable(on_saved): on_saved()

    core.ttk.Button(buttons,text="Скасувати",command=win.destroy).pack(side="right",padx=(6,0))
    core.ttk.Button(buttons,text="Зберегти",style="Accent.TButton",command=save).pack(side="right")
    win.transient(app)


def install(core, base_app):
    if getattr(core,"_TAXO_1045_INSTALLED",False):
        return core.App
    core.APP_VERSION=APP_VERSION

    class Taxo1045App(base_app):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            registry.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_personnel_registry_actions()

        def _install_personnel_registry_actions(self):
            root=getattr(self,"personnel_overview_page",None)
            if not _alive(root) or getattr(self,"_personnel_registry_actions_installed",False):
                return
            anchor=_find_button(root,"Новий працівник")
            if anchor is None:
                return
            parent=anchor.master
            self._personnel_registry_import_button=core.ttk.Button(
                parent,text="Імпорт з реєстру…",command=self.import_personnel_registry_xlsx
            )
            self._personnel_registry_import_button.pack(side="right",padx=(8,0))
            self._refresh_personnel_registry_quarter_status()
            core.ttk.Button(
                parent,text="Дані та документи…",command=self.open_personnel_data_center
            ).pack(side="right",padx=(8,0))
            self._personnel_registry_actions_installed=True

        def import_personnel_registry_xlsx(self):
            path=core.filedialog.askopenfilename(
                parent=self,title="Імпорт відомостей з державного реєстру",
                filetypes=(("Excel XLSX","*.xlsx"),("Усі файли","*.*")),
            )
            if not path:
                return
            try:
                preview=registry.preview_registry_import(core,path)
            except Exception as exc:
                core.messagebox.showerror("Імпорт даних працівників",str(exc),parent=self)
                return
            self._show_registry_import_preview(preview)

        def _show_registry_import_preview(self,preview):
            win=core.tk.Toplevel(self)
            _configure_window(core,win,"Попередній перегляд імпорту",1120,720)
            body=core.ttk.Frame(win,padding=14); body.pack(fill="both",expand=True)
            parsed=preview["parsed"]; plan=preview["plan"]
            updates=sum(1 for row in plan if row["status"]=="update")
            matched=sum(1 for row in plan if row.get("employee_id") is not None)
            problem=sum(1 for row in plan if row["status"] in ("unmatched","ambiguous","conflict"))
            local_only=list(preview.get("local_only") or [])
            core.ttk.Label(body,text="Імпорт даних працівників",style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=("Джерело: %s  ·  аркуш: %s  ·  рядків: %d  ·  знайдено працівників: %d  ·  зі змінами: %d  ·  потребують уваги: %d"
                      % (_source_label(parsed["source_kind"]),parsed["sheet_name"],len(plan),matched,updates,problem)),
                style="Muted.TLabel",
            ).pack(anchor="w",pady=(4,10))
            core.ttk.Label(
                body,
                text=("Taxo не створює нових працівників автоматично. РНОКПП має пріоритет; збіг лише за ПІБ показується окремо. "
                      "Порожні поля джерела ніколи не стирають наявні дані. Відсутність працівника/поля у витягу не видаляє його з Taxo."),
                wraplength=1040,justify="left",
            ).pack(anchor="w",pady=(0,8))
            mode_var=core.tk.StringVar(value=registry.IMPORT_FILL_EMPTY)
            modes=core.ttk.LabelFrame(body,text="Режим застосування державного витягу",padding=(8,5))
            modes.pack(fill="x",pady=(0,10))
            for value,label in (
                (registry.IMPORT_COMPARE,"Лише звірити — нічого не змінювати в Taxo"),
                (registry.IMPORT_FILL_EMPTY,"Доповнити — заповнити тільки порожні поля та нові відомості"),
                (registry.IMPORT_UPDATE,"Оновити — замінити непорожні реєстрові поля та доповнити нове"),
            ):
                core.ttk.Radiobutton(modes,text=label,variable=mode_var,value=value).pack(anchor="w",pady=1)
            core.ttk.Label(
                modes,
                text="У всіх режимах дані, яких немає у витягу, залишаються в Taxo без змін.",
                style="Muted.TLabel",
            ).pack(anchor="w",pady=(4,0))
            frame=core.ttk.Frame(body); frame.pack(fill="both",expand=True)
            frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            cols=("status","employee","match","changes","notes")
            tree=core.ttk.Treeview(frame,columns=cols,show="headings")
            for key,label,width in (
                ("status","Дія",110),("employee","Працівник",270),("match","Зіставлення",100),
                ("changes","Поля, що зміняться",390),("notes","Примітка",300),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
            sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
            tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
            for index,row in enumerate(plan):
                fields=", ".join(dict.fromkeys(change["label"] for change in row["changes"]))
                notes="; ".join(x for x in row.get("notes",[]) if x)
                tree.insert("","end",iid=str(index),values=(
                    _status_label(row["status"]),row["employee_name"],_match_label(row["match_quality"]),fields or "—",notes or "—"
                ),tags=(row["status"],))
            for offset,row in enumerate(local_only,start=len(plan)):
                tree.insert("","end",iid="local-%d" % offset,values=(
                    "Є лише в Taxo",row["employee_name"],"—","—",row["note"]
                ),tags=("local_only",))
            tree.tag_configure("local_only",foreground="#7A5B00")
            tree.tag_configure("update",foreground="#0B5D1E")
            tree.tag_configure("unmatched",foreground="#8A5A00")
            tree.tag_configure("ambiguous",foreground="#8A1C1C")
            tree.tag_configure("conflict",foreground="#8A1C1C")
            actions=core.ttk.Frame(body); actions.pack(fill="x",pady=(12,0))

            def apply_import():
                if not core.messagebox.askyesno(
                    "Застосувати імпорт?",
                    "Режим: %s\nПотенційних карток зі змінами: %d.\n\nНеоднозначні, конфліктні та незнайдені рядки буде пропущено. Дані, відсутні у витягу, не видаляються. Продовжити?" % (registry.IMPORT_MODE_LABELS[mode_var.get()],updates),
                    parent=win,
                ):
                    return
                try:
                    result=registry.apply_registry_import(core,preview,mode=mode_var.get())
                except Exception as exc:
                    core.messagebox.showerror("Імпорт даних працівників",str(exc),parent=win); return
                refresh=getattr(self,"_refresh_personnel_overview",None)
                if callable(refresh): refresh()
                core.messagebox.showinfo(
                    "Імпорт завершено",
                    ("Джерело: %s\nРежим: %s\nРядків: %d\nЗіставлено: %d\nЗмінено карток: %d\nЄ лише в Taxo: %d\nПропущено: %d\nПопереджень: %d"
                     % (_source_label(result["source_kind"]),registry.IMPORT_MODE_LABELS[result["mode"]],result["total"],result["matched"],
                        result["updated"],result["local_only"],result["skipped"],result["warnings"])),
                    parent=win,
                )
                self._refresh_personnel_registry_quarter_status()
                win.destroy()

            core.ttk.Button(actions,text="Закрити",command=win.destroy).pack(side="right",padx=(6,0))
            core.ttk.Button(actions,text="Застосувати оновлення",style="Accent.TButton",command=apply_import).pack(side="right")
            win.transient(self)

        def open_personnel_data_center(self):
            employee_id=_selected_employee_id(self)
            if employee_id is None:
                core.messagebox.showinfo("Працівники","Виберіть працівника у реєстрі.",parent=self)
                return
            con=core.db()
            try:
                employee,military=registry.employee_profile(con,employee_id)
            finally:
                con.close()
            if employee is None:
                core.messagebox.showerror("Працівники","Картку працівника не знайдено.",parent=self)
                return
            name=" ".join(x for x in (employee["last_name"],employee["first_name"],employee["middle_name"]) if x)
            win=core.tk.Toplevel(self)
            _configure_window(core,win,"Дані працівника — "+name,1080,720)
            head=core.ttk.Frame(win,padding=(14,12,14,6)); head.pack(fill="x")
            core.ttk.Label(head,text=name,style="Title.TLabel").pack(side="left")
            core.ttk.Label(head,text="  ·  таб. № "+str(employee["personnel_no"] or "—"),style="Muted.TLabel").pack(side="left")
            book=core.ttk.Notebook(win); book.pack(fill="both",expand=True,padx=10,pady=(0,10))
            personal_tab=core.ttk.Frame(book); military_tab=core.ttk.Frame(book); documents_tab=core.ttk.Frame(book); history_tab=core.ttk.Frame(book)
            book.add(personal_tab,text="Персональні дані")
            book.add(military_tab,text="Військовий облік")
            book.add(documents_tab,text="Документи")
            book.add(history_tab,text="Історія імпорту")

            personal_tree=_kv_tree(core,personal_tab)
            _fill_kv(personal_tree,[
                ("ПІБ",name),("Табельний №",employee["personnel_no"]),
                ("Стать",employee["gender"]),("Дата народження",registry.display_date(employee["birth_date"])),
                ("РНОКПП",employee["rnokpp"]),("Серія паспорта",employee["passport_series"]),
                ("Номер паспорта",employee["passport_number"]),("Номер ID-картки",employee["id_card_number"]),
                ("Зареєстроване місце проживання",employee["registered_address"]),
                ("Фактичне місце проживання",employee["actual_address"]),
                ("Посада",employee["position"]),("Прийнятий",employee["employment_date"]),
            ])

            mbody=core.ttk.Frame(military_tab); mbody.pack(fill="both",expand=True)
            military_tree=_kv_tree(core,mbody)
            mdata={key:(military[key] if military is not None and key in military.keys() else "") for key in registry.MILITARY_FIELD_LABELS}
            _fill_kv(military_tree,[(label,registry.display_date(mdata[key]) if key.endswith("_until") else mdata[key])
                                    for key,label in registry.MILITARY_FIELD_LABELS.items()])
            missing=registry.missing_appendix5_fields(employee,military)
            hint=("Поля додатка 5, які ще не заповнені у Taxo: "+", ".join(missing)) if missing else "Основні групи даних додатка 5 заповнені."
            core.ttk.Label(military_tab,text=hint,style="Muted.TLabel",wraplength=1020,justify="left").pack(fill="x",padx=12,pady=(0,10))

            dtop=core.ttk.Frame(documents_tab,padding=(10,10,10,4)); dtop.pack(fill="x")
            show_archived=core.tk.BooleanVar(value=False)
            dframe=core.ttk.Frame(documents_tab); dframe.pack(fill="both",expand=True,padx=10,pady=(0,10))
            dframe.rowconfigure(0,weight=1); dframe.columnconfigure(0,weight=1)
            dcols=("type","series","number","issue","expiry","issuer","source","status")
            dtree=core.ttk.Treeview(dframe,columns=dcols,show="headings")
            for key,label,width in (
                ("type","Тип",210),("series","Серія",80),("number","Номер",120),("issue","Виданий",95),
                ("expiry","Чинний до",95),("issuer","Ким виданий",180),("source","Джерело",190),("status","Стан",85),
            ):
                dtree.heading(key,text=label); dtree.column(key,width=width,anchor="w")
            dsy=core.ttk.Scrollbar(dframe,orient="vertical",command=dtree.yview)
            dsx=core.ttk.Scrollbar(dframe,orient="horizontal",command=dtree.xview)
            dtree.configure(yscrollcommand=dsy.set,xscrollcommand=dsx.set)
            dtree.grid(row=0,column=0,sticky="nsew"); dsy.grid(row=0,column=1,sticky="ns"); dsx.grid(row=1,column=0,sticky="ew")
            doc_cache={}

            def refresh_docs():
                for iid in dtree.get_children(): dtree.delete(iid)
                doc_cache.clear(); con=core.db()
                try: rows=registry.list_employee_documents(con,employee_id,show_archived.get())
                finally: con.close()
                for row in rows:
                    doc_cache[row["id"]]=row
                    source=(row["source_name"] or row["source_kind"] or "ручне введення")
                    dtree.insert("","end",iid=str(row["id"]),values=(
                        row["doc_type"],row["series"] or "",row["number"] or "",registry.display_date(row["issue_date"]),
                        registry.display_date(row["expiry_date"]),row["issuer"] or "",source,"Активний" if row["active"] else "Архів",
                    ),tags=("active" if row["active"] else "archived",))
                dtree.tag_configure("archived",foreground="#777777")

            def selected_doc():
                if not dtree.selection(): return None
                try: return doc_cache.get(int(dtree.selection()[0]))
                except Exception: return None

            def edit_doc():
                row=selected_doc()
                if row is None:
                    core.messagebox.showinfo("Документи","Виберіть документ.",parent=win); return
                _document_editor(self,core,employee_id,row,refresh_docs)

            def archive_doc():
                row=selected_doc()
                if row is None:
                    core.messagebox.showinfo("Документи","Виберіть документ.",parent=win); return
                if not core.messagebox.askyesno("Архівувати документ?","Документ залишиться в історії, але буде позначений архівним.",parent=win):
                    return
                con=core.db()
                try:
                    registry.archive_employee_document(con,employee_id,row["id"]); con.commit()
                finally: con.close()
                refresh_docs()

            def open_doc_file():
                row=selected_doc()
                if row is None or not (row["file_path"] or "").strip():
                    core.messagebox.showinfo("Документи","Для вибраного документа файл не вказано.",parent=win); return
                raw=row["file_path"]
                try: target=core.real_data_path(raw)
                except Exception: target=Path(raw)
                if not Path(target).exists():
                    core.messagebox.showerror("Документи","Файл не знайдено:\n"+str(target),parent=win); return
                core.open_external(target)

            core.ttk.Button(dtop,text="Додати документ",style="Accent.TButton",command=lambda:_document_editor(self,core,employee_id,None,refresh_docs)).pack(side="left")
            core.ttk.Button(dtop,text="Редагувати",command=edit_doc).pack(side="left",padx=5)
            core.ttk.Button(dtop,text="Відкрити файл",command=open_doc_file).pack(side="left",padx=5)
            core.ttk.Button(dtop,text="В архів",command=archive_doc).pack(side="left",padx=5)
            core.ttk.Checkbutton(dtop,text="Показати архівні",variable=show_archived,command=refresh_docs).pack(side="right")
            dtree.bind("<Double-1>",lambda _e:edit_doc())
            refresh_docs()

            hframe=core.ttk.Frame(history_tab); hframe.pack(fill="both",expand=True,padx=10,pady=10)
            hframe.rowconfigure(0,weight=1); hframe.columnconfigure(0,weight=1)
            hcols=("date","source","kind","row","hash")
            htree=core.ttk.Treeview(hframe,columns=hcols,show="headings")
            for key,label,width in (
                ("date","Імпортовано",160),("source","Файл-джерело",360),("kind","Форма",220),
                ("row","Рядок",70),("hash","Контрольний відбиток",260),
            ):
                htree.heading(key,text=label); htree.column(key,width=width,anchor="w")
            hsy=core.ttk.Scrollbar(hframe,orient="vertical",command=htree.yview)
            hsx=core.ttk.Scrollbar(hframe,orient="horizontal",command=htree.xview)
            htree.configure(yscrollcommand=hsy.set,xscrollcommand=hsx.set)
            htree.grid(row=0,column=0,sticky="nsew"); hsy.grid(row=0,column=1,sticky="ns"); hsx.grid(row=1,column=0,sticky="ew")
            con=core.db()
            try: history=registry.list_import_history(con,employee_id)
            finally: con.close()
            for row in history:
                htree.insert("","end",values=(row["imported_at"],row["source_name"],_source_label(row["source_kind"]),row["source_row"] or "",row["row_fingerprint"][:24]))
            win.transient(self)

    Taxo1045App.__name__="App"
    Taxo1045App.__qualname__="App"
    core.App=Taxo1045App
    core._TAXO_1045_INSTALLED=True
    return Taxo1045App
