# -*- coding: utf-8 -*-
"""One browser for orders and prepared paper documents with safe DOCX history."""
from __future__ import annotations

import queue
import threading
from pathlib import Path

import document_catalog
from document_library_tree import navigation_nodes, collection_navigation_nodes
from document_library_collections import (
    catalog_document_key,
    create_collection,
    move_collection,
    archive_collection,
    restore_collection,
    document_collection_ids,
    read_collection_state,
    rename_collection,
    set_document_collections,
)
import paper_documents as paperwork
from prepared_document_revision import (
    copy_prepared_document_for_editing,
    import_prepared_document_revision,
)
from prepared_document_pdf import (
    build_prepared_revision_pdf,
    suggested_prepared_pdf_name,
)
from document_viewer import open_document
from document_vault_ui import (
    open_document_vault,
    prepare_document_vault_view_copy,
    start_prepared_revision_registration,
)
from document_vault_paper_scans_ui import open_paper_scans_dialog
from paper_original_confirmation import set_paper_original_state
from datetime import date
from output_files import next_output_copy_path
from workspace import paths_for


_READER_SLOT = threading.BoundedSemaphore(1)


def _is_controlled_prepared_row(row):
    return bool(
        row
        and row.get("source") == "paper"
        and row.get("prepared_snapshot_id")
        and row.get("file_path") is not None
    )


def _reset_catalog_filters(values, state):
    """Restore the full document view without changing any saved document."""
    defaults = {
        "search": "",
        "source": "Усі — за датою",
        "scan": "Усі",
        "date_from": "",
        "date_to": "",
        "kind": "Усі типи",
        "category": "Усі категорії",
        "year": "Усі роки",
        "month": "Усі місяці",
        "employee": "Усі працівники",
        "vehicle": "Усі ТЗ",
    }
    for key, default in defaults.items():
        values[key].set(default)
    state["sort_field"] = "date"
    state["date_sort"] = "newest"
    state["number_sort"] = "ascending"
    state["category_sort"] = "ascending"
    state["page"] = 0
    state["library_filter"] = ("all",)


