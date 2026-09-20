# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Stable tag:** `v10.0`  
**Stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Previous candidates:** `v10.1-r1`, `v10.1-r2`, `v10.1-r3`, `v10.1-r4`  
**Current test checkpoint:** Taxo 10.1-r5 · 20.09.2026  
**Candidate tag:** `v10.1-r5`  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Статус

10.1-r5 — **candidate / navigation-loop fix checkpoint**, не stable. Stable 10.0 лишається експлуатаційною версією.

## Виправлено після r4

- головний пункт «Звіти» більше не відкриває нову повну копію branded application shell;
- «Звіти» відкриває внутрішню сторінку звітів у головному workspace;
- «Працівники» після звітів гарантовано повертає у реєстр працівників;
- активний sidebar синхронізується з прихованими сторінками персоналу;
- детальний табель персоналу має single-instance guard;
- повторне відкриття детального табеля піднімає існуюче вікно;
- з детального табеля прибрано дубльований sidebar;
- схема БД не змінювалася.

## Regression gate

- START/source publisher: **157 tests / OK**;
- START source package: **success**;
- Windows workflow: **157 tests / OK** + START preflight OK;
- macOS ARM64: **157 tests / OK**;
- macOS Intel x86_64: **157 tests / OK**;
- GitHub prerelease `v10.1-r5`: **published**;
- release target: `146d00916cb953efbcf7d3b167b7f5547d67f0b0`.

## Ручний gate

Перевірити на Windows:
1. «Звіти → Працівники → Звіти» — усе лишається в одному головному вікні.
2. «Табель персоналу» при повторному натисканні не створює другого вікна.
3. PDF / Excel / П-5 / «Папка звітів» залишаються доступними.
4. Немає дубльованого повного sidebar у детальному табелі.

## Політика

- `main` = stable 10.0 до ручного gate;
- `v10.0` = immutable stable;
- `v10.1-r1` … `v10.1-r5` = immutable candidates;
- merge у `main` — тільки після явного підтвердження користувача;
- старі tags/releases не пересуваються.

Деталі:
- [Audit 10.1-r5](AUDIT_v10_1_r5.md)
- [Release notes 10.1-r5](../releases/RELEASE_NOTES_v10_1_r5.md)
- [Stable audit 10.0](AUDIT_v10_0_STABLE.md)
