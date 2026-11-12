# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r4.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. `main` і stable assets не змінювалися кодом. Попередні тестові контрольні точки: r9 `53428d4287c0f4e83a55a739109c0bd209e3a623` (draft #355), r10 `1b39d60a7bce22843ebab575faa7173e3c818454` (draft #357), 10.17-r1 `fa9ba20497cd179038129cb61ad9d72df1617cc0` (draft #359), r2 `eb77fa477e75daa9a9264fbab4f07adf99184d2b` (draft #361), r3 `190f920b78160dca2510321921631ee720bd8d16` (draft #363).
- **Останній перевірений test artifact-checkpoint 10.17-r4:** [draft PR #365](https://github.com/RomanZavadaM/Taxo/pull/365), branch `work/v10.17-r4-stoir-dialog-cancel`, exact code head `f80e7559a4c3b7922da0fa9cb5b5fb3eb9caca2e`, не merged у main.
- Згідно з картою `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md` додано явну кнопку **«Скасувати»** до трьох дочірніх форм СТОІР: запис ТО/ремонту, нова заявка, зміна/закриття заявки. Форма профілю ТО вже мала скасування. Нові команди тільки `dialog.destroy`; існуючі callback збереження, облік, SQLite та дочірні дані не змінені.
- Аудит r4 у файлі за PR #365 розмежовує виправлення за кодом і **поки не виконане ручне** приймання X/Скасувати/Зберегти з незбереженими полями, повторного відкриття та 100/125/150 % DPI. У тахографі вже локалізовано наступну аналогічну невідповідність — `tachograph.py: interval_form` має тільки «Зберегти»; статистика/скан/протоколи мають «Закрити». Це кандидат r5.
- START/source [43222679904](https://github.com/RomanZavadaM/Taxo/actions/runs/43222679904) **SUCCESS, 1166 tests OK**, code head `eb4c8c4c27db10247b981dfd75d812ae11da150f`. Наступний єдиний commit до final head змінює лише Markdown audit. Final-head Windows [43222794856](https://github.com/RomanZavadaM/Taxo/actions/runs/43222794856), Win7 Python 3.8 [43222794843](https://github.com/RomanZavadaM/Taxo/actions/runs/43222794843), macOS Intel/ARM [43222794848](https://github.com/RomanZavadaM/Taxo/actions/runs/43222794848) — **усі SUCCESS**.
- CI artifacts: START `13945373845` (code-identical head); Windows x64 `13946064692`, Win7 x64 `13945364358`, macOS Intel `13946781165`, macOS ARM `13946945506` (усі платформи exact final head). Windows portable `Taxo_v10_17_candidate_r4_Windows_x64_Portable.zip` витягнуто з CI, SHA-256 `85b8fedac930df690865e2efa627ff5f0687c3fcb574c3d2bbc3f4300aeccb48` збігається з маніфестом.
- r4 — тестовий Actions artifact-checkpoint, **GitHub tag/release не створено**. Stable/Latest v10.16-r8 лишається без змін.

## Рішення власника

- Продовжувати послідовну роботу по карті аудиту та завершення поточної модульної перебудови, зі зрозумілими виходами з робочих сторінок і діалогів.
- **Бібліотеку шаблонів і сховище документів не чіпати**; окреме проєктування лише після завершення поточного етапу та переходу в новий чат.
- Не змінювати stable r8 без прямої команди, тестові PR не зливати як код у main.

## Наступна дія

1. Відновлення: `START_HERE.md` → цей файл → private Taxo-profile → live GitHub main / draft PR #365 / exact-head checks.
2. **Наступна нова кодова ревізія 10.17-r5**: перевірити й виправити `tachograph.interval_form` (видима не-зберігаюча «Скасувати»), інші тахографічні Toplevel/X та їхній стан; не зачіпати аналіз тахокарт або протоколи даних без потреби.
3. Провести ручний Windows UI smoke форм СТОІР і нових вікон. Автоматичний regression не замінює інтерактивне тестування.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
