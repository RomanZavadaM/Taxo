# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Stable tag:** `v10.0`  
**Stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Previous candidates:** `v10.1-r1`, `v10.1-r2`  
**Current test checkpoint:** Taxo 10.1-r3 · 20.09.2026  
**Work branch:** `work/v10.1-driver-role-ui-refresh`

## Статус

10.1-r3 — **candidate / approved UI shell checkpoint**, не stable. Stable 10.0 лишається експлуатаційною версією.

## Збережено з 10.1-r1 / r2

- статус працівника відокремлений від ролі водія;
- `driver_end_date` не губиться;
- роль `Водій` не повертається сама після restart;
- табель має прямі PDF/Excel/контроль/місячний баланс/П-5;
- є брендовані «Про програму» та F1-довідка.

## Нове в 10.1-r3

- прибрано старий native menu row на Windows/Linux;
- приховано стандартний ряд вкладок головного Notebook;
- додано постійний синій sidebar з іконками;
- додано велику світлу header-композицію як у затвердженому макеті;
- додано bottom status bar;
- «Працівники» відкриває саме реєстр персоналу, а legacy водійські картки лишаються окремим технічним контуром;
- реєстр персоналу отримав title/toolbar/search/count у стилі затвердженого макета;
- загальний табель використовує той самий shell;
- використовується затверджений text-free logo artwork без напису підприємства;
- назва підприємства береться з поля «Назва підприємства» і використовується у шапці та заголовках вікон.

## Regression gate

- START/source workflow: **144 tests / OK**;
- Windows workflow: **144 tests / OK** + START preflight OK;
- latest macOS PR jobs are queued on GitHub runners; a previous r3 shell commit passed the macOS suite;
- r3 remains a **source/START prerelease for manual Windows UI verification**, not stable.

## Політика

- `main` = stable 10.0 до manual gate;
- `v10.0` = immutable stable;
- `v10.1-r1`, `v10.1-r2` = immutable previous candidates;
- `v10.1-r3` буде опубліковано лише як новий prerelease після green gate;
- старі tags/releases не пересуваються.

Деталі:
- [Audit 10.1-r3](AUDIT_v10_1_r3.md)
- [Release notes 10.1-r3](../releases/RELEASE_NOTES_v10_1_r3.md)
- [Stable audit 10.0](AUDIT_v10_0_STABLE.md)
