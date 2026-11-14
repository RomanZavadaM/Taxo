# PROJECT_STATE — Taxo

**Дата:** 14.11.2026.

## Поточний підтверджений стан

Taxo інтегрував і опублікував продуктовий checkpoint **10.19-r2**.

- Exact product / release source: `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`.
- Stable/Latest: **v10.18-r3**, без змін.
- Current Test prerelease: **v10.19-r2 — Test Portable**.
- r2 release: 4 Portable + START + SHA256, без Setup.
- r8 executable publication залишається заблокованою; історичний Firefox verdict не оголошується false positive.

## Що додано в 10.19-r2

Другий slice системи шаблонів:
- окремий список `CompanyTemplates` і редактор власних копій;
- vendor `TemplateLibrary` не редагується;
- редактор змінює лише дозволені користувацькі тексти, зберігаючи структурні ID/типи/variables/data source;
- великі тексти не усікаються в межах встановлених лімітів;
- Save створює нову immutable власну редакцію, а попередній файл не переписується;
- current-index атомарно переключається на нову редакцію;
- SHA-256 захищає від silent last-write-wins при двох редакторах;
- Cancel/X попереджають про незбережені зміни;
- storage/service/list UI/editor UI винесені з `main.py`.

Підстановка фактичних даних, DOCX/PDF і `DocumentArchive` до r2 не входять.

## Exact-source перевірки 10.19-r2

Для `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`:
- START/source — `43595242155` SUCCESS;
- Windows — `43595242166` SUCCESS;
- Windows 7 — `43595242114` SUCCESS;
- macOS Intel + ARM — `43595242059` SUCCESS;
- Windows / Windows 7 Defender — PASS;
- post-scan integrity/hash verification — PASS.

Publisher `43595998112` — SUCCESS.
Immutable release `v10.19-r2` target = `6414e0fbeeca3f60d8bf609bc15fbf66482e5e82`.

## Release policy

Для нової ревізії з повним успішним exact-SHA комплектом START + Windows + Windows 7 + macOS Intel + macOS ARM і пройденими security/integrity gates публікувати immutable **Test prerelease**, якщо release ще не існує. Завершені артефакти не викидати й не перебудовувати лише заради публікації.

Це правило **не змінює Stable/Latest**. Stable призначається тільки прямим рішенням власника.

## Наступна продуктова ревізія

**10.19-r3.**

Наступний slice — типізована підстановка фактичних даних у вибрану власну редакцію та in-memory чернетка для preview:
- не змінювати шаблон;
- обов'язкові відсутні поля мають давати видиму помилку;
- не використовувати сліпий replace, що руйнує блокову структуру;
- preview не створює бізнес-факту наказу/інструктажу;
- Word/PDF і архів готових документів відокремити, якщо вони роблять slice надто великим.

Подальші етапи: генерація Word/PDF/друк → окремий `DocumentArchive` → optional scan/PDF підписаного паперового оригіналу.

Supply-chain hardening (повний dependency hash lock, provenance інструментів інсталятора) лишається backlog і не блокує продуктову роботу.

## Історичний контрольний якір

Незмінний історичний контрольний випуск: **Taxo 10.3 / `v10.3`**, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Це rollback/history anchor, не поточна Stable.
