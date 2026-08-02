# Propuesta de Proyecto: Laboratorio Virtual Auditivo

## 1. Resumen Ejecutivo

**Nombre:** Laboratorio Virtual Auditivo.

**Propósito:** Plataforma web que integra el modelo de simulación biológica de *Verhulst et al.* con inteligencia artificial (LLMs) y análisis de datos en un entorno unificado.

**Objetivo Principal:** Permitir a fonoaudiólogos e investigadores científicos cargar audiogramas, ejecutar de forma remota simulaciones biológicas complejas y poder visualizar los resultados a la par que se consulta literatura científica relevante, impulsada por un asistente de investigación de Inteligencia Artificial.

## 2. Arquitectura Orientada a Servicios (SOA)
El laboratorio se construye bajo un diseño modular destinado a soportar experimentación de alto rendimiento sin interrumpir la experiencia del usuario.

* **Frontend (Interfaz Científica):** Aplicación interactiva enfocada estrictamente en la orquestación de subida de archivos, visualización de iteraciones gráficas y lectura de PDFs.
* **Backend (Capa Central y APIs):** Enrutador principal construido con interfaces de alta velocidad para mediar entre la petición del usuario, las bases de datos y los microservicios.
* **Servicio de Simulación (Motor Matemático):** Subsistema en segundo plano especializado en procesar algoritmos pesados y modelos experimentales para que la UI principal permanezca siempre fluida.
* **Servicio de Análisis e Inteligencia Artificial:** Un ecosistema para Retrieval-Augmented Generation (RAG) destinado a la indexación, cruce y recuperación de información y metadatos desde papers científicos.

## 3. Stack Tecnológico Seleccionado

Se ha optado por tecnologías de vanguardia que agilicen el desarrollo analítico y potencien el flujo con grandes volúmenes de datos empíricos.

### Frontend
* **Core:** React con estilos de TailwindCSS.
* **Manejo Visual y de Formatos:** FilePond para la carga de audiogramas y PDF.js para la interactividad de archivos empíricos en los visualizadores.
* **Gráficos e Interfaz Científica:** Plotly.js para representar gráficamente las interacciones neuronales y de espectro.
* **Instalación:** Despliegue acelerado gestionado por *pnpm* (y *Node.js*) para eficientizar el almacenamiento tras instalaciones de dependencias pesadas.

### Backend y Base de Datos
* **Core:** FastAPI (Python) manejando peticiones JWT a través de Supabase Auth (OAuth2).
* **Gestión de Entorno:** Integración gestionada por *uv* como alternativa veloz al gestor pip estándar para dependencias de machine learning.
* **Bases de Datos & Almacenamiento:** PostgreSQL alojado con Supabase (para metadatos y modelos) complementado por Supabase Storage para los archivos del usuario (audiogramas, resultados generados MAT/CSV).

### Motor Científico (Simulación)
* **Procesamiento de Datos:** Pandas junto a NumPy/SciPy para toda la estructura de algebra y dataframes.
* **Sistema de Tareas Asíncronas:** Celery + Redis como gestor de colas indispensable para evitar bloqueos durante los pesados procesamientos matemáticos.
* **Ejecución y Extensibilidad:** Modelo de *Verhulst et al. (2018)* encapsulado a través de Docker y orquestación con Dask para el paralelismo en simulaciones complejas. Plotly (Python) y Matplotlib/Seaborn de ser necesario para generar los assets gráficos estáticos en el backend.

### IA, Módulos LLM y Literatura
* **Modelado y Embeddings:** Orquestación usando LangChain conectado a ChromaDB como base de datos vectorial para analizar textos científicos.
* **Modelos de Inferencia Open Source:** Uso asíncrono y acelerado en paralelo con *Ray*, integrando DeepSeek R1 y Qwen 2.5 como cerebros del análisis contextual.
* **Metadatos Literarios:** Integración vía Zotero API para vincular cada análisis con el archivo maestro de investigaciones en formato PDF (visualizable por PDF.js).
* **Visión a Futuro:** Exploración sistemática garantizada integrando DVC (Data Version Control) y MinIO para reproducibilidad extrema de la simulación.

