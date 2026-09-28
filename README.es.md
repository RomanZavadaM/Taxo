# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo es una aplicación de escritorio para una empresa de transporte: personal y conductores, horarios, control de jornada, hojas de ruta, certificados de actividad, vehículos, control documental, informes y procesamiento selectivo de discos de tacógrafo analógicos.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Último checkpoint completo en `main`:** [Taxo 10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3).  
> **Stable anterior / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.6-r3` es un candidate/checkpoint completo y no se convierte en stable sin una decisión separada del propietario.

## Descargas 10.6-r3

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/SHA256SUMS_v10_6_r3_FULL.txt)

Las bases de datos de usuario, archivos SQLite, escaneos, cachés y documentos personales nunca se incluyen en los releases de GitHub.

## Funciones principales

- registro de personal y conductores con roles e historial;
- horarios individuales y periódicos de conductores;
- hojas de horas con turnos divididos y separación explícita entre plan y real;
- control de trabajo, conducción, pausas y descanso;
- balances semanales separados de **60:00 de trabajo** y **56:00 de conducción**;
- registro de vehículos, kilometraje y control documental;
- rutas regulares y trabajos no regulares: encargos, servicios de traslado, ciudad, región, viajes interregionales y otros servicios puntuales;
- hojas de ruta, certificados de actividad e informes PDF/Excel;
- discos de tacógrafo analógicos con verificación manual;
- copias de seguridad y traslado de datos.

## Checkpoint 10.6-r3

El checkpoint incluye la corrección de la auditoría plan/real, el filtro predeterminado de vehículos inactivos, la emisión de hojas de ruta para trabajos no regulares sin exigir un `route_id` del catálogo y una ventana «Acerca de» adaptable. En una salida no regular la tabla de ruta permanece vacía, mientras que médico, mecánico, odómetro y kilometraje real se conservan cuando existe una fuente real en Taxo. Los hechos ausentes no se inventan a partir del plan.

Notas completas: [Release notes 10.6-r3](docs/releases/RELEASE_NOTES_v10_6_r3.md).

## Registros estatales y contabilidad militar

Taxo admite conciliación de vehículos con “Shlyakh”, valores de trabajo editables separados de snapshots estatales inmutables, registro de documentos de empleados, importación XLSX sin pérdida, relación empresarial de transporte militar y un flujo local Diia-first para la conciliación anual del personal.

Taxo **no sustituye una API estatal** ni afirma transmitir automáticamente datos a Diia, Oberih o Shlyakh.

## Documentación y desarrollo

La documentación operativa canónica se mantiene en ucraniano. Las sesiones nuevas empiezan por `START_HERE.md`, después `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` e Issue #61. Las revisiones publicadas son inmutables. Después de `10.6-r3`, la siguiente revisión de código es **10.6-r4**.

Consulte [Índice de documentación](docs/README.md) · [Descripción del sistema](docs/SYSTEM_OVERVIEW.md) · [Inicio rápido](docs/guides/QUICK_START.md) · [Índice de releases](docs/releases/RELEASE_INDEX.md).

## Derechos de autor y licencia

**Copyright © 2026 Roman Zavada (Роман Завада). Todos los derechos reservados.**

Taxo es software propietario. La visibilidad pública del repositorio no concede una licencia de código abierto ni permiso para redistribuir, vender, volver a publicar o distribuir versiones modificadas/derivadas sin autorización escrita del titular de los derechos.

Consulte [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
