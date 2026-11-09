# HANDOFF_CURRENT — Taxo

**Оновлено:** 09.11.2026 — stable v10.14-r4 збережено; інтегровано й повністю перевірено 10.14-r8.

## Фактичний стан

- **Stable / GitHub Latest:** [v10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4), 8/8 canonical assets. Stable/tag під час r5–r8 не змінювався.
- **Поточний main / інтегрований кандидат:** Taxo **10.14-r8**, exact main commit `98c9f2daea8398c1bf18b64e5f96163c6c02e4cc`, PR #280.
- **Exact-main CI r8:** START #2511, Windows #1396, Win7 #372, macOS Intel/ARM #1297 — **SUCCESS**.
- **Regression:** exact-main START **1033 tests / OK**. Окремо PASS: persistence single+bulk → commit → close DB → reopen; stale preview → fresh DOCX data; existing order → Edit → current assignments → bulk picker.
- **Наступна кодова ревізія:** **10.14-r9**. Виданий r8 не перевикористовувати.
- **Попередня стабільна / rollback:** [v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10).

## Що зроблено у 10.14-r6…r8

- r6 закрив Feature Loss у масовому виборі закріплень і почав окремий live-route контроль для цього робочого сценарію.
- r7 ввів строгий gate для критичних UI-маршрутів: функція вважається збереженою лише якщо вона реально mapped + onscreen + usable + activation.
- r8 після owner-test наказу №27 виправив уже не видимість кнопки, а **ланцюг даних до друку**:
  - у вже створеному наказі видно поточні пари і є прямі дії «Додати багато…» / «Керувати закріпленнями»;
  - одиночне і масове додавання перевіряють, що вибрані пари реально записані до commit;
  - після commit тест закриває БД, відкриває її знову і перевіряє всі пари;
  - вікно «Перегляд наказу» перед кожним DOCX/PDF/JPG заново читає актуальні дані з БД;
  - у Preview є «Оновити зміст»;
  - порожній новий наказ про закріплення веде у вкладку «Закріплення водіїв», а не одразу в порожній друк;
  - raw assignment більше не може мовчки зникнути з наказу через INNER JOIN.
- Старий docs PR #278 (r6 checkpoint) закрито без злиття як застарілий; r8 checkpoint робиться від фактичного main.

## Резерв

- Exact-main START artifact: GitHub Actions #2511, artifact ID `13677776040`, `Taxo_v10_14_candidate_r8_START`, 1 748 707 байт.
- SHA256 локальної копії: `e75beea340ea24088a05d90fcb37c7c96edbed7f6c2d41e81a586cf0494e7284`.
- Google Drive `02_CURRENT_MAIN`: `Taxo_CURRENT_MAIN_v10.14-r8_2026-11-09_START.zip`, file ID `1ObOoSjHZvMmOzMgkNDULCCnQ0M42B7F3`, 1 748 707 байт.
- Робочі SQLite, скани й документи персоналу в цей recovery ZIP не входять.

## Відкриті напрями

- #246 — ширший спільний вибір працівників/ТЗ;
- #237 — планування інструктажів;
- #164 — UX-спрощення;
- #251 — оптимізація CI для docs/release checkpoint;
- #61 — live development ledger.

## Одна наступна безпечна дія

Ручне приймання **10.14-r8** на реальній робочій БД: створити/відкрити наказ про закріплення → додати одну пару → додати кілька пар → закрити/повторно відкрити вікно → перевірити, що вкладка показує правильне `закріплень: N` → створити DOCX/PDF/JPG і звірити, що всі водії та ТЗ є в таблиці.

Новий код за наступним знайденим дефектом — тільки **10.14-r9**. Stable v10.14-r4 не просувати без окремого рішення власника.
