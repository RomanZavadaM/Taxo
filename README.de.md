# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo ist eine Desktop-Anwendung für ein einzelnes Verkehrsunternehmen: Personal und Fahrer, Dienstpläne, Arbeitszeiterfassung, Fahrtenblätter, Tätigkeitsbestätigungen, Fahrzeuge, Dokumentenkontrolle, Berichte, Wartungsplanung und selektive Verarbeitung analoger Tachographenscheiben.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Neuester integrierter Checkpoint in `main`:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Neuester vollständiger Multi-Plattform-Checkpoint:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1).  
> **Vorherige Stable-/Rollback-Version:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.9-r9` wird nicht automatisch zur Stable-Version; die Stable-Promotion ist eine separate Entscheidung des Eigentümers.

## Downloads

### Aktueller integrierter Checkpoint — 10.9-r9

[START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/SHA256SUMS_v10_9_r9.txt) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)

10.9-r9 ist der neueste integrierte Code-Checkpoint. Dafür wurde ein START-Paket veröffentlicht; ein vollständiger Satz ausführbarer Pakete wurde für r9 nicht erneut veröffentlicht.

### Letzter vollständiger Multi-Plattform-Checkpoint — 10.9-r1

[Release 10.9-r1 mit Windows/macOS-Paketen](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) · [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r1/SHA256SUMS_v10_9_r1_ALL.txt)

Für den normalen Betrieb verwenden Sie ein fertiges Windows/macOS-Paket aus `v10.9-r1`. `START.bat` ist hauptsächlich für Tests und technische Diagnose gedacht; das START-ZIP muss vollständig entpackt werden.

Benutzerdatenbanken, SQLite-Dateien, Scans, Caches und personenbezogene Dokumente sind niemals Bestandteil der GitHub-Releases.

## Hauptfunktionen

- Personal- und Fahrerregister mit Rollen und Historie;
- individuelle und periodische Fahrerpläne;
- Arbeitszeittabellen mit geteilten Schichten und klarer Trennung von Plan und Ist;
- Kontrolle von Arbeit, Lenkzeit, Pausen und Ruhezeit;
- 60-Tage-Aktivitätsregister ohne erfundenen Ruhezeitanteil aus unbekannter Zeit;
- Fahrzeugregister, Kilometerstand, Wartungsplanung und Dokumentenkontrolle;
- reguläre und nicht regelmäßige Fahrtenblätter;
- Tätigkeitsbestätigungen mit Revisionshistorie;
- analoge Tachographenscheiben mit manueller Prüfung;
- Schutz genehmigter/unterzeichneter Betriebsanordnungen und Fahrer→Fahrzeug-Zuordnungen;
- PDF-/Excel-Berichte;
- Sicherungen, Arbeitsbereichsübertragung und SQLite-Schema-Kompatibilitätskontrolle.

## In 10.9-r2 → 10.9-r9 integriert

Diese integrierte Linie enthält unveränderliche Historie für Fahrtenblattnummern, Gültigkeitsprüfung von Fahrzeugdokumenten über die gesamte Fahrt, stärkere Arbeits-/Ruhezeitkontrolle, sicherere Priorität tatsächlicher Datenquellen, historische Personal-/P-5-Korrekturen, robustere Kilometer- und Wartungsprognosen, unveränderliche genehmigte/unterzeichnete Anordnungen sowie die erste explizite SQLite-Schema-Basis über `PRAGMA user_version`.

Vollständige Hinweise: [Release Notes 10.9-r9](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [Release-Index](docs/releases/RELEASE_INDEX.md).

## Staatliche Register und militärische Buchhaltung

Taxo unterstützt den Fahrzeugabgleich mit „Shlyakh“, editierbare Arbeitswerte getrennt von unveränderlichen staatlichen Snapshots, ein Mitarbeiterdokumentenregister, verlustfreien XLSX-Import und einen lokalen Diia-first-Ablauf für den jährlichen Personalabgleich.

Taxo **ersetzt keine staatliche API** und behauptet keine automatische Übermittlung an Diia, Oberih oder Shlyakh.

## Dokumentation und Entwicklungsstand

Die kanonische Betriebsdokumentation wird auf Ukrainisch gepflegt. Neue Entwicklungs-/Recovery-Sitzungen beginnen mit `START_HERE.md`, danach `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` und Issue #61. Bereits ausgegebene Revisionen sind unveränderlich. Nach `10.9-r9` ist die nächste Code-Revision **10.9-r10**.

Siehe [Dokumentationsübersicht](docs/README.md) · [Systemübersicht](docs/SYSTEM_OVERVIEW.md) · [Produktstatus](docs/PRODUCT_STATUS.md) · [Schnellstart](docs/guides/QUICK_START.md) · [Release-Index](docs/releases/RELEASE_INDEX.md).

## Urheberrecht und Lizenz

**Copyright © 2026 Roman Zavada (Роман Завада). Alle Rechte vorbehalten.**

Taxo ist proprietäre Software. Die öffentliche Sichtbarkeit dieses Repositorys gewährt keine Open-Source-Lizenz und keine Erlaubnis zur Weiterverbreitung, zum Verkauf, zur Wiederveröffentlichung oder zur Verbreitung geänderter/abgeleiteter Versionen ohne schriftliche Zustimmung des Rechteinhabers.

Siehe [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) und [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
