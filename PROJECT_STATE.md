# PROJECT_STATE — Taxo

**Дата:** 05.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.10 / `v10.10` — immutable; промоція перевіреної власником 10.10-r3 з ідентичністю версії `10.10` (за зразком stable 10.3).
- **Previous stable / rollback:** Taxo 10.3 / `v10.3` — immutable; tag target `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Лінія 10.10:** r1 (PR #136, без PyMuPDF) → r2 (PR #137, CI hardening) → r3 (PR #138, правильна версія + попередження backup) → stable 10.10.
- **Verified candidate:** `v10.10-r3` → main `de9b11ad581cd91805b1a8b6e506e1fa74f44ea3`; 813 тестів; Windows/Win7/macOS/START success; перевірено власником.
- **Пакети stable:** Windows x64 Setup/Portable, Windows 7 x64 Portable, macOS arm64/x86_64 Portable, START, SHA256SUMS — з stable-коміту `main`.
- **Next code revision:** **10.10-r4**.
- **Live ledger:** Issue #61.

## Що додано в 10.10-r1

- PyMuPDF (AGPL-3.0) повністю прибрано з коду, тестів, requirements, specs і пакетів (`PROJECT_RULES.md` §17);
- новий `src/taxo/pdf_engine.py`: pypdfium2 (рендер), reportlab + pypdf (штамп);
- Бланк підтвердження PDF/JPG і дата у звіті №340 — попіксельно ідентичні попередній реалізації;
- вбудований перегляд/друк PDF — pypdfium2, з fallback на системну програму;
- license gate: `tests/test_v10_10_r1.py` + `scripts/check_bundle_licenses.py` у всіх збірках;
- без міграцій робочих БД і змін даних користувача.

## Що додано в 10.9-r10

- runtime/support Python modules перенесені з кореня в `src/taxo/`;
- executable entry points лишені в корені, сумісність flat imports збережена bootstrap-механізмом;
- runtime templates перенесені в `assets/`;
- активні PyInstaller/Inno Setup файли перенесені в `packaging/`, історичні spec — в `packaging/history/`;
- `START.bat`, Windows, Windows 7 і macOS packaging paths адаптовані до нової структури;
- `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.9-r10`;
- зміна не вводить міграції робочих БД, backup/workspace, сканів чи документів користувача.

## Інтегрована лінія 10.9-r2 → 10.9-r9

- **r2:** незворотна історія виданих шляхівок і номерів; retention не може видалити пов'язаний факт.
- **r3:** чинність обов'язкових документів ТЗ на весь плановий період рейсу.
- **r4:** посилений контроль робочого часу/відпочинку, gaps/overlaps, 3+9, weekly-rest spacing і двотижневий контроль.
- **r5:** 60-денний реєстр не вигадує відпочинок із невідомих хвилин; непідтверджений тахограф має нижчий пріоритет.
- **r6:** баланс персоналу/П-5, employment-aware historical selection, цикли 2/2 та 3/3.
- **r7:** СТОІР — хронологія одометра, fallback `work_date`, прогноз від останнього факту та spike guard.
- **r8:** незмінність затверджених/підписаних наказів, безпечне оновлення відповідального, захист driver→vehicle assignments.
- **r9:** SQLite schema compatibility baseline через `PRAGMA user_version` і future-schema guard.

## Репозиторій після structural cleanup

- поточний код береться тільки з `main`;
- `src/taxo/` — runtime/support modules;
- `assets/` — runtime templates/assets;
- `packaging/` — active build/installer definitions;
- historical work/candidate refs, tags і releases не є джерелом актуального коду;
- historical tags/releases залишаються immutable для audit/rollback.

## Чинні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження там, де це дозволено;
- Бланки підтвердження діяльності є фактичними документами;
- невідомий/ручний час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди;
- видана шляхівка та історично використаний номер захищені від тихого фізичного знищення/повторного використання;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- видані tags/releases immutable;
- після stable `10.10` наступна кодова ревізія — `10.10-r4`;
- у програму й пакети входять лише залежності з permissive-ліцензіями; PyMuPDF заборонений назавжди;
- regression-тести запускаються лише в CI або в ізольованому середовищі, ніколи — на машині з реальним робочим сховищем.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state.
