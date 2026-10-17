# 017 — Paginación por cursor

**Fecha:** 2026-10-16 · **Estado:** aceptada

## Contexto
El listado de casos es el primero de la API y el que van a copiar los demás (simulaciones, comparaciones). El historial de simulaciones puede crecer mucho, así que el equipo prefirió paginar desde el módulo de ejemplo.

## Decisión
- **Por cursor, con "Cargar más":** `GET /api/casos?limite=20&despues_de=<id>` devuelve `{"casos": [...], "siguiente": <id> | null}`. Para la página siguiente se pasa `siguiente` como `despues_de`; `null` significa que no hay más.
- **El cursor es el id:** los ids son UUIDv7, ordenados por tiempo de creación, así que "del más nuevo al más viejo" es `ORDER BY id DESC` y la página siguiente es `id < despues_de`. Usa el índice de la clave primaria.
- **`limite`:** 20 por defecto, entre 1 y 100 (fuera de rango, 422).
- **Se pide un elemento de más** (`limite + 1`) para saber si hay página siguiente sin un `COUNT`.
- Ejemplo a copiar: `backend/datos/casos.py` (`listar`) y `backend/controller/casos.py` (`listar`).

## Alternativas descartadas
- **Sin paginar:** suficiente para casos, pero el ejemplo no enseñaría el patrón que necesita el historial de simulaciones.
- **Por número de página (`OFFSET`):** si alguien crea o borra un caso mientras otro pagina, se repiten o se saltean filas, y con muchas filas cada página es más lenta (la base recorre todas las anteriores).

## Consecuencias
- No hay "ir a la página 7" ni total de elementos. Si alguna pantalla lo necesita, se agrega un endpoint de conteo aparte.
- Si un listado tuviera que ordenarse por otra columna (por ejemplo, alias), el cursor pasa a ser el par (columna, id).
