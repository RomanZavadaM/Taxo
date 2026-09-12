# Taxo v8.64 — recovery checkpoint

Дата: 12.09.2026

Поточний кандидат: **v8.64**. Стабільний `main`: **v8.56**. Не просувати `main` до локальної Windows-перевірки.

## Ключова архітектура

- DOCX створюється через `python-docx`, без Microsoft Word.
- PDF створюється автономно через PyMuPDF із вбудованого `attestation_visual_template.pdf`.
- JPG сторінок створюються з автономного PDF.
- Runtime не залежить від Word, LibreOffice, COM або `pywin32`.
- PDF/JPG мають візуально повторювати офіційний DOCX-бланк.
- Збережено прокрутку вкладок, безстрокове зберігання бланків, фільтр `Активні / Вилучені / Усі` та остаточне видалення з резервною копією.

## Контрольні архіви

- `Taxo_v8_64_TEST.zip` SHA-256 `03a0f6c6330c39bebfc748f51cb607eeee966d3ca1671dd518545aeb8b138a85`
- `Taxo_v8_64_source.zip` SHA-256 `1fffdadd03cb6118f6aaeece557b323f1cd1f130fa081e35659fb14b339d480f`

Повні контрольні копії також збережені у ChatGPT Library `/Taxo/Releases/`.
