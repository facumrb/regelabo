# 031 — Cambio obligatorio después de una contraseña temporal

**Fecha:** 2026-11-16 · **Estado:** aceptada

Amplía la [018](018-cambio-de-contrasena.md) (cambio de contraseña) y la [028](028-panel-de-administracion.md) (contraseña temporal del panel).

## Contexto
- El panel de admin genera una contraseña temporal y el admin se la manda al usuario por mail; el comando `resetear_contrasena` hace lo mismo con una que escribe el admin. En los dos casos **un admin conoce la contraseña**.
- Hasta ahora el usuario podía seguir usándola para siempre. Además, para cambiarla en *Mi cuenta* tenía que copiar la temporal del mail como "contraseña actual".

## Decisión
- Columna `usuario.debe_cambiar_contrasena`. La marca `resetear_contrasena` (panel y comando); cualquier otro cambio de contraseña la borra.
- **Bloqueo también en la API:** con la marca, todos los endpoints con sesión responden 403 `debe_cambiar_contrasena`, salvo `GET /api/auth/yo`, `POST /api/auth/logout` y el de elegirla. Lo resuelve la dependencia `usuario_actual`; `usuario_con_sesion` es la variante sin la regla.
- **Sin pedir la actual:** `POST /api/auth/contrasena-temporal` con solo la nueva (mismas reglas de largo, distinta de la temporal, límite de 5 por minuto). Solo funciona con la marca puesta (409 `sin_contrasena_temporal` si no). Mantiene la sesión actual y cierra las demás.
- **Frontend:** con la marca, cualquier ruta redirige a `/elegir-contrasena` (nueva dos veces, con "Cerrar sesión" como salida).

## Alternativas descartadas
- **Redirigir solo en la pantalla:** se esquiva llamando a la API directo con la sesión de la temporal.
- **Pedir la temporal otra vez:** el usuario acaba de entrar con ella; obliga a copiarla del mail dos veces sin ganar seguridad.
- **Solo para el panel, no para el comando:** con el comando el admin también conoce la contraseña.
- **Vencimiento de la temporal:** más reglas para el mismo objetivo; al obligar el cambio en el primer ingreso, la temporal deja de servir apenas se usa.

## Consecuencias
- Migración `e5c3a9b1d7f2` (las cuentas existentes quedan sin marca).
- `UsuarioPublico` suma `debe_cambiar_contrasena`; el frontend lo refleja en `services/auth.ts`.
- Un admin al que se le resetea la contraseña por comando también tiene que elegir una nueva al entrar.
