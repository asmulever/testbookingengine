# PR 1 - Filtro de Habitaciones

## Objetivo de negocio
Incorporar un mecanismo de búsqueda en la sección **Habitaciones** para mejorar la localización de cuartos por nombre y reducir tiempo operativo en front desk/soporte.

## Alcance implementado
- Se agregó un formulario de filtro por nombre en la vista de Habitaciones.
- El filtro opera por coincidencia parcial (`icontains`) sobre `Room.name`.
- Se mantiene el comportamiento original cuando no hay criterio de búsqueda (listado completo).
- Se agregó estado vacío cuando no existen coincidencias.
- Se mejoró la presentación de los controles de búsqueda para una experiencia más clara y consistente.

## Cambios funcionales y técnicos
1. **Backend**
- Se actualizó la lógica de `RoomsView` para aceptar parámetro `name` y filtrar resultados.
- Se agregó un formulario dedicado de filtro para desacoplar validación y render.

2. **Frontend**
- Se incorporó barra de filtro con input, botón de búsqueda y acción de limpieza.
- Se añadió feedback contextual del total de resultados.
- Se mejoró el layout visual del bloque de controles para reforzar jerarquía y legibilidad.

3. **Calidad**
- Se incorporaron pruebas automatizadas que validan:
  - listado completo sin filtro,
  - filtro por coincidencia parcial,
  - estado sin resultados.

## Archivos modificados
- `pms/forms.py`
- `pms/views.py`
- `pms/templates/rooms.html`
- `pms/statics/css/style.css`
- `pms/tests.py`

## Pruebas ejecutadas
- `python manage.py test pms.tests.RoomsFilterTests`

## Resultado esperado para el producto
- Menor fricción en operación diaria al buscar habitaciones.
- Mejor percepción de calidad UI en una pantalla de uso frecuente.
- Base funcional y visual estable para iteraciones futuras en catálogo/gestión de habitaciones.
