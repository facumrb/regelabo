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
uv run fastapi dev app.py            # Swagger en http://localhost:8000/api/docs
uv run flake8                        # estilo PEP8 (config en .flake8)
uv run pytest                        # tests en backend/tests/ (necesitan `docker compose up -d db`; usan la base regelabo_test, que se crea sola)

# Base de datos (desarrollo): copiar .env.example a .env antes
docker compose up -d db              # PostgreSQL 17 local
uv run alembic upgrade head          # aplicar migraciones (backend/datos/migraciones/)
uv run alembic revision --autogenerate -m "descripcion"   # tras cambiar backend/datos/tablas.py
uv run alembic check                 # confirma que tablas.py y la base coinciden
uv run python -m backend.comandos.crear_admin   # crea (o promueve) un admin; pide email y contraseña
uv run python -m backend.comandos.resetear_contrasena   # contraseña nueva para quien la olvidó (desbloquea y cierra sus sesiones)
```

Al autogenerar, **revisar la migración**: Alembic duplica los `CHECK` de los campos de valores fijos (`sa.Enum(..., native_enum=False)` ya los crea); hay que borrar las líneas `sa.CheckConstraint(...)` que agrega, o `upgrade` falla con `DuplicateObject`.

```bash
# Frontend solo
cd frontend && pnpm run dev          # también: pnpm run build / typecheck / preview

# Compilar el solver C (obligatorio tras clonar: tridiag.so está en .gitignore)
cd backend/simulacion/verhulst/src/c_lib && ./build.sh   # build.bat en Windows
```

Para verificar el backend: `GET /api/health` (`c_solver_available` debe ser `true`) y un `POST /api/simulate` desde Swagger. Una simulación tarda ~75 s y usa ~1,1 GB de RAM en un solo núcleo.

## Arquitectura

Monolito modular en 3 capas. `app.py` (raíz) crea la app con `backend.views.crear_app()`. Las dependencias van en un solo sentido:

```
views/ (HTTP) → controller/ (negocio) → datos/ (persistencia)
                                      → simulacion/ (motor Verhulst)
