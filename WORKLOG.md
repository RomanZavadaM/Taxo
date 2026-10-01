# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Current active slice:** **10.9-r2 — waybill integrity**  
**Base main:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Branch:** `work/v10.9-r2-waybill-integrity`  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r1 closeout

10.9-r1 повністю інтегрований і заморожений. Immutable issued source: `b0eebbf88b22fbd7761544640d9804416a328acb`; exact-source regression 730/730 OK; full-package run `36857771398` success. `main` після фінального state-sync: `8f18a7ccf1588556f6f3d7dca81943f87d817935`.

## EXTERNAL AUDIT — accepted backlog

Дві частини суміжного аудиту перевірені по актуальному runtime. Прийнятий backlog зафіксований у `docs/maintenance/AUDIT_EXTERNAL_REVIEW_2026-10-01.md`.

Черга після r2: документи ТЗ (`valid_from`/весь рейс) → робочий час/відпочинок → тахограф/60-денний реєстр → персонал/П-5 → СТОІР → накази → schema/versioning/connection/error-handling cleanup.

Для критичних бізнес-правил новий стандарт — поведінкові тести на реальній тимчасовій SQLite-БД; source-string guards не вважаються достатньою перевіркою бізнес-поведінки.

## DOING — 10.9-r2

Ціль: **видана шляхівка та її номер є незнищуваною історією**.

Уже зроблено:

- `waybill_integrity.py` — окремий доменно-інфраструктурний safeguard module;
- startup retention більше не видаляє `worklog`, якщо на нього посилається `waybills`;
- `waybill_number_history` накопичує всі історично використані серія+номер з `waybill_events` і поточного `waybills`;
- DB triggers забороняють повторне використання історичного номера після анулювання/перевидачі;
- DB triggers забороняють фізичне видалення driver/worklog, якщо існує видана шляхівка;
- модуль підключений останнім feature layer `v1092-waybill-integrity`;
- runtime identity і `VERSION.txt` переведені на `10.9-r2`;
- `START.bat` і source archive guard вимагають `waybill_integrity.py`;
- додано поведінкові SQLite-тести `tests/test_v10_9_r2.py`;
- one-shot identity workflow успішно виконався і самовидалився (`9c23a7faf41644558e837918bb41b8f44e44d044`).

## NEXT

1. Дочекатися актуального source regression на поточному head і виправити можливі регресії.
2. Відкрити draft PR 10.9-r2 від `main`, запустити Windows/macOS gates.
3. Додати release notes/audit r2 та exact issuance workflow лише після зелених поведінкових/регресійних тестів.
4. Не зливати в `main` без окремої прямої команди власника.
