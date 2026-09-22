# START_HERE — Taxo / Driver Worktime

> **Перша точка входу для будь-якої нової робочої сесії, нового чату або відновлення після обриву.**

Цей файл існує, щоб робота над Taxo не залежала від пам'яті конкретного чату.

## Обов'язковий startup protocol

Перед будь-якою зміною коду, документації, релізу або плану:

1. Прочитати цей файл.
2. Прочитати `PROJECT_RULES.md` — постійні правила Taxo.
3. Прочитати `PROJECT_STATE.md` — підтверджений інтегрований стан `main`, stable/candidate checkpoints і наступна ревізія.
4. Прочитати `WORKLOG.md` — активний slice, branch/PR, SHA, verify, `DOING/NEXT/BLOCKED`.
5. Перевірити фактичний GitHub: актуальний `main` SHA, відкриті PR, head SHA активного PR, останні GitHub Actions, tags/releases/assets.
6. Прочитати останні записи GitHub Issue **#61 — Taxo — live development ledger**.
7. Якщо GitHub суперечить тексту у файлах — GitHub має пріоритет; одразу синхронізувати `WORKLOG.md` і, якщо треба, `PROJECT_STATE.md`.
8. Продовжити з першого незавершеного пункту `DOING` / `NEXT`. Не повторювати merged або вже опубліковану роботу.

## Джерела істини

- `PROJECT_RULES.md` — постійні правила: версіювання, plan/fact, бланки, роль водія, дані, licensing, packaging.
- `PROJECT_STATE.md` — тільки підтверджений інтегрований стан `main`.
- `WORKLOG.md` — оперативний стан активної роботи.
- GitHub Issue #61 — append-only live development ledger.
- `VERSION.txt` — версія і тип release для packaging.

## Правило завершення slice

Slice не є `DONE`, доки код/документація завершені, потрібні перевірки пройдені, PR merged, потрібний release опублікований, `PROJECT_STATE.md` і `WORKLOG.md` синхронізовані, а в Issue #61 записані завершення й наступна точка.

## Новий чат

Мінімальна фраза:

> **Продовжуємо Taxo. Відкрий у GitHub `START_HERE.md` і продовжуй строго за ним.**

Репозиторій: `RomanZavadaM/Taxo`.
