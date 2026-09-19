# AUDIT — Taxo 9.1 candidate r9.8

**Дата:** 19.09.2026  
**Stable:** Taxo 9.0.1  
**Previous candidate:** r9.7  
**Причина:** різні лікарі/механіки для однієї зміни у шляхівках одного дня.

## Ручне підтвердження

На скріншоті «Шляхівки на 20.09.2026»:
- перший рейс переходить на 21.09.2026;
- другий завершується 20.09.2026;
- у колонках «Лікар» і «Механік» відображені різні ПІБ, хоча показується одна I зміна.

## Root cause

`_waybill_schedule_rows()` викликав `_duty_staff_for_interval()` окремо для кожного рейсу.

Нічний рейс охоплював наступну дату, тому I зміна 21.09 могла стати `doctor_1/mechanic_1` шляхівки 20.09.

## Fix

- додано `_duty_staff_for_work_date(work_date)`;
- вибірка обмежена exact `employee_shifts.work_date`;
- `_waybill_schedule_rows` отримує day-duty один раз перед циклом;
- кожен рядок цього дня отримує однаковий duty map;
- duplicate role/date/shift позначається conflict;
- видача шляхівки з conflict блокується;
- manual shift form більше не дозволяє другий role/date/shift slot через інше location;
- monthly planner slot query теж глобальний у межах одного АТП.

## Data policy

Старі дублікати не видаляються й не замінюються автоматично. Їх треба виправити вручну через план персоналу.

## Regression gate

`tests/test_v9_1_r9_8.py` відтворює:
- current-day vs next-day I shift;
- legacy duplicate locations;
- one day-duty call for all waybill rows;
- location-independent manual uniqueness.

Перед release обов'язкові:
- Windows full suite + START full/incomplete preflight;
- macOS ARM64 / Intel full suite;
- START source package verification;
- immutable publisher.
