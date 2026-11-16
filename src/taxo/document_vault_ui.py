# -*- coding: utf-8 -*-
"""Read-only DocumentVault browser and explicit prepared-revision UI bridge.

The UI never infers a signature or business fact. Registration copies one exact
controlled PaperDocuments revision through document_vault_store; browsing only
reads and verifies the immutable vault.
"""
from __future__ import annotations

import queue
import threading
from pathlib import Path

from document_vault_store import (
    DocumentVaultRecord,
    list_document_vault,
    register_prepared_revision,
)

_READER_SLOT = threading.BoundedSemaphore(1)
_WRITER_SLOT = threading.BoundedSemaphore(1)
_STATUS_LABELS = {
    "ready": "Готовий документ",
    "archived": "Архівний документ",
}


def format_document_vault_details(record: DocumentVaultRecord) -> str:
    """Return complete read-only provenance text for one verified record."""

    status = _STATUS_LABELS.get(record.status, record.status)
    return "\n".join((
        "Назва: %s" % record.title,
        "Тип: %s" % record.kind,
        "Дата документа: %s" % (record.document_date or "не вказана"),
        "Стан: %s" % status,
        "Редакція документа: r%d" % record.document_revision,
        "ID DocumentVault: %s" % record.vault_id,
        "Створено запис: %s" % record.created_at,
        "",
        "Походження:",
        "  PaperDocuments ID: %s" % record.source_document_id,
        "  Prepared snapshot ID: %s" % record.prepared_snapshot_id,
        "  Сім'я документа: %s" % record.document_family_id,
        "  CompanyTemplate ID: %s" % record.company_template_id,
        "  Редакція шаблону: r%d" % record.template_revision,
        "  SHA-256 джерела шаблону: %s" % record.template_source_sha256,
        "",
        "Файл:",
        "  Початкова назва: %s" % record.original_name,
        "  Розмір: %d байт" % record.size_bytes,
        "  SHA-256 exact DOCX: %s" % record.content_sha256,
        "",
        "Цей запис не є автоматичним підтвердженням підпису або проведення документа.",
    ))


def start_prepared_revision_registration(
    workspace_root: Path,
    paper_document_id: str,
    result_queue,
):
    """Register one exact prepared revision outside the Tk thread.

    The result queue receives a success flag and either a verified record or an
    error message. Only one UI registration runs at a time.
    """

    if not isinstance(paper_document_id, str) or not paper_document_id:
        raise ValueError("Не вибрано контрольовану Word-редакцію")
    if not _WRITER_SLOT.acquire(blocking=False):
        raise RuntimeError(
            "Попереднє збереження у сховище документів ще триває"
        )

    def worker():
        try:
            record = register_prepared_revision(
                Path(workspace_root),
                paper_document_id,
                status="ready",
            )
            result_queue.put((True, record))
        except Exception as exc:
            result_queue.put((False, str(exc)))
        finally:
            _WRITER_SLOT.release()

    thread = threading.Thread(
        target=worker,
        name="Taxo-document-vault-register",
        daemon=True,
    )
    try:
        thread.start()
    except Exception:
        _WRITER_SLOT.release()
        raise
    return thread


