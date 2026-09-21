# PROJECT_STATE — Taxo

**Дата фіксації:** 21.09.2026  
**Поточна stable:** Taxo 10.1  
**Stable tag:** `v10.1`  
**Stable release target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Previous stable / rollback:** Taxo 10.0  
**Previous stable target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Verified candidate:** `v10.1-r5`  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**PR #34:** merged  
**Stable audit:** `docs/maintenance/AUDIT_v10_1_STABLE.md`  
**Release notes:** `docs/releases/RELEASE_NOTES_v10_1.md`

## Результат stable 10.1

Taxo 10.1 успішно злитий у `main` і опублікований як GitHub stable release.

Stable publisher:
- source verify — **162 tests / OK**;
- Windows — **162 tests / OK** + START preflight OK;
- Windows x64 Setup — success;
- Windows x64 Portable — success;
- macOS ARM64 — **162 tests / OK**, native Taxo.app — success;
- macOS Intel x86_64 — **162 tests / OK**, native Taxo.app — success;
- START/source — success;
- per-platform SHA-256 — success;
- combined `SHA256SUMS_v10_1.txt` — success;
- GitHub Release `v10.1` — published, **10 assets**.

## Ключові зміни 10.1

- статус працівника відокремлено від ролі `Водій`;
- завершення ролі водія не звільняє працівника і не самовідновлюється після restart;
- `driver_end_date` зберігається окремо;
- новий application shell: світла шапка, синій sidebar, центральна робоча область, status bar;
- затверджений text-free логотип;
- динамічна назва підприємства у шапці й вікнах;
- реєстр працівників із KPI, пошуком і впорядкованими діями;
- «Звіти» працюють у головному workspace;
- «Працівники» повертає саме реєстр;
- детальний табель — single-instance і без дубльованого повного sidebar;
- PDF/Excel, П-5, місячний баланс, контроль і папка звітів збережені;
- «Про програму» та «Довідка» оформлені у єдиному стилі.

## Дані

- схема БД у 10.1 не змінюється;
- наявне робоче сховище зберігається;
- повторне введення даних не потрібне;
- retention робочих даних — 48 місяців;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у GitHub release.

## Stable packages

- `Taxo_v10_1_Setup_Windows_x64.exe`;
- `Taxo_v10_1_Windows_x64_Portable.zip`;
- `Taxo_v10_1_macOS_arm64_Portable.zip`;
- `Taxo_v10_1_macOS_x86_64_Portable.zip`;
- `Taxo_v10_1_START.zip`;
- `SHA256SUMS_v10_1_Windows_x64.txt`;
- `SHA256SUMS_v10_1_macOS_arm64.txt`;
- `SHA256SUMS_v10_1_macOS_x86_64.txt`;
- `SHA256SUMS_v10_1_START.txt`;
- `SHA256SUMS_v10_1.txt`.

## Source of truth

`main` + protected/immutable release tag `v10.1` є новим stable source of truth.  
`v10.0` лишається rollback.  
`v10.1-r1` … `v10.1-r5` лишаються historical immutable checkpoints.
