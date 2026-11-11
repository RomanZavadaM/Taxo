# -*- coding: utf-8 -*-
"""Paper-first preparation of safety briefing lists for the operations center.

Taxo prepares editable topics/programs and employee lists. It does not store
signatures and does not mark a briefing as actually completed. The paper journal
and real signatures remain the user's source of confirmation.
"""
from __future__ import annotations

from datetime import date

import entity_choices as ops
import safety_templates as safety_tpl
import safety_instruction_document_service as instruction_documents
from workspace import load_workspace_root


from briefing_preparation import (
    BRIEFING_KINDS, PREPARATION_NOTICE, quarter_for, shift_quarter,
    quarter_caption, prepare_list, preparation_filename, write_preparation_csv,
)


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def install_instruction_tab(app, core, book):
    """Install the paper-first briefing preparation tab."""
    for tab_id in book.tabs():
        if str(book.tab(tab_id, "text")) == "Інструктажі та журнали":
            return book.nametowidget(tab_id)

    tab = core.ttk.Frame(book, padding=12)
    book.add(tab, text="Інструктажі та журнали")
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(3, weight=1)

    core.ttk.Label(
        tab, text="Інструктажі та журнали", style="HeroTitle.TLabel"
    ).grid(row=0, column=0, sticky="w")
    core.ttk.Label(
        tab, text=(
            "Taxo дає готові редаговані заготовки програм і списки працівників. "
            "Це допоміжна підготовка: фактичне проведення та підписи залишаються у паперовому журналі. "
            "Заготовку потрібно звірити з умовами підприємства, маршрутом, професією та чинними інструкціями."
        ),
        style="Muted.TLabel", wraplength=920, justify="left",
    ).grid(row=1, column=0, sticky="ew", pady=(2, 8))

    quarter_box = core.ttk.LabelFrame(tab, text="Планування за кварталами", padding=8)
    quarter_box.grid(row=2, column=0, sticky="ew", pady=(0, 6))
    quarter_box.columnconfigure(1, weight=1)
    year, quarter = quarter_for()
    quarter_value = core.tk.StringVar(value=quarter_caption(year, quarter))

    def move_quarter(step):
        state = getattr(tab, "_taxo_quarter", (year, quarter))
        updated = shift_quarter(state[0], state[1], step)
        tab._taxo_quarter = updated
        quarter_value.set(quarter_caption(*updated))

    tab._taxo_quarter = (year, quarter)
    core.ttk.Button(
        quarter_box, text="Попередній", command=lambda: move_quarter(-1)
    ).grid(row=0, column=0, sticky="w", padx=(0, 8))
    core.ttk.Label(
        quarter_box, textvariable=quarter_value
    ).grid(row=0, column=1, sticky="w")
    core.ttk.Button(
        quarter_box, text="Наступний", command=lambda: move_quarter(1)
    ).grid(row=0, column=2, sticky="e")
    core.ttk.Label(
        quarter_box,
        text=(
            "Квартал тут — робочий календар Taxo, а не автоматично встановлений законом строк. "
            "Для БДР програми/строки затверджує керівник; сезонні повторні інструктажі передбачають "
            "перехід до осінньо-зимового та весняно-літнього періодів. Позапланові/цільові заходи "
            "проводяться за фактичною підставою незалежно від квартального плану."
        ),
        style="Muted.TLabel", wraplength=900, justify="left",
    ).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))

    frame = core.ttk.LabelFrame(tab, text="Підготувати матеріал для паперового інструктажу", padding=8)
    frame.grid(row=3, column=0, sticky="nsew")
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(10, weight=1)

    track_var = core.tk.StringVar(value="БДР")
    kind_var = core.tk.StringVar(value=BRIEFING_KINDS["БДР"][0])
    date_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
    topic_var = core.tk.StringVar(value="")
    reason_var = core.tk.StringVar(value="")
    template_var = core.tk.StringVar(value="")
    source_note_var = core.tk.StringVar(value="")
    program_var = core.tk.StringVar(value="")
    selected_template_id = core.tk.StringVar(value="")
    template_rows = []

    core.ttk.Label(frame, text="Напрям").grid(row=0, column=0, sticky="w", pady=3)
    track_box = core.ttk.Combobox(
        frame, textvariable=track_var, values=tuple(BRIEFING_KINDS), state="readonly"
    )
    track_box.grid(row=0, column=1, sticky="ew", pady=3)

    core.ttk.Label(frame, text="Вид").grid(row=1, column=0, sticky="w", pady=3)
    kind_box = core.ttk.Combobox(
        frame, textvariable=kind_var, values=BRIEFING_KINDS["БДР"], state="readonly"
    )
    kind_box.grid(row=1, column=1, sticky="ew", pady=3)

    core.ttk.Label(frame, text="Дата").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=3)
    core.ttk.Entry(frame, textvariable=date_var).grid(row=2, column=1, sticky="ew", pady=3)

    core.ttk.Label(frame, text="Типова заготовка").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=3)
    template_box = core.ttk.Combobox(
        frame, textvariable=template_var, values=(), state="readonly"
    )
    template_box.grid(row=3, column=1, sticky="ew", pady=3)

    core.ttk.Label(frame, text="Тема / програма").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=3)
    core.ttk.Entry(frame, textvariable=topic_var).grid(row=4, column=1, sticky="ew", pady=3)

    core.ttk.Label(frame, text="Підстава (для позапланового)").grid(
        row=5, column=0, sticky="w", padx=(0, 8), pady=3
    )
    core.ttk.Entry(frame, textvariable=reason_var).grid(row=5, column=1, sticky="ew", pady=3)

    source_label = core.ttk.Label(
        frame, textvariable=source_note_var, style="Muted.TLabel",
        wraplength=820, justify="left",
    )
    source_label.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(3, 3))

    program_bar = core.ttk.Frame(frame)
    program_bar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(2, 5))
    core.ttk.Label(
        program_bar,
        text="Зміст заготовки можна відкрити, змінити, скоротити або доповнити перед збереженням.",
        style="Muted.TLabel",
    ).pack(side="left")

    def edit_program():
        editor = core.tk.Toplevel(tab)
        editor.title("Текст програми інструктажу")
        try:
            core.fit_window_to_screen(editor, 900, 650, 700, 480)
            core.configure_toplevel(editor, title=editor.title(), minsize=(700, 480))
        except Exception:
            pass
        body = core.ttk.Frame(editor, padding=12)
        body.pack(fill="both", expand=True)
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)
        core.ttk.Label(
            body,
            text=topic_var.get() or "Текст програми",
            style="Subtitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        text_frame = core.ttk.Frame(body)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        editor_text = core.tk.Text(text_frame, wrap="word")
        ybar = core.ttk.Scrollbar(text_frame, orient="vertical", command=editor_text.yview)
        editor_text.configure(yscrollcommand=ybar.set)
        editor_text.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        editor_text.insert("1.0", program_var.get())

        def accept():
            program_var.set(editor_text.get("1.0", "end-1c").strip())
            editor.destroy()

        actions = core.ttk.Frame(body)
        actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        core.ttk.Button(actions, text="Скасувати", command=editor.destroy).pack(side="right")
        core.ttk.Button(
            actions, text="Зберегти текст", style="Accent.TButton", command=accept
        ).pack(side="right", padx=(0, 6))
        editor.transient(tab.winfo_toplevel())

    edit_button = core.ttk.Button(program_bar, text="Текст програми…", command=edit_program)
    edit_button.pack(side="right")

    def apply_template_by_title(title):
        row = next((item for item in template_rows if item["title"] == title), None)
        if not row:
            selected_template_id.set("")
            source_note_var.set("")
            return
        selected_template_id.set(row["id"])
        topic_var.set(row["topic"])
        program_var.set(row["program"])
        source_note_var.set(row["source_note"])

    def refresh_templates(select_first=True):
        template_rows[:] = list(safety_tpl.templates_for(track_var.get(), kind_var.get()))
        titles = [row["title"] for row in template_rows]
        template_box.configure(values=titles)
        if titles and select_first:
            template_var.set(titles[0])
            apply_template_by_title(titles[0])
        elif not titles:
            template_var.set("")
            selected_template_id.set("")
            source_note_var.set("")
            program_var.set("")

    def direction_changed(_event=None):
        kinds = BRIEFING_KINDS[track_var.get()]
        kind_box.configure(values=kinds)
        kind_var.set(kinds[0])
        refresh_templates(select_first=True)

    def kind_changed(_event=None):
        refresh_templates(select_first=True)

    def template_changed(_event=None):
        apply_template_by_title(template_var.get())

    track_box.bind("<<ComboboxSelected>>", direction_changed)
    kind_box.bind("<<ComboboxSelected>>", kind_changed)
    template_box.bind("<<ComboboxSelected>>", template_changed)

    controls = core.ttk.Frame(frame)
    controls.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(4, 4))
    core.ttk.Button(
        controls, text="Вибрати всіх", command=lambda: people.selection_set(0, "end")
    ).pack(side="left", padx=(0, 6))
    core.ttk.Button(
        controls, text="Очистити вибір", command=lambda: people.selection_clear(0, "end")
    ).pack(side="left")

    core.ttk.Label(
        frame,
        text="Працівники (Ctrl/Shift для вибору кількох):",
    ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(2, 2))
    people_frame = core.ttk.Frame(frame)
    people_frame.grid(row=10, column=0, columnspan=2, sticky="nsew")
    people_frame.columnconfigure(0, weight=1)
    people_frame.rowconfigure(0, weight=1)
    people = core.tk.Listbox(people_frame, selectmode="extended", height=3, exportselection=False)
    scroll = core.ttk.Scrollbar(people_frame, orient="vertical", command=people.yview)
    people.configure(yscrollcommand=scroll.set)
    people.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")

    choice_rows = []
    try:
        con = core.db()
        try:
            choices = ops.list_employee_choices(con, active_only=True)
        finally:
            con.close()
        choice_rows.extend(choices)
        for row in choices:
            people.insert("end", str(row["label"]))
    except Exception:
        core.ttk.Label(
            frame, text="Не вдалося прочитати персонал. Перевірте дані перед формуванням.",
            style="Muted.TLabel"
        ).grid(row=11, column=0, columnspan=2, sticky="w")

    def save_draft_list():
        try:
            selected_indexes = tuple(int(index) for index in people.curselection())
            selected_records = [
                choice_rows[index] for index in selected_indexes
                if 0 <= index < len(choice_rows)
            ]
            prepared = prepare_list(
                track_var.get(), kind_var.get(), date_var.get(), topic_var.get(),
                (
                    str(record.get("name") or record.get("label") or "").strip()
                    for record in selected_records
                ),
                reason_var.get(),
                people_records=selected_records,
                program_text=program_var.get(),
                template_id=selected_template_id.get(),
                source_note=source_note_var.get(),
            )
        except ValueError as exc:
            core.messagebox.showerror("Підготовка інструктажу", str(exc), parent=tab)
            return
        if not prepared["program_text"]:
            core.messagebox.showerror(
                "Інструктаж", "Текст програми порожній. Відкрийте «Текст програми…» та перевірте його.",
                parent=tab
            )
            return
        try:
            target = instruction_documents.save_briefing_document(
                load_workspace_root(),
                prepared,
            )
        except Exception as exc:
            core.messagebox.showerror("Файл не збережено", str(exc), parent=tab)
            return
        core.messagebox.showinfo(
            "Друкований комплект",
            "Створено Word із повною програмою та окремим листом для підписів. "
            "Документ збережено в каталозі Taxo і входить у повну резервну копію. "
            "Підписів і позначки «проведено» автоматично немає.\n\n" + str(target),
            parent=tab,
        )
        try:
            instruction_documents.open_briefing_document(target)
        except OSError as exc:
            core.messagebox.showwarning(
                "Документ збережено",
                "Файл створено, але його не вдалося відкрити автоматично. "
                "Відкрийте його в Word-сумісній програмі вручну.\n\n%s\n\n%s" % (target, exc),
                parent=tab,
            )

    def show_catalog():
        from paper_documents_ui import open_paper_document_catalog
        open_paper_document_catalog(tab, core, load_workspace_root())

    core.ttk.Button(
        controls, text="Створити комплект DOCX для друку",
        style="Accent.TButton", command=save_draft_list
    ).pack(side="right")

    core.ttk.Button(
        controls, text="Каталог документів…", command=show_catalog
    ).pack(side="right", padx=(0, 8))

    # Stable hooks for regression/feature-loss checks.
    tab._taxo_briefing_template_box = template_box
    tab._taxo_briefing_program_var = program_var
    tab._taxo_briefing_template_id = selected_template_id
    tab._taxo_briefing_edit_program_button = edit_button

    refresh_templates(select_first=True)
    return tab
