# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Stable tag:** `v10.0`  
**Stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Current test checkpoint:** Taxo 10.1-r1 · 20.09.2026  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Статус

10.1-r1 — **candidate / test checkpoint**, не stable. Stable 10.0 лишається експлуатаційною версією до завершення ручної перевірки.

## Головне виправлення

- статус працівника `employees.active` відокремлено від стану ролі `drivers.active`;
- startup sync більше не звільняє працівника через завершену роль водія;
- startup sync більше не повертає завершену роль `Водій`;
- `driver_end_date` зберігається окремо;
- re-employment не активує водійську роль автоматично;
- деактивація водійської картки запитує дату завершення ролі.

## UI refresh

- brand-мотив сонця й автобуса;
- приглушена синьо-жовта офісна палітра;
- text-free app icon;
- назва підприємства в шапці динамічна з поля «Назва підприємства»;
- фіксованого «АТП Завада» у графіці немає.

## Regression gate

- GitHub Actions run `35525130436`;
- **126 tests / OK**;
- START package preflight — OK;
- БД/SQLite/cache у package не потрапляють;
- `START.bat` ASCII-only + CRLF — OK.

## Політика

- `main` = stable 10.0 до manual gate;
- `v10.0` = immutable stable tag/release;
- 10.1-r1 тестується окремо;
- старі tags/releases не пересуваються.

Деталі:
- [Audit 10.1-r1](AUDIT_v10_1_r1.md)
- [Release notes 10.1-r1](../releases/RELEASE_NOTES_v10_1_r1.md)
- [Stable audit 10.0](AUDIT_v10_0_STABLE.md)
