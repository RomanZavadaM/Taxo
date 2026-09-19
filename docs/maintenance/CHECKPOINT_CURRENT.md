# Taxo — поточна контрольна точка

**Stable:** Taxo 10.0 · 19.09.2026  
**Previous stable / rollback:** Taxo 9.0.1  
**Verified candidate:** v9.1-r9.8  
**Stable release:** v10.0  
**Release target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`

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

## Build matrix 10.0 — success

- Windows x64 Setup — published;
- Windows x64 Portable — published;
- macOS ARM64 — published;
- macOS Intel x86_64 — published;
- START/source — published;
- SHA-256 per-platform + combined — published;
- Windows/macOS/source regression suites — 117 tests / OK.

## Політика

- `main` = stable 10.0;
- `v10.0` = immutable stable tag/release;
- `v9.1-r5` … `v9.1-r9.8` = історія;
- наступні зміни — нова work branch + PR.

Повний аудит: [AUDIT_v10_0_STABLE.md](AUDIT_v10_0_STABLE.md).
