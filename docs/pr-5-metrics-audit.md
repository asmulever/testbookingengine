# PR 5 - Auditoria Operativa y Metricas Comparativas

## Objetivo
Elevar la seccion de metricas a una experiencia de auditoria operativa util para negocio y liderazgo tecnico, permitiendo analisis diario/mensual, lectura rapida de tendencias y comparacion entre periodos sin salir del flujo principal.

## Alcance implementado
- Renombre funcional en navegacion: `Metricas` -> `Auditoria`.
- Rediseno de la seccion hacia un layout ejecutivo, con:
  - Cabecera de contexto operativo (fecha de corte).
  - KPIs principales del dia con variacion porcentual.
  - Vistas por periodo (diaria, mensual y combinada).
  - Widgets configurables para tabla, barras y resumen ejecutivo.
- Nuevos indicadores procesados en backend:
  - Tasa de cancelacion (diaria y mensual).
  - Ticket promedio (diario y mensual).
  - Pico de facturacion (dia y mes).
  - Acumulados de facturacion para ventanas de analisis.
- Visualizacion comparativa sin librerias externas:
  - Barras normalizadas para reservas creadas y facturacion.
  - Lectura rapida para detectar picos/caidas.
- Ajuste de pruebas para reflejar la nueva narrativa de pantalla.

## Archivos modificados
- `pms/templates/main.html`
- `pms/templates/metrics_audit.html`
- `pms/views.py`
- `pms/statics/css/style.css`
- `pms/tests.py`

## Detalle tecnico por componente
### Navegacion
Se actualiza el label del item en toolbar a `Auditoria`, alineado con el objetivo de negocio de la funcionalidad.

### Backend (procesamiento)
La vista `MetricsAuditView` incorpora calculos adicionales para enriquecer la toma de decisiones:
- porcentajes normalizados para visualizaciones de barras,
- metricas derivadas (rate/avg/peak),
- agregados diarios y mensuales listos para presentacion.

### Frontend (UX/UI)
Se implementa una interfaz mas orientada a analitica operativa:
- controles de vista por periodo,
- selector de widgets visibles,
- bloques de resumen ejecutivo,
- tablas y barras para analisis comparativo,
- comportamiento responsive para desktop y mobile.

### Calidad y mantenibilidad
La solucion reutiliza datos existentes del dominio `Booking` y evita dependencias adicionales, manteniendo bajo costo de mantenimiento y facil evolucion futura.

## Pruebas ejecutadas
- `python manage.py test pms.tests.MetricsAuditTests`
- Resultado: **OK (3/3)**

## Impacto esperado
- Mayor velocidad para identificar cambios de comportamiento operativo.
- Mejor soporte para conversaciones de negocio (ingresos, cancelacion, tendencia).
- Base solida para evolucionar a widgets avanzados (forecast, cohortes, alertas).

## Proposed Next Iteration (English)
- Add date-range presets (`Today`, `Last 7 days`, `Month to date`, `Last 90 days`) with URL persistence for shareable views.
- Include room-type segmentation to compare demand and cancellation behavior across categories.
- Add threshold-based alerts (for example: cancellation rate > X%) to surface risks proactively.
- Provide CSV export for table datasets to support external analysis and stakeholder reporting.
- Introduce trend forecasting (simple moving average) to estimate short-term bookings and revenue.
