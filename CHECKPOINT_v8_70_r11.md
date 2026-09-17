# Taxo v8.70 candidate r11 — 60-day driver activity register

Date: 17.09.2026
Base: `main` after candidate r10.

## User request

Create a separate work-time document for the tachograph-card retention window, using 60 calendar days. It must show the full time line rather than only inter-shift rest and allow an operator to determine what the driver was doing at any minute.

## Implementation

- New button in `Табель робочого часу`: **«Реєстр 60 днів»**.
- Fixed 60-calendar-day window with selectable end date.
- Separate landscape A4 PDF under `Output/ActivityRegisters`.
- First part: 60-day daily summary.
- Second part: exact `Від–До` interval journal for every day.
- Each day is represented by exactly 24:00 and each minute belongs to one of:
  - Керування;
  - Інша робота;
  - Готовність;
  - Перерва;
  - Відпочинок;
  - Відсутність;
  - Невизначено.
- Every interval includes its source, vehicle when known, and note.

## Source priority / auditability

1. Manually confirmed tachograph interval — highest priority.
2. Automatic tachograph candidate — clearly labelled as a candidate.
3. Exact worklog/work-segment time boundaries.
4. Confirmation-of-activities interval.
5. Day-type information.
6. Calculated break/rest only fills otherwise uncovered minutes around observed activity.
7. If no reliable source exists, the minute remains **Невизначено**; the program never silently invents rest.

Tachograph `Відпочинок` inside the observed active envelope of a day is shown as a calculated `Перерва`; outside that envelope it remains `Відпочинок`. The source still states that the underlying interval came from TAHO.

## Safety

- No database or personal data is committed.
- Existing tachograph recognition logic is unchanged.
- Existing №340 analysis and r10 weekly balances are unchanged.
- The report is generated from the current workspace databases read-only.

## Tests

`tests/test_v8_70_r11.py` covers:
- midnight-wrapped intervals;
- split workday -> break/rest filling;
- tachograph rest inside active envelope -> break classification;
- completely data-less day remains 24:00 `Невизначено`;
- exact 24:00 daily total.
