# -*- coding: utf-8 -*-
"""Browser for immutable PreparedDocuments snapshots saved in the workspace."""
from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from paper_document_store import list_documents
from prepared_document_docx import (
    export_prepared_snapshot_docx,
    suggested_docx_name,
)
from prepared_document_registry import register_prepared_document
from prepared_document_store import (
    list_prepared_snapshots,
    load_prepared_snapshot,
)

_READER_SLOT = threading.BoundedSemaphore(1)
_WRITER_SLOT = threading.BoundedSemaphore(1)


def _open_snapshot_preview(parent, workspace_root, snapshot_id):
    from tkinter import Text, Toplevel

    snapshot = load_prepared_snapshot(
        Path(workspace_root), snapshot_id
    )
    win = Toplevel(parent)
    win.title("Taxo — Збережена підготовлена чернетка")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 920, 650, 680, 440)
    except (ImportError, AttributeError, TypeError):
        win.geometry("920x650")

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.rowconfigure(2, weight=1)
    body.columnconfigure(0, weight=1)

    ttk.Label(
        body,
        text=snapshot.data["title"],
        font=("TkDefaultFont", 13, "bold"),
    ).grid(row=0, column=0, sticky="w")
    ttk.Label(
        body,
        text=(
            "Snapshot %s · власний шаблон r%d · SHA-256 %s…"
            % (
                snapshot.summary.snapshot_id,
                snapshot.summary.edit_revision,
                snapshot.summary.source_sha256[:12],
            )
        ),
        justify="left",
        wraplength=850,
    ).grid(row=1, column=0, sticky="ew", pady=(5, 8))

    frame = ttk.Frame(body)
    frame.grid(row=2, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    text = Text(frame, wrap="word")
    ybar = ttk.Scrollbar(
        frame, orient="vertical", command=text.yview
    )
    text.configure(yscrollcommand=ybar.set)
    text.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    text.insert("1.0", snapshot.data["rendered_content"])
    text.configure(state="disabled")

    ttk.Button(
        body, text="Закрити", command=win.destroy
    ).grid(row=3, column=0, sticky="e", pady=(8, 0))
    return win


def open_prepared_documents(parent, services):
    """List saved snapshots without requiring the template form to be filled again."""
    from tkinter import StringVar, TclError, Toplevel

    workspace_root = services.workspace.root
    win = Toplevel(parent)
    win.title("Taxo — Збережені чернетки")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 940, 580, 700, 430)
    except (ImportError, AttributeError, TypeError):
        win.geometry("940x580")

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(2, weight=1)

    ttk.Label(
        body,
        text="Збережені підготовлені чернетки",
        font=("TkDefaultFont", 13, "bold"),
    ).grid(row=0, column=0, sticky="w")
    status = StringVar(
        value="Читаю PreparedDocuments…"
    )
    ttk.Label(
        body,
        textvariable=status,
        justify="left",
        wraplength=860,
    ).grid(row=1, column=0, sticky="ew", pady=(6, 7))

    frame = ttk.Frame(body)
    frame.grid(row=2, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    columns = ("created", "title", "template", "status")
    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )
    for key, label, width in (
        ("created", "Створено", 170),
        ("title", "Назва", 390),
        ("template", "Шаблон", 150),
        ("status", "Стан", 150),
    ):
        tree.heading(key, text=label)
        tree.column(
            key,
            width=width,
            minwidth=70,
            stretch=(key == "title"),
        )
    ybar = ttk.Scrollbar(
        frame, orient="vertical", command=tree.yview
    )
    xbar = ttk.Scrollbar(
        frame, orient="horizontal", command=tree.xview
    )
    tree.configure(
        yscrollcommand=ybar.set,
        xscrollcommand=xbar.set,
    )
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

    footer = ttk.Frame(body)
    footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    footer.columnconfigure(0, weight=1)
    refresh_button = ttk.Button(footer, text="Оновити")
    preview_button = ttk.Button(
        footer, text="Переглянути", state="disabled"
    )
    export_button = ttk.Button(
        footer, text="Експорт DOCX…", state="disabled"
    )
    register_button = ttk.Button(
        footer, text="До каталогу Taxo", state="disabled"
    )
    refresh_button.grid(row=0, column=1, padx=(4, 8))
    preview_button.grid(row=0, column=2, padx=(4, 8))
    export_button.grid(row=0, column=3, padx=(4, 8))
    register_button.grid(row=0, column=4, padx=(4, 8))
    ttk.Button(
        footer, text="Закрити", command=lambda: close()
    ).grid(row=0, column=5)

    results = queue.Queue()
    actions = queue.Queue()
    state = {
        "closed": False,
        "busy": False,
        "action_busy": False,
        "generation": 0,
        "rows": {},
        "registered": set(),
        "after": None,
    }
    win._taxo_prepared_documents_state = state

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

    def selected_id():
        selected = tree.selection()
        return selected[0] if selected else ""

    def update_actions(_event=None):
        snapshot_id = selected_id()
        enabled = bool(snapshot_id) and not state["busy"] and not state["action_busy"]
        preview_button.configure(
            state="normal" if enabled else "disabled"
        )
        export_button.configure(
            state="normal" if enabled else "disabled"
        )
        register_button.configure(
            state=(
                "normal"
                if enabled and snapshot_id not in state["registered"]
                else "disabled"
            )
        )

    def render(payload):
        snapshots, registered, catalog_error = payload
        previous = selected_id()
        state["registered"] = registered
        state["rows"] = {
            item.snapshot_id: item for item in snapshots
        }
        tree.delete(*tree.get_children())
        for item in snapshots:
            tree.insert(
                "",
                "end",
                iid=item.snapshot_id,
                values=(
                    item.created_at.replace("T", " "),
                    item.title,
                    "r%d" % item.edit_revision,
                    (
                        "У каталозі Taxo"
                        if item.snapshot_id in registered
                        else "Лише snapshot"
                    ),
                ),
            )
        if previous and tree.exists(previous):
            tree.selection_set(previous)
            tree.see(previous)
        text = "Збережених чернеток: %d." % len(snapshots)
        if catalog_error:
            text += " Каталог документів не прочитано: " + catalog_error
        status.set(text)
        update_actions()

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
                    render(payload)
                else:
                    status.set("Не вдалося прочитати PreparedDocuments.")
                    messagebox.showerror(
                        "Збережені чернетки", str(payload), parent=win
                    )
                update_actions()
        except queue.Empty:
            pass

        try:
            while True:
                kind, ok, payload = actions.get_nowait()
                state["action_busy"] = False
                if ok:
                    if kind == "export":
                        status.set(
                            "DOCX створено: %s" % payload.name
                        )
                    elif kind == "register":
                        messagebox.showinfo(
                            "Каталог Taxo",
                            "DOCX збережено у каталозі Taxo. "
                            "Це prepared-документ, не факт підпису.",
                            parent=win,
                        )
                        refresh()
                else:
                    messagebox.showerror(
                        (
                            "Експорт DOCX"
                            if kind == "export"
                            else "Каталог Taxo"
                        ),
                        str(payload),
                        parent=win,
                    )
                update_actions()
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
        update_actions()
        status.set("Читаю PreparedDocuments…")

        def worker():
            with _READER_SLOT:
                try:
                    snapshots = list_prepared_snapshots(
                        workspace_root
                    )
                    catalog_error = ""
                    try:
                        registered = {
                            row.get("prepared_snapshot_id")
                            for row in list_documents(workspace_root)
                            if row.get("prepared_snapshot_id")
                        }
                    except Exception as exc:
                        registered = set()
                        catalog_error = str(exc)
                    results.put(
                        (
                            generation,
                            True,
                            (snapshots, registered, catalog_error),
                        )
                    )
                except Exception as exc:
                    results.put(
                        (generation, False, str(exc))
                    )

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-list",
            daemon=True,
        ).start()

    def preview_selected(_event=None):
        snapshot_id = selected_id()
        if not snapshot_id:
            return
        try:
            _open_snapshot_preview(
                win, workspace_root, snapshot_id
            )
        except Exception as exc:
            messagebox.showerror(
                "Збережена чернетка", str(exc), parent=win
            )

    def export_selected():
        snapshot_id = selected_id()
        item = state["rows"].get(snapshot_id)
        if item is None or state["action_busy"]:
            return
        target = filedialog.asksaveasfilename(
            parent=win,
            title="Зберегти DOCX",
            defaultextension=".docx",
            filetypes=[("Word DOCX", "*.docx")],
            initialfile=suggested_docx_name(
                item.title, snapshot_id
            ),
        )
        if not target:
            return
        state["action_busy"] = True
        update_actions()

        def worker():
            with _WRITER_SLOT:
                try:
                    path = export_prepared_snapshot_docx(
                        workspace_root,
                        snapshot_id,
                        Path(target),
                        overwrite=True,
                    )
                    actions.put(("export", True, path))
                except Exception as exc:
                    actions.put(("export", False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-reexport",
            daemon=True,
        ).start()

    def register_selected():
        snapshot_id = selected_id()
        if (
            not snapshot_id
            or snapshot_id in state["registered"]
            or state["action_busy"]
        ):
            return
        state["action_busy"] = True
        update_actions()

        def worker():
            with _WRITER_SLOT:
                try:
                    path = register_prepared_document(
                        workspace_root, snapshot_id
                    )
                    actions.put(("register", True, path))
                except Exception as exc:
                    actions.put(("register", False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-reregister",
            daemon=True,
        ).start()

    tree.bind(
        "<<TreeviewSelect>>", update_actions, add="+"
    )
    tree.bind(
        "<Double-1>", preview_selected, add="+"
    )
    tree.bind(
        "<Return>", preview_selected, add="+"
    )
    refresh_button.configure(command=refresh)
    preview_button.configure(command=preview_selected)
    export_button.configure(command=export_selected)
    register_button.configure(command=register_selected)
    state["after"] = win.after(120, poll)
    refresh()
    return win
