# -*- coding: utf-8 -*-
"""Taxo 10.8-r2 — runtime UI functionality contracts.

This layer does not change business data.  It records the critical interface
surfaces that must stay reachable and provides small runtime helpers used by
headless Tk smoke tests.  The goal is to catch a feature that still exists in
code but becomes invisible after later UI layers are composed.
"""
from __future__ import annotations

APP_VERSION = "10.8-r2"

CRITICAL_UI_CONTRACT = {
    "vehicle_core": (
        "Нове авто",
        "Редагувати",
        "Документи ТЗ",
        "Контроль документів",
        "Вивести з експлуатації",
        "Оновити",
    ),
    "vehicle_documents": (
        "Додати документ",
        "Редагувати",
        "Архівувати",
        "Відкрити копію",
        "Оновити",
        "Показувати архів",
    ),
    "navigation": (
        "Працівники",
        "Табель обліку",
        "Графіки",
        "Транспорт",
        "Експлуатація",
        "Маршрути",
        "Документи",
        "Тахограф",
        "Звіти",
        "Налаштування",
    ),
}


def widget_text(widget):
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def walk_widgets(widget):
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        yield child
        yield from walk_widgets(child)


def visible_texts(widget):
    """Return mapped widget texts under *widget* in display order where possible."""
    result = []
    for child in walk_widgets(widget):
        text = widget_text(child)
        if not text:
            continue
        try:
            mapped = bool(child.winfo_ismapped())
        except Exception:
            mapped = False
        if mapped:
            result.append(text)
    return tuple(result)


def missing_contract_labels(actual, required):
    present = set(actual)
    return tuple(label for label in required if label not in present)


def install(core, base_app):
    if getattr(core, "_TAXO_1082_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1082App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            try:
                self.title("Taxo %s — Працівники, графіки та шляхівки" % APP_VERSION)
            except Exception:
                pass

    Taxo1082App.__name__ = "App"
    Taxo1082App.__qualname__ = "App"
    core._TAXO_1082_INSTALLED = True
    core.App = Taxo1082App
    return Taxo1082App
