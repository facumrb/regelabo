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
