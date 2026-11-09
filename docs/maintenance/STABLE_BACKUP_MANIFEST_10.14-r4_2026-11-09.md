# Taxo 10.14-r4 — stable release & reserve manifest

**Дата:** 09.11.2026. **Статус:** GitHub stable/latest verified. **Користувацькі дані в реліз не включені.**

## Ідентичність

- Official release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4
- Tag target (immutable source): `214f714f4804cb284fdcbc5b5a26418cef40937a`.
- Product code baseline: `677458afa06893b4d221130db72de4045187e0c8` (10.14-r4 logic). Docs synchronized before tag.
- Publication workflow: `Promote verified historical Taxo checkpoint to stable` run #3 — SUCCESS; `publish-current` intentionally skipped on marker commit to avoid duplicate release.
- Exact-source checks: Windows #1364, Win7 #341, macOS #1266, START #2404 — SUCCESS.
- Previous stable / rollback: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10

## Офіційні файли GitHub Releases (8/8)

| Файл | Розмір, байт |
|---|---:|
| `Taxo_v10_14_candidate_r4_Setup_Windows_x64.exe` | 60 534 830 |
| `Taxo_v10_14_candidate_r4_Windows_x64_Portable.zip` | 88 915 724 |
| `Taxo_v10_14_candidate_r4_Setup_Windows7_x64.exe` | 52 373 457 |
| `Taxo_v10_14_candidate_r4_Windows7_x64_Portable.zip` | 80 137 706 |
| `Taxo_v10_14_candidate_r4_macOS_arm64_Portable.zip` | 77 092 158 |
| `Taxo_v10_14_candidate_r4_macOS_x86_64_Portable.zip` | 68 276 908 |
| `Taxo_v10_14_candidate_r4_START.zip` | 1 741 336 |
| `SHA256SUMS_v10_14_r4.txt` | 794 |

В усіх посиланнях базовий URL: `https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/` + точна назва. SHA256: https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/SHA256SUMS_v10_14_r4.txt

## Google Drive backup (фактичний стан)

Папка: https://drive.google.com/drive/folders/12Gf4yDjVXYVgJfhcOVcSs1cjrTPGMBYW

- macOS ARM64 GitHub build artifact ZIP: `1-190vJwRPqhTK2mwngiTCDrm1W-C9_uu`.
- macOS Intel GitHub build artifact ZIP: `12-9UGZBLf79LXaXoLqS4I1BB6g9CKHFH`.
- START/source GitHub build artifact ZIP: `1O4ImHsnLsFzro_lxjSA5eORoFRYBgkxP`.
- Separate exact-product START copy in `02_CURRENT_MAIN`: `13cu1dNOBcVAS8zFO0Z1JnBUy212wu3dp`.

**Обмеження:** Google Drive connector відхилив 131–148 МБ GitHub Actions artifact ZIP для Windows та Windows 7 (413; 100 МБ лиміт). Вони **не підтверджені як незалежний Drive backup**. Водночас шість офіційних Windows/macOS binary assets і START зберігаються в GitHub Releases за immutable tag. Резервні ZIP у Drive — це artifacts GitHub Actions, вони можуть містити по кілька файлів і **не є файлами з однаковою назвою/контрольною сумою** з release assets. Не стверджувати інакше.

## Перевірки та наступне

- `releases/latest` повертає `v10.14-r4`, `prerelease=false`, `draft=false`.
- Git tag має точний SHA, всі 8 імен/розмірів підтверджені через GitHub API.
- Перед масовими діями в робочих даних — користувацька резервна копія.
- Новий код починати з 10.14-r5; stable tag не пересувати.
