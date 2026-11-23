# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, prerelease=false.

**Current Test:** [10.24-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r8), exact source `d24b1bc96115de52d6088813992aca3b410fe243`, 8 canonical assets, prerelease=true. 58 strict live routes загалом; r8 додає fresh-reopen preservation control для order participant block поверх r7, correspondence contract лишається exact 17 routes. Exact-source START/Windows/Win7/macOS Intel/ARM — SUCCESS; Windows/Win7 Defender/integrity PASS; publisher #45237831016 SUCCESS.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r7 не змінює бізнес-правила наказів. Вона додає наскрізний live-control «Учасники / ТЗ»: add/edit/remove синхронізують відкритий preview, DOCX/PDF звіряються з frozen participant snapshot, history та full backup/restore зберігають identity/role/note/snapshot/sequence.

Stable 10.24-r3 не змінено. Після recovery наступний крок — звірити #553/#556/#562 і вибрати один bounded control slice для r8.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремими рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