def open_document_catalog(parent, core, workspace_root, initial_source="all"):
    win = core.tk.Toplevel(parent)
    win.title("Документи")
    try:
        core.fit_window_to_screen(win, 1120, 690, 760, 470)
    except Exception:
        win.geometry("1120x690")

    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(3, weight=1)
    core.ttk.Label(
        body, text="Готові документи та накази",
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, sticky="w")

    search = core.tk.StringVar(value="")
    bar = core.ttk.Frame(body)
    bar.grid(row=1, column=0, sticky="ew", pady=6)
    bar.columnconfigure(1, weight=1)
    core.ttk.Label(bar, text="Пошук:").grid(row=0, column=0, sticky="w")
    core.ttk.Entry(
        bar, textvariable=search
    ).grid(row=0, column=1, sticky="ew", padx=8)

    source_options = {
        "Усі — за датою": "all",
        "Підготовлені Word — новіші": "paper",
        "У сховищі": "vault",
        "Накази": "order",
    }
    selected_label = next(
        (
            label for label, value in source_options.items()
            if value == initial_source
        ),
        "Усі — за датою",
    )
    source_choice = core.tk.StringVar(value=selected_label)
    source_box = core.ttk.Combobox(
        bar,
        textvariable=source_choice,
        state="readonly",
        values=tuple(source_options),
        width=28,
    )
    source_box.grid(row=0, column=2, sticky="e")

    all_kinds_label = "Усі типи"
    kind_choice = core.tk.StringVar(value=all_kinds_label)
    core.ttk.Label(bar, text="Тип:").grid(
        row=2, column=0, sticky="w", pady=(6, 0)
    )
    kind_box = core.ttk.Combobox(
        bar,
        textvariable=kind_choice,
        state="readonly",
        values=(all_kinds_label,),
        width=28,
    )
    kind_box.grid(
        row=2, column=1, sticky="w", padx=8, pady=(6, 0)
    )

    all_categories_label = "Усі категорії"
    category_choice = core.tk.StringVar(value=all_categories_label)
    category_bar = core.ttk.Frame(bar)
    category_bar.grid(row=2, column=2, sticky="e", pady=(6, 0))
    core.ttk.Label(category_bar, text="Категорія:").pack(side="left")
    category_box = core.ttk.Combobox(
        category_bar,
        textvariable=category_choice,
        state="readonly",
        values=(all_categories_label,),
        width=22,
    )
    category_box.pack(side="left", padx=(6, 0))

    scan_options = {
        "Усі": "all",
        "Є скани": "present",
        "Немає сканів": "absent",
        "Помилка перевірки": "error",
    }
    scan_choice = core.tk.StringVar(value="Усі")
    core.ttk.Label(bar, text="Скани:").grid(
        row=1, column=0, sticky="w", pady=(6, 0)
    )
    scan_box = core.ttk.Combobox(
        bar,
        textvariable=scan_choice,
        state="readonly",
        values=tuple(scan_options),
        width=22,
    )
    scan_box.grid(
        row=1, column=1, sticky="w", padx=8, pady=(6, 0)
    )

    date_from = core.tk.StringVar(value="")
    date_to = core.tk.StringVar(value="")
    date_bar = core.ttk.Frame(bar)
    date_bar.grid(row=1, column=2, sticky="e", pady=(6, 0))
    core.ttk.Label(date_bar, text="Від:").pack(side="left")
    date_from_entry = core.ttk.Entry(
        date_bar, textvariable=date_from, width=11
    )
    date_from_entry.pack(side="left", padx=(4, 8))
    core.ttk.Label(date_bar, text="До:").pack(side="left")
    date_to_entry = core.ttk.Entry(
        date_bar, textvariable=date_to, width=11
    )
    date_to_entry.pack(side="left", padx=(4, 8))
    apply_date_button = core.ttk.Button(
        date_bar,
        text="Застосувати",
        command=lambda: refresh(reset=True),
    )
    apply_date_button.pack(side="left")

    all_years_label = "Усі роки"
    all_months_label = "Усі місяці"
    month_labels = {
        1: "01 — Січень",
        2: "02 — Лютий",
        3: "03 — Березень",
        4: "04 — Квітень",
        5: "05 — Травень",
        6: "06 — Червень",
        7: "07 — Липень",
        8: "08 — Серпень",
        9: "09 — Вересень",
        10: "10 — Жовтень",
        11: "11 — Листопад",
        12: "12 — Грудень",
    }
    month_values = {label: "%02d" % number for number, label in month_labels.items()}
    year_choice = core.tk.StringVar(value=all_years_label)
    month_choice = core.tk.StringVar(value=all_months_label)
    core.ttk.Label(bar, text="Рік / місяць:").grid(
        row=3, column=0, sticky="w", pady=(6, 0)
    )
    period_bar = core.ttk.Frame(bar)
    period_bar.grid(row=3, column=1, columnspan=2, sticky="w", padx=8, pady=(6, 0))
    year_box = core.ttk.Combobox(
        period_bar,
        textvariable=year_choice,
        state="readonly",
        values=(all_years_label,),
        width=12,
    )
    year_box.pack(side="left")
    month_box = core.ttk.Combobox(
        period_bar,
        textvariable=month_choice,
        state="readonly",
        values=(all_months_label,),
        width=18,
    )
    month_box.pack(side="left", padx=(8, 0))

    all_employees_label = "Усі працівники"
    all_vehicles_label = "Усі ТЗ"
    employee_choice = core.tk.StringVar(value=all_employees_label)
    vehicle_choice = core.tk.StringVar(value=all_vehicles_label)
    employee_values = {}
    vehicle_values = {}
    core.ttk.Label(bar, text="Працівник / ТЗ:").grid(
        row=4, column=0, sticky="w", pady=(6, 0)
    )
    entity_bar = core.ttk.Frame(bar)
    entity_bar.grid(row=4, column=1, columnspan=2, sticky="w", padx=8, pady=(6, 0))
    employee_box = core.ttk.Combobox(
        entity_bar, textvariable=employee_choice, state="readonly",
        values=(all_employees_label,), width=34,
    )
    employee_box.pack(side="left")
    vehicle_box = core.ttk.Combobox(
        entity_bar, textvariable=vehicle_choice, state="readonly",
        values=(all_vehicles_label,), width=34,
    )
    vehicle_box.pack(side="left", padx=(8, 0))

    source_status = core.tk.StringVar(value="")
    core.ttk.Label(
        body,
        textvariable=source_status,
        wraplength=980,
        justify="left",
    ).grid(row=2, column=0, sticky="ew")

    frame = core.ttk.Frame(body)
    frame.grid(row=3, column=0, sticky="nsew", pady=6)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    navigation = core.ttk.Frame(frame)
    navigation.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
    navigation.rowconfigure(1, weight=1)
    navigation.columnconfigure(0, weight=1)
    library_mode = core.tk.StringVar(value="За видами")
    library_mode_box = core.ttk.Combobox(
        navigation, textvariable=library_mode, state="readonly",
        values=("За видами", "За датами", "Мої папки"), width=22,
    )
    library_mode_box.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    library_tree = core.ttk.Treeview(
        navigation, show="tree", selectmode="browse", height=14,
    )
    library_tree.column("#0", width=205, minwidth=145, stretch=False)
    library_tree.grid(row=1, column=0, sticky="nsew")
    library_scroll = core.ttk.Scrollbar(
        navigation, orient="vertical", command=library_tree.yview,
    )
    library_scroll.grid(row=1, column=1, sticky="ns")
    library_tree.configure(yscrollcommand=library_scroll.set)

    folder_actions = core.ttk.Frame(navigation)
    folder_actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
    folder_actions.columnconfigure(0, weight=1)
    new_folder_button = core.ttk.Button(
        folder_actions, text="Нова папка…", state="disabled"
    )
    rename_folder_button = core.ttk.Button(
        folder_actions, text="Перейменувати…", state="disabled"
    )
    move_folder_button = core.ttk.Button(
        folder_actions, text="Перемістити папку…", state="disabled"
    )
    archive_folder_button = core.ttk.Button(
        folder_actions, text="Архівувати папку…", state="disabled"
    )
    restore_folder_button = core.ttk.Button(
        folder_actions, text="Відновити з архіву…", state="disabled"
    )
    place_in_folder_button = core.ttk.Button(
        folder_actions, text="Розмістити документ…", state="disabled"
    )
    new_folder_button.grid(row=0, column=0, sticky="ew")
    rename_folder_button.grid(row=1, column=0, sticky="ew", pady=(4, 0))
    move_folder_button.grid(row=2, column=0, sticky="ew", pady=(4, 0))
    archive_folder_button.grid(row=3, column=0, sticky="ew", pady=(4, 0))
    restore_folder_button.grid(row=4, column=0, sticky="ew", pady=(4, 0))
    place_in_folder_button.grid(row=5, column=0, sticky="ew", pady=(4, 0))

    cols = ("date", "number", "category", "kind", "title", "person", "revision", "source", "paper_original", "scans", "file")
    tree = core.ttk.Treeview(
        frame, columns=cols, show="headings", selectmode="browse"
    )
    for key, label, width in (
        ("date", "Дата", 100),
        ("number", "№", 80),
        ("category", "Категорія", 145),
        ("kind", "Документ", 125),
        ("title", "Тема / назва", 300),
        ("person", "Працівники / ТЗ", 220),
        ("revision", "Ред.", 65),
        ("source", "Джерело", 135),
        ("paper_original", "Папір / підпис", 160),
        ("scans", "Скани", 90),
        ("file", "Стан файла", 185),
    ):
        tree.heading(key, text=label)
        tree.column(key, width=width, minwidth=55)
    vertical = core.ttk.Scrollbar(
        frame, orient="vertical", command=tree.yview
    )
    horizontal = core.ttk.Scrollbar(
        frame, orient="horizontal", command=tree.xview
    )
    tree.configure(
        yscrollcommand=vertical.set,
        xscrollcommand=horizontal.set,
    )
    tree.grid(row=0, column=1, sticky="nsew")
    vertical.grid(row=0, column=2, sticky="ns")
    horizontal.grid(row=1, column=1, sticky="ew")

    actions = core.ttk.Frame(body)
    actions.grid(row=4, column=0, sticky="ew", pady=(4, 0))
    page_text = core.tk.StringVar(value="")
    state = {
        "date_sort": "newest",
        "sort_field": "date",
        "number_sort": "ascending",
        "category_sort": "ascending",
        "page": 0,
        "pages": 1,
        "rows": {},
        "library_filter": ("all",),
        "library_nodes": {},
        "after": None,
        "poll": None,
        "retry": None,
        "snapshot": None,
        "generation": 0,
        "busy": False,
        "wanted": None,
        "needs_reload": False,
        "resetting": False,
        "results": queue.Queue(),
        "vault_results": queue.Queue(),
        "vault_busy": False,
        "library_error": "",
    }

    edit_copy_button = core.ttk.Button(
        actions, text="Копія для редагування…", state="disabled"
    )
    import_revision_button = core.ttk.Button(
        actions, text="Додати редакцію DOCX…", state="disabled"
    )
    pdf_button = core.ttk.Button(
        actions, text="PDF / друк…", state="disabled"
    )
    vault_store_button = core.ttk.Button(
        body,
        text="Зберегти вибрану редакцію у сховищі",
        state="disabled",
    )
    vault_open_button = core.ttk.Button(
        body,
        text="Переглянути сховище документів",
    )
    paper_scans_button = core.ttk.Button(
        body,
        text="Скани…",
        state="disabled",
    )
    paper_original_button = core.ttk.Button(body, text="Паперовий підпис…", state="disabled")

    def selected_row():
        selected = tree.selection()
        if not selected:
            return None
        return state["rows"].get(selected[0])

    def selected_collection_id():
        selected = library_tree.selection()
        value = state["library_nodes"].get(
            selected[0] if selected else "", ()
        )
        if value and value[0] == "collection" and len(value) >= 2:
            return value[1]
        return ""

    def update_folder_actions():
        custom = library_mode.get() == "Мої папки"
        new_folder_button.configure(state="normal" if custom else "disabled")
        selected_folder = bool(selected_collection_id())
        rename_folder_button.configure(
            state="normal" if custom and selected_folder else "disabled"
        )
        move_folder_button.configure(
            state="normal" if custom and selected_folder else "disabled"
        )
        archive_folder_button.configure(
            state="normal" if custom and selected_folder else "disabled"
        )
        restore_folder_button.configure(
            state="normal" if custom else "disabled"
        )
        if custom and selected_folder:
            place_in_folder_button.configure(
                text="Додати документ у цю папку…",
                state="normal" if state.get("snapshot") is not None else "disabled",
            )
        else:
            place_in_folder_button.configure(
                text="Розмістити вибраний документ…",
                state="normal" if selected_row() is not None else "disabled",
            )

    def selection_changed(_event=None):
        row = selected_row()
        prepared = _is_controlled_prepared_row(row)
        value = "normal" if prepared else "disabled"
        edit_copy_button.configure(state=value)
        import_revision_button.configure(state=value)
        pdf_button.configure(state=value)
        vault_store_button.configure(
            state=(
                "normal"
                if prepared and not state["vault_busy"]
                else "disabled"
            )
        )
        paper_original_button.configure(state="normal" if row and row.get("vault_id") else "disabled")
        paper_scans_button.configure(
            state=(
                "normal"
                if row and row.get("vault_id")
                else "disabled"
            )
        )
        update_folder_actions()

    def create_user_folder():
        if library_mode.get() != "Мої папки":
            return
        parent_id = selected_collection_id()
        name = core.simpledialog.askstring(
            "Нова папка",
            (
                "Назва нової папки:"
                + ("\n\nВона буде створена всередині вибраної папки." if parent_id else "")
            ),
            parent=win,
        )
        if name is None:
            return
        try:
            created = create_collection(workspace_root, name, parent_id)
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        state["library_filter"] = ("collection", created.collection_id, ())
        refresh(reset=True)

    def rename_user_folder():
        collection_id = selected_collection_id()
        if not collection_id:
            core.messagebox.showinfo(
                "Мої папки", "Виберіть папку, яку треба перейменувати.", parent=win
            )
            return
        try:
            collection_state = read_collection_state(workspace_root)
            current = next(
                row for row in collection_state.collections
                if row.collection_id == collection_id
            )
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        name = core.simpledialog.askstring(
            "Перейменувати папку",
            "Нова назва папки:",
            initialvalue=current.name,
            parent=win,
        )
        if name is None:
            return
        try:
            rename_collection(workspace_root, collection_id, name)
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        refresh(reset=False)

    def move_user_folder():
        folder_id = selected_collection_id()
        if not folder_id or library_mode.get() != "Мої папки":
            return
        try:
            folder_state = read_collection_state(workspace_root)
            by_id = {item.collection_id: item for item in folder_state.collections}
            selected_folder = by_id[folder_id]
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return

        # Show only legal target folders; the data layer also rechecks on save.
        descendants = {folder_id}
        changed = True
        while changed:
            changed = False
            for item in folder_state.collections:
                if item.parent_id in descendants and item.collection_id not in descendants:
                    descendants.add(item.collection_id)
                    changed = True
        candidates = [
            item for item in folder_state.collections
            if not item.archived_at and item.collection_id not in descendants
        ]
        candidates.sort(key=lambda item: (item.name.casefold(), item.collection_id))
        choices = [("На верхній рівень", "")]
        choices.extend((item.name, item.collection_id) for item in candidates)
        dialog = core.tk.Toplevel(win)
        dialog.title("Перемістити папку")
        dialog.transient(win)
        dialog.resizable(False, False)
        content = core.ttk.Frame(dialog, padding=12)
        content.pack(fill="both", expand=True)
        core.ttk.Label(
            content,
            text="Куди перемістити папку «%s»?" % selected_folder.name,
            wraplength=380,
        ).pack(anchor="w")
        destination = core.tk.StringVar(value=choices[0][0])
        by_caption = {}
        for caption, identity in choices:
            unique_caption = caption
            if caption in by_caption:
                unique_caption = "%s (%s)" % (caption, identity[-6:])
            by_caption[unique_caption] = identity
        selector = core.ttk.Combobox(
            content, state="readonly", textvariable=destination,
            values=tuple(by_caption), width=44,
        )
        selector.pack(fill="x", pady=9)
        destination.set(next(
            (caption for caption, identity in by_caption.items()
             if identity == selected_folder.parent_id),
            next(iter(by_caption)),
        ))
        buttons = core.ttk.Frame(content)
        buttons.pack(fill="x")

        def apply_move():
            target_id = by_caption[destination.get()]
            if target_id == selected_folder.parent_id:
                dialog.destroy()
                return
            try:
                move_collection(workspace_root, folder_id, target_id)
            except Exception as exc:
                core.messagebox.showerror("Мої папки", str(exc), parent=dialog)
                return
            dialog.destroy()
            state["library_filter"] = ("collection", folder_id, ())
            refresh(reset=True)

        core.ttk.Button(buttons, text="Скасувати", command=dialog.destroy).pack(side="right")
        core.ttk.Button(buttons, text="Перемістити", command=apply_move).pack(
            side="right", padx=(0, 6)
        )

    def archive_user_folder():
        folder_id = selected_collection_id()
        if not folder_id or library_mode.get() != "Мої папки":
            return
        try:
            folder_state = read_collection_state(workspace_root)
            record = next(
                item for item in folder_state.collections if item.collection_id == folder_id
            )
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        if not core.messagebox.askyesno(
            "Архівувати папку",
            "Приховати папку «%s» та її вкладені папки?\n\n"
            "Документи, скани та їхнє розміщення НЕ видаляються. "
            "Папки можна буде відновити." % record.name,
            parent=win,
        ):
            return
        try:
            archive_collection(workspace_root, folder_id)
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        state["library_filter"] = ("all",)
        refresh(reset=True)

    def restore_user_folder():
        if library_mode.get() != "Мої папки":
            return
        try:
            folder_state = read_collection_state(workspace_root)
            by_id = {item.collection_id: item for item in folder_state.collections}
            archived = [
                item for item in folder_state.collections
                if item.archived_at and (
                    not item.parent_id or not by_id[item.parent_id].archived_at
                )
            ]
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        if not archived:
            core.messagebox.showinfo(
                "Мої папки", "Немає архівних папок для відновлення.", parent=win
            )
            return
        archived.sort(key=lambda item: (item.name.casefold(), item.collection_id))
        dialog = core.tk.Toplevel(win)
        dialog.title("Відновити папку з архіву")
        dialog.transient(win)
        content = core.ttk.Frame(dialog, padding=12)
        content.pack(fill="both", expand=True)
        core.ttk.Label(
            content,
            text="Виберіть папку. Усі вкладені папки та їхні документи повернуться.",
            wraplength=380,
        ).pack(anchor="w")
        listing = core.tk.Listbox(content, height=min(len(archived), 12), width=48)
        listing.pack(fill="both", expand=True, pady=8)
        for item in archived:
            listing.insert("end", item.name + "  [" + item.collection_id[-6:] + "]")
        buttons = core.ttk.Frame(content)
        buttons.pack(fill="x")

        def apply_restore():
            selected = listing.curselection()
            if not selected:
                core.messagebox.showinfo(
                    "Мої папки", "Виберіть архівну папку.", parent=dialog
                )
                return
            try:
                restore_collection(workspace_root, archived[selected[0]].collection_id)
            except Exception as exc:
                core.messagebox.showerror("Мої папки", str(exc), parent=dialog)
                return
            dialog.destroy()
            state["library_filter"] = ("all",)
            refresh(reset=True)

        core.ttk.Button(buttons, text="Скасувати", command=dialog.destroy).pack(side="right")
        core.ttk.Button(buttons, text="Відновити", command=apply_restore).pack(
            side="right", padx=(0, 6)
        )

    def add_document_to_selected_folder():
        """Choose from ALL catalog documents, even when current folder is empty."""
        folder_id = selected_collection_id()
        snapshot = state.get("snapshot")
        if not folder_id or snapshot is None:
            core.messagebox.showinfo(
                "Мої папки", "Спочатку виберіть власну папку.", parent=win
            )
            return
        try:
            folder_state = read_collection_state(workspace_root)
            folder = next(
                item for item in folder_state.collections
                if item.collection_id == folder_id and not item.archived_at
            )
        except (ValueError, StopIteration) as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return

        # The folder view is only a filter. Do not use its visible rows:
        # an empty folder has no rows, but still must accept documents.
        available = []
        seen = set()
        for item in snapshot.get("rows", ()):
            try:
                key = catalog_document_key(item)
            except ValueError:
                continue
            if key in seen:
                continue
            seen.add(key)
            available.append((key, item))
        if not available:
            core.messagebox.showinfo(
                "Мої папки", "У каталозі ще немає готових документів.", parent=win
            )
            return

        dialog = core.tk.Toplevel(win)
        dialog.title("Додати документ у папку")
        try:
            core.fit_window_to_screen(dialog, 700, 500, 460, 320)
        except Exception:
            dialog.geometry("700x500")
        dialog.transient(win)
        holder = core.ttk.Frame(dialog, padding=12)
        holder.pack(fill="both", expand=True)
        core.ttk.Label(
            holder,
            text="Папка: %s. Виберіть документ із усього каталогу."
                 % folder.name,
            wraplength=640,
        ).pack(anchor="w")
        core.ttk.Label(
            holder,
            text="Оригінал, скани й інші папки документа залишаться без змін.",
            wraplength=640,
        ).pack(anchor="w", pady=(0, 8))
        search_var = core.tk.StringVar(value="")
        core.ttk.Entry(holder, textvariable=search_var).pack(
            fill="x", pady=(0, 8)
        )
        listing = core.tk.Listbox(
            holder, selectmode="browse", exportselection=False
        )
        listing.pack(fill="both", expand=True)
        visible = []

        def refresh_choices(*_):
            needle = search_var.get().strip().casefold()
            visible.clear()
            listing.delete(0, "end")
            for key, item in available:
                title = "%s | № %s | %s | %s" % (
                    item.get("date") or "Без дати",
                    item.get("number") or "—",
                    item.get("title") or item.get("kind") or "Документ",
                    item.get("source_label") or "",
                )
                if needle and needle not in title.casefold():
                    continue
                visible.append(key)
                listing.insert("end", title)
        search_var.trace_add("write", refresh_choices)
        refresh_choices()
        actions = core.ttk.Frame(holder)
        actions.pack(fill="x", pady=(8, 0))

        def save_selected():
            selected = listing.curselection()
            if not selected:
                core.messagebox.showinfo(
                    "Мої папки", "Спочатку виберіть документ зі списку.",
                    parent=dialog,
                )
                return
            key = visible[selected[0]]
            try:
                old = document_collection_ids(workspace_root, key)
                if folder_id not in old:
                    set_document_collections(
                        workspace_root, key, old + (folder_id,)
                    )
            except Exception as exc:
                core.messagebox.showerror(
                    "Мої папки", str(exc), parent=dialog
                )
                return
            dialog.destroy()
            # Keep the chosen folder open and display the added document.
            refresh(reset=True)

        core.ttk.Button(
            actions, text="Скасувати", command=dialog.destroy
        ).pack(side="right")
        core.ttk.Button(
            actions, text="Додати у папку", command=save_selected
        ).pack(side="right", padx=(0, 6))
        listing.bind("<Double-1>", lambda _event: save_selected())

    def manage_document_folders():
        if library_mode.get() == "Мої папки" and selected_collection_id():
            add_document_to_selected_folder()
        else:
            place_selected_in_folders()

    def place_selected_in_folders():
        row = selected_row()
        if row is None:
            core.messagebox.showinfo(
                "Мої папки", "Виберіть документ.", parent=win
            )
            return
        try:
            document_key = catalog_document_key(row)
            collection_state = read_collection_state(workspace_root)
            active = {
                item.collection_id: item
                for item in collection_state.collections
                if not item.archived_at
            }
            current = set(document_collection_ids(workspace_root, document_key))
        except Exception as exc:
            core.messagebox.showerror("Мої папки", str(exc), parent=win)
            return
        if not active:
            core.messagebox.showinfo(
                "Мої папки",
                "Спочатку створіть хоча б одну власну папку.",
                parent=win,
            )
            return

        children = {}
        for item in active.values():
            parent_id = item.parent_id if item.parent_id in active else ""
            children.setdefault(parent_id, []).append(item)
        for values in children.values():
            values.sort(key=lambda item: (
                item.sort_order, item.name.casefold(), item.collection_id
            ))
        display = []

        def append_children(parent_id, depth):
            for item in children.get(parent_id, ()):
                display.append((item.collection_id, ("   " * depth) + item.name))
                append_children(item.collection_id, depth + 1)

        append_children("", 0)

        dialog = core.tk.Toplevel(win)
        dialog.title("Розміщення документа")
        try:
            core.fit_window_to_screen(dialog, 480, 430, 380, 300)
        except Exception:
            dialog.geometry("480x430")
        dialog.transient(win)
        holder = core.ttk.Frame(dialog, padding=12)
        holder.pack(fill="both", expand=True)
        core.ttk.Label(
            holder,
            text=(
                "Оберіть одну або кілька папок. Це лише розміщення у бібліотеці — "
                "файл документа не переноситься і не копіюється."
            ),
            wraplength=440,
            justify="left",
        ).pack(fill="x", pady=(0, 8))
        listing = core.tk.Listbox(
            holder, selectmode="multiple", exportselection=False
        )
        listing.pack(fill="both", expand=True)
        for index, (collection_id, label) in enumerate(display):
            listing.insert("end", label)
            if collection_id in current:
                listing.selection_set(index)

        buttons = core.ttk.Frame(holder)
        buttons.pack(fill="x", pady=(8, 0))

        def save_placement():
            selected_ids = [
                display[index][0]
                for index in listing.curselection()
            ]
            try:
                set_document_collections(
                    workspace_root, document_key, selected_ids
                )
            except Exception as exc:
                core.messagebox.showerror(
                    "Мої папки", str(exc), parent=dialog
                )
                return
            dialog.destroy()
            state["library_filter"] = ("all",)
            refresh(reset=True)

        core.ttk.Button(
            buttons, text="Скасувати", command=dialog.destroy
        ).pack(side="right")
        core.ttk.Button(
            buttons, text="Зберегти розміщення", command=save_placement
        ).pack(side="right", padx=(0, 6))

    def render_library_tree(snapshot):
        """Show virtual folders without changing stored documents."""
        label = library_mode.get()
        state["library_error"] = ""
        try:
            if label == "Мої папки":
                collection_state = read_collection_state(workspace_root)
                nodes = collection_navigation_nodes(snapshot, collection_state)
            else:
                mode = "date" if label == "За датами" else "kind"
                nodes = navigation_nodes(snapshot, mode)
        except Exception as exc:
            state["library_error"] = "Мої папки: " + str(exc)
            nodes = (("all", "", "Усі документи", len(snapshot.get("rows", ())), ("all",)),)
        state["library_nodes"] = {
            key: value for key, _parent, _title, _count, value in nodes
        }
        active_filter = state["library_filter"]
        state["drawing_library_tree"] = True
        try:
            library_tree.delete(*library_tree.get_children())
            selected = "all"
            current_selection = ("all",)
            for key, parent, title, count, value in nodes:
                library_tree.insert(
                    parent, "end", iid=key,
                    text="%s (%d)" % (title, count),
                    open=True,
                )
                # Membership keys can change when a document is added.
                # Compare stable folder ID, not a stale snapshot of its contents.
                same_folder = (
                    active_filter
                    and value
                    and active_filter[0] == "collection"
                    and value[0] == "collection"
                    and len(active_filter) > 1
                    and active_filter[1] == value[1]
                )
                if value == active_filter or same_folder:
                    selected = key
                    current_selection = value
            state["library_filter"] = current_selection
            library_tree.selection_set(selected)
            library_tree.focus(selected)
            update_folder_actions()
        finally:
            state["drawing_library_tree"] = False

    def change_library_mode(_event=None):
        state["library_filter"] = ("all",)
        refresh(reset=True)

    def select_library_node(_event=None):
        if state.get("drawing_library_tree"):
            return
        selected = library_tree.selection()
        selected_filter = state["library_nodes"].get(
            selected[0] if selected else "all", ("all",)
        )
        if selected_filter != state["library_filter"]:
            state["library_filter"] = selected_filter
            refresh(reset=True)
        update_folder_actions()

    def render(result):
        state["page"], state["pages"] = result["page"], result["pages"]
        tree.heading(
            "date",
            text=(
                ("Дата ▼" if state["date_sort"] == "newest" else "Дата ▲")
                if state["sort_field"] == "date" else "Дата"
            ),
        )
        tree.heading(
            "number",
            text=(
                ("№ ▲" if state["number_sort"] == "ascending" else "№ ▼")
                if state["sort_field"] == "number" else "№"
            ),
        )
        tree.heading(
            "category",
            text=(
                ("Категорія ▲" if state["category_sort"] == "ascending" else "Категорія ▼")
                if state["sort_field"] == "category" else "Категорія"
            ),
        )
        available_kinds = tuple(result.get("available_kinds", ()))
        selected_kind = kind_choice.get()
        kind_values = (all_kinds_label,) + available_kinds
        if (
            selected_kind
            and selected_kind != all_kinds_label
            and selected_kind not in available_kinds
        ):
            kind_values = (all_kinds_label, selected_kind) + available_kinds
        kind_box.configure(values=kind_values)
        available_categories = tuple(result.get("available_categories", ()))
        selected_category = category_choice.get()
        category_values = (all_categories_label,) + available_categories
        if (
            selected_category
            and selected_category != all_categories_label
            and selected_category not in available_categories
        ):
            category_values = (
                all_categories_label, selected_category
            ) + available_categories
        category_box.configure(values=category_values)
        available_years = tuple(str(value) for value in result.get("available_years", ()))
        selected_year = year_choice.get()
        year_values = (all_years_label,) + available_years
        if (
            selected_year
            and selected_year != all_years_label
            and selected_year not in available_years
        ):
            year_values = (all_years_label, selected_year) + available_years
        year_box.configure(values=year_values)

        available_months = tuple(
            month_labels[value]
            for value in result.get("available_months", ())
            if value in month_labels
        )
        selected_month = month_choice.get()
        month_options = (all_months_label,) + available_months
        if (
            selected_month
            and selected_month != all_months_label
            and selected_month not in available_months
        ):
            month_options = (all_months_label, selected_month) + available_months
        month_box.configure(values=month_options)

        employee_pairs = tuple(result.get("available_employees", ()))
        employee_values.clear()
        employee_values.update({label: key for key, label in employee_pairs})
        employee_labels = (all_employees_label,) + tuple(label for _key, label in employee_pairs)
        if employee_choice.get() not in employee_labels:
            employee_choice.set(all_employees_label)
        employee_box.configure(values=employee_labels)

        vehicle_pairs = tuple(result.get("available_vehicles", ()))
        vehicle_values.clear()
        vehicle_values.update({label: key for key, label in vehicle_pairs})
        vehicle_labels = (all_vehicles_label,) + tuple(label for _key, label in vehicle_pairs)
        if vehicle_choice.get() not in vehicle_labels:
            vehicle_choice.set(all_vehicles_label)
        vehicle_box.configure(values=vehicle_labels)

        source_status.set(" ".join(
            value for value in (
                result.get("order_status", ""),
                result.get("paper_status", ""),
                result.get("vault_status", ""),
                result.get("paper_scan_status", ""),
                result.get("paper_original_status", ""),
                state.get("library_error", ""),
            )
            if value
        ))
        page_text.set(
            "Сторінка %d з %d · записів: %d"
            % (result["page"] + 1, result["pages"], result["total"])
        )
        previous = tree.selection()
        previous_key = None
        if previous:
            old = state["rows"].get(previous[0])
            previous_key = old.get("key") if old else None
        tree.delete(*tree.get_children())
        state["rows"].clear()
        selected_iid = None
        for number, row in enumerate(result["rows"]):
            iid = str(number)
            state["rows"][iid] = row
            tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    row["date"],
                    row["number"],
                    row.get("category", document_catalog.CATEGORY_UNCLASSIFIED),
                    row["kind"],
                    row["title"],
                    row["person"],
                    row.get("revision_label", ""),
                    row.get("source_label", ""),
                    row.get("paper_original_state", "—"),
                    row.get("paper_scan_state", "—"),
                    row["file_state"],
                ),
            )
            if previous_key is not None and row.get("key") == previous_key:
                selected_iid = iid
        if selected_iid is not None:
            tree.selection_set(selected_iid)
            tree.focus(selected_iid)
            tree.see(selected_iid)
        selection_changed()

    def toggle_date_sort():
        if state["sort_field"] == "date":
            state["date_sort"] = (
                "oldest" if state["date_sort"] == "newest" else "newest"
            )
        else:
            state["sort_field"] = "date"
            state["date_sort"] = "newest"
        refresh(reset=True)

    def toggle_number_sort():
        if state["sort_field"] == "number":
            state["number_sort"] = (
                "descending"
                if state["number_sort"] == "ascending" else "ascending"
            )
        else:
            state["sort_field"] = "number"
            state["number_sort"] = "ascending"
        refresh(reset=True)

    def toggle_category_sort():
        if state["sort_field"] == "category":
            state["category_sort"] = (
                "descending"
                if state["category_sort"] == "ascending" else "ascending"
            )
        else:
            state["sort_field"] = "category"
            state["category_sort"] = "ascending"
        refresh(reset=True)

    def refresh(reset=False, reload_sources=False):
        if reset:
            state["page"] = 0
        state["generation"] += 1
        state["needs_reload"] = state["needs_reload"] or reload_sources
        state["wanted"] = (
            search.get(),
            state["page"],
            reload_sources,
            source_options.get(source_choice.get(), "all"),
            scan_options.get(scan_choice.get(), "all"),
            date_from.get(),
            date_to.get(),
            kind_choice.get(),
            category_choice.get(),
            year_choice.get(),
            month_choice.get(),
            employee_values.get(employee_choice.get(), "all"),
            vehicle_values.get(vehicle_choice.get(), "all"),
            state["date_sort"] if state["sort_field"] == "date" else "default",
            state["number_sort"] if state["sort_field"] == "number" else "default",
            state["category_sort"] if state["sort_field"] == "category" else "default",
            state["library_filter"],
        )
        source_status.set("Завантаження документів…")
        if not state["busy"]:
            start_worker(state["generation"], state["wanted"])

    def start_worker(generation, wanted):
        if not _READER_SLOT.acquire(blocking=False):
            source_status.set(
                "Попереднє читання ще триває. "
                "Перевірте з'єднання зі сховищем."
            )
            if state["retry"] is None:
                def retry():
                    state["retry"] = None
                    if not state["busy"]:
                        start_worker(
                            state["generation"], state["wanted"]
                        )
                state["retry"] = win.after(500, retry)
            return
        if state["retry"] is not None:
            win.after_cancel(state["retry"])
            state["retry"] = None
        state["busy"] = True
        (
            text_filter,
            page,
            reload_sources,
            source_filter,
            scan_filter,
            date_from_filter,
            date_to_filter,
            kind_filter_label,
            category_filter_label,
            year_filter_label,
            month_filter_label,
            employee_filter,
            vehicle_filter,
            date_sort,
            number_sort,
            category_sort,
            library_filter,
        ) = wanted
        previous = state["snapshot"]
        must_reload = (
            state["needs_reload"]
            or reload_sources
            or previous is None
        )

        def worker():
            try:
                snapshot = (
                    document_catalog.read_sources(workspace_root)
                    if must_reload else previous
                )
                result = document_catalog.paginate_sources(
                    snapshot,
                    text_filter,
                    page,
                    source_filter=source_filter,
                    scan_filter=scan_filter,
                    date_from=date_from_filter,
                    date_to=date_to_filter,
                    kind_filter=(
                        "all"
                        if kind_filter_label == all_kinds_label
                        else kind_filter_label
                    ),
                    category_filter=(
                        "all"
                        if category_filter_label == all_categories_label
                        else category_filter_label
                    ),
                    year_filter=(
                        "all"
                        if year_filter_label == all_years_label
                        else year_filter_label
                    ),
                    month_filter=(
                        "all"
                        if month_filter_label == all_months_label
                        else month_values.get(month_filter_label, "all")
                    ),
                    employee_filter=employee_filter,
                    vehicle_filter=vehicle_filter,
                    date_sort=date_sort,
                    number_sort=number_sort,
                    category_sort=category_sort,
                    library_filter=library_filter,
                )
                state["results"].put(
                    (generation, snapshot, result, None)
                )
            except Exception as exc:
                state["results"].put(
                    (generation, None, None, str(exc))
                )
            finally:
                _READER_SLOT.release()

        try:
            threading.Thread(target=worker, daemon=True).start()
        except Exception as exc:
            state["busy"] = False
            _READER_SLOT.release()
            source_status.set(
                "Не вдалося запустити читання: " + str(exc)
            )

    def poll_results():
        while True:
            try:
                generation, snapshot, result, error = (
                    state["results"].get_nowait()
                )
            except queue.Empty:
                break
            state["busy"] = False
            if generation != state["generation"]:
                start_worker(
                    state["generation"], state["wanted"]
                )
                continue
            if error:
                source_status.set(
                    "Не вдалося прочитати каталог: " + error
                )
            else:
                state["snapshot"] = snapshot
                state["needs_reload"] = False
                render_library_tree(snapshot)
                render(result)

        while True:
            try:
                ok, payload = state["vault_results"].get_nowait()
            except queue.Empty:
                break
            state["vault_busy"] = False
            if ok:
                core.messagebox.showinfo(
                    "Сховище документів",
                    (
                        "Точну редакцію r%d збережено у DocumentVault.\n\n"
                        "Це готова незмінна копія, але не автоматичний "
                        "факт підпису."
                    ) % payload.document_revision,
                    parent=win,
                )
                source_status.set(
                    "Документ додано у сховище: %s · SHA-256 %s…"
                    % (payload.vault_id, payload.content_sha256[:12])
                )
                refresh(reset=True, reload_sources=True)
            else:
                core.messagebox.showerror(
                    "Сховище документів",
                    str(payload),
                    parent=win,
                )
            selection_changed()
        state["poll"] = win.after(100, poll_results)

    def cancel_pending(event):
        if event.widget is not win:
            return
        for key in ("after", "poll", "retry"):
            token = state.get(key)
            if token is not None:
                try:
                    win.after_cancel(token)
                except Exception:
                    pass
                state[key] = None

    def search_changed(*_):
        if state["resetting"]:
            return
        if state["after"] is not None:
            win.after_cancel(state["after"])

        def later():
            state["after"] = None
            refresh(reset=True, reload_sources=True)

        state["after"] = win.after(250, later)

    def clear_filters():
        # Reset all controls in one pass; do not schedule a second search read.
        if state["after"] is not None:
            win.after_cancel(state["after"])
            state["after"] = None
        state["resetting"] = True
        try:
            _reset_catalog_filters({
                "search": search,
                "source": source_choice,
                "scan": scan_choice,
                "date_from": date_from,
                "date_to": date_to,
                "kind": kind_choice,
                "category": category_choice,
                "year": year_choice,
                "month": month_choice,
                "employee": employee_choice,
                "vehicle": vehicle_choice,
            }, state)
        finally:
            state["resetting"] = False
        if library_tree.exists("all"):
            library_tree.selection_set("all")
        refresh(reset=True)

    def change_page(delta):
        state["page"] = max(
            0,
            min(
                state["page"] + delta,
                state["pages"] - 1,
            ),
        )
        refresh()

    def open_selected(_event=None):
        row = selected_row()
        if row is None:
            core.messagebox.showinfo(
                "Документи", "Виберіть документ.", parent=win
            )
            return
        if _is_controlled_prepared_row(row):
            if core.messagebox.askyesno(
                "Prepared Word",
                "Ця редакція зберігається в історії Taxo і не відкривається "
                "для редагування напряму.\n\n"
                "Створити окрему копію DOCX для Word?",
                parent=win,
            ):
                copy_for_editing()
            return
        if row["source"] == "order":
            callback = getattr(
                parent.winfo_toplevel(),
                "_taxo_preview_catalog_order",
                None,
            )
            if callback is None:
                core.messagebox.showinfo(
                    "Наказ",
                    "Відкрийте цей наказ у розділі «Накази».",
                    parent=win,
                )
                return
            try:
                callback(row["source_id"])
            except Exception as exc:
                core.messagebox.showerror(
                    "Наказ", str(exc), parent=win
                )
            return
        if row["source"] == "vault":
            try:
                view_path = prepare_document_vault_view_copy(
                    workspace_root, row["vault_id"]
                )
                open_document(
                    win,
                    view_path,
                    external_opener=core.open_external,
                )
            except Exception as exc:
                core.messagebox.showerror(
                    "Документ зі сховища", str(exc), parent=win
                )
            return
        try:
            path = row["file_path"]
            if (
                path is None
                or document_catalog.paper_file(
                    workspace_root, path.name
                ) != path
            ):
                raise ValueError("Небезпечний шлях до документа.")
            if not path.is_file():
                raise FileNotFoundError(
                    "Файл документа відсутній: " + str(path)
                )
            paperwork.open_file(path)
        except Exception as exc:
            core.messagebox.showerror(
                "Документ", str(exc), parent=win
            )

    def copy_for_editing():
        row = selected_row()
        if not row or not row.get("prepared_snapshot_id"):
            return
        original = row.get("file_path")
        initial = (
            original.stem + "_edit.docx"
            if isinstance(original, Path)
            else "Taxo_document_edit.docx"
        )
        target = core.filedialog.asksaveasfilename(
            parent=win,
            title="Створити копію DOCX для редагування",
            defaultextension=".docx",
            filetypes=[("Word DOCX", "*.docx")],
            initialfile=initial,
        )
        if not target:
            return
        try:
            path = copy_prepared_document_for_editing(
                workspace_root,
                row["source_id"],
                Path(target),
                overwrite=True,
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Копія для редагування", str(exc), parent=win
            )
            return
        if core.messagebox.askyesno(
            "Копію створено",
            "Копію збережено окремо від каталогу Taxo.\n\n"
            "Відкрити її у Word зараз?",
            parent=win,
        ):
            paperwork.open_file(path)

    def create_pdf_for_print():
        row = selected_row()
        if not row or not row.get("prepared_snapshot_id"):
            return
        output_dir = paths_for(workspace_root)["output"]
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / suggested_prepared_pdf_name(row)
        if target.exists():
            target = next_output_copy_path(target)
        font_path = next(
            (
                Path(value)
                for value in core.report_font_candidates()
                if Path(value).is_file()
            ),
            None,
        )
        try:
            actual = core.write_output_file(
                lambda out: build_prepared_revision_pdf(
                    workspace_root,
                    row["source_id"],
                    out,
                    font_path=font_path,
                    overwrite=True,
                ),
                target,
                parent=win,
                kind="PDF підготовленого документа",
                error_title="PDF / друк",
            )
            if actual is None:
                return
            open_document(
                win,
                actual,
                external_opener=core.open_external,
            )
        except Exception as exc:
            core.messagebox.showerror(
                "PDF / друк", str(exc), parent=win
            )

    def store_selected_in_vault():
        row = selected_row()
        if not _is_controlled_prepared_row(row) or state["vault_busy"]:
            return
        if not core.messagebox.askyesno(
            "Зберегти у сховищі документів",
            (
                "Taxo збереже точну редакцію %s як окрему незмінну "
                "копію у DocumentVault.\n\n"
                "Ця дія не означає, що документ підписано або проведено. "
                "Продовжити?"
            ) % row.get("revision_label", ""),
            parent=win,
        ):
            return
        state["vault_busy"] = True
        selection_changed()
        try:
            start_prepared_revision_registration(
                workspace_root,
                row["source_id"],
                state["vault_results"],
            )
        except Exception as exc:
            state["vault_busy"] = False
            selection_changed()
            core.messagebox.showerror(
                "Сховище документів", str(exc), parent=win
            )

    def browse_document_vault():
        try:
            open_document_vault(win, core, workspace_root)
        except Exception as exc:
            core.messagebox.showerror(
                "Сховище документів", str(exc), parent=win
            )

    def manage_paper_original():
        row = selected_row()
        if not row or not row.get("vault_id"):
            return
        currently_signed = bool(row.get("paper_original_signed"))
        if currently_signed:
            if not core.messagebox.askyesno(
                "Паперовий оригінал",
                "Прибрати позначку «Підписано»? Попередня позначка і дата залишаться в історії змін.",
                parent=win,
            ):
                return
            signed, signed_date = False, ""
        else:
            signed_date = core.simpledialog.askstring(
                "Підпис на папері",
                "Дата фактичного підписання (РРРР-ММ-ДД).\nЦе лише ваша позначка, не електронний підпис.",
                initialvalue=date.today().isoformat(),
                parent=win,
            )
            if signed_date is None:
                return
            if not core.messagebox.askyesno(
                "Підтвердити паперовий підпис",
                "Позначити, що паперовий оригінал підписано %s?\nСкан необов'язковий." % signed_date,
                parent=win,
            ):
                return
            signed = True
        try:
            set_paper_original_state(
                workspace_root, row["vault_id"], signed, signed_date,
            )
        except Exception as exc:
            core.messagebox.showerror("Паперовий оригінал", str(exc), parent=win)
            return
        refresh(reset=False, reload_sources=True)

    def manage_paper_scans():
        row = selected_row()
        if not row or not row.get("vault_id"):
            return
        try:
            open_paper_scans_dialog(
                win,
                core,
                workspace_root,
                row["vault_id"],
                row.get("title", ""),
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Скан-копії документа", str(exc), parent=win
            )

    def import_revision():
        row = selected_row()
        if not row or not row.get("prepared_snapshot_id"):
            return
        source = core.filedialog.askopenfilename(
            parent=win,
            title="Виберіть відредагований DOCX",
            filetypes=[("Word DOCX", "*.docx")],
        )
        if not source:
            return
        if not core.messagebox.askyesno(
            "Нова редакція DOCX",
            "Taxo збереже вибраний файл як нову редакцію. "
            "Попередній DOCX залишиться без змін.\n\nПродовжити?",
            parent=win,
        ):
            return
        try:
            result = import_prepared_document_revision(
                workspace_root,
                row["source_id"],
                Path(source),
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Нова редакція DOCX", str(exc), parent=win
            )
            return
        core.messagebox.showinfo(
            "Нова редакція DOCX",
            "Збережено редакцію r%d. Попередній файл не перезаписано."
            % result.revision,
            parent=win,
        )
        refresh(reset=True, reload_sources=True)

    core.ttk.Button(
        actions,
        text="Оновити",
        command=lambda: refresh(reload_sources=True),
    ).pack(side="left")
    clear_filters_button = core.ttk.Button(
        actions,
        text="Скинути фільтри",
        command=clear_filters,
    )
    clear_filters_button.pack(side="left", padx=(6, 0))
    core.ttk.Button(
        actions,
        text="Попередня",
        command=lambda: change_page(-1),
    ).pack(side="left", padx=4)
    core.ttk.Button(
        actions,
        text="Наступна",
        command=lambda: change_page(1),
    ).pack(side="left")
    core.ttk.Label(
        actions, textvariable=page_text
    ).pack(side="left", padx=8)
    edit_copy_button.pack(side="left", padx=(10, 4))
    import_revision_button.pack(side="left", padx=4)
    pdf_button.pack(side="left", padx=4)
    core.ttk.Button(
        actions,
        text="Відкрити вибране",
        command=open_selected,
    ).pack(side="right")

    vault_actions = core.ttk.Frame(body)
    vault_actions.grid(row=5, column=0, sticky="ew", pady=(8, 0))
    core.ttk.Label(
        vault_actions,
        text="Сховище: незмінна копія документа + його походження.",
        style="Muted.TLabel",
    ).pack(side="left")
    vault_open_button.configure(command=browse_document_vault)
    vault_open_button.pack(in_=vault_actions, side="right")
    paper_original_button.configure(command=manage_paper_original)
    paper_original_button.pack(in_=vault_actions, side="right", padx=(0, 6))
    paper_scans_button.configure(command=manage_paper_scans)
    paper_scans_button.pack(
        in_=vault_actions, side="right", padx=(0, 6)
    )
    vault_store_button.configure(command=store_selected_in_vault)
    vault_store_button.pack(
        in_=vault_actions, side="right", padx=(0, 6)
    )

    core.ttk.Label(
        body,
        text=(
            "Prepared Word: для редагування створіть окрему копію, "
            "а потім додайте її як нову редакцію. Старі файли не перезаписуються."
        ),
        style="Muted.TLabel",
    ).grid(row=6, column=0, sticky="w", pady=(6, 0))

    edit_copy_button.configure(command=copy_for_editing)
    import_revision_button.configure(command=import_revision)
    pdf_button.configure(command=create_pdf_for_print)
    new_folder_button.configure(command=create_user_folder)
    rename_folder_button.configure(command=rename_user_folder)
    move_folder_button.configure(command=move_user_folder)
    archive_folder_button.configure(command=archive_user_folder)
    restore_folder_button.configure(command=restore_user_folder)
    place_in_folder_button.configure(command=manage_document_folders)
    library_mode_box.bind("<<ComboboxSelected>>", change_library_mode)
    library_tree.bind("<<TreeviewSelect>>", select_library_node)
    tree.heading("date", text="Дата ▼", command=toggle_date_sort)
    tree.heading("number", text="№", command=toggle_number_sort)
    tree.heading("category", text="Категорія", command=toggle_category_sort)
    tree.bind("<Double-1>", open_selected)
    tree.bind(
        "<<TreeviewSelect>>", selection_changed, add="+"
    )
    search.trace_add("write", search_changed)
    source_box.bind(
        "<<ComboboxSelected>>",
        lambda _event: refresh(
            reset=True, reload_sources=True
        ),
    )
    scan_box.bind(
        "<<ComboboxSelected>>",
        lambda _event: refresh(reset=True),
    )
    kind_box.bind(
        "<<ComboboxSelected>>",
        lambda _event: refresh(reset=True),
    )
    category_box.bind(
        "<<ComboboxSelected>>",
        lambda _event: refresh(reset=True),
    )
    def select_year(_event=None):
        month_choice.set(all_months_label)
        refresh(reset=True)

    year_box.bind("<<ComboboxSelected>>", select_year)
    month_box.bind(
        "<<ComboboxSelected>>",
        lambda _event: refresh(reset=True),
    )
    employee_box.bind("<<ComboboxSelected>>", lambda _event: refresh(reset=True))
    vehicle_box.bind("<<ComboboxSelected>>", lambda _event: refresh(reset=True))
    date_from_entry.bind(
        "<Return>", lambda _event: refresh(reset=True)
    )
    date_to_entry.bind(
        "<Return>", lambda _event: refresh(reset=True)
    )
    win._taxo_library_tree = library_tree
    win._taxo_library_mode = library_mode
    win._taxo_catalog_tree = tree
    win._taxo_catalog_date_sort = toggle_date_sort
    win._taxo_catalog_number_sort = toggle_number_sort
    win._taxo_catalog_search = search
    win._taxo_catalog_source = source_choice
    win._taxo_catalog_source_box = source_box
    win._taxo_catalog_scan_filter = scan_choice
    win._taxo_catalog_scan_filter_box = scan_box
    win._taxo_catalog_kind_filter = kind_choice
    win._taxo_catalog_kind_filter_box = kind_box
    win._taxo_catalog_category_filter = category_choice
    win._taxo_catalog_category_filter_box = category_box
    win._taxo_catalog_year_filter = year_choice
    win._taxo_catalog_year_filter_box = year_box
    win._taxo_catalog_month_filter = month_choice
    win._taxo_catalog_month_filter_box = month_box
    win._taxo_catalog_employee_filter = employee_choice
    win._taxo_catalog_employee_filter_box = employee_box
    win._taxo_catalog_vehicle_filter = vehicle_choice
    win._taxo_catalog_vehicle_filter_box = vehicle_box
    win._taxo_catalog_date_from = date_from
    win._taxo_catalog_date_to = date_to
    win._taxo_catalog_date_from_entry = date_from_entry
    win._taxo_catalog_date_to_entry = date_to_entry
    win._taxo_catalog_apply_date = apply_date_button
    win._taxo_catalog_status = source_status
    win._taxo_catalog_refresh = refresh
    win._taxo_catalog_clear_filters = clear_filters
    win._taxo_catalog_clear_filters_button = clear_filters_button
    win._taxo_catalog_open = open_selected
    win._taxo_catalog_edit_copy = copy_for_editing
    win._taxo_catalog_import_revision = import_revision
    win._taxo_catalog_pdf_print = create_pdf_for_print
    win._taxo_catalog_vault_store = store_selected_in_vault
    win._taxo_catalog_vault_open = browse_document_vault
    win._taxo_catalog_paper_scans = manage_paper_scans
    win._taxo_catalog_paper_original = manage_paper_original
    win.bind("<Destroy>", cancel_pending, add="+")
    refresh(reload_sources=True)
    state["poll"] = win.after(100, poll_results)
    return win
