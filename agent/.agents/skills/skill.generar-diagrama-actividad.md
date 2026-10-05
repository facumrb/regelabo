# Skill: Generar Diagrama de Actividad (DA)

> **Trigger:** `speckit.analyze` → produce `activity-diagrams/<nombre>.md`

---

## Propósito

Genera el **diagrama de actividad del recorrido del fonoaudiólogo** para una funcionalidad del sistema Regelabo. El output es un documento Markdown estructurado que describe:
- Las metas del fonoaudiólogo (qué quiere lograr)
- El flujo de pasos con bifurcaciones
- El modelo Verhulst tratado como **caja negra**
- Un subdiagrama interno opcional

---

## Plantilla de Output

```markdown
# Diagrama de Actividad: <Nombre de Funcionalidad>

> **Caso de uso #<N>:** <Nombre del caso de uso del overview>
> **Fecha:** <fecha> | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo

### Meta Principal
<Una oración que resume qué quiere lograr el fonoaudiólogo con esta funcionalidad>

### Sub-metas / Objetivos intermedios
- **M1:** <primera sub-meta>
- **M2:** <segunda sub-meta>
- ...

### Clasificación en la taxonomía del proyecto
```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: <esta funcionalidad>
│   ├── <sub-sub-meta 1>
│   └── <sub-sub-meta 2>
└── ...
```

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad del fonoaudiólogo o del sistema
- `<Decisión>` = Bifurcación (rombo de decisión)
- `→` = Flujo de control
- `║` = Barra de sincronización (fork/join paralelo)
- `╔═══╗` = Actividad compuesta / Caja Negra del modelo Verhulst

### Flujo

```
[●] INICIO
  │
  ▼
[1. Fonoaudiólogo accede al módulo "<nombre>"]
  │
  ▼
...
╔══════════════════════════════════════════════════════════════╗
║  N. PIPELINE DE SIMULACIÓN VERHULST (CAJA NEGRA)           ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: <parámetros específicos de esta funcionalidad>    ║
║  Salida:  <outputs esperados>                               ║
║                                                             ║
║  Ver verhulst-analysis/<nombre>.md para detalle             ║
╚══════════════════════════════════════════════════════════════╝
  │
  ▼
...
[●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| N | <decisión> | <rama A> | <rama B> |

---

## 3. Subdiagrama: Pipeline Verhulst (opcional)

> Solo incluir si la funcionalidad tiene lógica interna específica que difiere del pipeline estándar.
```

---

## Instrucciones de Ejecución

1. Leer la descripción de la funcionalidad en `functionalitiesOverview.md`.
2. Identificar el actor (fonoaudiólogo / investigador) y su objetivo clínico.
3. Mapear el flujo de pasos a alto nivel:
   - ¿Qué configura el usuario?
   - ¿Qué valida el sistema?
   - ¿Cuándo y cómo se invoca el modelo Verhulst?
   - ¿Qué visualiza el usuario al finalizar?
4. Identificar todas las bifurcaciones (opciones, validaciones, errores).
5. Tratar el modelo Verhulst como caja negra en el flujo principal.
6. Guardar en `docs/specs/activity-diagrams/<nombre-representativo>.md`.
