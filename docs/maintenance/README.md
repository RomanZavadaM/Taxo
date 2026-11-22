# Супровід Taxo 10.x

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 файлів, 37 strict live UI routes. START/Windows/Win7/macOS Intel/ARM — SUCCESS; Defender/integrity PASS. Owner manual acceptance 20.11.2026; stable promotion #44811800328 — SUCCESS.

**Попередня Stable:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1). **Current Test:** [10.24-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r2), exact source `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`, 8 assets, prerelease. Два журнали кореспонденції + controlled immutable attachments/live DocumentVault links; v10.23-r3 не публікувався.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Політика main](MAIN_BRANCH_POLICY.md)
- [Чекліст релізу](RELEASE_CHECKLIST.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

10.24-r2 опубліковано як Current Test. r6–r10 завершують AI-ready перед-APPLY цикл без APPLY. r1 додає incoming/outgoing registry; r2 — immutable attachment store, live vault links, history-only remove і full backup/restore. Наступний пакет — 10.24-r3: UI журналів і картка кореспонденції без e-mail automation. Історичні аудити не переписувати як нібито вони були виконані на r4; їхній актуальний статус уточнюється окремими checkpoint-файлами.
