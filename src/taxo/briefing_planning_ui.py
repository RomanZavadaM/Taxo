# -*- coding: utf-8 -*-
"""UI for 10.25-r3 program revisions and planned briefing preparation."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import briefing_planner as planner
import briefing_prepared_output as prepared_output
import briefing_program_sources as program_sources
from briefing_preparation import BRIEFING_KINDS
import entity_choices
import safety_instruction_document_service as instruction_documents
from workspace import load_workspace_root


def _ui_to_iso(value, label, allow_empty=False):
    clean = str(value or "").strip()
    if allow_empty and not clean:
        return ""
    try:
        return datetime.strptime(clean, "%d.%m.%Y").date().isoformat()
    except ValueError as exc:
        raise ValueError("%s має бути у форматі ДД.ММ.РРРР" % label) from exc


def _iso_to_ui(value):
    clean = str(value or "").strip()
    if not clean:
        return ""
    return date.fromisoformat(clean).strftime("%d.%m.%Y")


def _default_approved_by(core):
    """Suggest the configured company signer without asserting approval."""
    try:
        con = core.db()
        try:
            row = con.execute(
                "SELECT signer_position, signer_name FROM company WHERE id=1"
            ).fetchone()
        finally:
            con.close()
    except Exception:
        return ""
    if not row:
        return ""
    position = str(row[0] or "").strip()
    name = str(row[1] or "").strip()
    return " ".join(part for part in (position, name) if part)


class EmployeeSelectionModel:
    """Search never clears accumulated identity-based selection."""

    def __init__(self, rows):
        normalized = []
        by_id = {}
        for row in rows or ():
            if not isinstance(row, dict):
                continue
            try:
                employee_id = int(row.get("id"))
            except (TypeError, ValueError):
                continue
            if employee_id in by_id:
                continue
            copy = dict(row)
            copy["id"] = employee_id
            copy.setdefault("label", copy.get("name") or ("Працівник #%d" % employee_id))
            copy.setdefault(
                "search_text",
                " ".join(
                    str(copy.get(key) or "")
                    for key in ("name", "position", "personnel_no", "id")
                ).lower(),
            )
            normalized.append(copy)
            by_id[employee_id] = copy
        self._rows = tuple(normalized)
        self._by_id = by_id
        self._selected = []

    def search(self, text=""):
        needle = str(text or "").casefold().strip()
        if not needle:
            return self._rows
        return tuple(
            row for row in self._rows
            if needle in str(row.get("search_text") or "").casefold()
            or needle in str(row.get("label") or "").casefold()
        )

    def add_ids(self, values):
        selected = set(self._selected)
        for value in values:
            employee_id = int(value)
            if employee_id not in self._by_id or employee_id in selected:
                continue
            self._selected.append(employee_id)
            selected.add(employee_id)
        return self.selected_rows()

    def remove_ids(self, values):
        remove = {int(value) for value in values}
        self._selected = [
            employee_id for employee_id in self._selected
            if employee_id not in remove
        ]
        return self.selected_rows()

    def selected_rows(self):
        return tuple(
            self._by_id[employee_id] for employee_id in self._selected
        )

    def selected_ids(self):
        return tuple(self._selected)


def _program_caption(row):
    return "[%s] %s — %s / %s — r%d" % (
        program_sources.program_line(row.direction, row.kind),
        row.title,
        row.direction,
        row.kind,
        row.revision,
    )


def _latest_programs(workspace_root):
    latest = {}
    for row in planner.list_programs(workspace_root):
        current = latest.get(row.program_id)
        if current is None or row.revision > current.revision:
            latest[row.program_id] = row
    line_order = {
        label: index for index, label in enumerate(program_sources.LINE_ALL)
    }
    return tuple(sorted(
        latest.values(),
        key=lambda row: (
            line_order.get(
                program_sources.program_line(row.direction, row.kind), 99
            ),
            row.direction.casefold(),
            row.kind.casefold(),
            row.title.casefold(),
            row.program_id,
        ),
    ))


def open_program_history(parent, core, workspace_root, program_id):
    rows = planner.list_programs(workspace_root, program_id)
    if not rows:
        raise ValueError("Програму не знайдено")

    win = core.tk.Toplevel(parent)
    win.title("Історія редакцій програми")
    try:
        core.fit_window_to_screen(win, 900, 600, 680, 440)
        core.configure_toplevel(
            win, title=win.title(), minsize=(680, 440)
        )
    except Exception:
        pass

    body = core.ttk.Frame(win, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(1, weight=1)

    core.ttk.Label(
        body,
        text=rows[-1].title,
        style="Subtitle.TLabel",
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

    revisions = core.tk.Listbox(body, exportselection=False, width=28)
    revisions.grid(row=1, column=0, sticky="nsw", padx=(0, 8))
    text = core.tk.Text(body, wrap="word")
    text.grid(row=1, column=1, sticky="nsew")

    ordered = tuple(sorted(rows, key=lambda row: row.revision, reverse=True))
    for row in ordered:
        revisions.insert(
            "end",
            "r%d · від %s%s" % (
                row.revision,
                _iso_to_ui(row.valid_from),
                (
                    " · до " + _iso_to_ui(row.valid_until)
                    if row.valid_until else ""
                ),
            ),
        )

    def show_revision(_event=None):
        selection = revisions.curselection()
        if not selection:
            return
        row = ordered[int(selection[0])]
        payload = (
            "%s\n%s / %s\nРедакція: r%d\n"
            "Чинна від: %s%s\nЗатвердив: %s\nПідстава: %s\n\n%s"
            % (
                row.title,
                row.direction,
                row.kind,
                row.revision,
                _iso_to_ui(row.valid_from),
                (
                    " до " + _iso_to_ui(row.valid_until)
                    if row.valid_until else ""
                ),
                row.approved_by or "—",
                row.source_note or "—",
                row.program_text,
            )
        )
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", payload)
        text.configure(state="disabled")

    revisions.bind("<<ListboxSelect>>", show_revision)
    revisions.selection_set(0)
    show_revision()
    core.ttk.Button(
        body, text="Закрити", command=win.destroy
    ).grid(row=2, column=1, sticky="e", pady=(8, 0))
    return win


def open_program_editor(
    parent, core, workspace_root, *, current=None, on_saved=None
):
    """Create a program or append one immutable revision."""
    is_revision = current is not None
    win = core.tk.Toplevel(parent)
    win.title(
        "Нова редакція програми" if is_revision else "Нова програма інструктажу"
    )
    try:
        core.fit_window_to_screen(win, 900, 700, 700, 520)
        core.configure_toplevel(
            win, title=win.title(), minsize=(700, 520)
        )
    except Exception:
        pass

    body = core.ttk.Frame(win, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(8, weight=1)

    direction_var = core.tk.StringVar(
        value=current.direction if current else "БДР"
    )
    kind_var = core.tk.StringVar(
        value=current.kind if current else BRIEFING_KINDS["БДР"][0]
    )
    title_var = core.tk.StringVar(value=current.title if current else "")
    valid_from_var = core.tk.StringVar(
        value=_iso_to_ui(current.valid_from) if current else date.today().strftime("%d.%m.%Y")
    )
    valid_until_var = core.tk.StringVar(
        value=_iso_to_ui(current.valid_until) if current else ""
    )
    approved_var = core.tk.StringVar(
        value=current.approved_by if current else _default_approved_by(core)
    )
    source_var = core.tk.StringVar(
        value=current.source_note if current else ""
    )
    template_var = core.tk.StringVar(value="")

    core.ttk.Label(body, text="Напрям").grid(
        row=0, column=0, sticky="w", padx=(0, 8), pady=3
    )
    direction_box = core.ttk.Combobox(
        body,
        textvariable=direction_var,
        values=tuple(BRIEFING_KINDS),
        state="readonly",
    )
    direction_box.grid(row=0, column=1, sticky="ew", pady=3)

    core.ttk.Label(body, text="Вид").grid(
        row=1, column=0, sticky="w", padx=(0, 8), pady=3
    )
    kind_box = core.ttk.Combobox(
        body,
        textvariable=kind_var,
        values=BRIEFING_KINDS[direction_var.get()],
        state="readonly",
    )
    kind_box.grid(row=1, column=1, sticky="ew", pady=3)

    core.ttk.Label(body, text="Назва").grid(
        row=2, column=0, sticky="w", padx=(0, 8), pady=3
    )
    core.ttk.Entry(body, textvariable=title_var).grid(
        row=2, column=1, sticky="ew", pady=3
    )

    core.ttk.Label(body, text="Основа програми").grid(
        row=3, column=0, sticky="w", padx=(0, 8), pady=3
    )
    template_row = core.ttk.Frame(body)
    template_row.grid(row=3, column=1, sticky="ew", pady=3)
    template_row.columnconfigure(0, weight=1)
    template_box = core.ttk.Combobox(
        template_row, textvariable=template_var, state="readonly"
    )
    template_box.grid(row=0, column=0, sticky="ew")
    apply_template_button = core.ttk.Button(
        template_row,
        text="Підставити",
        command=lambda: apply_template(),
    )
    apply_template_button.grid(row=0, column=1, padx=(6, 0))
    source_status_var = core.tk.StringVar(value="")
    core.ttk.Label(
        template_row,
        textvariable=source_status_var,
        style="Muted.TLabel",
        wraplength=760,
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(3, 0))

    dates = core.ttk.Frame(body)
    dates.grid(row=4, column=0, columnspan=2, sticky="ew", pady=3)
    dates.columnconfigure(1, weight=1)
    dates.columnconfigure(3, weight=1)
    core.ttk.Label(dates, text="Чинна від").grid(
        row=0, column=0, sticky="w", padx=(0, 5)
    )
    core.ttk.Entry(dates, textvariable=valid_from_var).grid(
        row=0, column=1, sticky="ew", padx=(0, 10)
    )
    core.ttk.Label(dates, text="до (необов.)").grid(
        row=0, column=2, sticky="w", padx=(0, 5)
    )
    core.ttk.Entry(dates, textvariable=valid_until_var).grid(
        row=0, column=3, sticky="ew"
    )

    core.ttk.Label(body, text="Затвердив").grid(
        row=5, column=0, sticky="w", padx=(0, 8), pady=3
    )
    core.ttk.Entry(body, textvariable=approved_var).grid(
        row=5, column=1, sticky="ew", pady=3
    )
    core.ttk.Label(body, text="Підстава / примітка").grid(
        row=6, column=0, sticky="w", padx=(0, 8), pady=3
    )
    core.ttk.Entry(body, textvariable=source_var).grid(
        row=6, column=1, sticky="ew", pady=3
    )
    core.ttk.Label(
        body,
        text=(
            "Нова редакція не змінює попередню. Старі заходи завжди "
            "лишаються прив'язаними до тієї редакції, з якою їх створили."
        ),
        style="Muted.TLabel",
        wraplength=820,
        justify="left",
    ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(3, 5))

    text_frame = core.ttk.Frame(body)
    text_frame.grid(row=8, column=0, columnspan=2, sticky="nsew")
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)
    program_text = core.tk.Text(text_frame, wrap="word")
    ybar = core.ttk.Scrollbar(
        text_frame, orient="vertical", command=program_text.yview
    )
    program_text.configure(yscrollcommand=ybar.set)
    program_text.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    if current:
        program_text.insert("1.0", current.program_text)

    template_rows = []

    def refresh_templates(_event=None):
        try:
            rows, notes = program_sources.source_options(
                workspace_root,
                getattr(core, "APP_VERSION", "10.25-r5"),
                direction_var.get(),
                kind_var.get(),
            )
            template_rows[:] = list(rows)
        except Exception as exc:
            template_rows[:] = []
            notes = ("Не вдалося прочитати основи програм: %s" % exc,)
        captions = [row.caption for row in template_rows]
        template_box.configure(values=captions)
        template_var.set(captions[0] if captions else "")
        if notes:
            source_status_var.set(" · ".join(notes))
        else:
            source_status_var.set(
                "Доступно основ: %d. Вибрана основа копіюється у цю "
                "редакцію програми; подальші зміни бібліотеки її не перепишуть."
                % len(captions)
            )

    def direction_changed(_event=None):
        values = BRIEFING_KINDS[direction_var.get()]
        kind_box.configure(values=values)
        kind_var.set(values[0])
        refresh_templates()

    def apply_template():
        caption = template_var.get()
        row = next(
            (item for item in template_rows if item.caption == caption),
            None,
        )
        if row is None:
            return
        if not title_var.get().strip():
            title_var.set(row.topic)
        source_var.set(row.source_note)
        program_text.delete("1.0", "end")
        program_text.insert("1.0", row.program)
        source_status_var.set(
            "Підставлено: %s. Текст нижче можна доповнити під конкретне "
            "підприємство до збереження нової редакції."
            % row.caption
        )

    direction_box.bind("<<ComboboxSelected>>", direction_changed)
    kind_box.bind("<<ComboboxSelected>>", refresh_templates)
    if is_revision:
        direction_box.configure(state="disabled")
        kind_box.configure(state="disabled")

    def save():
        try:
            title = title_var.get().strip()
            text_value = program_text.get("1.0", "end-1c").strip()
            valid_from = _ui_to_iso(
                valid_from_var.get(), "Дата початку чинності"
            )
            valid_until = _ui_to_iso(
                valid_until_var.get(),
                "Дата завершення чинності",
                allow_empty=True,
            )
            if is_revision:
                row = planner.revise_program(
                    workspace_root,
                    current.program_id,
                    title=title,
                    program_text=text_value,
                    valid_from=valid_from,
                    valid_until=valid_until,
                    source_note=source_var.get(),
                    approved_by=approved_var.get(),
                )
            else:
                row = planner.create_program(
                    workspace_root,
                    direction=direction_var.get(),
                    kind=kind_var.get(),
                    title=title,
                    program_text=text_value,
                    valid_from=valid_from,
                    valid_until=valid_until,
                    source_note=source_var.get(),
                    approved_by=approved_var.get(),
                )
        except Exception as exc:
            core.messagebox.showerror(
                "Програма інструктажу", str(exc), parent=win
            )
            return
        if callable(on_saved):
            on_saved(row)
        win.destroy()

    actions = core.ttk.Frame(body)
    actions.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))
    core.ttk.Button(
        actions, text="Скасувати", command=win.destroy
    ).pack(side="right")
    save_button = core.ttk.Button(
        actions,
        text=("Створити редакцію" if is_revision else "Створити програму"),
        style="Accent.TButton",
        command=save,
    )
    save_button.pack(side="right", padx=(0, 6))

    refresh_templates()
    win._taxo_program_save_button = save_button
    win._taxo_program_text = program_text
    return win


def open_planning_preparation(
    parent, core, workspace_root=None
):
    workspace_root = Path(workspace_root or load_workspace_root())
    win = core.tk.Toplevel(parent)
    win.title("Інструктажі — програми, працівники та друк")
    try:
        core.fit_window_to_screen(win, 1080, 700, 780, 520)
        core.configure_toplevel(
            win, title=win.title(), minsize=(780, 520)
        )
    except Exception:
        pass

    body = core.ttk.Frame(win, padding=10)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(2, weight=1)

    program_frame = core.ttk.LabelFrame(
        body, text="Програма — згруповано за лініями", padding=7
    )
    program_frame.grid(row=0, column=0, sticky="ew", pady=(0, 7))
    program_frame.columnconfigure(0, weight=1)
    program_var = core.tk.StringVar(value="")
    program_box = core.ttk.Combobox(
        program_frame, textvariable=program_var, state="readonly"
    )
    program_box.grid(row=0, column=0, sticky="ew", padx=(0, 7))
    new_program_button = core.ttk.Button(
        program_frame, text="Нова програма…"
    )
    new_program_button.grid(row=0, column=1, padx=(0, 5))
    revise_button = core.ttk.Button(
        program_frame, text="Нова редакція…"
    )
    revise_button.grid(row=0, column=2, padx=(0, 5))
    history_button = core.ttk.Button(
        program_frame, text="Історія…"
    )
    history_button.grid(row=0, column=3)

    schedule = core.ttk.Frame(body)
    schedule.grid(row=1, column=0, sticky="ew", pady=(0, 7))
    schedule.columnconfigure(3, weight=1)
    day_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
    search_var = core.tk.StringVar(value="")
    core.ttk.Label(schedule, text="Дата плану").grid(
        row=0, column=0, sticky="w"
    )
    core.ttk.Entry(
        schedule, textvariable=day_var, width=14
    ).grid(row=0, column=1, sticky="w", padx=(5, 14))
    core.ttk.Label(schedule, text="Пошук працівників").grid(
        row=0, column=2, sticky="w"
    )
    search_entry = core.ttk.Entry(
        schedule, textvariable=search_var
    )
    search_entry.grid(row=0, column=3, sticky="ew", padx=(5, 0))

    people_frame = core.ttk.LabelFrame(
        body,
        text="Працівники — вибір накопичується під час пошуку",
        padding=7,
    )
    people_frame.grid(row=2, column=0, sticky="nsew")
    people_frame.columnconfigure(0, weight=1)
    people_frame.columnconfigure(2, weight=1)
    people_frame.rowconfigure(1, weight=1)

    core.ttk.Label(
        people_frame, text="Знайдені у реєстрі"
    ).grid(row=0, column=0, sticky="w")
    core.ttk.Label(
        people_frame, text="Вибрані для цього заходу"
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
    footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    count_var = core.tk.StringVar(value="Вибрано: 0")
    core.ttk.Label(
        footer, textvariable=count_var, style="Muted.TLabel"
    ).pack(side="left")
    core.ttk.Button(
        footer, text="Закрити", command=win.destroy
    ).pack(side="right")
    prepare_button = core.ttk.Button(
        footer,
        text="Підготувати DOCX",
        style="Accent.TButton",
    )
    prepare_button.pack(side="right", padx=(0, 7))

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
    selection_model = EmployeeSelectionModel(employee_rows)
    visible_rows = []
    selected_visible = []
    program_rows = []
    program_by_caption = {}

    def current_program():
        return program_by_caption.get(program_var.get())

    def refresh_programs(select_program_id=None):
        program_rows[:] = list(_latest_programs(workspace_root))
        program_by_caption.clear()
        captions = []
        selected_caption = ""
        for row in program_rows:
            caption = _program_caption(row)
            captions.append(caption)
            program_by_caption[caption] = row
            if select_program_id and row.program_id == select_program_id:
                selected_caption = caption
        program_box.configure(values=captions)
        if selected_caption:
            program_var.set(selected_caption)
        elif captions and program_var.get() not in program_by_caption:
            program_var.set(captions[0])
        elif not captions:
            program_var.set("")
        revise_button.configure(
            state=("normal" if current_program() is not None else "disabled")
        )
        history_button.configure(
            state=("normal" if current_program() is not None else "disabled")
        )

    def refresh_available(*_args):
        visible_rows[:] = list(selection_model.search(search_var.get()))
        available.delete(0, "end")
        selected_ids = set(selection_model.selected_ids())
        for row in visible_rows:
            suffix = "  ✓" if int(row["id"]) in selected_ids else ""
            available.insert("end", str(row["label"]) + suffix)

    def refresh_selected():
        selected_visible[:] = list(selection_model.selected_rows())
        selected.delete(0, "end")
        for row in selected_visible:
            selected.insert("end", str(row["label"]))
        count_var.set("Вибрано: %d" % len(selected_visible))
        refresh_available()

    def add_selected():
        ids = [
            visible_rows[int(index)]["id"]
            for index in available.curselection()
            if 0 <= int(index) < len(visible_rows)
        ]
        selection_model.add_ids(ids)
        refresh_selected()

    def remove_selected():
        ids = [
            selected_visible[int(index)]["id"]
            for index in selected.curselection()
            if 0 <= int(index) < len(selected_visible)
        ]
        selection_model.remove_ids(ids)
        refresh_selected()

    def create_program():
        open_program_editor(
            win,
            core,
            workspace_root,
            on_saved=lambda row: refresh_programs(row.program_id),
        )

    def revise_program():
        current = current_program()
        if current is None:
            return
        open_program_editor(
            win,
            core,
            workspace_root,
            current=current,
            on_saved=lambda row: refresh_programs(row.program_id),
        )

    def history():
        current = current_program()
        if current is None:
            return
        try:
            open_program_history(
                win, core, workspace_root, current.program_id
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Історія програми", str(exc), parent=win
            )

    def prepare():
        program = current_program()
        people = selection_model.selected_rows()
        if program is None:
            core.messagebox.showerror(
                "Підготовка інструктажу",
                "Створіть або виберіть програму.",
                parent=win,
            )
            return
        if not people:
            core.messagebox.showerror(
                "Підготовка інструктажу",
                "Виберіть хоча б одного працівника.",
                parent=win,
            )
            return
        try:
            scheduled_for = _ui_to_iso(day_var.get(), "Дата плану")
            session, link, path = prepared_output.ensure_planned_and_prepare(
                workspace_root,
                program_id=program.program_id,
                program_revision=program.revision,
                scheduled_for=scheduled_for,
                participants=people,
            )
        except Exception as exc:
            core.messagebox.showerror(
                "Підготовка інструктажу", str(exc), parent=win
            )
            return
        core.messagebox.showinfo(
            "Підготовлено до друку",
            (
                "DOCX збережено у каталозі Taxo і прив'язано до "
                "планового заходу. Стан: «Підготовлено». "
                "Це не означає, що інструктаж проведено або підписано.\n\n%s"
                % path
            ),
            parent=win,
        )
        try:
            instruction_documents.open_briefing_document(path)
        except OSError as exc:
            core.messagebox.showwarning(
                "Документ збережено",
                "DOCX створено, але не вдалося відкрити автоматично.\n\n%s"
                % exc,
                parent=win,
            )

    new_program_button.configure(command=create_program)
    revise_button.configure(command=revise_program)
    history_button.configure(command=history)
    add_button.configure(command=add_selected)
    remove_button.configure(command=remove_selected)
    prepare_button.configure(command=prepare)
    program_box.bind(
        "<<ComboboxSelected>>",
        lambda _event: refresh_programs(
            current_program().program_id if current_program() else None
        ),
    )
    search_var.trace_add("write", refresh_available)

    refresh_programs()
    refresh_selected()

    win._taxo_briefing_program_combo = program_box
    win._taxo_briefing_new_program_button = new_program_button
    win._taxo_briefing_revise_program_button = revise_button
    win._taxo_briefing_history_button = history_button
    win._taxo_briefing_search_entry = search_entry
    win._taxo_briefing_available_people = available
    win._taxo_briefing_selected_people = selected
    win._taxo_briefing_add_people_button = add_button
    win._taxo_briefing_remove_people_button = remove_button
    win._taxo_briefing_prepare_button = prepare_button
    win._taxo_briefing_selection_model = selection_model
    win._taxo_briefing_program_rows = program_rows
    return win
