# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo es una aplicación de escritorio para empresas de transporte: personal y vehículos, turnos y tiempo de trabajo, hojas de ruta, órdenes, documentos, mantenimiento, informes y copias de seguridad.

## Stable 10.24-r3

**10.24-r3 fue promovida a Stable/Latest por decisión explícita del propietario el 23 de noviembre de 2026.** Incluye todas las funciones aceptadas de 10.23-r4 y la línea de correspondencia r1–r3 terminada: registros Entrada/Salida, numeración segura, adjuntos controlados, búsqueda, fecha/calendario, tablas ordenables, ficha del correo y acciones para crear, responder, gestionar adjuntos y abrir documentos. Una fecha de envío vacía no significa «enviado».

37 rutas UI live estrictas comprueban visibilidad, posición en pantalla, usabilidad y activación. START, Windows, Windows 7 y macOS Intel/Apple Silicon superaron las pruebas; Windows/Win7 también superaron Defender e integridad. La cobertura completa (#556) y la auditoría integral más amplia de órdenes (#553) siguen abiertas.

## Descargas

**Stable / Latest: [Taxo 10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).** Versión estable anterior: [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/Taxo_v10_24_candidate_r3_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/SHA256SUMS_v10_24_r3.txt)

**Current Test:** [Taxo 10.24-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r8), prerelease de 8 archivos, exact source `d24b1bc96115de52d6088813992aca3b410fe243`. Esta revisión solo de control añade sobre r7 una garantía de reapertura completa de la interfaz: la misma orden persistida conserva número/fecha/asunto/estado y rol/nota de participantes; Draft → Active no modifica el frozen participant snapshot ni la secuencia, y el refresh de la misma orden conserva la selección. Siguen activos los controles r7 de add/edit/remove, live preview, DOCX/PDF y full backup/restore. Taxo mantiene 58 strict live routes y el contrato de correspondencia sigue siendo exactamente de 17 routes. Stable/Latest permanece en 10.24-r3.

Guarde bases y documentos en una carpeta de trabajo separada y haga una copia antes de actualizar. [Manual de usuario (ucraniano)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

Desarrollo: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). Todos los derechos reservados. [LICENSE](../../LICENSE.md).
