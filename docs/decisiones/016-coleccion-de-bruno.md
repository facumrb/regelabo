# 016 — Colección de Bruno para la API

**Fecha:** 2026-10-14 · **Estado:** aceptada

## Contexto
Los 29 tests de `pytest` cubren la API, pero no sirven para explorarla a mano ni para enseñársela al equipo o a la cátedra. Se quiso un cliente gráfico de requests.

## Decisión
- **Bruno**, con la colección en `docs/api/`: archivos de texto versionados con el código, sin cuenta ni nube.
- Cubre la autenticación con su flujo feliz y los errores (`codigo` y estado HTTP), más el estado del backend. Las rutas del prototipo no se incluyen porque las van a reemplazar los módulos siguientes.
- La cookie de sesión se manda a mano en un header (variable `token`), para no depender del manejo de cookies de cada versión y poder probar un token viejo.
- Los casos que necesitan esperar (límite por IP, bloqueo de cuenta) van en una carpeta aparte, `3-manuales`.
- Se verificó con el cliente de terminal de Bruno (`@usebruno/cli`) contra una copia del backend aislada: 18 requests y 39 tests.

## Alternativas descartadas
- **Postman:** muchas funciones piden cuenta y las colecciones se comparten por su nube o como JSON.
- **Solo Swagger y curl:** no dejan aserciones ni requests guardadas.

## Consecuencias
- Una corrida completa gasta el límite de 5 pedidos por minuto de login y registro: hay que esperar un minuto entre corridas.
- Cada módulo nuevo tiene que sumar su carpeta de requests.
- No reemplaza a `pytest`; no está en la integración continua.
