# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r9.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`; stable/tag/assets незмінні.
- **Останній test artifact-checkpoint — 10.17-r9:** [draft PR #375](https://github.com/RomanZavadaM/Taxo/pull/375), branch `work/v10.17-r9-driver-register-ui`, exact code head `0a61634932779024c03d09a2f72fe1d6575e69ac`, **не merged у main**.
- Реєстр водіїв: клікабельне сортування усіх 6 заголовків; ID — число, дати народження/прийняття — дата, ПІБ/посвідчення — природний текст, статус — явний порядок «Так»/«Ні». Після «Оновити» чинне сортування і вибраний водій відновлюються за стабільним driver ID; підживлення списків табелів/бланків незмінне.
- Вікно пулів серій/номерів шляхівок: неоднозначну кнопку «Закрити / активувати» перейменовано на **«Деактивувати / активувати пул»**; додано окрему **«Закрити вікно» → `win.destroy`**, яка не змінює стан пулу. Стандартний X також не викликає запис, повторне відкриття працює через наявний single-window guard.
- START/source [43246695276](https://github.com/RomanZavadaM/Taxo/actions/runs/43246695276) **SUCCESS, 1200 tests OK**, START artifact `13956962484`.
- Exact-head platform CI: Windows [43246709702](https://github.com/RomanZavadaM/Taxo/actions/runs/43246709702), Win7/Python 3.8 [43246709857](https://github.com/RomanZavadaM/Taxo/actions/runs/43246709857), macOS Intel/ARM [43246709856](https://github.com/RomanZavadaM/Taxo/actions/runs/43246709856). **Міжплатформний gate ще перевіряється перед merge recovery**.
- r9 — тестовий Actions checkpoint; GitHub tag/release не створено. Stable/Latest v10.16-r8 незмінна. Бібліотеку шаблонів і сховище документів не чіпали.
- **Ручний Windows UI/DPI gate** 100/125/150 %, фокус/табуляція, X із незбереженими даними та повторне відкриття залишаються pending.

## Рішення власника

- Продовжувати карту аудиту й перевіряти не лише кнопки, а навігацію, доступність функцій, збереження даних і регресії.
- **Бібліотеку шаблонів і сховище документів не чіпати**; повернутися до їх проєктування окремо після завершення поточної роботи.
- Продовжувати модульну перебудову; скорочення коду не є ціллю.
- Stable 10.16-r8 не змінювати; тестовий код не зливати в `main` без прямої команди.

## Наступна дія

1. Почати із `START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub і PR #375 exact head → `PROJECT_STATE.md`.
2. **Нова кодова ревізія 10.17-r10** тільки після повного CI PASS і злиття документаційного recovery r9 в `main`: перевірити журнал історії наказів і наступні робочі таблиці, типи datetime/status/text та сортування без втрати вибору. Продовжити аудит службових Toplevel.
3. Усе фіксувати в GitHub і провести повний regression/CI. Stable/Latest 10.16-r8 не змінювати, тестовий код не зливати без прямої команди власника.
4. Не чіпати бібліотеку шаблонів / сховище документів. Ручний Windows UI/DPI smoke — окремий незакритий gate.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
