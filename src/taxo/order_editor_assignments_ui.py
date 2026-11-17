# -*- coding: utf-8 -*-
"""Driver/vehicle assignment controls for the operations order editor.

The general order form delegates assignment-specific UI state to this module.
Order persistence remains in order_editor_persistence.py and the existing
operations_orders API.
"""
from __future__ import annotations


class OrderEditorAssignmentSection:
    """Own assignment controls without owning order persistence."""

    def __init__(
        self,
        *,
        core,
        ops,
        dialog,
        frame,
        existing,
        initial_type,
        owner_window,
        book,
        assignments_tab,
        refresh_assignments,
        add_assignments_bulk,
        edit_assignment_by_id=None,
        focus_assignments=None,
    ):
        self.core = core
        self.ops = ops
        self.dialog = dialog
        self.frame = frame
        self.existing = existing
        self.owner_window = owner_window
        self.book = book
        self.assignments_tab = assignments_tab
        self.refresh_assignments = refresh_assignments
        self.add_assignments_bulk = add_assignments_bulk
        self.edit_assignment_by_id = edit_assignment_by_id
        self.focus_assignments = focus_assignments

        self.box = None
        self.initial_vehicles = []
        self.initial_drivers = []
        self.initial_vehicle_list = None
        self.initial_driver_list = None
        self.assignment_count_var = core.tk.StringVar(value="")
        self.staged_initial_pairs = []
        self.staged_pair_tree = None

        if existing is None:
            self._build_new_order_section()
        elif initial_type == ops.TYPE_VEHICLE_ASSIGNMENT:
            self._build_existing_order_section(existing)

    def _build_new_order_section(self):
        connection = self.core.db()
        try:
            self.initial_vehicles = list(
                self.ops.list_vehicle_choices(connection, active_only=True)
            )
            self.initial_drivers = list(
                self.ops.list_driver_choices(connection, active_only=True)
            )
        finally:
            connection.close()

        self.box = self.core.ttk.LabelFrame(
            self.frame,
            text="Закріплення в цьому наказі",
            padding=8,
        )
        self.box.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(8, 2),
        )
        self.box.columnconfigure(0, weight=1)
        self.box.columnconfigure(1, weight=1)

        left = self.core.ttk.Frame(self.box)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        right = self.core.ttk.Frame(self.box)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        self.core.ttk.Label(left, text="Транспортний засіб").pack(anchor="w")
        self.initial_vehicle_list = self.core.tk.Listbox(
            left,
            selectmode="browse",
            exportselection=False,
            height=5,
        )
        self.initial_vehicle_list.pack(fill="both", expand=True, pady=(3, 0))
        for row in self.initial_vehicles:
            self.initial_vehicle_list.insert("end", row["label"])

        self.core.ttk.Label(
            right,
            text="Водій із бази водіїв",
        ).pack(anchor="w")
        self.initial_driver_list = self.core.tk.Listbox(
            right,
            selectmode="extended",
            exportselection=False,
            height=5,
        )
        self.initial_driver_list.pack(fill="both", expand=True, pady=(3, 0))
        for row in self.initial_drivers:
            self.initial_driver_list.insert("end", row["label"])

        # Stable live-test hooks for the critical bulk assignment controls.
        # These are widget references only; no business logic depends on them.
        self.dialog._taxo_assignment_box = self.box
        self.dialog._taxo_assignment_vehicle_list = self.initial_vehicle_list
        self.dialog._taxo_assignment_driver_list = self.initial_driver_list

        self.staged_pair_tree = self.core.ttk.Treeview(
            self.box,
            columns=("vehicle", "driver"),
            show="headings",
            height=3,
            selectmode="extended",
        )
        self.staged_pair_tree.heading("vehicle", text="Підготовлений ТЗ")
        self.staged_pair_tree.heading("driver", text="Підготовлений водій")
        self.staged_pair_tree.column("vehicle", width=350, anchor="w")
        self.staged_pair_tree.column("driver", width=350, anchor="w")
        self.staged_pair_tree.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(4, 2),
        )
        self.dialog._taxo_staged_assignment_tree = self.staged_pair_tree
        self.dialog._taxo_staged_assignment_pairs = self.staged_initial_pairs
        self.staged_pair_tree.bind("<Double-1>", self._load_selected_staged_pair)

        self.initial_vehicle_list.bind(
            "<<ListboxSelect>>",
            self._update_selection_summary,
        )
        self.initial_driver_list.bind(
            "<<ListboxSelect>>",
            self._update_selection_summary,
        )

        self.core.ttk.Label(
            self.box,
            textvariable=self.assignment_count_var,
            style="Subtitle.TLabel",
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 2),
        )

        controls = self.core.ttk.Frame(self.box)
        controls.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(2, 0),
        )
        self.core.ttk.Button(
            controls,
            text="Додати вибране як пари",
            command=lambda: self._stage_current_selection(show_error=True),
        ).pack(side="left")
        self.core.ttk.Button(
            controls,
            text="Замінити вибрану пару",
            command=self._replace_selected_pair,
        ).pack(side="left", padx=6)
        self.core.ttk.Button(
            controls,
            text="Прибрати вибрані пари",
            command=self._remove_selected_pairs,
        ).pack(side="left", padx=6)
        self.core.ttk.Button(
            controls,
            text="Очистити підготовлені пари",
            command=self._clear_staged_pairs,
        ).pack(side="left")
        self.core.ttk.Button(
            controls,
            text="Взяти готові пари з наказів…",
            command=self._import_prepared_pairs,
        ).pack(side="left", padx=6)

        self.assignment_count_var.set("Підготовлено пар: 0.")
        self.core.ttk.Label(
            self.box,
            text=(
                "Пари, які реально підуть у наказ, показані в таблиці вище. "
                "Виберіть рівно один ТЗ і одного або кількох водіїв, натисніть "
                "«Додати вибране як пари», потім повторіть для іншого ТЗ. "
                "Taxo не групує два незалежні списки автоматично. "
                "Для виправлення: двічі клацніть готовий рядок, "
                "виберіть потрібний ТЗ і водія, натисніть «Замінити вибрану пару». "
                "Можна також узяти пари з раніше створених наказів."
            ),
            style="Muted.TLabel",
            wraplength=700,
            justify="left",
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(4, 0),
        )

    def _render_staged_pairs(self):
        for item_id in self.staged_pair_tree.get_children():
            self.staged_pair_tree.delete(item_id)

        vehicle_by_id = {
            int(row["id"]): row
            for row in self.initial_vehicles
        }
        driver_by_id = {
            int(row["id"]): row
            for row in self.initial_drivers
        }
        for sequence, (vehicle_id, driver_id) in enumerate(
            self.staged_initial_pairs,
            1,
        ):
            vehicle = vehicle_by_id.get(int(vehicle_id), {})
            driver = driver_by_id.get(int(driver_id), {})
            self.staged_pair_tree.insert(
                "",
                "end",
                iid=str(sequence),
                values=(
                    vehicle.get("label") or ("ТЗ #%s" % vehicle_id),
                    driver.get("label") or ("Працівник #%s" % driver_id),
                ),
            )

    def _update_selection_summary(self, _event=None):
        vehicle_count = len(self.initial_vehicle_list.curselection())
        driver_count = len(self.initial_driver_list.curselection())
        self.assignment_count_var.set(
            "Підготовлено пар: %d. Поточний вибір: ТЗ — %d; водіїв — %d."
            % (len(self.staged_initial_pairs), vehicle_count, driver_count)
        )

    def _stage_current_selection(self, _event=None, *, show_error=False):
        vehicle_ids = [
            self.initial_vehicles[int(index)]["id"]
            for index in self.initial_vehicle_list.curselection()
        ]
        driver_ids = [
            self.initial_drivers[int(index)]["id"]
            for index in self.initial_driver_list.curselection()
        ]

        if len(vehicle_ids) != 1 or not driver_ids:
            message = (
                "Для явного формування пар виберіть рівно один ТЗ і одного "
                "або кількох водіїв. Для іншого ТЗ додайте наступні пари окремо."
            )
            self.assignment_count_var.set(
                "Підготовлено пар: %d. Поточний вибір потребує уточнення."
                % len(self.staged_initial_pairs)
            )
            if show_error:
                self.core.messagebox.showerror(
                    "Наказ про закріплення",
                    message,
                    parent=self.dialog,
                )
            return None

        try:
            pairs = self.ops.build_assignment_pairs(vehicle_ids, driver_ids)
        except Exception as exc:
            self.assignment_count_var.set(
                "Підготовлено пар: %d. Поточний вибір потребує уточнення."
                % len(self.staged_initial_pairs)
            )
            if show_error:
                self.core.messagebox.showerror(
                    "Наказ про закріплення",
                    str(exc),
                    parent=self.dialog,
                )
            return None

        existing = set(self.staged_initial_pairs)
        for vehicle_id, driver_id in pairs:
            pair = (int(vehicle_id), int(driver_id))
            if pair not in existing:
                self.staged_initial_pairs.append(pair)
                existing.add(pair)

        self._render_staged_pairs()
        try:
            self.initial_vehicle_list.selection_clear(0, "end")
            self.initial_driver_list.selection_clear(0, "end")
        except Exception:
            pass
        self.assignment_count_var.set(
            "Підготовлено пар: %d. Додано для одного ТЗ: %d."
            % (len(self.staged_initial_pairs), len(pairs))
        )
        return list(self.staged_initial_pairs)

    def _selected_staged_index(self):
        selected = self.staged_pair_tree.selection()
        if len(selected) != 1:
            return None
        try:
            index = int(selected[0]) - 1
        except (TypeError, ValueError):
            return None
        return index if 0 <= index < len(self.staged_initial_pairs) else None

    def _load_selected_staged_pair(self, _event=None):
        index = self._selected_staged_index()
        if index is None:
            return
        vehicle_id, driver_id = self.staged_initial_pairs[index]
        self.initial_vehicle_list.selection_clear(0, "end")
        self.initial_driver_list.selection_clear(0, "end")
        for offset, item in enumerate(self.initial_vehicles):
            if int(item["id"]) == int(vehicle_id):
                self.initial_vehicle_list.selection_set(offset)
                self.initial_vehicle_list.see(offset)
                break
        for offset, item in enumerate(self.initial_drivers):
            if int(item["id"]) == int(driver_id):
                self.initial_driver_list.selection_set(offset)
                self.initial_driver_list.see(offset)
                break
        self.assignment_count_var.set(
            "Редагування пари №%d: змініть ТЗ або водія і натисніть «Замінити вибрану пару»."
            % (index + 1)
        )

    def _replace_selected_pair(self):
        index = self._selected_staged_index()
        if index is None:
            self.core.messagebox.showinfo(
                "Пари наказу",
                "Виберіть рівно один рядок у таблиці підготовлених пар.",
                parent=self.dialog,
            )
            return
        vehicle_selection = self.initial_vehicle_list.curselection()
        driver_selection = self.initial_driver_list.curselection()
        if len(vehicle_selection) != 1 or len(driver_selection) != 1:
            self.core.messagebox.showerror(
                "Пари наказу",
                "Для заміни виберіть один ТЗ і одного водія. "
                "Заміна не виконується, доки вибір неоднозначний.",
                parent=self.dialog,
            )
            return
        candidate = (
            int(self.initial_vehicles[int(vehicle_selection[0])]["id"]),
            int(self.initial_drivers[int(driver_selection[0])]["id"]),
        )
        if candidate in (
            pair for i, pair in enumerate(self.staged_initial_pairs) if i != index
        ):
            self.core.messagebox.showerror(
                "Пари наказу",
                "Ця пара вже додана. Зміни не збережені.",
                parent=self.dialog,
            )
            return
        self.staged_initial_pairs[index] = candidate
        self._render_staged_pairs()
        self.staged_pair_tree.selection_set(str(index + 1))
        self.staged_pair_tree.see(str(index + 1))
        self.initial_vehicle_list.selection_clear(0, "end")
        self.initial_driver_list.selection_clear(0, "end")
        self.assignment_count_var.set(
            "Пару №%d замінено. Підготовлено пар: %d."
            % (index + 1, len(self.staged_initial_pairs))
        )

    def _available_prepared_pairs(self):
        """Read exact prior order pairs; do not mutate their source orders."""
        con = self.core.db()
        try:
            sources = []
            seen = set()
            for order in self.ops.list_orders(con):
                if str(order["order_type"]) != self.ops.TYPE_VEHICLE_ASSIGNMENT:
                    continue
                if str(order["status"]) == self.ops.ORDER_CANCELLED:
                    continue
                for pair in self.ops.order_assignments(con, order["id"]):
                    key = (int(pair["vehicle_id"]), int(pair["employee_id"]))
                    if key in seen:
                        continue
                    seen.add(key)
                    sources.append((
                        key[0], key[1],
                        str(order["order_no"]), str(order["order_date"]),
                    ))
        finally:
            con.close()
        active_vehicles = {int(row["id"]) for row in self.initial_vehicles}
        active_drivers = {int(row["id"]) for row in self.initial_drivers}
        return [
            item for item in sources
            if item[0] in active_vehicles and item[1] in active_drivers
        ]

    def _merge_prepared_pairs(self, pairs):
        """Append each chosen association once; never pair independent lists."""
        existing = set(self.staged_initial_pairs)
        added = 0
        for vehicle_id, driver_id in pairs:
            pair = (int(vehicle_id), int(driver_id))
            if pair not in existing:
                self.staged_initial_pairs.append(pair)
                existing.add(pair)
                added += 1
        return added

    def _import_prepared_pairs(self):
        """Copy exact, explicitly selected existing pairs; never infer by list order."""
        available = self._available_prepared_pairs()
        active_vehicles = {int(row["id"]): row["label"] for row in self.initial_vehicles}
        active_drivers = {int(row["id"]): row["label"] for row in self.initial_drivers}
        if not available:
            self.core.messagebox.showinfo(
                "Готові пари з Експлуатації",
                "Немає доступних пар з інших наказів для активних ТЗ і водіїв. "
                "Спочатку створіть пару або перевірте статуси карток.",
                parent=self.dialog,
            )
            return
        dlg = self.core.tk.Toplevel(self.dialog)
        dlg.title("Готові пари з Експлуатації")
        try:
            self.core.configure_toplevel(dlg, title=dlg.title(), minsize=(700, 440))
        except Exception:
            dlg.geometry("860x500")
        body = self.core.ttk.Frame(dlg, padding=12)
        body.pack(fill="both", expand=True)
        self.core.ttk.Label(
            body,
            text=("Виберіть конкретні пари з раніше створених наказів. "
                  "Вони будуть лише скопійовані в таблицю нового наказу. "
                  "Дата закріплення буде датою нового наказу; оригінали не змінюються."),
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))
        filter_var = self.core.tk.StringVar(value="")
        filter_row = self.core.ttk.Frame(body)
        filter_row.pack(fill="x", pady=(0, 6))
        self.core.ttk.Label(
            filter_row, text="Пошук: наказ, ТЗ або водій"
        ).pack(side="left")
        self.core.ttk.Entry(
            filter_row, textvariable=filter_var
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))
        table_frame = self.core.ttk.Frame(body)
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table = self.core.ttk.Treeview(
            table_frame, columns=("order", "vehicle", "driver"),
            show="headings", selectmode="extended", height=12,
        )
        for key, name, width in (
            ("order", "Наказ-джерело", 170),
            ("vehicle", "ТЗ", 270),
            ("driver", "Водій", 270),
        ):
            table.heading(key, text=name)
            table.column(key, width=width, anchor="w")
        scrollbar = self.core.ttk.Scrollbar(
            table_frame, orient="vertical", command=table.yview
        )
        table.configure(yscrollcommand=scrollbar.set)
        table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        visible_count = self.core.tk.StringVar(value="")
        self.core.ttk.Label(
            body, textvariable=visible_count
        ).pack(anchor="w", pady=(4, 0))

        def filter_source_pairs(*_args):
            for item_id in table.get_children():
                table.delete(item_id)
            query = filter_var.get().strip().casefold()
            shown = 0
            for offset, (vehicle, driver, number, day) in enumerate(available):
                labels = (
                    "%s (%s)" % (number, self.ops.display_day(day)),
                    active_vehicles[vehicle],
                    active_drivers[driver],
                )
                if query and query not in " ".join(labels).casefold():
                    continue
                table.insert("", "end", iid=str(offset), values=labels)
                shown += 1
            visible_count.set("Знайдено готових пар: %d" % shown)

        filter_var.trace_add("write", filter_source_pairs)
        filter_source_pairs()
        def copy_selected():
            selected = table.selection()
            if not selected:
                self.core.messagebox.showinfo(
                    "Готові пари", "Позначте хоча б один рядок для перенесення.",
                    parent=dlg,
                )
                return
            added = self._merge_prepared_pairs(
                (available[int(item_id)][0], available[int(item_id)][1])
                for item_id in selected
            )
            self._render_staged_pairs()
            self.assignment_count_var.set(
                "Перенесено готових пар: %d. У новому наказі всього: %d."
                % (added, len(self.staged_initial_pairs))
            )
            dlg.destroy()
        bar = self.core.ttk.Frame(body)
        bar.pack(fill="x", pady=(8, 0))
        self.core.ttk.Button(bar, text="Скасувати", command=dlg.destroy).pack(side="right")
        self.core.ttk.Button(
            bar, text="Взяти вибрані пари", command=copy_selected,
        ).pack(side="right", padx=6)
        dlg.transient(self.dialog)

    def _remove_selected_pairs(self):
        selected = []
        try:
            selected = [
                int(item_id) - 1
                for item_id in self.staged_pair_tree.selection()
            ]
        except Exception:
            selected = []
        if not selected:
            self.assignment_count_var.set(
                "Підготовлено пар: %d. Виберіть рядок у таблиці для видалення."
                % len(self.staged_initial_pairs)
            )
            return
        for index in sorted(set(selected), reverse=True):
            if 0 <= index < len(self.staged_initial_pairs):
                del self.staged_initial_pairs[index]
        self._render_staged_pairs()
        self.assignment_count_var.set(
            "Підготовлено пар: %d." % len(self.staged_initial_pairs)
        )

    def _clear_staged_pairs(self):
        self.staged_initial_pairs.clear()
        try:
            self.initial_vehicle_list.selection_clear(0, "end")
            self.initial_driver_list.selection_clear(0, "end")
        except Exception:
            pass
        self._render_staged_pairs()
        self.assignment_count_var.set("Підготовлено пар: 0.")

    def _build_existing_order_section(self, existing):
        connection = self.core.db()
        try:
            assignments = self.ops.order_assignments(
                connection,
                existing["id"],
            )
        finally:
            connection.close()

        self.box = self.core.ttk.LabelFrame(
            self.frame,
            text="Водії і ТЗ цього наказу",
            padding=8,
        )
        self.box.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(8, 2),
        )
        self.box.columnconfigure(0, weight=1)

        self.existing_pair_count = self.core.tk.StringVar(
            value="Поточні закріплення: %d" % len(assignments)
        )
        self.core.ttk.Label(
            self.box,
            textvariable=self.existing_pair_count,
            style="Subtitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        tree = self.core.ttk.Treeview(
            self.box,
            columns=("vehicle", "plate", "driver"),
            show="headings",
            height=max(1, min(4, len(assignments))),
            selectmode="browse",
        )
        for key, label, width in (
            ("vehicle", "Транспортний засіб", 300),
            ("plate", "Держ. номер", 130),
            ("driver", "Водій", 320),
        ):
            tree.heading(key, text=label)
            tree.column(key, width=width, anchor="w")
        tree.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        self.existing_pair_tree = tree
        for item in assignments:
            driver_name = " ".join(
                str(item[key] or "").strip()
                for key in ("last_name", "first_name", "middle_name")
                if str(item[key] or "").strip()
            )
            tree.insert(
                "",
                "end",
                iid=str(item["id"]),
                values=(
                    item["make_model"] or item["vehicle_name"],
                    item["plate"] or "—",
                    driver_name or "—",
                ),
            )

        buttons = self.core.ttk.Frame(self.box)
        buttons.grid(row=2, column=0, sticky="ew")
        edit_button = self.core.ttk.Button(
            buttons,
            text="Редагувати вибрану пару…",
            style="Accent.TButton",
            command=lambda: self._edit_existing_pair(tree),
        )
        edit_button.pack(side="left")
        add_button = self.core.ttk.Button(
            buttons,
            text="Додати пару…",
            command=self._add_existing_pair,
        )
        add_button.pack(side="left", padx=6)
        remove_button = self.core.ttk.Button(
            buttons,
            text="Прибрати вибрану пару",
            command=self._remove_existing_pair,
        )
        remove_button.pack(side="left", padx=6)
        tree.bind("<Double-1>", lambda _event: self._edit_existing_pair(tree))

        self.core.ttk.Label(
            self.box,
            text=(
                "Закріплення є частиною цього наказу. Тут видно поточний перелік; "
                "Виберіть рядок і натисніть «Редагувати вибрану пару…». "
                "«Додати пару…» відкриє форму нової пари для цього наказу. "
                "«Прибрати вибрану пару» попросить підтвердження. "
                "Після збереження список одразу оновлюється."
            ),
            style="Muted.TLabel",
            wraplength=700,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.dialog._taxo_existing_assignment_tree = tree
        self.dialog._taxo_existing_assignment_edit_button = edit_button
        self.dialog._taxo_existing_assignment_bulk_button = add_button
        self.dialog._taxo_existing_assignment_manage_button = remove_button

    def _refresh_existing_pairs(self, focus_id=None):
        """Refresh the current order's own list without switching tabs."""
        con = self.core.db()
        try:
            assignments = self.ops.order_assignments(con, self.existing["id"])
        finally:
            con.close()
        tree = self.existing_pair_tree
        for iid in tree.get_children():
            tree.delete(iid)
        for item in assignments:
            driver_name = " ".join(
                str(item[key] or "").strip()
                for key in ("last_name", "first_name", "middle_name")
                if str(item[key] or "").strip()
            )
            tree.insert("", "end", iid=str(item["id"]), values=(
                item["make_model"] or item["vehicle_name"],
                item["plate"] or "—",
                driver_name or "—",
            ))
        self.existing_pair_count.set(
            "Поточні закріплення: %d" % len(assignments)
        )
        target = str(focus_id) if focus_id is not None else None
        if target in tree.get_children():
            tree.selection_set(target)
            tree.focus(target)
            tree.see(target)
        self.refresh_assignments()

    def _edit_existing_pair(self, tree):
        selected = tree.selection()
        if not selected:
            self.core.messagebox.showinfo(
                "Пари цього наказу",
                "Виберіть конкретний рядок, який потрібно відредагувати.",
                parent=self.dialog,
            )
            return
        self._pair_dialog(int(selected[0]))

    def _add_existing_pair(self):
        self._pair_dialog(None)

    def _pair_dialog(self, assignment_id):
        """Edit exactly one pair in its order, keeping the order form open."""
        con = self.core.db()
        try:
            existing_pair = (
                self.ops.get_vehicle_assignment(con, assignment_id)
                if assignment_id is not None else None
            )
            if assignment_id is not None and (
                existing_pair is None
                or int(existing_pair["order_id"]) != int(self.existing["id"])
            ):
                self.core.messagebox.showerror(
                    "Пари цього наказу",
                    "Вибрана пара більше не належить цьому наказу.",
                    parent=self.dialog,
                )
                return
            vehicles = list(self.ops.list_vehicle_choices(
                con, active_only=assignment_id is None
            ))
            drivers = list(self.ops.list_driver_choices(
                con, active_only=assignment_id is None
            ))
        finally:
            con.close()
        vehicle_by_label = {item["label"]: int(item["id"]) for item in vehicles}
        driver_by_label = {item["label"]: int(item["id"]) for item in drivers}
        vehicle_by_id = {int(item["id"]): item["label"] for item in vehicles}
        driver_by_id = {int(item["id"]): item["label"] for item in drivers}
        if existing_pair and (
            int(existing_pair["vehicle_id"]) not in vehicle_by_id
            or int(existing_pair["employee_id"]) not in driver_by_id
        ):
            self.core.messagebox.showerror(
                "Пари цього наказу",
                "Поточний ТЗ або водій відсутній у довіднику. "
                "Пару не змінено.",
                parent=self.dialog,
            )
            return
        dlg = self.core.tk.Toplevel(self.dialog)
        dlg.title("Редагувати пару цього наказу" if existing_pair else
                  "Додати пару до цього наказу")
        frm = self.core.ttk.Frame(dlg, padding=14)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)
        vehicle_var = self.core.tk.StringVar(value=(
            vehicle_by_id.get(int(existing_pair["vehicle_id"]), "")
            if existing_pair else ""
        ))
        driver_var = self.core.tk.StringVar(value=(
            driver_by_id.get(int(existing_pair["employee_id"]), "")
            if existing_pair else ""
        ))
        from_var = self.core.tk.StringVar(value=self.ops.display_day(
            existing_pair["valid_from"] if existing_pair else
            self.existing["order_date"]
        ))
        until_var = self.core.tk.StringVar(value=self.ops.display_day(
            existing_pair["valid_until"]
        ) if existing_pair else "")
        for row, (label, var, choices) in enumerate((
            ("Транспортний засіб", vehicle_var, list(vehicle_by_label)),
            ("Водій", driver_var, list(driver_by_label)),
            ("Діє з", from_var, None),
            ("Діє до (необов'язково)", until_var, None),
        )):
            self.core.ttk.Label(frm, text=label).grid(
                row=row, column=0, sticky="w", padx=(0, 8), pady=5
            )
            widget = (
                self.core.ttk.Combobox(
                    frm, textvariable=var, values=choices, state="readonly"
                ) if choices is not None
                else self.core.ttk.Entry(frm, textvariable=var)
            )
            widget.grid(row=row, column=1, sticky="ew", pady=5)
        self.core.ttk.Label(
            frm,
            text="Зміна цієї пари зберігається одразу в наказі. "
                 "Інші пари та незбережений текст наказу не змінюються.",
            wraplength=440, justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)

        def save_pair():
            if (vehicle_var.get() not in vehicle_by_label
                    or driver_var.get() not in driver_by_label):
                self.core.messagebox.showerror(
                    "Пара", "Виберіть ТЗ і водія.", parent=dlg
                )
                return
            con2 = self.core.db()
            try:
                pair = (vehicle_by_label[vehicle_var.get()],
                        driver_by_label[driver_var.get()])
                if existing_pair:
                    self.ops.update_vehicle_assignment(
                        con2, assignment_id, vehicle_id=pair[0],
                        employee_id=pair[1], valid_from=from_var.get(),
                        valid_until=until_var.get(),
                        history_note="Редагування пари у наказі",
                    )
                    focus_id = assignment_id
                else:
                    focus_id = self.ops.add_vehicle_assignment(
                        con2, self.existing["id"], pair[0], pair[1],
                        valid_from=from_var.get(), valid_until=until_var.get(),
                    )
                self.ops.verify_vehicle_assignment_pairs(
                    con2, self.existing["id"], [pair]
                )
                con2.commit()
            except Exception as exc:
                con2.rollback()
                self.core.messagebox.showerror("Пара", str(exc), parent=dlg)
                return
            finally:
                con2.close()
            dlg.destroy()
            self._refresh_existing_pairs(focus_id)
        bar = self.core.ttk.Frame(frm)
        bar.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.core.ttk.Button(
            bar, text="Скасувати", command=dlg.destroy
        ).pack(side="right")
        self.core.ttk.Button(
            bar, text="Зберегти пару", command=save_pair
        ).pack(side="right", padx=6)
        dlg.transient(self.dialog)

    def _remove_existing_pair(self):
        selected = self.existing_pair_tree.selection()
        if not selected:
            self.core.messagebox.showinfo(
                "Пари цього наказу",
                "Виберіть рядок пари для видалення.",
                parent=self.dialog,
            )
            return
        assignment_id = int(selected[0])
        if not self.core.messagebox.askyesno(
            "Прибрати пару?",
            "Прибрати вибрану пару з цього наказу? "
            "Інші пари залишаться без змін.",
            parent=self.dialog,
        ):
            return
        con = self.core.db()
        try:
            row = self.ops.get_vehicle_assignment(con, assignment_id)
            if row is None or int(row["order_id"]) != int(self.existing["id"]):
                raise ValueError("Пара більше не належить цьому наказу.")
            self.ops.delete_vehicle_assignment(
                con, assignment_id, history_note="Видалення пари у наказі"
            )
            con.commit()
        except Exception as exc:
            con.rollback()
            self.core.messagebox.showerror(
                "Пари цього наказу", str(exc), parent=self.dialog
            )
            return
        finally:
            con.close()
        self._refresh_existing_pairs()

    def show_for_type(self, order_type):
        """Show assignment controls only for vehicle-assignment orders."""
        if self.box is None:
            return
        if order_type == self.ops.TYPE_VEHICLE_ASSIGNMENT:
            self.box.grid()
        else:
            self.box.grid_remove()

    def initial_pairs_for_save(self, order_type):
        """Return staged pairs for persistence, or None when save must stop."""
        if (
            self.existing is not None
            or order_type != self.ops.TYPE_VEHICLE_ASSIGNMENT
            or self.box is None
        ):
            return []

        current_vehicle_ids = [
            self.initial_vehicles[int(index)]["id"]
            for index in self.initial_vehicle_list.curselection()
        ]
        current_driver_ids = [
            self.initial_drivers[int(index)]["id"]
            for index in self.initial_driver_list.curselection()
        ]
        if current_vehicle_ids or current_driver_ids:
            self.core.messagebox.showerror(
                "Наказ про закріплення",
                (
                    "Є вибір, який ще не додано до таблиці пар. Натисніть "
                    "«Додати вибране як пари», перевірте таблицю і повторіть збереження."
                ),
                parent=self.dialog,
            )
            return None

        initial_pairs = list(self.staged_initial_pairs)
        if initial_pairs:
            return initial_pairs

        if not self.core.messagebox.askyesno(
            "Порожній наказ про закріплення?",
            (
                "Жодної пари ТЗ / водій не підготовлено. "
                "Створити порожній наказ без закріплень?"
            ),
            parent=self.dialog,
        ):
            return None
        return []


def install_order_editor_assignments(**kwargs):
    """Build and return the assignment section for one order editor dialog."""
    return OrderEditorAssignmentSection(**kwargs)
