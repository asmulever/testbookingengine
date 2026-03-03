# PR 3 - Edición de Fechas de Reserva

## Objetivo de negocio
Habilitar la edición de fechas de una reserva ya creada, manteniendo reglas de disponibilidad del inventario y evitando conflictos operativos por solapamientos.

## Alcance implementado
- Se agregó un nuevo acceso en Home para **Editar fechas** por reserva.
- Se implementó una nueva pantalla dedicada para editar `checkin` y `checkout`.
- Se agregó validación de disponibilidad sobre la habitación actual antes de persistir cambios.
- Se incorporó recálculo automático del total de la reserva tras modificar fechas.
- Se incluyó validación de rango máximo permitido para reservas.

## Cambios funcionales y técnicos
1. **Navegación y routing**
- Nueva ruta para edición de fechas:
  - `booking/<pk>/edit-dates`.
- Integración del nuevo acceso desde la lista de reservas.

2. **Lógica de aplicación**
- Se creó una vista específica para editar fechas, separada del flujo de edición de datos de contacto.
- Validaciones principales:
  - `checkout > checkin`.
  - límite de fechas permitido hasta `31/12/2026`.
  - bloqueo por solape en la misma habitación excluyendo la reserva en edición.
- Mensaje de negocio mostrado cuando no hay disponibilidad:
  - **“No hay disponibilidad para las fechas seleccionadas”**.

3. **Form y consistencia de datos**
- Se creó un formulario específico para edición de fechas.
- Se asegura render ISO en inputs de fecha (`YYYY-MM-DD`) para coherencia entre textbox y datepicker.

4. **Calidad**
- Se agregaron pruebas automatizadas para cubrir:
  - edición exitosa con disponibilidad,
  - render correcto de valores de fecha,
  - rechazo por solape,
  - rechazo por rango inválido.

## Archivos modificados
- `pms/forms.py`
- `pms/views.py`
- `pms/urls.py`
- `pms/templates/home.html`
- `pms/templates/edit_booking_dates.html`
- `pms/tests.py`

## Pruebas ejecutadas
- `python manage.py test pms.tests.EditBookingDatesTests`

## Resultado esperado para el producto
- Mayor flexibilidad operativa para atención al cliente post-reserva.
- Menor riesgo de sobreventa por validación consistente de disponibilidad.
- Mejora de confiabilidad del dato financiero al recalcular importe tras cambios de fechas.
