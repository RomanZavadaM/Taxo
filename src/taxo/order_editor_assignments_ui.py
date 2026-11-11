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
            selectmode="none",
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
            self._stage_current_selection,
        )
        self.initial_driver_list.bind(
            "<<ListboxSelect>>",
            self._stage_current_selection,
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
            text="Зафіксувати поточний вибір",
            command=lambda: self._stage_current_selection(show_error=True),
        ).pack(side="left")
        self.core.ttk.Button(
            controls,
            text="Очистити підготовлені пари",
            command=self._clear_staged_pairs,
        ).pack(side="left", padx=6)

        self.assignment_count_var.set("Підготовлено пар: 0.")
        self.core.ttk.Label(
            self.box,
            text=(
                "Пари, які реально підуть у наказ, показані в таблиці вище. "
                "Вибір зберігається окремо від підсвічування списків, тому не "
                "зникає при зміні фокусу. Правило: 1 ТЗ + кілька водіїв або "
                "однакова кількість ТЗ і водіїв."
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

    def _stage_current_selection(self, _event=None, *, show_error=False):
        vehicle_ids = [
            self.initial_vehicles[int(index)]["id"]
            for index in self.initial_vehicle_list.curselection()
        ]
        driver_ids = [
            self.initial_drivers[int(index)]["id"]
            for index in self.initial_driver_list.curselection()
        ]

        if not vehicle_ids and not driver_ids:
            self.assignment_count_var.set(
                "Підготовлено пар: %d. Поточне виділення порожнє."
                % len(self.staged_initial_pairs)
            )
            return list(self.staged_initial_pairs)

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

        self.staged_initial_pairs[:] = [
            (int(vehicle_id), int(driver_id))
            for vehicle_id, driver_id in pairs
        ]
        self._render_staged_pairs()
        self.assignment_count_var.set(
            "Вибрано: ТЗ — %d; водіїв — %d. Підготовлено пар: %d."
            % (
                len(vehicle_ids),
                len(driver_ids),
                len(self.staged_initial_pairs),
            )
        )
        return list(self.staged_initial_pairs)

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

        for item in assignments:
            driver_name = " ".join(
                str(item[key] or "").strip()
                for key in ("last_name", "first_name", "middle_name")
                if str(item[key] or "").strip()
            )
            tree.insert(
                "",
                "end",
                values=(
                    item["make_model"] or item["vehicle_name"],
                    item["plate"] or "—",
                    driver_name or "—",
                ),
            )

        buttons = self.core.ttk.Frame(self.box)
        buttons.grid(row=2, column=0, sticky="ew")
        bulk_button = self.core.ttk.Button(
            buttons,
            text="Додати багато…",
            style="Accent.TButton",
            command=lambda: self._open_existing_assignment_manager(True),
        )
        bulk_button.pack(side="left")
        manage_button = self.core.ttk.Button(
            buttons,
            text="Керувати закріпленнями",
            command=lambda: self._open_existing_assignment_manager(False),
        )
        manage_button.pack(side="left", padx=6)

        self.core.ttk.Label(
            self.box,
            text=(
                "Закріплення є частиною цього наказу. Тут видно поточний перелік; "
                "для додавання кількох водіїв/ТЗ натисніть «Додати багато…», "
                "для редагування або видалення окремих пар — "
                "«Керувати закріпленнями»."
            ),
            style="Muted.TLabel",
            wraplength=700,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.dialog._taxo_existing_assignment_tree = tree
        self.dialog._taxo_existing_assignment_bulk_button = bulk_button
        self.dialog._taxo_existing_assignment_manage_button = manage_button

    def _open_existing_assignment_manager(self, open_bulk=False):
        self.dialog.destroy()
        self.book.select(self.assignments_tab)
        self.refresh_assignments()
        if open_bulk:
            try:
                self.owner_window.after_idle(self.add_assignments_bulk)
            except Exception:
                self.add_assignments_bulk()

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
            staged = self._stage_current_selection(show_error=True)
            if staged is None:
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
