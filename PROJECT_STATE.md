# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 15.11.2026.**

- Завершений product checkpoint: **10.19-r8** (PR #437).
- Exact product/source SHA `4829bc7e3369442cc7cee7ad9ec8797fc26362e5`.
- Test prerelease [v10.19-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r8), publisher `43748041618` SUCCESS; 4 portable + START + SHA256.
- Stable/Latest: **v10.18-r3** unchanged.
- Release PR #438 merged as `882c9d5e44f919d63edd0f4574416838a82f503f`.

## Функціональний результат

На прохання власника пріоритет наступного r8 slice змінено з PDF/print на зв'язок чернетка → DOCX → реєстр. Додано явне збереження generated DOCX з immutable PreparedDocuments snapshot у вже наявний PaperDocuments/catalog, з provenance exact template revision та snapshot ID. Статус prepared не дорівнює виданому, затвердженому чи підписаному документу. Старі записи/бази не переписуються. Legacy каталог показує новий Word як документ.

## CI та security gates

Exact-main: START `43747281993`, Windows `43747281941`, Win7 `43747281957`, macOS Intel/ARM `43747281991` — всі SUCCESS. Windows/Win7 Defender і post-scan integrity PASS; publisher `43748041618` SUCCESS.

## Наступна ревізія

**10.19-r9** — контрольоване повторне відкриття збережених PreparedDocuments і запис відредагованого зовні DOCX як нової версії без перезаписування попередньої. PDF/print і DocumentVault лишаються окремими наступними етапами. Нові зразки не вносити у read-only TemplateLibrary; CompanyTemplates — користувацькі копії.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; `WORKLOG.md` — історія.