def open_document_vault(parent, core, workspace_root):
    """Open a read-only list/detail view of verified DocumentVault records."""

    win = core.tk.Toplevel(parent)
    win.title("Taxo — Сховище документів")
    try:
        core.fit_window_to_screen(win, 1080, 720, 760, 500)
    except Exception:
        win.geometry("1080x720")

    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(3, weight=3)
    body.rowconfigure(5, weight=2)

    core.ttk.Label(
        body,
        text="Сховище готових та архівних документів",
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, sticky="w")
    core.ttk.Label(
        body,
        text=(
            "DocumentVault зберігає незмінні точні копії контрольованих DOCX. "
            "Стан «готовий» або «архівний» не означає автоматичний підпис."
        ),
        style="Muted.TLabel",
        wraplength=1010,
        justify="left",
    ).grid(row=1, column=0, sticky="ew", pady=(4, 4))

    status = core.tk.StringVar(value="Читаю DocumentVault…")
    core.ttk.Label(
        body,
        textvariable=status,
        wraplength=1010,
        justify="left",
    ).grid(row=2, column=0, sticky="ew", pady=(0, 6))

    frame = core.ttk.Frame(body)
    frame.grid(row=3, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    columns = ("created", "date", "kind", "title", "revision", "status")
    tree = core.ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )
    for key, label, width, stretch in (
        ("created", "Додано", 160, False),
        ("date", "Дата документа", 110, False),
        ("kind", "Тип", 150, False),
        ("title", "Назва", 350, True),
        ("revision", "Ред.", 65, False),
        ("status", "Стан", 150, False),
    ):
        tree.heading(key, text=label)
        tree.column(
            key,
            width=width,
            minwidth=60,
            stretch=stretch,
        )
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

    core.ttk.Label(
        body, text="Походження та цілісність", style="Muted.TLabel"
    ).grid(row=4, column=0, sticky="w", pady=(8, 3))
    detail_frame = core.ttk.Frame(body)
    detail_frame.grid(row=5, column=0, sticky="nsew")
    detail_frame.rowconfigure(0, weight=1)
    detail_frame.columnconfigure(0, weight=1)
    details = core.tk.Text(
        detail_frame,
        wrap="word",
        height=10,
        state="disabled",
    )
    detail_bar = core.ttk.Scrollbar(
        detail_frame,
        orient="vertical",
        command=details.yview,
    )
    details.configure(yscrollcommand=detail_bar.set)
    details.grid(row=0, column=0, sticky="nsew")
    detail_bar.grid(row=0, column=1, sticky="ns")

    actions = core.ttk.Frame(body)
    actions.grid(row=6, column=0, sticky="ew", pady=(8, 0))
    actions.columnconfigure(0, weight=1)
    refresh_button = core.ttk.Button(actions, text="Оновити")
    refresh_button.grid(row=0, column=1, padx=(4, 8))
    core.ttk.Button(
        actions, text="Закрити", command=win.destroy
    ).grid(row=0, column=2)

    results = queue.Queue()
    state = {
        "closed": False,
        "busy": False,
        "generation": 0,
        "rows": {},
        "after": None,
    }
    win._taxo_document_vault_state = state

    def set_details(text):
        details.configure(state="normal")
        details.delete("1.0", "end")
        if text:
            details.insert("1.0", text)
        details.configure(state="disabled")

    def selection_changed(_event=None):
        selected = tree.selection()
        record = state["rows"].get(selected[0]) if selected else None
        set_details(
            format_document_vault_details(record) if record else ""
        )

    def render(records):
        previous = tree.selection()
        previous_id = previous[0] if previous else ""
        state["rows"] = {item.vault_id: item for item in records}
        tree.delete(*tree.get_children())
        for item in records:
            tree.insert(
                "",
                "end",
                iid=item.vault_id,
                values=(
                    item.created_at.replace("T", " "),
                    item.document_date,
                    item.kind,
                    item.title,
                    "r%d" % item.document_revision,
                    _STATUS_LABELS.get(item.status, item.status),
                ),
            )
        if previous_id and tree.exists(previous_id):
            tree.selection_set(previous_id)
            tree.focus(previous_id)
            tree.see(previous_id)
        elif records:
            tree.selection_set(records[0].vault_id)
            tree.focus(records[0].vault_id)
        status.set("Документів у сховищі: %d." % len(records))
        selection_changed()

    def poll():
        if state["closed"]:
            return
        try:
            while True:
                generation, ok, payload = results.get_nowait()
                if generation != state["generation"]:
                    continue
                state["busy"] = False
                refresh_button.configure(state="normal")
                if ok:
                    render(payload)
                else:
                    status.set(
                        "Не вдалося прочитати DocumentVault: " + str(payload)
                    )
                    set_details("")
                    core.messagebox.showerror(
                        "Сховище документів",
                        str(payload),
                        parent=win,
                    )
        except queue.Empty:
            pass
        if not state["closed"]:
            state["after"] = win.after(120, poll)

    def refresh():
        if state["closed"] or state["busy"]:
            return
        if not _READER_SLOT.acquire(blocking=False):
            status.set("Попереднє читання DocumentVault ще триває.")
            return
        state["busy"] = True
        state["generation"] += 1
        generation = state["generation"]
        refresh_button.configure(state="disabled")
        status.set("Перевіряю DocumentVault…")

        def worker():
            try:
                payload = list_document_vault(Path(workspace_root))
                results.put((generation, True, payload))
            except Exception as exc:
                results.put((generation, False, str(exc)))
            finally:
                _READER_SLOT.release()

        try:
            threading.Thread(
                target=worker,
                name="Taxo-document-vault-list",
                daemon=True,
            ).start()
        except Exception:
            state["busy"] = False
            _READER_SLOT.release()
            refresh_button.configure(state="normal")
            raise

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

    tree.bind(
        "<<TreeviewSelect>>", selection_changed, add="+"
    )
    refresh_button.configure(command=refresh)
    win._taxo_document_vault_tree = tree
    win._taxo_document_vault_details = details
    win._taxo_document_vault_refresh = refresh
    win.bind("<Destroy>", close_state, add="+")
    state["after"] = win.after(120, poll)
    refresh()
    return win
