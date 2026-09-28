# Taxo — стан продукту

**Актуально:** 28.09.2026

## Поточний статус

- **Stable:** Taxo 10.3 / `v10.3` — immutable.
- **Previous stable / rollback:** Taxo 10.1 / `v10.1`.
- **Latest full checkpoint in `main`:** Taxo 10.5-r8 / `v10.5-r8`.
- **Issued source:** `846e5c5111b14a4a1f2e49203803e86c495b458f`.
- **PR #76:** merged.
- **Main merge:** `eb9cb039d35419fb579ff0f5e1b9c633c95ccd86`.
- **Full release workflow:** `36406419955` — success.
- **Regression:** `483/483 OK`.
- **Packages:** Windows x64 Setup/Portable, Windows 7 SP1 x64 Setup/Portable, macOS ARM64/Intel Portable, START/source, SHA-256 manifests.
- **Next code revision:** `10.5-r9`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8

`v10.5-r8` — повний candidate/checkpoint, але stable лишається `v10.3` до окремого рішення власника.

## Функціональний стан

Taxo — настільна система для одного автотранспортного підприємства. Поточна інтегрована лінія охоплює:

- працівників, водіїв, ролі та історію;
- графіки водіїв і планування персоналу;
- табель робочого часу, план/факт, поділені зміни;
- маршрути, шляхові листи, пробіг;
- бланки підтвердження діяльності з ревізіями;
- транспортні засоби та документи ТЗ;
- страхування, ДЦВ, техконтроль, техпаспорти, тимчасову реєстрацію, протоколи тахографа;
- аналогові тахокарти, інтервали та протоколи;
- PDF/Excel звіти;
- резервування і переносиме робоче сховище;
- звірку ТЗ з «Шлях»;
- робочі редаговані registry-значення окремо від immutable державних snapshots;
- єдиний реєстр документів працівників;
- військово-транспортну відомість підприємства;
- локальний Diia-first цикл щорічного персонального військового звіряння без імітації державного API.

## 10.5-r8

r8 — вузьке compatibility-виправлення для Windows 7 / Python 3.8. Деякі XLSX «Шлях» можуть викликати openpyxl `TypeError` з `unexpected keyword argument 'tabId'` без `ChildSheet`. r8 розпізнає цей фактичний варіант, виконує in-memory retry, не змінює вихідний XLSX і не маскує сторонні помилки.

Бізнес-логіка r7 при цьому не змінювалась.

## Дані й сумісність

- робочі БД, SQLite, скани, кеші та персональні документи не входять до release;
- програма й робочі дані розділені;
- оновлення не повинно вимагати повторного введення робочої бази;
- raw snapshots державних витягів не переписуються локальними змінами;
- порожні державні значення не очищають локальні дані автоматично;
- план не оголошується фактом без явного підтвердження;
- для Windows 7 full checkpoint використовується окрема CPython 3.8.10 / PyInstaller 5.13.2 compatibility line.

## Recovery / джерело істини

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61.

Додатково:
- [Індекс релізів](releases/RELEASE_INDEX.md)
- [Release notes 10.5-r8](releases/RELEASE_NOTES_v10_5_r8.md)
- [Поточна контрольна точка](maintenance/CHECKPOINT_CURRENT.md)

## Право та власність

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo — proprietary software. Публічна видимість репозиторію не створює open-source ліцензії.

Документи: [LICENSE.md](../LICENSE.md) · [COPYRIGHT.md](../COPYRIGHT.md) · [Авторські права та ліцензія](LEGAL_AND_COPYRIGHT.md)
