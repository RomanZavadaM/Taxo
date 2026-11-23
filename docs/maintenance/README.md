# Maintenance / контрольні матеріали Taxo

**Stable/Latest:** [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3), exact source `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`, 8 canonical assets, prerelease=false. Promotion PR #620 passed START/Windows/Win7/macOS; publisher #45147941030 and guarded stable verification #45147941048 — SUCCESS.

**Попередня Stable:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4). **Current Test:** окремого новішого published Test немає. 10.24-r4 — наступна development revision, не Stable.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Індекс релізів](../releases/RELEASE_INDEX.md)
- [Стан продукту](../PRODUCT_STATUS.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

Stable 10.24-r3 містить r1 registry, r2 controlled attachments та r3 journal/card UI кореспонденції. Порожній sent_date не означає sent. Prep r4 PR #619 поки не merged: minimum-viewport test 760×520 виявив недоступну кнопку «Отримано…». Наступний крок — виправити layout без послаблення regression test, потім повторити повний CI.

Історичні аудити не переписувати як нібито виконані на новішій версії; їхній тодішній стан зберігається, а актуальний — у CHECKPOINT_CURRENT/PROJECT_STATE.
