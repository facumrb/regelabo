Para crear un laboratorio virtual que conecte la simulación auditiva de Verhulst et al. con estudios científicos, lo ideal es combinar herramientas web, científicas y de visualización que permitan: cargar audiogramas fácilmente, ejecutar la simulación en Python, visualizar resultados y consultar literatura científica dentro del mismo entorno.

Tres niveles:
Arquitectura lógica (qué hace cada módulo)
Arquitectura técnica (qué tecnologías usa cada módulo)
Arquitectura de flujo (cómo viajan los datos)
Así queda un mapa mental completo.

1. Arquitectura lógica (los módulos del laboratorio)
El laboratorio tiene 8 módulos principales:
Frontend (React)
Backend científico (FastAPI)
Motor de simulación (Python + Verhulst Model)
Orquestación de tareas (Celery + Redis)
Módulo de LLM + análisis de papers (LangChain + ChromaDB)
Autenticación y usuarios (Supabase Auth)
Base de datos estructurada (PostgreSQL)
Almacenamiento de archivos (Supabase Storage)
Cada uno cumple un rol distinto y complementario.

2. Arquitectura técnica recomendada (stack final)
Frontend
React → interfaz principal
Plotly.js → gráficos interactivos
TailwindCSS → estilos
FilePond → carga de audiogramas
PDF.js → visualización de papers

Backend
FastAPI → API principal
Pandas → lectura de audiogramas
NumPy / SciPy → procesamiento científico
Celery + Redis → ejecución de simulaciones en segundo plano
Docker → encapsular el modelo auditivo

Backend (visualización científica)
Plotly (Python)
Matplotlib
Seaborn


Simulación
Verhulstetal2018Model (Python)
Dask → paralelismo para simulaciones
Ray → paralelismo para LLMs (opcional, pero recomendado)

LLM + Papers
LangChain → orquestación
ChromaDB → vector DB para embeddings
DeepSeek R1 + Qwen 2.5 → modelos open-source
Zotero API → metadatos de papers
PDF.js → visualización

Usuarios y seguridad
Supabase Auth (OAuth2) → login con Google, email, etc.
JWT → validación en FastAPI

Base de datos
PostgreSQL (Supabase)
usuarios
simulaciones
parámetros
historial
permisos

Almacenamiento
Supabase Storage → archivos del usuario


audiogramas
resultados
gráficos
MAT, CSV, polos


DVC + MinIO (a futuro) → reproducibilidad científica


invisible para la fonoaudióloga
solo backend
Supabase Storage y MinIO son alternativos, pero pueden coexistir si se quiere simplicidad + reproducibilidad.

3. Arquitectura de flujo (cómo viajan los datos)
Flujo completo, paso a paso:
1. Usuario inicia sesión → Supabase Auth
2. Usuario sube audiograma → React + FilePond → Supabase Storage
3. Usuario configura parámetros → React → FastAPI
4. FastAPI envía tarea → Celery → Worker de simulación
5. Worker ejecuta Verhulst Model → genera MAT, CSV, gráficos
6. Worker guarda resultados → Supabase Storage
7. FastAPI registra metadatos → PostgreSQL
8. Usuario visualiza resultados → React + Plotly.js
9. Usuario abre un paper → PDF.js
10. LangChain extrae texto → embeddings → ChromaDB
11. Usuario pregunta: “¿Cómo se relaciona este EFR con el paper?”
12. LangChain recupera contexto → LLM (DeepSeek/Qwen)
13. LLM responde → React muestra análisis

Arquitectura recomendada (resumen en una frase)
React + FastAPI + Celery + Verhulst Model + Supabase (Auth + PostgreSQL + Storage) + LangChain + ChromaDB + DeepSeek/Qwen es la arquitectura ideal para un laboratorio virtual moderno, científico, multiusuario y escalable.