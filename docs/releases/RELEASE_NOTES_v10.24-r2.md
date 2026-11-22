# Taxo 10.24-r2 — контрольовані вкладення кореспонденції

**Робочий Test-кандидат. Stable/Latest залишається 10.23-r4; поточний опублікований Test — 10.24-r1.**

10.24-r2 додає другий bounded slice модуля ділової кореспонденції: безпечні вкладення до вже зареєстрованих вхідних/вихідних листів без зміни самого r1 registry і без автоматичної зміни бізнес-стану листа.

## Що додано

- окремий store `Data/CorrespondenceAttachments`, щоб не послаблювати строгий `Data/Correspondence/registry.json`;
- immutable copied attachments зі stable ID `ca-...`, SHA256, MIME, size та original filename;
- content-addressed object storage: однакові байти фізично зберігаються один раз, але можуть бути явно прив'язані до різних листів;
- окремий `vault:vd-...` link на реально наявний DocumentVault без копіювання його байтів;
- підтримка PDF/JPG/PNG/TIFF/DOCX із перевіркою фактичного вмісту;
- DOCX із macro payload відхиляється; небезпечні archive paths/symlink entries не приймаються;
- fake extension, symlink source, missing/orphan/tampered object — fail-closed;
- active duplicate того самого SHA або vault-link у тому самому листі заборонено;
- `remove` створює append-only history event: незмінні байти фізично не видаляються;
- removed bytes продовжують проходити integrity verification;
- full workspace backup/restore зберігає registry, attachment index/history/bytes та наступні реєстраційні номери.

## Важливі межі

- додавання файла **не означає** sent/received/delivered/signed;
- registration status і semantic dates листа r2 не переписує;
- немає UI, автоматичного e-mail, OCR, зовнішнього AI, AI APPLY або фізичного purge;
- Stable/Latest змінюється тільки окремим рішенням власника.

## Перевірки prep

Prep PR #611 на фінальній голові `ad1108a2c02a2fc03791a20f9486ae1e7aaf04a0` пройшов START #45061620559, Windows #45061620569, Windows 7 #45061620603 та macOS Intel/ARM #45061620648 — SUCCESS. Windows і Win7 також пройшли mandatory Defender та post-scan integrity.

Наступний крок після випуску r2 — окремий UI/journal slice поверх уже перевірених registry + attachment APIs; не змішувати його з e-mail automation.
