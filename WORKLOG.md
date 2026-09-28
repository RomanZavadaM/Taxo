# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.5-r8** / `v10.5-r8`  
**Latest issued fast-test:** Taxo **10.5-r10** / `v10.5-r10`  
**Issued r10 source:** `91a528ba92a56a8e1a399c8c114254f05798b5c7`  
**Active revision:** **10.6-r1**  
**Active branch:** `work/v10.6-r1-hide-inactive-vehicles`  
**Base:** post-r10 cleanup `324c7896901d53fc1134b5b46f567bd4657c97e3`  
**Scope:** фільтр неактивних автомобілів у реєстрі документів ТЗ  
**Tracking:** Issue #78; live ledger #61

## DOING — 10.6-r1

- [x] Додати у вікно «Транспортні засоби — реєстр документів» прапорець **«Сховати неактивні автомобілі»**.
- [x] Увімкнути фільтр за замовчуванням до першого завантаження списку.
- [x] При вимкненні фільтра показувати весь парк, включно з неактивними ТЗ.
- [x] Не змінювати картки ТЗ, документи або історію — фільтр лише візуальний.
- [x] Додати runtime-шар `v1061_features.py`, version identity, regression і START package guard.
- [ ] Пройти повний regression/CI.
- [ ] Перевірити чистий START package.
- [ ] Опублікувати immutable prerelease `v10.6-r1` з прямим START asset.
- [ ] Зафіксувати issued SHA/run/checksum у цьому файлі та Issue #61.

## PRESERVED — 10.5-r10 / r9

- r10: аудит конкретного дня не порівнює історичний план дня з поточним шаблоном маршруту; plan/fact не змішуються.
- r9: шляхівка **«Поза маршрутом…»**, плановий час з графіка, factual/тахографічний облік окремий, типове поле «по області» редагується.

## NEXT

Дочекатися успішного source-test workflow для актуального head 10.6-r1; після успіху зафіксувати exact candidate head і опублікувати GitHub prerelease/START. У `main` не зливати без окремої команди власника.

## BLOCKED

Немає.
