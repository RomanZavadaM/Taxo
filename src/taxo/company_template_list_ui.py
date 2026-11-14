# -*- coding: utf-8 -*-
"""Tk list of user-owned CompanyTemplates copies.

This module only lists verified company copies and opens the separate editor
window. It owns no storage logic and never modifies the vendor TemplateLibrary.
"""
from __future__ import annotations

import queue
import threading
from tkinter import messagebox, ttk

from company_template_editor_service import list_editor_templates
from company_template_editor_ui import open_company_template_editor

_LIST_READER_SLOT = threading.BoundedSemaphore(1)


def open_company_templates(parent, services):
    """Open the company-owned template list."""
    from tkinter import StringVar, TclError, Toplevel

    win = Toplevel(parent)
    win.title("Taxo — Власні шаблони")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 860, 540, 680, 420)
    except (ImportError, AttributeError, TypeError):
        win.geometry("860x540")

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(2, weight=1)

    ttk.Label(
        body, text="Власні шаблони",
        font=("TkDefaultFont", 13, "bold"),
    ).grid(row=0, column=0, sticky="w")

    status = StringVar(value="Завантажую власні шаблони…")
    ttk.Label(body, textvariable=status, justify="left", wraplength=780).grid(
        row=1, column=0, sticky="ew", pady=(7, 7)
    )

    list_frame = ttk.Frame(body)
    list_frame.grid(row=2, column=0, sticky="nsew")
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)

    columns = ("title", "revision", "source")
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )
    tree.heading("title", text="Назва")
    tree.heading("revision", text="Редакція")
    tree.heading("source", text="Початковий шаблон")
    tree.column("title", width=420, minwidth=180, stretch=True)
    tree.column("revision", width=90, minwidth=70, stretch=False)
    tree.column("source", width=250, minwidth=140, stretch=True)
    ybar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    xbar = ttk.Scrollbar(list_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

    footer = ttk.Frame(body)
    footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    footer.columnconfigure(0, weight=1)
    refresh_button = ttk.Button(footer, text="Оновити")
    refresh_button.grid(row=0, column=1, padx=(4, 8))
    edit_button = ttk.Button(footer, text="Редагувати", state="disabled")
    edit_button.grid(row=0, column=2, padx=(4, 8))
    ttk.Button(footer, text="Закрити", command=lambda: close()).grid(
        row=0, column=3
    )

    results = queue.Queue()
    state = {
        "closed": False,
        "busy": False,
        "generation": 0,
        "rows": (),
        "after": None,
    }
    win._taxo_company_templates_state = state

    def close():
        if state["closed"]:
            return
        state["closed"] = True
        state["generation"] += 1
        if state["after"] is not None:
            try:
                win.after_cancel(state["after"])
            except TclError:
                pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close)

    def render(rows):
        previous = tree.selection()
        tree.delete(*tree.get_children())
        for item in rows:
            tree.insert(
                "", "end",
                iid=item.company_template_id,
                values=(
                    item.title,
                    "r%d" % item.edit_revision,
                    "%s @ %s" % (
                        item.based_on_template_id,
                        item.based_on_revision_id,
                    ),
                ),
            )
        if previous and tree.exists(previous[0]):
            tree.selection_set(previous[0])
            tree.see(previous[0])
        edit_button.configure(
            state="normal" if tree.selection() else "disabled"
        )
        status.set("Власних шаблонів: %d" % len(rows))

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                generation, ok, payload = results.get_nowait()
                if generation != state["generation"]:
                    continue
                state["busy"] = False
                refresh_button.configure(state="normal")
                if ok:
                    state["rows"] = payload
                    render(payload)
                else:
                    status.set("Не вдалося прочитати власні шаблони.")
                    messagebox.showerror(
                        "Власні шаблони", str(payload), parent=win
                    )
        except queue.Empty:
            pass
        if not state["closed"]:
            state["after"] = win.after(120, poll)

    def refresh():
        if state["closed"] or state["busy"]:
            return
        state["busy"] = True
        state["generation"] += 1
        generation = state["generation"]
        refresh_button.configure(state="disabled")
        edit_button.configure(state="disabled")
        status.set("Завантажую власні шаблони…")

        def worker():
            with _LIST_READER_SLOT:
                try:
                    payload = list_editor_templates(services.workspace.root)
                    results.put((generation, True, payload))
                except Exception as exc:
                    results.put((generation, False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-company-template-list",
            daemon=True,
        ).start()

    def selection_changed(_event=None):
        edit_button.configure(
            state="normal" if tree.selection() and not state["busy"] else "disabled"
        )

    def edit_selected(_event=None):
        selected = tree.selection()
        if not selected:
            return
        open_company_template_editor(
            win,
            services,
            selected[0],
            on_saved=refresh,
        )

    tree.bind("<<TreeviewSelect>>", selection_changed, add="+")
    tree.bind("<Double-1>", edit_selected, add="+")
    tree.bind("<Return>", edit_selected, add="+")
    edit_button.configure(command=edit_selected)
    refresh_button.configure(command=refresh)
    state["after"] = win.after(120, poll)
    refresh()
    return win
