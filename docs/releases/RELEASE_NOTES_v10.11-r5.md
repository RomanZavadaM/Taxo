# Taxo 10.11-r5 — security update PDF/image dependencies

**Дата:** 06.11.2026  
**Статус:** **PRERELEASE / кандидат для користувацького тестування**.  
**Stable:** без змін, `v10.10-r5`.  
**Попередній immutable candidate:** `v10.11-r4`.

## Основна лінія Windows/macOS

- Pillow оновлено з `11.3.0` до `13.0.0`.
- pypdf оновлено з `6.19.0` до `6.21.4`.
- Це окремий security/dependency slice з Issue #175; функціональний UX, plan/fact, графіки та дані працівників не змінюються.

## Windows 7 / Python 3.8

Windows 7 лишається на окремій сумісній лінії:
- `Pillow==10.4.0` — не піднімається до Pillow 13, оскільки Pillow 13 не підтримує Python 3.8; ця Win7-версія не входить у дві Pillow advisory-range, зафіксовані в Issue #175.
- `pypdf==5.9.0` — сучасний patched pypdf 6.21.4 не підтримує Python 3.8, тому Taxo додає власний preflight page-tree budget перед будь-яким runtime flattening.

## Захист pypdf на Win7

- `src/taxo/pdf_engine.py` перевіряє PDF page tree до доступу до `reader.pages`.
- Ліміт page entries — 2 000 000, за концепцією upstream security fix.
- Додатково обмежено кількість вузлів і глибину дерева та блокуються цикли.
- Бланк підтвердження теж проходить через цей preflight; прямий runtime `PdfReader` обхід прибрано.
- Win7 workflow запускає `tests.test_v10_11_r5` на CPython 3.8.10 до packaging.

## Regression

Нові тести перевіряють:
- patched pins основної лінії;
- явну Win7 mitigation boundary;
- нормальний внутрішній PDF проходить preflight;
- синтетичне повторне “важке” page tree блокується до flattening;
- runtime Бланка підтвердження використовує захищений reader.

## Не входить

- UX Issue #164;
- CI optimization PR #142/#152;
- output/restore/backup disclosure hardening;
- загальна перебудова Win7 regression suite;
- build/release hardcoding та supply-chain pinning;
- архітектурний cleanup.

`v10.11-r4` immutable і не переписується. Stable `v10.10-r5` не змінюється.
