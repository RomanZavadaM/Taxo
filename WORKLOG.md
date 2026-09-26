# WORKLOG — Taxo

**Оновлено:** 27.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable, не пересувався  
**Latest published full checkpoint:** `v10.4-r2` → `ee6687c59d7dc1a8a38de4b7858669fddc3f647c`  
**Checkpoint PR:** #74 — merged  
**Main merge:** `271d43c0912e24c95014ac2a92ba2fc1695f4a11`  
**Full publisher:** run `36275440403` — success  
**Final PR gates:** Windows `36275442986` — success; macOS ARM64/Intel `36275442988` — success  
**Regression:** **300 tests / OK**; Win7 Python 3.8 regression — **300 tests / OK**  
**Windows 7 PE compatibility gate:** success  
**Live ledger:** Issue #61  
**Next code revision:** тільки `10.4-r3`.

## DONE — Taxo 10.4-r2

- [x] Виправлено перекриття кнопки «Зберегти» у формі точки маршруту.
- [x] Покращено адаптивність secondary windows і document viewer.
- [x] Додано/вирівняно горизонтальну та вертикальну прокрутку у широких таблицях і сторінках персоналу.
- [x] Перегруповано переповнені toolbars; зменшено ризики обрізання на вузьких екранах і при DPI scaling.
- [x] Прибрано критичні Unicode glyphs, проблемні для Windows 7.
- [x] У реєстр документів ТЗ додано необов’язковий тип **«ДЦВ страхування»**.
- [x] Скасовано автоматичне архівування попереднього документа того самого типу.
- [x] Додано явну опцію архівування; кілька активних документів одного типу можуть співіснувати.
- [x] У шляховому листі збільшено приблизно на 20% шрифт внесених даних.
- [x] Верхній лівий блок шляхового листа оформлено як кутовий штамп підприємства з наявних реквізитів.
- [x] Оновлено USER_MANUAL, QUICK_START, ADMIN_GUIDE, REPORTS_GUIDE, SYSTEM_OVERVIEW, release notes та UI remediation report.
- [x] Full publisher сформував modern Windows Setup/Portable, Windows 7 SP1 Setup/Portable, macOS ARM64/Intel Portable, START та SHA-256 manifests.
- [x] Виправлено publisher-gates: macOS bundle filename check і Win7 PE checker винесено в `scripts/check_win7_pe.py`.
- [x] Win7 PE scan реально виконано й пройдено.
- [x] Опубліковано immutable candidate checkpoint `v10.4-r2`.
- [x] PR #74 пройшов фінальні Windows/macOS gates та merged у `main`.

## NEXT

Новий функціональний код не додавати під номером r2. Наступний завершений крок розробки має бути **Taxo 10.4-r3** в окремій work-гілці з новим test archive/checkpoint.

## BLOCKED

Немає.
