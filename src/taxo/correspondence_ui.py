# -*- coding: utf-8 -*-
"""User-facing incoming/outgoing correspondence journals and cards.

The UI sits on top of the already verified 10.24-r1 registry and 10.24-r2
attachment APIs. It does not invent delivery facts: registration, attachment
presence and actual sent/received dates remain separate concepts.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from correspondence_attachments import (
    add_correspondence_file,
    link_correspondence_document,
    list_correspondence_attachments,
    list_removed_correspondence_attachments,
    load_correspondence_file,
    remove_correspondence_attachment,
)
from correspondence_cases import (
    add_linked_correspondence_to_case,
    case_for_correspondence,
    create_case,
    linked_correspondence_candidates,
    list_case_correspondence,
    list_cases,
    move_correspondence_to_case,
    rename_case,
    set_case_archived,
)
from correspondence_registry import (
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,
    get_correspondence,
)
from correspondence_service import (
    available_status_transitions,
    change_correspondence_status,
    correspondence_state_history,
    incoming_journal,
    is_overdue,
    mark_received,
    mark_sent,
    outgoing_journal,
    register_incoming,
    register_outgoing,
    register_response,
)
from document_vault_store import list_document_vault
from document_vault_ui import prepare_document_vault_view_copy
from paper_document_store import catalog_dir, list_documents, open_file
from table_sorting import configure_sortable_tree, restore_tree_selection


DATE_FORMAT = "%d.%m.%Y"

STATUS_LABELS = {
    "new": "Новий",
    "received": "Отримано",
    "in_progress": "В роботі",
    "awaiting_response": "Очікує відповіді",
    "response_prepared": "Відповідь підготовлена",
    "response_sent": "Відповідь надіслана",
    "registered": "Зареєстровано",
    "sent": "Надіслано",
    "closed": "Закрито",
    "cancelled": "Скасовано",
}
DELIVERY_LABELS = {
    "": "—",
    "mail": "Пошта",
    "email": "E-mail",
    "personal": "Особисто",
    "courier": "Кур'єр",
    "other": "Інше",
}
DELIVERY_CODES = {label: code for code, label in DELIVERY_LABELS.items()}

_COLUMNS = (
    ("number", "№", "text", None, 145),
    ("date", "Дата", "date", None, 92),
    ("correspondent", "Кореспондент", "text", None, 190),
    ("subject", "Тема", "text", None, 280),
    ("due", "Строк", "date", None, 92),
    ("status", "Стан", "status", tuple(STATUS_LABELS.values()), 145),
    ("control", "Контроль", "text", None, 105),
    ("attachments", "Файли", "number", None, 70),
)


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _display_date(value):
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return date.fromisoformat(text).strftime(DATE_FORMAT)
    except ValueError:
        return text


def _parse_user_date(value, label, *, allow_empty=True):
    text = str(value or "").strip()
    if not text:
        if allow_empty:
            return ""
        raise ValueError("%s не може бути порожньою" % label)
    for fmt in (DATE_FORMAT, "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError("%s має бути у форматі ДД.ММ.РРРР" % label)


def _human_size(size):
    value = int(size or 0)
    if value <= 0:
        return "—"
    units = ("Б", "КБ", "МБ", "ГБ")
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            if unit == "Б":
                return "%d %s" % (int(amount), unit)
            return "%.1f %s" % (amount, unit)
        amount /= 1024.0
    return "%d Б" % value


def _status_label(value):
    return STATUS_LABELS.get(str(value or ""), str(value or "") or "—")


def _delivery_label(value):
    return DELIVERY_LABELS.get(str(value or ""), str(value or "") or "—")


def _fit_window(core, win, width, height, min_width, min_height, title):
    try:
        core.fit_window_to_screen(win, width, height, min_width, min_height)
    except Exception:
        win.geometry("%dx%d" % (width, height))
    try:
        core.configure_toplevel(win, title=title, minsize=(min_width, min_height))
    except Exception:
        win.title(title)
        try:
            win.minsize(min_width, min_height)
        except Exception:
            pass


def _calendar_button(core, parent, variable):
    factory = getattr(core, "calendar_button", None)
    if not callable(factory):
        return None
    try:
        return factory(parent, variable)
    except Exception:
        return None


def _open_vault_document(workspace_root, vault_id):
    path = prepare_document_vault_view_copy(Path(workspace_root), vault_id)
    return open_file(path)


def _open_document_ref(core, parent, workspace_root, document_ref):
    ref = str(document_ref or "").strip()
    if not ref:
        core.messagebox.showinfo(
            "Кореспонденція",
            "До цього листа не прив'язано готовий документ.",
            parent=parent,
        )
        return False

    try:
        if ref.startswith("vault:"):
            _open_vault_document(workspace_root, ref.split(":", 1)[1])
            return True
        if ref.startswith("paper:"):
            document_id = ref.split(":", 1)[1]
            rows = [
                row for row in list_documents(workspace_root)
                if str(row.get("id") or "") == document_id
            ]
            if len(rows) != 1:
                raise ValueError("Пов'язаний Word-документ не знайдено")
            path = catalog_dir(workspace_root) / rows[0]["file"]
            if not path.is_file():
                raise ValueError("Файл пов'язаного документа відсутній")
            open_file(path)
            return True
        if ref.startswith("order:"):
            core.messagebox.showinfo(
                "Кореспонденція",
                "Це посилання на наказ. Відкрийте наказ через «Експлуатація → Накази».",
                parent=parent,
            )
            return False
        raise ValueError("Непідтримане посилання на документ")
    except Exception as exc:
        core.messagebox.showerror(
            "Кореспонденція",
            "Не вдалося відкрити документ:\n%s" % exc,
            parent=parent,
        )
        return False


def _choose_vault_document(parent, core, workspace_root):
    try:
        records = tuple(list_document_vault(Path(workspace_root)))
    except Exception as exc:
        core.messagebox.showerror(
            "Документи",
            "Не вдалося прочитати DocumentVault:\n%s" % exc,
            parent=parent,
        )
        return None
    if not records:
        core.messagebox.showinfo(
            "Документи",
            "У DocumentVault ще немає готових документів.",
            parent=parent,
        )
        return None

    dialog = core.tk.Toplevel(parent)
    _fit_window(core, dialog, 760, 460, 620, 360, "Вибрати готовий документ")
    try:
        dialog.transient(parent)
    except Exception:
        pass

    body = core.ttk.Frame(dialog, padding=10)
    body.pack(fill="both", expand=True)
    core.ttk.Label(
        body,
        text="Виберіть документ. Taxo збереже лише контрольоване посилання — байти не копіюються.",
        style="Muted.TLabel",
        wraplength=700,
        justify="left",
    ).pack(fill="x", pady=(0, 8))

    table_frame = core.ttk.Frame(body)
    table_frame.pack(fill="both", expand=True)
    columns = ("date", "kind", "title", "status")
    tree = core.ttk.Treeview(
        table_frame, columns=columns, show="headings", selectmode="browse"
    )
    tree.heading("date", text="Дата")
    tree.heading("kind", text="Вид")
    tree.heading("title", text="Назва")
    tree.heading("status", text="Стан")
    tree.column("date", width=95, stretch=False)
    tree.column("kind", width=150)
    tree.column("title", width=340)
    tree.column("status", width=110)
    ybar = core.ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=ybar.set)
    tree.pack(side="left", fill="both", expand=True)
    ybar.pack(side="right", fill="y")

    by_id = {}
    for record in records:
        by_id[record.vault_id] = record
        tree.insert(
            "",
            "end",
            iid=record.vault_id,
            values=(
                _display_date(record.document_date),
                record.kind,
                record.title,
                record.status,
            ),
        )

    result = {"value": None}

    def choose():
        selected = tree.selection()
        if not selected:
            core.messagebox.showinfo(
                "Документи", "Виберіть документ зі списку.", parent=dialog
            )
            return
        record = by_id[selected[0]]
        result["value"] = (
            "vault:" + record.vault_id,
            record.title or record.kind or record.vault_id,
        )
        dialog.destroy()

    buttons = core.ttk.Frame(body)
    buttons.pack(fill="x", pady=(8, 0))
    core.ttk.Button(buttons, text="Скасувати", command=dialog.destroy).pack(
        side="right", padx=(8, 0)
    )
    core.ttk.Button(
        buttons, text="Вибрати", style="Accent.TButton", command=choose
    ).pack(side="right")
    tree.bind("<Double-1>", lambda _event: choose())

    try:
        dialog.grab_set()
    except Exception:
        pass
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.wait_window()
    return result["value"]


def open_attachments_dialog(
    parent, core, workspace_root, correspondence_record, on_changed=None
):
    """Manage active/history attachments without changing correspondence state."""
    dialog = core.tk.Toplevel(parent)
    title = "Вкладення — %s" % correspondence_record.registration_number
    _fit_window(core, dialog, 920, 560, 700, 440, title)
    try:
        dialog.transient(parent)
    except Exception:
        pass

    body = core.ttk.Frame(dialog, padding=10)
    body.pack(fill="both", expand=True)
    hint = core.ttk.Label(
        body,
        text=(
            "Вкладення — це файл або посилання на готовий документ. "
            "Сам факт вкладення НЕ означає, що лист надіслано, отримано чи підписано."
        ),
        style="Muted.TLabel",
        justify="left",
        wraplength=850,
    )
    hint.pack(fill="x", pady=(0, 8))
    hint.bind(
        "<Configure>",
        lambda event: hint.configure(wraplength=max(360, event.width - 12)),
        add="+",
    )

    book = core.ttk.Notebook(body)
    book.pack(fill="both", expand=True)
    active_page = core.ttk.Frame(book, padding=6)
    history_page = core.ttk.Frame(book, padding=6)
    book.add(active_page, text="Активні")
    book.add(history_page, text="Історія")

    def make_tree(page, historical=False):
        frame = core.ttk.Frame(page)
        frame.pack(fill="both", expand=True)
        columns = ("kind", "name", "size", "id")
        tree = core.ttk.Treeview(
            frame, columns=columns, show="headings", selectmode="browse"
        )
        tree.heading("kind", text="Тип")
        tree.heading("name", text="Файл / документ")
        tree.heading("size", text="Розмір")
        tree.heading("id", text="ID")
        tree.column("kind", width=120, stretch=False)
        tree.column("name", width=390)
        tree.column("size", width=100, stretch=False)
        tree.column("id", width=240)
        ybar = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        xbar = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    active_tree = make_tree(active_page)
    history_tree = make_tree(history_page, historical=True)
    status_var = core.tk.StringVar(master=dialog, value="")
    core.ttk.Label(
        body, textvariable=status_var, style="Muted.TLabel"
    ).pack(fill="x", pady=(6, 0))

    state = {"active": {}, "history": {}}

    def refresh():
        selected = tuple(active_tree.selection())
        try:
            active = tuple(list_correspondence_attachments(
                workspace_root, correspondence_record.correspondence_id
            ))
            removed = tuple(list_removed_correspondence_attachments(
                workspace_root, correspondence_record.correspondence_id
            ))
        except Exception as exc:
            status_var.set("Помилка перевірки вкладень: %s" % exc)
            return False

        active_tree.delete(*active_tree.get_children(""))
        history_tree.delete(*history_tree.get_children(""))
        state["active"] = {item.attachment_id: item for item in active}
        state["history"] = {
            item.record.attachment_id: item for item in removed
        }

        for item in active:
            kind = "Документ" if item.source_kind == "document_ref" else "Файл"
            name = item.original_name or item.document_ref
            active_tree.insert(
                "",
                "end",
                iid=item.attachment_id,
                values=(kind, name, _human_size(item.size_bytes), item.attachment_id),
            )
        for item in removed:
            record = item.record
            kind = "Документ" if record.source_kind == "document_ref" else "Файл"
            name = record.original_name or record.document_ref
            history_tree.insert(
                "",
                "end",
                iid=record.attachment_id,
                values=(kind + " · прибрано", name, _human_size(record.size_bytes), record.attachment_id),
            )

        retained = [iid for iid in selected if iid in state["active"]]
        if retained:
            active_tree.selection_set(retained)
        elif active:
            active_tree.selection_set(active[0].attachment_id)
            active_tree.focus(active[0].attachment_id)
        status_var.set(
            "Активних вкладень: %d · в історії: %d" % (len(active), len(removed))
        )
        return True

    def selected_active():
        selected = active_tree.selection()
        if not selected:
            core.messagebox.showinfo(
                "Вкладення", "Виберіть вкладення.", parent=dialog
            )
            return None
        return state["active"].get(selected[0])

    def add_file():
        path = core.filedialog.askopenfilename(
            parent=dialog,
            title="Додати файл до листа",
            filetypes=(
                ("Документи", "*.pdf *.jpg *.jpeg *.png *.tif *.tiff *.docx"),
                ("PDF", "*.pdf"),
                ("Зображення", "*.jpg *.jpeg *.png *.tif *.tiff"),
                ("Word DOCX", "*.docx"),
                ("Усі файли", "*.*"),
            ),
        )
        if not path:
            return
        try:
            add_correspondence_file(
                workspace_root,
                correspondence_record.correspondence_id,
                Path(path),
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Вкладення", str(exc), parent=dialog
            )
            return
        refresh()
        if callable(on_changed):
            on_changed()

    def link_document():
        choice = _choose_vault_document(dialog, core, workspace_root)
        if choice is None:
            return
        ref, label = choice
        try:
            link_correspondence_document(
                workspace_root,
                correspondence_record.correspondence_id,
                ref,
                label,
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Вкладення", str(exc), parent=dialog
            )
            return
        refresh()
        if callable(on_changed):
            on_changed()

    def open_selected():
        record = selected_active()
        if record is None:
            return
        try:
            if record.source_kind == "stored":
                obj = load_correspondence_file(
                    workspace_root, record.attachment_id
                )
                open_file(obj.path)
            else:
                _open_document_ref(
                    core, dialog, workspace_root, record.document_ref
                )
        except Exception as exc:
            core.messagebox.showerror(
                "Вкладення",
                "Не вдалося відкрити вкладення:\n%s" % exc,
                parent=dialog,
            )

    def remove_selected():
        record = selected_active()
        if record is None:
            return
        if not core.messagebox.askyesno(
            "Прибрати вкладення?",
            (
                "Прибрати вкладення зі списку активних?\n\n"
                "Taxo НЕ видалить незмінний файл. Він залишиться у сховищі "
                "та буде видимий в історії."
            ),
            parent=dialog,
        ):
            return
        try:
            remove_correspondence_attachment(
                workspace_root, record.attachment_id
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Вкладення", str(exc), parent=dialog
            )
            return
        refresh()
        if callable(on_changed):
            on_changed()

    actions = core.ttk.Frame(active_page)
    actions.pack(fill="x", pady=(8, 0))
    core.ttk.Button(actions, text="Додати файл…", command=add_file).pack(
        side="left"
    )
    core.ttk.Button(
        actions, text="Додати готовий документ…", command=link_document
    ).pack(side="left", padx=(6, 0))
    core.ttk.Button(actions, text="Відкрити", command=open_selected).pack(
        side="left", padx=(6, 0)
    )
    core.ttk.Button(actions, text="Прибрати", command=remove_selected).pack(
        side="left", padx=(6, 0)
    )
    core.ttk.Button(
        body, text="Закрити", command=dialog.destroy
    ).pack(anchor="e", pady=(8, 0))

    active_tree.bind("<Double-1>", lambda _event: open_selected())
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog._taxo_correspondence_attachment_tree = active_tree
    dialog._taxo_correspondence_attachment_refresh = refresh
    refresh()
    return dialog


def open_correspondence_form(
    parent,
    core,
    workspace_root,
    direction,
    on_saved,
    response_to=None,
):
    """Create one incoming/outgoing record with unsaved-change protection."""
    is_incoming = direction == DIRECTION_INCOMING
    is_response = response_to is not None
    title = (
        "Відповідь на вхідний лист"
        if is_response
        else "Новий вхідний лист" if is_incoming else "Новий вихідний лист"
    )
    dialog = core.tk.Toplevel(parent)
    _fit_window(core, dialog, 780, 690, 640, 540, title)
    try:
        dialog.transient(parent)
    except Exception:
        pass

    body = core.ttk.Frame(dialog, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)

    registration_var = core.tk.StringVar(
        master=dialog, value=date.today().strftime(DATE_FORMAT)
    )
    document_date_var = core.tk.StringVar(master=dialog, value="")
    action_date_var = core.tk.StringVar(master=dialog, value="")
    external_var = core.tk.StringVar(master=dialog, value="")
    correspondent_var = core.tk.StringVar(
        master=dialog,
        value=response_to.correspondent if is_response else "",
    )
    subject_var = core.tk.StringVar(
        master=dialog,
        value=response_to.subject if is_response else "",
    )
    delivery_var = core.tk.StringVar(master=dialog, value="—")
    responsible_var = core.tk.StringVar(master=dialog, value="")
    due_var = core.tk.StringVar(master=dialog, value="")

    def add_date(row, label, variable):
        core.ttk.Label(body, text=label).grid(
            row=row, column=0, sticky="w", padx=(0, 8), pady=4
        )
        entry = core.ttk.Entry(body, textvariable=variable, width=18)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        button = _calendar_button(core, body, variable)
        if button is not None:
            button.grid(row=row, column=2, sticky="w", padx=(6, 0), pady=4)
        return entry

    add_date(0, "Дата реєстрації", registration_var)
    add_date(1, "Дата документа", document_date_var)
    add_date(
        2,
        "Дата отримання" if is_incoming else "Дата відправлення",
        action_date_var,
    )

    core.ttk.Label(body, text="Зовнішній №").grid(
        row=3, column=0, sticky="w", padx=(0, 8), pady=4
    )
    external_entry = core.ttk.Entry(body, textvariable=external_var)
    external_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)
    if is_response:
        external_entry.configure(state="disabled")

    core.ttk.Label(body, text="Кореспондент").grid(
        row=4, column=0, sticky="w", padx=(0, 8), pady=4
    )
    correspondent_entry = core.ttk.Entry(body, textvariable=correspondent_var)
    correspondent_entry.grid(row=4, column=1, columnspan=2, sticky="ew", pady=4)
    if is_response:
        correspondent_entry.configure(state="disabled")

    core.ttk.Label(body, text="Тема").grid(
        row=5, column=0, sticky="w", padx=(0, 8), pady=4
    )
    core.ttk.Entry(body, textvariable=subject_var).grid(
        row=5, column=1, columnspan=2, sticky="ew", pady=4
    )

    core.ttk.Label(body, text="Короткий зміст").grid(
        row=6, column=0, sticky="nw", padx=(0, 8), pady=4
    )
    summary = core.tk.Text(body, height=5, wrap="word")
    summary.grid(row=6, column=1, columnspan=2, sticky="nsew", pady=4)
    body.rowconfigure(6, weight=1)

    core.ttk.Label(body, text="Спосіб").grid(
        row=7, column=0, sticky="w", padx=(0, 8), pady=4
    )
    core.ttk.Combobox(
        body,
        textvariable=delivery_var,
        values=tuple(DELIVERY_CODES),
        state="readonly",
    ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=4)

    core.ttk.Label(body, text="Відповідальний").grid(
        row=8, column=0, sticky="w", padx=(0, 8), pady=4
    )
    core.ttk.Entry(body, textvariable=responsible_var).grid(
        row=8, column=1, columnspan=2, sticky="ew", pady=4
    )
    add_date(9, "Строк виконання", due_var)

    hint_text = (
        "Вхідний лист реєструється незалежно від наявності скана/файла."
        if is_incoming
        else (
            "Порожня «Дата відправлення» означає лише «Зареєстровано». "
            "Taxo не вважає лист надісланим автоматично."
        )
    )
    if is_response:
        hint_text = (
            "Відповідь буде пов'язана з %s. Порожня дата відправлення "
            "залишить її лише зареєстрованою."
        ) % response_to.registration_number
    core.ttk.Label(
        body,
        text=hint_text,
        style="Muted.TLabel",
        justify="left",
        wraplength=680,
    ).grid(row=10, column=0, columnspan=3, sticky="ew", pady=(6, 4))

    variables = (
        registration_var,
        document_date_var,
        action_date_var,
        external_var,
        correspondent_var,
        subject_var,
        delivery_var,
        responsible_var,
        due_var,
    )

    def snapshot():
        return (
            tuple(var.get() for var in variables),
            summary.get("1.0", "end-1c"),
        )

    initial = snapshot()
    saved = {"value": False}

    def request_close():
        if not saved["value"] and snapshot() != initial:
            if not core.messagebox.askyesno(
                "Незбережені зміни",
                "Закрити форму без збереження введених даних?",
                parent=dialog,
            ):
                return
        dialog.destroy()

    def save():
        try:
            registration_date = _parse_user_date(
                registration_var.get(), "Дата реєстрації", allow_empty=False
            )
            document_date = _parse_user_date(
                document_date_var.get(), "Дата документа"
            )
            action_date = _parse_user_date(
                action_date_var.get(),
                "Дата отримання" if is_incoming else "Дата відправлення",
            )
            due_date = _parse_user_date(due_var.get(), "Строк виконання")
            delivery = DELIVERY_CODES.get(delivery_var.get())
            if delivery is None:
                raise ValueError("Некоректний спосіб отримання/відправлення")

            common = {
                "registration_date": registration_date,
                "subject": subject_var.get(),
                "document_date": document_date,
                "summary": summary.get("1.0", "end-1c"),
                "delivery_method": delivery,
                "responsible_id": responsible_var.get(),
                "due_date": due_date,
            }

            if is_response:
                record = register_response(
                    workspace_root,
                    response_to.correspondence_id,
                    sent_date=action_date,
                    **common
                )
            elif is_incoming:
                record = register_incoming(
                    workspace_root,
                    correspondent=correspondent_var.get(),
                    received_date=action_date,
                    external_number=external_var.get(),
                    **common
                )
            else:
                record = register_outgoing(
                    workspace_root,
                    correspondent=correspondent_var.get(),
                    sent_date=action_date,
                    external_number=external_var.get(),
                    **common
                )
        except Exception as exc:
            core.messagebox.showerror(
                "Кореспонденція", str(exc), parent=dialog
            )
            return

        saved["value"] = True
        dialog.destroy()
        on_saved(record)

    buttons = core.ttk.Frame(body)
    buttons.grid(row=11, column=0, columnspan=3, sticky="e", pady=(8, 0))
    core.ttk.Button(
        buttons, text="Скасувати", command=request_close
    ).pack(side="right", padx=(8, 0))
    core.ttk.Button(
        buttons, text="Зберегти", style="Accent.TButton", command=save
    ).pack(side="right")

    dialog.protocol("WM_DELETE_WINDOW", request_close)
    dialog._taxo_correspondence_save = save
    dialog._taxo_correspondence_cancel = request_close
    dialog._taxo_correspondence_summary = summary
    dialog._taxo_correspondence_vars = {
        "registration_date": registration_var,
        "document_date": document_date_var,
        "action_date": action_date_var,
        "external_number": external_var,
        "correspondent": correspondent_var,
        "subject": subject_var,
        "delivery": delivery_var,
        "responsible": responsible_var,
        "due_date": due_var,
    }
    try:
        if is_response:
            subject_var.set(subject_var.get())
        else:
            correspondent_entry.focus_set()
    except Exception:
        pass
    return dialog


def open_correspondence_center(app, core, workspace_root):
    """Open one resizable correspondence center for the selected workspace."""
    existing = getattr(app, "_correspondence_window", None)
    if _alive(existing):
        existing.lift()
        existing.focus_force()
        return existing

    workspace_root = Path(workspace_root)
    win = core.tk.Toplevel(app)
    app._correspondence_window = win
    company = ""
    try:
        company = str(app._company_name_value() or "").strip()
    except Exception:
        pass
    title = "Кореспонденція" if not company else "Taxo / %s — Кореспонденція" % company
    _fit_window(core, win, 1180, 760, 760, 520, title)

    def close():
        try:
            cancel_pending_refresh()
        except Exception:
            pass
        try:
            app._correspondence_window = None
        except Exception:
            pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close)

    root = core.ttk.Frame(win, padding=10)
    root.pack(fill="both", expand=True)

    header = core.ttk.Frame(root)
    header.pack(fill="x")
    core.ttk.Label(
        header, text="Ділова кореспонденція", style="HeroTitle.TLabel"
    ).pack(side="left")
    core.ttk.Button(header, text="Закрити", command=close).pack(
        side="right", padx=(8, 0)
    )

    search_var = core.tk.StringVar(master=win, value="")
    date_var = core.tk.StringVar(master=win, value="")
    status_var = core.tk.StringVar(master=win, value="")

    toolbar = core.ttk.Frame(root)
    toolbar.pack(fill="x", pady=(8, 6))
    core.ttk.Label(toolbar, text="Пошук").pack(side="left")
    search_entry = core.ttk.Entry(toolbar, textvariable=search_var, width=28)
    search_entry.pack(side="left", padx=(4, 10))

    core.ttk.Label(toolbar, text="Дата").pack(side="left")
    date_entry = core.ttk.Entry(toolbar, textvariable=date_var, width=12)
    date_entry.pack(side="left", padx=(4, 4))
    calendar = _calendar_button(core, toolbar, date_var)
    if calendar is not None:
        calendar.pack(side="left", padx=(0, 5))
    core.ttk.Button(
        toolbar,
        text="Сьогодні",
        command=lambda: date_var.set(date.today().strftime(DATE_FORMAT)),
    ).pack(side="left", padx=2)
    core.ttk.Button(
        toolbar, text="Усі дати", command=lambda: date_var.set("")
    ).pack(side="left", padx=2)

    book = core.ttk.Notebook(root)
    book.pack(fill="both", expand=True)
    incoming_page = core.ttk.Frame(book, padding=4)
    outgoing_page = core.ttk.Frame(book, padding=4)
    cases_page = core.ttk.Frame(book, padding=4)
    book.add(incoming_page, text="Вхідні")
    book.add(outgoing_page, text="Вихідні")
    book.add(cases_page, text="Справи")

    state = {
        "records": {
            DIRECTION_INCOMING: {},
            DIRECTION_OUTGOING: {},
        },
        "trees": {},
        "details": {},
        "buttons": {},
        "pages": {
            DIRECTION_INCOMING: incoming_page,
            DIRECTION_OUTGOING: outgoing_page,
        },
        "sort": {
            DIRECTION_INCOMING: ("date", True),
            DIRECTION_OUTGOING: ("date", True),
        },
        "attachment_counts": {},
        "attachment_error": "",
        "cases": {},
        "case_members": {},
        "case_by_record": {},
        "case_error": "",
        "case_tree": None,
        "case_member_tree": None,
        "case_detail": None,
        "case_buttons": {},
        "pending_case": None,
        "pending_select": {},
        "after": None,
    }

    def cancel_pending_refresh(event=None):
        if event is not None and getattr(event, "widget", None) is not win:
            return
        token = state.get("after")
        if token is not None:
            try:
                win.after_cancel(token)
            except Exception:
                pass
            state["after"] = None

    win.bind("<Destroy>", cancel_pending_refresh, add="+")

    def selected_record(direction, quiet=False):
        tree = state["trees"][direction]
        selected = tree.selection()
        if not selected:
            if not quiet:
                core.messagebox.showinfo(
                    "Кореспонденція", "Виберіть лист у журналі.", parent=win
                )
            return None
        return state["records"][direction].get(selected[0])

    def all_record_labels():
        result = {}
        for mapping in state["records"].values():
            for identity, record in mapping.items():
                result[identity] = record.registration_number
        return result

    def card_text(record):
        labels = all_record_labels()
        lines = [
            "%s · %s" % (
                record.registration_number,
                "Вхідний" if record.direction == DIRECTION_INCOMING else "Вихідний",
            ),
            "Дата реєстрації: %s" % (_display_date(record.registration_date) or "—"),
            "Дата документа: %s" % (_display_date(record.document_date) or "—"),
            (
                "Дата отримання: %s" % (_display_date(record.received_date) or "—")
                if record.direction == DIRECTION_INCOMING
                else "Дата відправлення: %s" % (_display_date(record.sent_date) or "—")
            ),
            "Зовнішній №: %s" % (record.external_number or "—"),
            "Кореспондент: %s" % record.correspondent,
            "Тема: %s" % record.subject,
            "Короткий зміст: %s" % (record.summary or "—"),
            "Спосіб: %s" % _delivery_label(record.delivery_method),
            "Відповідальний: %s" % (record.responsible_id or "—"),
            "Строк: %s" % (_display_date(record.due_date) or "—"),
            "Стан: %s" % _status_label(record.status),
            "Контроль: %s" % (
                "Прострочено"
                if is_overdue(record)
                else "В межах строку" if record.due_date else "Без строку"
            ),
            "Готовий документ: %s" % (record.document_ref or "—"),
            "Справа: %s" % (
                state["case_by_record"].get(
                    record.correspondence_id, "Без справи"
                )
                if not state["case_error"]
                else "помилка перевірки"
            ),
        ]
        if record.response_to_ids:
            lines.append(
                "Відповідь на: %s" % ", ".join(
                    labels.get(value, value) for value in record.response_to_ids
                )
            )
        if record.related_ids:
            lines.append(
                "Пов'язані: %s" % ", ".join(
                    labels.get(value, value) for value in record.related_ids
                )
            )
        count = state["attachment_counts"].get(record.correspondence_id)
        if state["attachment_error"]:
            lines.append("Вкладення: помилка перевірки")
        else:
            lines.append("Активних вкладень: %d" % int(count or 0))
        return "\n".join(lines)

    def update_card(direction):
        record = selected_record(direction, quiet=True)
        variable = state["details"][direction]
        buttons = state["buttons"][direction]
        if record is None:
            variable.set("Виберіть лист у журналі.")
            for button in buttons.values():
                button.configure(state="disabled")
            return
        variable.set(card_text(record))
        buttons["attachments"].configure(state="normal")
        buttons["open"].configure(
            state="normal" if record.document_ref else "disabled"
        )
        buttons["history"].configure(state="normal")
        buttons["case"].configure(
            state="normal" if not state["case_error"] else "disabled"
        )
        transitions = set(available_status_transitions(record))
        if "received" in buttons:
            buttons["received"].configure(
                state="normal" if "received" in transitions else "disabled"
            )
        if "sent" in buttons:
            buttons["sent"].configure(
                state="normal" if "sent" in transitions else "disabled"
            )
        workflow_transitions = tuple(
            value for value in transitions if value not in {"received", "sent"}
        )
        buttons["status"].configure(
            state="normal" if workflow_transitions else "disabled"
        )
        if "response" in buttons:
            buttons["response"].configure(
                state="normal"
                if record.direction == DIRECTION_INCOMING
                else "disabled"
            )

    def build_page(direction, page):
        # Keep record actions outside the resizable table/card pane.  Otherwise a
        # small window or a user-moved sash can collapse the card far enough to
        # hide the business-state buttons even though the actions still exist.
        action_area = core.ttk.Frame(page)
        action_area.pack(side="bottom", fill="x")

        pane = core.ttk.Panedwindow(page, orient="vertical")
        pane.pack(side="top", fill="both", expand=True)

        table_frame = core.ttk.Frame(pane)
        card = core.ttk.LabelFrame(pane, text="Картка вибраного листа", padding=8)
        pane.add(table_frame, weight=3)
        pane.add(card, weight=2)

        column_ids = tuple(item[0] for item in _COLUMNS)
        tree = core.ttk.Treeview(
            table_frame,
            columns=column_ids,
            show="headings",
            selectmode="browse",
        )
        for key, label, _kind, _order, width in _COLUMNS:
            tree.heading(key, text=label)
            tree.column(
                key,
                width=width,
                minwidth=55 if key not in ("subject", "correspondent") else 100,
                stretch=key in ("subject", "correspondent"),
            )
        ybar = core.ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        xbar = core.ttk.Scrollbar(
            table_frame, orient="horizontal", command=tree.xview
        )
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        detail_var = core.tk.StringVar(master=win, value="Виберіть лист у журналі.")
        detail = core.ttk.Label(
            card,
            textvariable=detail_var,
            justify="left",
            anchor="nw",
            wraplength=1040,
        )
        detail.pack(fill="both", expand=True)
        detail.bind(
            "<Configure>",
            lambda event: detail.configure(wraplength=max(360, event.width - 12)),
            add="+",
        )

        state_actions = core.ttk.Frame(action_area)
        state_actions.pack(fill="x", pady=(6, 0))
        actions = core.ttk.Frame(action_area)
        actions.pack(fill="x", pady=(6, 0))
        buttons = {}
        if direction == DIRECTION_INCOMING:
            buttons["received"] = core.ttk.Button(
                state_actions,
                text="Отримано…",
                state="disabled",
                command=lambda: open_action_transition(
                    DIRECTION_INCOMING, "received"
                ),
            )
            buttons["received"].pack(side="left")
        else:
            buttons["sent"] = core.ttk.Button(
                state_actions,
                text="Надіслано…",
                state="disabled",
                command=lambda: open_action_transition(
                    DIRECTION_OUTGOING, "sent"
                ),
            )
            buttons["sent"].pack(side="left")
        buttons["status"] = core.ttk.Button(
            state_actions,
            text="Змінити стан…",
            state="disabled",
            command=lambda d=direction: open_status_transition(d),
        )
        buttons["status"].pack(side="left", padx=(6, 0))
        buttons["history"] = core.ttk.Button(
            state_actions,
            text="Історія…",
            state="disabled",
            command=lambda d=direction: open_state_history(d),
        )
        buttons["history"].pack(side="left", padx=(6, 0))

        if direction == DIRECTION_INCOMING:
            buttons["response"] = core.ttk.Button(
                actions,
                text="Відповісти…",
                state="disabled",
                command=lambda: open_response(),
            )
            buttons["response"].pack(side="left")
        buttons["attachments"] = core.ttk.Button(
            actions,
            text="Вкладення…",
            state="disabled",
            command=lambda d=direction: open_attachments(d),
        )
        buttons["attachments"].pack(side="left", padx=(6, 0))
        buttons["open"] = core.ttk.Button(
            actions,
            text="Відкрити документ",
            state="disabled",
            command=lambda d=direction: open_record_document(d),
        )
        buttons["open"].pack(side="left", padx=(6, 0))
        buttons["case"] = core.ttk.Button(
            actions,
            text="Справа…",
            state="disabled",
            command=lambda d=direction: open_case_assignment(d),
        )
        buttons["case"].pack(side="left", padx=(6, 0))
        core.ttk.Button(
            actions, text="Оновити", command=lambda: refresh_all()
        ).pack(side="right")

        state["trees"][direction] = tree
        state["details"][direction] = detail_var
        state["buttons"][direction] = buttons
        tree.bind("<<TreeviewSelect>>", lambda _event, d=direction: update_card(d))

    def selected_case(quiet=False):
        tree = state["case_tree"]
        if tree is None:
            return None
        selected = tree.selection()
        if not selected:
            if not quiet:
                core.messagebox.showinfo(
                    "Кореспонденція", "Виберіть справу.", parent=win
                )
            return None
        return state["cases"].get(selected[0])

    def selected_case_member(quiet=False):
        case = selected_case(quiet=True)
        tree = state["case_member_tree"]
        if case is None or tree is None:
            return None
        selected = tree.selection()
        if not selected:
            if not quiet:
                core.messagebox.showinfo(
                    "Кореспонденція",
                    "Виберіть лист у справі.",
                    parent=win,
                )
            return None
        mapping = {
            row.correspondence_id: row
            for row in state["case_members"].get(case.case_id, ())
        }
        return mapping.get(selected[0])

    def update_case_member_buttons():
        case = selected_case(quiet=True)
        member = selected_case_member(quiet=True)
        buttons = state["case_buttons"]
        if not buttons:
            return
        active = case is not None and not case.archived
        buttons["rename"].configure(
            state="normal" if active else "disabled"
        )
        buttons["archive"].configure(
            state="normal" if case is not None else "disabled",
            text=(
                "Відновити"
                if case is not None and case.archived
                else "Архівувати"
            ),
        )
        buttons["linked"].configure(
            state="normal" if active else "disabled"
        )
        buttons["open"].configure(
            state="normal" if member is not None else "disabled"
        )
        buttons["remove"].configure(
            state="normal" if active and member is not None else "disabled"
        )

    def refresh_case_members():
        tree = state["case_member_tree"]
        detail = state["case_detail"]
        if tree is None or detail is None:
            return
        selected_member = tuple(tree.selection())
        tree.delete(*tree.get_children(""))
        case = selected_case(quiet=True)
        if case is None:
            detail.set("Виберіть справу.")
            update_case_member_buttons()
            return

        members = state["case_members"].get(case.case_id, ())
        detail.set(
            "%s%s\nЛистів: %d%s"
            % (
                case.title,
                " · архів" if case.archived else "",
                len(members),
                ("\n" + case.notes) if case.notes else "",
            )
        )
        for record in members:
            tree.insert(
                "",
                "end",
                iid=record.correspondence_id,
                values=(
                    record.registration_number,
                    _display_date(record.registration_date),
                    "Вхідний"
                    if record.direction == DIRECTION_INCOMING
                    else "Вихідний",
                    record.correspondent,
                    record.subject,
                    _status_label(record.status),
                ),
            )
        retained = restore_tree_selection(tree, selected_member)
        if not retained:
            children = tree.get_children("")
            if children:
                tree.selection_set(children[0])
                tree.focus(children[0])
                try:
                    tree.see(children[0])
                except Exception:
                    pass
        update_case_member_buttons()

    def refresh_cases_page(cases):
        tree = state["case_tree"]
        if tree is None:
            return
        selected = tuple(tree.selection())
        pending = state.get("pending_case")
        state["pending_case"] = None
        tree.delete(*tree.get_children(""))

        needle = search_var.get().strip().casefold()
        filter_date = parse_filter_date()
        mapping = {}
        member_mapping = {}
        for case in cases:
            members = tuple(list_case_correspondence(
                workspace_root, case.case_id
            ))
            member_mapping[case.case_id] = members
            if filter_date and not any(
                row.registration_date == filter_date for row in members
            ):
                continue
            if needle:
                haystack = " ".join(
                    [case.title, case.notes]
                    + [
                        " ".join((
                            row.registration_number,
                            row.correspondent,
                            row.subject,
                            row.summary,
                        ))
                        for row in members
                    ]
                ).casefold()
                if needle not in haystack:
                    continue
            mapping[case.case_id] = case
            tree.insert(
                "",
                "end",
                iid=case.case_id,
                values=(
                    case.title,
                    len(members),
                    "Архів" if case.archived else "Активна",
                    case.updated_at.replace("T", " "),
                ),
            )

        state["cases"] = mapping
        state["case_members"] = member_mapping
        wanted = (pending,) if pending else selected
        retained = restore_tree_selection(tree, wanted)
        if not retained:
            children = tree.get_children("")
            if children:
                tree.selection_set(children[0])
                tree.focus(children[0])
                try:
                    tree.see(children[0])
                except Exception:
                    pass
        refresh_case_members()

    def build_cases_page(page):
        action_area = core.ttk.Frame(page)
        action_area.pack(side="bottom", fill="x")

        pane = core.ttk.Panedwindow(page, orient="vertical")
        pane.pack(side="top", fill="both", expand=True)

        cases_frame = core.ttk.LabelFrame(
            pane, text="Справи / теми", padding=4
        )
        members_frame = core.ttk.LabelFrame(
            pane, text="Ланцюжок справи", padding=4
        )
        pane.add(cases_frame, weight=2)
        pane.add(members_frame, weight=3)

        case_tree = core.ttk.Treeview(
            cases_frame,
            columns=("title", "count", "state", "updated"),
            show="headings",
            selectmode="browse",
        )
        for key, label, width, stretch in (
            ("title", "Назва справи", 360, True),
            ("count", "Листів", 70, False),
            ("state", "Стан", 90, False),
            ("updated", "Оновлено", 190, False),
        ):
            case_tree.heading(key, text=label)
            case_tree.column(
                key,
                width=width,
                minwidth=60,
                stretch=stretch,
            )
        case_y = core.ttk.Scrollbar(
            cases_frame, orient="vertical", command=case_tree.yview
        )
        case_tree.configure(yscrollcommand=case_y.set)
        case_tree.grid(row=0, column=0, sticky="nsew")
        case_y.grid(row=0, column=1, sticky="ns")
        cases_frame.rowconfigure(0, weight=1)
        cases_frame.columnconfigure(0, weight=1)

        detail_var = core.tk.StringVar(
            master=win, value="Виберіть справу."
        )
        core.ttk.Label(
            members_frame,
            textvariable=detail_var,
            justify="left",
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        member_tree = core.ttk.Treeview(
            members_frame,
            columns=(
                "number",
                "date",
                "direction",
                "correspondent",
                "subject",
                "status",
            ),
            show="headings",
            selectmode="browse",
        )
        for key, label, width, stretch in (
            ("number", "№", 120, False),
            ("date", "Дата", 95, False),
            ("direction", "Напрям", 90, False),
            ("correspondent", "Кореспондент", 180, True),
            ("subject", "Тема", 260, True),
            ("status", "Стан", 130, False),
        ):
            member_tree.heading(key, text=label)
            member_tree.column(
                key, width=width, minwidth=60, stretch=stretch
            )
        member_y = core.ttk.Scrollbar(
            members_frame, orient="vertical", command=member_tree.yview
        )
        member_x = core.ttk.Scrollbar(
            members_frame, orient="horizontal", command=member_tree.xview
        )
        member_tree.configure(
            yscrollcommand=member_y.set,
            xscrollcommand=member_x.set,
        )
        member_tree.grid(row=1, column=0, sticky="nsew")
        member_y.grid(row=1, column=1, sticky="ns")
        member_x.grid(row=2, column=0, sticky="ew")
        members_frame.rowconfigure(1, weight=1)
        members_frame.columnconfigure(0, weight=1)

        row1 = core.ttk.Frame(action_area)
        row1.pack(fill="x", pady=(6, 0))
        row2 = core.ttk.Frame(action_area)
        row2.pack(fill="x", pady=(6, 0))
        buttons = {}
        buttons["new"] = core.ttk.Button(
            row1,
            text="Нова справа…",
            command=lambda: open_case_editor(),
        )
        buttons["new"].pack(side="left")
        buttons["rename"] = core.ttk.Button(
            row1,
            text="Перейменувати…",
            state="disabled",
            command=lambda: open_case_editor(selected_case()),
        )
        buttons["rename"].pack(side="left", padx=(6, 0))
        buttons["archive"] = core.ttk.Button(
            row1,
            text="Архівувати",
            state="disabled",
            command=lambda: toggle_case_archive(),
        )
        buttons["archive"].pack(side="left", padx=(6, 0))
        buttons["linked"] = core.ttk.Button(
            row1,
            text="Додати пов'язані",
            state="disabled",
            command=lambda: add_case_linked(),
        )
        buttons["linked"].pack(side="left", padx=(6, 0))

        buttons["open"] = core.ttk.Button(
            row2,
            text="Відкрити лист",
            state="disabled",
            command=lambda: open_case_member(),
        )
        buttons["open"].pack(side="left")
        buttons["remove"] = core.ttk.Button(
            row2,
            text="Вилучити зі справи",
            state="disabled",
            command=lambda: remove_case_member(),
        )
        buttons["remove"].pack(side="left", padx=(6, 0))
        core.ttk.Button(
            row2,
            text="Оновити",
            command=lambda: refresh_all(),
        ).pack(side="right")

        state["case_tree"] = case_tree
        state["case_member_tree"] = member_tree
        state["case_detail"] = detail_var
        state["case_buttons"] = buttons
        case_tree.bind(
            "<<TreeviewSelect>>",
            lambda _event: refresh_case_members(),
        )
        member_tree.bind(
            "<<TreeviewSelect>>",
            lambda _event: update_case_member_buttons(),
        )

    def parse_filter_date():
        text = date_var.get().strip()
        if not text:
            return ""
        return _parse_user_date(text, "Дата фільтра", allow_empty=False)

    def filter_rows(rows, filter_date):
        needle = search_var.get().strip().casefold()
        result = []
        for record in rows:
            if filter_date and record.registration_date != filter_date:
                continue
            if needle:
                haystack = " ".join((
                    record.registration_number,
                    record.external_number,
                    record.correspondent,
                    record.subject,
                    record.summary,
                    record.responsible_id,
                    record.status,
                )).casefold()
                if needle not in haystack:
                    continue
            result.append(record)
        return result

    def refresh_page(direction, rows):
        tree = state["trees"][direction]
        selected = tuple(tree.selection())
        pending = state["pending_select"].pop(direction, None)
        filtered = filter_rows(rows, parse_filter_date())
        tree.delete(*tree.get_children(""))
        mapping = {}
        for record in filtered:
            mapping[record.correspondence_id] = record
            count = state["attachment_counts"].get(record.correspondence_id, 0)
            attachment_text = "!" if state["attachment_error"] else str(count)
            tree.insert(
                "",
                "end",
                iid=record.correspondence_id,
                values=(
                    record.registration_number,
                    _display_date(record.registration_date),
                    record.correspondent,
                    record.subject,
                    _display_date(record.due_date),
                    _status_label(record.status),
                    "Прострочено" if is_overdue(record) else "",
                    attachment_text,
                ),
            )
        state["records"][direction] = mapping

        specs = tuple(
            (key, label, value_type, status_order)
            for key, label, value_type, status_order, _width in _COLUMNS
        )
        configure_sortable_tree(
            tree, specs, state["sort"], direction
        )

        wanted = (pending,) if pending else selected
        retained = restore_tree_selection(tree, wanted)
        if not retained:
            children = tree.get_children("")
            if children:
                tree.selection_set(children[0])
                tree.focus(children[0])
                try:
                    tree.see(children[0])
                except Exception:
                    pass
        update_card(direction)

    def refresh_all():
        try:
            incoming = tuple(incoming_journal(workspace_root))
            outgoing = tuple(outgoing_journal(workspace_root))
        except Exception as exc:
            status_var.set("Помилка реєстру кореспонденції: %s" % exc)
            return False

        try:
            attachments = tuple(list_correspondence_attachments(workspace_root))
            counts = {}
            for item in attachments:
                counts[item.correspondence_id] = (
                    counts.get(item.correspondence_id, 0) + 1
                )
            state["attachment_counts"] = counts
            state["attachment_error"] = ""
        except Exception as exc:
            state["attachment_counts"] = {}
            state["attachment_error"] = str(exc)

        try:
            refresh_page(DIRECTION_INCOMING, incoming)
            refresh_page(DIRECTION_OUTGOING, outgoing)
        except ValueError as exc:
            status_var.set(str(exc))
            return False

        suffix = ""
        if state["attachment_error"]:
            suffix = " · вкладення: помилка перевірки"
        overdue_count = sum(
            1 for record in incoming + outgoing if is_overdue(record)
        )
        status_var.set(
            "Вхідних: %d · вихідних: %d · прострочено: %d%s"
            % (len(incoming), len(outgoing), overdue_count, suffix)
        )
        return True

    def run_scheduled_refresh():
        state["after"] = None
        if _alive(win):
            refresh_all()

    def schedule_refresh(*_args):
        token = state.get("after")
        if token is not None:
            try:
                win.after_cancel(token)
            except Exception:
                pass
        state["after"] = win.after(180, run_scheduled_refresh)

    def saved(record):
        direction = record.direction
        state["pending_select"][direction] = record.correspondence_id
        refresh_all()
        book.select(state["pages"][direction])

    def open_new(direction):
        return open_correspondence_form(
            win, core, workspace_root, direction, saved
        )

    def open_response():
        record = selected_record(DIRECTION_INCOMING)
        if record is None:
            return None
        return open_correspondence_form(
            win,
            core,
            workspace_root,
            DIRECTION_OUTGOING,
            saved,
            response_to=record,
        )

    def open_attachments(direction):
        record = selected_record(direction)
        if record is None:
            return None
        return open_attachments_dialog(
            win, core, workspace_root, record, on_changed=refresh_all
        )

    def open_record_document(direction):
        record = selected_record(direction)
        if record is None:
            return False
        return _open_document_ref(
            core, win, workspace_root, record.document_ref
        )

    def open_action_transition(direction, target_status):
        record = selected_record(direction)
        if record is None:
            return None
        allowed = set(available_status_transitions(record))
        if target_status not in allowed:
            core.messagebox.showinfo(
                "Кореспонденція",
                "Ця дія недоступна для поточного стану листа.",
                parent=win,
            )
            return None

        title = (
            "Фактичне отримання"
            if target_status == "received"
            else "Фактичне відправлення"
        )
        label = (
            "Дата отримання"
            if target_status == "received"
            else "Дата відправлення"
        )
        existing_date = (
            record.received_date
            if target_status == "received"
            else record.sent_date
        )
        dialog = core.tk.Toplevel(win)
        _fit_window(core, dialog, 460, 190, 400, 170, title)
        try:
            dialog.transient(win)
        except Exception:
            pass
        body = core.ttk.Frame(dialog, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        value = core.tk.StringVar(
            master=dialog,
            value=_display_date(existing_date)
            or date.today().strftime(DATE_FORMAT),
        )
        core.ttk.Label(body, text=label).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        entry = core.ttk.Entry(body, textvariable=value, width=16)
        entry.grid(row=0, column=1, sticky="ew", pady=4)
        calendar = _calendar_button(core, body, value)
        if calendar is not None:
            calendar.grid(row=0, column=2, padx=(6, 0), pady=4)

        def apply():
            try:
                actual_date = _parse_user_date(
                    value.get(), label, allow_empty=False
                )
                if target_status == "received":
                    updated = mark_received(
                        workspace_root,
                        record.correspondence_id,
                        received_date=actual_date,
                    )
                else:
                    updated = mark_sent(
                        workspace_root,
                        record.correspondence_id,
                        sent_date=actual_date,
                    )
            except Exception as exc:
                core.messagebox.showerror(
                    "Кореспонденція", str(exc), parent=dialog
                )
                return
            dialog.destroy()
            saved(updated)

        buttons = core.ttk.Frame(body)
        buttons.grid(row=1, column=0, columnspan=3, sticky="e", pady=(12, 0))
        core.ttk.Button(
            buttons, text="Скасувати", command=dialog.destroy
        ).pack(side="right", padx=(8, 0))
        core.ttk.Button(
            buttons, text="Зберегти", style="Accent.TButton", command=apply
        ).pack(side="right")
        dialog._taxo_correspondence_action_date = value
        dialog._taxo_correspondence_apply = apply
        try:
            entry.focus_set()
        except Exception:
            pass
        return dialog

    def open_status_transition(direction):
        record = selected_record(direction)
        if record is None:
            return None
        allowed = tuple(
            value for value in available_status_transitions(record)
            if value not in {"received", "sent"}
        )
        if not allowed:
            core.messagebox.showinfo(
                "Кореспонденція",
                "Для поточного стану немає доступного переходу.",
                parent=win,
            )
            return None

        dialog = core.tk.Toplevel(win)
        _fit_window(core, dialog, 500, 200, 430, 180, "Змінити стан")
        try:
            dialog.transient(win)
        except Exception:
            pass
        body = core.ttk.Frame(dialog, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        labels = {_status_label(value): value for value in allowed}
        choice = core.tk.StringVar(master=dialog, value=next(iter(labels)))
        core.ttk.Label(body, text="Новий стан").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        combo = core.ttk.Combobox(
            body,
            textvariable=choice,
            values=tuple(labels),
            state="readonly",
        )
        combo.grid(row=0, column=1, sticky="ew", pady=4)

        def apply():
            target = labels.get(choice.get())
            if target is None:
                return
            try:
                updated = change_correspondence_status(
                    workspace_root, record.correspondence_id, target
                )
            except Exception as exc:
                core.messagebox.showerror(
                    "Кореспонденція", str(exc), parent=dialog
                )
                return
            dialog.destroy()
            saved(updated)

        buttons = core.ttk.Frame(body)
        buttons.grid(row=1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        core.ttk.Button(
            buttons, text="Скасувати", command=dialog.destroy
        ).pack(side="right", padx=(8, 0))
        core.ttk.Button(
            buttons, text="Зберегти", style="Accent.TButton", command=apply
        ).pack(side="right")
        dialog._taxo_correspondence_status_choice = choice
        dialog._taxo_correspondence_apply = apply
        return dialog

    def open_state_history(direction):
        record = selected_record(direction)
        if record is None:
            return None
        try:
            events = correspondence_state_history(
                workspace_root, record.correspondence_id
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Кореспонденція", str(exc), parent=win
            )
            return None

        dialog = core.tk.Toplevel(win)
        _fit_window(core, dialog, 680, 420, 540, 300, "Історія станів")
        body = core.ttk.Frame(dialog, padding=12)
        body.pack(fill="both", expand=True)
        core.ttk.Label(
            body,
            text="%s · %s" % (
                record.registration_number, record.subject
            ),
        ).pack(fill="x", pady=(0, 8))
        text = core.tk.Text(body, wrap="word", height=12)
        text.pack(fill="both", expand=True)
        if not events:
            text.insert("1.0", "Змін стану ще не було.")
        else:
            rows = []
            for event in events:
                action = (
                    " · дата дії %s" % _display_date(event.action_date)
                    if event.action_date else ""
                )
                rows.append(
                    "%s · %s → %s%s"
                    % (
                        event.changed_at.replace("T", " "),
                        _status_label(event.from_status),
                        _status_label(event.to_status),
                        action,
                    )
                )
            text.insert("1.0", "\n".join(rows))
        text.configure(state="disabled")
        core.ttk.Button(
            body, text="Закрити", command=dialog.destroy
        ).pack(anchor="e", pady=(8, 0))
        dialog._taxo_correspondence_history_text = text
        return dialog

    build_page(DIRECTION_INCOMING, incoming_page)
    build_page(DIRECTION_OUTGOING, outgoing_page)

    core.ttk.Button(
        header,
        text="Новий вихідний…",
        command=lambda: open_new(DIRECTION_OUTGOING),
    ).pack(side="right", padx=(8, 0))
    core.ttk.Button(
        header,
        text="Новий вхідний…",
        style="Accent.TButton",
        command=lambda: open_new(DIRECTION_INCOMING),
    ).pack(side="right", padx=(8, 0))

    core.ttk.Label(
        root, textvariable=status_var, style="Muted.TLabel"
    ).pack(fill="x", pady=(6, 0))

    search_var.trace_add("write", schedule_refresh)
    date_entry.bind("<Return>", lambda _event: refresh_all())
    date_entry.bind("<KP_Enter>", lambda _event: refresh_all())

    win._taxo_correspondence_notebook = book
    win._taxo_correspondence_trees = state["trees"]
    win._taxo_correspondence_details = state["details"]
    win._taxo_correspondence_buttons = state["buttons"]
    win._taxo_correspondence_refresh = refresh_all
    win._taxo_correspondence_new_incoming = lambda: open_new(DIRECTION_INCOMING)
    win._taxo_correspondence_new_outgoing = lambda: open_new(DIRECTION_OUTGOING)
    win._taxo_correspondence_mark_received = lambda: open_action_transition(
        DIRECTION_INCOMING, "received"
    )
    win._taxo_correspondence_mark_sent = lambda: open_action_transition(
        DIRECTION_OUTGOING, "sent"
    )
    win._taxo_correspondence_change_incoming_status = lambda: open_status_transition(
        DIRECTION_INCOMING
    )
    win._taxo_correspondence_change_outgoing_status = lambda: open_status_transition(
        DIRECTION_OUTGOING
    )
    win._taxo_correspondence_open_incoming_history = lambda: open_state_history(
        DIRECTION_INCOMING
    )
    win._taxo_correspondence_open_outgoing_history = lambda: open_state_history(
        DIRECTION_OUTGOING
    )
    win._taxo_correspondence_status = status_var
    win._taxo_correspondence_search = search_var
    win._taxo_correspondence_date_filter = date_var

    refresh_all()
    try:
        search_entry.focus_set()
    except Exception:
        pass
    return win
