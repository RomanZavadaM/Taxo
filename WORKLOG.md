# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Latest issued fast-test:** **10.9-r4 / `v10.9-r4`**  
**Current active slice:** **10.9-r5 — tachograph / 60-day activity safety**  
**Integrated main baseline:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Active branch:** `work/v10.9-r5-tachograph-activity-safety`  
**Base:** immutable `v10.9-r4` → `c0e833ab81d91ed390e7917ed61bf5e2c5e86f21`  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r4 immutable issuance

10.9-r4 закрив підтверджені ризики контролю робочого часу та відпочинку: boundary gaps, відсутність кваліфікованого відпочинку, overlap як помилка даних, збереження 3+9, six-24h і консервативний двотижневий контроль. Immutable issued source: `c0e833ab81d91ed390e7917ed61bf5e2c5e86f21`; exact-source regression **748/748 OK**; publisher `36905246236`, START/source `36905246054`, Windows `36905253501`, macOS `36905253483` — success.

START: `Taxo_v10_9_candidate_r4_START.zip`; SHA-256 `c12bc995367f63c5e6d9a7af6aa283f5b220847dab08d6cd813f31a65788b3ab`.

10.9-r4 заморожена. PR #123 лишається draft/unmerged до окремої прямої команди власника.

## DOING — 10.9-r5

Ціль: **не дозволяти 60-денному реєстру або автоматичному розпізнаванню тахографа створювати юридично значущі факти без явного джерела**.

Зроблено:

- `activity_register_60.py` більше не перетворює незаповнені хвилини між активностями на `Перерва`;
- незаповнені хвилини поза активною частиною дня більше не стають автоматично `Відпочинок`;
- усі такі хвилини лишаються `Невизначено` з пояснювальною приміткою;
- явний тахографічний відпочинок продовжує класифікуватися як перерва всередині зміни або відпочинок поза нею;
- авто-кандидат тахографа знижено до пріоритету 40, щоб він не перекривав бланки/план/факт/межі керування;
- ручне підтвердження оператора лишається пріоритетом 100;
- `main.APP_VERSION` / `VERSION.txt` = `10.9-r5`;
- додані поведінкові тести, аудит і release notes.

## NEXT

1. Прогнати exact-head regression/START.
2. Відкрити draft PR r5 поверх frozen r4; підтвердити Windows/macOS gates.
3. Після зелених gates видати immutable `v10.9-r5` START+checksum.
4. Зафіксувати exact SHA/run IDs/checksum в Issue #61 і PR; r5 заморозити.
5. Не зливати в `main` без прямої команди власника.
