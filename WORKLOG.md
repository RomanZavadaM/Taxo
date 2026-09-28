# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Latest issued fast-test:** Taxo **10.6-r1** / `v10.6-r1`  
**Issued r1 source/tag target:** `e4823947d3c5d28af54fd4337bdaf0daf02b4201`  
**Regression / START verify:** `507/507 OK`; run `36420768488` — success  
**Publisher:** run `36420943804` — success  
**START asset:** `Taxo_v10_6_candidate_r1_START.zip`  
**START SHA-256:** `6c61ab0beb405aba19a686fbe352ab76b86ca7932fe6acdc4c6a7ba35d08b4d9`  
**Release:** https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r1  
**Active branch:** `work/v10.6-r1-hide-inactive-vehicles`  
**Tracking:** Issue #78; live ledger #61  
**Next code revision:** **10.6-r2**

## DONE — 10.6-r1

- [x] У вікні «Транспортні засоби — реєстр документів» додано прапорець **«Сховати неактивні автомобілі»**.
- [x] Фільтр увімкнений за замовчуванням ще до першого завантаження списку.
- [x] При знятті прапорця список одразу повертає весь парк, включно з неактивними ТЗ.
- [x] Фільтр змінює лише видимість рядків; картки ТЗ, документи, статуси та історія не переписуються.
- [x] Розміщення фільтра не залежить від старого підпису кнопки додавання автомобіля; передбачено fallback, якщо action-bar надалі зміниться.
- [x] `main.APP_VERSION`, `VERSION.txt`, runtime-шар `v1061_features.py`, regression і START guard синхронізовані як 10.6-r1.
- [x] Повний regression: **507/507 OK**.
- [x] Чистий START package guard — success.
- [x] Immutable prerelease `v10.6-r1` опублікований на точний source `e4823947d3c5d28af54fd4337bdaf0daf02b4201`.
- [x] GitHub Release містить прямий START ZIP і SHA-256 manifest.
- [x] Одноразовий publisher після успішної публікації видалено; issued tag/source не пересувався.

## PRESERVED — 10.5-r10 / r9

- r10: аудит конкретного дня не порівнює історичний план дня з поточним шаблоном маршруту; plan/fact не змішуються.
- r9: шляхівка **«Поза маршрутом…»**, плановий час з графіка, factual/тахографічний облік окремий, типове поле «по області» редагується.

## NEXT

10.6-r1 виданий і immutable. Наступна кодова зміна — тільки **10.6-r2** в окремій work-гілці. У `main` 10.6-r1 не зливати без окремої команди власника.

## BLOCKED

Немає.
