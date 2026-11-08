# -*- coding: utf-8 -*-
"""Paper-first preparation of safety briefing lists for the operations center.

No signature storage, no schema changes and no automatic completion status.
A saved CSV is only a preparation list, not an official instruction journal.
"""
from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

import operations_orders as ops


BRIEFING_KINDS = {
    "БДР": (
        "Вступний",
        "Первинний",
        "Передрейсовий (цільовий)",
        "Періодичний (повторний)",
        "Позаплановий (спеціальний)",
    ),
    "Охорона праці": (
        "Вступний",
        "Первинний",
        "Повторний",
        "Позаплановий",
        "Цільовий",
    ),
}

PREPARATION_NOTICE = (
    "ПІДГОТОВЧИЙ СПИСОК. НЕ Є ЖУРНАЛОМ ІНСТРУКТАЖІВ. "
    "Паперові записи та особисті підписи оформлює відповідальна особа."
)


def quarter_for(day=None):
    day = day or date.today()
    return (day.year, (day.month - 1) // 3 + 1)


def shift_quarter(year, quarter, delta):
    index = int(year) * 4 + int(quarter) - 1 + int(delta)
    if index < 0:
        raise ValueError("Некоректний квартал")
    return divmod(index, 4)[0], divmod(index, 4)[1] + 1


def quarter_caption(year, quarter):
    if int(quarter) not in (1, 2, 3, 4):
        raise ValueError("Квартал має бути від 1 до 4")
    return "%d квартал %d року" % (int(quarter), int(year))


def prepare_list(direction, kind, day_text, topic, people, reason="", people_records=None):
    direction = str(direction or "").strip()
    if direction not in BRIEFING_KINDS:
        raise ValueError("Виберіть напрям інструктажу")
    kind = str(kind or "").strip()
    if kind not in BRIEFING_KINDS[direction]:
        raise ValueError("Виберіть вид інструктажу")
    try:
        parsed_date = datetime.strptime(str(day_text).strip(), "%d.%m.%Y").date()
    except (ValueError, TypeError):
        raise ValueError("Дата має бути у форматі ДД.ММ.РРРР")
    topic = str(topic or "").strip()
    if not topic:
        raise ValueError("Вкажіть тему або назву затвердженої програми")
    reason = str(reason or "").strip()
    if kind.startswith("Позаплановий") and not reason:
        raise ValueError("Для позапланового інструктажу потрібна підстава")
    names = tuple(dict.fromkeys(str(person).strip() for person in people if str(person).strip()))
    if not names:
        raise ValueError("Виберіть хоча б одного працівника")

    records = []
    seen_ids = set()
    for record in people_records or ():
        if not isinstance(record, dict):
            continue
        try:
            employee_id = int(record.get("id"))
        except (TypeError, ValueError):
            continue
        if employee_id in seen_ids:
            continue
        seen_ids.add(employee_id)
        records.append({
            "id": employee_id,
            "name": str(record.get("name") or record.get("label") or "").strip(),
            "personnel_no": str(record.get("personnel_no") or "").strip(),
        })

    return {
        "direction": direction,
        "kind": kind,
        "day": parsed_date,
        "topic": topic,
        "reason": reason,
        "people": names,
        "people_records": tuple(records),
    }


def preparation_filename(prepared):
    kind = prepared["kind"].split(" ", 1)[0].lower().replace("(", "")
    return "Список_інструктажу_%s_%s_%s_%d-осіб.csv" % (
        "БДР" if prepared["direction"] == "БДР" else "ОП",
        kind,
        prepared["day"].isoformat(),
        len(prepared["people"]),
    )


def write_preparation_csv(path, prepared):
    """Create a new supplementary CSV; never overwrite another preparation."""
    target = Path(path)
    with target.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow([PREPARATION_NOTICE])
        writer.writerow(["Напрям", prepared["direction"]])
        writer.writerow(["Вид", prepared["kind"]])
        writer.writerow(["Дата", prepared["day"].strftime("%d.%m.%Y")])
        writer.writerow(["Тема / програма", prepared["topic"]])
        writer.writerow(["Підстава", prepared["reason"]])
        writer.writerow([])
        records = tuple(prepared.get("people_records") or ())
        if records:
            writer.writerow(["№", "Працівник", "Табельний №", "Код Taxo"])
            for number, record in enumerate(records, 1):
                writer.writerow([
                    number,
                    record.get("name", ""),
                    record.get("personnel_no", ""),
                    record.get("id", ""),
                ])
        else:
            writer.writerow(["№", "Працівник"])
            for number, name in enumerate(prepared["people"], 1):
                writer.writerow([number, name])
    return target


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def install_instruction_tab(app, core, book):
    """A separate visible operations tab; no writes to the operational DB."""
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
            "Це підготовка списків для інженера, а не електронний журнал. "
            "Проведення інструктажу та підписання на папері відбуваються окремо. "
            "Заповнення цієї форми не означає, що інструктаж проведено."
        ),
        style="Muted.TLabel", wraplength=860, justify="left",
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
            "У цьому першому кроці автоматичного календаря та затверджених програм ще немає. "
            "Дати й види визначає інженер за правилами підприємства. "
            "Позапланові заходи не замінюють регулярних."
        ),
        style="Muted.TLabel", wraplength=840, justify="left",
    ).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))

    frame = core.ttk.LabelFrame(tab, text="Підготувати список для паперової роботи", padding=8)
    frame.grid(row=3, column=0, sticky="nsew")
    frame.columnconfigure(1, weight=1)
    track_var = core.tk.StringVar(value="БДР")
    kind_var = core.tk.StringVar(value=BRIEFING_KINDS["БДР"][0])
    date_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
    topic_var = core.tk.StringVar(value="")
    reason_var = core.tk.StringVar(value="")
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

    def direction_changed(_event=None):
        kinds = BRIEFING_KINDS[track_var.get()]
        kind_box.configure(values=kinds)
        kind_var.set(kinds[0])

    track_box.bind("<<ComboboxSelected>>", direction_changed)
    for row_index, title, var in (
        (2, "Дата", date_var),
        (3, "Тема / програма", topic_var),
        (4, "Підстава (для позапланового)", reason_var),
    ):
        core.ttk.Label(frame, text=title).grid(
            row=row_index, column=0, sticky="w", padx=(0, 8), pady=3
        )
        core.ttk.Entry(frame, textvariable=var).grid(
            row=row_index, column=1, sticky="ew", pady=3
        )

    core.ttk.Label(
        frame,
        text="Працівники (Ctrl/Shift для вибору кількох):",
    ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 2))
    people_frame = core.ttk.Frame(frame)
    people_frame.grid(row=6, column=0, columnspan=2, sticky="nsew")
    people_frame.columnconfigure(0, weight=1)
    frame.rowconfigure(6, weight=1)
    people = core.tk.Listbox(people_frame, selectmode="extended", height=5, exportselection=False)
    scroll = core.ttk.Scrollbar(people_frame, orient="vertical", command=people.yview)
    people.configure(yscrollcommand=scroll.set)
    people.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")
    people_frame.rowconfigure(0, weight=1)
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
        ).grid(row=7, column=0, columnspan=2, sticky="w")

    controls = core.ttk.Frame(frame)
    controls.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    core.ttk.Button(
        controls, text="Вибрати всіх", command=lambda: people.selection_set(0, "end")
    ).pack(side="left", padx=(0, 6))
    core.ttk.Button(
        controls, text="Очистити вибір", command=lambda: people.selection_clear(0, "end")
    ).pack(side="left")

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
            )
        except ValueError as exc:
            core.messagebox.showerror("Підготовка інструктажу", str(exc), parent=tab)
            return
        target = core.filedialog.asksaveasfilename(
            parent=tab, title="Зберегти підготовчий список",
            defaultextension=".csv", filetypes=[("Таблиця CSV", "*.csv")],
            initialfile=preparation_filename(prepared)
        )
        if not target:
            return
        try:
            write_preparation_csv(target, prepared)
        except (OSError, ValueError) as exc:
            core.messagebox.showerror(
                "Файл не збережено", str(exc), parent=tab
            )
            return
        core.messagebox.showinfo(
            "Підготовчий список",
            "Список збережено. Це не журнал і не підтвердження проведення інструктажу.",
            parent=tab
        )

    core.ttk.Button(
        controls, text="Зберегти підготовчий список…",
        style="Accent.TButton", command=save_draft_list
    ).pack(side="right")
    return tab
