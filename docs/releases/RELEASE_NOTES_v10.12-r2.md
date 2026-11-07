# Taxo 10.12-r2 — function reachability gate

**Дата:** 07.11.2026  
**Тип:** test/contract candidate.  
**Stable:** без змін, `v10.10-r5`.

## Мета

Після підтвердженої втрати UI-входу до «Простого місячного графіка…» і історичної регресії вкладки «Транспорт» статичних source-contract тестів недостатньо.

10.12-r2 вводить виконуваний реєстр критичних користувацьких маршрутів та Xvfb/Tk smoke для ризикових runtime-входів.

## Додано

- `src/taxo/function_registry.py` — стабільні `function_id`, зона UI, label і callback.
- runtime smoke перевіряє реальні `winfo_ismapped()` та `.invoke()` для:
  - «Дані / Дія / документи…»;
  - fallback «Простий місячний графік…»;
  - «Військово-транспортний облік»;
  - «СТОІР».
- окремо зберігається source-contract постійної кнопки простого місячного графіка у Personnel UI.
- реальні БД/документи не використовуються; callback-и у smoke ізольовані.

## Не змінено

- business logic;
- database schema;
- plan/fact;
- exports;
- user data;
- stable release.
