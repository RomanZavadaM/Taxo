# -*- coding: utf-8 -*-
"""Preview and explicit persistence of an in-memory CompanyTemplateDraft.

The rendered text stays read-only. r6 adds one explicit action that stores the
already-rendered draft as an immutable PreparedDocuments snapshot. This does
not create an order/briefing, DOCX/PDF, final document archive entry, scan or signature.
"""
from __future__ import annotations

import queue
import threading
from tkinter import messagebox, ttk

from prepared_document_store import create_prepared_snapshot

_SNAPSHOT_WRITER_SLOT = threading.BoundedSemaphore(1)


def open_company_template_draft_preview(parent, services, draft):
    """Show one rendered draft and optionally freeze it as a prepared snapshot."""
    from tkinter import StringVar, TclError, Text, Toplevel

    workspace_root = services.workspace.root
    win = Toplevel(parent)
    win.title("Taxo — Чернетка документа")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 980, 720, 720, 500)
    except (ImportError, AttributeError, TypeError):
        win.geometry("980x720")

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
        wraplength=900,
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
            "Snapshot ще не створено. Він не є наказом/інструктажем "
            "і не створює DOCX/PDF."
        )
    )
    ttk.Label(
        footer,
        textvariable=status,
        justify="left",
        wraplength=620,
    ).grid(row=0, column=0, sticky="w")

    save_button = ttk.Button(
        footer,
        text="Зберегти підготовлену чернетку",
    )
    save_button.grid(row=0, column=1, padx=(8, 8))
    close_button = ttk.Button(footer, text="Закрити")
    close_button.grid(row=0, column=2)

    messages = queue.Queue()
    state = {
        "closed": False,
        "saving": False,
        "saved": False,
        "after": None,
    }
    win._taxo_prepared_snapshot_state = state

    def close():
        if state["closed"]:
            return
        if state["saving"]:
            messagebox.showinfo(
                "Підготовлена чернетка",
                "Збереження snapshot-а ще виконується.",
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
                    summary = create_prepared_snapshot(
                        workspace_root,
                        draft,
                    )
                    messages.put((True, summary))
                except Exception as exc:
                    messages.put((False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-prepared-document-snapshot-save",
            daemon=True,
        ).start()

    save_button.configure(command=save_snapshot)

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                ok, payload = messages.get_nowait()
                state["saving"] = False
                if ok:
                    state["saved"] = True
                    save_button.configure(state="disabled")
                    status.set(
                        "Збережено immutable snapshot %s · SHA-256 %s…"
                        % (
                            payload.snapshot_id,
                            payload.sha256[:12],
                        )
                    )
                else:
                    save_button.configure(state="normal")
                    status.set("Не вдалося зберегти snapshot.")
                    messagebox.showerror(
                        "Підготовлена чернетка",
                        str(payload),
                        parent=win,
                    )
        except queue.Empty:
            pass
        if not state["closed"]:
            state["after"] = win.after(120, poll)

    state["after"] = win.after(120, poll)
    return win
