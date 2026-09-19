# Taxo — технічний стан 10.0

**Stable:** Taxo 10.0  
**Previous stable / rollback:** 9.0.1  
**Verified candidate:** v9.1-r9.8  
**Release target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**Date:** 19.09.2026

## Технічний baseline

Taxo 10.0 є стабілізованим результатом лінії 9.1. Ручний operational gate завершено; користувач підтвердив перехід у `main`.

Ключові інваріанти:
- Plan != Fact;
- exact intervals > duration-only;
- duration-only не створює вигаданих часових меж;
- overlap duration = union;
- historical conflicts не переписуються автоматично;
- absence overlay зберігає історичний графік;
- П-5 не підставляє план без підтвердження;
- технічний аудит != нормативний контроль №340;
- role+date+shift — один операційний slot лікаря/механіка;
- user DB не входить у реліз.

## Релізна інфраструктура

- Windows build: PyInstaller onedir + Inno Setup;
- macOS build: native Taxo.app окремо на ARM64 та Intel;
- START/source package;
- SHA-256 per-platform + combined manifest;
- stable publisher працює з commit у `main`;
- `v10.0` не перезаписується.

## Перевірка

Фінальний stable publisher завершився успішно:
- source verify — 117 tests / OK;
- Windows — 117 tests / OK + START full/incomplete preflight;
- Windows Setup/Portable — success;
- macOS ARM64 — 117 tests / OK + native Taxo.app;
- macOS Intel x86_64 — 117 tests / OK + native Taxo.app;
- START/source package — success;
- per-platform і combined SHA-256 — success;
- GitHub Release v10.0 — published.

Фінальний звіт: [AUDIT_v10_0_STABLE.md](AUDIT_v10_0_STABLE.md).
