# -*- coding: utf-8 -*-
"""Координатор робочого центру «Експлуатація»."""
from __future__ import annotations

import operations_orders as ops
from driver_internship_ui import install_internship_tab
from operations_settings_ui import install_operations_settings
from order_register_ui import install_order_register
from order_type_catalog_ui import install_order_type_catalog
from safety_instructions_ui import install_instruction_tab


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def open_operations_center(app, core):
    """Відкрити центр експлуатації та зібрати його спеціалізовані модулі."""
    existing = getattr(app, "_operations_center_window", None)
    if _alive(existing):
        existing.lift()
        existing.focus_force()
        return existing

    ops.ensure_schema(core)
    win = core.tk.Toplevel(app)
    app._operations_center_window = win

    try:
        core.fit_window_to_screen(win, 1260, 780, 940, 600)
        core.configure_toplevel(
            win,
            title="Експлуатація",
            minsize=(940, 600),
        )
    except Exception:
        win.geometry("1260x780")

    win.title("Taxo / %s — Експлуатація" % app._company_name_value())

    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)

    header = core.ttk.Frame(body)
    header.pack(fill="x")
    core.ttk.Label(
        header,
        text="Експлуатація",
        style="HeroTitle.TLabel",
    ).pack(side="left")

    # Окреме вікно центру експлуатації має явний вихід,
    # незалежний від закриття головної програми.
    core.ttk.Button(
        header,
        text="Закрити",
        command=win.destroy,
    ).pack(side="right", padx=(8, 0))

    book = core.ttk.Notebook(body)

    def open_documents_catalog():
        from document_catalog_ui import open_document_catalog
        from workspace import load_workspace_root

        open_document_catalog(
            win,
            core,
            load_workspace_root(),
        )

    core.ttk.Button(
        header,
        text="Документи…",
        command=open_documents_catalog,
    ).pack(side="right", padx=(8, 0))

    core.ttk.Label(
        body,
        text=(
            "Робочий центр експлуатації: щоденні документи, технічна готовність, "
            "накази, закріплення ТЗ і відповідальні особи. Починайте з вкладки "
            "«Документи» — там зібрані найчастіші дії; реєстри нижче зберігають "
            "історію та деталі."
        ),
        style="Muted.TLabel",
        wraplength=1180,
        justify="left",
    ).pack(anchor="w", pady=(2, 8))

    book.pack(fill="both", expand=True)
    orders_tab = core.ttk.Frame(book)
    assignments_tab = core.ttk.Frame(book)
    entities_tab = core.ttk.Frame(book)
    settings_tab = core.ttk.Frame(book)
    catalog_tab = core.ttk.Frame(book)

    book.add(orders_tab, text="Накази")
    book.add(assignments_tab, text="Закріплення водіїв")
    book.add(entities_tab, text="Учасники / ТЗ")
    book.add(settings_tab, text="Відповідальні")
    book.add(catalog_tab, text="Каталог наказів")

    settings = install_operations_settings(core, settings_tab, win)

    install_instruction_tab(app, core, book)
    internship_tab = install_internship_tab(app, core, book)

    core.ttk.Button(
        header,
        text="Лист стажування…",
        command=lambda: book.select(internship_tab),
    ).pack(side="right")

    register = install_order_register(
        core,
        win,
        book,
        orders_tab,
        assignments_tab,
        entities_tab,
        settings_tab,
        catalog_tab,
        settings,
    )

    install_order_type_catalog(
        core,
        catalog_tab,
        win,
        register.order_dialog,
    )
    win._taxo_preview_catalog_order = register.preview_catalog_order
    register.refresh_orders()
    return win
