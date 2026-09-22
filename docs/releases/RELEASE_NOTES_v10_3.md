# Taxo 10.3

**Stable release — 22.09.2026**  
**Previous stable / rollback:** Taxo 10.1  
**Verified candidate before stable:** v10.3-r6  
**Manual operational gate:** підтверджено користувачем 22.09.2026

Taxo 10.3 переводить перевірену лінію 10.3-r1…r6 у стабільну експлуатаційну версію.

## Бланки підтвердження і фактичні межі

- межі маршруту/тахокарти не прирівнюються до повної робочої зміни;
- plan і fact зберігаються окремо;
- фактичні відхилення можуть уточнювати підготовлений бланк без стирання плану;
- 14/15/16 можуть впливати на фактичні межі роботи, 17/18/19 не трактуються як відпочинок;
- короткі реальні інтервали не приховуються порогом «10/15 хв»;
- неоднозначні проміжки не поглинаються автоматично;
- між роботою і відпочинком може бути ручний некласифікований час, який Taxo не додає автоматично ні в оплачувану роботу, ні в безперервний відпочинок.

## Архів бланків

- коректне сортування реальних дат/часу;
- режими «Останні створені/змінені», «Період — новіші», «Період — старіші»;
- лічильники відповідають тому самому фільтру водія/місяця;
- «Підставити у форму» та «Уточнити фактичні межі» працюють контекстно.

## Авторські права і ліцензія

- правовласник: **Roman Zavada (Роман Завада)**;
- Copyright © 2026 Roman Zavada. All rights reserved;
- Taxo — proprietary software;
- `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md` входять у source/START та executable bundles;
- назва підприємства у робочій БД не змінює правовласника;
- сторонні бібліотеки залишаються під власними ліцензіями.

## Перевірка

Перед stable promotion актуальний main після r6 пройшов START/source, Windows і macOS GitHub Actions; користувач вручну протестував `Taxo_v10_3_candidate_r6_START.zip`. Stable publisher повторно виконує regression suite для source, Windows і обох macOS architectures, Windows START preflight та packaging checks.

## Офіційні пакети

- `Taxo_v10_3_Setup_Windows_x64.exe`
- `Taxo_v10_3_Windows_x64_Portable.zip`
- `Taxo_v10_3_macOS_arm64_Portable.zip`
- `Taxo_v10_3_macOS_x86_64_Portable.zip`
- `Taxo_v10_3_START.zip`
- per-platform та combined SHA-256 manifests.

`v10.3-r6` і `v10.1` залишаються immutable historical/rollback checkpoints. Наступна кодова зміна після stable 10.3 — **10.3-r7**.
