# -*- coding: utf-8 -*-
"""One read-only browser for existing orders and prepared paper documents."""
from __future__ import annotations

from pathlib import Path

import document_catalog
import paper_documents as paperwork


def open_document_catalog(parent, core, workspace_root):
    win = core.tk.Toplevel(parent)
    win.title("Документи")
    try:
        core.fit_window_to_screen(win, 1040, 660, 700, 450)
    except Exception:
        win.geometry("1040x660")
    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(3, weight=1)
    core.ttk.Label(body, text="Готові документи та накази",
                   style="Subtitle.TLabel").grid(row=0, column=0, sticky="w")
    search = core.tk.StringVar(value="")
    bar = core.ttk.Frame(body)
    bar.grid(row=1, column=0, sticky="ew", pady=6)
    bar.columnconfigure(1, weight=1)
    core.ttk.Label(bar, text="Пошук:").grid(row=0, column=0, sticky="w")
    core.ttk.Entry(bar, textvariable=search).grid(row=0, column=1, sticky="ew", padx=8)
    source_status = core.tk.StringVar(value="")
    core.ttk.Label(body, textvariable=source_status, wraplength=900,
                   justify="left").grid(row=2, column=0, sticky="ew")
    frame = core.ttk.Frame(body)
    frame.grid(row=3, column=0, sticky="nsew", pady=6)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    cols = ("date", "number", "kind", "title", "person", "file")
    tree = core.ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
    for key, label, width in (
        ("date", "Дата", 105), ("number", "№", 90), ("kind", "Документ", 130),
        ("title", "Тема / назва", 300), ("person", "Працівники", 190),
        ("file", "Стан файла", 155),
    ):
        tree.heading(key, text=label)
        tree.column(key, width=width, minwidth=70)
    vertical = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    horizontal = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    actions = core.ttk.Frame(body)
    actions.grid(row=4, column=0, sticky="ew", pady=(4, 0))
    page_text = core.tk.StringVar(value="")
    state = {"page": 0, "pages": 1, "rows": {}, "after": None, "snapshot": None}

    def refresh(reset=False, reload_sources=False):
        if reset:
            state["page"] = 0
        if reload_sources or state["snapshot"] is None:
            state["snapshot"] = document_catalog.read_sources(workspace_root)
        result = document_catalog.paginate_sources(
            state["snapshot"], text_filter=search.get(), page=state["page"])
        state["page"], state["pages"] = result["page"], result["pages"]
        source_status.set(result["order_status"] + " " + result["paper_status"])
        page_text.set("Сторінка %d з %d · записів: %d" % (
            result["page"] + 1, result["pages"], result["total"]))
        tree.delete(*tree.get_children())
        state["rows"].clear()
        for number, row in enumerate(result["rows"]):
            iid = str(number)
            state["rows"][iid] = row
            tree.insert("", "end", iid=iid, values=(
                row["date"], row["number"], row["kind"], row["title"],
                row["person"], row["file_state"],
            ))

    def search_changed(*_):
        if state["after"] is not None:
            win.after_cancel(state["after"])
        def later():
            state["after"] = None
            refresh(reset=True)
        state["after"] = win.after(250, later)

    def change_page(delta):
        state["page"] = max(0, min(state["page"] + delta, state["pages"] - 1))
        refresh()

    def open_selected(_event=None):
        selected = tree.selection()
        if not selected:
            core.messagebox.showinfo("Документи", "Виберіть документ.", parent=win)
            return
        row = state["rows"][selected[0]]
        if row["source"] == "order":
            callback = getattr(parent.winfo_toplevel(), "_taxo_preview_catalog_order", None)
            if callback is None:
                core.messagebox.showinfo(
                    "Наказ", "Відкрийте цей наказ у розділі «Накази».", parent=win)
                return
            try:
                callback(row["source_id"])
            except Exception as exc:
                core.messagebox.showerror("Наказ", str(exc), parent=win)
            return
        try:
            # Re-read and revalidate the actual path immediately before opening.
            path = row["file_path"]
            if path is None or document_catalog._paper_file(
                    Path(workspace_root) / "Data" / "PaperDocuments", path.name) != path:
                raise ValueError("Небезпечний шлях до документа.")
            if not path.is_file():
                raise FileNotFoundError("Файл документа відсутній: " + str(path))
            paperwork.open_file(path)
        except Exception as exc:
            core.messagebox.showerror("Документ", str(exc), parent=win)

    core.ttk.Button(actions, text="Оновити", command=lambda: refresh(reload_sources=True)).pack(side="left")
    core.ttk.Button(actions, text="Попередня", command=lambda: change_page(-1)).pack(side="left", padx=4)
    core.ttk.Button(actions, text="Наступна", command=lambda: change_page(1)).pack(side="left")
    core.ttk.Label(actions, textvariable=page_text).pack(side="left", padx=8)
    core.ttk.Button(actions, text="Відкрити вибране", command=open_selected).pack(side="right")
    core.ttk.Label(body, text="Підготовлений документ не означає проведення чи підписання.",
                   style="Muted.TLabel").grid(row=5, column=0, sticky="w", pady=(6, 0))
    tree.bind("<Double-1>", open_selected)
    search.trace_add("write", search_changed)
    win._taxo_catalog_tree = tree
    win._taxo_catalog_search = search
    win._taxo_catalog_refresh = refresh
    win._taxo_catalog_open = open_selected
    refresh()
    return win
