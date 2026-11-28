# HANDOFF_CURRENT — Taxo

**28.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r7.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r7), exact issued source `76f2f7c8868154374457dc7c094a2c25ed2547d2`, 8 canonical assets, prerelease=true.
- Release-trigger main: `d5ee59f84fbc3d1d28e835978ca3eff87ee9555a` before this recovery checkpoint.

## 10.25-r7 — завершено

r7 виправляє проблеми, знайдені власником під час ручного приймання r6:

1. «Створити власну копію» більше не завершується помилкою, якщо копія цієї редакції вже існує: Taxo знаходить її та відкриває.
2. У Бібліотеці є прямий шлях «Заповнити поля / підготувати»; вкладка «Поля для заповнення» пояснює, де виконувати заповнення.
3. Технічні типи `order` / `instruction_program` / `notice` показуються людськими українськими назвами.
4. Старі звичні дії «Створити власну копію» і «Підготувати чернетку» збережені.
5. Для нової програми «Затвердив» пропонується з `signer_position + signer_name` картки підприємства; користувач може змінити значення, старі immutable редакції не переписуються.
6. Prepared DOCX явно A4; у листі ознайомлення друкуються ПІБ + посада, а внутрішній/табельний номер не виставляється на папір.
7. Новий планувальний шлях показує людську редакцію програми `rN`, при цьому exact ID лишається у структурованих даних/legacy-сумісності.
8. Prepared як і раніше не означає conducted або paper-signed. Реальна база власника автоматичними тестами не відкривалась.

## Перевірка і публікація r7

- Candidate exact head `8498b91f794a402d13ef2b6c2f855e5694003730`: START #46149046990 — **1749 tests PASS**; Windows #46149046880; Win7 #46149046913; macOS #46149046865 — SUCCESS; Defender/integrity PASS.
- Exact issued source `76f2f7c8868154374457dc7c094a2c25ed2547d2`: START #46149545768 — **1749 tests PASS**; Windows #46149545770; Win7 #46149545728; macOS #46149545741 — SUCCESS; Defender/integrity PASS.
- Product PR #683 merged as `76f2f7c8868154374457dc7c094a2c25ed2547d2`.
- Release trigger #684 merged as `d5ee59f84fbc3d1d28e835978ca3eff87ee9555a`.
- Publisher #46150624080 — SUCCESS.
- Release `v10.25-r7`: 8 canonical assets, prerelease=true, draft=false, exact target `76f2f7c8868154374457dc7c094a2c25ed2547d2`.
- Stable/Latest лишається `v10.24-r9`.

## Що далі

**Issue #237 НЕ закривати до ручного owner UI acceptance r7.**

Під час приймання насамперед перевірити:
- Бібліотека → «Створити власну копію» для шаблону, копія якого вже існує: має відкритися існуюча копія без червоної помилки;
- «Заповнити поля / підготувати» → зрозуміла форма заповнення;
- вкладка «Поля для заповнення» → зрозуміле пояснення наступної дії;
- людські назви типів у Бібліотеці;
- нова програма → автоматична пропозиція затверджувача з картки підприємства, з можливістю редагування;
- prepared DOCX → A4, «ЗАТВЕРДЖЕНО», людська редакція `rN`, ПІБ + посада у листі підписів, без внутрішнього номера;
- попередні r6/r5 сценарії: бібліотечна основа, квартали БДР/ОП, люди, prepared/conducted, event addendum, history, reopen, X/Закрити/Скасувати, мале вікно.

**Єдине сховище документів поки НЕ починати.** Лише після owner acceptance вирішувати, чи закривати #237 і переходити до наступного великого блоку.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub`.
