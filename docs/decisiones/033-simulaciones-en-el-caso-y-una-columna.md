# 033 — Simulaciones en la ficha del caso y ficha en una columna

**Fecha:** 2026-11-17 · **Estado:** aceptada

Cambia el diseño de la ficha del caso de la [024](024-rediseno-de-la-interfaz.md) y suma la lista de simulaciones a la ficha del caso de la [032](032-audiogramas-en-el-caso.md).

## Contexto
- En Nueva simulación, el selector de caso no mostraba un caso creado después de iniciar la sesión: la lista se pedía una sola vez. Si se llegaba desde el audiograma del caso, el caso sí quedaba elegido, pero el selector mostraba "Sin caso".
- La simulación ya guardaba `caso_id` y `GET /api/simulaciones?caso_id=` ya filtraba por caso, pero la ficha del caso no mostraba las simulaciones.
- En la ficha, cada bloque tenía un ancho distinto (`max-w-md` la tarjeta, `max-w-3xl` el resto).

## Decisión
- **Selector de caso:** los casos se vuelven a pedir cada vez que se entra a `/simular`.
- **Ficha del caso:** se agrega la sección "Simulaciones" (perfil, estímulo, estado y fecha, de a 20 con "Cargar más"), con un botón "Nueva simulación" que abre Simular con el caso ya elegido.
- **Diseño (opción B):** la ficha del caso queda en **una sola columna**, con todos los bloques del mismo ancho (`max-w-3xl`): caso, audiogramas, simulaciones y comparativas.

## Alternativas descartadas
- **Opción A, dos columnas a lo ancho:** aprovecha las pantallas anchas, pero hay más elementos que mantener alineados y es más riesgoso para la semana de la entrega. Se puede retomar después.
- **Nueva simulación también en una columna:** se probó y se volvió atrás a pedido de Valentino; las dos columnas ya funcionaban bien.
- **Reutilizar la tabla del Historial con un filtro:** arrastra las casillas de Superponer y el selector de caso, que en la ficha no hacen falta.

## Consecuencias
- La edición del caso sigue usando `Tarjeta` (`max-w-md`).
