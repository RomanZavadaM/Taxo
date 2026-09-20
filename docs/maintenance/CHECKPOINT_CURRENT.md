# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Stable tag:** `v10.0`  
**Stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Previous candidates:** `v10.1-r1`, `v10.1-r2`, `v10.1-r3`  
**Current test checkpoint:** Taxo 10.1-r4 · 20.09.2026  
**Candidate tag:** `v10.1-r4`  
**Candidate target:** `6aaf5017dbe201f838308d61c9b9c950e3bb50ea`  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Статус

10.1-r4 — **candidate / approved UI polish checkpoint**, не stable. Stable 10.0 лишається експлуатаційною версією.

## Збережено з r1–r3

- статус працівника відокремлений від ролі водія;
- `driver_end_date` не губиться;
- роль `Водій` не повертається сама після restart;
- затверджений text-free logo artwork використовується як runtime/build icon;
- application shell: світла шапка, синій sidebar, центральна робоча область і bottom status bar;
- є брендовані «Про програму» та F1-довідка.

## Нове в 10.1-r4

- реєстр працівників має чітку ієрархію: заголовок, primary actions, KPI-картки, secondary tools, пошук, таблиця;
- KPI: «Всього», «Працюють», «Водії», «Звільнені»;
- табель розділяє «Робота з табелем» і «Звіти та друк»;
- PDF/Excel для всього персоналу, деталізація, контроль, місячний баланс і П-5 залишаються доступними;
- додано «Папка звітів» у загальному та персональному блоці звітів;
- заголовки «Про програму» і «Довідка» використовують динамічну назву підприємства;
- схема БД у r4 не змінювалася.

## Regression gate

- START/source publisher: **150 tests / OK**;
- START source package: **success**;
- Windows workflow: **150 tests / OK** + START preflight OK;
- macOS ARM64: **150 tests / OK**;
- macOS Intel x86_64: **150 tests / OK**;
- GitHub prerelease `v10.1-r4`: **published**;
- release target: `6aaf5017dbe201f838308d61c9b9c950e3bb50ea`.

## Політика

- `main` = stable 10.0 до ручного gate;
- `v10.0` = immutable stable;
- `v10.1-r1` … `v10.1-r4` = immutable candidates;
- `v10.1-r4` призначений для ручної Windows-перевірки дизайну та основних дій;
- merge у `main` — тільки після явного підтвердження користувача;
- старі tags/releases не пересуваються.

Деталі:
- [Audit 10.1-r4](AUDIT_v10_1_r4.md)
- [Release notes 10.1-r4](../releases/RELEASE_NOTES_v10_1_r4.md)
- [Stable audit 10.0](AUDIT_v10_0_STABLE.md)