## 4. Alcance Temporal y Fases de Desarrollo
El desarrollo de la plataforma se plantea en dos grandes etapas secuenciales, priorizando primero la estabilidad de la simulación científica y dejando para una segunda instancia el ecosistema documental de investigación.

### Fase 1: Motor Científico y Gestión de Usuarios
**Objetivo:** Establecer la infraestructura base. Lograr que un investigador pueda registrarse, subir audiogramas, ejecutar la simulación y visualizar los resultados numéricos y gráficos.

**Tecnologías Clave:** 
* React, FilePond, TailwindCSS (Frontend). 
* FastAPI, Supabase Auth/PostgreSQL/Storage (Backend API).
* Python, Docker, Pandas, NumPy/SciPy.
* Celery + Redis para correr de manera encolada el modelo de *Verhulst et al.*
* *Dask* (paralelismo) y *Plotly.js* / Plotly Python (visualización).

### Fase 2: Asistente de Investigación y Análisis Bibliográfico
**Objetivo:** Transformar el laboratorio básico en un entorno de estudio. Integrar la capacidad de consultar bibliografía científica y utilizar IA local/Open-Source para extraer contexto avanzado al cruzar las simulaciones con los documentos.

**Tecnologías Clave:**
* PDF.js y Zotero API (manejo de literatura).
* LangChain (Orquestador RAG) y ChromaDB (Base vectorial).
* Modelos Open-Source como *DeepSeek R1* / *Qwen 2.5*.
* Bases sentadas para simulación avanzada y extensibilidad a futuros dominios u otros modelos biomédicos (ej. **CompuCell3D**).

## 5. Flujo Funcional de Datos (User Journey)
1.  **Autenticación:** El usuario fonoaudiólogo/científico inicia sesión a través de un gateway seguro con *Supabase Auth*.
2.  **Input Analítico:** A través del Frontend (React + FilePond), el usuario sube un archivo (audiograma) que es resguardado temporalmente en el *Supabase Storage*.
3.  **Configuración de Tarea:** Se configuran los parámetros de la simulación. FastAPI capta estas métricas y remite el paquete de datos encolándolo en un hilo separado por medio de *Celery*.
4.  **Generación de Simulación:** Un Worker específico (Docker) toma el encargo, ejecuta el modelo científico, compila los tensores matemáticos, y procesa archivos como MAT, CSV y las tramas gráficas (Plotly/Matplotlib). 
5.  **Output Analítico:** Regreso a FastAPI mediante el worker; donde los resultados son guardados y referenciados en *PostgreSQL* para mantener un historial.
6.  **Visualización Activa:** El usuario analiza la visualización en *Plotly.js* dentro de su dashboard de Frontend en tiempo real.
7.  **Soporte de Inteligencia:** Mientras consulta literatura científica (*PDF.js*), el investigador interactúa haciendo preguntas; bajo todo esto, *LangChain* extrae contexto (Embeddings guardados en *ChromaDB*) y formula una interpelación a *DeepSeek/Qwen*, proveyendo como salida la correlación biológica y el análisis esperado.

## 6. Impacto Esperado en la Investigación 
La unificación de este stack técnico bajo una estructura de Servicios Distribuidos logrará un impulso cuantitativo revolucionario:
* **Democratización de Modelos Biológicos:** Se elimina la fricción de instalar librerías pesadas en ecosistemas locales. Con orquestadores como *uv* para dependencias e interfaz remota de ejecución, solo queda expuesta activamente la etapa de toma de decisiones científicas.
* **Aceleración Literario-Experimental:** Al poder contrastar de forma paralela un resultado de modelo simulado directamente contra evidencia empírica analizada por medio de Retrieve-Augmented Generation, se reduce el tiempo necesario entre la obtención del dato biomarcador y la conformación de la hipótesis peritada.
* **Escalabilidad y Evolución Intelectual:** Gracias al paralelismo explícito (Celery, Dask, Redis) la plataforma queda formalmente preparada, no solo para mantener una operación a gran escala, sino para acomodar y acoplar nuevos sistemas o escenarios multi-celulares más adelante (e.g. CompuCell3D), sin necesidad de reescribir de cero el núcleo aplicativo.
