# Taxo — технічний стан 10.1

**Stable:** Taxo 10.1  
**Tag:** `v10.1`  
**Target:** `fa5bbe0a5de733af1e227847ef9584daca57676e`  
**Previous stable / rollback:** Taxo 10.0  
**Verified candidate:** v10.1-r5  
**Date:** 21.09.2026

## Технічний baseline

10.1 зберігає інваріанти 10.0 і додає перевірений UI/driver-role контур:
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

## Перевірка stable

- source — 162 tests / OK;
- Windows — 162 tests / OK + START preflight;
- Windows Setup/Portable — success;
- macOS ARM64 — 162 tests / OK + Taxo.app;
- macOS Intel x86_64 — 162 tests / OK + Taxo.app;
- START/source — success;
- SHA-256 manifests — success;
- GitHub Release v10.1 — published, 10 assets.

## Релізна інфраструктура

- Windows: PyInstaller onedir + Inno Setup;
- macOS: native Taxo.app ARM64 + Intel;
- START/source;
- stable publisher from `main`;
- old tags/releases immutable.

Фінальний аудит: [AUDIT_v10_1_STABLE.md](AUDIT_v10_1_STABLE.md).
