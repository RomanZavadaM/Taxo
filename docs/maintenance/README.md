# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, prerelease=false.

**Current Test:** [10.24-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r4), exact source `e1616ea0063575b2c989d684934364f38f995966`, 8 canonical assets, prerelease=true. Exact-source START/Windows/Win7/macOS Intel/ARM — SUCCESS; Windows/Win7 Defender/integrity PASS; publisher #45162074730 SUCCESS.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

r4 додає explicit actual «Отримано… / Надіслано…», forward-only state transitions, append-only history та due/overdue control. Перший minimum-viewport test виявив, що «Отримано…» могла бути невидимою при 760×520; тест не послаблювали, layout виправлено винесенням action rows у постійну нижню панель, після чого повний CI пройшов.

Stable 10.24-r3 не змінено. Automatic e-mail, cases/threads, OCR/AI APPLY і physical attachment purge залишаються окремими наступними рішеннями. Історичні аудити не переписувати заднім числом; актуальний стан — у CHECKPOINT_CURRENT/PROJECT_STATE.
