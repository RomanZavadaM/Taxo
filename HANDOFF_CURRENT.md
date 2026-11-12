# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r7.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. Stable assets і код stable не змінювалися.
- **Останній перевірений test artifact-checkpoint 10.17-r7:** [draft PR #371](https://github.com/RomanZavadaM/Taxo/pull/371), branch `work/v10.17-r7-employee-register-sorting`, exact final head `42319cc85cec392c6cd94815c9dd92c0b33118df`, не merged у `main`.
- Основний реєстр працівників: усі 8 заголовків сортуються кліком через спільний `table_sorting.sort_treeview`; типи задані явно — текст, дата, тривалість і статус. Повторний клік перемикає ▲/▼.
- Після `Оновити` та зміни пошукового фільтра чинне сортування застосовується повторно. Вибраний працівник зберігається за стабільним employee ID; якщо фільтр тимчасово приховує рядок, ID пам'ятається і вибір відновлюється після повернення рядка.
- Сумісний legacy-реєстр працівників приведено до того самого контракту; ID/оклад сортуються як числа, дати прийняття/звільнення — як дати, стан — як статус. Shared sorter розширено типами `number/date/duration/status` без зміни старої поведінки реєстрів ТЗ і маршрутів.
- Паралельний UI-аудит: налаштування Експлуатації є вкладкою і пишуть у БД лише через явну кнопку **«Зберегти»**; окремий **«Простий місячний графік роботи»** має явні **«Записати план»** і **«Закрити»**, а default X не викликає callback запису. Результат зафіксовано у `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md`.
- START/source [43237520972](https://github.com/RomanZavadaM/Taxo/actions/runs/43237520972) **SUCCESS, 1188 tests OK**. Exact-head platform CI: Windows [43237531429](https://github.com/RomanZavadaM/Taxo/actions/runs/43237531429), Win7/Python 3.8 compatibility [43237531436](https://github.com/RomanZavadaM/Taxo/actions/runs/43237531436), macOS Intel/ARM [43237531386](https://github.com/RomanZavadaM/Taxo/actions/runs/43237531386) — **усі SUCCESS**.
- CI artifacts: START `13953551669`; Windows x64 `13954256090`; Win7 x64 `13953387497`; macOS Intel `13954235887`; macOS ARM `13953446999`.
- r7 — тестовий Actions artifact-checkpoint, **GitHub tag/release не створено**. PR #371 лишається draft/unmerged. Stable/Latest v10.16-r8 незмінна.
- **Ще не виконано фізичне Windows UI-приймання** 100/125/150 % DPI, табуляції/фокуса та поведінки X із реально введеними незбереженими значеннями. Автоматичні regression/Tk-перевірки не заміняють цей візуальний gate.

## Рішення власника

- Продовжувати карту аудиту й перевіряти не лише кнопки, а навігацію, доступність функцій, збереження даних і регресії.
- **Бібліотеку шаблонів і сховище документів не чіпати**; повернутися до їх проєктування окремо після завершення поточної роботи.
- Продовжувати модульну перебудову; скорочення коду не є ціллю.
- Stable 10.16-r8 не змінювати; тестовий код не зливати в `main` без прямої команди.

## Наступна дія

1. Відновлення: `START_HERE.md` → цей файл → private Taxo-profile → live GitHub `main` / draft PR #371 / exact-head checks.
2. **Наступна нова кодова ревізія 10.17-r8:** продовжити type-aware сортування на інших реально вживаних реєстрах/таблицях, по одному безпечному блоку за раз; наступним кандидатом перевірити реєстр наказів та інші таблиці з датами/номерами/статусами.
3. Паралельно продовжити аудит службових і налаштувальних Toplevel: явний вихід, X, незбережені дані, destructive actions, повторне відкриття та зрозумілість дій.
4. Бібліотеку шаблонів і сховище документів не чіпати. Окремо залишається ручний Windows UI/DPI smoke; automation його не замінює.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
