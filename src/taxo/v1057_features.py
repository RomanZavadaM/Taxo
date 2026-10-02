# -*- coding: utf-8 -*-
"""Taxo 10.5-r7 — employer workflow for reconciliation through Diia."""
from __future__ import annotations

from datetime import date, datetime
from tkinter import simpledialog

import diia_reconciliation as diia
from v1043_features import company_edrpou
from v1048_features import _alive, _find_button, _configure_window

APP_VERSION = "10.5-r7"


def _display_day(value):
    text = str(value or "").strip()
    if not text:
        return "—"
    try:
        return date.fromisoformat(text[:10]).strftime("%d.%m.%Y")
    except Exception:
        return text


def _parse_user_day(value):
    text = str(value or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.")


def install(core, base_app):
    if getattr(core, "_TAXO_1057_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1057App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            diia.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_r7_actions()

        def _install_r7_actions(self):
            root = getattr(self, "personnel_overview_page", None)
            if not _alive(root) or getattr(self, "_r7_diia_cycle_action", False):
                return
            anchor = (
                _find_button(root, "Військові дані / Дія")
                or _find_button(root, "Оригінал держреєстру")
                or _find_button(root, "Реєстр документів")
            )
            if anchor is None:
                return
            core.ttk.Button(
                anchor.master,
                text="Звіряння через Дію",
                style="Accent.TButton",
                command=self.open_diia_reconciliation_cycle,
            ).pack(side="right", padx=(8, 0))
            self._r7_diia_cycle_action = True

        def open_diia_reconciliation_cycle(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Цикл звіряння через Дію", 1180, 790)
            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)

            core.ttk.Label(
                body,
                text="Цикл звіряння персонального військового обліку через Дію",
                style="Title.TLabel",
            ).pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "Taxo готує дані, відкриває офіційні сервіси та веде локальний контроль етапів. "
                    "Програма НЕ надсилає дані в Дію або Реєстр «Оберіг» і не ставить відмітку "
                    "«офіційно звірено» лише через імпорт XLSX чи локальну правку. Факт завершення "
                    "записується тільки після фактичної «Фіксації відомостей персонального обліку» в Дії."
                ),
                wraplength=1120,
                justify="left",
            ).pack(anchor="w", pady=(4, 10))

            readiness_var = core.tk.StringVar(value="")
            cycle_var = core.tk.StringVar(value="")
            info_box = core.ttk.LabelFrame(body, text="Готовність і поточний цикл", padding=10)
            info_box.pack(fill="x", pady=(0, 10))
            core.ttk.Label(info_box, textvariable=readiness_var, justify="left", wraplength=1080).pack(anchor="w")
            core.ttk.Label(
                info_box, textvariable=cycle_var, style="Subtitle.TLabel", justify="left", wraplength=1080
            ).pack(anchor="w", pady=(6, 0))

            services = core.ttk.LabelFrame(body, text="Офіційні сервіси Дії", padding=10)
            services.pack(fill="x", pady=(0, 10))
            for step in diia.service_steps():
                row = core.ttk.Frame(services)
                row.pack(fill="x", pady=3)
                core.ttk.Label(row, text=step["title"], width=42).pack(side="left")
                core.ttk.Label(
                    row, text=step["hint"], justify="left", wraplength=620
                ).pack(side="left", fill="x", expand=True, padx=(4, 8))
                core.ttk.Button(
                    row,
                    text="Відкрити в Дії",
                    command=lambda url=step["url"]: core.open_external(url),
                ).pack(side="right")

            fallback = core.ttk.LabelFrame(body, text="Резервний шлях", padding=10)
            fallback.pack(fill="x", pady=(0, 10))
            core.ttk.Label(
                fallback,
                text=(
                    "Електронний спосіб є основним за наявності технічної можливості. Якщо електронний "
                    "спосіб недоступний або підприємство не має коду ЄДРПОУ, Taxo не блокує роботу: "
                    "застосовується резервний порядок, передбачений п. 46 Порядку №1487."
                ),
                wraplength=1080,
                justify="left",
            ).pack(anchor="w")

            actions = core.ttk.LabelFrame(body, text="Локальні відмітки Taxo", padding=10)
            actions.pack(fill="x", pady=(0, 10))
            core.ttk.Label(
                actions,
                text=(
                    "Ці кнопки лише ведуть локальний журнал підготовки. Перші дві не є юридичним фактом "
                    "завершення звіряння і не створюють запис у журналі офіційних звірянь."
                ),
                wraplength=1080,
                justify="left",
            ).pack(anchor="w", pady=(0, 8))
            action_bar = core.ttk.Frame(actions)
            action_bar.pack(fill="x")

            current = {"cycle": None, "readiness": None}

            def refresh():
                con = core.db()
                try:
                    state = diia.readiness(con, edrpou=company_edrpou(core))
                    cycle = diia.latest_cycle(con, year=state["year"])
                finally:
                    con.close()
                current["readiness"] = state
                current["cycle"] = cycle
                edrpou = state["edrpou"] or "НЕ ЗАПОВНЕНО"
                imported = (
                    "%s · %s" % (state["latest_source_name"] or "державний витяг", state["latest_imported_at"] or "дата невідома")
                    if state["has_registry_import"] else "НЕМАЄ імпорту державних відомостей"
                )
                readiness_var.set(
                    "ЄДРПОУ: %s\n"
                    "Останні державні відомості в Taxo: %s\n"
                    "Активних працівників: %s; з РНОКПП: %s; з військовою карткою: %s"
                    % (
                        edrpou,
                        imported,
                        state["active_employees"],
                        state["employees_with_rnokpp"],
                        state["employees_with_military_profile"],
                    )
                )
                if cycle is None:
                    cycle_var.set("Активний цикл %s року ще не створено." % state["year"])
                else:
                    cycle_var.set(
                        "Цикл #%s · %s · старт %s · отримання/імпорт %s · актуалізації %s · фіксація %s"
                        % (
                            cycle["id"],
                            diia.STATUS_LABELS.get(cycle["status"], cycle["status"]),
                            str(cycle["started_at"] or "—")[:16].replace("T", " "),
                            str(cycle["data_received_at"] or "—")[:16].replace("T", " "),
                            str(cycle["updates_completed_at"] or "—")[:16].replace("T", " "),
                            _display_day(cycle["fixation_date"]),
                        )
                    )

            def ensure_cycle():
                cycle = current.get("cycle")
                if cycle is not None and cycle["status"] != diia.STATUS_FIXED:
                    return cycle
                con = core.db()
                try:
                    cycle = diia.start_cycle(
                        con,
                        edrpou=company_edrpou(core),
                        year=date.today().year,
                    )
                    con.commit()
                finally:
                    con.close()
                refresh()
                return cycle

            def start_or_resume():
                cycle = ensure_cycle()
                core.messagebox.showinfo(
                    "Звіряння через Дію",
                    "Активний локальний цикл Taxo: #%s.\n\nПочніть з офіційної послуги «Отримання відомостей персонального обліку»." % cycle["id"],
                    parent=win,
                )

            def mark_received():
                cycle = ensure_cycle()
                con = core.db()
                try:
                    diia.mark_data_received(con, cycle["id"])
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showwarning("Звіряння через Дію", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh()

            def mark_updates():
                cycle = ensure_cycle()
                note = simpledialog.askstring(
                    "Актуалізація",
                    "Необов'язкова примітка (наприклад «розбіжностей немає» або «заяви опрацьовано»):",
                    parent=win,
                )
                if note is None:
                    return
                con = core.db()
                try:
                    diia.mark_updates_completed(con, cycle["id"], note=note)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showwarning("Звіряння через Дію", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh()

            def record_fixation():
                cycle = ensure_cycle()
                day_text = simpledialog.askstring(
                    "Фактична фіксація в Дії",
                    "Дата успішної фіксації в Дії (ДД.ММ.РРРР):",
                    initialvalue=date.today().strftime("%d.%m.%Y"),
                    parent=win,
                )
                if day_text is None:
                    return
                reference = simpledialog.askstring(
                    "Фактична фіксація в Дії",
                    "Номер/реквізит заяви або підтвердження (якщо є):",
                    parent=win,
                )
                if reference is None:
                    return
                result = simpledialog.askstring(
                    "Фактична фіксація в Дії",
                    "Короткий фактичний результат (наприклад «успішно зафіксовано, PDF отримано»):",
                    parent=win,
                )
                if result is None:
                    return
                try:
                    fixation_day = _parse_user_day(day_text)
                except ValueError as exc:
                    core.messagebox.showerror("Дата", str(exc), parent=win)
                    return
                if not core.messagebox.askyesno(
                    "Підтвердити фактичне завершення",
                    "Підтверджуєте, що фіксацію вже реально завершено в офіційному сервісі Дії?\n\n"
                    "Taxo не може перевірити це автоматично і лише запише повідомлений вами факт.",
                    parent=win,
                ):
                    return
                con = core.db()
                try:
                    diia.record_external_fixation(
                        con,
                        cycle["id"],
                        fixation_day,
                        reference=reference,
                        result=result,
                    )
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Звіряння через Дію", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh()
                core.messagebox.showinfo(
                    "Звіряння через Дію",
                    "Фактичний результат записано в офіційний журнал Taxo.",
                    parent=win,
                )

            core.ttk.Button(
                action_bar, text="Почати / продовжити цикл", command=start_or_resume
            ).pack(side="left")
            core.ttk.Button(
                action_bar, text="Відомості отримано й імпортовано", command=mark_received
            ).pack(side="left", padx=5)
            core.ttk.Button(
                action_bar, text="Актуалізації завершено / не потрібні", command=mark_updates
            ).pack(side="left", padx=5)
            core.ttk.Button(
                action_bar, text="Записати результат фіксації", style="Accent.TButton", command=record_fixation
            ).pack(side="left", padx=5)

            footer = core.ttk.Frame(body)
            footer.pack(fill="x", pady=(2, 0))
            core.ttk.Button(
                footer,
                text="Журнал фактичних звірянь",
                command=self.open_official_reconciliation_log,
            ).pack(side="left")
            core.ttk.Button(footer, text="Оновити", command=refresh).pack(side="left", padx=6)
            core.ttk.Button(footer, text="Закрити", command=win.destroy).pack(side="right")

            refresh()
            win.transient(self)

    core._TAXO_1057_INSTALLED = True
    core.App = Taxo1057App
    return Taxo1057App
