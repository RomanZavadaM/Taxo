# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Code merge:** PR #118 → main merge `843a38243dd4eeeb02b40f8de59cc630ef4dce09`  
**Immutable issued source:** `b0eebbf88b22fbd7761544640d9804416a328acb`  
**START:** `Taxo_v10_9_candidate_r1_START.zip` · SHA-256 `0c819f9f3e4b31f58e6b86e2b4f1d72086901c0bd2a26a499e4c17f6de9c1766`  
**Regression:** **730/730 OK**  
**Full-package run:** `36857771398` — success  
**Next code revision:** **10.9-r2**  
**Live ledger:** Issue #61

## DONE — 10.8-r4 → 10.9-r1 cumulative integration

За прямою командою власника кумулятивний PR #118 ретаргетовано на `main`, переведено з draft у ready і успішно злито.

У main інтегровано весь послідовний ланцюг після 10.8-r3:

- 10.8-r4 — базовий СТОІР і контроль ТО;
- 10.8-r5 — прогноз ТО, заявки на ремонт, компактне fleet summary;
- 10.8-r6 — винесення neutral file-output helpers у `output_files.py`;
- 10.8-r7 — централізований `feature_layers.py` registry;
- 10.8-r8 — `application_context.py` та explicit infrastructure services;
- 10.8-r9 — `backup_migration.py`;
- 10.8-r10 — `database_runtime.py` і єдина SQLite connection policy;
- 10.9-r1 — `data_access.py`, transaction boundary та `ApplicationServices.data`.

Схема БД, plan/fact, фактичність Бланків, кадрова семантика й historical immutable checkpoints не переписувалися цим архітектурним ланцюгом.

## DONE — full package 10.9-r1

Existing immutable tag/source `v10.9-r1` не рухався. Full-package workflow використав exact source `b0eebbf88b22fbd7761544640d9804416a328acb`.

Run `36857771398` — success:

- exact-source verify — success;
- Windows x64 regression/build/portable/setup — success;
- Windows 7 SP1 x64 Python 3.8 regression, PyInstaller build, PE gate, portable/setup — success;
- macOS arm64 — success;
- macOS x86_64 — success;
- final release-asset verification — success;
- загальний `SHA256SUMS_v10_9_r1_ALL.txt` сформовано.

Release `v10.9-r1` містить START, Windows x64, Windows 7 SP1 x64, macOS arm64/x86_64 та platform/full SHA-256 manifests.

## DONE — cleanup

Після кумулятивної інтеграції закрито старі open PR, які більше не мають самостійного шляху злиття: #108, #109, #110, #111, #112, #113, а також старі тупикові #103, #94, #93, #91. Після cleanup open PR не залишалося до створення цього documentation-closeout PR.

#103 мав post-issuance хвіст, що розійшовся з канонічною лінією; immutable issued checkpoint збережено, але сам тупиковий PR закрито і його head не використовується як кодова база.

Історичні branch refs, tags і releases не видаляються як історія. Для нової роботи вони не є джерелом коду: старт тільки від актуального `main`.

## DOING

1. Завершити documentation closeout PR для 10.9-r1.
2. Після merge документації звірити `main`, `PROJECT_STATE.md`, `WORKLOG.md`, release index та Issue #61.
3. Не змінювати код під уже виданим `10.9-r1`.

## NEXT

Перший наступний code slice — **10.9-r2**, від актуального `main`. Продовжувати модульну архітектуру малими завершеними кроками: нові великі можливості підключати через чіткі межі `domain → service → repository/data access → infrastructure`, не повертаючи предметні залежності у глобальний `main.py`.