# Taxo 10.25-r3 — програми, працівники та підготовка DOCX

**Статус:** Test candidate. Stable/Latest залишається 10.24-r9 до окремого прямого рішення власника.

## Що додано

r3 з'єднує planning core r1/r2 з реєстром працівників і чинним PaperDocuments:

- окремий UI «Програми / план / друк…»;
- створення програми та нової незмінної редакції;
- історичні редакції доступні лише для перегляду;
- вибір працівників із єдиного реєстру;
- пошук не скидає вже накопичений multi-select;
- planned session отримує frozen snapshot Taxo ID / ПІБ / табельного № / посади;
- planning key детермінований за програмою, редакцією, датою і набором працівників;
- однаковий план не створює дубль session або другий DOCX;
- exact program revision → чинний PaperDocuments DOCX;
- session ↔ DOCX link зберігається окремо в `Data/BriefingPreparedOutputs` як document ID + filename + SHA-256;
- після успішної перевірки файла session стає тільки `prepared`;
- `prepared` не означає `conducted`, паперовий підпис або юридичне підтвердження;
- tampered/missing DOCX fail-closed;
- full backup/restore зберігає planning store, output links і PaperDocuments.

## Захист UI

Додано strict live routes:
- `operations.instructions_planning`;
- `operations.instructions_program_revision`;
- `operations.instructions_prepare_planned`.

Перший prep виявив реальний UI-регрес: додаткова кнопка зсунула стару «Створити комплект DOCX для друку» на 4 px за межу 940×600. Нову кнопку перенесено у верхній рядок кварталу; тест не послаблювався.

## Virtual acceptance до candidate

- r3 synthetic/live scenarios: 5/5 PASS;
- повний prep START після UI fix: **1727/1727 PASS**;
- реальна база власника не відкривалась.

Candidate повторно проходить START, Windows, Windows 7 Python 3.8, macOS Intel/ARM, Defender та integrity перед публікацією.

## Далі

Після окремого Test release r3 — **10.25-r4: «За подією» + явна ручна фіксація факту проведення**. Жодного автоматичного conducted.

Execution plan: `docs/planning/INSTRUCTIONS_10_25_EXECUTION_PLAN_2026-11-27.md`.
