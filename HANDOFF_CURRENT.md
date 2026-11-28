# HANDOFF_CURRENT — Taxo

**28.11.2026 — Stable/Latest = 10.24-r9; Current Test = 10.25-r6.**

- **Stable/Latest:** [v10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), exact source `e3770aa72b0744eee192979a2e569651bac4f257`, 8 canonical assets, prerelease=false, GitHub Latest.
- **Current Test:** [v10.25-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r6), exact issued source `f4950ddb7efcada08f8fe73a5bc9470776163462`, 8 canonical assets, prerelease=true.
- Current main after release-maintenance merge: `376569e8fc23b77e927892d346c35b6d6480ed87`.

## 10.25-r6 — завершено

r6 виникла з ручного приймання v10.25-r5 і виправляє саме практичний шлях підготовки інструктажу:

1. «Основа програми» реально читає придатні шаблони з `TemplateLibrary` та власні копії `CompanyTemplates`, а не лише вбудовані тексти Taxo.
2. Накази/акти та інші невідповідні власні шаблони не підмішуються в основу інструктажу.
3. Програми показуються у зрозумілих лініях: планові / річний цикл; початкові / вступні; цільові / перед роботою; позапланові / за подією.
4. Для повторних БДР та ОП є редаговані квартальні робочі теми I–IV; вони не встановлюють законодавчу періодичність автоматично.
5. «За подією…» окремо має підставу і окремо конкретний випадок / проблему / питання до розгляду.
6. DOCX має блок «ЗАТВЕРДЖЕНО», approved_by, місце для підпису/дати, exact program revision і окремий блок події.
7. Prepared / conducted / paper-first правила не змінені: підготовлений DOCX не означає проведення чи підписання.

Реальна база власника не відкривалась і не змінювалась.

## Перевірка та публікація

- Prep exact SHA `639329d8aff54020b2b1bf09be709edd13beeeaa`: START #46126867841, Windows #46126867911, Win7 #46126867844, macOS #46126867862 — SUCCESS; Defender/integrity PASS.
- Candidate #678 exact product source: `f4950ddb7efcada08f8fe73a5bc9470776163462`.
- Candidate CI: START #46127530499, Windows #46127530498, Win7 #46127530508, macOS #46127530503 — SUCCESS.
- Exact-source CI: START #46127933006, Windows #46127933023, Win7 #46127933027, macOS #46127932975 — SUCCESS; Defender/integrity PASS.
- Release trigger #679 merged `64d664b67f84ebfb5676d45b79c37bd155191687`; publisher #46128959017 — SUCCESS.
- [v10.25-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r6): 8 canonical assets, prerelease=true, draft=false, exact target `f4950ddb7efcada08f8fe73a5bc9470776163462`.
- Stable/Latest лишається `v10.24-r9`.
- PR #680 був дубльованим recovery-trigger після обриву чату; другий release не створювався.

## Що далі

**Issue #237 НЕ закривати.** Потрібне повторне ручне owner acceptance саме v10.25-r6:

- взяти шаблон із бібліотеки → підставити основу → перевірити текст;
- перевірити власну копію шаблону;
- створити/відкрити планову квартальну тему;
- перевірити вступний/первинний та позаплановий каркас;
- у «За подією…» заповнити підставу + конкретний випадок;
- підготувати DOCX і перевірити «ЗАТВЕРДЖЕНО», редакцію, список людей та вигляд друку;
- переконатися, що DOCX не ставить «Проведено» автоматично;
- small-window / X / Закрити / Скасувати / повторне відкриття.

**Одна наступна дія:** ручне owner UI acceptance v10.25-r6. Після нього вирішити, чи закривати #237 і переходити до наступного великого блоку — єдиного сховища документів.

Recovery: `START_HERE.md → HANDOFF_CURRENT.md → PROJECT_STATE.md → private profile/taxo → live GitHub`.
