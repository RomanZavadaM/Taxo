# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo ist eine Desktop-Anwendung für ein einzelnes Verkehrsunternehmen: Personal und Fahrer, Dienstpläne, Arbeitszeiterfassung, Fahrtenblätter, Tätigkeitsbestätigungen, Fahrzeuge, Dokumentenkontrolle, Berichte und selektive Verarbeitung analoger Tachographenscheiben.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Neuester vollständiger Checkpoint in `main`:** [Taxo 10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8).  
> **Vorherige Stable-/Rollback-Version:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.5-r8` ist ein vollständiger Candidate/Checkpoint und wird nicht ohne separate Entscheidung des Eigentümers zur Stable-Version.

## Downloads 10.5-r8

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/SHA256SUMS_v10_5_r8.txt)

Benutzerdatenbanken, SQLite-Dateien, Scans, Caches und personenbezogene Dokumente sind niemals Bestandteil der GitHub-Releases.

## Hauptfunktionen

- Personal- und Fahrerregister mit Rollen und Historie;
- individuelle und periodische Fahrerpläne;
- Arbeitszeittabellen mit geteilten Schichten und klarer Trennung von Plan und Ist;
- Kontrolle von Arbeit, Lenkzeit, Pausen und Ruhezeit;
- getrennte Wochenbilanzen für **60:00 Arbeitszeit** und **56:00 Lenkzeit**;
- 60-Tage-Aktivitätsregister mit minutengenauer Aufteilung;
- Fahrzeugregister, Kilometerhistorie und Dokumentenkontrolle;
- Versicherung, zusätzliche Haftpflichtversicherung, technische Prüfung, Zulassungsdokumente und Tachographen-Prüfprotokoll;
- Routen und Zeitszenarien;
- Fahrtenblätter, Tätigkeitsbestätigungen und PDF-/Excel-Berichte;
- analoge Tachographenscheiben mit manueller Prüfung;
- Arbeitsbereich, Sicherungen und Übertragung der Arbeitsdaten.

## Register- und militärische Buchhaltungsfunktionen der Linie 10.5

Die Linie 10.5 ergänzte den Fahrzeugabgleich mit „Shlyakh“, editierbare Arbeitswerte getrennt von unveränderlichen staatlichen Snapshots, ein einheitliches Mitarbeiterdokumentenregister, verlustfreien XLSX-Import, eine betriebliche militärische Fahrzeugaufstellung sowie einen lokalen Diia-first-Ablauf für den jährlichen Personalabgleich.

Taxo **ersetzt keine staatliche API**. Lokale Vorbereitung gilt nicht als offizieller staatlicher Vorgang, und die Anwendung behauptet keine automatische Übermittlung an Diia, Oberih oder Shlyakh.

## Änderung in 10.5-r8

Unter Windows 7 / Python 3.8 kann openpyxl bei bestimmten Shlyakh-XLSX-Dateien die kürzere Meldung `unexpected keyword argument 'tabId'` ohne `ChildSheet` ausgeben. r8 erkennt genau diesen Fall, verwendet eine In-Memory-Kompatibilitätskopie und verändert die Quelldatei nicht.

Vollständige Hinweise: [Release Notes 10.5-r8](docs/releases/RELEASE_NOTES_v10_5_r8.md).

## Dokumentation

Die kanonische Betriebsdokumentation wird auf Ukrainisch gepflegt:

- [Dokumentationsübersicht](docs/README.md)
- [Systemübersicht](docs/SYSTEM_OVERVIEW.md)
- [Schnellstart](docs/guides/QUICK_START.md)
- [Personalhandbuch](docs/guides/USER_MANUAL.md)
- [Administration und Sicherungen](docs/guides/ADMIN_GUIDE.md)
- [Fehlerbehebung](docs/guides/TROUBLESHOOTING.md)
- [Release-Index](docs/releases/RELEASE_INDEX.md)

## Entwicklungsstand

Neue Sitzungen beginnen mit `START_HERE.md`, danach `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` und Issue #61.

Jeder abgeschlossene Schritt erhält eine neue Revision `r1 … r10`; nach `r10` steigt die Minor-Version und die Revision beginnt wieder bei `r1`. Bereits ausgegebene Revisionen sind unveränderlich. Nach `10.5-r8` ist die nächste Code-Revision **10.5-r9**.

## Urheberrecht und Lizenz

**Copyright © 2026 Roman Zavada (Роман Завада). Alle Rechte vorbehalten.**

Taxo ist proprietäre Software. Die öffentliche Sichtbarkeit dieses Repositorys gewährt keine Open-Source-Lizenz und keine Erlaubnis zur Weiterverbreitung, zum Verkauf, zur Wiederveröffentlichung oder zur Verbreitung geänderter/abgeleiteter Versionen ohne schriftliche Zustimmung des Rechteinhabers.

Siehe [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) und [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
