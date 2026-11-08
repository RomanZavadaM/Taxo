# Taxo — поточна контрольна точка

**Дата:** 08.11.2026  
**Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10)  
**Stable exact source:** `6d0f32bc45323d4085bb165b2ec050dae7b378ee`  
**Поточний integrated main product:** **Taxo 10.13-r6** — не stable; exact product `a3f4e7e924f8d4c7389b28dc659c2f1e72e210da`  
**Previous stable / rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)  
**Older rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)  
**Next code revision:** `10.13-r7`  
**Recovery:** `START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub → `PROJECT_STATE.md`

## Stable 10.12-r10

- Owner approved promotion 07.11.2026 after manual r10 acceptance without a blocking defect.
- Tag/release `v10.12-r10` points exactly to product commit `6d0f32bc45323d4085bb165b2ec050dae7b378ee`.
- GitHub Latest verified; release is not draft and not prerelease.
- 8 canonical assets: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START, SHA256SUMS.
- Exact r10 checks: Windows #1269, Win7 #262, macOS #1187, START #2315 — SUCCESS.
- PR-head r10 Windows regression: **931 tests / OK**.
- Google Drive recovery copy already exists: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.12-r10_2026-11-07_START.zip`.

## Що закрила лінія 10.12

- повернення загубленого штатного входу до простого місячного графіка;
- executable registry критичних функцій;
- fail-safe для центру даних працівників;
- live reachability для вкладених маршрутів, layout-контролів, шляхівок, центру документів, основної навігації та вибору водіїв;
- **23/23 критичних маршрутів** мають runtime-smoke requirement;
- «План → факт» додатково має behavioral gate на ізольованих даних: відсутній факт заповнюється, наявний підтверджений факт не перезаписується.

## Поточний main після stable

У `main` інтегровано **10.13-r6**. Після r5 shared selector foundation r6 додав реальні структуровані зв'язки наказу:

- вкладка **«Учасники / ТЗ»** з масовим вибором працівників і транспортних засобів;
- пошук за ПІБ/табельним №/ідентифікатором і держномером/VIN;
- stable Taxo ID + роль + frozen snapshot реквізитів;
- зміна живої картки не переписує історичний документний перелік;
- inactive не додаються до нового наказу; після введення наказу в дію перелік immutable;
- add/remove лишаються в історії наказу;
- PDF друкує окремий структурований перелік із табельним №/Taxo ID та VIN;
- наказ про закріплення ТЗ/водіїв лишається на своїй спеціалізованій моделі.

Exact product `a3f4e7e924f8d4c7389b28dc659c2f1e72e210da`: Windows #1313 — **972 tests / OK**, Win7 #299 — SUCCESS, macOS #1224 Intel/ARM — SUCCESS, START #2329 — SUCCESS.

Recovery-copy exact START: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r6_2026-11-08_START.zip`, 1 669 795 байт, Drive file `1MXbWM_ppcKBGhRRtPJtq8V1Y226_4YKK`, SHA256 `6b362f065190b708f27c11cb1f8d08cd70fe57a9b2d5e72d0b2b247736392e36`.

Це новіша розробка, але вона **не входить у stable 10.12-r10**.

## Далі

Ручне приймання 10.13-r6: створити звичайний наказ, у вкладці «Учасники / ТЗ» масово додати працівників/ТЗ, перевірити табельний № / VIN, PDF і незмінність після введення наказу в дію. Наступний code revision — **10.13-r7**. Stable змінювати лише окремим рішенням власника.
