# PROJECT_STATE — Taxo

**Дата:** 14.11.2026.

## Поточний підтверджений стан

Taxo інтегрував і опублікував коригувальний checkpoint **10.19-r3**.

- Exact product / release source: `a89291553bca88a1b792d45f56cc99d5e93876b7`.
- Stable/Latest: **v10.18-r3**, без змін.
- Current Test prerelease: **v10.19-r3 — Test Portable**.
- r3 release: 4 Portable + START + SHA256, без Setup.
- `v10.19-r2` залишається виданим історичним prerelease і не переписується.

## Причина r3

Після випуску 10.19-r2 статичний перегляд виявив UI-thread defect:
background save-worker редактора читав Tk `StringVar` через `title.get()`.

CI r2 цього не зловив, бо проблема є thread-safety ризиком, а не гарантованим deterministic crash.

У 10.19-r3:
- значення Tk читається в UI thread до старту worker;
- worker отримує plain Python string;
- regression-тест забороняє повернення Tk read у save-worker;
- функціональна поведінка CompanyTemplates з r2 не розширювалась.

## Exact-source перевірки 10.19-r3

Для `a89291553bca88a1b792d45f56cc99d5e93876b7`:
- START/source — `43598231924` SUCCESS;
- Windows — `43598231921` SUCCESS;
- Windows 7 — `43598231945` SUCCESS;
- macOS Intel + ARM — `43598231954` SUCCESS;
- Windows / Windows 7 Defender — PASS;
- post-scan integrity/hash verification — PASS.

Publisher `43599116472` — SUCCESS.
Immutable release `v10.19-r3` target = `a89291553bca88a1b792d45f56cc99d5e93876b7`.

## Release policy

Для нової ревізії з повним успішним exact-SHA комплектом START + Windows + Windows 7 + macOS Intel + macOS ARM і пройденими security/integrity gates публікувати immutable **Test prerelease**, якщо release ще не існує.

Це правило **не змінює Stable/Latest**. Stable призначається тільки прямим рішенням власника.

## Наступна продуктова ревізія

**10.19-r4.**

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
