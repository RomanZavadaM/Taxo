# Taxo v8.70 — Personal, horarios y hojas de ruta

[Українська](README.md) | [English](README.en.md) | [Deutsch](README.de.md) | **Español** | [Français](README.fr.md)

Taxo es una aplicación de escritorio en ucraniano para gestionar el personal de una empresa de transporte, los horarios de los conductores, el tiempo de trabajo, las rutas, los vehículos, los certificados de actividades, las hojas de ruta de autobuses y los registros de tacógrafos analógicos. El candidato de desarrollo actual es **v8.70 r8**.

## Funciones principales

- Registro único de empleados con números de personal, fechas de contratación y varias funciones, entre ellas conductor, médico, mecánico, despachador y cobrador.
- Horarios de conductores y partes mensuales con el tiempo de trabajo planificado separado del tiempo de conducción planificado. Una jornada puede dividirse en varios segmentos.
- Catálogos de rutas y vehículos. Cada ruta contiene un horario preciso y puede comenzar fuera del depósito, cruzar la medianoche, incluir descansos o pernoctaciones y terminar en otro día natural.
- Introducción simplificada del recorrido: basta con pegar dos columnas, `Punto | Hora`, para los sentidos de ida y vuelta. Los cambios de día y los límites de la ruta se calculan automáticamente; se conserva un editor detallado para los casos especiales.
- Hojas de ruta de autobús vectoriales, de dos páginas A4, basadas en el formulario n.º 1-AP. El conductor, el vehículo, la ruta y las horas planificadas proceden del horario. Los documentos de varios días muestran fechas reales y no marcadores internos `D+N`.
- Series y grupos de números oficiales con períodos de validez, numeración automática o manual, historial de revisiones y registro de anulaciones.
- Turnos de médicos y mecánicos. Sus nombres pueden incorporarse a la hoja de ruta, mientras que las firmas manuscritas y los campos reales, de combustible y de control que todavía se desconocen permanecen vacíos.
- Parte completo de todo el personal con copia y pegado de un día en varias fechas, acciones masivas de plan→real y limpieza, planificación segura de ocho horas solo en laborables vacíos, informes individuales Excel/PDF, control plan/real y balance mensual imprimible/editable. Los turnos nocturnos se reparten entre los días naturales.
- Lecturas opcionales del odómetro al inicio y al final en la hoja de ruta. Se imprimen, se acumulan por vehículo y solo generan avisos de coherencia sin bloquear; el historial queda preparado para una futura fuente `tachograph`.
- Cada escenario completo de ruta puede tener una distancia planificada opcional. Se imprime como plan en la hoja de ruta, permite prever el odómetro final y genera un aviso no bloqueante si la distancia real difiere en más de 10 km o del 10 %.
- Certificados de actividades en DOCX, PDF y JPG, además de copia de seguridad y restauración de los datos persistentes.
- Área de trabajo para discos de tacógrafo analógico con imágenes escaneadas, intervalos de actividad y comparación de la conducción real con el plan. Los datos reales del tacógrafo no sobrescriben el horario planificado.

## Ejecución y almacenamiento de datos

En Windows, el paquete de código fuente puede iniciarse con `START.bat`. GitHub Actions genera paquetes Windows Setup y Portable, así como paquetes nativos de macOS para Apple Silicon e Intel, en los puntos de control ejecutables.

El instalador de Windows, el ZIP portátil, el ZIP del código fuente y las sumas SHA-256 actuales están disponibles en la [versión v8.70 de GitHub](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70).

La aplicación guarda los datos del usuario fuera de la carpeta del programa, en `Documents/DriverWorktime`. Las bases SQLite y los datos personales se excluyen deliberadamente del repositorio y de todos los paquetes de distribución; por tanto, una actualización del programa no sustituye los datos operativos.

La interfaz y los formularios oficiales generados están actualmente en ucraniano. Esta traducción facilita la presentación internacional del proyecto.

## Estado del proyecto

v8.70 r8 es el candidato de desarrollo activo sobre la base r7 publicada. Las ramas anteriores se conservan como puntos de control históricos. Antes de su uso operativo, la aplicación todavía debe validarse con datos reales de la empresa y con formularios impresos.
