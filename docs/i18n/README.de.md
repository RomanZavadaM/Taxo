# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo ist ein Desktop-System für ein einzelnes Transportunternehmen: Personal und Fahrer, Dienstpläne, Arbeitszeiterfassung, Fahrtenbücher, Tätigkeitsnachweise, Fahrzeuge, Dokumentenkontrolle, Wartung, Berichte und Prüfung analoger Tachographenscheiben.

> **Stable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 2026-10-05
> **Vorherige Stable / Rollback:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Nächste Code-Revision:** `10.10-r4`

## Downloads — Taxo 10.10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [Release Notes 10.10 (Ukrainisch)](../releases/RELEASE_NOTES_v10_10.md) · [Release-Index](../releases/RELEASE_INDEX.md)

Arbeitsdatenbanken, SQLite-Dateien, Scans, Caches und persönliche Dokumente sind nicht in GitHub-Releases enthalten. Ein Update erfordert keine erneute Eingabe der Arbeitsdaten.

## Neu in 10.10

- **Ohne PyMuPDF.** Tätigkeitsnachweis (PDF/JPG), Datumsstempel im Bericht Nr. 340 sowie PDF-Ansicht/-Druck nutzen Bibliotheken mit permissiven Lizenzen (pypdfium2, reportlab, pypdf); die Ausgabe ist pixelgleich zur Vorversion.
- **Korrekte Versionsanzeige** im Fenstertitel, im Info-Dialog, in PDF-Kopfzeilen und im Backup-Manifest.
- **Sicherungen** warnen ausdrücklich, wenn sie nur Datenbanken enthalten.
- **Infrastruktur:** veraltete Veröffentlichungs-Workflows deaktiviert, Tests vom Arbeitsspeicher isoliert, Lizenzprüfung in jedem Build.
- Enthält die gesamte Linie 10.4 … 10.9: Gültigkeit der Fahrzeugdokumente für die ganze Fahrt, Schutz ausgegebener Fahrtenbücher und Nummern, strengere Arbeits-/Ruhezeitkontrolle, 60-Tage-Register, Personalbilanz, Wartung, unveränderliche unterzeichnete Anordnungen, SQLite-Schemakompatibilität.

## Hauptfunktionen

Personal- und Fahrerhistorie; individuelle und periodische Dienstpläne; Plan/Ist-Arbeitszeit und geteilte Schichten; Kontrolle von Arbeits-, Lenk-, Pausen- und Ruhezeiten; 60-Tage-Tätigkeitsregister; Fahrzeuge, Kilometerstand, Wartung und Dokumente; reguläre und nicht reguläre Fahrtenbücher; Tätigkeitsnachweise; analoge Tachographenprüfung; geschützte Anordnungen und Fahrer→Fahrzeug-Zuordnungen; PDF/Excel-Berichte; Sicherungen und SQLite-Kompatibilitätskontrolle.

## Entwicklung

Die maßgebliche Betriebsdokumentation wird auf Ukrainisch geführt. Einstieg: [`START_HERE.md`](../../START_HERE.md). Nach Stable 10.10 beginnt neuer Code mit `10.10-r4` vom aktuellen `main`. Veröffentlichte Revisionen sind unveränderlich.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo ist proprietäre Software.
