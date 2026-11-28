# HANDOFF_CURRENT — Taxo

**28.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r6.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r6), exact issued source `f4950ddb7efcada08f8fe73a5bc9470776163462`, 8 canonical assets, prerelease=true.
- Current main after release trigger: `64d664b67f84ebfb5676d45b79c37bd155191687`.

## 10.25-r6 — завершено

r6 — виправлення за ручним owner acceptance r5, без зміни Stable:

1. «Основа програми» реально підключена до перевіреної `TemplateLibrary` для категорій «Інструктажі» / «Навчальні програми».
2. Придатні власні копії `CompanyTemplates` теж доступні як основа; накази/акти не підмішуються.
3. Програми згруповано у зрозумілі лінії: планові / річний цикл; початкові / вступні; цільові / перед роботою; позапланові / за подією.
4. Для повторних БДР та ОП додано редаговані робочі теми I–IV кварталу. Вони не встановлюють законодавчу періодичність автоматично.
5. «За подією…» має окремий допис конкретного випадку / проблеми / питань до базової програми.
6. DOCX має блок «ЗАТВЕРДЖЕНО», approved_by з exact program revision, місце для підпису/дати, точну редакцію програми та окремий блок події.
7. Prepared як і раніше не означає conducted або paper-signed.
8. Старий date-sensitive r2 test зафіксовано на його історичній контрольній даті; реальна overdue-логіка не послаблена.
9. Реальна база власника не відкривалась.

## Приймання r6

- Prep exact SHA `639329d8aff54020b2b1bf09be709edd13beeeaa`: START #46126867841; Windows #46126867911; Win7 #46126867844; macOS #46126867862 — SUCCESS; Defender/integrity PASS.
- Candidate exact SHA `cc71527e48be1463780be0b4aab8f0af8e38843c`: START #46127530499 — **1743 tests PASS**; Windows #46127530498; Win7 #46127530508; macOS #46127530503 — SUCCESS.
- Exact issued source `f4950ddb7efcada08f8fe73a5bc9470776163462`: START #46127933006; Windows #46127933023; Win7 #46127933027; macOS #46127932975 — SUCCESS; Defender/integrity PASS.
- Release trigger #679 merged `64d664b67f84ebfb5676d45b79c37bd155191687`.
- Publisher #46128959017 — SUCCESS.
- Release `v10.25-r6`: 8 canonical assets, prerelease=true, draft=false, exact target `f4950ddb7efcada08f8fe73a5bc9470776163462`.
- Stable/Latest лишається `v10.24-r9`.

## Що далі

**Issue #237 НЕ закривати до повторного ручного owner UI acceptance r6.**

Під час приймання насамперед перевірити:
- «Програми / план / друк…» → «Основа програми»;
- реальний шаблон із Бібліотеки → «Підставити» → текст нової редакції;
- власну копію шаблону;
- щоб накази/акти не з'являлися як основи інструктажу;
- лінії програм і квартальні теми I–IV;
- створення/редагування нової immutable редакції;
- «За подією…» → базова програма + конкретний допис випадку;
- prepared DOCX: «ЗАТВЕРДЖЕНО», затверджувач, підпис/дата, exact revision, конкретний випадок;
- попередні r5 дії: люди, квартал/БДР/ОП, prepared/conducted, history, X/Закрити/Скасувати, мале вікно, reopen.

Лише після owner acceptance вирішувати, чи закривати #237 і переходити до наступного великого блоку — **єдиного сховища документів**.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub`.
