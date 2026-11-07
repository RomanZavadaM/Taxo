# Taxo — Function Registry draft

Статус: чернетка після Feature Loss Audit. Це не UI-специфікація дизайну; це контракт досяжності функцій.

| function_id | Маршрут | Обов'язкова дія | Callback / target | Gate |
|---|---|---|---|---|
| personnel.registry | Працівники | Реєстр працівників | personnel page | required |
| personnel.new | Працівники | Новий працівник | employee_form | required |
| personnel.data_center | Працівники | Дані / Дія / документи… | open_personnel_data_center_r6 | required |
| personnel.birthdays | Працівники | Дні народження | open_birthday_reminders | required |
| personnel.planning.driver_schedule | Працівники → Планування | Графік водіїв… | tab_schedule | required |
| personnel.planning.bulk_shifts | Працівники → Планування | Робочі зміни персоналу — масово… | show_general_personnel_shift_planner | required |
| personnel.planning.simple_month | Працівники → Планування | Простий місячний графік… | open_simple_month_schedule_r8 | required |
| personnel.planning.dispatch_day | Працівники → Планування | Оперативний день випуску… | show_dispatch_staff_schedule | required |
| personnel.planning.regimes | Працівники → Планування | Режими робочого часу працівників… | show_employee_work_regime | required |
| personnel.planning.regime_month | Працівники → Планування | Норма за режимом → план місяця… | show_regime_month_plan_filler | required |
| personnel.planning.absence | Працівники → Планування | Відпустки / лікарняні / інші відсутності… | show_personnel_absence_planner | required |
| personnel.docs.registry | Дані / Дія / документи | Відкрити реєстр документів | open_employee_document_register | required |
| personnel.docs.control | Дані / Дія / документи | Контроль обов'язкових документів… | open_required_employee_documents_r7 | required |
| personnel.registry.bulk | Дані / Дія / документи | Масові дії з останнього імпорту… | open_personnel_registry_bulk_actions_r6 | required |
| personnel.diia.cycle | Дані / Дія / документи | Офіційний цикл Дії… | open_diia_reconciliation_cycle | required |
| personnel.military.overview | Дані / Дія / документи | Військовий облік / строки… | open_military_accounting_overview | required |
| timesheet.all | Табель обліку | Табель робочого часу всіх працівників | show_employee_timesheet | required |
| timesheet.plan_to_fact | Табель | План → факт | plan_to_fact | required |
| drivers.monthly_report | Графіки | Водії для звіту… | choose_monthly_shift_report_drivers | required |
| vehicles.core | Транспорт | core vehicle toolbar | VEHICLE_CORE_ACTIONS | required/runtime-smoke |
| vehicles.registry | Транспорт | Дані «Шлях» | open_selected_vehicle_registry_data | required |
| vehicles.military | Транспорт | Військово-транспортний облік | open_military_transport_dashboard | required |
| vehicles.military.statement | Військово-транспортний облік | Відомість (додаток 1) | open_military_transport_statement | required |
| operations.center | Ліве меню | Експлуатація | open_operations_center | required |
| maintenance.stoir | Ліве меню | СТОІР | open_vehicle_maintenance | required |
| documents.center | Експлуатація → Документи | Документи підприємства | DOCUMENT_CENTER_GROUPS | required |
| waybills.actions | Шляхові листи | повний набір WAYBILL_ACTION_LABELS | existing callbacks | required |
| tachograph.main | Ліве меню | Тахограф | tab_tacho | required |
| reports.home | Ліве меню | Звіти | show_reports_home | required |
| settings.main | Ліве меню | Налаштування | tab_company | required |

## Мінімальний runtime gate

Для кожного `required`:
1. маршрут/кнопка реально mapped;
2. callback callable;
3. invoke/select відкриває очікуваний tab/window;
4. primary actions усередині присутні;
5. якщо функцію замінено — registry змінюється явним `replaced_by`, а не тихим видаленням.
