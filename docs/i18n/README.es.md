# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo es una aplicación de escritorio para empresas de transporte: personal y vehículos, turnos y tiempo de trabajo, hojas de ruta, órdenes, documentos, mantenimiento, informes y copias de seguridad.

## Stable 10.23-r4

**10.23-r4 fue aceptada manualmente por el propietario el 20 de noviembre de 2026 y es Stable/Latest.** Incluye búsqueda, filtros, ordenación, árboles por tipo/fecha y carpetas propias anidadas, revisiones Word controladas, PDF/impresión, DocumentVault, escaneos en papel opcionales y estado de firma en papel por separado. Las órdenes permiten pares conductor–vehículo explícitos, editar pares existentes, editar rol/nota y conservar la selección durante las búsquedas. Las áreas de trabajo de documentos y el ancho del árbol del catálogo son ajustables. Las acciones DOCX/PDF/JPG del visor de órdenes permanecen accesibles en ventanas estrechas, incluso 760×560.

37 rutas UI live estrictas comprueban visibilidad, posición en pantalla, usabilidad y activación. START, Windows, Windows 7 y macOS Intel/Apple Silicon superaron las pruebas; Windows/Win7 también superaron Defender e integridad. La cobertura completa (#556) y la auditoría integral más amplia de órdenes (#553) siguen abiertas.

## Descargas

**Stable / Latest: [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** Versión estable anterior: [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Current Test:** [Taxo 10.23-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r9), prerelease de 8 archivos, exact source `9f41c46a4745815cfc7518f7319f6c6f941ba559`. Añade una capa ANALYZE→PROPOSE de solo lectura sobre el lote verificado de r8: propuestas deterministas de fecha, número, tipo, categoría y título descriptivo, cada una con confianza y motivo. Las ambigüedades pasan a needs_review, los metadatos estructurados existentes no se sobrescriben y los archivos fuente no se vuelven a abrir. Sin OCR, IA externa, APPLY, escritura en DocumentVault/BD ni ordenación física; Stable/Latest sigue siendo 10.23-r4.

Guarde bases y documentos en una carpeta de trabajo separada y haga una copia antes de actualizar. [Manual de usuario (ucraniano)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Desarrollo: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). Todos los derechos reservados. [LICENSE](../../LICENSE.md).
