# Taxo — поточна контрольна точка

**Дата:** 09.11.2026  
**Stable / Latest:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4).  
**Поточний інтегрований кандидат:** Taxo **10.15-r1**, exact main `825a1994984aec6b47ce08224f2969735ee27d47`.  
**Наступна кодова ревізія:** **10.15-r2**.

## Що сталося

На реальній БД власника наказ №28 був створений без пар: сам order є, але assignment-записів для нього немає. Наказ №27 безпосередньо перед ним має 12 пар. Це локалізувало дефект до передачі UI-вибору в момент «Створити», а не до Preview чи друку.

## Що виправлено в 10.15-r1

- вибрані ТЗ/водії стають окремими видимими **підготовленими парами**;
- prepared pairs не залежать від поточного Listbox selection;
- порожній наказ не створюється мовчки — потрібне явне підтвердження;
- перед commit перевіряється точна кількість записаних пар;
- додано owner-regression: 12+12 → зафіксувати → примусово очистити UI selection → «Створити» → SQLite → Preview → DOCX/PDF/JPG → reopen.

## Доказ перевірок

- PR #286 merged → exact main `825a1994984aec6b47ce08224f2969735ee27d47`.
- Exact-main START #2559 — SUCCESS.
- Exact-main Windows #1418 — SUCCESS, **1041 tests / OK**.
- Exact-main Win7 #394 — SUCCESS.
- Exact-main macOS Intel/ARM #1319 — SUCCESS.
- Owner-scenario `test_owner_scenario_pairs_survive_selection_loss_and_reach_docx_pdf` — PASS.
- На локальній копії реальної БД власника 12 підготовлених пар пережили примусове очищення selection і потрапили в Preview.

## Резерв

- START artifact #13695956407, 1 766 785 байт.
- SHA256 `143cd4a662f4596e727d75a998944e4f6c3f1cd66d113756e64b48fc6bc1d054`.
- Drive: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.15-r1_2026-11-09_START.zip`, ID `1EwYuyv7nATjfmnDCQcpQVU9U-XRy9xZl`.
- Реальна робоча SQLite власника не зберігалася в репозиторії чи Drive.

## Далі

Ручне приймання 10.15-r1 на робочому сховищі власника. Stable v10.14-r4 не змінювати без окремої команди. До завершення цього checkpoint новий код не починати.
