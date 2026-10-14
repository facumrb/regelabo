# 005 — Cola de simulaciones en la base de datos

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
Una simulación tarda ~75 s en una notebook (i7 de 11.ª gen.) y se estiman entre 1,5 y 2,5 min en el servidor; usa ~1,1 GB de RAM y un solo núcleo. Un pedido HTTP que espera minutos lo corta el proxy.

## Decisión
La tabla `simulacion` tiene un campo `estado` (en_cola, ejecutando, completada, error). Un **proceso worker** toma las tareas con `SELECT … FOR UPDATE SKIP LOCKED`, que permite varios workers en paralelo sin que dos tomen la misma. El frontend consulta el estado cada pocos segundos (polling).

## Alternativas descartadas
- **Celery + Redis:** dos piezas más que configurar y vigilar en un servidor gratuito.
- **Esperar con el pedido abierto:** lo corta el proxy y bloquea al usuario.
- **WebSocket:** más complejidad que el polling, para el mismo resultado visible.

## Consecuencias
- Escalar es levantar más workers.
- Se puede pasar a Celery más adelante sin tocar la capa de negocio.
