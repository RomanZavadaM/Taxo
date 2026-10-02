# -*- coding: utf-8 -*-
"""Taxo 10.6-r2 — нерегулярні шляхівки без обов'язкового каталожного маршруту.

Регулярний маршрут і надалі проходить повну route/stops validation. Якщо день
водія не має ``route_id``, стандартна кнопка видачі шляхівки відкриває окремий
сценарій нерегулярної поїздки: замовлення, розвозка, по місту, по області,
міжобласна або інша разова робота. Час береться з плану дня; факт і тахограф
не переписуються. Автобус, якщо він ще не прив'язаний до дня, можна вибрати
безпосередньо під час видачі шляхівки.
"""
from __future__ import annotations

from v1059_features import OFF_ROUTE_DEFAULT_LABEL, normalize_off_route_label

APP_VERSION = "10.6-r2"
NONREGULAR_ACTION_LABEL = "Інша поїздка / замовлення…"


def is_nonregular_waybill_candidate(row):
    """День без каталожного route_id не повинен вимагати регулярний маршрут."""
    return bool(row) and not row.get("route_id")


def vehicle_choice_label(vehicle):
    """Людинозрозумілий підпис автобуса для списку вибору."""
    if not vehicle:
        return ""
    make_model = str(vehicle.get("make_model") or "").strip()
    name = str(vehicle.get("name") or "").strip()
    plate = str(vehicle.get("plate") or "").strip()
    garage = str(vehicle.get("garage_no") or "").strip()
    parts = []
    if make_model:
        parts.append(make_model)
    elif name:
        parts.append(name)
    if plate:
        parts.append(plate)
    if garage:
        parts.append("гар. № %s" % garage)
    return " / ".join(parts) or ("ТЗ #%s" % vehicle.get("id"))


