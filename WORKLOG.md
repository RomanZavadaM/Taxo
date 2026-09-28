# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main merge:** PR #84 → `0151fea9a2a27bf8e970ca71ef9786a2d750d0ab`  
**Issued source/tag target:** `97e646936d14d163faf93882daf7894f5bb38ab6`  
**Regression:** `530/530 OK`  
**START verify:** `36434131185` — success  
**Full asset publisher:** `36440880324` — success  
**Final Windows gate:** `36441149032` — success  
**Final macOS gate:** `36441148816` — success  
**Release:** https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3  
**Next code revision:** **10.6-r4**  
**Live ledger:** Issue #61

## DONE — 10.6-r3 main checkpoint

- [x] Fast-test r3: нерегулярна шляхівка очищає лише regular-route таблиці/напрямок.
- [x] Лікар I/II, механік I/II, спідометр і фактичний пробіг зберігаються, якщо реально є в payload.
- [x] Поля без фактичного джерела не вигадуються; `schedule_code` навмисно порожній.
- [x] Успадковано нерегулярні виїзди: замовлення, розвозки, місто, область, міжобласні та інші разові роботи.
- [x] Успадковано plan/fact audit correction і default-on фільтр неактивних ТЗ.
- [x] Успадковано адаптивне вікно «Про програму».
- [x] Regression: `530/530 OK`.
- [x] START asset виданий і перевірений; SHA-256 `ea97909e7ae8a895730172aef4f6cabf61c18c227adce12cdaec803dfe8c490c`.
- [x] Повні пакети з exact issued source `97e646936d14d163faf93882daf7894f5bb38ab6` зібрані: Windows x64, Windows 7 SP1, macOS ARM64, macOS Intel.
- [x] Win7 PE compatibility gate пройдено.
- [x] Перший publisher run `36439848549`: усі build jobs success; publish-only step зупинився через вкладений `release_out/` шлях інсталятора в Actions artifact.
- [x] Publisher retry `36440880324` нормалізував шлях і успішно додав executable assets та platform/full checksums до існуючого `v10.6-r3` без пересування tag/START.
- [x] One-shot publisher workflows видалені з work-гілки до merge.
- [x] Фінальні PR gates на head `737bc5a855be8e81f8ba403a16df06d336692a3a`: Windows і macOS success.
- [x] PR #84 merged у `main`: `0151fea9a2a27bf8e970ca71ef9786a2d750d0ab`.
- [x] Документація й README синхронізуються окремим docs-only closeout без зміни runtime/revision.

## RELEASE ASSETS — v10.6-r3

- `Taxo_v10_6_candidate_r3_Setup_Windows_x64.exe`
- `Taxo_v10_6_candidate_r3_Windows_x64_Portable.zip`
- `Taxo_v10_6_candidate_r3_Setup_Windows7_x64.exe`
- `Taxo_v10_6_candidate_r3_Windows7_x64_Portable.zip`
- `Taxo_v10_6_candidate_r3_macOS_arm64_Portable.zip`
- `Taxo_v10_6_candidate_r3_macOS_x86_64_Portable.zip`
- `Taxo_v10_6_candidate_r3_START.zip`
- platform SHA-256 manifests
- `SHA256SUMS_v10_6_r3_FULL.txt`

## PRESERVED

- Stable `v10.3` не пересунуто.
- `v10.6-r3` tag target лишається exact issued source `97e646936d14d163faf93882daf7894f5bb38ab6`.
- plan/fact і тахографічна межа не змінюються.
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Наступна кодова робота починається тільки як **10.6-r4** у новій work-гілці після наступного завдання власника.

## BLOCKED

Немає.
