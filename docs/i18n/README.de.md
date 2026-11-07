# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo ist ein Desktop-System für ein einzelnes Transportunternehmen: Personal und Fahrer, Dienstpläne, Arbeitszeiterfassung, Fahrtenbücher, Tätigkeitsnachweise, Fahrzeuge, Dokumentenkontrolle, Wartung, Berichte und Prüfung analoger Tachographenscheiben.

> **Stable:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — vom Eigentümer als stable freigegeben; exakter r10-Checkpoint unter Windows 10/11, Windows 7, macOS Intel und Apple Silicon geprüft
> **Ersetzt:** [Taxo 10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r4) — für macOS wegen eines bestätigten Startfehlers nicht empfohlen
> **Vorherige Stable / Rollback:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)
> **Älterer Rollback:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
> **Älterer Rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)

## Downloads — Taxo 10.9-r10 (älterer Rollback)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Release Notes 10.9-r10 (Ukrainisch)](../releases/RELEASE_NOTES_v10.9-r10.md) · [Release-Index](../releases/RELEASE_INDEX.md)

## Downloads — Taxo 10.12-r10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/SHA256SUMS_v10_12_r10.txt)

Arbeitsdatenbanken, SQLite-Dateien, Scans, Caches und persönliche Dokumente sind nicht in GitHub-Releases enthalten. Ein Update erfordert keine erneute Eingabe der Arbeitsdaten.

## Inhalt der vorherigen Stable 10.9-r10

- dauerhafte Historie ausgegebener Fahrtenbücher und Nummern; Aufbewahrungsfristen löschen keine verknüpften Fakten
- Gültigkeit der Fahrzeugdokumente für die gesamte geplante Fahrt
- strengere Arbeits-/Ruhezeitkontrolle: Überschneidungen, 3+9, wöchentliche und zweiwöchentliche Ruhezeit
- 60-Tage-Register ohne erfundene Ruhezeit; tatsächliche Quellen haben Vorrang
- Personalbilanz / P-5, Regime 2/2 und 3/3
- Wartung: Kilometerstand-Chronologie und Wartungsprognose
- genehmigte/unterzeichnete Anordnungen und Fahrer→Fahrzeug-Zuordnungen sind unveränderlich
- Kontrolle der SQLite-Schemakompatibilität
- strukturierter Code ohne Änderung der Geschäftslogik

## Linie 10.10

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) sind frühere Vorabversionen. [**10.10-r5**](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) behob den macOS-Startfehler und ist jetzt die vorherige Stable / Rollback-Version. **10.12-r10 ist die aktuelle Stable-Version**.

## Entwicklung

Die maßgebliche Betriebsdokumentation wird auf Ukrainisch geführt. Einstieg: [`START_HERE.md`](../../START_HERE.md). Aktuelle Stable ist `10.12-r10`; die neuere `10.13-r1` ist in `main` integriert, aber nicht stable. Die nächste Code-Revision ist `10.13-r2`.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo ist proprietäre Software.
