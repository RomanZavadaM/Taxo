# HANDOFF_CURRENT — Taxo

**Оновлено:** 09.11.2026 — stable v10.14-r4 збережено; інтегровано й exact-main перевірено 10.14-r10.

## Фактичний стан

- **Stable / GitHub Latest:** [v10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4), 8 canonical assets. Stable/tag під час r5–r10 не змінювався.
- **Поточний main / інтегрований кандидат:** Taxo **10.14-r10**, exact main `12d6ff9e49b9a9ac2753b29f63828531c66bd1c8`, PR #283.
- **Exact-main CI r10:** START #2556, Windows #1413, Win7 #389, macOS Intel/ARM #1314 — **SUCCESS**.
- **Regression:** **1039 tests / OK**. Окремо PASS — повний холодний запуск `main.init_db → taxo_app.App() → update_idletasks() → update()`.
- **Наступна кодова ревізія:** **10.15-r1**. r10 завершив цикл 10.14; видані ревізії не перевикористовувати.
- **Попередня стабільна / rollback:** [v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10).

## Що важливо у r6–r10

- r6–r8 відновили й захистили механізм закріплення водіїв/ТЗ, persistence пар, повторне читання БД і актуальний друк наказу.
- r9 додав автоматичну синхронізацію вже відкритого Preview після single/bulk add, edit і delete.
- r10 виправив реальний Windows cold-start crash `pack/grid` у старому шарі «Шлях»:
  - «Реєстр “Шлях”» і «Дані “Шлях”» винесені в окрему панель **«Реєстри та облік ТЗ»**;
  - старий тест, який фактично дозволяв known geometry conflict, переписано на заборону;
  - додано справжній cold-start regression в ізольованому дочірньому процесі.
- Важливий висновок для системи контролю: існування функції в коді недостатньо. Для критичних state-changing сценаріїв потрібні **reachability + persistence/outcome + live synchronization + cold-start** перевірки.

## Резерв

- Exact-main START artifact: GitHub Actions #2556, artifact ID `13682040160`, `Taxo_v10_14_candidate_r10_START`, **1 760 098 байт**.
- SHA256: `a8304385abe5e120a5802872909eb2bd892adbbf3ef6a1bd678244929e21671b`.
- Google Drive `02_CURRENT_MAIN`: `Taxo_CURRENT_MAIN_v10.14-r10_2026-11-09_START.zip`, file ID `13aUUhV1yGawzaqdrujn_emPqyK999cey`.
- Робочі SQLite, скани й документи персоналу в recovery ZIP не входять.

## Відкриті напрями

- #275 — системне посилення Feature Loss / outcome / startup guard;
- #246 — ширший спільний вибір працівників/ТЗ;
- #237 — планування інструктажів;
- #164 — UX-спрощення;
- #251 — оптимізація CI для docs/release checkpoint;
- #61 — live development ledger.

## Одна наступна безпечна дія

Ручне приймання **10.14-r10 exact-main** через START ZIP:

1. програма має відкритися без traceback;
2. відкрити «Транспорт» і перевірити окрему панель «Реєстри та облік ТЗ»;
3. відкрити/створити наказ про закріплення;
4. single + bulk пари → закрити/відкрити → пари лишаються;
5. Preview має оновлюватися автоматично після зміни пар;
6. DOCX/PDF/JPG мають містити всі пари.

Новий код за наступним дефектом — тільки **10.15-r1**. Stable v10.14-r4 не просувати без окремого рішення власника.
