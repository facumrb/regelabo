# 015 — Interfaz de autenticación y primeros pasos en TypeScript

**Fecha:** 2026-10-14 · **Estado:** aceptada

## Contexto
Antes de seguir con el módulo de Casos se quiso una interfaz mínima para verificar a mano el registro, el login, la sesión y los límites del backend.

## Decisión
- **Páginas propias** `/login` y `/registro` con `react-router-dom`, y dos botones a la derecha del navbar: *Iniciar sesión* (secundario) y *Registrarse* (primario). Con sesión, el navbar muestra el usuario (con insignia `admin` si corresponde) y *Cerrar sesión*.
- **TypeScript para el código nuevo** (`.tsx`/`.ts`), con `allowJs` para convivir con los `.jsx` del prototipo (migrado después, ver decisión 012). Script `pnpm run typecheck`.
- **Estado de sesión** en un contexto de React (`SesionContext`): al cargar la página pide `GET /api/auth/yo` para recuperar la sesión.
- **Panel de pruebas** (solo con `import.meta.env.DEV`): registra los pedidos a `/api/auth/*` con lo enviado y lo respondido, oculta las contraseñas y explica cómo leerse. No existe en producción.
- **Los formularios no validan en el navegador** (`noValidate`): todo llega al servidor, que es el dueño de las reglas.
- El prototipo de simulación y audiogramas sigue en la ruta `/`, sin cambios.

## Alternativas descartadas
- **Ventanas modales:** más rápidas, pero el equipo prefirió páginas propias.
- **JSX para esta interfaz:** habría que reescribirla al migrar a TypeScript.

## Consecuencias
- Se adelanta `react-router`, previsto para el módulo de Casos.
- **Al desplegar**, Caddy tiene que devolver `index.html` para cualquier ruta que no sea `/api` (si no, recargar `/login` da 404).
- Pendiente: las pantallas de administración, y proteger las rutas del prototipo.
