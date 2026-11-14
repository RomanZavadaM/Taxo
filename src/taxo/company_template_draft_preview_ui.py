# -*- coding: utf-8 -*-
"""Read-only Tk preview for an in-memory CompanyTemplateDraft."""
from __future__ import annotations

from tkinter import ttk


def open_company_template_draft_preview(parent, draft):
    """Show one rendered draft without any save/export/business action."""
    from tkinter import END, Text, Toplevel

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
            "Лише перегляд у пам’яті. "
            "Шаблон, БД, накази/інструктажі та архів документів не змінюються. "
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
    ttk.Button(footer, text="Закрити", command=win.destroy).grid(
        row=0, column=1
    )

    win.protocol("WM_DELETE_WINDOW", win.destroy)
    return win
