# -*- coding: utf-8 -*-
"""Taxo 10.5-r10 — коректні домени аудиту графіків.

10.4-r4 додав корисну перевірку меж маршруту, але для конкретного дня вона
порівнювала дві різні сутності:

* ``work_segments`` — збережений план конкретного дня (snapshot/ручна правка);
* ``route_stops`` — ПОТОЧНИЙ редагований шаблон маршруту.

Після перепланування дня або редагування каталогу ці два плани мають право
відрізнятися. Така різниця не доводить ані помилку введення, ані фактичне
порушення. Фактичні ``fact_work_*`` поля взагалі не повинні брати участі у
цьому порівнянні.

Тому r10 прибирає тільки ``виїзд/заїзд не збігається`` для source_kind=worklog.
Перевірка тих самих меж для source_kind=route лишається: там ``route_segments``
і ``route_stops`` належать одному актуальному шаблону і порівняння коректне.
Жодні планові чи фактичні дані цим шаром не змінюються.
"""
from __future__ import annotations

APP_VERSION = "10.5-r10"

DAY_VS_LIVE_TEMPLATE_KINDS = frozenset({
    "route_start_boundary_mismatch",
    "route_end_boundary_mismatch",
})


def separate_schedule_audit_domains(data):
    """Remove only invalid day-snapshot ↔ live-template boundary comparisons.

    The function deliberately leaves:
    - all ordinary day input-integrity findings;
    - all route-template findings, including route boundary mismatches;
    - every stored plan/fact value untouched.
    """
    result = dict(data or {})
    source = list(result.get("findings") or [])
    kept = []
    suppressed = []
    for item in source:
        if (
            item.get("source_kind") == "worklog"
            and item.get("kind") in DAY_VS_LIVE_TEMPLATE_KINDS
        ):
            suppressed.append(item)
            continue
        kept.append(item)

    result["findings"] = kept
    result["day_findings"] = sum(
        1 for item in kept if item.get("source_kind") == "worklog"
    )
    result["route_findings"] = sum(
        1 for item in kept if item.get("source_kind") == "route"
    )
    result["suppressed_day_route_boundary_findings"] = len(suppressed)
    result["audit_domain_note"] = (
        "День водія перевіряється як власний збережений план. "
        "Межі поточного шаблону маршруту перевіряються окремо в режимі "
        "«Шаблони маршрутів»; фактичні fact_work_* не підміняють план."
    )
    return result


def install(core, base_app):
    if getattr(core, "_TAXO_10510_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION
    original_audit = core.collect_schedule_integrity_audit

    def collect_schedule_integrity_audit(
        year,
        month,
        active_routes_only=True,
        work_date=None,
        include_days=True,
        include_routes=True,
    ):
        data = original_audit(
            year,
            month,
            active_routes_only=active_routes_only,
            work_date=work_date,
            include_days=include_days,
            include_routes=include_routes,
        )
        return separate_schedule_audit_domains(data)

    core.collect_schedule_integrity_audit = collect_schedule_integrity_audit

    class Taxo10510App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo10510App.__name__ = "App"
    Taxo10510App.__qualname__ = "App"
    core._TAXO_10510_INSTALLED = True
    core.App = Taxo10510App
    return Taxo10510App
