# Taxo v8.70 — Fahrpersonal, Dienstpläne und Fahrtenblätter

[Українська](README.md) | [English](README.en.md) | **Deutsch** | [Español](README.es.md) | [Français](README.fr.md)

Taxo ist eine ukrainischsprachige Desktop-Anwendung für die Verwaltung von Beschäftigten eines Verkehrsunternehmens, Fahrerplänen, Arbeitszeiten, Linien, Fahrzeugen, Tätigkeitsbescheinigungen, Bus-Fahrtenblättern und Aufzeichnungen analoger Fahrtenschreiber. Der aktuelle Entwicklungskandidat ist **v8.70 r8**.

## Wichtigste Funktionen

- Einheitliches Personalregister mit Personalnummern, Beschäftigungszeiträumen und mehreren Rollen, darunter Fahrer, Arzt, Mechaniker, Disponent und Schaffner.
- Fahrerpläne und monatliche Arbeitszeitnachweise mit getrennten Planwerten für Arbeitszeit und Lenkzeit. Ein Arbeitstag kann aus mehreren Abschnitten bestehen.
- Linien- und Fahrzeugverzeichnisse. Jede Linie enthält einen genauen Fahrplan, kann außerhalb des Betriebshofs beginnen, über Mitternacht hinausgehen, Ruhe- oder Übernachtungszeiten enthalten und an einem späteren Kalendertag enden.
- Vereinfachte Fahrplaneingabe: Für Hin- und Rückrichtung genügen zwei eingefügte Spalten, `Punkt | Uhrzeit`. Tageswechsel und Liniengrenzen werden automatisch ermittelt; für Sonderfälle bleibt ein detaillierter Editor verfügbar.
- Zweiseitige vektorbasierte A4-Fahrtenblätter für Busse nach Formular Nr. 1-AP. Fahrer, Fahrzeug, Linie und Planzeiten werden aus dem Dienstplan übernommen. Mehrtägige Dokumente zeigen reale Kalenderdaten statt interner `D+N`-Kennzeichnungen.
- Serien- und Nummernkreise für offizielle Fahrtenblätter mit Gültigkeitszeiträumen, automatischer oder manueller Nummerierung, Revisionsverlauf und Annullierungsprotokoll.
- Dienstpläne für Ärzte und Mechaniker. Ihre Namen können in das Fahrtenblatt übernommen werden; handschriftliche Unterschriften sowie unbekannte Ist-, Kraftstoff- und Kontrollfelder bleiben frei.
- Vollständiger Personalzeitnachweis mit Kopieren/Einfügen eines Tages auf mehrere Daten, Sammelaktionen für Plan→Ist und Löschen, sicherer Acht-Stunden-Planung nur für leere Werktage, individuellen Excel/PDF-Berichten, Plan/Ist-Kontrolle und druckbarer/bearbeitbarer Monatsbilanz für alle Beschäftigten. Nachtarbeit wird auf Kalendertage verteilt.
- Optionale Kilometerstände zu Beginn und Ende im Fahrtenblatt. Sie werden gedruckt, je Fahrzeug historisiert und nur für nicht blockierende Plausibilitätswarnungen verwendet; die Historie ist für eine spätere Quelle `tachograph` vorbereitet.
- Für jeden vollständigen Linienablauf kann eine optionale Planstrecke hinterlegt werden. Sie wird als Plan im Fahrtenblatt gedruckt, prognostiziert den Endkilometerstand und warnt unverbindlich bei mehr als 10 km oder 10 % Abweichung.
- Tätigkeitsbescheinigungen als DOCX, PDF und JPG sowie Sicherung und Wiederherstellung der dauerhaft gespeicherten Anwendungsdaten.
- Arbeitsbereich für analoge Fahrtenschreiberscheiben mit Scans, Tätigkeitsintervallen und Vergleich der tatsächlichen Lenkzeit mit dem Plan. Tachographen-Istwerte überschreiben keine Plandaten.

## Start und Datenspeicherung

Unter Windows kann das Quellpaket über `START.bat` gestartet werden. Windows-Setup- und Portable-Pakete sowie native macOS-Pakete für Apple Silicon und Intel werden an ausführbaren Kontrollpunkten über GitHub Actions erstellt.

Das aktuelle Windows-Setup, das Portable-ZIP, das Quellcode-ZIP und die SHA-256-Prüfsummen stehen im [GitHub-Release v8.70](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70) bereit.

Benutzerdaten werden außerhalb des Programmordners unter `Documents/DriverWorktime` gespeichert. SQLite-Datenbanken und personenbezogene Daten sind bewusst weder im Repository noch in den Distributionspaketen enthalten. Programmaktualisierungen ersetzen daher keine Betriebsdaten.

Die Benutzeroberfläche und die erzeugten amtlichen Formulare sind derzeit ukrainisch. Diese Übersetzung dient der internationalen Projektübersicht.

## Projektstatus

v8.70 r8 ist der aktive Entwicklungskandidat auf Grundlage der veröffentlichten r7-Version. Ältere Branches bleiben als historische Kontrollpunkte erhalten. Vor dem produktiven Einsatz sind weiterhin Prüfungen mit echten Unternehmensdaten und gedruckten Formularen erforderlich.
