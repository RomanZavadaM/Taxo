# Taxo 10.5-r8 — full multi-platform checkpoint

## Статус

- **Tag/release:** `v10.5-r8`
- **Issued source:** `846e5c5111b14a4a1f2e49203803e86c495b458f`
- **Release workflow:** `36406419955` — success
- **Regression:** `483/483 OK`
- **PR:** #76 — merged
- **Main merge commit:** `eb9cb039d35419fb579ff0f5e1b9c633c95ccd86`
- **Stable:** `v10.3` залишається без змін до окремого рішення власника.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8

## Чому з’явилась r8

Під час повного багатоплатформного checkpoint після r7 окрема Windows 7 / Python 3.8 лінія показала коротший текст помилки openpyxl: `__init__() got an unexpected keyword argument 'tabId'` без слова `ChildSheet`. r7 уже була видана й залишилась immutable, тому виправлення оформлено новою ревізією r8.

## Виправлено

- імпорт XLSX «Шлях» на Windows 7 / Python 3.8 розпізнає обидва фактичні варіанти `tabId` TypeError;
- compatibility retry запускається лише для помилки з `unexpected keyword argument` і `tabId`;
- вихідний XLSX не змінюється — службовий атрибут прибирається тільки у тимчасовій in-memory копії;
- сторонні `TypeError` не перехоплюються як compatibility-випадок;
- regression fixture не залежить від того, чи openpyxl включив `ChildSheet` у текст помилки.

## Збережено без зміни бізнес-логіки

r8 не змінює правила r7 та попередніх revision. Збережено:

- Diia-first цикл персонального військового звіряння;
- чітке розділення локальної підготовки та фактичної зовнішньої фіксації в Дії;
- immutable державні snapshots і окремі редаговані робочі значення;
- звірку ТЗ з «Шлях»;
- реєстр документів працівників;
- військово-транспортну відомість підприємства;
- plan/fact, бланки, табелі, графіки, шляхові листи та контроль документів ТЗ.

## Опубліковані пакети

- `Taxo_v10_5_candidate_r8_START.zip`
- `Taxo_v10_5_candidate_r8_Windows_x64_Portable.zip`
- `Taxo_v10_5_candidate_r8_Setup_Windows_x64.exe`
- `Taxo_v10_5_candidate_r8_Windows7_x64_Portable.zip`
- `Taxo_v10_5_candidate_r8_Setup_Windows7_x64.exe`
- `Taxo_v10_5_candidate_r8_macOS_arm64_Portable.zip`
- `Taxo_v10_5_candidate_r8_macOS_x86_64_Portable.zip`
- `SHA256SUMS_v10_5_r8.txt` та platform manifests.

Робочі БД, SQLite-файли, скани, кеші й персональні документи в release не входять.

## SHA-256 основних пакетів

- START: `4ed92fb110f3911ea8d172bc1abbfdd9594460acfe6c1a8084f42bc15447148b`
- Windows 7 Setup: `145bb7a8ac7d143aea50b961d1bf7c27c9fa6234a994e46ffffa806aae66e347`
- Windows modern Setup: `ccf6b2113bdc7cf77016f85639c670082720df4dac31976488e04e3da72852a6`
- Windows 7 Portable: `eec35eca3ed5f866d343c5b895e17d7cf35c7c6f660f28c85aad0f8a7b2131bd`
- Windows modern Portable: `b6bf08672e63519063e9cbfdf3389b0021935d9ed2641c562fb8a57f12af9ddf`
- macOS ARM64: `5e44f8437c2b22b1c03a11438dbdd83cd373e97ae45f53a7b64490a8e812d59a`
- macOS Intel: `278fe622fcebc045f78d317ae2187424a0195a9ed0162f047df34d0123502d92`

## Наступна ревізія

`10.5-r8` immutable. Наступний кодовий крок — тільки **10.5-r9**.
