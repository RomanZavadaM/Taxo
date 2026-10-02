# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo ist eine Desktop-Anwendung für ein einzelnes Verkehrsunternehmen: Personal und Fahrer, Dienstpläne, Arbeitszeiterfassung, Fahrtenblätter, Tätigkeitsbestätigungen, Fahrzeuge, Dokumentenkontrolle, Berichte, Wartungsplanung und selektive Verarbeitung analoger Tachographenscheiben.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Neuester integrierter Checkpoint in `main`:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Neuester vollständiger Multi-Plattform-Checkpoint:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Vorherige Stable-/Rollback-Version:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).

## Downloads — 10.9-r9

**Windows:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [ARM64 / Apple Silicon](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**Tests/Diagnose:** [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [Release](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9) · [Release Notes](docs/releases/RELEASE_NOTES_v10.9-r9.md)

Für den normalen Betrieb verwenden Sie ein fertiges Windows/macOS-Paket. Benutzerdatenbanken, SQLite-Dateien, Scans, Caches und personenbezogene Dokumente sind nicht Bestandteil der GitHub-Releases.

## Hauptfunktionen

Personal/Fahrer mit Historie, individuelle und periodische Dienstpläne, Plan/Ist-Arbeitszeit, geteilte Schichten, Work/Driving/Break/Rest-Kontrolle, 60-Tage-Aktivitätsregister, Fahrzeuge und Dokumente, Wartung, reguläre und nicht regelmäßige Fahrtenblätter, Tätigkeitsbestätigungen, analoge Tachographenscheiben, geschützte genehmigte/unterzeichnete Anordnungen, PDF/Excel-Berichte, Backups und SQLite-Schema-Kompatibilität.

## 10.9-r2 → 10.9-r9

Integriert wurden unveränderliche Fahrtenblattnummern-Historie, Dokumentgültigkeit über die gesamte Fahrt, stärkere Arbeits-/Ruhezeitkontrolle, sicherere Tatsachendaten-Priorität, historische Personal-/P-5-Korrekturen, Kilometer-/Wartungsprognosen, unveränderliche genehmigte/unterzeichnete Anordnungen und `PRAGMA user_version` als SQLite-Schema-Basis.

[Release Notes 10.9-r9](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [Release-Index](docs/releases/RELEASE_INDEX.md)

## Entwicklungsstand

Kanonische Betriebsdokumentation: Ukrainisch. Neue Sitzungen beginnen mit `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61. Nach `10.9-r9` ist die nächste Code-Revision **10.9-r10**.

## Urheberrecht und Lizenz

**Copyright © 2026 Roman Zavada (Роман Завада). Alle Rechte vorbehalten.** Taxo ist proprietäre Software.
