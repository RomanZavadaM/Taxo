# Taxo — поточна контрольна точка

**Дата:** 08.11.2026  
**Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10)  
**Stable exact source:** `6d0f32bc45323d4085bb165b2ec050dae7b378ee`  
**Поточний integrated main product:** **Taxo 10.13-r5** — не stable; exact product `0b6e0b99dedcfcdbfe25df1460f483d197e623c9`  
**Previous stable / rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)  
**Older rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)  
**Next code revision:** `10.13-r6`  
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

У `main` інтегровано **10.13-r5**. Після r4, який дав вибір водія й ТЗ для наказу про закріплення, r5 виніс цей підхід у спільний механізм:

- працівники, водії та ТЗ вибираються як конкретні записи бази зі стабільним Taxo ID;
- працівник показується з ПІБ, табельним № і посадою; RNOKPP/registry ID доступні для точного зіставлення без автоматичного друку повного RNOKPP;
- водій — driver-only фільтр спільної employee-моделі;
- ТЗ показується з держномером, маркою/моделлю та VIN;
- інструктажі використовують той самий structured employee selector і формують CSV з ПІБ, табельним № та Кодом Taxo;
- active/historical режим не губить старі деактивовані записи;
- shared choices вже мають snapshot реквізитів, але збереження immutable snapshot у всіх наказах — ще наступний етап.

Exact product `0b6e0b99dedcfcdbfe25df1460f483d197e623c9`: Windows #1309 — **960 tests / OK**, Win7 #295 — SUCCESS, macOS #1220 Intel/ARM — SUCCESS, START #2327 — SUCCESS.

Recovery-copy exact START: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.13-r5_2026-11-08_START.zip`, 1 656 837 байт, Drive file `12xjT-MYyacorZVroEesvEicwR7Z17nPP`, SHA256 `c4d3f8cdbfa1d6c911f74bddc6682f18dc71a55699896ffbc5142d14c1c37107`.

Це новіша розробка, але вона **не входить у stable 10.12-r10**.

## Далі

Ручне приймання 10.13-r5: перевірити однозначний вибір водія/працівника й ТЗ (табельний №, VIN), а також масовий вибір працівників у підготовці інструктажу. Наступний code revision — **10.13-r6**: поширення спільного механізму на наступні типи наказів та історичні snapshots. Stable змінювати лише окремим рішенням власника.
