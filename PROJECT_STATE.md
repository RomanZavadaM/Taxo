# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Завершена продуктова ревізія: **10.21-r5**, product PR #503 merged, exact immutable source `d3f01d1cefd11ac5cab15054dfab85d962c0a84c`.
- Exact-source CI: START `44141706069` — **1459/1459**; Windows `44141706165`, Win7 `44141706293`, macOS Intel/ARM `44141706021` — SUCCESS, Defender/integrity PASS.
- Release-trigger PR #504 merged `1515b1b52fe0a9e9d38d49bed7fd4f06f0de674f`; publisher run `44143863239` SUCCESS.
- [v10.21-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r5): Test prerelease, 6 assets (4 Portable + START + SHA256), immutable tag target `d3f01d1cefd11ac5cab15054dfab85d962c0a84c`.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 assets, unchanged, immutable source `b104f94ace0ae355df79c914b3be6f39417bd6e9`.

## Результат 10.21-r5

- Натискання заголовка «№» у «Документи» перемикає натуральне сортування номерів: 2 перед 10, 2-А перед 10-А; порожні номери наприкінці.
- Обробка всього відфільтрованого списку перед пагінацією; комбінація з пошуком, джерелом, типом, сканами, періодом «Від / До».
- Після перемикання — перша сторінка; сортування «Дата» з r4 не втрачено.
- Немає змін сховища, файлів, scan/backup/restore, статусів, БД, OCR, КЕП та залежностей.

## Активна кодова ревізія

Немає. **10.21-r6 ще не розпочата.**

## Наступний крок

Після live GitHub verification, включно з гілками без PR, вибрати один новий вузький крок Issue #289 для **10.21-r6**. Stable не змінювати без прямої команди.

## Recovery

Перед r5: main `fd0e97f9af7cb54bf5112188cd1004e414d829fe`, 415 refs, r5 не була почата. Спочатку тест знайшов неправильне екранування `\\d` у regex; виправлено до merge, final 1459/1459. Основний журнал — Issue #61, історія — WORKLOG. Докладний аудит r5: [номер](docs/maintenance/AUDIT_DOCUMENT_NUMBER_SORT_10_21_R5.md).

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
