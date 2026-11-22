# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo est une application de bureau pour les entreprises de transport : personnel et véhicules, plannings et temps de travail, feuilles de route, ordres, documents, maintenance, rapports et sauvegardes.

## Stable 10.23-r4

**10.23-r4 a été validée manuellement par le propriétaire le 20 novembre 2026 et est Stable/Latest.** Elle comprend la recherche, les filtres, le tri, les arbres type/date et les dossiers personnalisés imbriqués, les révisions Word contrôlées, PDF/impression, DocumentVault, les scans papier facultatifs et un état de signature papier séparé. Les ordres gèrent des paires conducteur–véhicule explicites, leur modification, l’édition du rôle/de la note et la conservation de la sélection pendant la recherche. Les zones de travail des documents et la largeur de l’arbre du catalogue sont réglables. Les actions DOCX/PDF/JPG de l’aperçu d’ordre restent accessibles dans une fenêtre étroite, y compris 760×560.

37 parcours UI live stricts vérifient visibilité, position à l’écran, utilisabilité et activation. START, Windows, Windows 7 et macOS Intel/Apple Silicon ont réussi ; Windows/Win7 ont également passé Defender et les contrôles d’intégrité. La couverture complète (#556) et l’audit de bout en bout plus large des ordres (#553) restent ouverts.

## Téléchargements

**Stable / Latest : [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** Version stable précédente : [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Current Test :** [Taxo 10.23-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r9), prerelease de 8 fichiers, exact source `9f41c46a4745815cfc7518f7319f6c6f941ba559`. Elle ajoute une couche ANALYZE→PROPOSE en lecture seule au-dessus du lot r8 vérifié : propositions déterministes pour la date, le numéro, le type, la catégorie et un titre descriptif, avec confiance et justification. Les ambiguïtés passent en needs_review, les métadonnées structurées existantes ne sont pas écrasées et les fichiers source ne sont pas rouverts. Aucun OCR, AI externe, APPLY, écriture DocumentVault/BD ni tri physique ; Stable/Latest reste 10.23-r4.

Conservez les bases et documents dans un dossier de travail séparé et sauvegardez-le avant mise à jour. [Guide utilisateur (ukrainien)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Développement : [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). Tous droits réservés. [LICENSE](../../LICENSE.md).