```

- **`backend/views/`**: routers FastAPI, todos bajo `/api`. Solo reciben el pedido, llaman al controller y traducen errores a HTTP: `ErrorDeNegocio` → `{"detail": {"codigo", "mensaje"}}` con el estado de `views/errores.py` (los endpoints del prototipo todavía usan `ValueError` → 400). `views/dependencias.py` tiene `usuario_actual` y `requiere_admin` para proteger rutas (todas piden sesión salvo `/health`, `/api/`, el registro y el login); `views/limites.py`, el límite de pedidos por IP (slowapi). No importan nada de `datos/` ni de `simulacion/`.
- **`backend/controller/`**: lógica de negocio. `modelos.py` tiene los objetos de negocio (Pydantic) que también usan las views como `response_model`; `errores.py`, `ErrorDeNegocio`; `autenticacion.py`, registro, login con bloqueo y sesiones. Nunca accede al disco ni al modelo directamente.
- **`backend/datos/`**: todo acceso a persistencia. `tablas.py` define las 10 tablas (SQLAlchemy, internas a la capa: las funciones devuelven objetos de negocio del controller); `conexion.py` lee `DATABASE_URL` y ofrece `transaccion()`, que el controller usa para agrupar operaciones (ej. verificar cupo + encolar) pasando la sesión a las funciones de datos (`casos.py` es el ejemplo a copiar: filtra siempre por dueño y excluye los borrados, y pagina por cursor); `perfiles.py` lee y escribe los perfiles de polos en `simulacion/verhulst/data/Poles/<perfil>/StartingPoles.dat`.
- **`backend/configuracion.py`**: parámetros leídos de variables de entorno (`.env` en desarrollo): `DATABASE_URL`, duración de sesión, intentos máximos, bloqueo y `COOKIE_SECURE` (por defecto `true`; el `.env` de desarrollo lo pone en `false`).
- **`backend/comandos/`**: scripts de administración, fuera de las 3 capas; solo llaman al controller.
- **`backend/simulacion/motor.py`**: adaptador del modelo; único lugar que manipula `sys.path` para importar el código de Verhulst como módulos top-level (`model2018`, `core`, `utils`). Expone `ejecutar_modelo(...)` y `solver_c_disponible()`.
- **`backend/simulacion/verhulst/`**: código del modelo Verhulst 2018 copiado al repo (Python + C). No se edita salvo necesidad; está excluido de Flake8. Hay `EXPLICACION.md` en `src/core/`, `src/utils/` y `src/c_lib/`.

Detalles a tener en cuenta:
- Sesión: cookie `sesion` (`httpOnly`, `SameSite=Lax`, ruta `/api`) con un token aleatorio; en la tabla `sesion` solo se guarda su hash SHA-256. Al lanzar un error de negocio dentro de `transaccion()` se revierte todo: para registrar un efecto (ej. un intento fallido) hay que salir del bloque antes de lanzar, como hace `iniciar_sesion`.
- El modelo es determinista: el ruido de la cóclea usa la semilla `subject`, así que mismos parámetros ⇒ mismo resultado (habilita la caché de resultados planificada).
- `model2018` se llama con `data_folder='./'` y deja archivos `*_0.npz` en el directorio de trabajo (están en `.gitignore`).
- El flujo de audiograma clasifica por PTA (500/1k/2k/4k Hz) y patrón plano/pendiente, y genera `Custom_<nombre>` **copiando** los polos del perfil base más cercano; todavía no usa `OHC_ind` (faltan los `.mat` del repo oficial). Las carpetas `Custom_*` se generan en runtime y están en `.gitignore`.

### Frontend (`frontend/`)
React 18 + Vite + Tailwind + Plotly, con `react-router-dom`. Todo el código está en TypeScript (`.tsx`/`.ts`; `pnpm run typecheck`, y `allowJs` está apagado: no se admiten `.js`/`.jsx` en `src`). Los tipos de la simulación y los audiogramas están en `src/services/tiposSimulacion.ts` y reflejan `backend/controller/modelos.py`: si cambia un modelo del backend, actualizar ahí. `src/App.tsx` concentra el estado del prototipo (ruta `/`) y muestra en `/` la pantalla de bienvenida (`pages/Bienvenida.tsx`) si no hay sesión, y define las rutas `/login`, `/registro`, `/cuenta` (cambio de contraseña) y `/casos` (`src/pages/`; las que piden sesión se envuelven en `components/RequiereSesion.tsx`). `src/context/SesionContext.tsx` guarda el usuario de la sesión (recuperado con `GET /api/auth/yo` al cargar). `src/components/PanelPruebas.tsx` es una barra solo de desarrollo que muestra los pedidos a `/api/auth/*` y `/api/casos`. Guía para probar todo: `docs/guia-de-pruebas.md`. Todas las llamadas HTTP pasan por `src/services/api.js` (axios, base `/api`: en desarrollo Vite reenvía `/api` a `localhost:8000`, igual que Caddy en producción, así que no hay CORS; **no definir `VITE_API_URL` en `frontend/.env`**, porque pisa ese valor y rompe las llamadas). 

### Otros directorios
- `docs/reglas-de-negocio.md` (RN1–RN10) y `docs/decisiones/` (una decisión por archivo, con alternativas descartadas): leerlos antes de proponer cambios de diseño.
- `docs/api/`: colección de Bruno (requests y aserciones de la API, con su README); desde esa carpeta, `pnpm dlx @usebruno/cli run 0-estado 1-flujo-feliz 2-errores 3-manuales -r --env desarrollo` y, pasado un minuto cada vez (límite de 5 registros/logins por minuto), `... run 4-casos -r --env desarrollo` y `... run 5-cuenta -r --env desarrollo`. Al sumar un módulo, agregarle su carpeta copiando `4-casos`.
- `docs/specs/`: casos de uso y requerimientos por funcionalidad, y el plan de cuellos de botella. `docs/guias/`: visualización y metodología SDD. `docs/CC3D/`: idea descartada de CompuCell3D (solo referencia).
- `agent/`, `.agents/`, `.claude/skills/`, `.opencode/`: configuración de agentes IA; no forman parte de la app.
- `validacionPlanAnalisis/`: scripts y salidas de validación del plan de análisis.

## Estado

El sprint 0 está en curso (rama `feature/setup-entorno`): ya están la reorganización en capas, la base de datos (10 tablas), la autenticación (con cambio de contraseña, decisión 018) y el **módulo de ejemplo Casos** (`views/casos.py` → `controller/casos.py` → `datos/casos.py`, `tests/test_casos_api.py`, `frontend/src/pages/casos/`, `docs/api/4-casos/`): es la plantilla para los módulos nuevos. Falta pasar el prototipo a TypeScript (paso 4b), la cola de simulaciones con worker y el CI. Plan y estado de cada paso: `docs/plan-de-trabajo.md`.

## Reglas
- Nunca tomar una desición, ya sea de negocio, diseño, codigo, etc por tu cuenta. Siempre consultar, dar opciones y justificacion del porque de las mismas.
- Cualquier plan que tengamos para realizar, ya sea de organización, funcionalidad, etc., consulta todo lo que sea necesario para validar bien. Si se requiere se puede hacer uso de la skill `.claude/skills/grill-me`.
- NO EJECUTAR COMANDO DE ALTA O MODIFICACION DE GIT, SOLO LECTURA DE RAMAS E HISTORIAL
- NO TOCAR LA BASE DE DATOS, TODA CONSULTA NECESARIA SE HACE DESDE LA LOGICA DEL NEGOCIO

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

