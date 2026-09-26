# WORKLOG — Taxo

**Оновлено:** 26.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest published full checkpoint:** `v10.4-r1` → `4970ee3497c9340c1c5f414d7a193071092ce70c`  
**Main before active slice:** `95d29578525a017c18457591f1610992fb5d4265`  
**Active revision:** `10.4-r2`  
**Active branch:** `work/v10.4-r2-ui-docs-waybill`  
**Verified code commit:** `59e7a34f3f3eaf573615c8523a315ba69316235c`  
**Local regression:** **300 tests / OK**  
**UI audit source:** `docs/maintenance/AUDIT_UI_10_4_R1.md`  
**Remediation record:** `docs/maintenance/UI_REMEDIATION_10_4_R2.md`  
**Live ledger:** Issue #61.

## DOING — Taxo 10.4-r2

- [x] Виправлено перекриття кнопки «Зберегти» у формі точки маршруту.
- [x] Покращено адаптивність secondary windows і document viewer.
- [x] Додано/вирівняно горизонтальну та вертикальну прокрутку у широких таблицях і сторінках персоналу.
- [x] Перегруповано переповнені toolbars; зменшено ризики обрізання на 900–1024 px та DPI scaling.
- [x] Прибрано частину критичних Unicode glyphs, проблемних для Windows 7.
- [x] У реєстр документів ТЗ додано необов’язковий тип **«ДЦВ страхування»**.
- [x] Скасовано автоматичне архівування попереднього документа того самого типу.
- [x] Додано явну опцію **«Вивести попередній документ в архів»**; кілька документів одного типу можуть співіснувати.
- [x] У шляховому листі збільшено приблизно на 20% шрифт внесених при виписці даних.
- [x] Верхній лівий реквізитний блок шляхового листа оформлено як кутовий штамп підприємства з наявних реквізитів без вигаданих даних.
- [x] Оновлено керівництва, system overview, release notes та UI remediation report.
- [x] Regression suite: 300 tests / OK.
- [ ] Опублікувати immutable `v10.4-r2` з START, Windows modern, Windows 7 та macOS ARM64/Intel пакетами.
- [ ] Відкрити PR, пройти PR gates і злити в `main`.
- [ ] Після merge синхронізувати `PROJECT_STATE.md`, `WORKLOG.md`, release index та Issue #61.

## NEXT

Додати one-shot publisher для exact candidate head, перевірити повний multi-platform publish, потім PR → gates → merge у `main`.

## BLOCKED

Немає.
