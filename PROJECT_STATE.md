# PROJECT_STATE — Taxo

**Дата:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`.
- **Latest integrated code checkpoint in `main`:** Taxo **10.8-r3**.
- **Main merge:** PR #105 → `db444a37ead421c8083558cfcf81ee97adc241f6`.
- **Issued tag/source:** `v10.8-r3` → `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd` — не пересувати.
- **START:** `Taxo_v10_8_candidate_r3_START.zip`.
- **START SHA-256:** `aa75661658194425f7dc95c353516a6f1c44f98040989f72d402985e2f023d00`.
- **Full package workflow:** `36741933852` — success.
- **Windows x64:** Portable + Setup — success.
- **Windows 7 SP1 x64:** Portable + Setup, Python 3.8 compatibility + PE gate — success.
- **macOS:** Apple Silicon arm64 + Intel x86_64 Portable — success.
- **Checksums:** platform manifests + `SHA256SUMS_v10_8_r3_ALL.txt` — published and verified.
- **Next code revision:** тільки **10.8-r4**.
- **Live ledger:** Issue #61.

`v10.3` залишається stable до окремого рішення власника. `v10.8-r3` є інтегрованим повним multi-platform checkpoint, але не автоматичною stable promotion.

## Що увійшло в 10.8-r3

### Відомість ТЦК — виправлення дати

Виправлено production-збій при даті Taxo формату `ДД.ММ.РРРР`, зокрема `30.09.2026`.

- підтримуються `ДД.ММ.РРРР`, ISO `YYYY-MM-DD`, `date` і `datetime`;
- дата нормалізується до внутрішнього ISO-формату перед запитами до БД;
- додано regression-тести на коректні й помилкові дати.

### Реквізити ТЦК у картці транспортного засобу

До картки ТЗ додано необов'язкові реквізити для військово-транспортної відомості:

- належність до власного / балансового парку;
- тип ТЗ;
- технічний стан;
- залишкова / балансова вартість;
- примітка.

Дані зберігаються у вже наявній `vehicle_military_transport_statement_data`; паралельна модель не створюється. Звичайна картка автомобіля не вимагає обов'язкового заповнення цих полів.

## Повний пакет 10.8-r3

У release `v10.8-r3` опубліковано і перевірено:

- `Taxo_v10_8_candidate_r3_START.zip`;
- `Taxo_v10_8_candidate_r3_Windows_x64_Portable.zip`;
- `Taxo_v10_8_candidate_r3_Setup_Windows_x64.exe`;
- `Taxo_v10_8_candidate_r3_Windows7_x64_Portable.zip`;
- `Taxo_v10_8_candidate_r3_Setup_Windows7_x64.exe`;
- `Taxo_v10_8_candidate_r3_macOS_arm64_Portable.zip`;
- `Taxo_v10_8_candidate_r3_macOS_x86_64_Portable.zip`;
- окремі SHA-256 manifests для платформ;
- `SHA256SUMS_v10_8_r3_ALL.txt`.

Усі executable assets зібрані з exact issued source `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`; tag `v10.8-r3` не пересувався.

## Чинні функціональні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження користувача там, де така підстановка дозволена;
- Бланки підтвердження діяльності є фактичними документами;
- ручний/некласифікований час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди і не дорівнює факту працевлаштування;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- історичні tag/release checkpoints immutable;
- старі work/tmp branches не використовуються як джерело коду для нової розробки.

## Windows 7

Compatibility line зберігається: CPython 3.8.10 x64 + PyInstaller 5.13.2 + `requirements-win7.txt`, `Taxo_win7.spec` і `scripts/check_win7_pe.py`. Для `10.8-r3` regression та PE compatibility gate пройдені успішно.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61.

## Наступний крок

Після повністю інтегрованого й упакованого `10.8-r3` наступна кодова ревізія — тільки **10.8-r4**. Починати її з нового pre-flight за `START_HERE.md`; stable `v10.3` не пересувати без окремого рішення власника.
