# PROJECT_STATE — Taxo

**Дата фіксації:** 21.09.2026  
**Поточна stable:** Taxo 10.1  
**Попередня stable / rollback:** Taxo 10.0  
**Verified candidate:** v10.1-r5  
**Stable tag:** `v10.1`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Verified candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`  
**PR #34:** merged  
**Stable audit:** `docs/maintenance/AUDIT_v10_1_STABLE.md`  
**Release notes:** `docs/releases/RELEASE_NOTES_v10_1.md`

## Рішення про stable 10.1

21.09.2026 користувач завершив ручний Windows gate і явно дозволив merge у `main`, multi-platform release та публікацію.

10.1 промотує перевірену лінію `v10.1-r1` … `v10.1-r5`. Старі tags/releases лишаються immutable.

## Ключові зміни 10.1

- виправлено змішування `drivers.active`, `employees.active` і ролі `Водій`;
- завершення ролі водія не звільняє працівника і не самовідновлюється після restart;
- `driver_end_date` зберігається окремо;
- новий application shell із затвердженим text-free логотипом;
- динамічна назва підприємства у шапці й вікнах;
- реєстр працівників із KPI, пошуком і впорядкованими діями;
- «Звіти» працюють у головному workspace;
- детальний табель single-instance, без дубльованого повного sidebar;
- PDF/Excel, П-5, баланс, контроль і папка звітів збережені;
- «Про програму» та «Довідка» оформлені у новому стилі.

## Перевірка перед stable

v10.1-r5:
- source/START — 157 tests / OK;
- Windows — 157 tests / OK + START preflight;
- macOS ARM64 — 157 tests / OK;
- macOS Intel x86_64 — 157 tests / OK;
- ручний Windows navigation/UI gate — підтверджено.

## Дані

- схема БД у 10.1 не змінюється;
- наявне робоче сховище зберігається;
- повторне введення даних не потрібне;
- retention робочих даних — 48 місяців;
- робочі бази, скани, кеші та персональні документи не публікуються.

## Stable release result

1. PR #34 — merged у `main`.
2. Stable target — `fa5bbe0a5de733af1e227847ef9584daca57676e`.
3. Source verify — **162 tests / OK**.
4. Windows stable build — **162 tests / OK**, START preflight OK, Setup + Portable success.
5. macOS ARM64 — **162 tests / OK**, native Taxo.app package success.
6. macOS Intel x86_64 — **162 tests / OK**, native Taxo.app package success.
7. START/source package — success.
8. Per-platform і combined SHA-256 manifests — published.
9. GitHub Release `v10.1` — published as latest stable, 10 assets.
10. `main` + immutable `v10.1` є новим stable source of truth; `v10.0` — rollback.

Офіційні пакети:
- `Taxo_v10_1_Setup_Windows_x64.exe`;
- `Taxo_v10_1_Windows_x64_Portable.zip`;
- `Taxo_v10_1_macOS_arm64_Portable.zip`;
- `Taxo_v10_1_macOS_x86_64_Portable.zip`;
- `Taxo_v10_1_START.zip`;
- per-platform та combined SHA-256.
