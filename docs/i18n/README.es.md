# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo es un sistema de escritorio para una sola empresa de transporte: personal y conductores, horarios, control del tiempo de trabajo, hojas de ruta, formularios de confirmación de actividad, vehículos, control documental, mantenimiento, informes y verificación de discos de tacógrafo analógico.

> **Estable:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — verificada con datos reales
> **Estable anterior / reversión:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Candidato actual:** [Taxo 10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r4) — versión preliminar publicada; verificada en Windows 10/11, Windows 7, macOS Intel y Apple Silicon

## Descargas — Taxo 10.9-r10 (estable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Notas de la versión 10.9-r10 (ucraniano)](../releases/RELEASE_NOTES_v10.9-r10.md) · [Índice de versiones](../releases/RELEASE_INDEX.md)

## Descargas — Taxo 10.10-r4 (prueba / versión preliminar)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/Taxo_v10_10_candidate_r4_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10-r4/SHA256SUMS_v10_10_r4.txt)

Las bases de datos de trabajo, archivos SQLite, escaneos, cachés y documentos personales no se incluyen en las versiones de GitHub. La actualización no requiere volver a introducir los datos de trabajo.

## Contenido de la versión estable 10.9-r10

- historial permanente de hojas de ruta y números emitidos; la retención nunca borra hechos vinculados
- validez de los documentos del vehículo durante todo el viaje planificado
- control reforzado de trabajo/descanso: solapamientos, 3+9, descanso semanal y quincenal
- registro de 60 días sin descanso inventado; prioridad de las fuentes reales
- balance de personal / P-5, regímenes 2/2 y 3/3
- mantenimiento: cronología del odómetro y previsión de servicio
- órdenes aprobadas/firmadas y asignaciones conductor→vehículo inmutables
- control de compatibilidad del esquema SQLite
- código estructurado sin cambios en la lógica de negocio

## Versiones de prueba (no estables)

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) son versiones preliminares publicadas. **10.10-r4** corrige números de versión antiguos en todas las ventanas y recupera el instalador para Windows 7. Las compilaciones de Windows, Win7, macOS Intel y macOS ARM son correctas. La versión preliminar ya está publicada.

## Desarrollo

La documentación operativa canónica se mantiene en ucraniano. Empiece por [`START_HERE.md`](../../START_HERE.md). `10.10-r4` ya está en `main` y publicada como versión preliminar de prueba; la próxima revisión será `10.10-r5`.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo es software propietario.
