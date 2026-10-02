# -*- coding: utf-8 -*-
"""Taxo 10.8-r3 — TCC statement date fix and vehicle requisites entry."""
from __future__ import annotations

from datetime import date, datetime

import military_transport_statement as statement

APP_VERSION = "10.8-r3"


def normalize_statement_day(value):
    """Return ISO YYYY-MM-DD for accepted Taxo date representations.

    UI uses DD.MM.YYYY, while database comparisons use ISO.  Keep both accepted
    so historical callers that already pass ISO continue to work.
    """
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        return date.today().isoformat()
    head = text[:10]
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(head, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(
        "Некоректна дата відомості: %r. Використовуйте ДД.ММ.РРРР." % text
    )


def _selected_vehicle_id(app):
    tree = getattr(app, "vehicle_tree", None)
    if tree is None:
        return None
    selected = tree.selection()
    if not selected:
        return None
    iid = selected[0]
    try:
        candidate = int(iid)
    except (TypeError, ValueError):
        candidate = None
    con = app._taxo_v1083_core.db()
    try:
        if candidate is not None:
            row = con.execute("SELECT id FROM vehicles WHERE id=?", (candidate,)).fetchone()
            if row:
                return int(row[0])
        item = tree.item(iid)
        values = [str(v or "").strip() for v in item.get("values", ())]
        text = str(item.get("text") or "").strip()
        probes = [v for v in values if v]
        if text:
            probes.append(text)
        for probe in probes:
            row = con.execute(
                "SELECT id FROM vehicles WHERE plate=? OR name=? ORDER BY id LIMIT 1",
                (probe, probe),
            ).fetchone()
            if row:
                return int(row[0])
    finally:
        con.close()
    return None


def _open_vehicle_statement_requisites(app, core):
    vehicle_id = _selected_vehicle_id(app)
    if vehicle_id is None:
        core.messagebox.showinfo(
            "Реквізити ТЦК",
            "Спочатку виберіть транспортний засіб у списку.",
            parent=app,
        )
        return
    con = core.db()
    try:
        statement.ensure_schema_on_connection(con)
        vehicle = con.execute("SELECT id,name,plate FROM vehicles WHERE id=?", (vehicle_id,)).fetchone()
        current = statement.get_vehicle_statement_data(con, vehicle_id)
    finally:
        con.close()

    win = core.tk.Toplevel(app)
    win.title("Реквізити ТЦК — %s" % ((vehicle["plate"] or vehicle["name"]) if vehicle else vehicle_id))
    win.transient(app)
    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)

    scope_var = core.tk.StringVar(value=(current["report_scope"] if current else statement.SCOPE_UNKNOWN))
    type_var = core.tk.StringVar(value=(current["vehicle_type"] if current else ""))
    condition_var = core.tk.StringVar(value=(current["technical_condition"] if current else ""))
    value_var = core.tk.StringVar(value=(current["residual_book_value_thousand_uah"] if current else ""))

    labels = {
        statement.SCOPE_UNKNOWN: statement.SCOPE_LABELS[statement.SCOPE_UNKNOWN],
        statement.SCOPE_OWN: statement.SCOPE_LABELS[statement.SCOPE_OWN],
        statement.SCOPE_EXCLUDED: statement.SCOPE_LABELS[statement.SCOPE_EXCLUDED],
    }
    reverse_labels = {v: k for k, v in labels.items()}
    scope_label = core.tk.StringVar(value=labels.get(scope_var.get(), labels[statement.SCOPE_UNKNOWN]))

    core.ttk.Label(body, text="Відомість ТЦК / власний парк:").grid(row=0, column=0, sticky="w", padx=(0,8), pady=4)
    combo = core.ttk.Combobox(body, textvariable=scope_label, values=list(reverse_labels), state="readonly")
    combo.grid(row=0, column=1, sticky="ew", pady=4)
    core.ttk.Label(body, text="Тип ТЗ:").grid(row=1, column=0, sticky="w", padx=(0,8), pady=4)
    core.ttk.Entry(body, textvariable=type_var).grid(row=1, column=1, sticky="ew", pady=4)
    core.ttk.Label(body, text="Технічний стан:").grid(row=2, column=0, sticky="w", padx=(0,8), pady=4)
    core.ttk.Entry(body, textvariable=condition_var).grid(row=2, column=1, sticky="ew", pady=4)
    core.ttk.Label(body, text="Залишкова (балансова) вартість, тис. грн:").grid(row=3, column=0, sticky="w", padx=(0,8), pady=4)
    core.ttk.Entry(body, textvariable=value_var).grid(row=3, column=1, sticky="ew", pady=4)
    core.ttk.Label(body, text="Примітка:").grid(row=4, column=0, sticky="nw", padx=(0,8), pady=4)
    note = core.tk.Text(body, height=4, width=45)
    note.grid(row=4, column=1, sticky="nsew", pady=4)
    if current:
        note.insert("1.0", str(current["note"] or ""))

    core.ttk.Label(
        body,
        text="Ці реквізити необов'язкові для картки ТЗ, але використовуються при формуванні відомості ТЦК.",
        style="Muted.TLabel",
        wraplength=620,
    ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8,4))

    buttons = core.ttk.Frame(body)
    buttons.grid(row=6, column=0, columnspan=2, sticky="e", pady=(10,0))

    def save():
        con2 = core.db()
        try:
            statement.set_vehicle_statement_data(
                con2,
                vehicle_id,
                report_scope=reverse_labels.get(scope_label.get(), statement.SCOPE_UNKNOWN),
                vehicle_type=type_var.get(),
                technical_condition=condition_var.get(),
                residual_book_value_thousand_uah=value_var.get(),
                note=note.get("1.0", "end").strip(),
            )
            con2.commit()
        except Exception as exc:
            con2.rollback()
            core.messagebox.showerror("Реквізити ТЦК", str(exc), parent=win)
            return
        finally:
            con2.close()
        win.destroy()

    core.ttk.Button(buttons, text="Скасувати", command=win.destroy).pack(side="right", padx=(6,0))
    core.ttk.Button(buttons, text="Зберегти", style="Accent.TButton", command=save).pack(side="right")


def install(core, base_app):
    if getattr(core, "_TAXO_1083_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION
    statement._iso_day = normalize_statement_day

    class Taxo1083App(base_app):
        _taxo_v1083_core = core

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            try:
                self.title("Taxo %s — Працівники, графіки та шляхівки" % APP_VERSION)
            except Exception:
                pass
            self.after_idle(self._taxo_v1083_add_vehicle_requisites_button)

        def _taxo_v1083_add_vehicle_requisites_button(self):
            frame = getattr(self, "vehicle_core_toolbar", None)
            if frame is None or getattr(self, "_taxo_v1083_requisites_button", None) is not None:
                return
            button = core.ttk.Button(
                frame,
                text="Реквізити ТЦК",
                command=lambda: _open_vehicle_statement_requisites(self, core),
            )
            existing = list(getattr(self, "vehicle_core_action_buttons", ()))
            existing.append(button)
            self.vehicle_core_action_buttons = tuple(existing)
            self._taxo_v1083_requisites_button = button
            try:
                from v1081_features import _layout_toolbar
                _layout_toolbar(self)
            except Exception:
                button.grid(row=0, column=len(existing)-1, padx=4, pady=2, sticky="w")

    Taxo1083App.__name__ = "App"
    Taxo1083App.__qualname__ = "App"
    core._TAXO_1083_INSTALLED = True
    core.App = Taxo1083App
    return Taxo1083App
