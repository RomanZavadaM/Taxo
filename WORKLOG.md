# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Latest issued fast-test:** **10.9-r3 / `v10.9-r3`**  
**Current active slice:** **10.9-r4 — work/rest compliance**  
**Integrated main baseline:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Active branch:** `work/v10.9-r4-work-rest-compliance`  
**Base:** immutable `v10.9-r3` → `df4cecf08595ef90dbf9216505aa8634d354ccf5`  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r3 immutable issuance

10.9-r3 закрив контроль обов'язкових документів ТЗ на весь плановий рейс. Immutable issued source: `df4cecf08595ef90dbf9216505aa8634d354ccf5`; tag `v10.9-r3` вказує саме на цей SHA; exact-source regression **741/741 OK**; publisher `36876067099`, START/source `36876067003`, Windows `36876072197`, macOS `36876072373` — success.

START: `Taxo_v10_9_candidate_r3_START.zip`; SHA-256 `5acdaf869d32d46414f7f76d971c4af21c3c6dcd89f3b7c4ef491aaaaf7d707b`.

10.9-r3 заморожена. PR #122 лишається draft/unmerged до окремої прямої команди власника.

## DOING — 10.9-r4

Ціль: **закрити підтверджені ризики контролю робочого часу та відпочинку, не змішуючи PLAN і FACT**.

Зроблено в code slice:

- новий `work_rest_compliance.py` поверх історичної моделі 10.4-r6;
- межі контрольного вікна включені у free-gap analysis;
- якщо кваліфікованого щоденного/щотижневого відпочинку немає, це більше не проходить мовчки;
- перекриття робочих інтервалів позначається як помилка даних, а не тихо поглинається merge;
- збережено законну модель 3+9;
- збережено ліміт скорочених щоденних відпочинків між щотижневими;
- додано контроль шести 24-годинних періодів між щотижневими відпочинками;
- додано консервативний контроль двох послідовних тижнів;
- runtime layer `v1094-work-rest-compliance` підключений після r3;
- `main.APP_VERSION` і `VERSION.txt` = `10.9-r4`;
- START/source package guards включають `work_rest_compliance.py`;
- додані поведінкові тести r4;
- аудит і release notes створені.

## NEXT

1. Прогнати повний exact-head regression/START та виправити лише підтверджені r4 failures.
2. Відкрити draft PR r4 поверх frozen r3 і підтвердити exact-head Windows/macOS gates.
3. Після зелених gates додати immutable publisher `v10.9-r4`, видати START і checksum.
4. Зафіксувати exact SHA/run IDs/checksum в Issue #61 і PR; r4 заморозити.
5. Не зливати в `main` без прямої команди власника.
