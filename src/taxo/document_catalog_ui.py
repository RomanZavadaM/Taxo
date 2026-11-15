# -*- coding: utf-8 -*-
"""One browser for orders and prepared paper documents with safe DOCX history."""
from __future__ import annotations

import queue
import threading
from pathlib import Path

import document_catalog
import paper_documents as paperwork
from prepared_document_revision import (
    copy_prepared_document_for_editing,
    import_prepared_document_revision,
)


_READER_SLOT = threading.BoundedSemaphore(1)


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
    frame.columnconfigure(0, weight=1)
    cols = ("date", "number", "kind", "title", "person", "revision", "file")
    tree = core.ttk.Treeview(
        frame, columns=cols, show="headings", selectmode="browse"
    )
    for key, label, width in (
        ("date", "Дата", 100),
        ("number", "№", 80),
        ("kind", "Документ", 125),
        ("title", "Тема / назва", 300),
        ("person", "Працівники", 165),
        ("revision", "Ред.", 65),
        ("file", "Стан файла", 145),
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
    tree.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")

    actions = core.ttk.Frame(body)
    actions.grid(row=4, column=0, sticky="ew", pady=(4, 0))
    page_text = core.tk.StringVar(value="")
    state = {
        "page": 0,
        "pages": 1,
        "rows": {},
        "after": None,
        "poll": None,
        "retry": None,
        "snapshot": None,
        "generation": 0,
        "busy": False,
        "wanted": None,
        "needs_reload": False,
        "results": queue.Queue(),
    }

    edit_copy_button = core.ttk.Button(
        actions, text="Копія для редагування…", state="disabled"
    )
    import_revision_button = core.ttk.Button(
        actions, text="Додати редакцію DOCX…", state="disabled"
    )

    def selected_row():
        selected = tree.selection()
        if not selected:
            return None
        return state["rows"].get(selected[0])

    def selection_changed(_event=None):
        row = selected_row()
        prepared = bool(
            row
            and row.get("source") == "paper"
            and row.get("prepared_snapshot_id")
            and row.get("file_path") is not None
        )
        value = "normal" if prepared else "disabled"
        edit_copy_button.configure(state=value)
        import_revision_button.configure(state=value)

    def render(result):
        state["page"], state["pages"] = result["page"], result["pages"]
        source_status.set(
            result["order_status"] + " " + result["paper_status"]
        )
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
                    row["kind"],
                    row["title"],
                    row["person"],
                    row.get("revision_label", ""),
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
        text_filter, page, reload_sources, source_filter = wanted
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
                render(result)
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
        if state["after"] is not None:
            win.after_cancel(state["after"])

        def later():
            state["after"] = None
            refresh(reset=True, reload_sources=True)

        state["after"] = win.after(250, later)

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
    core.ttk.Button(
        actions,
        text="Відкрити вибране",
        command=open_selected,
    ).pack(side="right")

    core.ttk.Label(
        body,
        text=(
            "Prepared Word: для редагування створіть окрему копію, "
            "а потім додайте її як нову редакцію. Старі файли не перезаписуються."
        ),
        style="Muted.TLabel",
    ).grid(row=5, column=0, sticky="w", pady=(6, 0))

    edit_copy_button.configure(command=copy_for_editing)
    import_revision_button.configure(command=import_revision)
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
    win._taxo_catalog_tree = tree
    win._taxo_catalog_search = search
    win._taxo_catalog_source = source_choice
    win._taxo_catalog_source_box = source_box
    win._taxo_catalog_status = source_status
    win._taxo_catalog_refresh = refresh
    win._taxo_catalog_open = open_selected
    win._taxo_catalog_edit_copy = copy_for_editing
    win._taxo_catalog_import_revision = import_revision
    win.bind("<Destroy>", cancel_pending, add="+")
    refresh(reload_sources=True)
    state["poll"] = win.after(100, poll_results)
    return win
