---
trigger: manual
command: /speckit.diagram
description: Genera únicamente el diagrama de actividad de una funcionalidad.
skills:
  - skill.generar-diagrama-actividad
rules:
  - constitution.md
---

# Workflow: /speckit.diagram — Diagrama de Actividad

## Propósito
Dado el número o nombre de una funcionalidad, genera exclusivamente:
`docs/specs/activity-diagrams/<nombre>.md`

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

### Paso 2 — Ejecutar skill: Diagrama de Actividad

Aplicar `skill.generar-diagrama-actividad.md`:
- Identificar actor y meta clínica.
- Mapear flujo de pasos con bifurcaciones.
- Tratar modelo Verhulst como caja negra.
- Guardar en `docs/specs/activity-diagrams/<nombre_archivo>.md`.

### Paso 3 — Verificar vínculo con análisis Verhulst

- Si existe `docs/specs/verhulst-analysis/<nombre_archivo>.md`, enlazarlo en la sección de subdiagrama.
- Si no existe, incluir la nota: *"Análisis Verhulst pendiente de generación mediante /speckit.verhulst."*

### Paso 4 — No actualizar índice

La generación del diagrama **no** modifica `docs/specs/README.md` ni el mapeo de funcionalidades. La actualización del estado global se hará cuando ambos documentos (diagrama + análisis) estén completos, mediante revisión manual o el comando combinado `/speckit.analyze`.

---

## Ejemplo de Invocación

Para generar el diagrama de actividad de la funcionalidad #2:

```
/speckit.diagram
funcionalidad_numero: 2
funcionalidad_nombre: Generar datos sintéticos controlados
nombre_archivo: datos-sinteticos-ml
```

El agente ejecutará los pasos 1-4 y producirá:
- `docs/specs/activity-diagrams/datos-sinteticos-ml.md`