# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, prerelease=false.

**Current Test:** [10.24-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r5), exact source `6d697a641b4f546dc533c8f55379696ad827b278`, 8 canonical assets, prerelease=true. Exact-source START/Windows/Win7/macOS Intel/ARM — SUCCESS; Windows/Win7 Defender/integrity PASS; publisher #45193506957 SUCCESS.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r5 додає logical correspondence cases/topics у окремому `Data/CorrespondenceCases`: explicit membership, archive/read-only, thread candidates з наявних response/related links, third «Справи» tab і full backup/restore. Case membership не копіює документи, не змінює реєстраційні номери та не створює sent/received/status.

Перший prep START зберіг строгий r1 boundary: `cases.json` не дозволили покласти у `Data/Correspondence`, тому case-store винесено в окремий sibling store замість послаблення guard. Другий START знайшов stale test path і неоднозначну кнопку «Оновити»; виправлено path та назву «Оновити справи» без послаблення reachability.

Stable 10.24-r3 не змінено. Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремими рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
