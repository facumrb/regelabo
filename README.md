# Laboratorio Virtual Auditivo

Plataforma basada totalmente en Arquitectura Orientada a Servicios que integra modelos de simulación biológica (Verhulst et al.) con herramientas de análisis de datos e inteligencia artificial (LLM) para la investigación auditiva.

## Arquitectura Orientada a Servicios

El proyecto está diseñado de forma modular para garantizar la escalabilidad, la mantenibilidad y dejar la puerta abierta a integraciones de futuros servicios (ej. CompuCell3D):

- **`frontend/`**: Aplicación de interfaz al usuario (React). Encargada estrictamente de la presentación, la orquestación de subida de archivos (audiogramas), la interacción para consultar estudios (PDFs) y la visualización gráfica.
- **`backend/`**: Capa central de negocio (FastAPI). Gestiona múltiples sub-servicios y enruta la información. Contiene:
  - **Servicio Core / API:** (`backend/src/api`, `backend/src/db`) Responsable de los endpoints de la API, manejo de estado y autenticación con Supabase.
  - **Servicio de Simulación:** (`backend/src/simulation`) Procesamiento científico con el modelo de Verhulst y uso de herramientas matemáticas (NumPy/SciPy). Escalará mediante colas como Celery.
  - **Servicio de Análisis/IA:** (`backend/src/llm`) Uso de modelos LLM, RAG y bases de datos vectoriales (ChromaDB) para consultar papers e investigaciones a la par de los resultados.

## Herramientas de Instalación Recomendadas

Dado que este laboratorio une múltiples dominios (IA, ciencia de datos e interfaces pesadas), las librerías pueden volverse conflictivas o tardar mucho tiempo en compilar por canales tradicionales. Se recomienda este set de herramientas de nueva generación:

### 1. El Backend (Python) -> Instalación con `uv`
Se recomienda utilizar [**uv**](https://github.com/astral-sh/uv).
* **¿Por qué `uv`?**: Es un gestor ultrarrápido creado en Rust. Las librerías científicas pesadas (como `scipy`, `pandas`) o el stack de IA (`dask`, `langchain`) tardan varios minutos en resolverse limpiamente usando el `pip` tradicional. `uv` no solo permite resolver el árbol de dependencias e instalarlas en milisegundos, sino que maneja la creación de tu ecosistema virtual mucho más limpio, limitando los típicos errores cruzados en Data Science.
* **Uso (Estando ubicado en el repositorio)**:
  ```bash
  cd backend
  uv venv               # Crea un entorno virtual
  .\.venv\Scripts\activate   # Activa tu entorno en Windows
  uv pip install -r requirements.txt  # Instala las dependencias en segundos
  ```

### 2. El Frontend (React / Web) -> Instalación con `pnpm`
Se recomienda utilizar [**pnpm**](https://pnpm.io/es/) (o alternativamente **bun**).
* **¿Por qué `pnpm`?**: En una arquitectura basada en servicios estarás en un flujo constante de creación de proyectos, instalaciones y despliegues. Usar algo como `npm` duplicará en tu disco de Windows cada mega que descargues en `node_modules`. Al usar herramientas como `Plotly.js` y `pdfjs-dist`, que son muy grandes, `pnpm` reutilizará los archivos descargados globalmente (hard-links), lo que instalará tu proyecto el triple de rápido y ahorrará gigabytes de almacenamiento.
* **Uso (Estando ubicado en el repositorio)**:
  ```bash
  cd frontend
  pnpm install          # Resuelve el package.json
  # pnpm run dev
  ```

## Paso a Paso para Empezar a Desarrollar

1. **Bases de datos:** Asegúrate de tener al día y configurado el proyecto de Supabase. Deberás crear copias de los archivos `.env.example` llamadas `.env` e ingresar allí tus credenciales.
2. **Instalación de Dependencias Conjunta:**
   En la raíz del proyecto, asegúrate de tener `Node.js` y `uv` instalados. Ejecuta el orquestador:
   ```bash
   npm install      # Instala las herramientas de orquestación global
   npm run install:all # Instala tanto en backend como frontend automáticamente
   ```
3. **Ejecutar TODO a la vez:** 
   Puedes levantar tanto el servidor **FastAPI** como la pre-visualización de **React** en una sola consola con el siguiente comando en la raíz del proyecto:
   ```bash
   npm run dev
   ```
   *Esto iniciará ambos servicios con recarga en memoria. FastAPI suele exponerse en `http://localhost:8000` y React en el puerto `http://localhost:5173`.*
