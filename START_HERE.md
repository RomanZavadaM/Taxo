# START_HERE — Taxo / Driver Worktime

> **Перша точка входу для будь-якої нової робочої сесії, нового чату або відновлення після обриву.**

Цей файл існує, щоб робота над Taxo відновлювалася з GitHub, а не з пам'яті конкретного чату.

## Startup protocol

### Швидке відновлення після обриву або нового чату

1. Прочитати цей файл.
2. Прочитати `HANDOFF_CURRENT.md`.
3. Звірити фактичний GitHub: актуальний `main`, відкриті PR, active head і останні перевірки.
4. Якщо GitHub суперечить HANDOFF — GitHub має пріоритет; спочатку виконати reconciliation.
5. Визначити одну наступну безпечну дію.

Цього достатньо, щоб **відновити стан**. Не треба одразу перечитувати весь WORKLOG або Issue #61.

### Перед внесенням змін

Перед записом у код, документацію, workflow, release або інші проєктні матеріали додатково:

1. Прочитати [приватний Taxo-profile](https://github.com/RomanZavadaM/dev-strategy/blob/profile/taxo/TAXO_PROFILE.md) у гілці `profile/taxo`; [архів журналу Taxo](https://github.com/RomanZavadaM/dev-strategy/blob/profile/taxo/taxo-history/2026-11-10-worklog-snapshot/WORKLOG.md) збережено там само.
2. Прочитати `PROJECT_RULES.md`.
3. Прочитати `PROJECT_STATE.md`.
4. За потреби відкрити `WORKLOG.md` та Issue #61 для деталей і доказів.
5. Для release/build/security/dependency змін виконати повний відповідний preflight.

Так розділяються **швидке recovery** і **повна перевірка перед зміною**.

## Джерела істини та їхня роль

### `PROJECT_RULES.md`
Постійні правила:
- версіювання і незворотність виданих revision;
- plan/fact і правила Бланків;
- роль водія та збереження історії;
- дані користувача;
- licensing/copyright;
- git/release workflow;
- значення команди власника «злити у main».

### `PROJECT_STATE.md`
Тільки підтверджений інтегрований стан `main`:
- stable і rollback checkpoint;
- останній прийнятий candidate;
- що реально вже merged;
- наступна дозволена ревізія.

Не використовувати цей файл як журнал незлитої роботи.

### `HANDOFF_CURRENT.md`
Головний файл швидкого відновлення після обриву:
- підтверджена база;
- що завершено;
- що не завершено;
- одна наступна дія;
- recovery-порядок.

Він має бути коротким і замінюватися після критичних змін, а не рости як журнал.

### `WORKLOG.md`
Хронологічний технічний журнал. Використовується для деталей і доказів, але не як перша сторінка recovery.

### GitHub Issue #61 — live development ledger
Append-only хронологія:
- старт slice;
- branch/PR;
- важливі зміни;
- analyze/test;
- CI success/failure;
- blocker;
- merge;
- release;
- наступна точка.

Issue #61 зберігає довгу історію. Поточний recovery-знімок — `HANDOFF_CURRENT.md`; `WORKLOG.md` лишається детальним технічним журналом.

### `VERSION.txt` + `main.APP_VERSION`
Машинна ідентичність активної збірки. Перед candidate/release вони повинні збігатися. Назва START archive формується з цієї версії через `release_naming.py`.

### `docs/releases/RELEASE_INDEX.md`
Індекс опублікованих release/checkpoint. Не використовувати замість `HANDOFF_CURRENT.md` для визначення поточної незавершеної роботи.

## Команда власника «злити у main»

У Taxo фраза **«злити у `main` / зливай у `main`»** не означає лише натиснути Merge.

Вона означає **повний релізний checkpoint**:
- завершити й перевірити поточну ревізію;
- інтегрувати PR у `main`;
- синхронізувати документацію;
- створити новий immutable tag/release;
- опублікувати START/source;
- зібрати й опублікувати Windows та macOS пакети для підтримуваних архітектур, якщо власник не вказав інше;
- опублікувати checksums/legal notices;
- записати результат у `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61.

Якщо потрібен тільки merge без повного релізного checkpoint, це має бути сформульовано окремо як **«інтегрувати PR у main»**.

## Правило завершення slice

Slice не є `DONE`, доки:

1. код/документація завершені;
2. обов'язкові regression/CI перевірки пройдені;
3. тестовий START archive сформований і перевірений, якщо це кодова ревізія;
4. PR merged у `main`;
5. потрібний tag/release опублікований;
6. `PROJECT_STATE.md` оновлений, якщо змінився підтверджений стан;
7. `HANDOFF_CURRENT.md` одразу показує нову підтверджену базу та рівно одну наступну дію;
8. `WORKLOG.md` і, за потреби, Issue #61 містять детальний результат.

## Новий чат / відновлення після обриву

Не відтворювати стан з пам'яті чату. Порядок recovery: `START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub. Якщо чат завис або обірвався, нова сесія виконує reconciliation, а не переказ старої розмови.

Мінімальна фраза:

> **Продовжуємо Taxo. Відкрий у GitHub `START_HERE.md` і продовжуй строго за ним.**

Репозиторій: `RomanZavadaM/Taxo`.