def install(core, base_app):
    if getattr(core, "_TAXO_1062_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1062App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        # ------------------------------------------------------------------
        # Waybills: regular route != mandatory for every bus trip.
        # ------------------------------------------------------------------
        def _nonregular_vehicle_choices(self, current_vehicle_id=None):
            con = core.db()
            columns = {r[1] for r in con.execute("PRAGMA table_info(vehicles)").fetchall()}
            extra = ",garage_no" if "garage_no" in columns else ""
            params = []
            where = "COALESCE(active,1)=1"
            if current_vehicle_id:
                where += " OR id=?"
                params.append(int(current_vehicle_id))
            rows = con.execute(
                "SELECT id,name,plate,make_model,active%s FROM vehicles WHERE %s "
                "ORDER BY COALESCE(active,1) DESC, name, plate, id" % (extra, where),
                params,
            ).fetchall()
            con.close()
            return [dict(r) for r in rows]

        def _nonregular_waybill_dialog(self, row):
            parent = getattr(self, "waybill_win", self)
            choices = self._nonregular_vehicle_choices(row.get("vehicle_id"))
            if not choices:
                core.messagebox.showerror(
                    "Шляхівка — нерегулярна поїздка",
                    "У реєстрі немає активного автобуса. Спочатку додайте або активуйте транспортний засіб.",
                    parent=parent,
                )
                return None

            win = core.tk.Toplevel(parent)
            win.title("Шляхівка — нерегулярна поїздка")
            try:
                core.configure_toplevel(win)
            except Exception:
                pass
            try:
                core.fit_window_to_screen(win, 640, 330, 540, 280)
            except Exception:
                win.geometry("640x330")
            try:
                win.transient(parent)
                win.grab_set()
            except Exception:
                pass

            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)
            body.columnconfigure(1, weight=1)

            core.ttk.Label(
                body,
                text="Нерегулярна поїздка / замовлення",
                font=("TkDefaultFont", 12, "bold"),
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
            core.ttk.Label(
                body,
                text=(
                    "Регулярний маршрут не потрібен. Час виїзду/повернення береться з графіка водія; "
                    "зворотний бік не заповнюється маршрутним розкладом."
                ),
                wraplength=590,
                justify="left",
                foreground=core.PALETTE["muted"],
            ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

            initial_label = self._saved_off_route_label(row)
            if not initial_label:
                # Legacy/free-text day descriptions are useful, but the normal default is "по області".
                initial_label = normalize_off_route_label(row.get("route") or "") or OFF_ROUTE_DEFAULT_LABEL
            trip_var = core.tk.StringVar(value=initial_label)
            core.ttk.Label(body, text="Поїздка / замовник:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
            trip_entry = core.ttk.Entry(body, textvariable=trip_var)
            trip_entry.grid(row=2, column=1, sticky="ew", pady=5)

            labels = [vehicle_choice_label(v) for v in choices]
            label_to_vehicle = {label: vehicle for label, vehicle in zip(labels, choices)}
            current_label = ""
            current_id = row.get("vehicle_id")
            if current_id:
                for label, vehicle in label_to_vehicle.items():
                    if int(vehicle.get("id") or 0) == int(current_id):
                        current_label = label
                        break
            if not current_label and labels:
                current_label = labels[0]
            vehicle_var = core.tk.StringVar(value=current_label)
            core.ttk.Label(body, text="Автобус:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
            combo = core.ttk.Combobox(body, textvariable=vehicle_var, values=labels, state="readonly")
            combo.grid(row=3, column=1, sticky="ew", pady=5)

            core.ttk.Label(
                body,
                text=(
                    "Приклади: «по області», «по місту», «міжобласна поїздка», "
                    "«розвозка», «замовлення Львів — ...». Поле можна редагувати довільно."
                ),
                wraplength=590,
                justify="left",
                foreground=core.PALETTE["muted"],
            ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 8))

            result = {"value": None}

            def accept():
                label = normalize_off_route_label(trip_var.get())
                vehicle = label_to_vehicle.get(vehicle_var.get())
                if not label:
                    core.messagebox.showwarning(
                        "Шляхівка — нерегулярна поїздка",
                        "Вкажіть короткий опис поїздки або замовника.",
                        parent=win,
                    )
                    return
                if vehicle is None:
                    core.messagebox.showwarning(
                        "Шляхівка — нерегулярна поїздка",
                        "Виберіть автобус.",
                        parent=win,
                    )
                    return
                result["value"] = (label, vehicle)
                win.destroy()

            buttons = core.ttk.Frame(body)
            buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(8, 0))
            core.ttk.Button(buttons, text="Скасувати", command=win.destroy).pack(side="right", padx=(8, 0))
            core.ttk.Button(buttons, text="Сформувати шляхівку", style="Accent.TButton", command=accept).pack(side="right")
            win.protocol("WM_DELETE_WINDOW", win.destroy)
            trip_entry.focus_set()
            win.wait_window()
            return result["value"]

        def _bind_nonregular_vehicle_to_day(self, row, vehicle):
            vehicle_id = int(vehicle["id"])
            label = vehicle_choice_label(vehicle)
            con = core.db()
            # Це планове призначення автобуса на день, не фактичний тахографічний запис.
            con.execute(
                "UPDATE worklog SET vehicle_id=?, vehicle=? WHERE id=?",
                (vehicle_id, label, int(row["worklog_id"])),
            )
            con.commit()
            con.close()
            row["vehicle_id"] = vehicle_id
            row["vehicle"] = label
            row["vehicle_garage_no"] = str(vehicle.get("garage_no") or "")

        def issue_selected_nonregular_waybill(self, row=None):
            row = row or self._selected_waybill_data()
            if not row:
                core.messagebox.showinfo(
                    "Шляхівка — нерегулярна поїздка",
                    "Виберіть водія / робочий день у списку.",
                    parent=getattr(self, "waybill_win", self),
                )
                return
            if not row.get("planned_departure") or not row.get("planned_return"):
                core.messagebox.showwarning(
                    "Шляхівка — нерегулярна поїздка",
                    "У графіку немає планового часу початку/закінчення роботи. Для шляхівки потрібні часові межі графіка.",
                    parent=getattr(self, "waybill_win", self),
                )
                return
            picked = self._nonregular_waybill_dialog(row)
            if not picked:
                return
            route_label, vehicle = picked
            if int(row.get("vehicle_id") or 0) != int(vehicle["id"]):
                self._bind_nonregular_vehicle_to_day(row, vehicle)
            return self._issue_off_route_waybill(row, route_label)

        def issue_selected_off_route_waybill(self):
            # Compatibility alias for the 10.5-r9 action name.
            return self.issue_selected_nonregular_waybill()

        def issue_selected_waybill(self):
            row = self._selected_waybill_data()
            if is_nonregular_waybill_candidate(row):
                return self.issue_selected_nonregular_waybill(row)
            # A real catalog route keeps the old strict route/stops validation.
            return super().issue_selected_waybill()

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
                text=NONREGULAR_ACTION_LABEL,
                command=self.issue_selected_nonregular_waybill,
            ).pack(side="left", padx=(0, 8))
            core.ttk.Label(
                bar,
                text=(
                    "Замовлення, розвозка, по місту/області, міжобласна або інша разова поїздка: "
                    "час — з графіка; автобус можна вибрати тут; опис редагується; зворотний бік без маршрутного розкладу."
                ),
                foreground=core.PALETTE["muted"],
                wraplength=860,
                justify="left",
            ).pack(side="left", fill="x", expand=True)
            self._off_route_waybill_bar = bar

        # ------------------------------------------------------------------
        # About window: keep the bottom action visible on scaled/small screens.
        # ------------------------------------------------------------------
        def _compact_about_layout(self, win):
            if win is None:
                return
            try:
                win.resizable(True, True)
                direct = list(win.winfo_children())
                canvases = [w for w in direct if w.winfo_class() == "Canvas"]
                if canvases:
                    canvases[0].configure(height=82)

                def texts(widget):
                    found = []
                    stack = [widget]
                    while stack:
                        current = stack.pop()
                        try:
                            text = str(current.cget("text") or "")
                        except Exception:
                            text = ""
                        if text:
                            found.append(text)
                        try:
                            stack.extend(current.winfo_children())
                        except Exception:
                            pass
                    return found

                frames = [w for w in direct if w.winfo_class() == "TFrame"]
                footer = None
                for frame in frames:
                    if "Закрити" in texts(frame):
                        footer = frame
                        break
                for frame in frames:
                    if frame is footer:
                        frame.configure(padding=(12, 4, 12, 6))
                    else:
                        try:
                            frame.configure(padding=10)
                        except Exception:
                            pass

                win.update_idletasks()
                available = max(520, win.winfo_screenheight() - 70)
                if win.winfo_reqheight() > available:
                    if canvases:
                        canvases[0].configure(height=72)
                    for frame in frames:
                        if frame is footer:
                            frame.configure(padding=(8, 2, 8, 4))
                        else:
                            try:
                                frame.configure(padding=8)
                            except Exception:
                                pass
                    win.update_idletasks()
                current_w = max(760, win.winfo_width(), win.winfo_reqwidth())
                current_h = min(max(540, win.winfo_reqheight()), available)
                current_w = min(current_w, max(760, win.winfo_screenwidth() - 40))
                win.geometry("%dx%d" % (current_w, current_h))
            except Exception:
                # Layout hardening must never break About itself.
                return

        def show_about(self):
            result = super().show_about()
            self._compact_about_layout(getattr(self, "_about_win", None))
            return result

    Taxo1062App.__name__ = "App"
    Taxo1062App.__qualname__ = "App"
    core._TAXO_1062_INSTALLED = True
    core.App = Taxo1062App
    return Taxo1062App
