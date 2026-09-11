# Taxo v8.60 — test report

Date: 11.09.2026

- `main.py` and `tachograph.py`: `py_compile` OK.
- Old DB migration automatically adds `last_name_en`, `first_name_en`, `middle_name_en`.
- Filled English driver fields are used on the English side of the Attestation form.
- Per-field fallback verified: a blank English field uses the corresponding Ukrainian value.
- If all English driver-name fields are blank, the English side uses the full Ukrainian driver name.
- Company English fields introduced earlier remain functional.
- No user SQLite database is included in the release archive.
