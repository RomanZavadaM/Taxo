# AUDIT — Taxo 10.0.1 candidate r1

**Дата:** 19.09.2026  
**Stable:** Taxo 10.0  
**Candidate:** 10.0.1 r1

## Симптом

Після зняття ролі «Водій» і повторного запуску Taxo:
- роль «Водій» могла повернутися;
- працівник міг стати «Звільнений».

## Root cause

У `init_db()` legacy sync для кожного запису `drivers` при **кожному запуску**:
- виконував `UPDATE employees ... active=drivers.active`;
- виконував `INSERT OR IGNORE employee_roles(...,'Водій')`.

Отже `drivers.active`, який після завершення водійської ролі дорівнює 0, помилково трактувався як кадрове звільнення.

Окремо employee save очищав `driver_end_date`, навіть якщо роль «Водій» уже була завершена.

## Correct model

- employment status і driver role — незалежні;
- `employees.active` не синхронізується з `drivers.active` після первинної legacy migration;
- `driver_end_date` належить водійській ролі;
- `dismissal_date` належить трудовим відносинам;
- restart не має змінювати жодне явне рішення користувача щодо ролей.

## Fix

- додано `ensure_legacy_driver_employee()`: existing employee = no role/status rewrite;
- додано `set_employee_active_state()`: rehire не відновлює відсутню driver role;
- додано `sync_employee_driver_role()`: збереження без driver role не стирає driver end date;
- driver-card sync більше не копіює driver active у employee active;
- inactive historical driver card не додає driver role автоматично.

## Data safety

Автоматичний repair уже пошкоджених карток **не виконується**, тому що система не може безпечно відрізнити:
- реально звільненого працівника;
- працівника, якого баг помилково позначив звільненим.

Виправлення існуючого неоднозначного запису — тільки після явної перевірки оператором.

## Gate

Перед publication:
- regression suite Windows;
- regression suite macOS ARM64;
- regression suite macOS Intel;
- START/source verification;
- окремий pre-release tag без merge у main.
