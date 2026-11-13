# -*- coding: utf-8 -*-
"""Read-only, scrollable preview window for one Taxo template revision.

No printing, editing, text interpolation, archiving or document generation.
A bounded worker loads the verified template; all Tk calls remain on the main
thread. The child can be closed without waiting on an unavailable network disk.
"""
from __future__ import annotations

import queue
import threading
from tkinter import Toplevel, StringVar, Text, TclError, ttk

from template_library_preview import load_template_preview

_PREVIEW_READER_SLOT = threading.BoundedSemaphore(1)
_LEGAL = {
    "not_checked": "Нормативні посилання не перевірені",
    "requires_review": "Потрібна перевірка нормативних посилань",
}


def open_template_preview(parent, library_root, app_version, template_id, revision_id):
    """Show one revision read-only and return its child window immediately."""
    window = Toplevel(parent)
    window.title("Taxo — Перегляд шаблону")
    window.geometry("1000x700")
    window.minsize(680, 440)

    body = ttk.Frame(window, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(2, weight=1)

    title = StringVar(value="Завантаження шаблону…")
    ttk.Label(body, textvariable=title, font=("TkDefaultFont", 12, "bold"),
              wraplength=900).grid(row=0, column=0, sticky="ew", pady=(0, 4))
    status = StringVar(value="Текст лише для перегляду. Не є затвердженим документом.")
    ttk.Label(body, textvariable=status, wraplength=900,
              justify="left").grid(row=1, column=0, sticky="ew", pady=(0, 6))

    book = ttk.Notebook(body)
    book.grid(row=2, column=0, sticky="nsew")
    content_page = ttk.Frame(book)
    fields_page = ttk.Frame(book)
    book.add(content_page, text="Текст та додатки")
    book.add(fields_page, text="Поля для заповнення")
    for page in (content_page, fields_page):
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)

    def readonly_text(page):
        widget = Text(page, wrap="word", undo=False, takefocus=1)
        ybar = ttk.Scrollbar(page, orient="vertical", command=widget.yview)
        xbar = ttk.Scrollbar(page, orient="horizontal", command=widget.xview)
        widget.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set, state="disabled")
        widget.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        return widget

    text = readonly_text(content_page)
    fields = readonly_text(fields_page)
    ttk.Button(body, text="Закрити", command=lambda: close()).grid(
        row=3, column=0, sticky="e", pady=(8, 0))

    messages = queue.Queue(maxsize=1)
    state = {"closed": False, "after": None}

    def close():
        if state["closed"]:
            return
        state["closed"] = True
        if state["after"] is not None:
            try:
                window.after_cancel(state["after"])
            except TclError:
                pass
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", close)

    def show(widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def poll():
        if state["closed"]:
            return
        try:
            ok, result = messages.get_nowait()
        except queue.Empty:
            state["after"] = window.after(120, poll)
            return
        if ok:
            title.set(result.title)
            status.set(
                "Редакція: %s  •  Пакет: %s  •  %s. Лише перегляд — дані не підставлено."
                % (result.revision_id, result.package_version,
                   _LEGAL.get(result.legal_review, "Нормативні посилання не перевірені"))
            )
            show(text, result.content or "У шаблоні немає текстового вмісту.")
            lines = [
                "Це перелік полів шаблону, а не форма редагування.",
                "Відомості про працівників та підприємство сюди не завантажуються.",
                "",
            ]
            for v in result.variables:
                lines.append("%s  [%s]  •  %s" % (
                    v.label, v.variable_type, "обов'язкове" if v.required else "необов'язкове"
                ))
                if v.label != v.name:
                    lines.append("    ID: " + v.name)
            if not result.variables:
                lines.append("Полів для заповнення не визначено.")
            if result.description:
                lines.extend(["", "Опис:", result.description])
            if result.source_notes:
                lines.extend(["", "Примітки до джерел:", result.source_notes])
            show(fields, "\n".join(lines))
        else:
            title.set("Не вдалося відкрити шаблон")
            status.set(str(result))
            show(text, "Файл не змінено. Перевірте цілісність бібліотеки та повторіть спробу.")
        state["after"] = None

    def worker():
        with _PREVIEW_READER_SLOT:
            try:
                result = load_template_preview(
                    library_root, app_version, template_id, revision_id
                )
                messages.put((True, result))
            except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
                messages.put((False, "Помилка перевірки: " + str(exc)))
            except Exception as exc:
                messages.put((False, "Помилка читання: " + type(exc).__name__))

    threading.Thread(target=worker, name="Taxo-template-preview", daemon=True).start()
    state["after"] = window.after(120, poll)
    return window
