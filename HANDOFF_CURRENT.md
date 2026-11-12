# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r5.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. Stable assets і код stable не змінювалися.
- **Останній перевірений test artifact-checkpoint 10.17-r5:** [draft PR #367](https://github.com/RomanZavadaM/Taxo/pull/367), branch `work/v10.17-r5-tachograph-dialog-cancel`, exact final head `4615073fed50acff921c8b7b80928ab0ae531494`, не merged у `main`.
- За картою `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md` виконано повний поточний прохід тахографа, а не лише додавання кнопки. Редактор інтервалу має non-saving **«Скасувати»**, Cancel/default X не записують дані, modal grab звільняється, повторне відкриття працює; валідний Save окремо робить запис/commit/refresh.
- Виправлено перевірку ручного часу: дозволено тільки `00:00–23:59`; значення на кшталт `99:99` більше не можуть потрапити в SQLite. У вікні протоколів рознесено по окремих рядках горизонтальну прокрутку, деталі й «Закрити».
- Небезпечні дії зроблено зрозумілішими: `Видалити тест` перейменовано на **«Видалити тахокарту»**; видалення інтервалу потребує підтвердження; повторне розпізнавання попереджає перед заміною наявних, у тому числі ручних, інтервалів.
- Імпорт і тестове seed-наповнення більше не запускають destructive `recognize_all()`: новий `recognize_unprocessed()` обробляє тільки тахокарти без інтервалів і не видаляє вже перевірені дані. Також відновлено реально досяжне попередження, коли коло шайби не знайдено.
- START/source [43226444606](https://github.com/RomanZavadaM/Taxo/actions/runs/43226444606) **SUCCESS, 1177 tests OK**. Exact-head platform CI: Windows [43226454498](https://github.com/RomanZavadaM/Taxo/actions/runs/43226454498), Win7/Python 3.8 compatibility [43226454247](https://github.com/RomanZavadaM/Taxo/actions/runs/43226454247), macOS Intel/ARM [43226454270](https://github.com/RomanZavadaM/Taxo/actions/runs/43226454270) — **усі SUCCESS**.
- CI artifacts: START `13948173229`; Windows x64 `13948671038`; Win7 x64 `13948705865`; macOS Intel `13948665908`; macOS ARM `13947244468`. Windows portable `Taxo_v10_17_candidate_r5_Windows_x64_Portable.zip` SHA-256 `3c39dfe2a420d4c9ccfe075f43f6dc45e94603e567dcc7d474f9f21255b6aeef` звірено з CI manifest; Setup SHA-256 `d59b2d5709fe87914457eccbee03886966b514abab84ec7379067c3e511225cb` також збігається.
- r5 — тестовий Actions artifact-checkpoint, **GitHub tag/release не створено**. PR #367 лишається draft/unmerged. Stable/Latest v10.16-r8 незмінна.
- **Ще не виконано фізичне Windows UI-приймання** тахографа на 100/125/150 % DPI та оцінка фокуса/розмірів на реальному робочому екрані. Автоматичні Tk-тести перевіряють поведінку й дані, але не заміняють цей візуальний gate.

## Рішення власника

- Продовжувати послідовну роботу по карті аудиту; перевіряти не лише кнопки, а навігацію, доступність функцій, збереження даних і регресії.
- **Бібліотеку шаблонів і сховище документів не чіпати**; до їхнього проєктування повернутися окремо після завершення поточної роботи.
- Продовжувати модульну перебудову; скорочення коду не є ціллю.
- Stable 10.16-r8 не змінювати; тестовий код не зливати в `main` без прямої команди.

## Наступна дія

1. Відновлення: `START_HERE.md` → цей файл → private Taxo-profile → live GitHub `main` / draft PR #367 / exact-head checks.
2. **Наступна нова кодова ревізія 10.17-r6:** продовжити карту аудиту з **Маршрутів та решти діалогів Експлуатації** — X/Скасувати/Зберегти, повторний вхід, зрозумілість дій, destructive actions і правильність збереження.
3. Після цього перейти до ширшого застосування сортування таблиць (з окремими типами дат/чисел/тексту), якщо карта не виявить вищого пріоритету.
4. Окремо залишається ручний Windows UI/DPI smoke; automation його не замінює.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
