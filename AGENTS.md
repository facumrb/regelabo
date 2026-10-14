# AGENTS.md — regelabo (Laboratorio Virtual Auditivo)

Plataforma web que integra el modelo de simulación biológica de Verhulst et al.
(2018) con herramientas de análisis de datos para la investigación auditiva.
Permite a fonoaudiólogos/investigadores cargar audiogramas, ejecutar de forma remota
simulaciones biológicas complejas y visualizar los resultados (EFR, ABR, FFT) en tiempo real.

---

## 1. Arquitectura del Proyecto (según proposal.md)

Arquitectura Orientada a Servicios (SOA): **FastAPI (backend) + React (frontend)**.

```
regelabo/
├── frontend/                    ← React + Vite + TailwindCSS + Plotly.js (UI científica)
├── backend/
│   ├── main.py                  ← Entry point unificado (uv run fastapi dev main.py)
│   └── services/
│       ├── core-service/        ← FastAPI: auth, usuarios, API central (Supabase)
│       ├── simulation-service/  ← Motor Verhulst 2018 (cálculo biológico en C + Python)
│       └── llm-service/         ← RAG con LangChain + ChromaDB (Fase 2)
├── agent/                       ← Scaffolding de agentes IA
├── docs/                        ← Specs, guías, presentación
└── docker-compose.yml           ← Orquestación de servicios
```

---

## 2. Estado de Implementación

### ✅ Completado y Verificado
- **Motor de Simulación (`simulation-service`):**
  - Solver en C (`tridiag.so`) compilado con GCC (`-O3 -ffast-math`). Verificado con `HAS_CLIB: True`.
  - Endpoint `GET /health`: Estado del servicio y disponibilidad del solver C.
  - Endpoint `GET /profiles`: Lista 33 perfiles clínicos disponibles en `data/Poles/` (`Flat00`, `Flat20`, `Slope20`, etc.).
  - Endpoint `POST /simulate`: Ejecución completa del modelo Verhulst 2018. Devuelve EFR en $\mu\text{V}$, armónicos (110, 220, 330, 440 Hz), espectro FFT (0-1000 Hz) y ondas ABR (W1, W3, W5) decimadas para entrega web ágil (< 50 KB).
  - CORS habilitado para comunicación con React (`http://localhost:5173`).
- **Módulo de Audiogramas y Síntesis Coclear (`simulation-service`):**
  - Endpoint `POST /audiogram/upload`: Carga de archivos CSV/TXT vía FilePond.
  - Endpoint `POST /audiogram/manual`: Procesamiento de curvas audiométricas interactivas.
  - Cálculo de PTA, detección de patrones (Plano vs Pendiente) y síntesis de perfiles `Custom_<paciente>` en `data/Poles/` listos para simular.
- **Frontend Científico (`frontend/`):**
  - Aplicación completa React 18 + Vite + TailwindCSS corriendo en `http://localhost:5173`.
  - **Dashboard de Simulación**: Controles de estímulo RAM, sliders de frecuencia/intensidad/modulación, parámetros neuronales (sinaptopatía), y gráficos Plotly interactivos para FFT y ondas ABR.
  - **Gestor de Audiogramas**: Componente FilePond para drag & drop de CSVs, trazado audiométrico clínico con escala invertida dB HL, presets patológicos rápidos y vinculación de perfiles a la simulación.
- **Backend Unificado (`backend/main.py`):**
  - Expone el servicio de simulación, audiogramas y documentación OpenAPI (`/docs`).
  - Ejecutable directamente con `uv run fastapi dev main.py`.

### 🔶 En Progreso / Pendiente
- **Gestión de Usuarios (`core-service`):** Conexión con Supabase Auth y PostgreSQL.
- **Fase 2 (LLM / RAG):** `llm-service` con LangChain y ChromaDB.

---

## 3. Comandos de Desarrollo

```bash
# Backend (desde backend/)
cd backend
uv run fastapi dev main.py
# → Swagger UI interactivo en http://localhost:8000/docs

# Frontend (desde frontend/)
cd frontend
pnpm install
pnpm run dev
# → UI en http://localhost:5173
```
