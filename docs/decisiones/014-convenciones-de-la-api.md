# 014 — Convenciones de la API y de los tests

**Fecha:** 2026-10-14 · **Estado:** aceptada

## Decisión
- **Todas las rutas cuelgan de `/api`** (Swagger en `/api/docs`). En desarrollo, Vite reenvía `/api` al backend; en producción lo hace Caddy. El navegador habla con un solo origen: la cookie funciona sin CORS y se eliminó el CORS abierto del prototipo.
- **Errores con código estable:** `{"detail": {"codigo": "email_ya_registrado", "mensaje": "..."}}`. El frontend decide qué mostrar según el código; el mensaje está en español. Los errores de validación (422) conservan el formato de FastAPI.
- **Los tests corren contra PostgreSQL real**, en una base aparte (`<nombre>_test`) que se crea sola con las migraciones de Alembic; los de reglas puras no usan base. Nunca tocan la base de desarrollo.
- **El paso de autenticación es solo backend:** las pantallas de login llegan con el módulo de ejemplo (Casos) y la migración a TypeScript. Los endpoints del prototipo (`/api/simulate`, `/api/audiogram/*`, `/api/profiles`) siguen **sin autenticación** hasta que los reemplacen los módulos de casos y simulación.
- El **primer admin** se crea con `uv run python -m backend.comandos.crear_admin`.

## Alternativas descartadas
- Sin prefijo y con CORS con credenciales para `localhost:5173`: dos orígenes en desarrollo, distinto de producción.
- Mensajes de error como texto suelto: el frontend tendría que comparar textos.
- Tests con SQLite: no prueban bloqueos ni concurrencia, que necesitan las reglas de cupo y la cola.
- Admin por variables de entorno (la contraseña quedaría en un archivo) o con SQL a mano.

## Consecuencias
- Los endpoints del prototipo ya piden sesión (decisión 019).
- El límite de pedidos (slowapi) necesita que el servidor lea la IP real del cliente desde Caddy; si no, todos los usuarios comparten el mismo límite.
- Con `COOKIE_SECURE=true` (el valor por defecto) la cookie solo viaja por HTTPS.
