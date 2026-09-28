# Taxo 10.6-r7 — адаптивна панель дій картки документів ТЗ

**Тип:** fast-test candidate  
**База:** issued `v10.6-r6`; latest full `main` checkpoint — `v10.6-r3`.

## Зміни

- Панель дій вікна документів конкретного транспортного засобу стала адаптивною.
- Збережено «Додати документ», «Редагувати», «Архівувати», «Відкрити копію», «Оновити» та «Показувати архів».
- Контроли автоматично переносяться на наступний рядок, якщо ширини вікна недостатньо.
- Існуючі callback-и та `show_archived` не замінюються.
- Таблиця документів і її горизонтальна/вертикальна прокрутка не змінені.

## Межа змін

Це UI-only revision. Вона не змінює document schema, archive semantics, правила строків дії, копії файлів, vehicle data, шляхівки, plan/fact або тахографічні дані.

## Перевірка і публікація

- exact issued source: `e3f1666bafbd82e37ac2e63b08bfed2d265bae30`;
- full regression: **562/562 OK**;
- clean START verify run: `36463667268` — success;
- Actions artifact: `Taxo_v10_6_candidate_r7_START`, ID `10989440117`;
- prerelease publisher run: `36467902934` — success;
- immutable project checkpoint: `v10.6-r7` → `e3f1666bafbd82e37ac2e63b08bfed2d265bae30`;
- Release asset: `Taxo_v10_6_candidate_r7_START.zip`;
- Release asset SHA-256: `5fe124b6865419a14f4073d9bbb54efe18a3142a1e44aa03dc1339554e2a49fd`;
- checksum manifest: `SHA256SUMS_v10_6_r7.txt`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r7  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r7/Taxo_v10_6_candidate_r7_START.zip

`v10.6-r7` не зливався у `main`; latest full checkpoint у `main` лишається `v10.6-r3`, stable — `v10.3`.
