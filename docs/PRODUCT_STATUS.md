# Taxo — стан продукту

**Актуально:** 08.11.2026

## Поточний статус

- **Stable / Latest:** Taxo 10.12-r10 / `v10.12-r10` — [GitHub Release](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10); exact source `6d0f32bc`, 8 assets, GitHub Latest.
- **Previous stable / safe rollback:** Taxo 10.10-r5 / `v10.10-r5`.
- **Older rollback:** Taxo 10.9-r10 / `v10.9-r10`.
- **Current integrated candidate:** Taxo 10.13-r6 / exact product `a3f4e7e9` — не stable; звичайні накази мають структуровані працівники/ТЗ з mass-select, frozen snapshot і PDF-переліком; exact CI/START і резерв на Drive PASS.
- **Next code revision:** `10.13-r8`.

## Відомі обмеження попередньої stable 10.9-r10

- у вікні програми версія може показуватися як «10.8-r5» (виправлено в тестовій 10.10-r3);
- повна резервна копія без позначених вкладень не попереджає, що містить лише БД (виправлено в 10.10-r3);
- пакети містять PyMuPDF (AGPL-3.0) — у 10.10 його вже немає.

## Лінія 10.10

- **10.10-r1:** PyMuPDF прибрано; PDF/JPG бланка, дата №340 і перегляд PDF — pypdfium2 + reportlab + pypdf.
- **10.10-r2:** застарілі публікаційні workflow вимкнено; тести ізольовано від робочого сховища.
- **10.10-r3:** правильна версія у головному вікні; попередження «лише БД».
- **10.10-r4:** правильна версія у всіх вікнах і Windows 7 Setup; superseded через проблему запуску на macOS.
- **10.10-r5 (previous stable):** виправлено запуск macOS у навігації «Працівники»; власник перевірив Apple Silicon; повні Windows/Win7/macOS/START перевірки успішні.

## Stable 10.12-r10

- завершено Feature Loss cycle 10.12-r1…r10;
- 23/23 критичних маршрутів мають runtime-smoke requirement;
- «План → факт» перевіряється реальною дією на ізольованій SQLite-БД без перезапису наявного факту;
- exact r10 Windows/Win7/macOS/START gates — SUCCESS;
- owner manual r10 acceptance — без блокера;
- stable promotion 07.11.2026 з exact source `6d0f32bc45323d4085bb165b2ec050dae7b378ee`.

## Integrated 10.13-r7

- Наказ про закріплення: масовий вибір пар ТЗ/водій; у draft є «Додати багато…», single-pair сценарій збережено.
- Нумерація: окремі work/personnel series, personnel suffix `-К`, configurable next number, legacy work counter continuation.
- PR-head: Windows #1320 — **981 tests / OK**; Win7 #306 — SUCCESS; macOS #1231 Intel/ARM — SUCCESS.
- Exact-main: Windows #1321 — **981 tests / OK**; Win7 #307 — SUCCESS; macOS #1232 Intel/ARM — SUCCESS; START #2331 — SUCCESS.
- Drive recovery-copy confirmed: 1 680 167 bytes, `1lVmLFCqToh_9Bqhxrdd1e9Yuzz8Ol5r2`, SHA256 `09e0185d52dfbfd31c6745cf2afa31910be6a88645b18678eb95f683a8dbfea0`.
- Known pre-delivery safety mismatch: r7 draft-helper permits 1 driver→many vehicles while approval guard rejects simultaneous multi-vehicle assignment. Next code revision **10.13-r8** must reject this mode earlier and add approval regression.
- Stable remains **10.12-r10**.

## Integrated 10.13-r6

- вкладка «Учасники / ТЗ» у наказах з масовим вибором;
- stable Taxo ID + роль + frozen snapshot працівника/ТЗ;
- пошук за ПІБ/табельним №/ідентифікатором, держномером/VIN;
- driver-only pool для водійських типів наказів;
- inactive не додаються; після введення наказу в дію перелік immutable;
- add/remove зберігаються в історії наказу;
- PDF має окремий структурований перелік; RNOKPP автоматично не друкується, VIN друкується;
- specialized vehicle assignment model не замінено загальним механізмом;
- exact-main Windows **972 tests / OK**, Win7/macOS/START SUCCESS;
- exact START зарезервовано на Google Drive;
- stable не змінено: **10.12-r10**.

## Integrated 10.13-r5

