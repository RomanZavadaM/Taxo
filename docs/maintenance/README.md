# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, prerelease=false.

**Current Test:** [10.24-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r6), exact source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`, 8 canonical assets, prerelease=true. 55 strict live routes загалом / 17 correspondence routes. Exact-source START/Windows/Win7/macOS Intel/ARM — SUCCESS; Windows/Win7 Defender/integrity PASS; publisher #45209524416 SUCCESS.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r6 не додає нової бізнес-функції. Вона переводить критичні correspondence actions r1–r5 у strict executable route contract: mapped + onscreen + usable + activation.

Stable 10.24-r3 не змінено. Наступний окремий пакет — PR #630 з end-to-end контролем учасників наказу після rebase на актуальний main і повторного CI.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремими рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
