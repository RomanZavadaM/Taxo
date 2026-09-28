# Taxo 10.6-r6 — адаптивна панель команд реєстру ТЗ

**Тип:** fast-test candidate  
**База:** issued `v10.6-r5`; latest full `main` checkpoint — `v10.6-r3`.

## Зміни

- Панель команд вкладки транспортних засобів більше не залежить від одного довгого горизонтального рядка.
- Збережено всі існуючі дії: «Нове авто», «Редагувати», «Документи», «Контроль документів», «Вивести з експлуатації», «Оновити».
- Збережено прапорець «Сховати неактивні автомобілі»; він як і раніше увімкнений за замовчуванням.
- Кнопки і прапорець автоматично переносяться на наступний рядок, якщо ширини вікна недостатньо.
- Існуючі callback-и, значення фільтра, дані автомобілів, документи та статуси не змінюються.

## Межа змін

Це UI-only revision. Вона не змінює схему БД, vehicle/document business rules, шляхівки, plan/fact або тахографічні дані.

## Перевірка і публікація

- exact issued source/tag target: `90ab67ae00be381f8b2bc14e18f9614574e3493f`;
- regression: **554/554 OK**;
- clean START verify: run `36462366765` — success;
- Actions artifact: `Taxo_v10_6_candidate_r6_START`, ID `10988412209`;
- prerelease publisher: run `36462529738` — success;
- tag/release: `v10.6-r6`;
- START asset: `Taxo_v10_6_candidate_r6_START.zip`;
- START Release SHA-256: `7493202b3282ffba5238342136dd3a19a5cd7f663514c12eb3827451eff83e79`;
- checksum manifest: `SHA256SUMS_v10_6_r6.txt`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r6  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r6/Taxo_v10_6_candidate_r6_START.zip

`v10.6-r6` після видачі не пересувається і не переписується. Наступна кодова ревізія — `10.6-r7`.
