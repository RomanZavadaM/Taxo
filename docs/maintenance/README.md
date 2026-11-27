# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest. Promotion PR #651 / publisher #46014386874 — SUCCESS.

**Current Test:** [10.25-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r4), exact source `ed3b79a96659aa011f60fa7912092fbc15157cdb`, 8 assets, prerelease=true.

**Previous Stable:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r7 не змінює бізнес-правила наказів. Вона додає наскрізний live-control «Учасники / ТЗ»: add/edit/remove синхронізують відкритий preview, DOCX/PDF звіряються з frozen participant snapshot, history та full backup/restore зберігають identity/role/note/snapshot/sequence.

Stable/Latest лишається 10.24-r9. Previous Test 10.24-r10 завершує synthetic end-to-end контроль наказів. Previous Test 10.25-r1 закриває planning core. Previous Test 10.25-r2 закриває квартальний live-view. Previous Test 10.25-r3 закриває program revisions + cumulative employee selection + exact prepared DOCX link. Current Test 10.25-r4 закриває event briefing + explicit manual conducted evidence + read-only audit. Next: 10.25-r5 full Instructions end-to-end acceptance. Після кожного завершеного етапу — virtual acceptance і окремий Test release.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремими рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
