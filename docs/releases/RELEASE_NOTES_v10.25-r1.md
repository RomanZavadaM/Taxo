# Taxo 10.25-r1 — фундамент планування інструктажів

**Статус:** Test candidate. Stable/Latest залишається 10.24-r9 до окремого прямого рішення власника.

## Що додано

Перший етап лінії «Інструктажі БДР / охорони праці / стажування» реалізує лише безпечне сховище планування. Великий новий UI у r1 не додається.

Новий `src/taxo/briefing_planner.py` зберігає у `Data/BriefingPlanning`:

- незмінні редакції програм із stable program ID та revision;
- напрям, вид, назву, текст, підставу, затвердив, чинність від/до;
- planned sessions з унікальним `planning_key`, щоб повторне формування не дублювало план;
- event sessions з обов'язковою фактичною підставою;
- frozen snapshot вибраних працівників: Taxo ID, ПІБ, табельний №, посада;
- точне посилання session → program revision;
- чесні стани `planned / prepared / conducted`;
- `conducted` лише через явну дію з фактичною датою і приміткою/посиланням на паперовий запис;
- derived `overdue` без автоматичного переписування історії.

## Гарантії

- нова редакція програми не переписує стару;
- session, створений на r1 програми, лишається на r1 після появи r2;
- duplicate planned key відхиляється;
- event session не закриває planned session;
- `prepared` / друк не означає `conducted`;
- факт проведення не можна мовчки переписати іншою датою/приміткою;
- JSON store fail-closed: duplicate keys, невідомий формат/об'єкт, symlink або зламане посилання не ігноруються;
- store лежить у Data і проходить повний workspace backup/restore.

## Віртуальне приймання

Підготовчий isolated прогін перед candidate:
- 3/3 нових r1 scenarios PASS;
- повний START: **1717/1717 PASS**;
- реальна база власника не відкривалася.

Candidate повторно проходить START, Windows, Windows 7 Python 3.8, macOS Intel/ARM, Defender та integrity перед публікацією.

## Далі

Наступний етап після окремого Test release r1 — **10.25-r2: екран «На цей квартал»** поверх цього store. Він теж матиме власне virtual acceptance і окремий Test release.

Повний execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.
