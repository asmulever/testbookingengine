# PR 2 - Dashboard Occupancy

## Objetivo de negocio
Incorporar un indicador operativo de ocupación para facilitar seguimiento diario del rendimiento comercial y de capacidad del hotel desde el dashboard principal.

## Alcance implementado
- Se agregó un nuevo widget `% ocupación` en Dashboard.
- El cálculo implementado sigue la regla definida para la prueba:
  - **reservas confirmadas / total de habitaciones**.
- Se contempló el caso borde sin habitaciones disponibles para evitar errores por división por cero.

## Cambios funcionales y técnicos
1. **Backend (cálculo de métrica)**
- En `DashboardView` se añadió:
  - conteo de reservas confirmadas (`state = NEW`),
  - conteo total de habitaciones,
  - cálculo de porcentaje de ocupación.
- Se expone el valor como `dashboard.occupancy_percentage` para consumo en template.

2. **Frontend (visualización)**
- Se agregó un quinto widget en la grilla de Dashboard para mostrar `% ocupación`.
- Se mantuvo la estructura de visualización existente y se integró el nuevo indicador en la misma jerarquía de información.

3. **Calidad**
- Se añadieron pruebas para validar:
  - cálculo correcto en escenario estándar,
  - resultado `0` cuando no hay habitaciones.

## Archivos modificados
- `pms/views.py`
- `pms/templates/dashboard.html`
- `pms/tests.py`

## Pruebas ejecutadas
- `python manage.py test pms.tests.DashboardOccupancyTests pms.tests.DashboardOccupancyWithoutRoomsTests`

## Resultado esperado para el producto
- Mayor visibilidad de capacidad utilizada.
- Señal temprana para decisiones de pricing, promociones o gestión de disponibilidad.
- Mejora del valor analítico del Dashboard sin incrementar complejidad operativa para el usuario final.
