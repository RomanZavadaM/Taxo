# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Previous stable / rollback:** Taxo 9.0.1  
**Verified candidate:** v9.1-r9.8  
**Stable release:** v10.0

## Статус

Manual operational gate завершено. Лінія 9.1 більше не є поточним candidate-напрямком; вона стала основою stable 10.0.

## Що підтверджено

- START запускається у Windows після повного розпакування;
- START.bat сумісний із cmd.exe;
- місячний графік має пряме відкриття деталізації;
- шляхівки однієї зміни мають єдиного лікаря/механіка;
- overnight не підтягує staff наступної дати;
- П-5, Персонал, аудит, №340, архів бланків і місячний контроль входять у stable;
- бази/скани/персональні файли не публікуються.

## Build matrix 10.0

- Windows x64 Setup;
- Windows x64 Portable;
- macOS ARM64;
- macOS Intel x86_64;
- START/source;
- SHA-256.

## Політика

- `main` = stable 10.0;
- `v10.0` = immutable stable tag/release;
- `v9.1-r5` … `v9.1-r9.8` = історія;
- наступні зміни — нова work branch + PR.

Повний аудит: [AUDIT_v10_0_STABLE.md](AUDIT_v10_0_STABLE.md).
