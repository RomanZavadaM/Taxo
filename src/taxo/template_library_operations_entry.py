# -*- coding: utf-8 -*-
"""Make the template library discoverable in the existing Operations window.

The historical Operations screen is owned by v10710_features. Rather than
editing that legacy implementation, this thin extension adds one button in an
unused cell of its existing "Накази та розпорядження" group. The button opens
the independent, read-only r6 library browser.

No template data, SQL statements, file paths or document operations live here.
"""
from __future__ import annotations

from tkinter import ttk

_GROUP_TITLE = "Накази та розпорядження"
_BUTTON_LABEL = "Бібліотека шаблонів…"
_ENTRY_MARKER = "_taxo_template_library_operations_entry_r7"


def _find_orders_group(window):
    """Find the existing grouped actions without relying on fixed child IDs."""
    pending = [window]
    while pending:
        current = pending.pop()
        try:
            if isinstance(current, ttk.LabelFrame) and current.cget("text") == _GROUP_TITLE:
                return current
            pending.extend(current.winfo_children())
        except (AttributeError, RuntimeError):
            continue
    return None


def add_operations_library_button(window, app):
    """Attach a visible action to the already constructed Operations window.

    Returns True when a new button is inserted; False if the relevant panel or
    application command is unavailable. Repeated calls never duplicate buttons.
    """
    if window is None or getattr(window, _ENTRY_MARKER, False):
        return False
    callback = getattr(app, "show_template_library", None)
    if not callable(callback):
        return False
    group = _find_orders_group(window)
    if group is None:
        return False

    button = ttk.Button(group, text=_BUTTON_LABEL, command=callback)
    button.grid(row=2, column=1, sticky="ew", padx=3, pady=3)
    setattr(window, _ENTRY_MARKER, True)
    return True


def install(_core, base_app, _services):
    """Wrap the Operations opening point after all historic feature layers.

    This is deliberately not a new App class: the existing r6 class already
    supplies show_template_library(). We only expose its command to users.
    """
    import operations_orders_ui

    previous = operations_orders_ui.open_operations_center
    if getattr(previous, _ENTRY_MARKER, False):
        return base_app

    def open_operations_center(app, core_module):
        window = previous(app, core_module)
        add_operations_library_button(window, app)
        return window

    setattr(open_operations_center, _ENTRY_MARKER, True)
    operations_orders_ui.open_operations_center = open_operations_center
    return base_app
