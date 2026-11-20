# PROJECT_STATE — Taxo

**Підтверджено GitHub 20.11.2026 після публікації 10.23-r4.**

**Stable/Latest:** [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1), exact source `84184bbbf6c26b681c04feaebee19910269bd25c`, 8 assets.

**Поточний Test:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact product/release source `a919ced6bc8665ced70ebb4d897808e4e2618667`, prerelease, 8 assets. r3 інтегрований раніше, але окремий v10.23-r3 навмисно не видавався за прямою вказівкою власника.

## 10.23-r4

- Перегляд наказу адаптовано для малого вікна: форматні дії DOCX/PDF/JPG — дві колонки, нижні дії — стабільна 2×2 сітка.
- Пояснювальний текст, статус формату та опис «Експлуатації» переносяться за реальною шириною.
- Виправлено приховування форматних кнопок при мінімальній висоті: основний Text більше не резервує надмірну висоту.
- Реєстр збереження функцій має новий strict runtime route `operations.order_preview_formats`; live Tk gate перевіряє 760×560 і центр 940×600.

## Перевірка й публікація

Exact-main source `a919ced6bc8665ced70ebb4d897808e4e2618667`:
- START #44803423646 — SUCCESS;
- Windows #44803423874 — SUCCESS, Defender/integrity PASS;
- Windows 7 #44803423649 — SUCCESS, Defender/integrity PASS;
- macOS Intel/ARM #44803423740 — SUCCESS;
- publisher #44804999191 — SUCCESS.

Release v10.23-r4 перевірено після публікації: tag target збігається з exact source, prerelease=true, 8 assets. Stable/Latest лишається v10.23-r1.

## Наступне

Наступна кодова ревізія — **10.23-r5**. Один змістовний пакет із залишку #556: малий viewport «Документи → Каталог» — дерево, таблиця, нижні дії, прокрутка/доступність + live regression. #553/#556/#562 лишаються відкритими до ручного приймання. Draft #543/#395 не змінювати.

GitHub — canonical. Drive: документаційний резерв `05_CURRENT_DOCS_2026-11-20_main-r3`; код і binary releases на Drive не дублювати.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
