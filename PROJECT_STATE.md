# PROJECT_STATE — Taxo

**Дата:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest full multi-platform checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`.
- **Main merge:** PR #84 → `0151fea9a2a27bf8e970ca71ef9786a2d750d0ab`.
- **Issued r3 source/tag target:** `97e646936d14d163faf93882daf7894f5bb38ab6` — immutable.
- **Regression:** `530/530 OK`.
- **START verify run:** `36434131185` — success.
- **Original START publisher:** `36434348730` — success.
- **Full multi-platform package gate:** build run `36439848549`; all source/Windows/Win7/macOS build jobs success; initial publish-only normalization step failed without invalidating builds.
- **Full asset publisher retry:** `36440880324` — success.
- **Final PR gates:** Windows `36441149032` — success; macOS `36441148816` — success.
- **Release:** https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3
- **Release START SHA-256:** `ea97909e7ae8a895730172aef4f6cabf61c18c227adce12cdaec803dfe8c490c`.
- **Next code revision:** тільки **10.6-r4**.
- **Live ledger:** Issue #61.

`v10.3` залишається stable до окремого рішення власника. `v10.6-r3` є повним multi-platform checkpoint у `main`, але не stable promotion.

## Що інтегровано після 10.5-r8

### 10.5-r9 / 10.6-r2 — шляхівки поза регулярним маршрутом

- шляховий лист може видаватися, навіть якщо робочий день не має регулярного `route_id`;
- підтримуються замовлення, розвозки, поїздки по місту, області, міжобласні та інші разові роботи;
- плановий час виїзду/повернення береться з графіка водія;
- якщо автобус не призначено, його можна вибрати при видачі; це планове призначення, а не тахографічний факт;
- поле «Поїздка / замовник» редагується довільно; типове значення — «по області»;
- для нерегулярної роботи не друкується вигаданий регулярний маршрутний розклад;
- для реального регулярного маршруту сувора route/stops validation збережена.

### 10.5-r10 — межа plan / fact в аудиті графіків

- аудит конкретного дня не порівнює історичний/перепланований план дня з поточним редагованим шаблоном маршруту;
- фактичні `fact_work_*` залишаються окремим шаром і не підміняють план;
- аудит нічого автоматично не переписує.

### 10.6-r1 — реєстр документів ТЗ

- у вікні «Транспортні засоби — реєстр документів» прапорець **«Сховати неактивні автомобілі»** увімкнений за замовчуванням;
- вимкнення фільтра повертає весь парк;
- фільтр змінює лише видимість, не статуси/картки/документи.

### 10.6-r2 — UI

- вікно «Про програму» ущільнене й адаптивне по висоті, щоб нижня кнопка не обрізалась на невисоких/масштабованих екранах.

### 10.6-r3 — зворот нерегулярної шляхівки

- очищаються лише regular-route поля `start_direction`, `outbound_stops`, `return_stops`;
- лікар I/II, механік I/II, показники спідометра та фактичний пробіг зберігаються й друкуються, якщо реально є в Taxo;
- проведено аудит issuer → PDF renderer для автоматично заповнюваних полів;
- графа **«Графік»** (`schedule_code`) не заповнюється вигаданим значенням: у поточній моделі немає канонічного коду графіка;
- ДАІ/служба руху, лінійний контроль, причина заїзду, підписи та інші фактичні відмітки без джерела залишаються ручними.

## Повний пакет 10.6-r3

Release містить:

- Windows x64 Setup;
- Windows x64 Portable;
- Windows 7 SP1 x64 Setup;
- Windows 7 SP1 x64 Portable;
- macOS ARM64 Portable;
- macOS Intel x86_64 Portable;
- START/source;
- platform SHA-256 manifests і `SHA256SUMS_v10_6_r3_FULL.txt`.

Tag `v10.6-r3` не пересувався: усі executable-пакети зібрані з exact issued source `97e646936d14d163faf93882daf7894f5bb38ab6`.

## Постійні межі даних

- робочі БД, SQLite, скани, кеші та персональні документи не публікуються;
- оновлення програми не повинно стирати або підміняти робочі дані;
- державні XLSX/CSV — джерело звірки/доповнення, а не заміна робочої БД;
- raw snapshots державних витягів не переписуються локальними змінами;
- порожнє значення в держреєстрі не видаляє локальне значення автоматично;
- локальне редагування в Taxo не означає зміну даних у Дії, «Оберіг» або «Шлях»;
- імпорт державного XLSX сам по собі не означає офіційно завершене звіряння;
- планові дані не оголошуються фактом без явного підтвердження.

## Windows 7

Окрема compatibility line: CPython 3.8.10 x64 + PyInstaller 5.13.2 + `requirements-win7.txt`, `Taxo_win7.spec` і PE compatibility gate `scripts/check_win7_pe.py`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61.

## Наступний крок

10.6-r3 повністю інтегрований у `main` і виданий для всіх підтримуваних систем. Наступна кодова зміна — тільки **10.6-r4** у новій work-гілці. Stable `v10.3` не пересувати без окремого рішення власника.
