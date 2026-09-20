# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Stable tag:** `v10.0`  
**Stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Previous candidate:** `v10.1-r1`  
**Current test checkpoint:** Taxo 10.1-r2 · 20.09.2026  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Статус

10.1-r2 — **candidate / UI test checkpoint**, не stable. Stable 10.0 лишається експлуатаційною версією.

## Збережено з 10.1-r1

- `employees.active` не переписується з `drivers.active`;
- завершена роль `Водій` не повертається після restart;
- `driver_end_date` зберігається окремо;
- re-employment не активує роль водія автоматично.

## Нове в 10.1-r2

- погоджена світла шапка з автобусом без вбудованої назви;
- dynamic enterprise name з поля «Назва підприємства»;
- live preview шапки у налаштуваннях підприємства;
- перероблена картка працівника;
- перероблений табель персоналу з картками План/Факт/Відхилення/Без факту;
- видимі переходи до деталізації, PDF, Excel, контролю, місячного балансу та П-5;
- прибрано legacy UI-кнопку масового «8 год у порожні будні»;
- окреме вікно «Про програму»;
- вбудована пошукова F1-довідка.

## Regression gate

- START/source — **135 tests / OK**;
- Windows — **135 tests / OK**;
- macOS ARM64 — **135 tests / OK**;
- macOS Intel x86_64 — **135 tests / OK**;
- source archive preflight — OK.

## Політика

- `main` = stable 10.0 до manual gate;
- `v10.0` = immutable stable;
- `v10.1-r1` = immutable previous candidate;
- `v10.1-r2` = current candidate після green gate;
- старі tags/releases не пересуваються.

Деталі:
- [Audit 10.1-r2](AUDIT_v10_1_r2.md)
- [Release notes 10.1-r2](../releases/RELEASE_NOTES_v10_1_r2.md)
- [Audit 10.1-r1](AUDIT_v10_1_r1.md)
- [Stable audit 10.0](AUDIT_v10_0_STABLE.md)
