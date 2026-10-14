# CLAUDE.md

Este archivo orienta a Claude Code (claude.ai/code) al trabajar con el código de este repositorio.

Laboratorio Virtual Auditivo: plataforma web (FastAPI + React) que ejecuta el modelo biofísico de Verhulst et al. (2018) a partir de audiogramas y visualiza EFR, ABR y FFT. Ver también `AGENTS.md` (estado de implementación) y `proposal.md` (propuesta de la cátedra).

## Idioma

Todo el trabajo en este repositorio se hace en **español**: respuestas en el chat, comentarios y docstrings, mensajes de error y de log, textos de la UI, documentación, mensajes de commit y descripciones de PR. Los identificadores siguen la convención ya presente en el código (nombres en inglés como `execute_simulation`, `SimulationRequest`); no traducir los existentes.

## Comandos

```bash
# Todo junto desde la raíz (usa concurrently)
npm install && npm run install:all   # uv venv + requirements en backend/, pnpm install en frontend/
npm run dev                          # backend :8000 + frontend :5173

# Backend solo
cd backend && uv run fastapi dev main.py   # Swagger en http://localhost:8000/docs

# Frontend solo
cd frontend && pnpm run dev                # también: pnpm run build / pnpm run preview

# Recompilar el solver C (necesario tras clonar en otra plataforma o editar cochlea_utils.c)
cd backend/services/simulation-service/src/Verhulst/src/c_lib && ./build.sh   # build.bat en Windows
```

No hay suite de tests ni linter configurados. Para verificar el backend, usar `GET /health` (`c_solver_available` debe ser `true`) y ejecutar un `POST /simulate` desde Swagger.

## Arquitectura

### Backend: un solo servicio activo detrás de un loader
- `backend/main.py` no define rutas: carga dinámicamente `services/simulation-service/main.py` con `importlib` y re-exporta su `app`. Todo lo que hoy se sirve en :8000 proviene de **simulation-service**.
- `core-service` (Supabase/auth) y `llm-service` (RAG) existen como esqueletos con Dockerfile, pero **no están montados** en `backend/main.py`. `backend/docker-compose.yml` los define como contenedores separados (puertos 8001–8003 tras Traefik), aunque el flujo de desarrollo real no usa Docker.

### simulation-service (`backend/services/simulation-service/`)
Capas: `src/api/simulation_controller.py` (router FastAPI) → `src/services/` (lógica) → `src/models/` (Pydantic). Endpoints: `/health`, `/profiles`, `/simulate`, `/audiogram/upload`, `/audiogram/manual`.

- **Manejo de `sys.path`**: el `main.py` del servicio inserta su directorio en `sys.path` para que funcionen los imports `src.…`; `simulation_service.py` además inserta `src/Verhulst/src`, por lo que el código de Verhulst se importa como módulos top-level (`from model2018 import model2018`, `from core.cochlear_model2018 import HAS_CLIB`, `from utils.get_RAM_stims import …`). Respetar esta convención al agregar imports.
- **Modelo Verhulst** (`src/Verhulst/`): código científico vendorizado (Python + C). `core/` contiene las etapas (cóclea → IHC → nervio auditivo → CN/IC), `model2018.py` las orquesta y `storeflag` decide qué salidas se calculan. Hay `EXPLICACION.md` en `core/`, `utils/` y `c_lib/` con la explicación de cada módulo.
- **Solver C**: `core/cochlear_model2018.py` carga `c_lib/tridiag.so` (o `.dll`) vía ctypes; si falla, `HAS_CLIB=False` y cae a un fallback Python mucho más lento. El `.so` versionado es un binario Linux.
- **Perfiles de audición**: cada carpeta en `src/Verhulst/data/Poles/<perfil>/StartingPoles.dat` es un perfil simulable; `/profiles` lista esas carpetas.
- **Flujo de audiograma** (`audiogram_service.py`): parsea CSV/TXT o puntos manuales → calcula PTA (500/1k/2k/4k Hz) → clasifica plano vs pendiente (diferencia agudos-graves ≥ 15 dB) → elige un perfil base (`Flat*`/`Slope*`) → escribe `data/Poles/Custom_<paciente>/`. Hoy `_synthesize_custom_poles` **copia** los polos del perfil base; no los deriva de la curva del paciente. Estas carpetas `Custom_*` son generadas en runtime.
- **Pipeline `/simulate`** (`simulation_service.py`): carga polos → genera estímulo RAM (`fs=100 kHz`, 0.4 s) → `model2018(...)` → EFR = W1+W3+W5 → FFT, amplitudes de los 4 primeros armónicos de `f_mod`, espectro recortado a 0–1000 Hz y ondas ABR decimadas para mantener la respuesta liviana. Es síncrono y puede tardar minutos (el frontend usa timeout de 180 s).
- `model2018` se llama con `data_folder='./'`, así que deja archivos `*_0.npz` en el directorio de trabajo (por eso aparecen en `backend/`).

### Frontend (`frontend/`)
React 18 + Vite + Tailwind + Plotly. `src/App.jsx` concentra el estado global (vista `simulation`/`audiogram`, parámetros, resultado) y lo pasa a los componentes de `src/components/`. Todas las llamadas HTTP pasan por `src/services/api.js` (axios, base `VITE_API_URL` o `http://localhost:8000`).

### Otros directorios
- `docs/`: specs funcionales (`docs/specs/`), guías de visualización y metodología SDD (`docs/guias/`), presentación.
- `agent/`, `.agents/`, `.opencode/`: scaffolding de agentes IA, no forman parte de la app.
