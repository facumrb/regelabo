# 013 — Sesión en el servidor

**Fecha:** 2026-10-14 · **Estado:** aceptada · **Reemplaza** el mecanismo de sesión de [004](004-autenticacion-propia.md)

## Contexto
La decisión 004 proponía un JWT en una cookie. Al implementarla se comparó con guardar la sesión en el servidor: cuestan casi lo mismo, y la segunda da un cierre de sesión real.

## Decisión
La cookie `sesion` (`httpOnly`, `SameSite=Lax`, ruta `/api`) guarda un **token aleatorio**. En la tabla `sesion` (la décima) solo se guarda su **hash SHA-256**, con el usuario y el vencimiento (12 horas desde el login, fijo). Cada pedido busca la sesión y trae al usuario. Las sesiones vencidas se borran al hacer login.

## Alternativas descartadas
- **JWT con duración fija:** un token robado sigue valiendo después del logout hasta que vence, y hay una clave (`SECRET_KEY`) que cuidar.
- **JWT corto + token de renovación:** más piezas para el mismo resultado visible.

## Consecuencias
- Logout y vencimiento se aplican al instante en el servidor; no hay clave de firma.
- Cada pedido autenticado consulta la base (con JWT también habría que hacerlo para recargar el usuario).
- Queda pendiente decidir si un admin puede cerrar las sesiones de otro usuario.
