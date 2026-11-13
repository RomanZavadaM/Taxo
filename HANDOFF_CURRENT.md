# HANDOFF_CURRENT — Taxo

**13.11.2026 — код інтегрований у main на 10.18-r8. GitHub Stable/Latest досі v10.18-r3. Реліз r8 НЕ опубліковано: SECURITY HOLD через попередження Firefox про можливе шкідливе ПЗ. Наступна нова кодова ревізія — 10.18-r9.**

## Перевірений стан GitHub

- **Код main** після інтеграції: `b1153adde923c73cba9a71d152ee749e351b2588`. `VERSION.txt = Version: 10.18-r8`. Злиття за прямою командою власника, [PR #404](https://github.com/RomanZavadaM/Taxo/pull/404) MERGED; первинний [PR #402](https://github.com/RomanZavadaM/Taxo/pull/402) теж GitHub позначив MERGED. Це інтеграція коду, **не реліз виконуваних файлів**.
- **Стабільний реліз:** [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3), `prerelease=false`, 8 assets. Його НЕ змінено. Rollback попередній `v10.17-r10`.
- **Кандидат r8, виданий раніше для ручного тестування:** source head `eb1d74872ce785c4bbaf4607333f78648ffa8a3a`, код із r7 `aed893047ef8853d2c8c9ef96e7d58603ad66c55`. Для інтеграції створено окремий 2-parent merge commit `9a2334952f32469344f0927f41aa35b7c9a4d7df` (код r8 + актуальний `HANDOFF_CURRENT.md` із main); початковий source head не переписували.
- **Exact-source r8 CI SUCCESS:** [START/source 43467284684](https://github.com/RomanZavadaM/Taxo/actions/runs/43467284684) — 1263/1263; [Windows 43467336419](https://github.com/RomanZavadaM/Taxo/actions/runs/43467336419); [Win7 43467336453](https://github.com/RomanZavadaM/Taxo/actions/runs/43467336453); [macOS Intel/ARM 43467336517](https://github.com/RomanZavadaM/Taxo/actions/runs/43467336517). Усі перевірили source `eb1d74872ce785c4bbaf4607333f78648ffa8a3a`.
- **Exact-integration CI SUCCESS:** Windows [43473156192](https://github.com/RomanZavadaM/Taxo/actions/runs/43473156192), Win7 [43473156115](https://github.com/RomanZavadaM/Taxo/actions/runs/43473156115), macOS Intel/ARM [43473156367](https://github.com/RomanZavadaM/Taxo/actions/runs/43473156367), source head `9a2334952f32469344f0927f41aa35b7c9a4d7df`.
- Попередні видані тестові ревізії r4/r5/r6/r7 включені в послідовну r8-кодову гілку. Їхні GitHub Pre-release не слід називати опублікованими без окремої live-перевірки тегів. Жодна версія не може бути видана повторно під тим самим номером.

## Що працює в продукті

- Власник вручну перевірив у Windows r7: у вікні «Експлуатація → Документи» видно кнопку «Бібліотека шаблонів…», приватну бібліотеку `0.1.0` завантажено, **28 із 28 шаблонів** знайдено й показано. Це не означає перевірку вмісту/друку.
- r8 містить ізольовані `template_library_preview.py` та `template_library_preview_ui.py`: відкриття тексту шаблону через подвійне клацання/Enter/кнопку, read-only вкладки «Текст та додатки» і «Поля для заповнення», хеш/структурні перевірки. `main.py` змінювався лише в номері версії. **Ручний r8 preview власником не прийнято**, бо Firefox заблокував ZIP.
- **Знеособлені вихідні документи** зберігаються тільки в окремому приватному каталозі та локальному `<workspace>/TemplateLibrary`; жодних реальних шаблонів у публічних файлах Taxo, release assets або CI fixtures. Бібліотека — source форм, а не друге сховище готових документів. [Архітектурний PR #395](https://github.com/RomanZavadaM/Taxo/pull/395) окремо містить формат і план, не поспішати з редактором і міграцією.

## SECURITY HOLD — невирішено, обов'язково перед release

- Власник надіслав скриншот Firefox із червоним попередженням **«Цей файл містить вірус чи іншу небезпеку»** для ZIP GitHub Actions r8. Детальна панель Firefox показала лише загальне повідомлення про загрозу, **не назву детекції або антивіруса**.
- Тестова Windows збірка r8 має artifact ID `14059297915` в run `43467336419`. Для технічного аналізу цей самий архів завантажено **без запуску**. ZIP містить Windows portable та Setup і SHA256SUMS. Контрольні суми архівів збіглися з GitHub checksum. Склад ZIP без незвичних шляхо-прохідних файлів. Це **не доказ відсутності вірусу**.
- Збірка на PyInstaller 6.22.2 із `upx=True` і без підпису та без явного антивірусного gate. UPX/невідомий видавець **можуть** спричиняти евристичні помилкові спрацювання, але без незалежного сканування/детекції це **НЕ підтверджено**. Ні SHA256, ні CI успіх не встановлюють безпечність.
- **Не публікувати r8 ZIP/Setup/EXE як реліз, не змушувати користувача обходити Firefox/Defender**, не оголошувати нову Stable, поки незалежний сканер або антивірусний постачальник не визначить природу попередження. Не додавати flagged ZIP у приватний каталог шаблонів.
- Подальша технічна дія: відтворити збірку з контрольованими залежностями, перевірити бінарні файли незалежним AV/сканером, вивчити повну детекцію та походження build chain; за необхідності наступною кодовою ревізією `r9` вимкнути UPX, порівняти артефакти, додати malware gate/signing і повторити scanning. Не робити невидимі зміни вже виданої r8.
- GitHub workflow `publish-current.yml` є окремим процесом випуску через workflow_dispatch; **жодної перевіреної публікації r8 не виконано**. Не плутати CI artifact із GitHub Release.

## Наступна дія для нового чату

**Насамперед — безпека Windows-бінарника, не розширення функціоналу.** Відкрити `START_HERE.md`, цей `HANDOFF_CURRENT.md`, актуальні `main`, `VERSION.txt`, releases і Issue #61, перевірити source та artifact SHA. Провести незалежне сканування r8/перезбірку, усунути причину Firefox warning та лише тоді розглядати GitHub Pre-release. Ручний тест r8 перегляду приватних шаблонів — після безпечної збірки. Наступна нова ревізія `10.18-r9`; не reuse r8. Stable `v10.18-r3` зберегти до окремого рішення.

## Recovery

`START_HERE.md` → цей файл → `PROJECT_RULES.md` / `PROJECT_STATE.md` → GitHub main / PR #404 / PR #402 / CI / Releases → приватний Taxo-профіль dev-strategy. Докладний журнал у [Issue #61](https://github.com/RomanZavadaM/Taxo/issues/61). Після відкату — STOP→READ→VERIFY→RECONCILE→CONTINUE.
