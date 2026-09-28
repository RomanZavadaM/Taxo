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

## Перевірка та видача

- exact issued source / tag target: `2705fb5c9105e21bfb669a2d40d4f29449e1a00b`;
- full regression: **578/578 OK**;
- clean START verify run: `36472489549` — success;
- Actions artifact: `Taxo_v10_6_candidate_r9_START`, ID `10992162136`;
- prerelease publisher run: `36472783754` — success;
- GitHub prerelease: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r9
- START asset: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r9/Taxo_v10_6_candidate_r9_START.zip
- START Release SHA-256: `37a6214bb4ba5b33569804e3efb06912549625600361cf510d52808a55a0a8c4`;
- checksum manifest: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r9/SHA256SUMS_v10_6_r9.txt

`v10.6-r9` виданий як immutable fast-test checkpoint за правилами проєкту. Stable `v10.3` і latest full multi-platform checkpoint у `main` `v10.6-r3` не пересувались. Наступна кодова ревізія — тільки `10.6-r10`.
