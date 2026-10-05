---
trigger: manual
command: /speckit.verhulst
description: Genera únicamente el análisis Verhulst de una funcionalidad.
skills:
  - skill.analizar-verhulst
rules:
  - constitution.md
---

# Workflow: /speckit.verhulst — Análisis Verhulst

## Propósito
Dado el número o nombre de una funcionalidad, genera exclusivamente:
`docs/specs/verhulst-analysis/<nombre>.md`

## Inputs Requeridos
```yaml
funcionalidad_numero: <número>
funcionalidad_nombre: <nombre descriptivo>
nombre_archivo: <slug para el archivo>
```

## Pasos del Workflow

### Paso 1 — Leer fuentes

1. Leer `docs/specs/functionalitiesOverview.md` → extraer la sección de la funcionalidad.
2. Leer `docs/specs/analisisScreeningNeonatal.md` → usar como referencia de formato y profundidad.
3. Leer `docs/specs/Integration Points Bera Abr.md` → contexto técnico de integración.
4. Revisar `backend/services/simulation-service/src/Verhulst/` → confirmar APIs y funciones reales del modelo.

### Paso 2 — Ejecutar skill: Análisis Verhulst

Aplicar `skill.analizar-verhulst.md`:
- Determinar veredicto (caja negra / modificación interna).
- Mapear entradas y salidas del modelo para esta funcionalidad.
- Diseñar interfaz API.
- Comparar con pipeline de referencia (Screening BERA).
- Guardar en `docs/specs/verhulst-analysis/<nombre_archivo>.md`.

### Paso 3 — Verificar vínculo con diagrama de actividad

- Si existe `docs/specs/activity-diagrams/<nombre_archivo>.md`, enlazarlo en la sección de análisis.
- Si no existe, incluir la nota: *"Diagrama de actividad pendiente de generación mediante /speckit.diagram."*

### Paso 4 — No actualizar índice

La generación del análisis **no** modifica `docs/specs/README.md` ni el mapeo de funcionalidades. La actualización del estado global se hará cuando ambos documentos (diagrama + análisis) estén completos, mediante revisión manual o el comando combinado `/speckit.analyze`.

---

## Ejemplo de Invocación

Para generar el análisis Verhulst de la funcionalidad #2:

```
/speckit.verhulst
funcionalidad_numero: 2
funcionalidad_nombre: Generar datos sintéticos controlados
nombre_archivo: datos-sinteticos-ml
```

El agente ejecutará los pasos 1-4 y producirá:
- `docs/specs/verhulst-analysis/datos-sinteticos-ml.md`