# -*- coding: utf-8 -*-
"""Preview, immutable snapshot save and DOCX export for CompanyTemplateDraft.

The rendered text stays read-only. A DOCX can be exported only after the draft
has been committed as an immutable PreparedDocuments snapshot. Export reloads
that verified snapshot; it does not render from a live template and does not
create a business fact, PDF, print job, final archive entry, scan or signature.
"""
from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from prepared_document_docx import (
    export_prepared_snapshot_docx,
    suggested_docx_name,
)
from prepared_document_store import create_prepared_snapshot
from prepared_document_registry import register_prepared_document

_SNAPSHOT_WRITER_SLOT = threading.BoundedSemaphore(1)
_DOCX_EXPORT_SLOT = threading.BoundedSemaphore(1)


def open_company_template_draft_preview(parent, services, draft):
    """Show a draft, freeze it as a snapshot, then optionally export DOCX."""
    from tkinter import StringVar, TclError, Text, Toplevel

    workspace_root = services.workspace.root
    win = Toplevel(parent)
    win.title("Taxo — Чернетка документа")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 1020, 720, 760, 500)
    except (ImportError, AttributeError, TypeError):
        win.geometry("1020x720")

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.rowconfigure(2, weight=1)
    body.columnconfigure(0, weight=1)

    ttk.Label(
        body,
        text=draft.title or "Чернетка документа",
        font=("TkDefaultFont", 13, "bold"),
    ).grid(row=0, column=0, sticky="w")

    ttk.Label(
        body,
        text=(
            "Перегляд у пам’яті. Шаблон і бізнес-дані не змінюються. "
            "Джерело: власна редакція r%d · SHA-256 %s…"
            % (draft.edit_revision, draft.source_sha256[:12])
        ),
        justify="left",
        wraplength=940,
    ).grid(row=1, column=0, sticky="ew", pady=(5, 8))

    frame = ttk.Frame(body)
    frame.grid(row=2, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    text = Text(frame, wrap="word", state="normal")
    ybar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
    xbar = ttk.Scrollbar(frame, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    text.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    text.insert("1.0", draft.content)
    text.configure(state="disabled")

    footer = ttk.Frame(body)
    footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    footer.columnconfigure(0, weight=1)

    status = StringVar(
        value=(
            "Snapshot ще не створено. Спочатку зафіксуйте чернетку; "
            "DOCX експортується лише з immutable snapshot-а."
        )
    )
    ttk.Label(
        footer,
        textvariable=status,
        justify="left",
        wraplength=560,
    ).grid(row=0, column=0, sticky="w")

    save_button = ttk.Button(
        footer,
        text="Зберегти підготовлену чернетку",
    )
    save_button.grid(row=0, column=1, padx=(8, 6))

    export_button = ttk.Button(
        footer,
        text="Експорт DOCX…",
        state="disabled",
    )
    export_button.grid(row=0, column=2, padx=(0, 6))

    register_button = ttk.Button(
        footer, text="Зберегти DOCX у каталозі Taxo", state="disabled"
    )
    register_button.grid(row=1, column=1, columnspan=2, sticky="e", pady=(6, 0))

    close_button = ttk.Button(footer, text="Закрити")
    close_button.grid(row=0, column=3)

    messages = queue.Queue()
    state = {
        "closed": False,
        "saving": False,
        "saved": False,
        "snapshot_id": "",
        "exporting": False,
        "registering": False,
        "registered": False,
        "after": None,
    }
    win._taxo_prepared_snapshot_state = state

    def close():
        if state["closed"]:
            return
        if state["saving"] or state["exporting"] or state["registering"]:
            messagebox.showinfo(
                "Підготовлена чернетка",
                "Збереження або експорт документа ще виконується.",
                parent=win,
            )
            return
        state["closed"] = True
        if state["after"] is not None:
            try:
                win.after_cancel(state["after"])
            except TclError:
                pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close)
    close_button.configure(command=close)

    def save_snapshot():
        if state["closed"] or state["saving"] or state["saved"]:
            return
        state["saving"] = True
        save_button.configure(state="disabled")
        status.set("Зберігаю immutable snapshot у PreparedDocuments…")

        def worker():
            with _SNAPSHOT_WRITER_SLOT:
                try:
                    summary = create_prepared_snapshot(workspace_root, draft)
                    messages.put(("snapshot", True, summary))
                except Exception as exc:
                    messages.put(("snapshot", False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-snapshot-save",
            daemon=True,
        ).start()

    save_button.configure(command=save_snapshot)

    def export_docx():
        if (
            state["closed"]
            or state["saving"]
            or state["exporting"]
            or not state["snapshot_id"]
        ):
            return

        target_name = filedialog.asksaveasfilename(
            parent=win,
            title="Зберегти DOCX",
            defaultextension=".docx",
            filetypes=[("Word DOCX", "*.docx")],
            initialfile=suggested_docx_name(
                draft.title,
                state["snapshot_id"],
            ),
        )
        if not target_name:
            return

        target = Path(target_name)
        snapshot_id = state["snapshot_id"]
        state["exporting"] = True
        export_button.configure(state="disabled")
        status.set("Створюю editable DOCX з immutable snapshot-а…")

        def worker():
            with _DOCX_EXPORT_SLOT:
                try:
                    path = export_prepared_snapshot_docx(
                        workspace_root,
                        snapshot_id,
                        target,
                        overwrite=True,
                    )
                    messages.put(("docx", True, path))
                except Exception as exc:
                    messages.put(("docx", False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-docx-export",
            daemon=True,
        ).start()

    export_button.configure(command=export_docx)

    def register_docx():
        if (state["closed"] or state["saving"] or state["exporting"]
                or state["registering"] or state["registered"]
                or not state["snapshot_id"]):
            return
        snapshot_id = state["snapshot_id"]
        state["registering"] = True
        register_button.configure(state="disabled")
        status.set("Зберігаю документ у каталозі Taxo…")

        def worker():
            with _DOCX_EXPORT_SLOT:
                try:
                    path = register_prepared_document(workspace_root, snapshot_id)
                    messages.put(("registered", True, path))
                except Exception as exc:
                    messages.put(("registered", False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-catalog-register",
            daemon=True,
        ).start()

    register_button.configure(command=register_docx)

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                kind, ok, payload = messages.get_nowait()
                if kind == "snapshot":
                    state["saving"] = False
                    if ok:
                        state["saved"] = True
                        state["snapshot_id"] = payload.snapshot_id
                        save_button.configure(state="disabled")
                        export_button.configure(state="normal")
                        register_button.configure(state="normal")
                        status.set(
                            "Збережено immutable snapshot %s · SHA-256 %s… "
                            "DOCX можна експортувати з цього exact snapshot-а."
                            % (payload.snapshot_id, payload.sha256[:12])
                        )
                    else:
                        save_button.configure(state="normal")
                        status.set("Не вдалося зберегти snapshot.")
                        messagebox.showerror(
                            "Підготовлена чернетка",
                            str(payload),
                            parent=win,
                        )
                elif kind == "registered":
                    state["registering"] = False
                    if ok:
                        state["registered"] = True
                        status.set(
                            "DOCX збережено в каталозі Taxo: %s. "
                            "Це підготовлений документ, не підтверджений підпис."
                            % payload.name
                        )
                    else:
                        register_button.configure(state="normal")
                        status.set("Документ не вдалося зареєструвати.")
                        messagebox.showerror(
                            "Каталог документів", str(payload), parent=win
                        )
                elif kind == "docx":
                    state["exporting"] = False
                    export_button.configure(state="normal")
                    if ok:
                        status.set(
                            "DOCX створено з immutable snapshot-а: %s"
                            % payload.name
                        )
                    else:
                        status.set("Не вдалося створити DOCX.")
                        messagebox.showerror(
                            "Експорт DOCX",
                            str(payload),
                            parent=win,
                        )
        except queue.Empty:
            pass
        if not state["closed"]:
            state["after"] = win.after(120, poll)

    state["after"] = win.after(120, poll)
    return win
