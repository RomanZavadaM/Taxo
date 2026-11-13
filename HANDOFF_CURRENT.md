# HANDOFF_CURRENT — Taxo

**13.11.2026 — Stable/Latest: v10.18-r3. Остання видана тестова кодова ревізія: 10.18-r7, CI PASS, draft/unmerged/unreleased. Наступна нова ревізія — 10.18-r8.**

## Відновлення після ручного тестування r6 і перевірки r7 (13.11)

- Власник запустив Windows Portable **10.18-r6** і надіслав скриншот «Експлуатація → Документи»: бібліотеку шаблонів не видно. Причина — r6 додав нову функцію тільки в меню `Шаблони`, яке на Windows приховане/неочевидне. Це UX-дефект доступності, а не доказ несправності читача чи змісту приватної бібліотеки.
- **Новий тестовий r7:** [draft PR #400](https://github.com/RomanZavadaM/Taxo/pull/400), branch `work/v10.18-r7-template-library-visible-entry`, exact head `aed893047ef8853d2c8c9ef96e7d58603ad66c55` (від exact r6 head `ad6f60cf2b95cf79597447e42164c5efd91c0155`). Створено окремий `template_library_operations_entry.py`, додано кнопку «Бібліотека шаблонів…» у чинний блок «Накази та розпорядження» праворуч від «Каталог типів наказів», через чинний `feature_layers.py`. `main.py` — тільки номер ревізії, жодного нового великого коду чи змін SQLite.
- **Усі exact-head r7 CI успішні:** [START/source 43455393733](https://github.com/RomanZavadaM/Taxo/actions/runs/43455393733), **1255/1255** тестів, artifact `14052174811`; [Windows 43455410179](https://github.com/RomanZavadaM/Taxo/actions/runs/43455410179), artifact `14054111027`; [Win7 43455410214](https://github.com/RomanZavadaM/Taxo/actions/runs/43455410214), artifact `14052518546`; [macOS Intel/ARM 43455410124](https://github.com/RomanZavadaM/Taxo/actions/runs/43455410124), artifacts `14052538346`/`14054175651`. Прямий Windows-артефакт для власника: https://github.com/RomanZavadaM/Taxo/actions/runs/43455410179/artifacts/14054111027.
- **r7 ще не merged/tagged/published GitHub Pre-release і НЕ Stable.** Чекає ручного Windows приймання: видима кнопка → приватна бібліотека 28 шаблонів → пошук/категорії/сортування → X/«Закрити» та повторне відкриття. Не плутати успіх CI із ручним UX-тестом.
- Власницький приватний каталог шаблонів у цьому репозиторії **не з'явився** і в публічні release assets не включався. r5/r6 GitHub Pre-release checkpoint ще потребує звірки та завершення; не переписувати видані ревізії. Stable/Latest v10.18-r3 не змінювати без окремої команди.
- Подробиці й архів дій — Issue #61.

## Підтверджена база

- **Стабільна версія:** [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3), source/tag `65bc80ecae85793cb7c2c14edd4d3eabaa2b4470`, 8 файлів, ручне приймання 25/25. **Rollback:** v10.17-r10.
- `main` до цього docs-only handoff — `c4b040fef695cd489805bad407fe0e5f9ad7912c`. Код r4–r6 у main **не злитий**; Stable не змінювали.
- **r4:** [draft PR #393](https://github.com/RomanZavadaM/Taxo/pull/393), exact head `eb762664dbd85650d3b8e5a6a59a7f3dfb4ea551`. Перевірене сортування тахографа.
- **r5:** [draft PR #396](https://github.com/RomanZavadaM/Taxo/pull/396), exact head `7ee89f3f0dcb731c4b2fd416b6ddb630e3ebe7d2`, модуль `template_library_reader.py`. CI 1242/1242 і Windows/Win7/macOS PASS, артефакти є, але **GitHub Pre-release v10.18-r5 досі НЕ опублікований** (404 на перевірку 13.11). r5 не перевикористовувати.
- **r6:** [draft PR #398](https://github.com/RomanZavadaM/Taxo/pull/398), branch `work/v10.18-r6-template-library-browser`, **exact head `ad6f60cf2b95cf79597447e42164c5efd91c0155`** від exact r5 head. Нові окремі модулі `template_library_service.py`, `template_library_ui.py`, `template_library_feature.py` через `feature_layers.py`. Меню «Шаблони → Бібліотека шаблонів…» відкриває дочірній read-only браузер із пошуком, категоріями, сортуванням, оновленням, X/«Закрити»; бере актуальний workspace від `ApplicationServices`. `main.py` містить тільки зміну номера версії.
- **Exact-head r6 CI PASS усі:** [START/source](https://github.com/RomanZavadaM/Taxo/actions/runs/43450233818) 1250/1250, artifact `14049094156`; [Windows](https://github.com/RomanZavadaM/Taxo/actions/runs/43450245205) artifact `14051860059`; [Windows 7](https://github.com/RomanZavadaM/Taxo/actions/runs/43450245408) artifact `14051410332`; [macOS Intel+ARM64](https://github.com/RomanZavadaM/Taxo/actions/runs/43450245202) artifacts `14050156557` / `14050196221`.
- **r6 не tagged, не GitHub release, не merged і не Stable.** Ручний Windows/UI/DPI тест із власником поки pending; CI не є доказом ручного приймання.

## Бібліотека документів: приватність та межі

- Джерельна бібліотека знеособлених документів існує **окремо і приватно**. Власник розпакував її під `TemplateLibrary` в обраному workspace. Тестовий пакет містить 28 сумісних шаблонів і manifest; не є публічним активом Taxo й не вбудований у exe/portable/source archive. Відсутність або некоректність бібліотеки не повинна блокувати Taxo.
- [Draft architecture PR #395](https://github.com/RomanZavadaM/Taxo/pull/395): формат бібліотеки, перевірка маніфесту, журнал ризиків, документаційна модель архіву/інструктажів. Бібліотека лише джерело форм, не другий архів готових наказів.
- r6 — лише **перегляд**. Немає редактора, генерації наказів, завантаження ZIP програмою, зміни налаштувань зовнішнього шляху, роботи зі сканами/КЕП чи міграції БД. Приватні тексти, персональні шляхи і приватні URL не включено в публічний Taxo.
- Слід посилити повну schema validation та пам'яттєву ефективність читача до майбутнього імпорту/генерації; `AVAILABLE` не означає юридичного затвердження.

## Наступна одна дія

**Отримати ручне Windows-приймання тестового r7 від власника:** завантажити [r7 Windows x64 artifact](https://github.com/RomanZavadaM/Taxo/actions/runs/43455410179/artifacts/14054111027), відкрити «Експлуатація → Документи», натиснути нову видиму кнопку «Бібліотека шаблонів…» праворуч від «Каталог типів наказів», переконатися у відображенні 28 шаблонів приватного каталогу, перевірити сортування/пошук/X/повторне відкриття. Не вимагати від власника повторного розпакування бібліотеки без доказу проблеми. **Після ручного тесту** завершити релізну чергу r5/r6/r7 через штатний GitHub workflow без перевикористання тегів; Stable r3 незмінна. Новий код після виданого r7 — r8.

## Відновлення

`START_HERE.md` → цей файл → GitHub main/PR #393/#395/#396/#398 та exact CI → приватний Taxo-профіль dev-strategy → `PROJECT_RULES.md`, `PROJECT_STATE.md`. Розгорнуті технічні докази й історія — Issue #61. Якщо фактичний GitHub змінився — спочатку reconciliation.
