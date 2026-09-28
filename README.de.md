# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo ist eine Desktop-Anwendung für ein einzelnes Verkehrsunternehmen: Personal und Fahrer, Dienstpläne, Arbeitszeiterfassung, Fahrtenblätter, Tätigkeitsbestätigungen, Fahrzeuge, Dokumentenkontrolle, Berichte und selektive Verarbeitung analoger Tachographenscheiben.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Neuester vollständiger Checkpoint in `main`:** [Taxo 10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3).  
> **Vorherige Stable-/Rollback-Version:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.6-r3` ist ein vollständiger Candidate/Checkpoint und wird nur durch eine separate Entscheidung des Eigentümers zur Stable-Version.

## Downloads 10.6-r3

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/SHA256SUMS_v10_6_r3_FULL.txt)

Benutzerdatenbanken, SQLite-Dateien, Scans, Caches und personenbezogene Dokumente sind niemals Bestandteil der GitHub-Releases.

## Hauptfunktionen

- Personal- und Fahrerregister mit Rollen und Historie;
- individuelle und periodische Fahrerpläne;
- Arbeitszeittabellen mit geteilten Schichten und klarer Trennung von Plan und Ist;
- Kontrolle von Arbeit, Lenkzeit, Pausen und Ruhezeit;
- getrennte Wochenbilanzen für **60:00 Arbeitszeit** und **56:00 Lenkzeit**;
- Fahrzeugregister, Kilometerhistorie und Dokumentenkontrolle;
- reguläre Routen sowie nicht regelmäßige Einsätze: Aufträge, Zubringer-/Personalverkehr, Stadt-, Regional- und überregionale Fahrten;
- Fahrtenblätter, Tätigkeitsbestätigungen und PDF-/Excel-Berichte;
- analoge Tachographenscheiben mit manueller Prüfung;
- Arbeitsbereich, Sicherungen und Übertragung der Arbeitsdaten.

## Checkpoint 10.6-r3

Der Checkpoint enthält die Korrektur der Plan/Ist-Prüfung, das standardmäßige Ausblenden inaktiver Fahrzeuge im Dokumentenregister, die Ausgabe von Fahrtenblättern für nicht regelmäßige Fahrten ohne zwingende Katalog-`route_id` sowie ein anpassbares „Über das Programm“-Fenster. Bei nicht regelmäßigen Fahrten bleibt die Routentabelle leer; vorhandene reale Daten zu Arzt, Mechaniker, Kilometerzähler und tatsächlicher Fahrleistung bleiben erhalten. Fehlende Ist-Werte werden nicht aus dem Plan erfunden.

Vollständige Hinweise: [Release Notes 10.6-r3](docs/releases/RELEASE_NOTES_v10_6_r3.md).

## Staatliche Register und militärische Buchhaltung

Taxo unterstützt den Fahrzeugabgleich mit „Shlyakh“, editierbare Arbeitswerte getrennt von unveränderlichen staatlichen Snapshots, ein Mitarbeiterdokumentenregister, verlustfreien XLSX-Import, eine betriebliche militärische Fahrzeugaufstellung sowie einen lokalen Diia-first-Ablauf für den jährlichen Personalabgleich.

Taxo **ersetzt keine staatliche API** und behauptet keine automatische Übermittlung an Diia, Oberih oder Shlyakh.

## Dokumentation und Entwicklungsstand

Die kanonische Betriebsdokumentation wird auf Ukrainisch gepflegt. Neue Entwicklungs-/Recovery-Sitzungen beginnen mit `START_HERE.md`, danach `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` und Issue #61. Bereits ausgegebene Revisionen sind unveränderlich. Nach `10.6-r3` ist die nächste Code-Revision **10.6-r4**.

Siehe [Dokumentationsübersicht](docs/README.md) · [Systemübersicht](docs/SYSTEM_OVERVIEW.md) · [Schnellstart](docs/guides/QUICK_START.md) · [Release-Index](docs/releases/RELEASE_INDEX.md).

## Urheberrecht und Lizenz

**Copyright © 2026 Roman Zavada (Роман Завада). Alle Rechte vorbehalten.**

Taxo ist proprietäre Software. Die öffentliche Sichtbarkeit dieses Repositorys gewährt keine Open-Source-Lizenz und keine Erlaubnis zur Weiterverbreitung, zum Verkauf, zur Wiederveröffentlichung oder zur Verbreitung geänderter/abgeleiteter Versionen ohne schriftliche Zustimmung des Rechteinhabers.

Siehe [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) und [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
