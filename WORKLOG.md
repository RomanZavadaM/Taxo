# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Previous published candidate:** `v10.3-r7` → `3bcdb93b9ceffecd07705e3d2a9e6d8b6864e420`  
**r7 manual gate:** accepted by user for the backup-window fix  
**Active candidate:** `10.3-r8`  
**Branch:** `work/v10.3-r8-macos-sidebar-contrast`  
**PR:** #66  
**Live ledger:** Issue #61.

## ACTIVE SLICE — 10.3-r8

### Ціль
Виправити слабку читабельність лівого navigation sidebar у macOS, показану користувачем на реальній збірці.

### Причина
macOS Aqua може малювати native `tk.Button` власною світлою поверхнею, ігноруючи заданий синій `background`. При білому `foreground` пункти меню стають майже невидимими.

### Рішення
- тільки на macOS sidebar navigation використовує clickable `tk.Label` замість native `tk.Button`;
- фон/текст/іконки залишаються під повним контролем Taxo;
- normal = фірмовий синій + білий текст;
- selected = темний navy + білий текст;
- hover/focus = `blue_dark` + білий текст;
- mouse click, Enter і Space запускають ту саму команду;
- Windows/Linux лишаються на попередньому button rendering.

### Критерії готовності
- `main.APP_VERSION == VERSION.txt == 10.3-r8`;
- regression guard перевіряє Darwin-safe navigation path;
- бізнес-логіка та схема БД не змінені;
- full regression suite зелений;
- Windows PR gate зелений;
- macOS ARM64 та Intel gates зелені;
- immutable `v10.3-r8` містить `Taxo_v10_3_candidate_r8_START.zip`;
- PR merged у `main`;
- `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61 синхронізовані.

## DOING

- [x] Відновлено стан за `START_HERE.md`.
- [x] Зафіксовано прийняття manual gate 10.3-r7.
- [x] Створено branch `work/v10.3-r8-macos-sidebar-contrast`.
- [x] Реалізовано macOS-safe sidebar navigation.
- [x] Додано regression test і release notes.
- [x] Відкрито PR #66.
- [ ] Запустити exact-head candidate publisher і PR gates.
- [ ] Перевірити release asset/tag.
- [ ] Merge та фінальна документація.

## NEXT

PR #66 відкрито. Останнім branch commit додати r8 publisher; після цього head не змінювати без нового виявленого дефекту.

## BLOCKED

Немає.
