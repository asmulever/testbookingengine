# PR 4 - Dark/Light Modes

## Objetivo de negocio
Incorporar un sistema de tema visual claro/oscuro con persistencia de preferencia del usuario para mejorar confort de uso, continuidad de experiencia y percepción de calidad del producto.

## Alcance implementado
- Se agregó selector de tema en la toolbar superior (a la derecha del botón **Buscar**).
- El selector alterna entre:
  - icono **sol** para modo claro,
  - icono **luna** para modo oscuro.
- La preferencia se persiste en cookie de navegador y se reaplica automáticamente al cargar la app.
- Se mantuvo la interfaz funcional original, encapsulando el cambio en capa visual/estilos.

## Cambios funcionales y técnicos
1. **Integración en layout principal**
- Se incorporó botón de toggle de tema en `main.html`.
- Se añadió inicialización temprana del tema para evitar parpadeo visual al cargar.

2. **Lógica de persistencia**
- Se creó script dedicado para:
  - leer preferencia desde cookie,
  - alternar tema,
  - actualizar cookie con duración anual.

3. **Sistema de estilos por tema**
- Se evolucionó `style.css` a un esquema basado en variables, con reglas para ambos modos.
- Se aseguró consistencia visual y contraste en componentes base sin modificar lógica de negocio.

4. **Criterio de estabilidad visual**
- Se preservaron colores originales de elementos clave solicitados (toolbar, estados críticos y widgets del dashboard) para mantener familiaridad operativa.

## Archivos modificados
- `pms/templates/main.html`
- `pms/statics/css/style.css`
- `pms/statics/js/theme_mode.js` (nuevo)

## Pruebas realizadas
- Validación funcional manual en navegador:
  - toggle claro/oscuro,
  - cambio de icono sol/luna,
  - persistencia de preferencia tras recarga.
- Verificación de configuración Django:
  - `python manage.py check`

## Resultado esperado para el producto
- Mejor ergonomía visual para diferentes contextos de trabajo (día/noche).
- Experiencia más moderna y adaptable, alineada a estándares de productos SaaS.
- Base de theming reutilizable para futuras evoluciones UI sin reescribir templates funcionales.
