# -*- coding: utf-8 -*-
"""Executable registry of critical Taxo user-facing function routes.

A feature is considered preserved only when its user route remains reachable,
not merely when its implementation method still exists.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionRoute:
    function_id: str
    area: str
    action_label: str
    callback: str
    required: bool = True
    runtime_smoke: bool = False


FUNCTION_ROUTES = (
    FunctionRoute("personnel.data_center", "Працівники", "Дані / Дія / документи…", "open_personnel_data_center_r6", runtime_smoke=True),
    FunctionRoute("personnel.simple_month_schedule", "Працівники → Планування", "Простий місячний графік…", "open_simple_month_schedule_r8", runtime_smoke=True),
    FunctionRoute("personnel.document_control", "Дані / Дія / документи", "Контроль обов'язкових документів…", "open_required_employee_documents_r7"),
    FunctionRoute("personnel.registry_bulk", "Дані / Дія / документи", "Масові дії з останнього імпорту…", "open_personnel_registry_bulk_actions_r6"),
    FunctionRoute("personnel.diia_cycle", "Дані / Дія / документи", "Офіційний цикл Дії…", "open_diia_reconciliation_cycle"),
    FunctionRoute("personnel.military", "Дані / Дія / документи", "Військовий облік / строки…", "open_military_accounting_overview"),
    FunctionRoute("personnel.bulk_replan", "Працівники → Планування", "Перепланувати: замінити існуючий ПЛАН", "show_general_personnel_shift_planner"),
    FunctionRoute("drivers.report_selection", "Графіки", "Водії для звіту…", "choose_monthly_shift_report_drivers"),
    FunctionRoute("timesheet.plan_to_fact", "Табель", "План → факт", "show_employee_timesheet"),
    FunctionRoute("vehicles.core", "Транспорт", "Картка транспортного засобу", "vehicle_core_toolbar", runtime_smoke=True),
    FunctionRoute("vehicles.military", "Транспорт", "Військово-транспортний облік", "open_military_transport_dashboard", runtime_smoke=True),
    FunctionRoute("vehicles.military.statement", "Військово-транспортний облік", "Відомість (додаток 1)", "open_military_transport_statement"),
    FunctionRoute("operations.center", "Ліве меню", "Експлуатація", "open_operations_center", runtime_smoke=True),
    FunctionRoute("maintenance.stoir", "Ліве меню", "СТОІР", "open_vehicle_maintenance", runtime_smoke=True),
    FunctionRoute("documents.center", "Експлуатація → Документи", "Документи підприємства", "DOCUMENT_CENTER_GROUPS"),
    FunctionRoute("waybills.actions", "Шляхові листи", "Повна панель дій", "WAYBILL_ACTION_LABELS"),
    FunctionRoute("tachograph.main", "Ліве меню", "Тахограф", "tab_tacho"),
    FunctionRoute("reports.home", "Ліве меню", "Звіти", "show_reports_home"),
    FunctionRoute("settings.main", "Ліве меню", "Налаштування", "tab_company"),
)


def validate_routes(routes=FUNCTION_ROUTES):
    ids = [route.function_id for route in routes]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate function_id in Taxo function registry")
    required = [route for route in routes if route.required]
    if not required:
        raise RuntimeError("Taxo function registry contains no required routes")
    for route in routes:
        if not route.function_id or not route.action_label or not route.callback:
            raise RuntimeError("Incomplete Taxo function route: %r" % (route,))
    return True


def required_route_ids(routes=FUNCTION_ROUTES):
    return tuple(route.function_id for route in routes if route.required)
