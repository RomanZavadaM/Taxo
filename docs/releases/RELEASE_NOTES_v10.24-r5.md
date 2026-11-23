# Taxo 10.24-r5 — справи та ланцюжки кореспонденції

**Test-кандидат. Stable/Latest залишається 10.24-r3; поточний опублікований Test до видачі цього кандидата — 10.24-r4.**

10.24-r5 продовжує лінію кореспонденції після r1 registry, r2 controlled attachments, r3 journal/card UI та r4 explicit sent/received + deadlines. Ця ревізія додає **логічні справи/теми та ланцюжки листування** без копіювання документів, зміни реєстраційних номерів або автоматичного e-mail.

## Що додано

- окремий case-store `Data/CorrespondenceCases/cases.json`, не змішаний зі strict registry store;
- stable case ID формату `cc-...`;
- назва справи, примітки, explicit membership листів, active/archive state та timestamps;
- один зареєстрований лист у цьому bounded slice може належати максимум одній справі;
- членство справи зберігає лише ID листів — файли, scans, attachment bytes і document_ref не дублюються;
- створення, перейменування, архівування/відновлення справ;
- архівована справа read-only до явного відновлення;
- атомарне переміщення листа між справами або у «Без справи»;
- existing `response_to_ids` і `related_ids` використовуються як граф відомого ланцюжка;
- **«Додати пов'язані»** спочатку показує знайдені листи й тільки після явного підтвердження атомарно додає їх до справи;
- fail-closed validation для duplicate case IDs, duplicate names, missing correspondence та подвійного membership;
- повний workspace backup/restore зберігає справи й членство;
- третя вкладка **«Справи»** у центрі кореспонденції;
- case browser: список справ + ланцюжок листів із №, датою, напрямом, кореспондентом, темою й станом;
- у картці листа видно поточну справу; дія **«Справа…»** прив'язує/переміщує лист;
- зі справи можна відкрити лист назад у правильний журнал або вилучити його без видалення самого листа;
- case editor захищає незбережені зміни через X/«Скасувати»;
- case actions винесені у постійну нижню область і перевіряються на minimum viewport 760×520;
- START package guard тепер вимагає `correspondence_cases.py`.

## Що r5 навмисно не робить

- справа не є новим архівом файлів і не копіює attachment bytes;
- справа не змінює registration number, sent/received, status або due date листа;
- explicit thread candidates не стають членами справи без підтвердження користувача;
- немає automatic e-mail, mailbox sync, external integrations, OCR, AI APPLY або physical attachment purge.

## Перевірки prep

Prep PR #625 після двох знайдених regression-помилок пройшов фінальний цикл:
- START #45169334073 — SUCCESS;
- Windows #45169334161 — SUCCESS;
- Windows 7 #45169334164 — SUCCESS;
- macOS Intel/ARM #45169334069 — SUCCESS;
- Windows/Win7 Defender та post-scan integrity — SUCCESS.

Перший START захистив strict correspondence registry: `cases.json` не дозволено класти у `Data/Correspondence`, тому case-store винесено в окремий `Data/CorrespondenceCases` замість послаблення r1 guard. Другий START зловив залишений старий test path та неоднозначну кнопку «Оновити»; шлях виправлено, а case refresh отримав окрему назву **«Оновити справи»** без послаблення reachability test.
