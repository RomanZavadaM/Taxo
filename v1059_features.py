# -*- coding: utf-8 -*-
"""Taxo 10.5-r9 — шляхівка для роботи поза регулярним маршрутом.

Режим не створює фіктивний маршрут у каталозі. Плановий час береться з
наявного графіка водія, а фактичний облік залишається окремим і надалі може
походити з тахографа. Для позамаршрутної роботи на лицьовій стороні друкується
редагований опис поїздки (типово «по області»), а зворотний бік не
заповнюється даними маршрутного розкладу/відміток.
"""
from __future__ import annotations

APP_VERSION = "10.5-r9"
OFF_ROUTE_DEFAULT_LABEL = "по області"
_OFF_ROUTE_VALIDATION_POINT = "поза маршрутом"


def normalize_off_route_label(value):
    """Нормалізувати введений користувачем опис позамаршрутної поїздки."""
    return " ".join(str(value or "").split())


def prepare_off_route_row(row, route_label):
    """Підготувати копію рядка графіка для існуючого issuer-а шляхівки.

    Службові точки/лічильники потрібні лише для проходження legacy validation;
    у PDF і в БД вони не зберігаються як фактичні маршрутні дані.
    """
    prepared = dict(row)
    prepared.update({
        "route": normalize_off_route_label(route_label),
        "route_id": None,
        "start_location": _OFF_ROUTE_VALIDATION_POINT,
        "end_location": _OFF_ROUTE_VALIDATION_POINT,
        "start_direction": "",
        "outbound_stop_count": 1,
        "return_stop_count": 1,
        "planned_distance_km": None,
    })
    return prepared


def prepare_off_route_front_payload(payload, route_label):
    """Лицьова сторона: свій опис поїздки, без вигаданих точок маршруту."""
    prepared = dict(payload)
    prepared["route"] = normalize_off_route_label(route_label)
    prepared["start_location"] = ""
    prepared["end_location"] = ""
    prepared["start_direction"] = ""
    prepared["outbound_stops"] = []
    prepared["return_stops"] = []
    prepared["planned_distance_km"] = None
    return prepared


def prepare_blank_reverse_payload(payload):
    """Зворотний бік позамаршрутної шляхівки лишити незаповненим даними."""
    prepared = dict(payload)
    prepared.update({
        "start_direction": "",
        "outbound_stops": [],
        "return_stops": [],
        "doctor_1": "",
        "doctor_2": "",
        "mechanic_1": "",
        "mechanic_2": "",
        "odometer_start": None,
        "odometer_end": None,
        "distance_km": None,
        "planned_distance_km": None,
    })
    return prepared


