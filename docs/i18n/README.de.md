# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo ist eine Desktop-Anwendung für Verkehrsunternehmen: Personal und Fahrzeuge, Dienstpläne und Arbeitszeit, Fahrtblätter, Anordnungen, Dokumente, Wartung, Berichte und Sicherungen.

## Stable 10.23-r4

**10.23-r4 wurde am 20.11.2026 vom Eigentümer manuell angenommen und ist Stable/Latest.** Enthalten sind Dokumentensuche, Filter, Sortierung, Typ-/Datumsbäume und eigene verschachtelte Ordner, kontrollierte Word-Revisionen, PDF/Druck, DocumentVault, optionale Papierscans und ein getrennt erfasster Papierunterschriftsstatus. Anordnungen unterstützen eindeutige Fahrer–Fahrzeug-Paare, die Bearbeitung vorhandener Paare, Rollen-/Notizbearbeitung und eine Auswahl, die beim Suchen erhalten bleibt. Dokument-Arbeitsbereiche und die Breite des Katalogbaums sind verstellbar. Die DOCX/PDF/JPG-Aktionen im Anordnungsfenster bleiben auch bei kleinen Fenstern bis 760×560 erreichbar.

37 strenge Live-UI-Pfade prüfen Sichtbarkeit, Bildschirmposition, Nutzbarkeit und Aktivierung. START, Windows, Windows 7 und macOS Intel/Apple Silicon waren erfolgreich; Windows/Win7 bestanden zusätzlich Defender- und Integritätsprüfungen. Die vollständige Funktionsabdeckung (#556) und der breitere End-to-End-Test der Anordnungen (#553) bleiben offen.

## Downloads

**Stable / Latest: [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** Vorheriger stabiler Stand: [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Current Test:** [Taxo 10.24-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r1), Prerelease mit 8 Dateien, exact source `adb6ae40e966d77018c6dc8c1c4fdcbde6a6a827`. Es startet das Modul für Geschäftskorrespondenz mit getrennten Ein-/Ausgangsjournalen, unabhängiger jährlicher Nummerierung, getrennten Registrierungs-/Dokument-/Empfangs-/Sendedaten, Korrespondent/Betreff/Kontroll-Metadaten, expliziten Antwortbeziehungen und stabilen Dokumentverweisen ohne Byte-Kopien. Das Register wird durch das vollständige Workspace-Backup/Restore erhalten. Noch keine Korrespondenz-UI, kein Attachment-Store und kein automatischer E-Mail-Versand; Stable/Latest bleibt 10.23-r4.

Datenbanken und Dokumente in einem separaten Arbeitsordner speichern und vor Updates sichern. [Benutzerhandbuch (Ukrainisch)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Entwicklung: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). Alle Rechte vorbehalten. [LICENSE](../../LICENSE.md).
