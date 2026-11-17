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
        edit_assignment_by_id,
        focus_assignments,
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
            selectmode="extended",
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
            text="Прибрати вибрані пари",
            command=self._remove_selected_pairs,
        ).pack(side="left", padx=6)
        self.core.ttk.Button(
            controls,
            text="Очистити підготовлені пари",
            command=self._clear_staged_pairs,
        ).pack(side="left")

        self.assignment_count_var.set("Підготовлено пар: 0.")
        self.core.ttk.Label(
            self.box,
            text=(
                "Пари, які реально підуть у наказ, показані в таблиці вище. "
                "Виберіть рівно один ТЗ і одного або кількох водіїв, натисніть "
                "«Додати вибране як пари», потім повторіть для іншого ТЗ. "
                "Taxo не групує два незалежні списки автоматично."
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
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(8, 2),
        )
        self.box.columnconfigure(0, weight=1)

        self.core.ttk.Label(
            self.box,
            text="Поточні закріплення: %d" % len(assignments),
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

        self.existing_assignment_ids = [int(item["id"]) for item in assignments]
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
        bulk_button = self.core.ttk.Button(
            buttons,
            text="Додати пари…",
            command=lambda: self._open_existing_assignment_manager(True),
        )
        bulk_button.pack(side="left", padx=6)
        manage_button = self.core.ttk.Button(
            buttons,
            text="Відкрити всі пари…",
            command=lambda: self._open_existing_assignment_manager(False),
        )
        manage_button.pack(side="left", padx=6)
        tree.bind("<Double-1>", lambda _event: self._edit_existing_pair(tree))

        self.core.ttk.Label(
            self.box,
            text=(
                "Закріплення є частиною цього наказу. Тут видно поточний перелік; "
                "Виберіть рядок і натисніть «Редагувати вибрану пару…». "
                "«Додати пари…» відкриє додавання для цього наказу. "
                "«Відкрити всі пари…» відкриє повний список з діями «Прибрати»."
            ),
            style="Muted.TLabel",
            wraplength=700,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.dialog._taxo_existing_assignment_tree = tree
        self.dialog._taxo_existing_assignment_edit_button = edit_button
        self.dialog._taxo_existing_assignment_bulk_button = bulk_button
        self.dialog._taxo_existing_assignment_manage_button = manage_button

    def _confirm_leave_existing_order(self):
        return self.core.messagebox.askyesno(
            "Перейти до пар цього наказу?",
            "Відкриється окрема форма пар. Незбережені зміни тексту наказу "
            "не будуть записані. Продовжити?",
            parent=self.dialog,
        )

    def _edit_existing_pair(self, tree):
        selected = tree.selection()
        if not selected:
            self.core.messagebox.showinfo(
                "Пари цього наказу",
                "Спочатку виберіть конкретну пару в таблиці. "
                "Можна також двічі клацнути її рядок.",
                parent=self.dialog,
            )
            return
        if not self._confirm_leave_existing_order():
            return
        assignment_id = int(selected[0])
        self.dialog.destroy()
        self.book.select(self.assignments_tab)
        self.refresh_assignments()
        self.owner_window.after_idle(
            lambda: self.edit_assignment_by_id(assignment_id)
        )

    def _open_existing_assignment_manager(self, open_bulk=False):
        if not self._confirm_leave_existing_order():
            return
        self.dialog.destroy()
        self.book.select(self.assignments_tab)
        self.refresh_assignments()
        action = self.add_assignments_bulk if open_bulk else self.focus_assignments
        self.owner_window.after_idle(action)

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
