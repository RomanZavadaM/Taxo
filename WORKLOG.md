# WORKLOG — Taxo

**Оновлено:** 01.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest integrated code checkpoint:** **10.9-r1**  
**Latest full multi-platform checkpoint:** **10.9-r1 / `v10.9-r1`**  
**Latest issued fast-test:** **10.9-r7 / `v10.9-r7`**  
**Current active slice:** **10.9-r8 — накази / незмінність і закріплення**  
**Integrated main baseline:** `8f18a7ccf1588556f6f3d7dca81943f87d817935`  
**Active branch:** `work/v10.9-r8-orders-immutability`  
**Base:** immutable `v10.9-r7` → `88fcfb20e8632178b095a99ef9b09c86701a072e`  
**Stable remains:** `v10.3`  
**Live ledger:** Issue #61

## DONE — 10.9-r7 immutable issuance

10.9-r7 виправив підтверджені ризики СТОІР:

- `reading_at -> work_date` fallback для хронології одометра;
- новіший waybill-факт не губиться через порожній `reading_at`;
- середній пробіг використовує валідні датовані сегменти і newest-fact lookback;
- прогноз ТО відраховується від останньої надійної дати одометра;
- одиничний очевидний викид не домінує середній при достатній історії;
- ТО-1/ТО-2 лишилися окремими циклами до явного бізнес-рішення.

Immutable source: `88fcfb20e8632178b095a99ef9b09c86701a072e`.  
Exact-source regression: **769/769 OK**.  
Gates: source `36916227610`, Windows `36916259871`, macOS `36916259785`, publisher `36916515063` — success.  
Release: `v10.9-r7` / https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r7  
START SHA-256: `8d35d2e8af76af1a90e9a6600b5d637d80fb80a28cb4d2331e85f9a336e88222`.

PR #126 лишається draft/unmerged. `main` не змінено.

## DOING — 10.9-r8

Ціль: **зробити затверджені/підписані накази незмінними й прибрати неоднозначність закріплень водія за ТЗ**.

Підтверджено на старому runtime і реалізовано:

1. approved/signed наказ не можна редагувати як чернетку;
2. cancelled наказ не можна повторно approve;
3. непереданий `control_employee_id` більше не очищає відповідального;
4. assignments під approved/signed наказом не можна додавати/редагувати/видаляти;
5. overlapping assignment одного водія за різними ТЗ у новому наказі блокує approval;
6. одне однозначне попереднє закріплення завершується новим наказом окремим фактом, без переписування старого затвердженого наказу.

Технічно:

- additive runtime layer `v1098_orders_immutability.py`;
- additive table `vehicle_driver_assignment_endings`;
- `tests/test_v10_9_r8.py` — поведінкові SQLite-сценарії;
- machine identity = `10.9-r8`;
- feature layer `v1098-orders-immutability` у domain `operations`;
- START/source package guards вимагають r8 runtime;
- аудит: `docs/maintenance/AUDIT_OPERATIONS_ORDERS_v10.9-r8.md`;
- release notes: `docs/releases/RELEASE_NOTES_v10.9-r8.md`.

## NEXT

1. Прибрати тимчасовий integration workflow.
2. Відкрити draft PR r8 поверх frozen r7.
3. Прогнати exact-head source/START + Windows/macOS gates.
4. Якщо gates зелені — видати immutable `v10.9-r8` START+checksum.
5. Зафіксувати SHA/run IDs/checksum у PR та Issue #61.
6. Не зливати в `main` без прямої команди власника.
