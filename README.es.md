# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo es una aplicación de escritorio para una empresa de transporte: personal y conductores, horarios, control de jornada, hojas de ruta, certificados de actividad, vehículos, control documental, informes, mantenimiento y procesamiento selectivo de discos de tacógrafo analógicos.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Último checkpoint integrado en `main`:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Último checkpoint completo multiplataforma:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1).  
> **Stable anterior / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.9-r9` no se convierte automáticamente en stable; la promoción a stable requiere una decisión separada del propietario.

## Descargas

### Checkpoint integrado actual — 10.9-r9

[START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/SHA256SUMS_v10_9_r9.txt) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)

10.9-r9 es el checkpoint de código integrado más reciente. Tiene paquete START; no se volvió a publicar un juego completo de ejecutables para r9.

### Último checkpoint completo multiplataforma — 10.9-r1

[Release 10.9-r1 con paquetes Windows/macOS](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) · [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r1/SHA256SUMS_v10_9_r1_ALL.txt)

Para uso normal utilice un paquete preparado de Windows/macOS de `v10.9-r1`. `START.bat` está pensado principalmente para pruebas y diagnóstico técnico; extraiga completamente el ZIP START antes de ejecutarlo.

Las bases de datos de usuario, archivos SQLite, escaneos, cachés y documentos personales nunca se incluyen en los releases de GitHub.

## Funciones principales

- registro de personal y conductores con roles e historial;
- horarios individuales y periódicos de conductores;
- hojas de horas con turnos divididos y separación explícita entre plan y real;
- control de trabajo, conducción, pausas y descanso;
- registro de actividad de 60 días sin inventar descanso a partir de tiempo desconocido;
- registro de vehículos, kilometraje, mantenimiento y control documental;
- hojas de ruta regulares y no regulares;
- certificados de actividad con historial de revisiones;
- discos de tacógrafo analógicos con verificación manual;
- protección del historial de órdenes aprobadas/firmadas y asignaciones conductor→vehículo;
- informes PDF/Excel;
- copias de seguridad, traslado del espacio de trabajo y control de compatibilidad del esquema SQLite.

## Integrado en 10.9-r2 → 10.9-r9

La línea integrada añade historial inmutable de hojas de ruta y números, validación de documentos del vehículo durante todo el viaje, controles reforzados de trabajo/descanso, prioridad más segura de fuentes reales, correcciones históricas de personal/P-5, mayor seguridad en odómetro y previsión de mantenimiento, órdenes aprobadas/firmadas inmutables y la primera base explícita del esquema SQLite mediante `PRAGMA user_version`.

Notas completas: [Release notes 10.9-r9](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [Índice de releases](docs/releases/RELEASE_INDEX.md).

## Registros estatales y contabilidad militar

Taxo admite conciliación de vehículos con “Shlyakh”, valores de trabajo editables separados de snapshots estatales inmutables, registro de documentos de empleados, importación XLSX sin pérdida y un flujo local Diia-first para la conciliación anual del personal.

Taxo **no sustituye una API estatal** ni afirma transmitir automáticamente datos a Diia, Oberih o Shlyakh.

## Documentación y desarrollo

La documentación operativa canónica se mantiene en ucraniano. Las sesiones nuevas empiezan por `START_HERE.md`, después `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` e Issue #61. Las revisiones publicadas son inmutables. Después de `10.9-r9`, la siguiente revisión de código es **10.9-r10**.

Consulte [Índice de documentación](docs/README.md) · [Descripción del sistema](docs/SYSTEM_OVERVIEW.md) · [Estado del producto](docs/PRODUCT_STATUS.md) · [Inicio rápido](docs/guides/QUICK_START.md) · [Índice de releases](docs/releases/RELEASE_INDEX.md).

## Derechos de autor y licencia

**Copyright © 2026 Roman Zavada (Роман Завада). Todos los derechos reservados.**

Taxo es software propietario. La visibilidad pública del repositorio no concede una licencia de código abierto ni permiso para redistribuir, vender, volver a publicar o distribuir versiones modificadas/derivadas sin autorización escrita del titular de los derechos.

Consulte [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
