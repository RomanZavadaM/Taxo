# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo es un sistema de escritorio para una sola empresa de transporte: personal y conductores, horarios, control del tiempo de trabajo, hojas de ruta, formularios de confirmación de actividad, vehículos, control documental, mantenimiento, informes y verificación de discos de tacógrafo analógico.

> **Estable:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — verificada con datos reales
> **Estable anterior / reversión:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Línea de pruebas:** [10.10-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) (versión preliminar, en verificación con datos reales)

## Descargas — Taxo 10.9-r10 (estable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Notas de la versión 10.9-r10 (ucraniano)](../releases/RELEASE_NOTES_v10.9-r10.md) · [Índice de versiones](../releases/RELEASE_INDEX.md)

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

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) son versiones preliminares para verificar con datos reales: sin PyMuPDF, versión correcta en la ventana, aviso de copia solo de BD, refuerzo de CI. Solo serán estables tras la verificación del propietario.

## Desarrollo

La documentación operativa canónica se mantiene en ucraniano. Empiece por [`START_HERE.md`](../../START_HERE.md). El código en `main` es la línea de pruebas 10.10; la próxima revisión de código es `10.10-r4`.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo es software propietario.
