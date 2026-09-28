# Taxo 10.6-r5 — адаптивні фільтри звіту документів ТЗ

**Тип:** fast-test candidate  
**База:** issued `v10.6-r4`; latest full `main` checkpoint — `v10.6-r3`.

## Зміни

- Верхня панель звіту «Стан документів транспортних засобів» стала адаптивною.
- Група `дата + поле + Дата…` не розривається.
- Прапорці «Тільки авто в експлуатації» та «Тільки проблемні / попередження» переносяться на новий рядок, якщо ширини бракує.
- «Тільки авто в експлуатації» залишається ввімкненим за замовчуванням.
- Таблиця, горизонтальна/вертикальна прокрутка, SQL, експорт PDF/Excel та правила документів не змінені.

## Межа змін

Це UI-only revision. Вона не змінює БД, шляхівки, plan/fact, тахографічний факт або склад обов'язкових документів.

## Перевірка і публікація

- exact issued source/tag target: `118d4111e183528c49e8060e8782479fa4436377`;
- regression: **546/546 OK**;
- clean START verify: run `36452858366` — success;
- prerelease publisher: run `36461104704` — success;
- tag/release: `v10.6-r5`;
- START asset: `Taxo_v10_6_candidate_r5_START.zip`;
- START SHA-256: `8586e5aa6c07860ea4aeda5eaf76b409acc4719b41a9b60da991c3ca14ec27c9`;
- checksum manifest: `SHA256SUMS_v10_6_r5.txt`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r5  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r5/Taxo_v10_6_candidate_r5_START.zip

`v10.6-r5` після видачі не пересувається і не переписується. Наступна кодова ревізія — `10.6-r6`.
