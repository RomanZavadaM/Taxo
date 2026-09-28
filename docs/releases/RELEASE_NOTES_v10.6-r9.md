# Taxo 10.6-r9 — адаптивний заголовок картки документів ТЗ

**Тип:** fast-test candidate  
**База:** issued `v10.6-r8`; latest full `main` checkpoint — `v10.6-r3`.

## Зміни

- Назва автомобіля та підсумок стану документів більше не конкурують за один жорсткий horizontal row.
- На достатній ширині header зберігає один рядок.
- Коли title + summary не вміщаються, вони автоматично переходять у два рядки.
- На вузькому header підсумок отримує динамічний `wraplength`.
- `summary_var`, його текст і розрахунок стану документів не змінені.
- Таблиця, responsive action-bar r7 і responsive form r8 збережені.

## Межа змін

Це UI-only revision. Вона не змінює document schema, SQL, archive semantics, копії файлів, строки дії, vehicle data, шляхівки, plan/fact або тахографічні дані.

## Перевірка

Фінальні regression/START run, issued SHA, release asset і SHA-256 будуть записані після green CI та публікації кандидата.
