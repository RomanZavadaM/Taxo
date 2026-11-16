# -*- coding: utf-8 -*-
"""User-facing read-only paper-scan list and explicit add action."""
from __future__ import annotations

import queue
import threading
from pathlib import Path

from document_vault_paper_scans import (
    list_paper_scans,
    load_paper_scan,
    register_paper_scan,
)
from document_viewer import open_document


_IO_SLOT = threading.BoundedSemaphore(1)

_MEDIA_LABELS = {
    "application/pdf": "PDF",
    "image/jpeg": "JPG",
    "image/png": "PNG",
    "image/tiff": "TIFF",
}


def _size_label(size_bytes):
    size = int(size_bytes or 0)
    if size >= 1024 * 1024:
        return "%.1f MB" % (size / (1024.0 * 1024.0))
    if size >= 1024:
        return "%.1f KB" % (size / 1024.0)
    return "%d B" % size


def open_paper_scans_dialog(
    parent,
    core,
    workspace_root,
    vault_id,
    document_title="",
):
    """Show attached paper scans and allow one explicit background import."""

    if not isinstance(vault_id, str) or not vault_id:
        raise ValueError("Документ ще не збережено у сховищі")

    win = core.tk.Toplevel(parent)
    win.title("Taxo — Скан-копії паперового оригіналу")
    try:
        core.fit_window_to_screen(win, 920, 600, 700, 440)
    except Exception:
        win.geometry("920x600")

    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(3, weight=1)

    core.ttk.Label(
        body,
        text="Скан-копії паперового оригіналу",
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, sticky="w")

    subtitle = (
        "Документ: %s" % document_title
        if document_title
        else "Вибраний документ зі сховища"
    )
    core.ttk.Label(
        body,
        text=subtitle,
        style="Muted.TLabel",
        wraplength=880,
        justify="left",
    ).grid(row=1, column=0, sticky="ew", pady=(4, 2))

    status = core.tk.StringVar(value="Читаю прикріплені скани…")
    core.ttk.Label(
        body,
        textvariable=status,
        wraplength=880,
        justify="left",
    ).grid(row=2, column=0, sticky="ew", pady=(0, 6))

    frame = core.ttk.Frame(body)
    frame.grid(row=3, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    columns = ("created", "name", "type", "size", "sha")
    tree = core.ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )
    for key, label, width, stretch in (
        ("created", "Додано", 160, False),
        ("name", "Файл", 300, True),
        ("type", "Тип", 75, False),
        ("size", "Розмір", 90, False),
        ("sha", "SHA-256", 180, True),
    ):
        tree.heading(key, text=label)
        tree.column(key, width=width, minwidth=60, stretch=stretch)

    ybar = core.ttk.Scrollbar(
        frame, orient="vertical", command=tree.yview
    )
    xbar = core.ttk.Scrollbar(
        frame, orient="horizontal", command=tree.xview
    )
    tree.configure(
        yscrollcommand=ybar.set,
        xscrollcommand=xbar.set,
    )
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

    details = core.tk.StringVar(value="")
    core.ttk.Label(
        body,
        textvariable=details,
        style="Muted.TLabel",
        wraplength=880,
        justify="left",
    ).grid(row=4, column=0, sticky="ew", pady=(8, 0))

    actions = core.ttk.Frame(body)
    actions.grid(row=5, column=0, sticky="ew", pady=(10, 0))
    actions.columnconfigure(0, weight=1)

    open_button = core.ttk.Button(
        actions, text="Відкрити", state="disabled"
    )
    add_button = core.ttk.Button(actions, text="Додати скан…")
    refresh_button = core.ttk.Button(actions, text="Оновити")
    open_button.grid(row=0, column=1, padx=(4, 6))
    refresh_button.grid(row=0, column=2, padx=(0, 6))
    add_button.grid(row=0, column=3, padx=(0, 6))
    core.ttk.Button(
        actions, text="Закрити", command=win.destroy
    ).grid(row=0, column=4)

    core.ttk.Label(
        body,
        text=(
            "Скан є лише копією паперового оригіналу. "
            "Його наявність не означає, що документ підписано."
        ),
        style="Muted.TLabel",
        wraplength=880,
        justify="left",
    ).grid(row=6, column=0, sticky="ew", pady=(8, 0))

    results = queue.Queue()
    state = {
        "closed": False,
        "busy": False,
        "generation": 0,
        "rows": {},
        "after": None,
    }
    win._taxo_paper_scans_state = state

    def set_busy(value):
        state["busy"] = bool(value)
        button_state = "disabled" if value else "normal"
        add_button.configure(state=button_state)
        refresh_button.configure(state=button_state)
        open_button.configure(
            state=(
                "disabled"
                if value or not tree.selection()
                else "normal"
            )
        )

    def selection_changed(_event=None):
        selected = tree.selection()
        record = state["rows"].get(selected[0]) if selected else None
        if record is None:
            details.set("")
            open_button.configure(state="disabled")
            return
        details.set(
            "ID: %s · SHA-256: %s"
            % (record.attachment_id, record.sha256)
        )
        open_button.configure(
            state="disabled" if state["busy"] else "normal"
        )

    def render(records, message=""):
        previous = tree.selection()
        previous_id = previous[0] if previous else ""
        state["rows"] = {
            item.attachment_id: item for item in records
        }
        tree.delete(*tree.get_children())
        for item in records:
            tree.insert(
                "",
                "end",
                iid=item.attachment_id,
                values=(
                    item.created_at.replace("T", " "),
                    item.original_name,
                    _MEDIA_LABELS.get(item.media_type, item.media_type),
                    _size_label(item.size_bytes),
                    item.sha256[:16] + "…",
                ),
            )
        if previous_id and tree.exists(previous_id):
            tree.selection_set(previous_id)
            tree.focus(previous_id)
            tree.see(previous_id)
        elif records:
            tree.selection_set(records[0].attachment_id)
            tree.focus(records[0].attachment_id)
        if message:
            status.set(message)
        elif records:
            status.set("Прикріплених сканів: %d." % len(records))
        else:
            status.set("Прикріплених сканів ще немає.")
        selection_changed()

    def start_background(kind, worker):
        if state["closed"] or state["busy"]:
            return
        if not _IO_SLOT.acquire(blocking=False):
            status.set("Попередня операція зі сканами ще триває.")
            return
        state["generation"] += 1
        generation = state["generation"]
        set_busy(True)

        def run():
            try:
                payload = worker()
                results.put((generation, kind, True, payload))
            except Exception as exc:
                results.put((generation, kind, False, str(exc)))
            finally:
                _IO_SLOT.release()

        try:
            threading.Thread(
                target=run,
                name="Taxo-paper-scan-%s" % kind,
                daemon=True,
            ).start()
        except Exception:
            _IO_SLOT.release()
            set_busy(False)
            raise

    def refresh():
        status.set("Перевіряю прикріплені скани…")
        start_background(
            "refresh",
            lambda: list_paper_scans(Path(workspace_root), vault_id),
        )

    def open_scan():
        if state["busy"]:
            return
        selected = tree.selection()
        record = state["rows"].get(selected[0]) if selected else None
        if record is None:
            return
        status.set("Перевіряю скан перед відкриттям…")
        start_background(
            "open",
            lambda: load_paper_scan(
                Path(workspace_root),
                record.attachment_id,
            ),
        )

    def add_scan():
        if state["busy"]:
            return
        source = core.filedialog.askopenfilename(
            parent=win,
            title="Виберіть скан паперового оригіналу",
            filetypes=[
                ("Підтримувані скани", "*.pdf *.jpg *.jpeg *.png *.tif *.tiff"),
                ("PDF", "*.pdf"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("TIFF", "*.tif *.tiff"),
            ],
        )
        if not source:
            return
        if not core.messagebox.askyesno(
            "Додати скан",
            (
                "Taxo збереже окрему незмінну копію вибраного файла "
                "біля цього документа.\n\n"
                "Це не означає, що документ підписано. Продовжити?"
            ),
            parent=win,
        ):
            return

        source_path = Path(source)
        status.set("Копіюю скан у сховище…")

        def worker():
            record = register_paper_scan(
                Path(workspace_root),
                vault_id,
                source_path,
            )
            records = list_paper_scans(
                Path(workspace_root),
                vault_id,
            )
            return record, records

        start_background("add", worker)

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                generation, kind, ok, payload = results.get_nowait()
                if generation != state["generation"]:
                    continue
                set_busy(False)
                if ok:
                    if kind == "add":
                        record, records = payload
                        render(
                            records,
                            "Скан додано: %s."
                            % record.original_name,
                        )
                    elif kind == "open":
                        status.set(
                            "Скан перевірено: %s."
                            % payload.record.original_name
                        )
                        try:
                            open_document(win, payload.path)
                        except Exception as exc:
                            status.set(
                                "Не вдалося відкрити скан: " + str(exc)
                            )
                            core.messagebox.showerror(
                                "Відкрити скан",
                                str(exc),
                                parent=win,
                            )
                    else:
                        render(payload)
                else:
                    status.set("Помилка роботи зі сканом: " + str(payload))
                    core.messagebox.showerror(
                        "Скан-копії документа",
                        str(payload),
                        parent=win,
                    )
        except queue.Empty:
            pass
        if not state["closed"]:
            state["after"] = win.after(120, poll)

    def close_state(event):
        if event.widget is not win:
            return
        state["closed"] = True
        state["generation"] += 1
        if state["after"] is not None:
            try:
                win.after_cancel(state["after"])
            except Exception:
                pass
            state["after"] = None

    tree.bind("<<TreeviewSelect>>", selection_changed, add="+")
    open_button.configure(command=open_scan)
    add_button.configure(command=add_scan)
    refresh_button.configure(command=refresh)
    win._taxo_paper_scans_tree = tree
    win._taxo_paper_scans_open = open_scan
    win._taxo_paper_scans_add = add_scan
    win._taxo_paper_scans_refresh = refresh
    win.bind("<Destroy>", close_state, add="+")
    state["after"] = win.after(120, poll)
    refresh()
    return win
