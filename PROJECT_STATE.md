# PROJECT_STATE — Taxo

**Дата фіксації:** 20.09.2026  
**Поточна stable:** Taxo 10.0  
**Попередня stable / rollback:** Taxo 9.0.1  
**Останній кандидат перед stable:** v9.1-r9.8  
**Stable release tag:** `v10.0`  
**Stable release target:** `91c0d6365a40eb09fe40f97a2965da40b314bc15`  
**PR #29:** merged  
**Release pipeline fixes:** PR #30 і #31 merged  
**Фінальний аудит:** `docs/maintenance/AUDIT_v10_0_STABLE.md`

**Поточна робоча контрольна точка:** Taxo 10.1-r3 candidate  
**Робоча гілка:** `work/v10.1-driver-role-ui-refresh`  
**Candidate audit:** `docs/maintenance/AUDIT_v10_1_r3.md`  
**Previous candidates:** `v10.1-r1`, `v10.1-r2` — immutable prereleases
**Candidate regression:** 144 tests / OK — START/source, Windows, macOS ARM64, macOS Intel x86_64

## Після stable 10.0 — Taxo 10.1-r3 candidate

- виправлено змішування `drivers.active`, `employees.active` та `employee_roles('Водій')`;
- завершення ролі водія більше не звільняє працівника;
- роль водія не повинна самовідновлюватися після restart;
- `driver_end_date` зберігається окремо і не стирається звичайним редагуванням;
- re-employment не повертає водійську роль автоматично;
- додано repair старого конкретного bug-стану, створеного startup sync;
- почато UI refresh: сонце + автобус, стримана синьо-жовта палітра, text-free icon;
- назва підприємства у brand-шапці динамічна з поля «Назва підприємства»;
- 10.1-r1 зафіксував driver-role fix і лишається immutable;
- 10.1-r2 зафіксував перший UI refresh, але ручне порівняння показало, що старий Tkinter-каркас ще залишався;
- 10.1-r3 перебудовує саме application shell: велика світла шапка, ліва синя навігація, центральна робоча область і нижній status bar;
- «Працівники» тепер відкриває реєстр персоналу, а не legacy список водійських карток;
- у header/runtime/build icon використовується саме затверджений text-free логотип-автобус, а не програмно намальоване наближення;
- назва підприємства динамічна також у заголовках вікон;
- stable `v10.0` не змінюється; 10.1-r3 призначено для наступної ручної Windows-перевірки.


## Рішення про stable

Користувач завершив ручний operational gate на реальній Windows-базі та явно підтвердив:
- злити робочу гілку у `main`;
- підняти версію до **10.0**;
- оформити документацію;
- випустити executable packages для Windows x64, macOS ARM64 та macOS Intel x86_64;
- опублікувати START/source і SHA-256.

До цього моменту `main` навмисно лишався на 9.0.1.

## Функціональний стан 10.0

### Робочий час
- один канонічний стан дня для Табеля і Графіка водіїв;
- точні інтервали, split-shift, overnight;
- union перекриттів без подвійного часу;
- duration-only не вигадує 08:00–16:00;
- нові часові конфлікти блокуються;
- історичні конфлікти не переписуються автоматично.

### Персонал
- Реєстр / Планування / Табель / Звіти;
- режими 5/40, 6/40, 6/36, 6/24, підсумований, індивідуальний;
- відсутності не стирають історичний план;
- внутрішнє сумісництво контролюється за точними інтервалами;
- роль водія не дублюється через employee_shifts.

### П-5
- PDF/XLSX типової форми;
- коди 01–30;
- факт має пріоритет;
- план замість факту підставляється тільки після явного запиту;
- підстановка плану виділяється та пояснюється приміткою.

### Графіки й аудит
- місячний графік змінності;
- PDF графіка й PDF деталізації;
- «Відкрити деталізацію» формує актуальний PDF і відкриває його;
- «Аудит графіків…» — технічна перевірка введення;
- «Контроль №340» — окрема нормативна перевірка.

### Шляхівки
- нумерація, маршрути, авто, пробіг/спідометр, історія;
- role + schedule date + shift = один duty slot;
- нічний рейс не підхоплює персонал наступного дня;
- legacy duplicates позначаються як конфлікт;
- ручний тест r9.8 підтвердив однакового лікаря/механіка для двох шляхівок однієї зміни.

### START / пакування
- START.bat ASCII-only + CRLF;
- перевірка повноти пакета до pip;
- full/incomplete preflight у Windows CI;
- БД/SQLite/кеші/скани/персональні файли не потрапляють у artifacts.

## Дані

- робоче сховище зберігається між версіями;
- повторне введення даних не потрібне;
- робочі бази не зберігаються у Git;
- retention робочих даних — 48 місяців;
- backup/restore лишається частиною експлуатаційного контуру.

## Релізи

Історичні immutable контрольні точки:
- stable: `v9.0`, `v9.0.1`;
- candidates: `v9.1-r5` … `v9.1-r9.8`;
- `v9.1-r9.5` лишається історичним known-bad START release і не пересувається.

Нова stable:
- `v10.0` — опублікований stable release;
- target commit: `91c0d6365a40eb09fe40f97a2965da40b314bc15`;
- Windows x64 Setup;
- Windows x64 Portable;
- macOS ARM64;
- macOS Intel x86_64;
- START/source;
- per-platform і combined SHA-256 manifests.

## Stable release result

1. PR #29 — merged у `main`.
2. PR #30/#31 — release-pipeline hardening merged.
3. `Publish Taxo 10.0 stable` — success.
4. Source verify — 117 tests / OK.
5. Windows — 117 tests / OK, Setup + Portable success.
6. macOS ARM64 — 117 tests / OK, Taxo.app package success.
7. macOS Intel x86_64 — 117 tests / OK, Taxo.app package success.
8. START/source verification — success.
9. GitHub Release `v10.0` — published, 10 assets.
10. `main` + protected tag `v10.0` є новим stable source of truth.

Деталі:
- [Release notes 10.0](docs/releases/RELEASE_NOTES_v10_0.md)
- [Фінальний аудит](docs/maintenance/AUDIT_v10_0_STABLE.md)
- [Release index](docs/releases/RELEASE_INDEX.md)
