# -*- coding: utf-8 -*-
"""Taxo 10.6-r3 — збереження операційних полів нерегулярної шляхівки.

10.5-r9 навмисно очищав увесь динамічний зворот нерегулярної шляхівки разом
із таблицями регулярного маршруту. Після розширення сценарію у 10.6-r2 це
виявилось занадто грубо: лікар, механік і вже внесені показники спідометра є
реквізитами конкретного випуску автобуса, а не регулярного маршруту.

Поточний шар очищає тільки route-only частину звороту (напрямок і таблиці
зупинок). Усі операційні реквізити, які вже є у payload, проходять у PDF без
підміни плану фактом. Історичний helper r9 не змінюється.
"""
from __future__ import annotations

import v1059_features as r9

APP_VERSION = "10.6-r3"

ROUTE_ONLY_REVERSE_FIELDS = (
    "start_direction",
    "outbound_stops",
    "return_stops",
)

# Поля, які мають пережити адаптацію нерегулярної шляхівки, якщо значення вже
# отримане з чинних джерел Taxo. Цей перелік також є regression-contract для
# аудиту решти заповнюваних реквізитів.
PRESERVED_OPERATIONAL_FIELDS = (
    "company_name",
    "company_address",
    "company_phone",
    "company_fax",
    "company_email",
    "waybill_no",
    "waybill_series",
    "date",
    "work_date",
    "driver",
    "driver_personnel_no",
    "vehicle",
    "transport_column",
    "brigade",
    "planned_departure",
    "planned_return",
    "planned_route_time",
    "planned_duty_time",
    "doctor_1",
    "doctor_2",
    "mechanic_1",
    "mechanic_2",
    "odometer_start",
    "odometer_end",
    "distance_km",
)


def prepare_nonregular_reverse_payload(payload):
    """Прибрати лише дані регулярного маршрутного розкладу зі звороту.

    Лікар/механік, спідометр і фактичний пробіг не є route-only даними, тому
    вони не очищаються. ``planned_distance_km`` тут спеціально не чіпаємо:
    для нерегулярної поїздки r9/r2 вже прибирає каталожний план кілометрів на
    етапі підготовки рядка, а цей helper не повинен затирати інші джерела.
    """
    prepared = dict(payload or {})
    prepared["start_direction"] = ""
    prepared["outbound_stops"] = []
    prepared["return_stops"] = []
    return prepared


def install(core, base_app):
    if getattr(core, "_TAXO_1063_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1063App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def _issue_off_route_waybill(self, row, route_label):
            """Використати issuer r9/r2, але не знищувати операційний зворот."""
            historical_sanitizer = r9.prepare_blank_reverse_payload
            r9.prepare_blank_reverse_payload = prepare_nonregular_reverse_payload
            try:
                return super()._issue_off_route_waybill(row, route_label)
            finally:
                r9.prepare_blank_reverse_payload = historical_sanitizer

    Taxo1063App.__name__ = "App"
    Taxo1063App.__qualname__ = "App"
    core._TAXO_1063_INSTALLED = True
    core.App = Taxo1063App
    return Taxo1063App
