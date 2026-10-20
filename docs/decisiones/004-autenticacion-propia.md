# 004 — Autenticación propia

**Fecha:** 2026-10-13 · **Estado:** aceptada (la sesión se reemplazó por [013](013-sesion-en-el-servidor.md))

## Contexto
El TPI exige contraseñas guardadas con hash, que el sistema funcione en una ventana normal y en una de incógnito de forma independiente (tokens o cookies) y errores HTTP. Con Supabase Auth las contraseñas no pasan por nuestro código, y eso es difícil de demostrar en la corrección.

## Decisión
Tabla `usuario` propia, contraseña con hash **argon2** y sesión en una **cookie que JavaScript no puede leer** (ver 013: token aleatorio, no JWT). Frontend y API se sirven bajo el mismo dominio (Caddy), así la cookie funciona sin pelear con CORS.

## Alternativas descartadas
- **Supabase Auth:** no permite mostrar el hash ni la lógica en nuestra capa de negocio.

## Consecuencias
- Limitación de intentos de login y bloqueo de cuenta a cargo nuestro (ver `docs/reglas-de-negocio.md`).
