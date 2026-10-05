# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo es un sistema de escritorio para una sola empresa de transporte: personal y conductores, horarios, control del tiempo de trabajo, hojas de ruta, formularios de confirmación de actividad, vehículos, control documental, mantenimiento, informes y verificación de discos de tacógrafo analógico.

> **Estable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 2026-10-05
> **Estable anterior / reversión:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Próxima revisión de código:** `10.10-r4`

## Descargas — Taxo 10.10 (estable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [Notas de la versión 10.10 (ucraniano)](../releases/RELEASE_NOTES_v10_10.md) · [Índice de versiones](../releases/RELEASE_INDEX.md)

Las bases de datos de trabajo, archivos SQLite, escaneos, cachés y documentos personales no se incluyen en las versiones de GitHub. La actualización no requiere volver a introducir los datos de trabajo.

## Novedades de 10.10

- **Sin PyMuPDF.** El formulario de confirmación de actividad (PDF/JPG), el sello de fecha del informe n.º 340 y la vista/impresión de PDF usan bibliotecas con licencias permisivas (pypdfium2, reportlab, pypdf); el resultado es idéntico píxel a píxel a la versión anterior.
- **Versión correcta en la aplicación** — título de la ventana, diálogo «Acerca de», encabezados PDF y manifiesto de copia de seguridad.
- **Las copias de seguridad** advierten explícitamente cuando solo contienen bases de datos.
- **Infraestructura:** flujos de publicación obsoletos desactivados, pruebas aisladas del almacenamiento de trabajo, control de licencias en cada compilación.
- Incluye toda la línea 10.4 … 10.9: validez de documentos del vehículo durante todo el viaje, protección de hojas de ruta y números emitidos, control reforzado de trabajo/descanso, registro de 60 días, balance de personal, mantenimiento, órdenes firmadas inmutables, compatibilidad del esquema SQLite.

## Funciones principales

Historial de personal y conductores; horarios individuales y periódicos; tiempo de trabajo plan/real y turnos partidos; control de trabajo, conducción, pausas y descanso; registro de actividad de 60 días; vehículos, kilometraje, mantenimiento y documentos; hojas de ruta regulares y no regulares; formularios de confirmación de actividad; verificación de tacógrafo analógico; órdenes protegidas y asignaciones conductor→vehículo; informes PDF/Excel; copias de seguridad y control de compatibilidad SQLite.

## Desarrollo

La documentación operativa canónica se mantiene en ucraniano. Empiece por [`START_HERE.md`](../../START_HERE.md). Tras la versión estable 10.10, el nuevo código empieza en `10.10-r4` desde el `main` actual. Las revisiones publicadas son inmutables.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo es software propietario.
