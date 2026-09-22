# Taxo — технічний стан

## Актуальний candidate

**Дата:** 22.09.2026  
**Stable:** Taxo 10.1 / `v10.1`  
**Останній опублікований candidate:** Taxo 10.3-r5  
**Завершений candidate:** Taxo 10.3-r6 — copyright / proprietary license hardening  
**Правовласник:** Roman Zavada (Роман Завада)  
**Release:** `v10.3-r6` published  
**PR:** #58 merged  
**Next:** `10.3-r7`

Канонічний поточний стан: [../../PROJECT_STATE.md](../../PROJECT_STATE.md).  
Постійні правила: [../../PROJECT_RULES.md](../../PROJECT_RULES.md).  
Ліцензія: [../../LICENSE.md](../../LICENSE.md).

Нижче збережено історичні технічні записи попередніх checkpoint.

---

# Taxo — технічний стан 10.1

**Stable published:** 21.09.2026  
**New stable:** Taxo 10.1  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** v10.1-r5  
**Stable tag:** `v10.1`  
**Stable target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`

## Технічний baseline

10.1 зберігає всі інваріанти 10.0 і додає перевірений UI/driver-role контур.

Ключові інваріанти:
- Plan != Fact;
- exact intervals > duration-only;
- duration-only не створює вигаданих часових меж;
- overlap duration = union;
- historical conflicts не переписуються автоматично;
- absence overlay зберігає історичний графік;
- П-5 не підставляє план без підтвердження;
- технічний аудит != нормативний контроль №340;
- employment state != driver role;
- user DB не входить у реліз.

## 10.1

- новий shell: branded header + sidebar + content + status bar;
- text-free logo + dynamic enterprise name;
- personnel registry KPI/search/action hierarchy;
- driver-role persistence fix;
- Reports inside main workspace;
- single-instance detailed personnel timesheet;
- no duplicated full sidebar in secondary timesheet;
- About/Help branded windows.

## Candidate gate

v10.1-r5:
- source/START — 157 tests / OK;
- Windows — 157 tests / OK + START preflight;
- macOS ARM64 — 157 tests / OK;
- macOS Intel x86_64 — 157 tests / OK;
- manual Windows UI/navigation gate — accepted.

## Release infrastructure

- Windows: PyInstaller onedir + Inno Setup;
- macOS: native Taxo.app on ARM64 and Intel;
- START/source;
- per-platform + combined SHA-256;
- stable publisher builds from `main`;
- old tags/releases are immutable.

Фінальний звіт: [AUDIT_v10_1_STABLE.md](AUDIT_v10_1_STABLE.md).


## Stable release verification

- source — 162 tests / OK;
- Windows — 162 tests / OK + START preflight, Setup + Portable published;
- macOS ARM64 — 162 tests / OK, package published;
- macOS Intel x86_64 — 162 tests / OK, package published;
- START/source — published;
- SHA-256 manifests — published;
- GitHub Release `v10.1` — latest stable;
- stable code/release tag `v10.1` targets `fa5bbe0a5de733af1e227847ef9584daca57676e`; `main` may contain later docs-only follow-up commits without moving the immutable release tag.

Taxo 10.0 is the previous stable / rollback point.


## Active development 10.2-r4

Stable 10.1 залишається експлуатаційною базою. Активний candidate: `10.2-r4`, гілка `work/v10.2-r4-replanning`, PR #40.

Обов’язкове правило розробки:
- кожен завершений крок = нова ревізія;
- `r1 ... r10`; після `r10` — наступна minor-версія з `r1`;
- після виданого тестового архіву та сама ревізія більше не використовується;
- кожен крок завершується START-архівом і прямим посиланням для ручного тестування;
- канонічні правила: [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md).
