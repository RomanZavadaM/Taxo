# TAXO — AI HANDOFF / НЕ ВТРАЧАТИ СТАН

Оновлено: 11.09.2026

## КРИТИЧНЕ ПРАВИЛО
Перед будь-якою зміною Taxo НЕ покладатися на пам'ять чату і НЕ визначати версію зі старих повідомлень.
Спочатку перевірити, у такому порядку:
1. `/Taxo/PROJECT_STATE.md` у ChatGPT Library.
2. `/Taxo/RECOVERY_INDEX.md` у ChatGPT Library.
3. Контрольні ZIP у `/Taxo/Releases/`.
4. `/Taxo/GITHUB_RECOVERY_STATUS_v8_60.md` у ChatGPT Library.
5. GitHub `RomanZavadaM/Taxo`, гілки `main` та актуальна `release-*`.
Якщо є суперечність — контрольний ZIP користувача + SHA-256 мають пріоритет над пам'яттю чату.

## Актуальна відновлена лінія
- v8.56 — остання стабільна версія на GitHub `main` перед відновленням.
- v8.57 TEST — редагування Бланків, soft-delete, відновлення, ревізії, `attestation_audit`, архівування замінених/вилучених DOCX, backup БД перед EDIT/DELETE/RESTORE.
- v8.58 TEST — окремі англійські реквізити підприємства з fallback на українські.
- v8.59 TEST — видима кнопка збереження реквізитів + автозбереження перед створенням/редагуванням Бланка.
- v8.60 TEST — окремі англійські ПІБ водія: `last_name_en`, `first_name_en`, `middle_name_en`, поелементний fallback на українські, автоматична міграція старої БД.
- НАСТУПНА версія для розробки: v8.61.

## Наступна узгоджена задача v8.61
Для Бланка підтвердження діяльності додати формування:
- DOCX (залишається),
- PDF,
- JPG page1 + page2,
- команда «Створити все».
Бажано PDF/JPG без залежності від встановленого Microsoft Word.
Не починати v8.61 від v8.56 або від помилкової проміжної збірки — тільки від перевіреної v8.60.

## Контрольні копії в ChatGPT Library
- `/Taxo/Releases/Taxo_v8_57_TEST.zip`
- `/Taxo/Releases/Taxo_v8_58_TEST.zip`
- `/Taxo/Releases/Taxo_v8_59_TEST.zip`
- `/Taxo/Releases/Taxo_v8_60_TEST.zip`
- `/Taxo/Releases/Taxo_v8_60_RECOVERED.zip`
- `/Taxo/Releases/Taxo_v8_60_source.zip`

## GitHub
Repository: `RomanZavadaM/Taxo`
- `main`: контрольна v8.56 до окремого рішення про переведення v8.60 у стабільний реліз.
- `release-v8.60`: повністю синхронізована і перевірена контрольна v8.60.
- Кореневий `main.py` у `release-v8.60` тепер byte-for-byte збігається з контрольним v8.60: SHA-256 `bb11ecc39e2f7b54fd9926d4023d72b282556efa869922b1e0b7abfc98f31a8c`, Git blob `8d19b94d7fea2d8f77ccb2e40fccbad0465bf214`.
- Синхронізаційний commit: `7edc68314a5570cab2fbcadd6d0e44c15072f1da`.
- Так само перевірені `tachograph.py`, `START.bat`, `requirements.txt`, `VERSION.txt` і `Бланк підтвердження.docx`.
- v8.61 можна починати з `release-v8.60` або з `/Taxo/Releases/Taxo_v8_60_source.zip`.
Не переводити `main` на v8.60 без явного рішення, що v8.60 прийнята як стабільна.

## Незмінні правила проєкту
- Основну БД користувача не класти в ZIP і GitHub.
- Постійні дані: `%USERPROFILE%\\Documents\\DriverWorktime\\`.
- Дати UI: ДД.ММ.РРРР.
- Офісний друк: A4; широкі місячні таблиці — A4 landscape.
- Денна клітинка місячного табеля/балансу — тільки години.
- Тахокарти — вибірковий контроль, не автоматичне переписування основного графіка.
- Бланк підтвердження: дата документа = дата завершення періоду; за один період одна позиція 14–19.

## Антиаварійне правило релізу
Кожну наступну версію зберігати мінімум у трьох місцях:
1. локальний ZIP користувача;
2. ChatGPT Library `/Taxo/Releases/`;
3. GitHub окрема гілка/commit.
Після кожної версії оновлювати `PROJECT_STATE.md`, `RECOVERY_INDEX.md`, цей `AI_HANDOFF.md`, `VERSION.txt` і SHA-256.
