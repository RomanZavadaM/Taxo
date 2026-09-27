# -*- coding: utf-8 -*-
"""Taxo 10.5-r4 — lossless personnel state-registry UI."""
from __future__ import annotations

import personnel_registry as registry
import personnel_registry_lossless as lossless
from v1045_features import _alive, _configure_window, _find_button, _selected_employee_id

APP_VERSION = "10.5-r4"


def install(core, base_app):
    if getattr(core, "_TAXO_1054_INSTALLED", False):
        return core.App

    # Patch before base App.__init__ so all earlier personnel screens use the
    # extended schema/parser and the new registry_note label immediately.
    lossless.install(registry)
    core.APP_VERSION = APP_VERSION

    class Taxo1054App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            registry.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_lossless_registry_action()

        def _install_lossless_registry_action(self):
            root = getattr(self, "personnel_overview_page", None)
            if not _alive(root) or getattr(self, "_lossless_registry_action_installed", False):
                return
            anchor = _find_button(root, "Реєстр документів") or _find_button(root, "Дані та документи…")
            if anchor is None:
                return
            core.ttk.Button(
                anchor.master,
                text="Оригінал держреєстру",
                command=self.open_employee_registry_raw_snapshot,
            ).pack(side="right", padx=(8, 0))
            self._lossless_registry_action_installed = True

        def open_employee_registry_raw_snapshot(self):
            employee_id = _selected_employee_id(self)
            if employee_id is None:
                core.messagebox.showinfo("Держреєстр", "Виберіть працівника у реєстрі.", parent=self)
                return
            con = core.db()
            try:
                employee, military = registry.employee_profile(con, employee_id)
                rows = lossless.latest_raw_snapshot(con, employee_id)
            finally:
                con.close()
            if employee is None:
                core.messagebox.showerror("Держреєстр", "Картку працівника не знайдено.", parent=self)
                return
            name = " ".join(x for x in (employee["last_name"], employee["first_name"], employee["middle_name"]) if x)

            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Оригінал державного витягу — " + name, 1240, 720)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Оригінал державного витягу — " + name, style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=("Це lossless-знімок останнього імпорту. Він показує буквально те, що було у XLSX. "
                      "Значення з помилковим/службовим форматом зберігаються тут, але не переносяться у робочі паспортні поля. "
                      "Порожнє поле нового витягу не очищає дані Taxo."),
                style="Muted.TLabel", wraplength=1170, justify="left",
            ).pack(anchor="w", pady=(4, 10))

            if not rows:
                core.ttk.Label(
                    body,
                    text=("Для цього працівника ще немає lossless-знімка. Старі імпорти не переписуються заднім числом. "
                          "Завантажте свіжий державний XLSX — наступна звірка збереже всі його колонки."),
                    wraplength=1100, justify="left",
                ).pack(anchor="w", pady=20)
                core.ttk.Button(body, text="Закрити", command=win.destroy).pack(anchor="e", pady=(12, 0))
                win.transient(self)
                return

            first = rows[0]
            core.ttk.Label(
                body,
                text="Джерело: %s  ·  імпорт: %s  ·  рядок XLSX: %s" % (
                    first["source_name"] or first["source_kind"], first["imported_at"], first["source_row"] or "—"
                ),
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(0, 8))

            frame = core.ttk.Frame(body)
            frame.pack(fill="both", expand=True)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            cols = ("header", "raw", "mapping", "canonical", "status", "note")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings")
            for key, label, width in (
                ("header", "Колонка державного XLSX", 300),
                ("raw", "Оригінальне значення", 310),
                ("mapping", "Поле Taxo", 190),
                ("canonical", "Перенесене значення", 220),
                ("status", "Стан перенесення", 210),
                ("note", "Пояснення", 340),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")

            tree.tag_configure(lossless.STATUS_MAPPED, foreground="#0B5D1E")
            tree.tag_configure(lossless.STATUS_REJECTED, foreground="#8A1C1C")
            tree.tag_configure(lossless.STATUS_IDENTITY, foreground="#365A7A")
            tree.tag_configure(lossless.STATUS_BLANK, foreground="#777777")
            tree.tag_configure(lossless.STATUS_SOURCE_ONLY, foreground="#7A5B00")

            for row in rows:
                mapping = "—"
                if row["canonical_scope"] and row["canonical_field"]:
                    if row["canonical_scope"] == "personal":
                        mapping = registry.EMPLOYEE_FIELD_LABELS.get(row["canonical_field"], row["canonical_field"])
                    elif row["canonical_scope"] == "military":
                        mapping = registry.MILITARY_FIELD_LABELS.get(row["canonical_field"], row["canonical_field"])
                    else:
                        mapping = row["canonical_field"]
                tree.insert(
                    "", "end",
                    values=(
                        row["source_header"], row["raw_value"] or "—", mapping,
                        row["canonical_value"] or "—",
                        lossless.STATUS_LABELS.get(row["transfer_status"], row["transfer_status"]),
                        row["transfer_note"] or "—",
                    ),
                    tags=(row["transfer_status"],),
                )

            foot = core.ttk.Frame(body)
            foot.pack(fill="x", pady=(8, 0))
            core.ttk.Label(
                foot,
                text="Червоне = значення є у витягу, але воно не пройшло перевірку формату і не забруднило робоче поле Taxo.",
                style="Muted.TLabel",
            ).pack(side="left")
            core.ttk.Button(foot, text="Закрити", command=win.destroy).pack(side="right")
            win.transient(self)

    Taxo1054App.__name__ = "App"
    Taxo1054App.__qualname__ = "App"
    core.App = Taxo1054App
    core._TAXO_1054_INSTALLED = True
    return Taxo1054App
