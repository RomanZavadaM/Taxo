# -*- coding: utf-8 -*-
"""A small, read-only Tk browser for the installed template library.

Tk is owned by this module; source file validation belongs to
template_library_reader, and workspace selection to ApplicationServices.
Closing this child window never closes Taxo. Blocking disk/network reads are
performed off the Tk thread with a bounded number of active workers.
"""
from __future__ import annotations

import queue
import threading
from tkinter import ttk

from template_library_service import LibraryView, inspect_workspace_library
from template_library_preview_ui import open_template_preview

# Avoid a new thread per click on a slow or disconnected network workspace.
_READER_SLOT = threading.BoundedSemaphore(1)
_FILTER_ALL = "Усі категорії"


def open_template_library(parent, services):
    """Open the library browser; returns a child window, never changes data."""
    from tkinter import Toplevel, StringVar, TclError

    win = Toplevel(parent)
    win.title("Taxo — Бібліотека шаблонів (перегляд)")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 940, 620, 700, 440)
    except (ImportError, AttributeError, TypeError):
        win.geometry("940x620")

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(3, weight=1)

    ttk.Label(body, text="Бібліотека шаблонів — лише перегляд",
              font=("TkDefaultFont", 13, "bold")).grid(row=0, column=0, sticky="w")

    status = StringVar(value="Перевіряю бібліотеку…")
    details = StringVar(value="")
    path = StringVar(value="")
    ttk.Label(body, textvariable=status, wraplength=850, justify="left").grid(
        row=1, column=0, sticky="ew", pady=(8, 2))
    ttk.Label(body, textvariable=details, wraplength=850, justify="left").grid(
        row=2, column=0, sticky="ew", pady=(0, 6))

    frame = ttk.Frame(body)
    frame.grid(row=3, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    tools = ttk.Frame(frame)
    tools.grid(row=0, column=0, sticky="ew", pady=(0, 6))
    tools.columnconfigure(1, weight=1)
    ttk.Label(tools, text="Пошук:").grid(row=0, column=0, padx=(0, 5))
    search = StringVar(value="")
    ttk.Entry(tools, textvariable=search).grid(row=0, column=1, sticky="ew")
    category = StringVar(value=_FILTER_ALL)
    combo = ttk.Combobox(tools, state="readonly", textvariable=category,
                         width=24, values=(_FILTER_ALL,))
    combo.grid(row=0, column=2, padx=(8, 0))

    list_frame = ttk.Frame(frame)
    list_frame.grid(row=1, column=0, sticky="nsew")
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)
    columns = ("category", "title", "kind", "revision")
    tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
    columns_info = (("category", "Категорія", 150), ("title", "Назва шаблону", 380),
                    ("kind", "Тип", 145), ("revision", "Редакція", 90))
    for key, label, width in columns_info:
        tree.heading(key, text=label)
        tree.column(key, width=width, minwidth=70, stretch=(key == "title"))
    ybar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    xbar = ttk.Scrollbar(list_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

    ttk.Label(body, textvariable=path, wraplength=850, justify="left").grid(
        row=4, column=0, sticky="ew", pady=(7, 2))
    footer = ttk.Frame(body)
    footer.grid(row=5, column=0, sticky="ew")
    footer.columnconfigure(0, weight=1)
    count = StringVar(value="Шаблонів: 0")
    ttk.Label(footer, textvariable=count).grid(row=0, column=0, sticky="w")
    refresh_button = ttk.Button(footer, text="Оновити")
    refresh_button.grid(row=0, column=1, padx=(4, 8))
    ttk.Button(footer, text="Закрити", command=lambda: close()).grid(row=0, column=3)

    results = queue.Queue()
    state = {"closed": False, "busy": False, "generation": 0, "view": None,
             "poll": None, "sort": ("title", False)}
    win._taxo_library_state = state

    def close():
        """Cancel UI polling, not the shared application or a file read in flight."""
        if state["closed"]:
            return
        state["closed"] = True
        state["generation"] += 1
        if state["poll"] is not None:
            try:
                win.after_cancel(state["poll"])
            except TclError:
                pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close)

    def render_rows(*_):
        view = state["view"]
        if state["closed"] or view is None:
            return
        needle = search.get().strip().casefold()
        selected = category.get()
        rows = [item for item in view.rows
                if (selected == _FILTER_ALL or item.category == selected)
                and (not needle or needle in
                     (item.title + " " + item.template_id + " " + item.kind).casefold())]
        key, reverse = state["sort"]
        rows.sort(key=lambda item: (getattr(item, key).casefold(), item.template_id),
                  reverse=reverse)
        previous = tree.selection()
        tree.delete(*tree.get_children())
        for item in rows:
            iid = item.template_id + "@" + item.revision_id
            tree.insert("", "end", iid=iid,
                        values=(item.category, item.title, item.kind, item.revision_id))
        if previous and tree.exists(previous[0]):
            tree.selection_set(previous[0])
            tree.see(previous[0])
        count.set("Показано: %d із %d" % (len(rows), len(view.rows)))

    def set_sort(key):
        prev, rev = state["sort"]
        state["sort"] = (key, not rev if prev == key else False)
        render_rows()

    for key, label, _width in columns_info:
        attr = {"category": "category", "title": "title",
                "kind": "kind", "revision": "revision_id"}[key]
        tree.heading(key, text=label, command=lambda k=attr: set_sort(k))

    def open_selected_preview(_event=None):
        """Open the selected, verified template revision without editing data."""
        view = state["view"]
        if state["closed"] or view is None or view.status != "AVAILABLE":
            return
        selection = tree.selection()
        if not selection:
            return
        # IDs are selection keys only; never treat them as filesystem paths.
        selected_key = selection[0]
        for row in view.rows:
            if row.template_id + "@" + row.revision_id == selected_key:
                open_template_preview(
                    win, view.root, services.app_version,
                    row.template_id, row.revision_id
                )
                return

    tree.bind("<Double-1>", open_selected_preview, add="+")
    tree.bind("<Return>", open_selected_preview, add="+")
    ttk.Button(footer, text="Переглянути шаблон",
               command=open_selected_preview).grid(row=0, column=2, padx=(4, 8))

    search.trace_add("write", render_rows)
    combo.bind("<<ComboboxSelected>>", render_rows, add="+")

    def show_result(view):
        state["view"] = view
        status.set(view.summary)
        details.set(("%s · версія: %s" % (view.detail, view.package_version))
                    if view.package_version else view.detail)
        path.set("Розміщення: " + str(view.root))
        values = sorted({item.category for item in view.rows})
        combo.configure(values=(_FILTER_ALL,) + tuple(values))
        if category.get() not in (_FILTER_ALL,) + tuple(values):
            category.set(_FILTER_ALL)
        render_rows()

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                generation, view = results.get_nowait()
                if generation != state["generation"]:
                    continue
                state["busy"] = False
                refresh_button.configure(state="normal")
                show_result(view)
        except queue.Empty:
            pass
        if not state["closed"]:
            state["poll"] = win.after(100, poll)

    def refresh():
        if state["closed"] or state["busy"]:
            return
        state["busy"] = True
        state["generation"] += 1
        generation = state["generation"]
        refresh_button.configure(state="disabled")
        status.set("Перевіряю бібліотеку…")

        def worker():
            with _READER_SLOT:
                try:
                    view = inspect_workspace_library(
                        services.workspace.root, services.app_version)
                except Exception as exc:
                    # Unexpected read errors are presented without exposing source data.
                    from template_library_service import LibraryView
                    from template_library_reader import default_library_root
                    view = LibraryView(
                        status="UNAVAILABLE", summary="Помилка читання бібліотеки.",
                        detail=type(exc).__name__,
                        root=default_library_root(services.workspace.root),
                        package_version="", rows=(),
                    )
                results.put((generation, view))

        threading.Thread(target=worker, name="Taxo-template-library-reader",
                         daemon=True).start()

    refresh_button.configure(command=refresh)
    state["poll"] = win.after(100, poll)
    refresh()
    return win
