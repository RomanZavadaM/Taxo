# GitHub publication summary — Taxo 9.1 candidate r9.4

**Дата:** 19.09.2026  
**Repository:** `RomanZavadaM/Taxo`  
**Stable:** Taxo 9.0.1  
**Candidate:** Taxo 9.1 candidate r9.4  
**Branch:** `work/v9.1-monthly-dispatch-waybill-ui`  
**PR:** #29 — open, not merged

## Що опубліковано

GitHub Releases перевірені фактично. На момент цієї фіксації немає draft-релізів.

Актуальна лінія:
- stable `v9.0`;
- stable hotfix `v9.0.1`;
- candidate `v9.1-r5`;
- candidate `v9.1-r6`;
- immutable source/START candidates `v9.1-r7`, `v9.1-r8`, `v9.1-r9`, `v9.1-r9.1`, `v9.1-r9.2`, `v9.1-r9.3`, `v9.1-r9.4`.

Повний індекс: [RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).

## Контрольна точка r9.4

Release:
- tag: `v9.1-r9.4`;
- target: `3da975ff3dc30740aeaf300d9e3471415075dbe0`;
- package: `Taxo_v9_1_candidate_r9_4_START.zip`;
- checksum: `SHA256SUMS_v9_1_candidate_r9_4.txt`;
- GitHub pre-release: published.

Post-release handoff checkpoint до цього оформлення:
- `c4461e779f07639042f1348d7f61e14f6dc99df3`;
- від release target відрізнявся лише `PROJECT_STATE.md` та новим handoff-документом.

Подальші commits цього оформлення є документаційними та **не змінюють код release r9.4**. Tag `v9.1-r9.4` не пересувати.

## CI

На release target `3da975f...`:
- Windows — 97 regression tests, success;
- macOS Intel x86_64 — 97 regression tests, success;
- macOS ARM64 — 97 regression tests, success;
- START/source package — success;
- immutable source release publisher — success.

На post-release documentation head Windows/macOS/START checks також проходили успішно.

У GitHub Actions є службове попередження про Node.js 20 для `actions/checkout@v4` / `actions/setup-python@v5`. Воно не є дефектом Taxo r9.4 і не блокує operational gate; оновлення action versions слід виконувати окремою технічною зміною після gate.

## Захист GitHub

Перевірено rulesets:
- **Protect main** — active; заборонені deletion/non-fast-forward, merge через PR, required status check `build-windows`;
- **Protect releases** — active для `refs/tags/v*`; заборонені deletion, non-fast-forward та update.

Окремо publisher r9.4 відмовляється перезаписувати release, якщо `v9.1-r9.4` вже існує.

## Що входить у r9.4

- канонічні exact intervals;
- union перекриттів без подвійного рахунку;
- коректний перехід через 00:00;
- duration-only без вигаданого 08:00–16:00;
- блокування нових перекриттів без переписування старої історії;
- єдиний стан дня у Табелі / Графіку водіїв;
- Персонал, режими робочого часу та внутрішнє сумісництво;
- П-5 PDF/XLSX з явним рішенням щодо підстановки плану;
- архів підтверджень діяльності з фільтрами;
- місячний контроль водія;
- центр «Аудит графіків…»;
- чітке розділення технічного аудиту і нормативного Контролю №340;
- backup/restore safety, перевірений технічним аудитом.

## Що ще НЕ завершено

Автоматична частина пройдена, але **manual operational gate на реальній Windows-базі не завершено**.

Тому:
- stable залишається 9.0.1;
- PR #29 не merge;
- main не змінювати;
- stable 9.1 не оголошувати;
- наступний великий функціональний етап не починати до завершення gate.

Чекліст ручної перевірки: [AUDIT_v9_1_r9_4.md](AUDIT_v9_1_r9_4.md).

## Release policy

- дрібні candidate: START/source;
- executable Windows/macOS — на визначених контрольних версіях;
- кожна нова **кодова** контрольна точка — новий immutable tag/release;
- документаційні commits після release не є підставою пересувати попередній tag;
- робочі БД, скани, кеші й персональні дані не публікуються.

## Наступна дія

Продовжити manual operational gate з першого неперевіреного пункту. Якщо виявлено дефект:
1. виправити у робочій гілці;
2. додати regression test;
3. прогнати CI;
4. оновити VERSION / PROJECT_STATE / audit / release notes;
5. створити новий candidate tag/release;
6. не змінювати `v9.1-r9.4`.

Якщо весь gate пройдено — окремо прийняти рішення про stable Taxo 9.1 і merge PR #29.
