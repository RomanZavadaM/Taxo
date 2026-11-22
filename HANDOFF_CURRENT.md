# HANDOFF_CURRENT — Taxo

**22.11.2026 — 10.24-r1 опубліковано як Test prerelease; Stable/Latest лишається 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`, GitHub Latest.

**Current Test:** [10.24-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r1), exact source `adb6ae40e966d77018c6dc8c1c4fdcbde6a6a827`, 8 assets, prerelease. Publisher #45053863942 — SUCCESS.

Exact-source r1 CI: START #45052687870, Windows #45052687839, Win7 #45052687867, macOS Intel/ARM #45052687880 — SUCCESS. Windows і Win7 mandatory Microsoft Defender gates та post-scan integrity verification — SUCCESS.

## Що додає 10.24-r1

- окремі доменні модулі `correspondence_registry` і `correspondence_service`, без розростання `main.py`;
- керований реєстр `Data/Correspondence/registry.json`, format `taxo.correspondence-registry.v1`;
- два незалежні журнали: incoming / outgoing;
- окремі річні номерні послідовності з відображенням `Вх. № 0001/2026` та `Вих. № 0001/2026`;
- preview наступного номера не резервує номер; реєстрація резервує його атомарно;
- stable correspondence ID `cr-...`;
- розділені `registration_date`, `document_date`, `received_date`, `sent_date`;
- зовнішній номер кореспондента, кореспондент, тема, короткий зміст, спосіб отримання/відправлення, відповідальний, строк і стан;
- явні response/related links; вихідна відповідь посилається на існуючий вхідний лист;
- `document_ref` — лише стабільне посилання на контрольований готовий документ, без копіювання його байтів;
- пошкоджена номерна послідовність fail-closed, щоб уже виданий номер не можна було видати повторно;
- same-process parallel registration не дублює номери;
- чинний full workspace backup/restore зберігає реєстр і наступний номер.

## Важливі межі

- реєстрація вихідного листа не означає фактичного відправлення;
- вхідний лист можна зареєструвати без скана чи файла;
- немає UI, автоматичного e-mail, OCR, зовнішнього AI, AI APPLY або фізичного сортування;
- немає нового дублюючого сховища готових документів;
- DocumentVault/БД не змінюються цим модулем;
- Stable/Latest не змінено.

## Наступний крок

**10.24-r2 — контрольовані файли/вкладення кореспонденції та backup/restore.**

Перший bounded slice r2:
- окремий immutable attachment store у робочому сховищі або контрольований link на вже наявний DocumentVault, без дублювання одного й того самого файла;
- SHA256, MIME/extension, original filename, size і stable attachment ID;
- прив'язка attachment → correspondence record;
- safe add/list/open/remove-as-history semantics, без автоматичного «надіслано/отримано»;
- full backup/restore має зберігати attachment metadata/bytes і не ламати номерні послідовності;
- UI, e-mail automation, OCR/AI і справи/ланцюжки — окремими наступними ревізіями.

Draft #543 лишається архітектурним планом. #553/#556/#562 залишаються відкритими. Draft #395 не закривати автоматично.

APPLY старих AI-import proposals не починати без окремого рішення власника.

Recovery: START_HERE → HANDOFF → private Taxo-profile → live GitHub.
