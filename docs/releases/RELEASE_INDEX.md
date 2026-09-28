# Індекс релізів Taxo

**Стан:** 29.09.2026  
**Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) — immutable  
**Latest full multi-platform checkpoint:** [Taxo 10.6-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10)  
**Latest integrated code checkpoint in `main`:** Taxo **10.6-r10** — merged via PR #87  
**Next code revision:** **10.7-r1**.

> `v10.3` лишається stable до окремого рішення власника. `v10.6-r10` — поточний інтегрований і повний multi-platform checkpoint; це не автоматичне stable promotion.

## Поточний checkpoint

| Ревізія | Main / issued source | Перевірка | Пакети / зміст |
|---|---|---|---|
| **10.6-r10** | main merge `4bc63060be9911fcf20f432b5e6535b4d8cd0155`; tag source `0baad010d0c0d4f29db62f26c29d512c71058928` | `588/588 OK`; START `36476665666`; full build `36485005797`; binary publisher `36485643153` | Windows x64 Setup/Portable, Windows 7 SP1 x64 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256; P-5 PDF/XLSX EDRPOU fix |

## Taxo 10.6 history

| Ревізія | Issued source | Перевірка | Зміст |
|---|---|---|---|
| **10.6-r10** | `0baad010d0c0d4f29db62f26c29d512c71058928` | `588/588 OK`; full build `36485005797`; publisher `36485643153`; PR #87 merged | full multi-platform checkpoint; P-5 PDF/XLSX EDRPOU compatibility fix |
| 10.6-r9 | `2705fb5c9105e21bfb669a2d40d4f29449e1a00b` | `578/578 OK`; START `36472489549`; publisher `36472783754` | адаптивний header картки документів ТЗ |
| 10.6-r8 | `09f0e6e6cf3809b6d0efc6c9cdad7937a44d78d3` | `570/570 OK`; START `36469618323` | адаптивна форма документа ТЗ |
| 10.6-r7 | `e3f1666bafbd82e37ac2e63b08bfed2d265bae30` | `562/562 OK`; START `36463667268` | адаптивна панель дій картки документів ТЗ |
| 10.6-r6 | `90ab67ae00be381f8b2bc14e18f9614574e3493f` | `554/554 OK`; START `36462366765` | адаптивна панель команд реєстру ТЗ |
| 10.6-r5 | `118d4111e183528c49e8060e8782479fa4436377` | `546/546 OK`; START `36452858366` | адаптивні фільтри звіту документів ТЗ |
| 10.6-r4 | historical immutable checkpoint | fast-test | адаптивний action bar вікна шляхівок |
| **10.6-r3** | `97e646936d14d163faf93882daf7894f5bb38ab6` | `530/530 OK`; full assets `36440880324`; merged via PR #84 | previous full multi-platform checkpoint; нерегулярні шляхівки, plan/fact audit, UI fixes |
| 10.6-r2 | `4d976bc7686015c00a3af5387634e8486cefc48b` | `519/519 OK` | нерегулярні поїздки без обов'язкового route_id; адаптивне «Про програму» |
| 10.6-r1 | `e4823947d3c5d28af54fd4337bdaf0daf02b4201` | `507/507 OK` | default-on приховування неактивних ТЗ у реєстрі документів |

## Останні повні multi-platform checkpoints

| Tag | Статус | Пакети |
|---|---|---|
| [v10.6-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10) | **Latest full multi-platform checkpoint** | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, platform/full SHA-256 |
| [v10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3) | previous full checkpoint | Windows x64 Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel, START, SHA-256 |
| [v10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8) | historical | Windows x64/Win7, macOS ARM64/Intel, START, SHA-256 |
| [v10.4-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.4-r2) | historical | Windows x64/Win7, macOS ARM64/Intel, START, SHA-256 |

## Historical identity anchors

- **Taxo 10.4-r7** — historical issued source `9f397a092fe828570927bc39cef7a3a467e2aff0`; межа між локальним контролем документів ТЗ та державними реєстрами. Checkpoint **immutable** і не використовується як нова база, але його точна ідентичність зберігається для regression/history.

## Stable line

| Tag | Статус |
|---|---|
| [v10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3) | **Current stable** |
| [v10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1) | Previous stable / rollback |
| [v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0) | Historical stable |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | Historical stable |

## Документи поточної лінії

- [Release notes 10.6-r10](RELEASE_NOTES_v10.6-r10.md)
- [Release notes 10.6-r9](RELEASE_NOTES_v10.6-r9.md)
- [Release notes 10.6-r8](RELEASE_NOTES_v10.6-r8.md)
- [Release notes 10.6-r7](RELEASE_NOTES_v10.6-r7.md)
- [Release notes 10.6-r6](RELEASE_NOTES_v10.6-r6.md)
- [Release notes 10.6-r5](RELEASE_NOTES_v10.6-r5.md)
- [Release notes 10.6-r4](RELEASE_NOTES_v10.6-r4.md)
- [Release notes 10.6-r3](RELEASE_NOTES_v10_6_r3.md)

Точна історія старіших revision збережена в Git history, release notes та Issue #61. Старі work/candidate branches не використовуються як нова кодова база.

## Release policy

1. Stable формується тільки після manual operational gate та окремого рішення власника.
2. Виданий tag/release не пересувається і не перевидається поверх іншого коду.
3. Full multi-platform checkpoint містить Windows, Windows 7 compatibility packages, macOS packages, START та checksums.
4. БД, SQLite, скани, кеші та персональні документи не публікуються.
5. Кодові зміни йдуть через окрему work branch і PR.
6. «Злити у main» = перевірки → інтеграція → синхронізація документації → повні пакети/checksums, якщо не вказано інше.
