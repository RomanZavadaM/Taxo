# -*- coding: utf-8 -*-
"""Fact-entry window for in-memory CompanyTemplates draft preview.

The UI loads one exact company-template revision plus read-only registry choices.
All Tk values are collected on the UI thread before a background renderer is
started. The renderer receives plain Python data and writes nothing.
"""
from __future__ import annotations

import queue
import threading
from tkinter import messagebox, ttk

from company_template_draft import (
    load_draft_definition,
    prepare_company_template_draft,
)
from company_template_draft_preview_ui import (
    open_company_template_draft_preview,
)
from company_template_fact_choices import load_fact_choice_catalog
from company_template_fact_widgets import build_fact_control

_FORM_READER_SLOT = threading.BoundedSemaphore(1)
_FORM_RENDER_SLOT = threading.BoundedSemaphore(1)


def open_company_template_draft_form(
    parent,
    services,
    company_template_id,
):
    """Open read-only-fact collection for one exact CompanyTemplates revision."""
    from tkinter import Canvas, TclError, Toplevel

    workspace_root = services.workspace.root
    win = Toplevel(parent)
    win.title("Taxo — Підготувати чернетку")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 900, 720, 720, 500)
    except (ImportError, AttributeError, TypeError):
        win.geometry("900x720")

    outer = ttk.Frame(win, padding=12)
    outer.pack(fill="both", expand=True)
    outer.rowconfigure(2, weight=1)
    outer.columnconfigure(0, weight=1)

    ttk.Label(
        outer,
        text="Підготувати чернетку з власного шаблону",
        font=("TkDefaultFont", 13, "bold"),
    ).grid(row=0, column=0, sticky="w")

    status = ttk.Label(
        outer,
        text=(
            "Завантажую поля шаблону та чинні реєстри Taxo…"
        ),
        justify="left",
        wraplength=820,
    )
    status.grid(row=1, column=0, sticky="ew", pady=(5, 8))

    host = ttk.Frame(outer)
    host.grid(row=2, column=0, sticky="nsew")
    host.rowconfigure(0, weight=1)
    host.columnconfigure(0, weight=1)

    canvas = Canvas(host, highlightthickness=0)
    ybar = ttk.Scrollbar(host, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=ybar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")

    fields_frame = ttk.Frame(canvas)
    window_id = canvas.create_window(
        (0, 0), window=fields_frame, anchor="nw"
    )
    fields_frame.columnconfigure(0, weight=1)

    footer = ttk.Frame(outer)
    footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    footer.columnconfigure(0, weight=1)
    preview_button = ttk.Button(
        footer, text="Переглянути чернетку", state="disabled"
    )
    preview_button.grid(row=0, column=1, padx=(4, 8))
    close_button = ttk.Button(footer, text="Закрити")
    close_button.grid(row=0, column=2)

    messages = queue.Queue()
    state = {
        "closed": False,
        "loading": True,
        "rendering": False,
        "definition": None,
        "catalog": None,
        "controls": {},
        "after": None,
    }
    win._taxo_company_template_draft_form_state = state

    def update_scrollregion(_event=None):
        if state["closed"]:
            return
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfigure(window_id, width=canvas.winfo_width())

    fields_frame.bind("<Configure>", update_scrollregion, add="+")
    canvas.bind("<Configure>", update_scrollregion, add="+")

    def close():
        if state["closed"]:
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

    def render_form(definition, catalog):
        state["definition"] = definition
        state["catalog"] = catalog
        state["controls"].clear()

        for child in fields_frame.winfo_children():
            child.destroy()

        if not definition.variables:
            ttk.Label(
                fields_frame,
                text="У шаблоні немає полів для підстановки.",
            ).grid(row=0, column=0, sticky="w")
            preview_button.configure(state="normal")
        else:
            for row_index, variable in enumerate(definition.variables):
                try:
                    control = build_fact_control(
                        fields_frame, variable, catalog
                    )
                except ValueError as exc:
                    ttk.Label(
                        fields_frame,
                        text="%s: %s" % (variable.label, exc),
                    ).grid(
                        row=row_index,
                        column=0,
                        sticky="ew",
                        pady=(0, 10),
                    )
                    continue
                control.frame.grid(
                    row=row_index,
                    column=0,
                    sticky="ew",
                    pady=(0, 12),
                )
                state["controls"][variable.name] = control
            preview_button.configure(state="normal")

        state["loading"] = False
        status.configure(
            text=(
                "Власна редакція r%d · SHA-256 %s… "
                "Це лише підготовка preview: шаблон і бізнес-дані не змінюються."
                % (
                    definition.edit_revision,
                    definition.source_sha256[:12],
                )
            )
        )
        update_scrollregion()

    def load_worker():
        with _FORM_READER_SLOT:
            try:
                definition = load_draft_definition(
                    workspace_root, company_template_id
                )
                catalog = load_fact_choice_catalog(services)
                messages.put(("load", True, (definition, catalog)))
            except Exception as exc:
                messages.put(("load", False, str(exc)))

    def collect_facts():
        definition = state["definition"]
        facts = {}
        for variable in definition.variables:
            control = state["controls"].get(variable.name)
            if control is None:
                raise ValueError(
                    "Поле «%s» поки не можна заповнити у цьому вікні."
                    % variable.label
                )
            try:
                facts[variable.name] = control.get_value()
            except ValueError as exc:
                raise ValueError("%s: %s" % (variable.label, exc))
        return facts

    def preview():
        if (
            state["loading"]
            or state["rendering"]
            or state["definition"] is None
        ):
            return
        try:
            facts = collect_facts()
        except ValueError as exc:
            messagebox.showerror(
                "Поля чернетки", str(exc), parent=win
            )
            return

        # Everything below is plain Python state captured on the UI thread.
        definition = state["definition"]
        state["rendering"] = True
        preview_button.configure(state="disabled")
        status.configure(text="Готую in-memory чернетку…")

        def worker():
            with _FORM_RENDER_SLOT:
                try:
                    result = prepare_company_template_draft(
                        workspace_root,
                        company_template_id,
                        facts,
                        expected_source_sha256=definition.source_sha256,
                    )
                    messages.put(("render", True, result))
                except Exception as exc:
                    messages.put(("render", False, str(exc)))

        threading.Thread(
            target=worker,
            name="Taxo-company-template-draft-render",
            daemon=True,
        ).start()

    preview_button.configure(command=preview)

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                kind, ok, payload = messages.get_nowait()
                if kind == "load":
                    if ok:
                        definition, catalog = payload
                        render_form(definition, catalog)
                    else:
                        state["loading"] = False
                        status.configure(
                            text="Не вдалося відкрити форму чернетки."
                        )
                        messagebox.showerror(
                            "Чернетка шаблону", str(payload), parent=win
                        )
                elif kind == "render":
                    state["rendering"] = False
                    preview_button.configure(state="normal")
                    definition = state["definition"]
                    status.configure(
                        text=(
                            "Власна редакція r%d · SHA-256 %s… "
                            "Чернетка не зберігається автоматично."
                            % (
                                definition.edit_revision,
                                definition.source_sha256[:12],
                            )
                        )
                    )
                    if ok:
                        open_company_template_draft_preview(win, services, payload)
                    else:
                        messagebox.showerror(
                            "Не вдалося підготувати чернетку",
                            str(payload),
                            parent=win,
                        )
        except queue.Empty:
            pass

        if not state["closed"]:
            state["after"] = win.after(120, poll)

    threading.Thread(
        target=load_worker,
        name="Taxo-company-template-draft-load",
        daemon=True,
    ).start()
    state["after"] = win.after(120, poll)
    return win
