# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r6.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. Stable assets і код stable не змінювалися.
- **Останній перевірений test artifact-checkpoint 10.17-r6:** [draft PR #369](https://github.com/RomanZavadaM/Taxo/pull/369), branch `work/v10.17-r6-route-ui-consistency`, exact final head `f7e9fef96d933aba8001b34d8984f2e2bef47d68`, не merged у `main`.
- За картою `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md` завершено прохід **Маршрутів** і залишкового діалогу **Експлуатації**. У головній картці маршруту, редакторі точки, редакторі частини зміни та обох швидких редакторах є явне non-saving **«Скасувати»**; стандартний X також не викликає callback збереження.
- Локальне видалення точки або частини маршруту тепер потребує підтвердження. «Вимкнути» маршрут лишається окремою підтвердженою деактивацією без фізичного видалення історії.
- Реєстр маршрутів: усі 8 заголовків сортуються кліком через спільний `table_sorting.sort_treeview`; повторний клік перемикає ▲/▼; після «Оновити» зберігаються вибране сортування та вибраний маршрут за стабільним ID.
- В Експлуатації перевірені редактор наказу, закріплення, масове закріплення, учасники/ТЗ, preview та редактор інструктажу — вони вже мали «Скасувати»/«Закрити». У вікно **«Історія наказу»** в r6 додано явне **«Закрити» → тільки `dlg.destroy`**, без зміни БД або історії.
- START/source [43229483181](https://github.com/RomanZavadaM/Taxo/actions/runs/43229483181) **SUCCESS, 1182 tests OK**. Exact-head platform CI: Windows [43229499946](https://github.com/RomanZavadaM/Taxo/actions/runs/43229499946), Win7/Python 3.8 compatibility [43229499993](https://github.com/RomanZavadaM/Taxo/actions/runs/43229499993), macOS Intel/ARM [43229499965](https://github.com/RomanZavadaM/Taxo/actions/runs/43229499965) — **усі SUCCESS**.
- CI artifacts: START `13949052740`; Windows x64 `13949472964`; Win7 x64 `13950591080`; macOS Intel `13949955949`; macOS ARM `13950760757`.
- Windows portable `Taxo_v10_17_candidate_r6_Windows_x64_Portable.zip` SHA-256 `17608016c532d9066ae7db451fabc9c60c1b0079db30d4ad4e48738ebc366eb6`; Setup SHA-256 `31976f5926961dd70eb6c0865334fa059c12550f7f28322d9717d11cda1f6745`. Обидва значення повторно обчислені з artifact #13949472964 і збігаються з CI manifest.
- r6 — тестовий Actions artifact-checkpoint, **GitHub tag/release не створено**. PR #369 лишається draft/unmerged. Stable/Latest v10.16-r8 незмінна.
- **Ще не виконано фізичне Windows UI-приймання** 100/125/150 % DPI, табуляції/фокуса і вкладених modal-вікон. Автоматичні regression/Tk-перевірки не заміняють цей візуальний gate.

## Рішення власника

- Продовжувати карту аудиту й перевіряти не лише кнопки, а навігацію, доступність функцій, збереження даних і регресії.
- **Бібліотеку шаблонів і сховище документів не чіпати**; повернутися до їх проєктування окремо після завершення поточної роботи.
- Продовжувати модульну перебудову; скорочення коду не є ціллю.
- Stable 10.16-r8 не змінювати; тестовий код не зливати в `main` без прямої команди.

## Наступна дія

1. Відновлення: `START_HERE.md` → цей файл → private Taxo-profile → live GitHub `main` / draft PR #369 / exact-head checks.
2. **Наступна нова кодова ревізія 10.17-r7:** перейти до реєстру працівників та інших таблиць — підключати спільне сортування з правильними типами дат/чисел/тексту, не порушуючи фільтри й вибір рядка.
3. Паралельно в межах того ж аудиту продовжити інвентаризацію службових/налаштувальних Toplevel на явний вихід, X, незбережені дані та destructive actions.
4. Окремо залишається ручний Windows UI/DPI smoke; automation його не замінює.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
