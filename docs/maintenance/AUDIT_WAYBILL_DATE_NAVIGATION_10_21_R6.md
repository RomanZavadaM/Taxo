# Аудит 10.21-r6 — навігація по даті у вікні «Шляхівки»

**Дата:** 17.11.2026. **Підстава:** зауваження власника під час роботи з кілометражем.  
**Exact release source:** `ef444e7753ee0f112baf8729ca6cceefea738652`.

## Межі зміни

- У вже існуючому вікні «Шляхівки» read/navigation-only поле дати `ДД.ММ.РРРР`.
- Enter і «Перейти» завантажують рядки вибраного дня.
- «День -», «Сьогодні», «День +» змінюють лише `waybill_date` цього вікна.
- Невірний формат дати дає явну помилку й відновлює попередню коректну дату.
- Головна дата графіка не змінюється.
- Реалізація окремим модулем `waybill_date_navigation.py`; нова UI-логіка не додана у `main.py`.

## Не змінювалися

БД/schema, записи пробігу, перевірки спідометра, формування/анулювання шляхівок, план/факт, backup/restore, release/security механізми та зовнішні залежності.

## Перевірки

- Regression: `tests/test_v10_21_r6_waybill_date_navigation.py` — формат дати, перехід/зсув, відновлення після помилки, feature registration та відсутність SQL-мутування.
- Проміжний START на `43bdb5a…`: 1464 tests, 1 failure лише через пропущений descriptor layer; виправлено до final head.
- Final PR head `e94c39080e2d2ab0e3db25bc7639edd50483c70f`: START 1464/1464, Windows/Win7/macOS SUCCESS.
- Product PR #506 merged; exact source `ef444e7753ee0f112baf8729ca6cceefea738652`.
- Exact-source CI: START `44150116439` **1464/1464**; Windows `44150116540`; Win7 `44150116763`; macOS Intel/ARM `44150116499` SUCCESS; Defender/integrity PASS.
- Release-trigger #507 merged `f89351973061538407e64e5c9746a0aec358bca9`; publisher `44151934906` SUCCESS.
- Test prerelease [v10.21-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r6): 6 assets, immutable tag exact source. Stable/Latest `v10.21-r2` unchanged.

## Ручне тестування власником

У цій сесії нове поле дати ще не перевірялося вручну на комп'ютері власника. Для короткої перевірки: відкрити «Шляхівки», перейти на іншу дату через поле/Enter, потім День-/День+, внести кілометраж у вибраному дні й переконатися, що повернення між днями показує збережені значення.