def install(core, base_app):
    if getattr(core, "_TAXO_1059_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1059App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def _waybill_schedule_rows(self, work_date):
            rows = super()._waybill_schedule_rows(work_date)
            ids = [row.get("waybill_id") for row in rows if row.get("waybill_id")]
            if not ids:
                return rows
            con = core.db()
            placeholders = ",".join("?" for _ in ids)
            saved = {
                int(r["id"]): r
                for r in con.execute(
                    "SELECT id,route_id,route_label FROM waybills WHERE id IN (%s)" % placeholders,
                    ids,
                ).fetchall()
            }
            con.close()
            for row in rows:
                wb = saved.get(int(row.get("waybill_id") or 0))
                if wb is None:
                    continue
                label = normalize_off_route_label(wb["route_label"])
                if wb["route_id"] is None and label:
                    row["route"] = label
                    row["_off_route_waybill"] = True
            return rows

        def show_waybills_for_schedule(self):
            result = super().show_waybills_for_schedule()
            self._ensure_off_route_waybill_controls()
            return result

        def _ensure_off_route_waybill_controls(self):
            win = getattr(self, "waybill_win", None)
            if win is None or not win.winfo_exists():
                return
            bar = getattr(self, "_off_route_waybill_bar", None)
            if bar is not None and bar.winfo_exists():
                return
            bar = core.ttk.Frame(win, padding=(10, 0, 10, 8))
            bar.pack(fill="x", side="bottom")
            core.ttk.Button(
                bar,
                text="Поза маршрутом…",
                command=self.issue_selected_off_route_waybill,
            ).pack(side="left", padx=(0, 8))
            core.ttk.Label(
                bar,
                text=(
                    "Для поїздки без регулярного маршруту: час — з графіка; "
                    "опис типово «по області» (можна змінити); зворотний бік не заповнюється."
                ),
                foreground=core.PALETTE["muted"],
                wraplength=820,
                justify="left",
            ).pack(side="left", fill="x", expand=True)
            self._off_route_waybill_bar = bar

        def _saved_off_route_label(self, row):
            if not row or not row.get("worklog_id"):
                return ""
            con = core.db()
            wb = con.execute(
                "SELECT route_id,route_label,status FROM waybills WHERE worklog_id=?",
                (row["worklog_id"],),
            ).fetchone()
            con.close()
            if wb is None or (wb["status"] or "active") == "void":
                return ""
            if wb["route_id"] is None:
                return normalize_off_route_label(wb["route_label"])
            return ""

        def issue_selected_off_route_waybill(self):
            row = self._selected_waybill_data()
            if not row:
                core.messagebox.showinfo(
                    "Шляхівка поза маршрутом",
                    "Виберіть водія / робочий день у списку.",
                    parent=getattr(self, "waybill_win", self),
                )
                return
            if not row.get("vehicle"):
                core.messagebox.showwarning(
                    "Шляхівка поза маршрутом",
                    "Спочатку прив'яжіть автобус до робочого дня.",
                    parent=getattr(self, "waybill_win", self),
                )
                return
            if not row.get("planned_departure") or not row.get("planned_return"):
                core.messagebox.showwarning(
                    "Шляхівка поза маршрутом",
                    "У графіку немає планового часу початку/закінчення роботи.",
                    parent=getattr(self, "waybill_win", self),
                )
                return

            initial = self._saved_off_route_label(row) or OFF_ROUTE_DEFAULT_LABEL
            label = core.simpledialog.askstring(
                "Шляхівка поза маршрутом",
                "Маршрут / замовник:\n\n"
                "Типово: «по області». Можна вказати «по місту», міжобласну поїздку "
                "або одноразовий маршрут/замовлення.",
                initialvalue=initial,
                parent=getattr(self, "waybill_win", self),
            )
            if label is None:
                return
            label = normalize_off_route_label(label)
            if not label:
                core.messagebox.showerror(
                    "Шляхівка поза маршрутом",
                    "Вкажіть опис поїздки / замовника.",
                    parent=getattr(self, "waybill_win", self),
                )
                return
            return self._issue_off_route_waybill(row, label)

        def issue_selected_waybill(self):
            row = self._selected_waybill_data()
            saved_label = self._saved_off_route_label(row) if row else ""
            if saved_label:
                return self._issue_off_route_waybill(row, saved_label)
            return super().issue_selected_waybill()

        def _issue_off_route_waybill(self, row, route_label):
            """Використати перевірений issuer/number-pool, прибравши route-only вимоги."""
            prepared = prepare_off_route_row(row, route_label)
            changed_keys = (
                "route", "route_id", "start_location", "end_location", "start_direction",
                "outbound_stop_count", "return_stop_count", "planned_distance_km",
            )
            original = {key: row.get(key) for key in changed_keys}

            con = core.db()
            before_row = con.execute(
                "SELECT id,revision,pdf_path FROM waybills WHERE worklog_id=?",
                (row["worklog_id"],),
            ).fetchone()
            before = dict(before_row) if before_row else None
            con.close()

            for key in changed_keys:
                row[key] = prepared.get(key)

            original_builder = core.build_waybill_pdf
            import waybill as waybill_module
            original_page_two = waybill_module._page_two

            def off_route_builder(template_path, out_path, payload):
                clean = prepare_off_route_front_payload(payload, route_label)
                return original_builder(template_path, out_path, clean)

            def blank_reverse_page(c, payload):
                return original_page_two(c, prepare_blank_reverse_payload(payload))

            core.build_waybill_pdf = off_route_builder
            waybill_module._page_two = blank_reverse_page
            try:
                result = super(Taxo1059App, self).issue_selected_waybill()
            finally:
                core.build_waybill_pdf = original_builder
                waybill_module._page_two = original_page_two
                for key, value in original.items():
                    row[key] = value

            con = core.db()
            after_row = con.execute(
                "SELECT id,revision,pdf_path FROM waybills WHERE worklog_id=?",
                (row["worklog_id"],),
            ).fetchone()
            after = dict(after_row) if after_row else None
            issued = bool(after) and (
                before is None
                or int(after.get("revision") or 0) != int(before.get("revision") or 0)
                or (after.get("pdf_path") or "") != (before.get("pdf_path") or "")
            )
            if issued:
                con.execute(
                    """UPDATE waybills
                          SET route_id=NULL,route_label=?,start_location='',end_location='',
                              planned_distance_km=NULL
                        WHERE worklog_id=?""",
                    (normalize_off_route_label(route_label), row["worklog_id"]),
                )
                con.commit()
            con.close()
            if issued and hasattr(self, "waybill_win") and self.waybill_win.winfo_exists():
                self.refresh_waybill_issue_list()
            return result

    Taxo1059App.__name__ = "App"
    Taxo1059App.__qualname__ = "App"
    core._TAXO_1059_INSTALLED = True
    core.App = Taxo1059App
    return Taxo1059App