- спільний selector для працівників, водіїв і ТЗ зі стабільними Taxo ID;
- працівники розрізняються за табельним №/ідентифікаційними реквізитами, ТЗ — за держномером/VIN;
- driver-only вибір не змішує водіїв з іншими працівниками;
- інструктажі використовують той самий structured employee choice;
- підготовчий CSV інструктажу містить ПІБ, табельний № і Код Taxo без автоматичного друку RNOKPP;
- active/historical режим зберігає історичні записи;
- shared snapshot підготовлено як основу наступного етапу; повне збереження snapshot у багатьох типах наказів ще не завершене;
- exact-main Windows **960 tests / OK**, Win7/macOS/START SUCCESS;
- exact START зарезервовано на Google Drive;
- stable не змінено: **10.12-r10**.

## Integrated 10.13-r4

- наказ про закріплення дозволяє одразу вибрати активний транспорт і водія з бази Taxo;
- список водіїв не містить довільних активних працівників;
- перша пара ТЗ/водій створюється разом із чернеткою наказу;
- неповна пара блокується, а порожня зберігає старий сценарій;
- exact-product Windows **953 tests / OK**, Win7/macOS/START SUCCESS;
- stable не змінено: **10.12-r10**.

## Integrated 10.13-r2

- СТОІР має явний «Відкрити вибране ТЗ» замість залежності від знання про double-click;
- внутрішні коди ТО/ремонту, джерел пробігу та ISO timestamps у робочих таблицях показуються людською українською;
- робочий стіл має прямий старт «Оформити новий наказ…»;
- order actions адаптовані до меншої ширини;
- Feature Loss gate не дозволив видалити старий «Каталог типів наказів»: фінальний r2 зберігає обидва маршрути;
- exact-product Windows **941 tests / OK**, Win7/macOS/START SUCCESS;
- stable не змінено: **10.12-r10**.

## Функціональний стан

Taxo — настільна система для одного автотранспортного підприємства. Поточна інтегрована лінія охоплює:

- працівників, водіїв, ролі та історію;
- графіки водіїв і планування персоналу;
- табель робочого часу, plan/fact, поділені зміни;
- маршрути, шляхові листи, пробіг;
- бланки підтвердження діяльності з ревізіями;
- транспортні засоби, документи ТЗ та СТОІР;
- страхування, ДЦВ, техконтроль, техпаспорти, тимчасову реєстрацію, протоколи тахографа;
- аналогові тахокарти, інтервали та протоколи;
- PDF/Excel звіти;
- резервування і переносиме робоче сховище;
- звірку ТЗ з «Шлях»;
- робочі редаговані registry-значення окремо від immutable державних snapshots;
- єдиний реєстр документів працівників;
- військово-транспортну відомість підприємства;
- локальний Diia-first цикл щорічного персонального військового звіряння без імітації державного API;
- захист історії виданих шляхівок і номерів;
- контроль чинності документів ТЗ на весь плановий період рейсу;
- посилений контроль work/rest, overlaps, boundary gaps, 3+9 і двотижневих меж;
- коректний пріоритет фактичних джерел у 60-денному реєстрі;
- historical employment/P-5 safety і цикли 2/2, 3/3;
- захист затверджених/підписаних наказів та закріплень водій→ТЗ;
- explicit SQLite schema baseline і future-schema guard.

## Дані й сумісність

- робочі БД, SQLite, скани, кеші та персональні документи не входять до release;
- програма й робочі дані розділені;
- оновлення не повинно вимагати повторного введення робочої бази;
- raw snapshots державних витягів не переписуються локальними змінами;
- порожні державні значення не очищають локальні дані автоматично;
- plan не оголошується fact без явного підтвердження;
- future SQLite schema, новіша за підтримувану збіркою, блокується від відкриття r9+;
- для Windows 7 використовується окрема CPython 3.8.10 / PyInstaller 5.13.2 compatibility line.

## Recovery / джерело істини

`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → `PROJECT_STATE.md`; `WORKLOG.md` та Issue #61 — для деталей.

Додатково:
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Release notes 10.12-r10](releases/RELEASE_NOTES_v10.12-r10.md)
- [Release notes 10.9-r10](releases/RELEASE_NOTES_v10.9-r10.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)

## Право та власність

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo — proprietary software. Публічна видимість репозиторію не створює open-source ліцензії.

Документи: [LICENSE.md](../LICENSE.md) · [COPYRIGHT.md](../COPYRIGHT.md) · [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)
