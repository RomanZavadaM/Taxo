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

Автоматичний gate завершено успішно:
- source / START — **157 tests / OK**;
- Windows — **157 tests / OK** + START preflight OK;
- macOS ARM64 — **157 tests / OK**;
- macOS Intel x86_64 — **157 tests / OK**;
- prerelease `v10.1-r5` — **published**;
- immutable release target — `146d00916cb953efbcf7d3b167b7f5547d67f0b0`.

До merge у main лишається ручний Windows gate:
1. «Звіти → Працівники → Звіти» без нових головних вікон;
2. повторне натискання «Табель персоналу» піднімає існуючий детальний табель;
3. PDF/Excel/П-5 та «Папка звітів» працюють;
4. старі immutable tags/releases не пересуваються.
