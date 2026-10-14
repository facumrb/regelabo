# CLAUDE.md

Este archivo orienta a Claude Code (claude.ai/code) al trabajar con el código de este repositorio.

Laboratorio Virtual Auditivo: plataforma web (FastAPI + React) que ejecuta el modelo biofísico de Verhulst et al. (2018) a partir de audiogramas y visualiza EFR, ABR y FFT. Es el TPI de la materia Soporte (UTN FRRO): debe cumplir la arquitectura en 3 capas con los nombres de carpeta del checklist de la cátedra. Ver también `AGENTS.md` y `proposal.md`.

## Idioma

Todo el trabajo en este repositorio se hace en **español**: respuestas en el chat, comentarios y docstrings, mensajes de error y de log, textos de la UI, documentación, mensajes de commit y descripciones de PR. Los identificadores siguen la convención ya presente en el código (nombres en inglés como `execute_simulation`, `SimulationRequest`); no traducir los existentes.

## Comandos

```bash
# Todo junto desde la raíz (usa concurrently)
npm install && npm run install:all   # uv sync + pnpm install en frontend/
npm run dev                          # backend :8000 + frontend :5173

# Backend solo (desde la raíz)
uv run fastapi dev app.py            # Swagger en http://localhost:8000/docs
uv run flake8                        # estilo PEP8 (config en .flake8)
uv run pytest                        # tests (cuando existan, en backend/tests/)

# Base de datos (desarrollo): copiar .env.example a .env antes
docker compose up -d db              # PostgreSQL 17 local
uv run alembic upgrade head          # aplicar migraciones (backend/datos/migraciones/)
uv run alembic revision --autogenerate -m "descripcion"   # tras cambiar backend/datos/tablas.py
uv run alembic check                 # confirma que tablas.py y la base coinciden
```

Al autogenerar, **revisar la migración**: Alembic duplica los `CHECK` de los campos de valores fijos (`sa.Enum(..., native_enum=False)` ya los crea); hay que borrar las líneas `sa.CheckConstraint(...)` que agrega, o `upgrade` falla con `DuplicateObject`.

```bash
# Frontend solo
cd frontend && pnpm run dev          # también: pnpm run build / pnpm run preview

# Compilar el solver C (obligatorio tras clonar: tridiag.so está en .gitignore)
cd backend/simulacion/verhulst/src/c_lib && ./build.sh   # build.bat en Windows
```

Para verificar el backend: `GET /health` (`c_solver_available` debe ser `true`) y un `POST /simulate` desde Swagger. Una simulación tarda ~75 s y usa ~1,1 GB de RAM en un solo núcleo.

## Arquitectura

Monolito modular en 3 capas. `app.py` (raíz) crea la app con `backend.views.crear_app()`. Las dependencias van en un solo sentido:

```
views/ (HTTP) → controller/ (negocio) → datos/ (persistencia)
                                      → simulacion/ (motor Verhulst)
```

- **`backend/views/`**: routers FastAPI. Solo reciben el pedido, llaman al controller y traducen excepciones a códigos HTTP (`ValueError` → 400). No importan nada de `datos/` ni de `simulacion/`.
- **`backend/controller/`**: lógica de negocio. `modelos.py` tiene los objetos de negocio (Pydantic) que también usan las views como `response_model`. Nunca accede al disco ni al modelo directamente.
- **`backend/datos/`**: todo acceso a persistencia. `tablas.py` define las 9 tablas (SQLAlchemy, internas a la capa: las funciones devuelven objetos de negocio del controller); `conexion.py` lee `DATABASE_URL` y ofrece `transaccion()`, que el controller usa para agrupar operaciones (ej. verificar cupo + encolar) pasando la sesión a las funciones de datos; `perfiles.py` lee y escribe los perfiles de polos en `simulacion/verhulst/data/Poles/<perfil>/StartingPoles.dat`.
- **`backend/simulacion/motor.py`**: adaptador del modelo; único lugar que manipula `sys.path` para importar el código de Verhulst como módulos top-level (`model2018`, `core`, `utils`). Expone `ejecutar_modelo(...)` y `solver_c_disponible()`.
- **`backend/simulacion/verhulst/`**: código del modelo Verhulst 2018 copiado al repo (Python + C). No se edita salvo necesidad; está excluido de Flake8. Hay `EXPLICACION.md` en `src/core/`, `src/utils/` y `src/c_lib/`.

Detalles a tener en cuenta:
- El modelo es determinista: el ruido de la cóclea usa la semilla `subject`, así que mismos parámetros ⇒ mismo resultado (habilita la caché de resultados planificada).
- `model2018` se llama con `data_folder='./'` y deja archivos `*_0.npz` en el directorio de trabajo (están en `.gitignore`).
- El flujo de audiograma clasifica por PTA (500/1k/2k/4k Hz) y patrón plano/pendiente, y genera `Custom_<nombre>` **copiando** los polos del perfil base más cercano; todavía no usa `OHC_ind` (faltan los `.mat` del repo oficial). Las carpetas `Custom_*` se generan en runtime y están en `.gitignore`.

### Frontend (`frontend/`)
React 18 + Vite + Tailwind + Plotly. `src/App.jsx` concentra el estado global y lo pasa a `src/components/`. Todas las llamadas HTTP pasan por `src/services/api.js` (axios, base `VITE_API_URL` o `http://localhost:8000`). Está planificada la migración a TypeScript.

### Otros directorios
- `docs/reglas-de-negocio.md` (RN1–RN10) y `docs/decisiones/` (una decisión por archivo, con alternativas descartadas): leerlos antes de proponer cambios de diseño.
- `docs/specs/`: casos de uso y requerimientos por funcionalidad, y el plan de cuellos de botella. `docs/guias/`: visualización y metodología SDD. `docs/CC3D/`: idea descartada de CompuCell3D (solo referencia).
- `agent/`, `.agents/`, `.claude/skills/`, `.opencode/`: configuración de agentes IA; no forman parte de la app.
- `validacionPlanAnalisis/`: scripts y salidas de validación del plan de análisis.

## Estado

El sprint 0 está en curso (rama `feature/setup-entorno`): ya están la reorganización en capas y la base de datos (9 tablas, migración inicial); faltan autenticación propia, cola de simulaciones con worker, módulo de ejemplo (Casos), CI y la migración del frontend a TypeScript.

## Reglas
- Nunca tomar una desición, ya sea de negocio, diseño, codigo, etc por tu cuenta. Siempre consultar, dar opciones y justificacion del porque de las mismas.
- Cualquier plan que tengamos para realizar, ya sea de organización, funcionalidad, etc., consulta todo lo que sea necesario para validar bien. Si se requiere se puede hacer uso de la skill `.claude/skills/grill-me`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
