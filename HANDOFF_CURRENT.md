# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r8.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, exact stable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`; жодних змін stable/tag/assets.
- **Останній перевірений test artifact-checkpoint — 10.17-r8:** [draft PR #373](https://github.com/RomanZavadaM/Taxo/pull/373), branch `work/v10.17-r8-order-register-sorting`, exact head `d98dec73bb748a86972b535c614f1b36bd951e6e`, **не merged у main**.
- У реєстрі наказів усі 9 заголовків сортуються кліком. Дата сортується хронологічно, номер — природним порядком (2-К перед 10-К), стани наказу/паперового оригіналу — за явним порядком, інші поля — текст. Другий клік перемикає ▲/▼.
- Після refresh та зміни фільтра груп вибраний наказ відновлюється за стабільним ID, чинне сортування зберігається. Якщо вибраний наказ тимчасово прихований фільтром, він не підмінюється; після видалення наказу старий ID очищається разом із видимим вибором. Логіка наказів, підтвердження destructive actions, SQLite, PDF та backup не змінені.
- UI-аудит доповнено у `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md`. В історії наказу «Закрити» → тільки `dlg.destroy`; налаштування нумерації лишаються вкладкою центру Експлуатації.
- START/source [43243891648](https://github.com/RomanZavadaM/Taxo/actions/runs/43243891648) **SUCCESS, 1195 tests OK**. Exact-head Windows [43243908886](https://github.com/RomanZavadaM/Taxo/actions/runs/43243908886), Win7/Python 3.8 [43243909031](https://github.com/RomanZavadaM/Taxo/actions/runs/43243909031), macOS Intel/ARM [43243908747](https://github.com/RomanZavadaM/Taxo/actions/runs/43243908747) — **усі SUCCESS**.
- CI artifacts: START `13954838323`; Windows x64 `13956253300`; Win7 x64 `13955348499`; macOS Intel `13955258718`; ARM `13955677886`.
- r8 — **Actions test artifact-checkpoint**, GitHub tag/release не створено. Stable/Latest `v10.16-r8` незмінна.
- **Не завершено фізичне Windows UI-приймання** 100/125/150 % DPI, фокус, вкладені modal, поведінка X/незбережених даних. Автоматичний regression не заміняє реальний UI smoke.

## Рішення власника

- Продовжувати карту аудиту й перевіряти не лише кнопки, а навігацію, доступність функцій, збереження даних і регресії.
- **Бібліотеку шаблонів і сховище документів не чіпати**; повернутися до їх проєктування окремо після завершення поточної роботи.
- Продовжувати модульну перебудову; скорочення коду не є ціллю.
- Stable 10.16-r8 не змінювати; тестовий код не зливати в `main` без прямої команди.

## Наступна дія

1. `START_HERE.md` → цей файл → private Taxo-profile → live GitHub `main` / draft PR #373 / exact-head CI → `PROJECT_STATE.md`.
2. **Наступна кодова ревізія 10.17-r9:** послідовно підключити type-aware сортування в реєстрі водіїв (ID, дати, статус і текст) зі збереженням вибору після refresh; продовжити статичний аудит службових Toplevel/історії наказу без зміни їхніх даних.
3. Після regression/CI оформити наступний docs-only recovery-checkpoint. Stable 10.16-r8 не змінювати і тестовий код не зливати в `main`.
4. Не чіпати бібліотеку шаблонів і сховище документів. Фізичне Windows UI/DPI-приймання залишається окремим ручним gate.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
