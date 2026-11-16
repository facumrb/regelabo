# 009 — Roles, cupos y límites

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
Hay 3 tipos de usuario final (estudiante, investigador y fonoaudiólogo), y el servidor es modesto.

## Decisión
- **`tipo_perfil`** como dato del usuario: cambia textos de ayuda y cupos, no permisos.
- Rol técnico **admin**: administra usuarios y arquetipos; de los demás usuarios solo ve totales.
- **Cupos y límites** según RN5a, RN5b y RN5c. Se calculan contando filas de `simulacion` dentro de una transacción con bloqueo sobre el usuario (ver 010).
- **Límites de seguridad** con `slowapi`: login, registro y API en general.

## Alternativas descartadas
- **Permisos distintos por tipo de usuario:** traba a los usuarios sin aportar nada en una herramienta de estudio.
- **Tope diario en lugar de por hora:** el servidor cuesta lo mismo se use o no; lo que importa es no saturar la cola.

## Consecuencias
- `slowapi` guarda los contadores en memoria. Si hay varias instancias de la API, hay que configurarlo con Redis.

## Ajuste del 2026-11-16: límite general implementado
- 120 pedidos por minuto **por sesión** (la cookie; sin sesión, la IP), no por usuario: así no hace falta consultar la base en cada pedido, y en Codespaces, donde todos llegan desde la misma IP, no se castiga a todos juntos. Con varias sesiones abiertas el tope se multiplica.
- Va como dependencia global de la app (`limite_general` en `views/limites.py`), con los contadores de slowapi. Se descartó `SlowAPIMiddleware`: con FastAPI 0.143 no encuentra las rutas de los routers y las deja pasar sin límite.
- `/api/health` queda exenta. Las consultas automáticas del frontend suman unos 80 pedidos por minuto en el peor caso normal (3 simulaciones en curso y el detalle abierto); dos pestañas con eso a la vez pueden llegar al tope.
