# 001 — Alcance del TPI

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
La propuesta original incluía simulación, gestión de usuarios, un asistente de IA con papers (LangChain + ChromaDB) y varias funcionalidades de I+D. El TPI de Soporte (UTN FRRO) se entrega a fin de 2026 con un equipo de 3 personas.

## Decisión
El TPI cubre 4 módulos:
1. **Autenticación y usuarios.**
2. **Casos y audiogramas:** carga CSV o manual, PTA, clasificación y perfil auditivo propio (`OHC_ind`).
3. **Simulación con historial:** cola en segundo plano, ondas W1/W3/W5, EFR, FFT, latencias y amplitudes.
4. **Arquetipos:** biblioteca de ~12 arquetipos con nombre clínico, comparación del ABR cargado por similitud y registro de la hipótesis de estudio.

El sistema es una herramienta de **estudio y experimentación, no profesional**: muestra coincidencias, nunca diagnósticos (RN9).

## Alternativas descartadas
- Incluir el asistente de IA con papers: queda para el año próximo, fuera de la materia.
- Un clasificador de ML entrenado: queda como evolución del módulo de arquetipos; la similitud por correlación se reemplaza sin tocar el resto.

## Consecuencias
- Quedan para después: exportar a PDF, comparación entre fenotipos, generación en lote, optimización de estímulos, estímulos click y tone burst, WebSocket e integración con hospitales (HL7 FHIR, leyes 25.326 y 26.529).
