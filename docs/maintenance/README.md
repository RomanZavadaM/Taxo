# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, prerelease=false.

**Current Test:** [10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=true. Vehicle-document Taxo-owned copies + source/size/SHA-256, actual file-state, selected backup/restore integrity and archive preservation. Exact-source START/Windows/Win7/macOS Intel/ARM — SUCCESS; Windows/Win7 Defender/integrity PASS; publisher #46004721962 SUCCESS.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r9 посилює збереження документів ТЗ: непорожній DB path більше не вважається доказом файла; selected vehicle-document backup перевіряє bytes та архівовані записи, а restore повторно перевіряє DB→file. Історично відсутні bytes без доступного source/backup автоматично не відновлюються.

Stable 10.24-r3 не змінено. Після recovery наступний крок — ручне приймання #642 на реальному робочому сховищі. Наступна кодова ревізія — 10.24-r10.

Automatic e-mail/mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge лишаються окремими рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
