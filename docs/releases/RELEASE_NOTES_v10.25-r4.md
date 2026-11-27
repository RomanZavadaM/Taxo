# Taxo 10.25-r4 — «За подією» та явний факт проведення

**Статус:** Test candidate. Stable/Latest залишається 10.24-r9 до окремого прямого рішення власника.

## Що додано

- окрема дія **«За подією…»** у чинному модулі інструктажів;
- підстава події обов'язкова;
- вибір працівників накопичується під час пошуку з єдиного реєстру;
- event session зберігає точну редакцію програми та frozen snapshots людей;
- event session не закриває і не змінює regular planned session;
- можна створити event окремо або створити й підготувати DOCX; DOCX означає лише `prepared`;
- у квартальному вікні додано **«Зафіксувати проведення…»**;
- факт проведення записується тільки вручну з фактичною датою та обов'язковою приміткою/посиланням на паперовий журнал;
- уже зафіксований факт не можна мовчки переписати іншою датою чи приміткою;
- **«Історія…»** показує read-only audit: режим, reason, exact program revision, frozen people, created/updated/prepared/conducted, paper evidence і prepared DOCX/SHA-256.

## Віртуальне приймання

Prep:
- 3/3 нових r4 scenarios PASS;
- strict live actions PASS: open event, create event, save conducted fact, open history;
- повний START: **1731/1731 PASS**;
- Windows/Win7/macOS — SUCCESS;
- Defender/integrity PASS;
- реальна база власника не відкривалась.

Candidate повторно проходить START, Windows, Windows 7 Python 3.8, macOS Intel/ARM, Defender та integrity перед публікацією.

## Далі

Після окремого Test release r4 — **10.25-r5: наскрізне контрольне приймання Інструктажів**: program revision → quarter plan → employees → prepared DOCX → close/reopen → event → manual conducted fact → overdue → full backup/restore → equality/integrity.

Повний execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.
