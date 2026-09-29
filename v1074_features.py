# -*- coding: utf-8 -*-
"""Taxo 10.7-r4 — operations order workflow usability and corrections.

This layer keeps the existing r2/r3 data model but fixes two practical problems:
1) an empty Operations window did not clearly guide the user into creating the
   first order, especially from the Vehicle/driver assignment tab;
2) paper orders may contain clerical mistakes, therefore Taxo must allow the
   working record to be corrected even after it was marked approved internally.

The signed paper original remains the legally relevant physical instance; Taxo
keeps the working data and should warn when a previously printed/signed document
may need to be reprinted/re-signed.
"""
from __future__ import annotations

from datetime import datetime

import operations_orders as ops
import v1073_features as r3

APP_VERSION = "10.7-r4"


def _walk(widget):
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        yield child
        yield from _walk(child)


def _find_notebook(widget):
    for item in _walk(widget):
        try:
            if item.winfo_class() == "TNotebook":
                return item
        except Exception:
            pass
    return None


def _tab_frame(book, text):
    try:
        for tab_id in book.tabs():
            if str(book.tab(tab_id, "text")) == text:
                return book.nametowidget(tab_id)
    except Exception:
        pass
    return None


def _find_button(widget, text):
    for item in _walk(widget):
        try:
            if item.winfo_class() in ("TButton", "Button") and str(item.cget("text")) == text:
                return item
        except Exception:
            pass
    return None


def _find_tree(widget):
    for item in _walk(widget):
        try:
            if item.winfo_class() == "Treeview":
                return item
        except Exception:
            pass
    return None


def _allow_order_corrections():
    """r3 appendices may be corrected regardless of internal status.

    The old helper blocked all changes for approved/cancelled orders.  In actual
    ATP paperwork clerical corrections happen; the signed paper copy is the
    authoritative physical document.  We therefore only validate existence.
    """
    if getattr(r3, "_taxo_v1074_editable_appendices", False):
        return

    def require_existing(con, order_id):
        row = ops.get_order(con, order_id)
        if row is None:
            raise ValueError("Наказ не знайдено.")
        return row

    r3._require_draft = require_existing
    r3._taxo_v1074_editable_appendices = True


def _employee_maps(con):
    rows = ops.list_employee_choices(con, active_only=False)
    by_label = {row["label"]: row["id"] for row in rows}
    by_id = {row["id"]: row["label"] for row in rows}
    return rows, by_label, by_id


def _edit_order_dialog(app, core, win, order_id):
    con = core.db()
    try:
        row = ops.get_order(con, order_id)
        if row is None:
            raise ValueError("Наказ не знайдено.")
        employees, emp_by_label, emp_by_id = _employee_maps(con)
    finally:
        con.close()

    dialog = core.tk.Toplevel(win)
    try:
        core.configure_toplevel(dialog, title="Редагувати наказ", minsize=(780, 560))
        core.fit_window_to_screen(dialog, 820, 650, 760, 520)
    except Exception:
        dialog.geometry("820x650")
    dialog.title("Редагувати наказ №%s" % str(row["order_no"] or ""))
    frm = core.ttk.Frame(dialog, padding=14)
    frm.pack(fill="both", expand=True)
    frm.columnconfigure(1, weight=1)
    frm.rowconfigure(7, weight=1)

    type_labels = list(ops.ORDER_TYPE_LABELS.values())
    type_by_label = {label: key for key, label in ops.ORDER_TYPE_LABELS.items()}
    current_type_label = ops.ORDER_TYPE_LABELS.get(str(row["order_type"]), str(row["order_type"]))

    type_var = core.tk.StringVar(value=current_type_label)
    no_var = core.tk.StringVar(value=str(row["order_no"] or ""))
    date_var = core.tk.StringVar(value=ops.display_day(row["order_date"]))
    place_var = core.tk.StringVar(value=str(row["place"] or ""))
    subject_var = core.tk.StringVar(value=str(row["subject"] or ""))
    control_var = core.tk.StringVar(value=emp_by_id.get(row["control_employee_id"], ""))

    labels = (
        ("Тип наказу", type_var),
        ("Номер", no_var),
        ("Дата", date_var),
        ("Місце", place_var),
        ("Тема", subject_var),
        ("Контроль", control_var),
    )
    for idx, (label, var) in enumerate(labels):
        core.ttk.Label(frm, text=label).grid(row=idx, column=0, sticky="nw", padx=(0, 8), pady=5)
        if label == "Тип наказу":
            widget = core.ttk.Combobox(frm, textvariable=var, values=type_labels, state="readonly")
        elif label == "Контроль":
            widget = core.ttk.Combobox(frm, textvariable=var,
                                       values=[x["label"] for x in employees], state="readonly")
        else:
            widget = core.ttk.Entry(frm, textvariable=var)
        widget.grid(row=idx, column=1, sticky="ew", pady=5)

    core.ttk.Label(frm, text="Підстава / вступ").grid(row=6, column=0, sticky="nw", pady=5)
    preamble = core.tk.Text(frm, height=4, wrap="word")
    preamble.grid(row=6, column=1, sticky="nsew", pady=5)
    preamble.insert("1.0", str(row["preamble"] or ""))

    core.ttk.Label(frm, text="Текст пунктів").grid(row=7, column=0, sticky="nw", pady=5)
    body = core.tk.Text(frm, height=8, wrap="word")
    body.grid(row=7, column=1, sticky="nsew", pady=5)
    body.insert("1.0", str(row["body_text"] or ""))

    if str(row["status"]) != ops.ORDER_DRAFT:
        core.ttk.Label(
            frm,
            text=(
                "Наказ уже має внутрішній стан «%s». Редагування дозволене, але якщо паперовий примірник "
                "вже підписано, після виправлення його потрібно звірити та за потреби передрукувати/підписати повторно."
            ) % ops.ORDER_STATUS_LABELS.get(row["status"], row["status"]),
            style="Muted.TLabel", wraplength=680, justify="left",
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(6, 4))

    def save():
        number = str(no_var.get() or "").strip()
        if not number:
            core.messagebox.showerror("Наказ", "Вкажіть номер наказу.", parent=dialog)
            return
        try:
            day = ops._day(date_var.get())
        except Exception as exc:
            core.messagebox.showerror("Наказ", str(exc), parent=dialog)
            return
        order_type = type_by_label.get(type_var.get(), ops.TYPE_GENERIC)
        now = datetime.now().isoformat(timespec="seconds")
        con2 = core.db()
        try:
            con2.execute(
                """UPDATE operations_orders
                      SET order_type=?,order_no=?,order_date=?,place=?,subject=?,preamble=?,body_text=?,
                          control_employee_id=?,updated_at=?
                    WHERE id=?""",
                (
                    order_type, number, day, str(place_var.get() or "").strip(),
                    str(subject_var.get() or "").strip(),
                    preamble.get("1.0", "end-1c").strip(), body.get("1.0", "end-1c").strip(),
                    emp_by_label.get(control_var.get()), now, int(order_id),
                ),
            )
            con2.commit()
        except Exception as exc:
            con2.rollback()
            core.messagebox.showerror("Наказ", str(exc), parent=dialog)
            return
        finally:
            con2.close()
        dialog.destroy()
        try:
            win.destroy()
        except Exception:
            pass
        app._operations_center_window = None
        app.open_operations_center()

    buttons = core.ttk.Frame(frm)
    buttons.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    core.ttk.Button(buttons, text="Скасувати", command=dialog.destroy).pack(side="right")
    core.ttk.Button(buttons, text="Зберегти зміни", style="Accent.TButton", command=save).pack(side="right", padx=(0, 6))
    dialog.transient(win)


