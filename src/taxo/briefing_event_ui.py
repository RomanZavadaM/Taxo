# -*- coding: utf-8 -*-
"""10.25-r4 event briefings and explicit conducted-fact UI.

Paper-first rule: creating/preparing an event never means it was conducted.
A conducted fact is written only through the dedicated explicit action with a
factual date and a mandatory note referring to the paper record.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import briefing_planner as planner
import briefing_planning_ui as planning_ui
import briefing_prepared_output as prepared_output
import entity_choices
from workspace import load_workspace_root


def _ui_to_iso(value, label):
    clean = str(value or "").strip()
    try:
        return datetime.strptime(clean, "%d.%m.%Y").date().isoformat()
    except ValueError as exc:
        raise ValueError("%s має бути у форматі ДД.ММ.РРРР" % label) from exc


def create_event(
    workspace_root,
    *,
    program_id,
    program_revision,
    scheduled_for,
    reason,
    participants,
):
    """Create one event session; it never changes regular planned sessions."""
    return planner.create_event_session(
        workspace_root,
        program_id=program_id,
        program_revision=program_revision,
        scheduled_for=scheduled_for,
        reason=reason,
        participants=participants,
    )


def record_conducted(
    workspace_root,
    session_id,
    *,
    conducted_on,
    evidence_note,
):
    """Record the factual paper-confirmed conducted state explicitly."""
    return planner.mark_conducted(
        workspace_root,
        session_id,
        conducted_on=conducted_on,
        evidence_note=evidence_note,
    )


def session_audit(workspace_root, session_id):
    session = planner.get_session(workspace_root, session_id)
    program = planner.program_for_session(workspace_root, session)
    link = prepared_output.get_link(workspace_root, session.session_id)
    return {
        "session": session,
        "program": program,
        "prepared_output": link,
    }


def _program_rows(workspace_root):
    return planning_ui._latest_programs(workspace_root)


def _program_caption(row):
    return planning_ui._program_caption(row)


def open_event_dialog(
    parent,
    core,
    workspace_root=None,
    *,
    on_saved=None,
):
    workspace_root = Path(workspace_root or load_workspace_root())
    win = core.tk.Toplevel(parent)
    win.title("Інструктаж — За подією")
    try:
        core.fit_window_to_screen(win, 980, 680, 740, 500)
        core.configure_toplevel(
            win, title=win.title(), minsize=(740, 500)
        )
    except Exception:
        pass

    body = core.ttk.Frame(win, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(3, weight=1)

    core.ttk.Label(
        body,
        text="За подією",
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, sticky="w")
    core.ttk.Label(
        body,
        text=(
            "Цей запис не закриває регулярний плановий інструктаж. "
            "Підстава обов'язкова. Створення або DOCX не означають, "
            "що інструктаж фактично проведено чи підписано."
        ),
        style="Muted.TLabel",
        wraplength=900,
        justify="left",
    ).grid(row=1, column=0, sticky="ew", pady=(2, 7))

    top = core.ttk.Frame(body)
    top.grid(row=2, column=0, sticky="ew", pady=(0, 7))
    top.columnconfigure(1, weight=1)
    program_var = core.tk.StringVar(value="")
    day_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
    reason_var = core.tk.StringVar(value="")
    search_var = core.tk.StringVar(value="")

    core.ttk.Label(top, text="Програма").grid(
        row=0, column=0, sticky="w", padx=(0, 6), pady=3
    )
    program_box = core.ttk.Combobox(
        top, textvariable=program_var, state="readonly"
    )
    program_box.grid(row=0, column=1, columnspan=3, sticky="ew", pady=3)
    core.ttk.Label(top, text="Дата").grid(
        row=1, column=0, sticky="w", padx=(0, 6), pady=3
    )
    core.ttk.Entry(
        top, textvariable=day_var, width=14
    ).grid(row=1, column=1, sticky="w", pady=3)
    core.ttk.Label(top, text="Підстава події").grid(
        row=2, column=0, sticky="w", padx=(0, 6), pady=3
    )
    core.ttk.Entry(
        top, textvariable=reason_var
    ).grid(row=2, column=1, columnspan=3, sticky="ew", pady=3)
    core.ttk.Label(
        top, text="Конкретний випадок / що додатково розглянути"
    ).grid(row=3, column=0, sticky="nw", padx=(0, 6), pady=3)
    details_text = core.tk.Text(top, height=4, wrap="word")
    details_text.grid(
        row=3, column=1, columnspan=3, sticky="ew", pady=3
    )
    core.ttk.Label(
        top,
        text=(
            "Основа береться з вибраної програми. Тут достатньо дописати "
            "конкретну проблему, обставини та питання саме цього випадку."
        ),
        style="Muted.TLabel",
        wraplength=760,
        justify="left",
    ).grid(row=4, column=1, columnspan=3, sticky="ew", pady=(0, 3))
    core.ttk.Label(top, text="Пошук працівників").grid(
        row=5, column=0, sticky="w", padx=(0, 6), pady=3
    )
    search_entry = core.ttk.Entry(top, textvariable=search_var)
    search_entry.grid(row=5, column=1, columnspan=3, sticky="ew", pady=3)

    people_frame = core.ttk.LabelFrame(
        body,
        text="Працівники — вибір накопичується під час пошуку",
        padding=7,
    )
    people_frame.grid(row=3, column=0, sticky="nsew")
    people_frame.columnconfigure(0, weight=1)
    people_frame.columnconfigure(2, weight=1)
    people_frame.rowconfigure(1, weight=1)
    core.ttk.Label(
        people_frame, text="Знайдені"
    ).grid(row=0, column=0, sticky="w")
    core.ttk.Label(
        people_frame, text="Вибрані"
    ).grid(row=0, column=2, sticky="w")

    available = core.tk.Listbox(
        people_frame, selectmode="extended", exportselection=False
    )
    available.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
    selected = core.tk.Listbox(
        people_frame, selectmode="extended", exportselection=False
    )
    selected.grid(row=1, column=2, sticky="nsew", pady=(4, 0))
    middle = core.ttk.Frame(people_frame)
    middle.grid(row=1, column=1, padx=7)
    add_button = core.ttk.Button(middle, text="Додати →")
    add_button.pack(pady=(15, 5))
    remove_button = core.ttk.Button(middle, text="← Прибрати")
    remove_button.pack()

    footer = core.ttk.Frame(body)
    footer.grid(row=4, column=0, sticky="ew", pady=(8, 0))
    count_var = core.tk.StringVar(value="Вибрано: 0")
    core.ttk.Label(
        footer, textvariable=count_var, style="Muted.TLabel"
    ).pack(side="left")
    core.ttk.Button(
        footer, text="Скасувати", command=win.destroy
    ).pack(side="right")
    prepare_button = core.ttk.Button(
        footer, text="Створити + DOCX"
    )
    prepare_button.pack(side="right", padx=(0, 6))
    create_button = core.ttk.Button(
        footer, text="Створити захід", style="Accent.TButton"
    )
    create_button.pack(side="right", padx=(0, 6))

    programs = list(_program_rows(workspace_root))
    program_map = {_program_caption(row): row for row in programs}
    captions = list(program_map)
    program_box.configure(values=captions)
    if captions:
        program_var.set(captions[0])

    try:
        con = core.db()
        try:
            employee_rows = entity_choices.list_employee_choices(
                con, active_only=True
            )
        finally:
            con.close()
    except Exception:
        employee_rows = []
    model = planning_ui.EmployeeSelectionModel(employee_rows)
    visible_rows = []
    selected_rows = []

    def refresh_available(*_args):
        visible_rows[:] = list(model.search(search_var.get()))
        available.delete(0, "end")
        selected_ids = set(model.selected_ids())
        for row in visible_rows:
            mark = "  ✓" if int(row["id"]) in selected_ids else ""
            available.insert("end", str(row["label"]) + mark)

    def refresh_selected():
        selected_rows[:] = list(model.selected_rows())
        selected.delete(0, "end")
        for row in selected_rows:
            selected.insert("end", str(row["label"]))
        count_var.set("Вибрано: %d" % len(selected_rows))
        refresh_available()

    def add_people():
        ids = [
            visible_rows[int(index)]["id"]
            for index in available.curselection()
            if 0 <= int(index) < len(visible_rows)
        ]
        model.add_ids(ids)
        refresh_selected()

    def remove_people():
        ids = [
            selected_rows[int(index)]["id"]
            for index in selected.curselection()
            if 0 <= int(index) < len(selected_rows)
        ]
        model.remove_ids(ids)
        refresh_selected()

    def save(prepare_docx=False):
        program = program_map.get(program_var.get())
        people = model.selected_rows()
        if program is None:
            core.messagebox.showerror(
                "За подією", "Виберіть програму.", parent=win
            )
            return None
        if not people:
            core.messagebox.showerror(
                "За подією",
                "Виберіть хоча б одного працівника.",
                parent=win,
            )
            return None
        try:
            base_reason = reason_var.get().strip()
            if not base_reason:
                raise ValueError("Вкажіть підставу події")
            details = details_text.get("1.0", "end-1c").strip()
            reason = base_reason
            if details:
                reason += "\n\nКонкретний випадок / додатково розглянути:\n" + details
            scheduled_for = _ui_to_iso(day_var.get(), "Дата події")
            session = create_event(
                workspace_root,
                program_id=program.program_id,
                program_revision=program.revision,
                scheduled_for=scheduled_for,
                reason=reason,
                participants=people,
            )
        except Exception as exc:
            core.messagebox.showerror(
                "За подією", str(exc), parent=win
            )
            return None

        path = None
        if prepare_docx:
            try:
                session, _link, path = prepared_output.prepare_session_document(
                    workspace_root, session.session_id
                )
            except Exception as exc:
                core.messagebox.showwarning(
                    "Захід створено",
                    (
                        "Подієвий запис збережено, але DOCX не вдалося "
                        "підготувати. Запис не втрачено.\n\n%s" % exc
                    ),
                    parent=win,
                )
        if callable(on_saved):
            on_saved(session)
        core.messagebox.showinfo(
            "За подією",
            (
                "Подієвий захід збережено%s. Це не означає, що він "
                "проведений або підписаний."
                % (" і DOCX підготовлено" if path else "")
            ),
            parent=win,
        )
        win.destroy()
        return session

    add_button.configure(command=add_people)
    remove_button.configure(command=remove_people)
    create_button.configure(command=lambda: save(False))
    prepare_button.configure(command=lambda: save(True))
    search_var.trace_add("write", refresh_available)
    refresh_selected()

    win._taxo_event_program_combo = program_box
    win._taxo_event_reason_var = reason_var
    win._taxo_event_details_text = details_text
    win._taxo_event_day_var = day_var
    win._taxo_event_search_entry = search_entry
    win._taxo_event_available_people = available
    win._taxo_event_selected_people = selected
    win._taxo_event_add_people_button = add_button
    win._taxo_event_remove_people_button = remove_button
    win._taxo_event_create_button = create_button
    win._taxo_event_prepare_button = prepare_button
    win._taxo_event_selection_model = model
    return win


def open_conducted_dialog(
    parent,
    core,
    workspace_root,
    session_id,
    *,
    on_saved=None,
):
    workspace_root = Path(workspace_root)
    session = planner.get_session(workspace_root, session_id)
    if session.status == planner.STATUS_CONDUCTED:
        raise ValueError("Факт проведення цього інструктажу вже зафіксовано")

    win = core.tk.Toplevel(parent)
    win.title("Зафіксувати проведення")
    try:
        core.fit_window_to_screen(win, 720, 440, 620, 360)
        core.configure_toplevel(
            win, title=win.title(), minsize=(620, 360)
        )
    except Exception:
        pass

    body = core.ttk.Frame(win, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(3, weight=1)

    program = planner.program_for_session(workspace_root, session)
    core.ttk.Label(
        body,
        text="%s — %s" % (program.title, program.kind),
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, columnspan=2, sticky="w")
    core.ttk.Label(
        body,
        text=(
            "Ця дія фіксує лише фактичний запис із паперового журналу. "
            "Вона не створює підпис і не змінює інші планові/подієві заходи."
        ),
        style="Muted.TLabel",
        wraplength=680,
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(3, 8))

    day_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
    core.ttk.Label(body, text="Фактична дата").grid(
        row=2, column=0, sticky="w", padx=(0, 8)
    )
    core.ttk.Entry(body, textvariable=day_var).grid(
        row=2, column=1, sticky="ew"
    )
    core.ttk.Label(
        body,
        text="Паперовий запис / журнал / сторінка",
    ).grid(row=3, column=0, sticky="nw", padx=(0, 8), pady=(8, 0))
    evidence = core.tk.Text(body, wrap="word", height=8)
    evidence.grid(row=3, column=1, sticky="nsew", pady=(8, 0))

    actions = core.ttk.Frame(body)
    actions.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
    core.ttk.Button(
        actions, text="Скасувати", command=win.destroy
    ).pack(side="right")

    def save():
        try:
            row = record_conducted(
                workspace_root,
                session.session_id,
                conducted_on=_ui_to_iso(
                    day_var.get(), "Фактична дата"
                ),
                evidence_note=evidence.get("1.0", "end-1c"),
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Факт проведення", str(exc), parent=win
            )
            return None
        if callable(on_saved):
            on_saved(row)
        core.messagebox.showinfo(
            "Факт проведення",
            "Фактичний запис збережено. Історичні дані не переписуються.",
            parent=win,
        )
        win.destroy()
        return row

    save_button = core.ttk.Button(
        actions,
        text="Зафіксувати проведення",
        style="Accent.TButton",
        command=save,
    )
    save_button.pack(side="right", padx=(0, 6))

    win._taxo_conducted_day_var = day_var
    win._taxo_conducted_evidence = evidence
    win._taxo_conducted_save_button = save_button
    return win


def open_session_history(parent, core, workspace_root, session_id):
    data = session_audit(workspace_root, session_id)
    session = data["session"]
    program = data["program"]
    link = data["prepared_output"]

    win = core.tk.Toplevel(parent)
    win.title("Історія інструктажу")
    try:
        core.fit_window_to_screen(win, 820, 620, 650, 440)
        core.configure_toplevel(
            win, title=win.title(), minsize=(650, 440)
        )
    except Exception:
        pass

    body = core.ttk.Frame(win, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(1, weight=1)

    core.ttk.Label(
        body,
        text="%s — редакція r%d" % (
            program.title, program.revision
        ),
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, sticky="w")

    mode = "За подією" if session.mode == planner.MODE_EVENT else "Плановий"
    people = "\n".join(
        "- %s%s%s" % (
            person.name,
            (" · таб. № " + person.personnel_no)
            if person.personnel_no else "",
            (" · " + person.position) if person.position else "",
        )
        for person in session.participants
    )
    payload = (
        "Режим: %s\n"
        "Дата: %s\n"
        "Стан: %s\n"
        "Напрям / вид: %s / %s\n"
        "Підстава події: %s\n"
        "Створено: %s\n"
        "Оновлено: %s\n"
        "Підготовлено: %s\n"
        "Фактично проведено: %s\n"
        "Паперовий запис: %s\n"
        "DOCX: %s\n"
        "SHA-256: %s\n\n"
        "Працівники:\n%s"
        % (
            mode,
            session.scheduled_for,
            session.status,
            program.direction,
            program.kind,
            session.reason or "—",
            session.created_at,
            session.updated_at,
            session.prepared_at or "—",
            session.conducted_on or "—",
            session.evidence_note or "—",
            link.filename if link else "—",
            link.content_sha256 if link else "—",
            people or "—",
        )
    )
    text = core.tk.Text(body, wrap="word")
    text.grid(row=1, column=0, sticky="nsew", pady=(7, 0))
    text.insert("1.0", payload)
    text.configure(state="disabled")
    core.ttk.Button(
        body, text="Закрити", command=win.destroy
    ).grid(row=2, column=0, sticky="e", pady=(8, 0))

    win._taxo_session_history_text = text
    return win
