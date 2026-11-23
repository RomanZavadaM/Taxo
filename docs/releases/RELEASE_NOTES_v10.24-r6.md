# Taxo 10.24-r6 — повний live-control кореспонденції

**Опублікований Current Test. Stable/Latest залишається 10.24-r3.** Exact source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`; 8 canonical assets; `prerelease=true`; publisher #45209524416 — SUCCESS.

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

## Публікація Test

Candidate PR #631 merged у main як exact issued source `d713dd2b085216d8ec764fb16a3ab057f01f07ec`. На exact source успішно пройшли START #45207404713, Windows #45207404491, Win7 #45207404242 і macOS Intel/ARM #45207404447. Release-trigger PR #632 merged як `4dec0786d2dfc50e718f52901f8a012bf08d58e8`; його START #45208494055, Windows #45208494039, Win7 #45208494062 і macOS #45208494429 — SUCCESS. Publisher #45209524416 опублікував `v10.24-r6` як prerelease з 8 canonical assets.