def _install_operations_usability(app, core, win):
    if getattr(win, "_taxo_v1074_usability", False):
        return
    book = _find_notebook(win)
    if book is None:
        return
    orders_tab = _tab_frame(book, "Накази")
    assignments_tab = _tab_frame(book, "Закріплення водіїв")
    appendices_tab = _tab_frame(book, "Додатки до наказів")
    if orders_tab is None:
        return

    create_btn = _find_button(orders_tab, "Новий наказ") or _find_button(orders_tab, "Створити наказ")
    if create_btn is not None:
        try:
            create_btn.configure(text="Створити наказ")
        except Exception:
            pass
        toolbar = create_btn.master
        help_label = core.ttk.Label(
            toolbar,
            text="1. Створіть наказ  →  2. заповніть реквізити  →  3. для закріплення додайте ТЗ і водія",
            style="Muted.TLabel",
        )
        help_label.pack(side="left", padx=(12, 0))

        order_tree = _find_tree(orders_tab)

        def edit_selected():
            if order_tree is None:
                return
            sel = order_tree.selection()
            if not sel:
                core.messagebox.showinfo("Накази", "Виберіть наказ для редагування.", parent=win)
                return
            _edit_order_dialog(app, core, win, int(sel[0]))

        core.ttk.Button(toolbar, text="Редагувати наказ", command=edit_selected).pack(side="left", padx=(6, 0))

        if order_tree is not None and not order_tree.get_children():
            core.ttk.Label(
                orders_tab,
                text=(
                    "Реєстр наказів поки порожній. Почніть зі «Створити наказ». "
                    "Для наказу про закріплення після збереження Taxo автоматично переведе вас до таблиці ТЗ/водіїв."
                ),
                style="Muted.TLabel", wraplength=1100, justify="left",
            ).pack(fill="x", padx=12, pady=(0, 8), before=order_tree.master)

    if assignments_tab is not None and create_btn is not None:
        top_children = assignments_tab.winfo_children()
        direct_bar = core.ttk.Frame(assignments_tab, padding=(10, 6, 10, 4))
        if top_children:
            direct_bar.pack(fill="x", before=top_children[0])
        else:
            direct_bar.pack(fill="x")

        def create_assignment_order():
            try:
                book.select(orders_tab)
            except Exception:
                pass
            create_btn.invoke()

        core.ttk.Button(
            direct_bar, text="Створити наказ про закріплення",
            style="Accent.TButton", command=create_assignment_order,
        ).pack(side="left")
        core.ttk.Label(
            direct_bar,
            text="Не потрібно спочатку створювати порожній рядок у цій таблиці — закріплення належить наказу.",
            style="Muted.TLabel",
        ).pack(side="left", padx=(10, 0))

    if appendices_tab is not None:
        for item in _walk(appendices_tab):
            try:
                if item.winfo_class() == "TLabel" and "Після затвердження наказу вони не редагуються" in str(item.cget("text")):
                    item.configure(text="Додатки можна виправляти і після внутрішнього затвердження. Для вже підписаного паперового примірника перевірте потребу повторного друку/підпису.")
            except Exception:
                pass

    win._taxo_v1074_usability = True


def install(core, base_app):
    if getattr(core, "_TAXO_1074_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION
    _allow_order_corrections()

    class Taxo1074App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def open_operations_center(self):
            result = super().open_operations_center()
            win = getattr(self, "_operations_center_window", None)
            if win is not None:
                try:
                    _install_operations_usability(self, core, win)
                except Exception as exc:
                    core.messagebox.showerror("Експлуатація", str(exc), parent=win)
            return result

    Taxo1074App.__name__ = "App"
    Taxo1074App.__qualname__ = "App"
    core.App = Taxo1074App
    core._TAXO_1074_INSTALLED = True
    return Taxo1074App
