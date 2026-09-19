# Taxo — технічний стан 10.0

**Stable:** Taxo 10.0  
**Previous stable / rollback:** 9.0.1  
**Verified candidate:** v9.1-r9.8  
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

Перед merge:
- весь unittest suite;
- Windows START full/incomplete preflight;
- Windows source CI;
- macOS ARM64 source CI;
- macOS Intel source CI.

Після merge stable publisher повторює тести і будує executable artifacts.

Фінальний звіт: [AUDIT_v10_0_STABLE.md](AUDIT_v10_0_STABLE.md).
