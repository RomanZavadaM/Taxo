# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo es un sistema de escritorio para una empresa de transporte: personal y conductores, horarios, jornada laboral, hojas de ruta, certificados de actividad, vehículos, documentos, mantenimiento, informes y tacógrafos analógicos.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **Último checkpoint integrado en `main`:** **Taxo 10.9-r10**  
> **Último release multiplataforma completo publicado:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **Siguiente revisión de código:** `10.10-r1`

`10.9-r10` ya está integrado en `main`, pero no se publicó como un release público multiplataforma completo independiente. Para paquetes listos de Windows/macOS, utilice `v10.9-r9`.

## Descargas — 10.9-r9

**Windows 10/11:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip)

**Windows 7 SP1:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**Pruebas/código fuente:** [START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [Notas 10.9-r10](../releases/RELEASE_NOTES_v10.9-r10.md) · [Índice de releases](../releases/RELEASE_INDEX.md)

Las bases de datos de usuario, SQLite, escaneos, cachés y documentos personales no se incluyen en los releases de GitHub.

## Cambios en 10.9-r10

El repositorio se reorganizó sin cambiar la lógica de negocio: los módulos runtime pasaron a `src/taxo/`, las plantillas a `assets/` y las definiciones activas de empaquetado a `packaging/`. No se introdujo ninguna migración de datos de usuario.

## Funciones principales

Personal y conductores con historial; horarios individuales/periódicos; plan/real y turnos divididos; control de trabajo, conducción, pausas y descanso; registro de 60 días; vehículos, kilometraje, mantenimiento y documentos; hojas de ruta; certificados de actividad; tacógrafos analógicos; órdenes y asignaciones conductor→vehículo protegidas; informes PDF/Excel; copias de seguridad y compatibilidad SQLite.

## Desarrollo

La documentación canónica se mantiene en ucraniano. Punto de entrada: [`START_HERE.md`](../../START_HERE.md). Después de `10.9-r10`, el nuevo código comienza en `10.10-r1` desde el `main` actual. Las revisiones publicadas son inmutables.

**Copyright © 2026 Roman Zavada (Роман Завада). Todos los derechos reservados.** Taxo es software propietario.
