# -*- coding: utf-8 -*-
"""Taxo 10.7-r10 — grouped document center inside «Експлуатація».

This layer does not remove legacy entry points. It gives the user one grouped place
for frequently used document/form actions while keeping existing modules intact.
"""
from __future__ import annotations

APP_VERSION = "10.7-r10"

DOCUMENT_CENTER_GROUPS = (
    ("Операційні документи", (
        ("Шляхові листи на день", "show_waybills_for_schedule"),
    )),
    ("Транспорт", (
        ("Контроль документів ТЗ", "vehicle_document_control"),
    )),
    ("Військовий облік", (
        ("Відомість ТЦК — транспорт підприємства", "open_military_transport_statement"),
    )),
    ("Персонал", (
        ("Реєстр усіх працівників", "show_employee_registry"),
    )),
)


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _find_notebook(win):
    for widget in _walk(win):
        try:
            if widget.winfo_class() == "TNotebook":
                return widget
        except Exception:
            pass
    return None


def _select_tab(book, title):
    for tab_id in book.tabs():
        try:
            if str(book.tab(tab_id, "text")) == title:
                book.select(tab_id)
                return True
        except Exception:
            pass
    return False


def _invoke(app, method_name, core, parent):
    callback = getattr(app, method_name, None)
    if not callable(callback):
        core.messagebox.showinfo(
            "Документи",
            "Ця дія недоступна у поточній конфігурації Taxo.",
            parent=parent,
        )
        return
    callback()


def _install_document_tab(app, core, win):
    if not _alive(win) or getattr(win, "_taxo_v10710_documents", False):
        return win
    book = _find_notebook(win)
    if book is None:
        return win

    tab = core.ttk.Frame(book)
    try:
        book.insert(0, tab, text="Документи")
    except Exception:
        book.add(tab, text="Документи")

    shell = core.ttk.Frame(tab, padding=14)
    shell.pack(fill="both", expand=True)
    shell.columnconfigure(0, weight=1)
    shell.columnconfigure(1, weight=1)

    core.ttk.Label(
        shell,
        text="Документи підприємства",
        style="HeroTitle.TLabel",
    ).grid(row=0, column=0, columnspan=2, sticky="w")
    core.ttk.Label(
        shell,
        text=("Єдина точка входу до форм і реєстрів. Старі кнопки та меню залишені, "
              "щоб не ламати звичні сценарії роботи."),
        style="Muted.TLabel",
        wraplength=980,
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 12))

    row = 2
    for idx, (group_title, actions) in enumerate(DOCUMENT_CENTER_GROUPS):
        box = core.ttk.LabelFrame(shell, text=group_title, padding=10)
        box.grid(row=row + idx // 2, column=idx % 2, sticky="nsew", padx=(0 if idx % 2 == 0 else 6, 6 if idx % 2 == 0 else 0), pady=6)
        box.columnconfigure(0, weight=1)
        for action_row, (label, method_name) in enumerate(actions):
            core.ttk.Button(
                box,
                text=label,
                command=lambda m=method_name: _invoke(app, m, core, win),
            ).grid(row=action_row, column=0, sticky="ew", pady=3)

    internal = core.ttk.LabelFrame(shell, text="Накази та розпорядження", padding=10)
    internal.grid(row=row + 2, column=0, columnspan=2, sticky="ew", pady=(10, 4))
    for col, (label, target) in enumerate((
        ("Реєстр наказів", "Накази"),
        ("Закріплення водіїв", "Закріплення водіїв"),
        ("Відповідальні особи", "Відповідальні"),
        ("Каталог типів наказів", "Каталог наказів"),
    )):
        internal.columnconfigure(col, weight=1)
        core.ttk.Button(
            internal,
            text=label,
            command=lambda t=target: _select_tab(book, t),
        ).grid(row=0, column=col, sticky="ew", padx=3)

    core.ttk.Label(
        shell,
        text=("Відомість ТЦК як і раніше вимагає внутрішнього затвердження відповідальним перед експортом. "
              "Дані з реєстрів/Дії використовуються лише після підтвердженого перенесення у робочі реквізити Taxo."),
        style="Muted.TLabel",
        wraplength=980,
        justify="left",
    ).grid(row=row + 3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    win._taxo_v10710_documents = True
    return win


def install(core, base_app):
    if getattr(core, "_TAXO_V10710_INSTALLED", False):
        return base_app

    import operations_orders_ui as operations_ui

    original_open = operations_ui.open_operations_center
    if not getattr(original_open, "_taxo_v10710_wrapped", False):
        def open_operations_center(app, core_module):
            win = original_open(app, core_module)
            return _install_document_tab(app, core_module, win)
        open_operations_center._taxo_v10710_wrapped = True
        operations_ui.open_operations_center = open_operations_center

    core.APP_VERSION = APP_VERSION
    core._TAXO_V10710_INSTALLED = True
    return base_app
