# Taxo — поточна контрольна точка

**Дата:** 07.11.2026  
**Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10)  
**Stable exact source:** `6d0f32bc45323d4085bb165b2ec050dae7b378ee`  
**Поточний integrated main product:** **Taxo 10.13-r1** — не stable  
**Previous stable / rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)  
**Older rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)  
**Next code revision:** `10.13-r2`  
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

У `main` уже інтегровано **10.13-r1** (Експлуатація / СТОІР / накази). Це новіша розробка, але вона **не входить у stable 10.12-r10** і не повинна підміняти exact stable source.

## Далі

Спочатку ручне приймання 10.13-r1. Наступний дозволений code revision — **10.13-r2**. Stable змінювати лише окремим рішенням власника.
