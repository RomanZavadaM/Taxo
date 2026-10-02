# -*- coding: utf-8 -*-
"""Taxo 10.6-r10 — P-5 exporter EDRPOU compatibility fix.

The historical 10.4-r3 wrapper only checked keyword ``edrpou``. The current
reports UI passes EDRPOU positionally, so that wrapper added a second keyword
value and Python raised ``got multiple values for argument 'edrpou'``.

This outer layer normalizes the call before invoking the original personnel
exporter. It fixes both PDF and XLSX without changing report calculations,
rows, plan/fact semantics or database data.
"""
from __future__ import annotations

import personnel_v91 as personnel
from v1043_features import company_edrpou

APP_VERSION = "10.6-r10"
EDRPOU_ARG_INDEX = 7  # self, year, month, out_path, active_only, form_date, department, edrpou


def _closure_value(func, name):
    """Read a named closure value from an older compatibility wrapper."""
    code = getattr(func, "__code__", None)
    names = getattr(code, "co_freevars", ()) if code is not None else ()
    cells = getattr(func, "__closure__", ()) or ()
    for freevar, cell in zip(names, cells):
        if freevar == name:
            try:
                return cell.cell_contents
            except ValueError:
                return None
    return None


def normalize_edrpou_call(args, kwargs, fallback):
    """Return args/kwargs with EDRPOU supplied exactly once.

    Positional input has precedence because it reflects the explicit current
    UI call. A blank positional value is replaced with the company fallback.
    When no positional slot exists, a blank/missing keyword is filled.
    """
    call_args = list(args)
    call_kwargs = dict(kwargs)
    fallback = str(fallback or "").strip()

    if len(call_args) > EDRPOU_ARG_INDEX:
        if not str(call_args[EDRPOU_ARG_INDEX] or "").strip():
            call_args[EDRPOU_ARG_INDEX] = fallback
        # Never pass the same parameter both positionally and by keyword.
        call_kwargs.pop("edrpou", None)
    else:
        if not str(call_kwargs.get("edrpou", "") or "").strip():
            call_kwargs["edrpou"] = fallback

    return tuple(call_args), call_kwargs


def _base_exporter(current, closure_name):
    """Bypass the buggy 10.4-r3 wrapper when it is still installed."""
    return _closure_value(current, closure_name) or current


def _patch_p5_exporters(core):
    if getattr(personnel, "_taxo_v10610_p5_patched", False):
        return

    current_pdf = personnel.export_p5_pdf
    current_xlsx = personnel.export_p5_xlsx
    base_pdf = _base_exporter(current_pdf, "original_p5_pdf")
    base_xlsx = _base_exporter(current_xlsx, "original_p5_xlsx")

    def export_p5_pdf(*args, **kwargs):
        call_args, call_kwargs = normalize_edrpou_call(
            args, kwargs, company_edrpou(core)
        )
        return base_pdf(*call_args, **call_kwargs)

    def export_p5_xlsx(*args, **kwargs):
        call_args, call_kwargs = normalize_edrpou_call(
            args, kwargs, company_edrpou(core)
        )
        return base_xlsx(*call_args, **call_kwargs)

    personnel.export_p5_pdf = export_p5_pdf
    personnel.export_p5_xlsx = export_p5_xlsx
    personnel._taxo_v10610_p5_patched = True
    personnel._taxo_v10610_base_p5_pdf = base_pdf
    personnel._taxo_v10610_base_p5_xlsx = base_xlsx


def install(core, base_app):
    if getattr(core, "_TAXO_10610_INSTALLED", False):
        return core.App

    _patch_p5_exporters(core)
    core.APP_VERSION = APP_VERSION

    class Taxo10610App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo10610App.__name__ = "App"
    Taxo10610App.__qualname__ = "App"
    core._TAXO_10610_INSTALLED = True
    core.App = Taxo10610App
    return Taxo10610App
