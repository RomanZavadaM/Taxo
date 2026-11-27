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
    FunctionRoute("personnel.registry_import", "Дані / Дія / документи", "Завантажити XLSX / звірити…", "import_personnel_registry_xlsx", runtime_smoke=True),
    FunctionRoute("personnel.working_data", "Дані / Дія / документи", "Робочі дані з реєстрів", "open_employee_military_working_data", runtime_smoke=True),
    FunctionRoute("personnel.card_documents", "Дані / Дія / документи", "Картка та документи", "open_personnel_data_center", runtime_smoke=True),
    FunctionRoute("personnel.document_register", "Дані / Дія / документи", "Відкрити реєстр документів", "open_employee_document_register", runtime_smoke=True),
    FunctionRoute("personnel.simple_month_schedule", "Працівники → Планування", "Простий місячний графік…", "open_simple_month_schedule_r8", runtime_smoke=True),
    FunctionRoute("personnel.document_control", "Дані / Дія / документи", "Контроль обов'язкових документів…", "open_required_employee_documents_r7", runtime_smoke=True),
    FunctionRoute("personnel.registry_bulk", "Дані / Дія / документи", "Масові дії з останнього імпорту…", "open_personnel_registry_bulk_actions_r6", runtime_smoke=True),
    FunctionRoute("personnel.diia_cycle", "Дані / Дія / документи", "Офіційний цикл Дії…", "open_diia_reconciliation_cycle", runtime_smoke=True),
    FunctionRoute("personnel.military", "Дані / Дія / документи", "Військовий облік / строки…", "open_military_accounting_overview", runtime_smoke=True),
    FunctionRoute("personnel.bulk_replan", "Працівники → Планування", "Перепланувати: замінити існуючий ПЛАН", "show_general_personnel_shift_planner", runtime_smoke=True),
    FunctionRoute("drivers.report_selection", "Графіки", "Водії для звіту…", "choose_monthly_shift_report_drivers", runtime_smoke=True),
    FunctionRoute("timesheet.plan_to_fact", "Табель", "План → факт", "show_employee_timesheet", runtime_smoke=True),
    FunctionRoute("vehicles.core", "Транспорт", "Картка транспортного засобу", "vehicle_core_toolbar", runtime_smoke=True),
    FunctionRoute("vehicles.military", "Транспорт", "Військово-транспортний облік", "open_military_transport_dashboard", runtime_smoke=True),
    FunctionRoute("vehicles.military.statement", "Військово-транспортний облік", "Відомість (додаток 1)", "open_military_transport_statement", runtime_smoke=True),
    FunctionRoute("operations.center", "Ліве меню", "Експлуатація", "open_operations_center", runtime_smoke=True),
    FunctionRoute("operations.assignment_bulk", "Експлуатація → Накази", "Закріпити ТЗ за водіями / Додати багато…", "operations_orders_ui.bulk_assignment_controls", runtime_smoke=True),
    FunctionRoute("operations.assignment_existing", "Експлуатація → Накази → Редагувати наказ", "Поточні закріплення / Додати багато… / Керувати закріпленнями", "operations_orders_ui.existing_assignment_controls", runtime_smoke=True),
    FunctionRoute("operations.assignment_preview_sync", "Експлуатація → Накази → Перегляд наказу", "Автооновлення Preview після зміни закріплень", "operations_orders_ui.refresh_open_order_previews", runtime_smoke=True),
    FunctionRoute("operations.order_preview_formats", "Експлуатація → Накази → Перегляд наказу", "Створити / переглянути DOCX, PDF, JPG", "order_preview_ui.open_order_preview", runtime_smoke=True),
    FunctionRoute("operations.entity_search_selection", "Експлуатація → Учасники / ТЗ", "Додати працівників… з накопиченням вибору", "order_entities_ui.entity_picker", runtime_smoke=True),
    FunctionRoute("operations.entity_edit", "Експлуатація → Накази → Учасники / ТЗ", "Змінити роль / примітку…", "order_entities_ui.edit_order_entity", runtime_smoke=True),
    FunctionRoute("operations.entity_add_vehicle", "Експлуатація → Накази → Учасники / ТЗ", "Додати ТЗ…", "order_entities_ui.entity_picker", runtime_smoke=True),
    FunctionRoute("operations.entity_remove", "Експлуатація → Накази → Учасники / ТЗ", "Прибрати вибрані", "order_entities_ui.remove_order_entities", runtime_smoke=True),
    FunctionRoute("operations.entity_preview_sync", "Експлуатація → Накази → Учасники / ТЗ", "Автооновлення Preview після зміни учасників / ТЗ", "order_entities_ui.refresh_live_preview", runtime_smoke=True),
    FunctionRoute("operations.instructions", "Експлуатація", "Інструктажі та журнали", "open_operations_center", runtime_smoke=True),
    FunctionRoute("operations.instructions_quarter", "Експлуатація → Інструктажі", "На цей квартал…", "safety_instructions_ui.open_quarter_view", runtime_smoke=True),
    FunctionRoute("operations.printable_briefing", "Експлуатація → Інструктажі", "Створити комплект DOCX для друку", "safety_instructions_ui.save_draft_list", runtime_smoke=True),
    FunctionRoute("operations.driver_internship", "Експлуатація", "Стажування водіїв", "driver_internship_ui.install_internship_tab", runtime_smoke=True),
    FunctionRoute("maintenance.stoir", "Ліве меню", "СТОІР", "open_vehicle_maintenance", runtime_smoke=True),
    FunctionRoute("correspondence.center", "Ліве меню", "Кореспонденція", "open_correspondence_center", runtime_smoke=True),
    FunctionRoute("correspondence.new_incoming", "Кореспонденція", "Новий вхідний…", "correspondence_ui.open_new_incoming", runtime_smoke=True),
    FunctionRoute("correspondence.new_outgoing", "Кореспонденція", "Новий вихідний…", "correspondence_ui.open_new_outgoing", runtime_smoke=True),
    FunctionRoute("correspondence.reply", "Кореспонденція → Вхідні", "Відповісти…", "correspondence_ui.open_response", runtime_smoke=True),
    FunctionRoute("correspondence.attachments", "Кореспонденція → картка листа", "Вкладення…", "correspondence_ui.open_attachments", runtime_smoke=True),
    FunctionRoute("correspondence.open_document", "Кореспонденція → картка листа", "Відкрити документ", "correspondence_ui.open_record_document", runtime_smoke=True),
    FunctionRoute("correspondence.mark_received", "Кореспонденція → Вхідні", "Отримано…", "correspondence_ui.open_action_transition", runtime_smoke=True),
    FunctionRoute("correspondence.mark_sent", "Кореспонденція → Вихідні", "Надіслано…", "correspondence_ui.open_action_transition", runtime_smoke=True),
    FunctionRoute("correspondence.status_transition", "Кореспонденція → картка листа", "Змінити стан…", "correspondence_ui.open_status_transition", runtime_smoke=True),
    FunctionRoute("correspondence.state_history", "Кореспонденція → картка листа", "Історія…", "correspondence_ui.open_state_history", runtime_smoke=True),
    FunctionRoute("correspondence.case_create", "Кореспонденція → Справи", "Нова справа…", "correspondence_ui.open_case_editor", runtime_smoke=True),
    FunctionRoute("correspondence.case_assign", "Кореспонденція → картка листа", "Справа…", "correspondence_ui.open_case_assignment", runtime_smoke=True),
    FunctionRoute("correspondence.case_edit", "Кореспонденція → Справи", "Перейменувати…", "correspondence_ui.open_case_editor", runtime_smoke=True),
    FunctionRoute("correspondence.case_archive", "Кореспонденція → Справи", "Архівувати / Відновити", "correspondence_ui.toggle_case_archive", runtime_smoke=True),
    FunctionRoute("correspondence.case_thread_add", "Кореспонденція → Справи", "Додати пов'язані", "correspondence_ui.add_case_linked", runtime_smoke=True),
    FunctionRoute("correspondence.case_open_letter", "Кореспонденція → Справи", "Відкрити лист", "correspondence_ui.open_case_member", runtime_smoke=True),
    FunctionRoute("correspondence.case_remove_letter", "Кореспонденція → Справи", "Вилучити зі справи", "correspondence_ui.remove_case_member", runtime_smoke=True),
    FunctionRoute("documents.center", "Експлуатація → Документи", "Документи підприємства", "DOCUMENT_CENTER_GROUPS", runtime_smoke=True),
    FunctionRoute("documents.catalog_filters", "Документи → Каталог", "Скинути фільтри", "document_catalog_ui.clear_filters", runtime_smoke=True),
    FunctionRoute("documents.catalog_folders", "Документи → Мої папки", "Нова папка…", "document_catalog_ui.create_user_folder", runtime_smoke=True),
    FunctionRoute("documents.attestation_resize", "Документи → Бланки", "Більша історія / Більша форма", "build_attestation", runtime_smoke=True),
    FunctionRoute("documents.catalog_resize", "Документи → Каталог", "Регульоване дерево папок", "document_catalog_ui.open_document_catalog", runtime_smoke=True),
    FunctionRoute("documents.catalog_small_viewport", "Документи → Каталог", "Дерево / таблиця / нижні дії при 760×470", "document_catalog_ui.open_document_catalog", runtime_smoke=True),
    FunctionRoute("documents.catalog_tree_modes", "Документи → Дерево", "За видами / За датами / Мої папки", "document_catalog_ui.change_library_mode", runtime_smoke=True),
    FunctionRoute("waybills.actions", "Шляхові листи", "Повна панель дій", "WAYBILL_ACTION_LABELS", runtime_smoke=True),
    FunctionRoute("tachograph.main", "Ліве меню", "Тахограф", "tab_tacho", runtime_smoke=True),
    FunctionRoute("reports.home", "Ліве меню", "Звіти", "show_reports_home", runtime_smoke=True),
    FunctionRoute("settings.main", "Ліве меню", "Налаштування", "tab_company", runtime_smoke=True),
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
