# Taxo v8.56 — контрольна публікація

Дата: 11.09.2026

## Контрольний реліз

Еталонний ZIP: `Taxo_v8_56.zip`  
SHA-256: `c1056a771457c4d499be2b2ff70eef45acdccc2bc9e2047fd7ca9aed2d533881`

Через обмеження GitHub-конектора повний ZIP не завантажувався як двійковий файл. У гілці `release-v8.56` код v8.56 збережено у відтворюваному текстовому вигляді:

- база: `releases/Taxo_v8_41_source.zip`;
- патчі v8.45: `Taxo_v8_45_main.part1` … `part4`;
- патчі v8.49: `Taxo_v8_49_delta.part1` … `part2`;
- патч v8.56 для `main.py`: `Taxo_v8_56_main.part01` … `part08`;
- патч v8.56 для `tachograph.py`: `Taxo_v8_56_tachograph.part01` … `part02`.

Кореневий `main.py` автоматично збирає runtime v8.56 і перевіряє SHA-256 кінцевих файлів перед запуском.

## Перевірені кінцеві SHA-256

- `main.py`: `30c5d46974964be86ee3a0d72130f20ef7c63893c7e82e30b8484abda014815f`
- `tachograph.py`: `6018a71b4a283dbbba640e1daa313eff9f26cdde931aa4cba77884a5141d20cc`
- `Бланк підтвердження.docx`: `47aeb545509af8d43102f76de772838b36de1fa85a2d09bae2d2ce7798358ec0`
- `requirements.txt`: `09acc97b0f5b65cab55a2dfb27304107769283154f81209bf5f65b3b30c9f319`
- `START.bat`: `34e20856ca85902b9a4b8beef5ef51c30cd86bdac3c83b9db23340606506cfb9`

## Перевірка копій

Дві незалежні копії `Taxo_v8_56.zip` у ChatGPT Library перевірені побайтно:

- розмір кожної: `1 774 832` байти;
- SHA-256 кожної: `c1056a771457c4d499be2b2ff70eef45acdccc2bc9e2047fd7ca9aed2d533881`;
- ZIP CRC/test: успішно;
- `main.py` та `tachograph.py`: `py_compile` успішно.

GitHub-текстові патчі також перевірені: їхні Git blob SHA збігаються з локально сформованими частинами, а застосування патчів до еталонної v8.49 дає байт-у-байт ті самі `main.py` та `tachograph.py`, що містяться в еталонному ZIP v8.56.

## Дані користувача

База користувача не входить до релізу і не публікується на GitHub. Постійні дані зберігаються поза програмою в `%USERPROFILE%\Documents\DriverWorktime\`.

Наступна версія для розробки: **v8.57**.
