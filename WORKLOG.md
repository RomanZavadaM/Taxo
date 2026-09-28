# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Latest issued fast-test:** Taxo **10.5-r10** / `v10.5-r10`  
**Issued source:** `91a528ba92a56a8e1a399c8c114254f05798b5c7`  
**Branch:** `work/v10.5-r10-audit-plan-fact`  
**Regression:** `499/499 OK`  
**Verified START run:** `36416851443` — success  
**Release:** https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r10  
**START:** https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r10/Taxo_v10_5_candidate_r10_START.zip  
**SHA-256:** `396d78153c67388033b39a4548aae7d2ee48e32cba47359943a84f1a99a1e753`  
**Next code revision:** **10.6-r1** — not started  
**Live ledger:** Issue #61

## DONE — 10.5-r10

- [x] Проаналізовано хибні повідомлення аудиту «Виїзд із АТП не збігається / Заїзд в АТП не збігається».
- [x] Встановлено причину: аудит дня порівнював збережений план конкретного дня (`work_segments`) з поточним редагованим шаблоном маршруту (`route_stops`).
- [x] Це порівняння прибрано тільки для `source_kind=worklog`: різниця між історичним/перепланованим днем і поточним шаблоном не вважається помилкою дня.
- [x] Внутрішній контроль актуального шаблону `route_segments ↔ route_stops` збережено для `source_kind=route`.
- [x] `fact_work_*` не використовується для підміни плану і не переписується аудитом.
- [x] Інші перевірки дня — неповні пари, перекриття, керування поза роботою, порожні частини — залишені без змін.
- [x] Додано `v10510_features.py`, regression-тести та START package guard.
- [x] Full regression: **499/499 OK**.
- [x] Чистий START перевірено та опубліковано як GitHub prerelease `v10.5-r10`.

## PRESERVED FROM 10.5-r9

- окрема дія шляхівки **«Поза маршрутом…»** без створення фіктивного регулярного маршруту;
- плановий час береться з чинного графіка водія;
- тахографічний та factual-облік не змінюються;
- поле «Маршрут / замовник» редаговане, типово «по області».

## NEXT

`10.5-r10` виданий та immutable. Наступний кодовий крок — тільки **10.6-r1** в новій work-гілці після читання `START_HERE.md`, `PROJECT_RULES.md`, `PROJECT_STATE.md`, цього файлу та Issue #61. У `main` r10 не зливати без окремої команди власника.

## BLOCKED

Немає.
