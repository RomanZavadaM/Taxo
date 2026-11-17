# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Завершена продуктова ревізія: **10.21-r6**, product PR #506 merged, exact immutable source `ef444e7753ee0f112baf8729ca6cceefea738652`.
- Exact-source CI: START `44150116439` — **1464/1464**; Windows `44150116540`, Win7 `44150116763`, macOS Intel/ARM `44150116499` — SUCCESS; Defender/integrity PASS.
- Release-trigger PR #507 merged `f89351973061538407e64e5c9746a0aec358bca9`; publisher `44151934906` SUCCESS.
- [v10.21-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r6): Test prerelease, 6 assets (4 Portable + START + SHA256), immutable tag target `ef444e7753ee0f112baf8729ca6cceefea738652`.
- **Stable/Latest:** [v10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2), 8 assets, unchanged, immutable source `b104f94ace0ae355df79c914b3be6f39417bd6e9`.

## Результат 10.21-r6

- Вікно «Шляхівки» має власне редаговане поле дати `ДД.ММ.РРРР`.
- Enter або «Перейти» показує шляхівки вибраного дня; «День -», «Сьогодні», «День +» дають послідовну навігацію при перенесенні кілометражу.
- Навігація змінює лише `waybill_date` відкритого вікна та оновлює його список; головна дата графіка не переписується.
- UI-логіка винесена в окремий `src/taxo/waybill_date_navigation.py`; `main.py` не роздувався новою реалізацією.
- Немає змін БД/schema, правил пробігу, видачі/анулювання шляхівок, plan/fact, backup/restore, security або залежностей.

## Активна кодова ревізія

Немає. **10.21-r7 ще не розпочата.**

## Наступний крок

Після fresh GitHub verification, включно з гілками без PR, врахувати ручний результат перевірки r6 або вибрати один новий вузький крок. Stable не змінювати без прямої команди власника.

## Recovery

На проміжному head r6 перший START мав 1/1464 failure лише через відсутній descriptor нового layer у `feature_layers.py`; виправлено до merge. Final work head `e94c39080e2d2ab0e3db25bc7639edd50483c70f`; exact release source `ef444e7753ee0f112baf8729ca6cceefea738652`; усі final/exact checks SUCCESS. Докладний аудит: [навігація дати шляхівок](docs/maintenance/AUDIT_WAYBILL_DATE_NAVIGATION_10_21_R6.md).

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
