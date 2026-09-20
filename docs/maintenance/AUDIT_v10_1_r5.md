# AUDIT — Taxo 10.1-r5

**Дата:** 20.09.2026  
**Baseline:** stable Taxo 10.0  
**Previous candidate:** v10.1-r4

## Дефект, підтверджений ручною перевіркою

У r4 пункт «Звіти» головного sidebar був прив'язаний до `show_employee_timesheet()`. Ця функція створювала `Toplevel` з повторною шапкою, sidebar і дорожнім footer-мотивом, тобто візуально — ще одну повну копію програми. Повторний виклик не мав single-instance guard.

## Виправлення r5

- головний «Звіти» викликає `show_reports_home()`, а не `show_employee_timesheet()`;
- за наявності personnel module звіти вибираються всередині `personnel_book` у головному workspace;
- «Працівники» примусово вибирає `personnel_overview_page`;
- sidebar має named-button registry та explicit active override для командних сторінок;
- hidden personnel notebook синхронізує активний «Працівники / Звіти»;
- детальний табель має single-instance guard;
- з детального табеля вилучено дубльований application sidebar;
- схема БД не змінена.

## Gate

До merge у main:
1. повний automated regression suite;
2. Windows: «Звіти → Працівники → Звіти» без нових головних вікон;
3. повторне натискання «Табель персоналу» піднімає існуючий детальний табель;
4. PDF/Excel/П-5 та «Папка звітів» працюють;
5. старі immutable tags/releases не пересуваються.
