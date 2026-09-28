# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo es una aplicación de escritorio para una empresa de transporte: personal y conductores, horarios, control de jornada, hojas de ruta, certificados de actividad, vehículos, control documental, informes y procesamiento selectivo de discos de tacógrafo analógicos.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Último checkpoint completo en `main`:** [Taxo 10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8).  
> **Stable anterior / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.5-r8` es un candidate/checkpoint completo y no se convierte en stable sin una decisión separada del propietario.

## Descargas 10.5-r8

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/SHA256SUMS_v10_5_r8.txt)

Las bases de datos de usuario, archivos SQLite, escaneos, cachés y documentos personales nunca se incluyen en los releases de GitHub.

## Funciones principales

- registro de personal y conductores con roles e historial;
- horarios individuales y periódicos de conductores;
- hojas de horas con turnos divididos y separación explícita entre plan y real;
- control de trabajo, conducción, pausas y descanso;
- balances semanales separados de **60:00 de trabajo** y **56:00 de conducción**;
- registro de actividad de 60 días con detalle por minuto;
- registro de vehículos, historial de kilometraje y control de documentos;
- seguro, seguro adicional de responsabilidad, inspección técnica, documentos de matriculación y protocolo de inspección del tacógrafo;
- rutas y escenarios horarios;
- hojas de ruta, certificados de actividad e informes PDF/Excel;
- discos de tacógrafo analógicos con verificación manual;
- espacio de trabajo configurable, copias de seguridad y traslado de datos.

## Registros y contabilidad militar en la línea 10.5

La línea 10.5 añadió conciliación de vehículos con datos de “Shlyakh”, valores de trabajo editables separados de snapshots estatales inmutables, un registro unificado de documentos de empleados, importación XLSX sin pérdida, una relación empresarial de transporte militar y un flujo local Diia-first para la conciliación anual del personal.

Taxo **no sustituye una API estatal**. La preparación local no se considera un hecho oficial y la aplicación no afirma transmitir automáticamente datos a Diia, Oberih o Shlyakh.

## Cambio en 10.5-r8

En Windows 7 / Python 3.8 openpyxl puede devolver para algunos XLSX de Shlyakh el error corto `unexpected keyword argument 'tabId'` sin la palabra `ChildSheet`. r8 reconoce ese caso concreto, reintenta sobre una copia en memoria y no modifica el XLSX de origen.

Notas completas: [Release notes 10.5-r8](docs/releases/RELEASE_NOTES_v10_5_r8.md).

## Documentación

La documentación operativa canónica se mantiene en ucraniano:

- [Índice de documentación](docs/README.md)
- [Descripción del sistema](docs/SYSTEM_OVERVIEW.md)
- [Inicio rápido](docs/guides/QUICK_START.md)
- [Manual de personal](docs/guides/USER_MANUAL.md)
- [Administración y copias de seguridad](docs/guides/ADMIN_GUIDE.md)
- [Solución de problemas](docs/guides/TROUBLESHOOTING.md)
- [Índice de releases](docs/releases/RELEASE_INDEX.md)

## Estado de desarrollo

Las nuevas sesiones deben empezar por `START_HERE.md`, después `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` e Issue #61.

Cada paso completado recibe una nueva revisión `r1 … r10`; después de `r10` aumenta la versión minor y la revisión vuelve a `r1`. Las revisiones publicadas son inmutables. Después de `10.5-r8`, la siguiente revisión de código es **10.5-r9**.

## Derechos de autor y licencia

**Copyright © 2026 Roman Zavada (Роман Завада). Todos los derechos reservados.**

Taxo es software propietario. La visibilidad pública del repositorio no concede una licencia de código abierto ni permiso para redistribuir, vender, volver a publicar o distribuir versiones modificadas/derivadas sin autorización escrita del titular de los derechos.

Consulte [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
