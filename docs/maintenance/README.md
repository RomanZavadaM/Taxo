# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest. Promotion PR #651 / publisher #46014386874 — SUCCESS.

**Current Test:** [10.25-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r7), exact source `76f2f7c8868154374457dc7c094a2c25ed2547d2`, 8 assets, prerelease=true.

**Previous Stable:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r7 не змінює бізнес-правила наказів. Вона додає наскрізний live-control «Учасники / ТЗ»: add/edit/remove синхронізують відкритий preview, DOCX/PDF звіряються з frozen participant snapshot, history та full backup/restore зберігають identity/role/note/snapshot/sequence.

Stable/Latest лишається 10.24-r9. Previous Test 10.25-r5 завершує synthetic end-to-end приймання Інструктажів r1–r4. Current Test 10.25-r7 виправляє UX бібліотеки після owner acceptance r6: існуюча власна копія відкривається без помилки, є прямий fill/prepare шлях, людські типи, signer suggestion та A4 briefing DOCX. Issue #237 лишається open до ручного owner UI acceptance r7; unified document storage ще не починається.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремими рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
