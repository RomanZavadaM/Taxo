# -*- coding: utf-8 -*-
"""Preview and export the current version of an operations order."""
from order_pdf_workflow import generate_order_formats, open_order_format


def open_order_preview(core, ops, win, row, _order_print_data,
                       register_order_preview, order_mutability_message, order_dialog):
    row,assignments,entities,company,control=_order_print_data(row)
    preview=ops.order_preview_text(
        row,assignments=assignments,entities=entities,company=company,control_name=control
    )
    dlg=core.tk.Toplevel(win)
    dlg.title("Перегляд наказу №%s" % row["order_no"])
    try:
        core.configure_toplevel(dlg,title=dlg.title(),minsize=(760,560))
    except Exception:
        dlg.geometry("900x700")
    frm=core.ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
    core.ttk.Label(
        frm,
        text=("Перевірте зміст наказу. Оберіть формат: Word, PDF, JPG "
              "(для кожної сторінки) або створіть усі. "
              "Перегляд доступний у Taxo, відкриття — у програмі комп'ютера."),
        style="Muted.TLabel",wraplength=820,justify="left",
    ).pack(anchor="w",pady=(0,8))
    text_frame=core.ttk.Frame(frm); text_frame.pack(fill="both",expand=True)
    text_frame.rowconfigure(0,weight=1); text_frame.columnconfigure(0,weight=1)
    viewer=core.tk.Text(text_frame,wrap="word",font=("TkDefaultFont",11),padx=12,pady=12)
    sy=core.ttk.Scrollbar(text_frame,orient="vertical",command=viewer.yview)
    viewer.configure(yscrollcommand=sy.set)
    viewer.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns")
    viewer.insert("1.0",preview); viewer.configure(state="disabled")

    generated={}
    status_var=core.tk.StringVar(value="Файли ще не створено.")
    def refresh_preview_content():
        nonlocal row,assignments,entities,company,control
        row,assignments,entities,company,control=_order_print_data(row)
        current_preview=ops.order_preview_text(
            row,assignments=assignments,entities=entities,company=company,control_name=control
        )
        viewer.configure(state="normal")
        viewer.delete("1.0","end")
        viewer.insert("1.0",current_preview)
        viewer.configure(state="disabled")
        status_var.set("Зміст актуальний. Закріплень: %d" % len(assignments))
        return len(assignments)

    register_order_preview(row["id"], dlg, refresh_preview_content)
    dlg._taxo_refresh_preview=refresh_preview_content

    def make_formats(formats):
        try:
            refresh_preview_content()
            results=generate_order_formats(
                core,ops,row,assignments,entities,company,control,
                formats=formats,parent=dlg,
            )
        except Exception as exc:
            core.messagebox.showerror("Формування наказу",str(exc),parent=dlg)
            return
        generated.update(results)
        if not results:
            status_var.set("Файл не створено.")
            return
        summary=", ".join(
            "%s: %d" % (kind.upper(), len(paths))
            for kind,paths in results.items()
        )
        status_var.set("Збережено: "+summary)
        preferred=next((kind for kind in ("pdf","docx","jpg") if kind in results),None)
        if preferred:
            view_format(preferred)

    def view_format(kind,external=False):
        paths=generated.get(kind,())
        if not paths:
            core.messagebox.showinfo(
                "Документи наказу",
                "Спочатку створіть %s для цього наказу." % kind.upper(),parent=dlg
            )
            return
        try:
            if kind=="docx" and not external:
                # Never present the plain-text DOCX reader as a page proof.
                # Prefer matching PDF already generated in this dialog,
                # otherwise let the installed Word-compatible app render it.
                matching_pdf=generated.get("pdf",())
                if matching_pdf:
                    open_order_format(core,matching_pdf,dlg)
                else:
                    open_order_format(core,paths,dlg,external=True)
            else:
                open_order_format(core,paths,dlg,external=external)
            if external and len(paths)>1:
                core.messagebox.showinfo(
                    "Сторінки JPG",
                    "Відкрито першу сторінку. Інші JPG-сторінки збережено поруч:\n%s"
                    % paths[0].parent,parent=dlg
                )
        except Exception as exc:
            core.messagebox.showwarning(
                "Відкриття документа",
                "Файл збережено, але його не вдалося відкрити:\n%s" % exc,
                parent=dlg
            )

    formats_box=core.ttk.LabelFrame(frm,text="Документи наказу",padding=(8,6))
    formats_box.pack(fill="x",pady=(8,0))
    for col in range(4):
        formats_box.columnconfigure(col,weight=1)
    for col,(title,kinds) in enumerate((
        ("Створити DOCX",("docx",)),("Створити PDF",("pdf",)),
        ("Створити JPG",("jpg",)),("Створити все",("docx","pdf","jpg"))
    )):
        core.ttk.Button(
            formats_box,text=title,command=lambda f=kinds:make_formats(f)
        ).grid(row=0,column=col,sticky="ew",padx=3,pady=3)
    for col,kind in enumerate(("docx","pdf","jpg")):
        core.ttk.Button(
            formats_box,text="Перегляд "+kind.upper(),
            command=lambda f=kind:view_format(f)
        ).grid(row=1,column=col,sticky="ew",padx=3,pady=3)
        core.ttk.Button(
            formats_box,text="Відкрити у програмі: "+kind.upper(),
            command=lambda f=kind:view_format(f,external=True)
        ).grid(row=2,column=col,sticky="ew",padx=3,pady=3)
    core.ttk.Label(
        formats_box,textvariable=status_var,style="Muted.TLabel",
        wraplength=810,justify="left"
    ).grid(row=3,column=0,columnspan=4,sticky="w",padx=4,pady=(4,0))
    bar=core.ttk.Frame(frm); bar.pack(fill="x",pady=(8,0))
    core.ttk.Button(bar,text="Закрити",command=dlg.destroy).pack(side="right")
    core.ttk.Button(bar,text="Оновити зміст",command=refresh_preview_content).pack(side="left")
    core.ttk.Button(
        bar,text="Сформувати PDF / друк",style="Accent.TButton",
        command=lambda:make_formats(("pdf",))
    ).pack(side="right",padx=(0,6))
    if not order_mutability_message(row):
        core.ttk.Button(
            bar,text="Редагувати наказ",
            command=lambda:(dlg.destroy(),order_dialog(row))
        ).pack(side="left")
    dlg.transient(win)
    try:
        dlg.lift(); dlg.focus_force()
    except Exception:
        pass
    return dlg

