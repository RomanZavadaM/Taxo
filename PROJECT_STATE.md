# PROJECT_STATE — Taxo

**Дата:** 14.11.2026.

## Поточний підтверджений стан

Taxo інтегрував і опублікував продуктовий checkpoint **10.19-r1**.

- Exact product / release source: `c1357d6ba84e521bfa332f99024fbc85c8304ec3`.
- Stable/Latest: **v10.18-r3**, без змін.
- Current Test prerelease: **v10.19-r1 — Test Portable**.
- r1 release: 4 Portable + START + SHA256, без Setup.
- r8 executable publication залишається заблокованою; історичний Firefox verdict не оголошується false positive.

## Що додано в 10.19-r1

Перший slice нової системи шаблонів:
- vendor `TemplateLibrary` лишається read-only;
- створюється окрема user/company-owned копія під `CompanyTemplates`;
- копія зберігає provenance початкового package/template/revision/SHA-256;
- дублювання тієї самої vendor revision блокується;
- tamper/integrity перевірки виявляють змінену копію;
- повний backup включає `TemplateLibrary` і `CompanyTemplates`;
- symlink у цих template storage зонах відхиляється;
- storage/business logic не перенесено в `main.py`.

Редактор, Word/PDF generation і `DocumentArchive` до r1 не входять.

## Exact-source перевірки 10.19-r1

Для `c1357d6ba84e521bfa332f99024fbc85c8304ec3`:
- START/source — `43592182090` SUCCESS;
- Windows — `43592182079` SUCCESS;
- Windows 7 — `43592182138` SUCCESS;
- macOS Intel + ARM — `43592182091` SUCCESS;
- Windows / Windows 7 Defender — PASS;
- post-scan integrity/hash verification — PASS.

Publisher `43592683925` — SUCCESS.
Immutable release `v10.19-r1` target = `c1357d6ba84e521bfa332f99024fbc85c8304ec3`.

## Release policy від 14.11.2026

Для нової ревізії, яка вже має повний успішний exact-SHA комплект:
- START;
- Windows;
- Windows 7;
- macOS Intel;
- macOS ARM;
- усі обов'язкові security/integrity gates;

публікувати **immutable Test prerelease** з готових артефактів, якщо release для цієї ревізії ще не існує. Не викидати завершений кросплатформний комплект і не перебудовувати його лише заради публікації.

Це правило **не змінює Stable/Latest**. Stable призначається лише прямим рішенням власника.

## Наступна продуктова ревізія

**10.19-r2.**

Наступний slice — редактор власної копії шаблону в `CompanyTemplates`:
- vendor template не змінювати;
- підтримати великі тексти;
- коректні Save / Cancel / X та незбережені зміни;
- редактор і storage-логіку тримати окремими модулями;
- не змішувати цей slice з Word/PDF/готовими документами.

Подальші етапи після цього: підстановка даних → формування Word/PDF/друк → окремий `DocumentArchive` → optional scan/PDF підписаного паперового оригіналу.

Подальший supply-chain hardening (повний dependency hash lock, provenance інструментів інсталятора) лишається backlog і не блокує продуктову роботу.

## Історичний контрольний якір

Незмінний історичний контрольний випуск: **Taxo 10.3 / `v10.3`**, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`. Це rollback/history anchor, не поточна Stable.
