# Taxo — технічний стан 10.1

**Stable promotion approved:** 21.09.2026  
**New stable:** Taxo 10.1  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** v10.1-r5  
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
