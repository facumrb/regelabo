# 002 — Monolito modular en 3 capas

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
El checklist de la cátedra exige 3 capas con nombres de carpeta fijos (`views`, `controller` o `business`, `datos`) y un `app.py` en la raíz. El prototipo estaba armado como 3 microservicios (core, simulation, llm).

## Decisión
Una sola aplicación FastAPI dividida en capas:
`app.py` → `backend/views/` (HTTP) → `backend/controller/` (negocio) → `backend/datos/` (persistencia) y `backend/simulacion/` (modelo Verhulst). El frontend es React y está separado.

## Alternativas descartadas
- **Microservicios:** más contenedores, redes y despliegues que mantener, sin beneficio para el TPI; además no se ven como "3 capas" en la corrección.

## Consecuencias
- Las dependencias van en un solo sentido; la capa de presentación nunca importa `datos/`.
- El código del modelo Verhulst se usa solo a través de `simulacion/motor.py`.
