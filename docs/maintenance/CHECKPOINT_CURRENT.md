# Taxo — поточна контрольна точка

**Дата:** 09.11.2026  
**Stable / Latest:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4).  
**Поточний інтегрований кандидат:** Taxo **10.14-r10**, exact main `12d6ff9e49b9a9ac2753b29f63828531c66bd1c8`.  
**Наступна кодова ревізія:** **10.15-r1**.

## Що сталося

Після owner-test r6–r9 послідовно виявилися:
- втрачена видимість/доступність mass assignment;
- stale Preview і порожній документ після додавання пар;
- відсутність live sync уже відкритого Preview;
- у r9 — критичний cold-start crash на Windows через змішаний `pack/grid`.

## Що виправлено в r10

- дії «Шлях» винесені з legacy vehicle toolbar в окрему панель «Реєстри та облік ТЗ»;
- різні geometry manager тепер працюють у різних parent-контейнерах;
- старий regression більше не вимагає збереження known geometry bug;
- додано реальний cold-start smoke в окремому ізольованому процесі.

## Доказ перевірок

- PR #283 merged.
- Exact main: `12d6ff9e49b9a9ac2753b29f63828531c66bd1c8`.
- START #2556 — SUCCESS, **1039 tests / OK**.
- Windows #1413 — SUCCESS.
- Win7 #389 — SUCCESS.
- macOS Intel/ARM #1314 — SUCCESS.
- Cold-start regression — PASS.

## Резерв

- Artifact #13682040160, 1 760 098 байт.
- SHA256 `a8304385abe5e120a5802872909eb2bd892adbbf3ef6a1bd678244929e21671b`.
- Drive: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.14-r10_2026-11-09_START.zip`, ID `13aUUhV1yGawzaqdrujn_emPqyK999cey`.

## Далі

Ручне приймання r10 на реальній БД. Stable v10.14-r4 не змінювати без окремої команди власника. Наступний код — **10.15-r1**.
