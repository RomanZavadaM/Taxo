# Супровід Taxo 10.x

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 файлів, 37 strict live UI routes. START/Windows/Win7/macOS Intel/ARM — SUCCESS; Defender/integrity PASS. Owner manual acceptance 20.11.2026; stable promotion #44811800328 — SUCCESS.

**Попередня Stable:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1). **Current Test:** [10.23-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r9), exact source `9f41c46a4745815cfc7518f7319f6c6f941ba559`, 8 assets, prerelease. Read-only ANALYZE→PROPOSE metadata hints; v10.23-r3 не публікувався.

- [Поточний стан](../../PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Політика main](MAIN_BRANCH_POLICY.md)
- [Чекліст релізу](RELEASE_CHECKLIST.md)
- [Захист функцій](FUNCTION_PRESERVATION_FULL_COVERAGE_2026-11-19.md)
- [Правила розробки](DEVELOPMENT_RULES.md)

10.23-r9 опубліковано як Current Test. AI-ready нормативна документація вже в main; r6 = read-only INVENTORY, r7 = atomic dry-run batch store, r8 = verified deterministic preview, r9 = read-only ANALYZE→PROPOSE metadata hints. Наступний пакет — 10.23-r10: REVIEW із явними confirm/reject/needs_review рішеннями, що зберігаються окремо й нічого не APPLY. Після r10 — окремий модуль вхідної/вихідної кореспонденції. Історичні аудити не переписувати як нібито вони були виконані на r4; їхній актуальний статус уточнюється окремими checkpoint-файлами.
