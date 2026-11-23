# Taxo 10.24-r6 — повний live-control кореспонденції

**Test-кандидат. Stable/Latest залишається 10.24-r3; поточний опублікований Test до видачі цього кандидата — 10.24-r5.**

10.24-r6 не додає нової бізнес-функції. Це контрольний пакет після r1–r5: він переводить критичні дії кореспонденції з рівня «кнопка/тест існує» у строгий executable route contract із live Tk reachability.

## Що захищено

До `src/taxo/function_registry.py` додано 16 нових critical routes поверх наявного `correspondence.center`. Загалом у Taxo тепер **55 strict routes**, із них **17 — кореспонденція**.

Live-control охоплює:
- відкриття центру «Кореспонденція»;
- «Новий вхідний…»;
- «Новий вихідний…»;
- «Відповісти…»;
- «Вкладення…»;
- «Відкрити документ»;
- «Отримано…»;
- «Надіслано…»;
- «Змінити стан…»;
- «Історія…»;
- «Нова справа…»;
- «Справа…» / прив'язка листа;
- «Перейменувати…»;
- «Архівувати / Відновити»;
- «Додати пов'язані»;
- «Відкрити лист» зі справи;
- «Вилучити зі справи».

Кожен route має `runtime_smoke=True`, mapping у `runtime_reachability.py` і живий Tk-тест, який повинен довести **mapped + onscreen + usable + activation**. Якщо кнопка зникне, стане disabled, вийде за межі доступного контейнера або перестане активувати дію — meta-gate має падати.

«Відкрити документ» перевіряється без запуску зовнішньої програми через безпечний `order:` reference: кнопка активується і виконує штатний маршрут-повідомлення.

## Що не змінюється

- registry/attachments/states/cases data model r1–r5;
- sent/received, due/overdue та state history;
- case membership, нумерація і backup/restore;
- UI layout кореспонденції;
- Stable/Latest;
- automatic e-mail, mailbox sync, external integrations, OCR/AI APPLY і physical attachment purge.

## Prep verification

Prep PR #629 final head `1d9a2f3de70eed3a27bf488cbbae7c6f29ddbecf`:
- START #45204102723 — SUCCESS;
- Windows #45204102869 — SUCCESS;
- Windows 7 #45204102379 — SUCCESS;
- macOS Intel/ARM #45204102369 — SUCCESS;
- Windows/Win7 Defender та post-scan integrity — SUCCESS.

Prep merged у main як `af6fb1d0adf86627e119cadb77ca0a0912475987`.

Наступний контрольний slice після r6 за поточним аудитом — базові дії реєстру наказів, які мають source-tripwire, але ще не мають окремих strict live routes. Це контроль існуючої функціональності, не зміна бізнес-логіки наказів.
