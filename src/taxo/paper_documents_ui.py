# -*- coding: utf-8 -*-
"""Workspace document browser shared by safety briefings and internships."""
from __future__ import annotations

import paper_documents as paperwork


def open_paper_document_catalog(parent, core, workspace_root):
    win = core.tk.Toplevel(parent)
    win.title("Каталог підготовлених документів")
    try:
        core.fit_window_to_screen(win, 980, 620, 700, 450)
    except Exception:
        win.geometry("980x620")
    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(2, weight=1)
    core.ttk.Label(body, text="Документи для друку", style="Subtitle.TLabel").grid(
        row=0, column=0, sticky="w")
    filter_text = core.tk.StringVar(value="")
    filter_bar = core.ttk.Frame(body)
    filter_bar.grid(row=1, column=0, sticky="ew", pady=8)
    filter_bar.columnconfigure(1, weight=1)
    core.ttk.Label(filter_bar, text="Пошук за датою, темою, працівником:").grid(row=0, column=0)
    core.ttk.Entry(filter_bar, textvariable=filter_text).grid(
        row=0, column=1, sticky="ew", padx=8)
    frame = core.ttk.Frame(body)
    frame.grid(row=2, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    tree = core.ttk.Treeview(
        frame, columns=("date", "kind", "topic", "person"), show="headings",
        selectmode="browse"
    )
    for name, title, width in (
        ("date", "Дата", 110),
        ("kind", "Документ", 140),
        ("topic", "Тема / назва", 360),
        ("person", "Працівники / водій", 250),
    ):
        tree.heading(name, text=title)
        tree.column(name, width=width)
    ybar = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    xbar = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    found = {}
    def refresh():
        try:
            rows = paperwork.list_documents(workspace_root, filter_text.get())
        except Exception as exc:
            core.messagebox.showerror("Каталог документів", str(exc), parent=win)
            return
        tree.delete(*tree.get_children())
        found.clear()
        for record in rows:
            rid = record["id"]
            found[rid] = record
            tree.insert("", "end", iid=rid, values=(
                record.get("date", ""), record.get("kind", ""),
                record.get("title", ""), record.get("person", ""),
            ))
    def open_selected(_event=None):
        selection = tree.selection()
        if not selection:
            return
        try:
            path = paperwork.document_path(workspace_root, found[selection[0]])
            if not path.is_file():
                raise FileNotFoundError("Файл документа відсутній: " + str(path))
            paperwork.open_file(path)
        except Exception as exc:
            core.messagebox.showerror("Документ", str(exc), parent=win)
    actions = core.ttk.Frame(body)
    actions.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    core.ttk.Button(actions, text="Оновити", command=refresh).pack(side="left")
    core.ttk.Button(actions, text="Відкрити Word для перегляду / друку",
                    command=open_selected).pack(side="right")
    core.ttk.Label(
        body, text="Підготовлений документ не означає проведення, підписання чи допуск.",
        style="Muted.TLabel"
    ).grid(row=4, column=0, sticky="w", pady=(8, 0))
    tree.bind("<Double-1>", open_selected)
    filter_text.trace_add("write", lambda *_: refresh())
    refresh()
    return win
