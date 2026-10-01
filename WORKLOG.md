# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Latest issued fast-test:** **10.9-r2 / `v10.9-r2`**  
**Current active slice:** **10.9-r3 — vehicle-document validity for the full trip**  
**Integrated main baseline:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Active branch:** `work/v10.9-r3-vehicle-document-validity`  
**Draft PR:** #122, stacked on frozen r2 branch  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r2 immutable issuance

10.9-r2 закрив ризики незнищуваної історії виданих шляхових листів і номерів. Immutable issued source: `03ad7a01411c63aeb3d17eaebe0b1b59a27726ff`; tag `v10.9-r2` вказує саме на цей SHA; exact-source regression **734/734 OK**; publisher `36872542242`, START/source `36872542116`, Windows `36872548774`, macOS `36872548762` — success.

START: `Taxo_v10_9_candidate_r2_START.zip`; SHA256 `81ee180c46e8b3d56002c275525a6e604257b27d6a925ad33823eb0a0ea4b716`.

10.9-r2 заморожена. PR #121 лишається draft/unmerged до окремої прямої команди власника.

## EXTERNAL AUDIT — accepted backlog

Дві частини суміжного аудиту перевірені по актуальному runtime. Прийнятий backlog зафіксований у `docs/maintenance/AUDIT_EXTERNAL_REVIEW_2026-10-01.md`.

Після захисту шляхівок наступний активний пункт — документи ТЗ (`valid_from` + чинність на весь рейс). Далі: робочий час/відпочинок → тахограф/60-денний реєстр → персонал/П-5 → СТОІР → накази → schema/versioning/connection/error-handling cleanup.

Для критичних бізнес-правил стандарт — поведінкові тести на реальній тимчасовій SQLite-БД; source-string guards не вважаються достатньою перевіркою бізнес-поведінки.

## DOING — 10.9-r3

Ціль: **обов'язкові документи ТЗ мають бути чинними протягом усього планового рейсу, а не лише на дату виїзду**.

Зроблено:

- `valid_from` реально бере участь в оперативній перевірці;
- `valid_until` контролюється до дати завершення рейсу;
- кілька активних документів одного типу можуть разом безперервно перекривати багатоденний рейс;
- архівні документи не використовуються для нового рейсу;
- старі записи без `valid_from` зберігають backward compatibility;
- тимчасовий реєстраційний документ обов'язковий лише для ТЗ з відповідною ознакою;
- ДЦВ лишається необов'язковим;
- ручне архівування та кілька документів одного типу збережені;
- шляхівка передає в перевірку `row["date"]` → `row["end_date"]`;
- новий runtime layer `v1093-vehicle-document-validity` підключений після r2;
- START guard і source-package guard містять `vehicle_document_validity.py`;
- додано 7 нових поведінкових SQLite-тестів;
- застарілий r1 source-string test виправлений так, щоб перевіряти історичний інваріант попередження/підтвердження, а не назавжди фіксувати одно-денний виклик;
- one-shot helper workflow після виконання видалений.

## NEXT

1. Прогнати повний exact-head regression/START після state-sync і підтвердити весь набір тестів.
2. Підтвердити exact-head Windows/macOS gates PR #122.
3. Лише після зелених gates додати immutable publisher `v10.9-r3`, видати START і checksum.
4. Після issuance зафіксувати exact SHA/run IDs/checksum в Issue #61 і PR #122; r3 заморозити.
5. Не зливати в `main` без окремої прямої команди власника.
