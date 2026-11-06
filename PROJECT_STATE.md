# PROJECT_STATE — Taxo

**Дата:** 06.11.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable / Latest:** Taxo 10.10-r5 / `v10.10-r5` — виправлення запуску macOS; прийнято власником 05.11.2026.
- **Superseded:** Taxo 10.10-r4 / `v10.10-r4` — підтверджена проблема запуску на macOS.
- **Previous safe rollback:** Taxo 10.9-r10 / `v10.9-r10`.
- **Older rollback:** Taxo 10.3 / `v10.3`; historical tag target `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Current main candidate:** Taxo **10.11-r5** — security/dependency update Pillow/pypdf + Win7 mitigation. Офіційний [prerelease v10.11-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r5) опубліковано 06.11.2026; 8 assets і SHA256; exact tag source `f2614caf60380c4898c1d042bd6c8d402edc38da`. Stable не змінено.
- **Next code revision:** **10.11-r6**.
- **Continuity:** `HANDOFF_CURRENT.md` — обов'язковий recovery-знімок; private process profile — `RomanZavadaM/dev-strategy` / `profile/taxo` / `TAXO_PROFILE.md`.
- **Google Drive backup:** повний stable-комплект + `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r5_2026-11-06_START.zip` (1 525 891 байт) у папці `Taxo — Розробка — резервний комплект`.
- **Live ledger:** Issue #61 — історія, не перша сторінка recovery.

## Поточний main 10.11-r5 — стабілізація та dependency security

- **r6:** єдиний центр «Дані / Дія / документи» та масове поновлення державних даних для вибраних працівників.
- **r7:** вимоги до документів на рівні конкретного працівника; незалежний контроль строку; копії документів у workspace; employee documents завжди входять у повний backup.
- **r8:** простий місячний графік для вибраних працівників; шаблони Пн–Пт, 2/2, 3/3, щодня та вибрані дні; факт/відсутність/конфлікти не перезаписуються.
- **r9:** вибрані водії відображають основний worklog замість загальної кадрової норми; посада водія не створює дубль у планувальнику; виправлено аварію коригування відсутностей. Тести r9 додано. PR #160 merged; exact-main START, Windows, Windows 7, macOS ARM64/Intel — SUCCESS.
- **r10:** українське «част.»; вибір водіїв у деталізованому водійському PDF/Excel, PR #162 merged.
- **10.11-r1:** спрощення до вибору документа та двох дій; читабельні імена файлів; PR #163 merged. Exact-main START/Windows/Win7/macOS SUCCESS. Issue #164 — подальша системна UX робота.
- **10.11-r2:** PR #169 — інформативні назви простого графіка працівників і вилучення «Роль» лише з PDF; PR #171 — виправлення залишкових r1-імен у активному packaging; exact-main `68d7459b` START/Windows/Win7/macOS SUCCESS; prerelease `v10.11-r2` опублікований workflow #42086984364. Stable залишається r5.
- **10.11-r3:** повний code-review Issue #175 виявив два критичні дефекти цілісності даних; PR #176 закрив їх: «План → факт» більше не перезаписує існуючий факт, а детальне перепланування стало атомарним. Exact issued source `a82a3dc6`; START #42219595152, Windows #42219595132, Win7 #42219595055, macOS #42219595074 — SUCCESS; publisher #42220584720 опублікував immutable prerelease `v10.11-r3` з 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r4.
- **10.11-r4:** PR #179 — DB-level захист `control_protocols` від каскадного видалення через `discs`, UI guard і behavioral SQLite regression. Exact issued source `c4e70158`; START #42223328213, Windows #42223328267, Win7 #42223328554, macOS #42223328239 — SUCCESS; publisher #42224658087 опублікував immutable prerelease `v10.11-r4` з 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r5.
- **10.11-r5:** PR #182 — основна лінія Pillow 13.0.0 / pypdf 6.21.4; Win7 лишається на Python 3.8-сумісних Pillow 10.4.0 / pypdf 5.9.0 з Taxo page-tree security preflight і окремим Win7 security-smoke. Exact issued source `f2614caf`; START #42230454712, Windows #42230454659, Win7 #42230454846, macOS #42230454687 — SUCCESS; publisher #42231569758 опублікував immutable prerelease `v10.11-r5` з 8 assets. Google Drive START backup підтверджений. Наступна ревізія — 10.11-r6.
- **Публікація:** docs PR #165/#166 та release trigger PR #167 merged; publish workflow #42063810115 SUCCESS. 10.11-r1 = immutable prerelease, не stable.
- **Зауваження власника до r1 закриті в r2:** неоднозначне ім'я `Графік_працівників_2026_11.pdf` замінено на змістовну схему, зайву колонку «Роль» прибрано лише з PDF. Подальший UX — Issue #164; власник тестує r2.
- Водійський план не дублюється у загальному плануванні персоналу.
- Персональний PDF/Excel містить тільки вибраних працівників і не показує службові проблеми інших ролей.
- Перед інтеграцією r8 повні перевірки Windows, Windows 7, macOS ARM64/Intel та START пройшли успішно.
- Повторна перевірка точного інтегрованого main r8: START, Windows, Windows 7, macOS ARM64 та Intel — SUCCESS.
- Stable / Latest залишається **v10.10-r5** до окремого рішення власника.

## Що додано в 10.10-r1

- PyMuPDF (AGPL-3.0) повністю прибрано з коду, тестів, requirements, specs і пакетів (`PROJECT_RULES.md` §17);
- новий `src/taxo/pdf_engine.py`: pypdfium2 (рендер), reportlab + pypdf (штамп);
- Бланк підтвердження PDF/JPG і дата у звіті №340 — попіксельно ідентичні попередній реалізації;
- вбудований перегляд/друк PDF — pypdfium2, з fallback на системну програму;
- license gate: `tests/test_v10_10_r1.py` + `scripts/check_bundle_licenses.py` у всіх збірках;
- без міграцій робочих БД і змін даних користувача.

## Поточна stable 10.10-r5

- виправлено показ версії у всіх вікнах і діалогах;
- повернено Windows 7 Setup поруч із Portable;
- опубліковано повний комплект Windows, Windows 7, macOS Intel/ARM, START і SHA256;
- універсальний механізм публікації замінив окремі publish-файли під кожну ревізію;
- виправлено macOS startup crash у навігації «Працівники»; виправлення перевірено власником на Apple Silicon.

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
- поточна stable — `10.10-r5`; `10.10-r4` superseded через macOS startup issue; поточний main candidate — `10.11-r5`; наступна кодова ревізія — `10.11-r6`; наступна stable змінюється лише рішенням власника;
- у програму й пакети входять лише залежності з permissive-ліцензіями; PyMuPDF заборонений назавжди;
- regression-тести запускаються лише в CI або в ізольованому середовищі, ніколи — на машині з реальним робочим сховищем.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `HANDOFF_CURRENT.md` → private `dev-strategy/profile/taxo/TAXO_PROFILE.md` → live GitHub → `PROJECT_STATE.md`; `WORKLOG.md` та Issue #61 — для деталей/історії.

При суперечності документації з live GitHub перемагає фактичний GitHub state.
