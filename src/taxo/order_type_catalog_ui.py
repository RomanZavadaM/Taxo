# -*- coding: utf-8 -*-
"""Каталог типів наказів у центрі експлуатації."""
from __future__ import annotations

import operations_orders as ops


def install_order_type_catalog(core, tab, win, order_dialog):
    """Побудувати вкладку вибору типу наказу."""
    body = core.ttk.Frame(tab, padding=14)
    body.pack(fill="both", expand=True)

    core.ttk.Label(
        body,
        text="Що потрібно оформити?",
        style="Title.TLabel",
    ).pack(anchor="w")
    core.ttk.Label(
        body,
        text=(
            "Почніть не з порожнього бланка, а з потрібної дії. "
            "Taxo підставить типову тему, вступ і редаговану заготовку пунктів. "
            "Це робоча заготовка, а не юридичне твердження: перед підписанням "
            "перевірте фактичні реквізити й зміст."
        ),
        style="Muted.TLabel",
        wraplength=1040,
        justify="left",
    ).pack(anchor="w", pady=(4, 8))

    quick = core.ttk.LabelFrame(
        body,
        text="Найчастіші дії",
        padding=8,
    )
    quick.pack(fill="x", pady=(0, 10))

    quick_types = [
        ("Закріпити ТЗ за водіями", ops.TYPE_VEHICLE_ASSIGNMENT),
        ("Організувати ТО / ремонти", ops.TYPE_MAINTENANCE_REPAIR),
    ]
    if hasattr(ops, "TYPE_RESPONSIBLE_PERSONS"):
        quick_types.append(
            ("Призначити відповідальних", ops.TYPE_RESPONSIBLE_PERSONS)
        )
    if hasattr(ops, "TYPE_VEHICLE_RELEASE_RETURN"):
        quick_types.append(
            ("Порядок випуску / повернення ТЗ", ops.TYPE_VEHICLE_RELEASE_RETURN)
        )

    for column in range(2):
        quick.columnconfigure(column, weight=1)

    for index, (label, order_type) in enumerate(quick_types):
        core.ttk.Button(
            quick,
            text=label,
            command=lambda current_type=order_type: order_dialog(
                force_type=current_type
            ),
        ).grid(
            row=index // 2,
            column=index % 2,
            sticky="ew",
            padx=(0 if index % 2 == 0 else 4, 4 if index % 2 == 1 else 0),
            pady=3,
        )

    core.ttk.Label(
        body,
        text="Повний каталог типів наказів",
        style="Subtitle.TLabel",
    ).pack(anchor="w", pady=(2, 4))

    catalog_frame = core.ttk.Frame(body)
    catalog_frame.pack(fill="both", expand=True)
    catalog_frame.rowconfigure(0, weight=1)
    catalog_frame.columnconfigure(0, weight=1)

    columns = ("group", "type", "subject")
    catalog_tree = core.ttk.Treeview(
        catalog_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )
    for key, label, width in (
        ("group", "Група", 250),
        ("type", "Тип наказу", 320),
        ("subject", "Типова тема", 430),
    ):
        catalog_tree.heading(key, text=label)
        catalog_tree.column(key, width=width, anchor="w")

    ybar = core.ttk.Scrollbar(
        catalog_frame,
        orient="vertical",
        command=catalog_tree.yview,
    )
    xbar = core.ttk.Scrollbar(
        catalog_frame,
        orient="horizontal",
        command=catalog_tree.xview,
    )
    catalog_tree.configure(
        yscrollcommand=ybar.set,
        xscrollcommand=xbar.set,
    )
    catalog_tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

    type_by_item = {}
    catalog_index = 0
    for group_key, group_label in ops.ORDER_GROUP_LABELS.items():
        for order_type in ops.ORDER_GROUP_TYPES.get(group_key, ()):
            catalog_index += 1
            item_id = str(catalog_index)
            type_by_item[item_id] = order_type
            catalog_tree.insert(
                "",
                "end",
                iid=item_id,
                values=(
                    group_label,
                    ops.ORDER_TYPE_LABELS[order_type],
                    ops.DEFAULT_SUBJECTS.get(order_type, "") or "—",
                ),
            )

    def create_from_catalog():
        selection = catalog_tree.selection()
        if not selection:
            core.messagebox.showinfo(
                "Каталог наказів",
                "Виберіть тип наказу.",
                parent=win,
            )
            return

        order_type = type_by_item.get(selection[0])
        if order_type:
            order_dialog(force_type=order_type)

    action_bar = core.ttk.Frame(body)
    action_bar.pack(fill="x", pady=(8, 0))
    core.ttk.Button(
        action_bar,
        text="Створити наказ за вибраним типом",
        style="Accent.TButton",
        command=create_from_catalog,
    ).pack(side="left")
    catalog_tree.bind("<Double-1>", lambda _event: create_from_catalog())

    return catalog_tree
