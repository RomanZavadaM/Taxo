# AUDIT — Taxo 10.1-r2 candidate

**Дата:** 20.09.2026  
**Stable baseline:** Taxo 10.0 / `v10.0`  
**Previous candidate:** `v10.1-r1`  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Scope

10.1-r2 не змінює підтверджену модель робочого часу 10.0 і не скасовує driver-role fix 10.1-r1. Основна мета — UI refresh та підняття видимості звітів/контролю.

## Перевірені конструктивні рішення

1. Назва підприємства не вбудована у logo artwork і береться з `company.name`.
2. `drivers.active`, `employees.active` та `employee_roles` залишаються розділеними.
3. Табель не підставляє план як факт автоматично.
4. Масова кнопка legacy «8 год у порожні будні» не експонується у новому UI.
5. PDF/XLSX звіти використовують наявні перевірені exporters, а не нову паралельну логіку розрахунку.
6. П-5 викликає існуючий модуль типової форми.
7. Вбудована довідка не змінює робочі дані.

## Новий UI-контур

- main header — approved light design;
- company settings — live header preview;
- employee card — branded window with separate employment/role blocks;
- personnel timesheet — summary/daily cards, statuses and report toolbar;
- About — branded system information window;
- Help — searchable F1 window.

## Regression coverage added

`tests/test_v10_1_r2.py` перевіряє:
- r2 version marker;
- видимість звітних кнопок табеля;
- summary/daily live stat variables;
- missing-fact row states;
- відсутність legacy mass-fill button;
- branded/dynamic About;
- searchable Help + F1;
- візуальне розділення employment/roles у картці працівника;
- live company header preview;
- text-free branding.

## Regression result

- START/source gate: **135 tests / OK**;
- Windows gate: **135 tests / OK**;
- macOS ARM64 gate: **135 tests / OK**;
- macOS Intel x86_64 gate: **135 tests / OK**;
- START archive package preflight: OK;
- databases / SQLite caches / personal working data are not bundled.

Source workflow run: `35529418802`. Windows: `35529422213`. macOS: `35529422228`.

## Release policy

`v10.1-r2` може бути опублікований лише як prerelease/source checkpoint після green regression gate. `main` не зливається до ручної Windows-перевірки.
