# -*- coding: utf-8 -*-
"""Independent date navigation for the existing Taxo waybill window.

The historical waybill screen is still owned by main.py. This extension keeps
that code untouched and adds only a date-navigation surface around the already
existing waybill_date state and refresh_waybill_issue_list() method.

No SQL, waybill issuance, odometer rules or workspace files are changed here.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from tkinter import messagebox, ttk

DATE_FORMAT = "%d.%m.%Y"
_DATE_LABEL = "Дата графіка:"
_MARKER = "_taxo_waybill_date_navigation_r6"


def parse_waybill_date_text(value):
    """Parse the user-facing DD.MM.YYYY value or raise ValueError."""
    text = str(value or "").strip()
    if not text:
        raise ValueError("Вкажіть дату у форматі ДД.ММ.РРРР.")
    try:
        return datetime.strptime(text, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.") from exc


def apply_waybill_date(app, target):
    """Switch only the open waybill window to target and refresh its rows."""
    if not isinstance(target, date):
        raise TypeError("target must be datetime.date")
    app.waybill_date = target
    value = target.strftime(DATE_FORMAT)
    variable = getattr(app, "waybill_date_label", None)
    if variable is not None:
        variable.set(value)
    window = getattr(app, "waybill_win", None)
    try:
        if window is not None and window.winfo_exists():
            window.title("Шляхівки на %s" % value)
    except (AttributeError, RuntimeError):
        pass
    refresh = getattr(app, "refresh_waybill_issue_list", None)
    if callable(refresh):
        refresh()
    return target


def go_to_entered_waybill_date(app, parent=None):
    """Apply the typed date while preserving the previous day on validation error."""
    variable = getattr(app, "waybill_date_label", None)
    raw = variable.get() if variable is not None else ""
    try:
        target = parse_waybill_date_text(raw)
    except ValueError as exc:
        current = getattr(app, "waybill_date", None)
        if variable is not None and isinstance(current, date):
            variable.set(current.strftime(DATE_FORMAT))
        messagebox.showerror(
            "Шляхівки", str(exc),
            parent=parent or getattr(app, "waybill_win", None),
        )
        return False
    apply_waybill_date(app, target)
    return True


def open_waybill_calendar(app, picker, parent):
    """Reuse the schedule calendar; refresh only after an actual day selection."""
    variable = getattr(app, "waybill_date_label", None)
    current = getattr(app, "waybill_date", None)
    if variable is None or not isinstance(current, date):
        return False
    # The displayed date may be an unsubmitted draft. Start from the active day.
    old_value = current.strftime(DATE_FORMAT)
    variable.set(old_value)
    picker(parent, variable)
    if variable.get() == old_value:
        return False  # Calendar cancelled or same day selected.
    return go_to_entered_waybill_date(app, parent)


def shift_waybill_date(app, days):
    """Move the waybill window by a whole number of calendar days."""
    current = getattr(app, "waybill_date", None)
    if not isinstance(current, date):
        variable = getattr(app, "waybill_date_label", None)
        current = parse_waybill_date_text(variable.get() if variable is not None else "")
    return apply_waybill_date(app, current + timedelta(days=int(days)))


def _walk_widgets(root):
    pending = [root]
    while pending:
        current = pending.pop(0)
        yield current
        try:
            pending.extend(current.winfo_children())
        except (AttributeError, RuntimeError):
            continue


def _find_date_bar(window):
    for widget in _walk_widgets(window):
        try:
            if isinstance(widget, ttk.Label) and widget.cget("text") == _DATE_LABEL:
                return widget.master
        except (AttributeError, RuntimeError):
            continue
    return None


def _remove_old_value_label(frame, variable):
    variable_name = str(variable)
    for child in frame.winfo_children():
        try:
            if isinstance(child, ttk.Label) and child.cget("textvariable") == variable_name:
                child.pack_forget()
                return child
        except (AttributeError, RuntimeError):
            continue
    return None


def add_waybill_date_navigation(window, app, calendar_button=None, calendar_picker=None):
    """Add one independent date field to the already constructed waybill window."""
    if window is None or getattr(window, _MARKER, False):
        return False
    variable = getattr(app, "waybill_date_label", None)
    if variable is None:
        return False
    frame = _find_date_bar(window)
    if frame is None:
        return False

    _remove_old_value_label(frame, variable)
    entry = ttk.Entry(frame, textvariable=variable, width=12)
    entry.pack(side="left", padx=(4, 5))
    if calendar_button is not None and calendar_picker is not None:
        # Actual shared «Дата…» control from the main schedule (same calendar).
        calendar = calendar_button(frame, variable)
        calendar.configure(command=lambda: open_waybill_calendar(app, calendar_picker, window))
        calendar.pack(side="left", padx=(0, 5))
    ttk.Button(frame, text="День -", width=8,
               command=lambda: shift_waybill_date(app, -1)).pack(side="left", padx=2)
    ttk.Button(frame, text="Сьогодні", width=9,
               command=lambda: apply_waybill_date(app, date.today())).pack(side="left", padx=2)
    ttk.Button(frame, text="День +", width=8,
               command=lambda: shift_waybill_date(app, 1)).pack(side="left", padx=2)
    ttk.Button(frame, text="Перейти", width=9,
               command=lambda: go_to_entered_waybill_date(app, window)).pack(side="left", padx=(5, 2))
    entry.bind("<Return>", lambda _event: go_to_entered_waybill_date(app, window))
    entry.bind("<KP_Enter>", lambda _event: go_to_entered_waybill_date(app, window))
    entry.configure(takefocus=True)
    setattr(window, _MARKER, True)
    return True


def install(_core, base_app):
    """Attach date navigation after the historical waybill UI is built."""
    class TaxoWaybillDateNavigationApp(base_app):
        def show_waybills_for_schedule(self):
            result = super().show_waybills_for_schedule()
            window = getattr(self, "waybill_win", None)
            try:
                exists = window is not None and window.winfo_exists()
            except (AttributeError, RuntimeError):
                exists = False
            if exists:
                add_waybill_date_navigation(
                    window, self,
                    calendar_button=_core.calendar_button,
                    calendar_picker=_core.show_calendar_picker,
                )
            return result

    TaxoWaybillDateNavigationApp.__name__ = "App"
    TaxoWaybillDateNavigationApp.__qualname__ = "App"
    return TaxoWaybillDateNavigationApp
