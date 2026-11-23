# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo ist eine Desktop-Anwendung für Verkehrsunternehmen: Personal und Fahrzeuge, Dienstpläne und Arbeitszeit, Fahrtblätter, Anordnungen, Dokumente, Wartung, Berichte und Sicherungen.

## Stable 10.24-r3

**10.24-r3 wurde durch die ausdrückliche Entscheidung des Eigentümers am 23.11.2026 zu Stable/Latest.** Enthalten sind alle akzeptierten Funktionen aus 10.23-r4 sowie die abgeschlossene Korrespondenzlinie r1–r3: getrennte Eingangs-/Ausgangsjournale, sichere Nummerierung, kontrollierte Anhänge, Suche, Datum/Kalender, sortierbare Tabellen, Detailkarte sowie Aktionen für Neu, Antwort, Anhänge und Dokument öffnen. Ein leeres Sendedatum bedeutet nicht automatisch „gesendet“.

37 strenge Live-UI-Pfade prüfen Sichtbarkeit, Bildschirmposition, Nutzbarkeit und Aktivierung. START, Windows, Windows 7 und macOS Intel/Apple Silicon waren erfolgreich; Windows/Win7 bestanden zusätzlich Defender- und Integritätsprüfungen. Die vollständige Funktionsabdeckung (#556) und der breitere End-to-End-Test der Anordnungen (#553) bleiben offen.

## Downloads

**Stable / Latest: [Taxo 10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).** Vorheriger stabiler Stand: [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/Taxo_v10_24_candidate_r3_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/SHA256SUMS_v10_24_r3.txt)

**Current Test:** [Taxo 10.24-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r4), Prerelease mit 8 Dateien, exact source `e1616ea0063575b2c989d684934364f38f995966`. Neu sind explizite tatsächliche Aktionen „Empfangen/Gesendet“ mit Pflichtdatum, nur vorwärts erlaubte Zustandsübergänge, eine unveränderliche Verlaufskette sowie Termin-/Überfällig-Kontrolle. Registrierung oder Anhang erzeugen keinen Versand-/Empfangsfakt. Der 760×520-Erreichbarkeitsfehler wurde im Layout behoben, ohne den Test abzuschwächen. Stable/Latest bleibt 10.24-r3.

Datenbanken und Dokumente in einem separaten Arbeitsordner speichern und vor Updates sichern. [Benutzerhandbuch (Ukrainisch)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Entwicklung: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). Alle Rechte vorbehalten. [LICENSE](../../LICENSE.md).
