# Taxo 10.6-r8 — адаптивна форма документа ТЗ

**Тип:** fast-test candidate  
**База:** issued `v10.6-r7`; latest full `main` checkpoint — `v10.6-r3`.

## Зміни

- Форма додавання/редагування документа транспортного засобу адаптується до невисокого/масштабованого вікна.
- При висоті менше 620 px стандартні вертикальні відступи полів ущільнюються.
- Поле «Примітка» в компактному режимі зменшується з 4 до 3 видимих рядків, щоб не притискати нижню кнопку «Зберегти».
- Пояснення про ручне архівування попередніх документів і про поточну копію отримують динамічний `wraplength` за фактичною шириною вікна.
- При поверненні до нормальної висоти початкові відступи і висота примітки відновлюються.
- Вікно лишається resizeable.

## Межа змін

Це UI-only revision. Runtime layer викликає існуючий `VehicleDocumentsWindow._form()` і адаптує вже створені widgets. `save()` closure, `EXPIRY_REQUIRED`, перевірка дат, `archive_current_document_slot()`, `copy_document_file()`, SQL, архівні semantics і робочі дані не переписуються.

## Перевірка і публікація

- exact issued source: `09f0e6e6cf3809b6d0efc6c9cdad7937a44d78d3`;
- full regression: **570/570 OK**;
- clean START verify run: `36469618323` — success;
- Actions artifact: `Taxo_v10_6_candidate_r8_START`, ID `10990373762`;
- prerelease publisher run: `36469958643` — success;
- immutable project checkpoint: `v10.6-r8` → `09f0e6e6cf3809b6d0efc6c9cdad7937a44d78d3`;
- GitHub Release asset: `Taxo_v10_6_candidate_r8_START.zip`;
- GitHub Release asset size: `1102820` bytes;
- Release asset SHA-256: `90e04c065a157aa1453e2aa50024ca3f4093de37db30be23ae007114531eb7ec`;
- checksum manifest: `SHA256SUMS_v10_6_r8.txt`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r8  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r8/Taxo_v10_6_candidate_r8_START.zip

`v10.6-r8` не зливався у `main`; latest full checkpoint у `main` лишається `v10.6-r3`, stable — `v10.3`.
