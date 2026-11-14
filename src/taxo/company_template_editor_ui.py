# -*- coding: utf-8 -*-
"""Tk editor for one user-owned CompanyTemplates revision.

Template content is accessed only through the editor service. Vendor
TemplateLibrary data is never edited here. Reads and writes run outside the Tk
thread, and all close paths protect unsaved user text.
"""
from __future__ import annotations

import queue
import threading
from tkinter import messagebox, ttk

from company_template_editor_service import load_editor_model, save_editor_model

_EDITOR_READER_SLOT = threading.BoundedSemaphore(1)
_EDITOR_WRITER_SLOT = threading.BoundedSemaphore(1)


def open_company_template_editor(
    parent,
    services,
    company_template_id,
    on_saved=None,
):
    """Open one text-only company-template editor."""
    from tkinter import END, StringVar, Text, TclError, Toplevel

    win = Toplevel(parent)
    win.title("Taxo — Редактор власного шаблону")
    try:
        from window_layout import fit_window_to_screen
        fit_window_to_screen(win, 1040, 700, 760, 500)
    except (ImportError, AttributeError, TypeError):
        win.geometry("1040x700")

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(3, weight=1)

    status = StringVar(value="Завантажую шаблон…")
    ttk.Label(
        body, textvariable=status, justify="left", wraplength=930
    ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 7))

    ttk.Label(body, text="Назва:").grid(row=1, column=0, sticky="w")
    title = StringVar(value="")
    title_entry = ttk.Entry(body, textvariable=title, state="disabled")
    title_entry.grid(row=1, column=1, sticky="ew", pady=(0, 7))

    ttk.Label(body, text="Частина шаблону:").grid(
        row=2, column=0, columnspan=2, sticky="w"
    )

    field_frame = ttk.Frame(body)
    field_frame.grid(row=3, column=0, sticky="nsew", padx=(0, 8))
    field_frame.rowconfigure(0, weight=1)
    field_frame.columnconfigure(0, weight=1)
    fields = ttk.Treeview(
        field_frame,
        columns=("section", "label"),
        show="headings",
        selectmode="browse",
        height=18,
    )
    fields.heading("section", text="Розділ")
    fields.heading("label", text="Поле")
    fields.column("section", width=180, minwidth=120, stretch=True)
    fields.column("label", width=260, minwidth=160, stretch=True)
    field_y = ttk.Scrollbar(field_frame, orient="vertical", command=fields.yview)
    fields.configure(yscrollcommand=field_y.set)
    fields.grid(row=0, column=0, sticky="nsew")
    field_y.grid(row=0, column=1, sticky="ns")

    text_frame = ttk.Frame(body)
    text_frame.grid(row=3, column=1, sticky="nsew")
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)
    editor = Text(
        text_frame,
        wrap="word",
        undo=True,
        maxundo=100,
        state="disabled",
        takefocus=1,
    )
    editor_y = ttk.Scrollbar(text_frame, orient="vertical", command=editor.yview)
    editor_x = ttk.Scrollbar(text_frame, orient="horizontal", command=editor.xview)
    editor.configure(yscrollcommand=editor_y.set, xscrollcommand=editor_x.set)
    editor.grid(row=0, column=0, sticky="nsew")
    editor_y.grid(row=0, column=1, sticky="ns")
    editor_x.grid(row=1, column=0, sticky="ew")

    footer = ttk.Frame(body)
    footer.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
    footer.columnconfigure(0, weight=1)
    revision = StringVar(value="")
    ttk.Label(footer, textvariable=revision).grid(row=0, column=0, sticky="w")
    save_button = ttk.Button(footer, text="Зберегти", state="disabled")
    save_button.grid(row=0, column=1, padx=(4, 8))
    cancel_button = ttk.Button(footer, text="Скасувати")
    cancel_button.grid(row=0, column=2)

    messages = queue.Queue()
    state = {
        "closed": False,
        "loading": True,
        "saving": False,
        "model": None,
        "values": {},
        "current_key": None,
        "after": None,
        "loading_widget": False,
    }
    win._taxo_company_template_editor_state = state

    def current_text():
        return editor.get("1.0", "end-1c")

    def stash_current():
        key = state["current_key"]
        if key is not None and state["model"] is not None:
            state["values"][key] = current_text()

    def original_values():
        model = state["model"]
        if model is None:
            return {}
        return {item.key: item.value for item in model.fields}

    def has_changes():
        if state["model"] is None:
            return False
        stash_current()
        if title.get() != state["model"].title:
            return True
        baseline = original_values()
        return any(
            state["values"].get(key, value) != value
            for key, value in baseline.items()
        )

    def update_save_state(*_args):
        if state["loading"] or state["saving"] or state["model"] is None:
            save_button.configure(state="disabled")
            return
        save_button.configure(state="normal" if has_changes() else "disabled")

    def request_close():
        if state["closed"]:
            return
        if state["saving"]:
            messagebox.showinfo(
                "Редактор шаблону",
                "Збереження ще виконується.",
                parent=win,
            )
            return
        if has_changes():
            discard = messagebox.askyesno(
                "Незбережені зміни",
                "Закрити редактор і відкинути незбережені зміни?",
                parent=win,
            )
            if not discard:
                return
        close_now()

    def close_now():
        if state["closed"]:
            return
        state["closed"] = True
        if state["after"] is not None:
            try:
                win.after_cancel(state["after"])
            except TclError:
                pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", request_close)
    cancel_button.configure(command=request_close)

    def load_field(key):
        model = state["model"]
        if model is None:
            return
        field = next((item for item in model.fields if item.key == key), None)
        if field is None:
            return
        state["loading_widget"] = True
        editor.configure(state="normal")
        editor.delete("1.0", END)
        editor.insert("1.0", state["values"].get(key, field.value))
        editor.edit_modified(False)
        state["loading_widget"] = False
        state["current_key"] = key
        editor.focus_set()

    def selection_changed(_event=None):
        if state["loading"] or state["model"] is None:
            return
        stash_current()
        selected = fields.selection()
        if not selected:
            state["current_key"] = None
            editor.configure(state="disabled")
            return
        load_field(selected[0])
        update_save_state()

    fields.bind("<<TreeviewSelect>>", selection_changed, add="+")

    def text_modified(_event=None):
        if state["loading_widget"] or state["model"] is None:
            editor.edit_modified(False)
            return
        if editor.edit_modified():
            stash_current()
            editor.edit_modified(False)
            update_save_state()

    editor.bind("<<Modified>>", text_modified, add="+")
    title.trace_add("write", update_save_state)

    def render_model(model, preferred_key=None):
        state["model"] = model
        state["values"] = {item.key: item.value for item in model.fields}
        state["current_key"] = None
        state["loading"] = False
        title.set(model.title)
        title_entry.configure(state="normal")
        fields.delete(*fields.get_children())
        for item in model.fields:
            fields.insert(
                "", "end", iid=item.key,
                values=(item.section, item.label),
            )
        revision.set(
            "Власна редакція: r%d · %s" % (
                model.edit_revision,
                model.updated_at or "час не вказано",
            )
        )
        if model.fields:
            key = (
                preferred_key
                if preferred_key and fields.exists(preferred_key)
                else model.fields[0].key
            )
            fields.selection_set(key)
            fields.see(key)
            load_field(key)
        else:
            editor.configure(state="disabled")
            status.set(
                "У шаблоні немає текстових полів, доступних у цьому редакторі."
            )
        update_save_state()

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                kind, ok, payload, preferred_key = messages.get_nowait()
                if kind == "load":
                    state["loading"] = False
                    if ok:
                        status.set(
                            "Редагується лише власна копія. "
                            "Початкова бібліотека не змінюється."
                        )
                        render_model(payload)
                    else:
                        status.set("Не вдалося відкрити власний шаблон.")
                        messagebox.showerror(
                            "Редактор шаблону", str(payload), parent=win
                        )
                elif kind == "save":
                    state["saving"] = False
                    title_entry.configure(state="normal")
                    editor.configure(
                        state="normal" if state["model"] else "disabled"
                    )
                    if ok:
                        status.set("Зміни збережено як нову власну редакцію.")
                        render_model(payload, preferred_key=preferred_key)
                        if callable(on_saved):
                            on_saved()
                    else:
                        status.set("Не вдалося зберегти зміни.")
                        messagebox.showerror(
                            "Редактор шаблону", str(payload), parent=win
                        )
                        update_save_state()
        except queue.Empty:
            pass
        if not state["closed"]:
            state["after"] = win.after(120, poll)

    def load_worker():
        with _EDITOR_READER_SLOT:
            try:
                model = load_editor_model(
                    services.workspace.root, company_template_id
                )
                messages.put(("load", True, model, None))
            except Exception as exc:
                messages.put(("load", False, str(exc), None))

    def save():
        if state["loading"] or state["saving"] or state["model"] is None:
            return
        stash_current()
        model = state["model"]
        preferred_key = state["current_key"]
        values = dict(state["values"])
        title_value = title.get()
        state["saving"] = True
        save_button.configure(state="disabled")
        title_entry.configure(state="disabled")
        editor.configure(state="disabled")
        status.set("Зберігаю нову власну редакцію…")

        def worker():
            with _EDITOR_WRITER_SLOT:
                try:
                    result = save_editor_model(
                        services.workspace.root,
                        model.company_template_id,
                        model.expected_sha256,
                        title_value,
                        values,
                    )
                    messages.put(("save", True, result, preferred_key))
                except Exception as exc:
                    messages.put(("save", False, str(exc), preferred_key))

        threading.Thread(
            target=worker,
            name="Taxo-company-template-save",
            daemon=True,
        ).start()

    save_button.configure(command=save)
    threading.Thread(
        target=load_worker,
        name="Taxo-company-template-editor-load",
        daemon=True,
    ).start()
    state["after"] = win.after(120, poll)
    return win
