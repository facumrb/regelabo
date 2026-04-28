# Arquitectura y Tecnologías del Laboratorio Virtual Auditivo

Este documento constituye una guía conceptual sobre el *stack* tecnológico del Laboratorio Virtual Auditivo. Su propósito no es servir como manual de uso, sino establecer una comprensión precisa de los principios que rigen cada tecnología seleccionada, habilitando a todos los integrantes del equipo —independientemente de su perfil técnico— a interpretar correctamente las decisiones de arquitectura y el flujo de datos del sistema.

Para crear un laboratorio virtual que conecte la simulación auditiva de Verhulst et al. con estudios científicos, lo ideal es combinar herramientas web, científicas y de visualización que permitan: cargar audiogramas fácilmente, ejecutar la simulación en Python, visualizar resultados y consultar literatura científica dentro del mismo entorno.

El proyecto se divide en tres niveles para conformar un mapa mental completo:
1. Arquitectura lógica (qué hace cada módulo)
2. Arquitectura técnica (qué tecnologías usa cada módulo)
3. Arquitectura de flujo (cómo viajan los datos)

---

## 1. Fundamentos Arquitectónicos (Conceptos Transversales)

Antes de abordar cada componente de forma individual, es necesario establecer tres conceptos estructurales que atraviesan todas las capas del sistema.

### Interfaz de Programación de Aplicaciones (API)
Una **API** (*Application Programming Interface*) es un contrato formal de comunicación entre dos sistemas de software. Define de manera precisa qué operaciones pueden solicitarse, qué parámetros deben acompañar cada solicitud y qué formato tendrá la respuesta, sin exponer los detalles internos de implementación del sistema receptor.
En la presente plataforma, el Frontend se comunica con el Backend de forma exclusiva a través de una API REST. Esta separación garantiza que ambas capas puedan evolucionar de forma independiente sin alterar la interfaz de intercambio.

### Arquitectura Orientada a Servicios (SOA)
En lugar de un sistema monolítico —donde toda la lógica reside en un único bloque de código—, la plataforma se estructura en **servicios especializados** que se comunican entre sí a través de interfaces definidas. Cada servicio tiene una responsabilidad acotada y puede escalar, actualizarse o reemplazarse de forma autónoma sin afectar el conjunto del sistema.

### Contenedor (Docker)
Un **contenedor** es una unidad de empaquetado de software que incluye el código de una aplicación junto con todas sus dependencias, configuraciones y versiones de entorno de ejecución. Su principal atributo es la **portabilidad**: un contenedor se comporta de manera idéntica en cualquier máquina donde se ejecute, eliminando las inconsistencias originadas por diferencias entre entornos de desarrollo, prueba y producción.

---

## 2. Arquitectura Lógica (Los Módulos del Laboratorio)

El laboratorio tiene 8 módulos principales. Cada uno cumple un rol distinto y complementario:
1. **Frontend** (React)
2. **Backend científico** (FastAPI)
3. **Motor de simulación** (Python + Verhulst Model)
4. **Orquestación de tareas** (Celery + Redis)
5. **Autenticación y usuarios** (Supabase Auth)
6. **Base de datos estructurada** (PostgreSQL)
7. **Almacenamiento de archivos** (Supabase Storage)
8. **Módulo de LLM + análisis de papers** (LangChain + ChromaDB)

---

## 3. Arquitectura Técnica Recomendada (Stack Final)

### 3.1. Frontend (Interfaz Científica)
La capa de Frontend constituye la interfaz de interacción directa con el usuario. Se ejecuta íntegramente en el navegador del cliente y es responsable de la organización de la experiencia de usuario, la carga de archivos y la visualización de resultados.

*   **React:** Biblioteca de JavaScript orientada a la construcción de interfaces de usuario. Su unidad fundamental es el **componente**: una pieza de interfaz encapsulada, reutilizable e independiente que puede combinarse con otras para conformar la aplicación. React gestiona de forma eficiente la actualización del estado visual ante cambios en los datos subyacentes, sin necesidad de recargar la página en su totalidad. Es el estándar prevalente en Single Page Applications (SPA) y facilita la construcción de interfaces científicas ordenadas.
*   **TailwindCSS:** Framework de CSS basado en el paradigma *utility-first*. En lugar de definir estilos en hojas de estilo externas, los estilos se aplican directamente en el marcado mediante clases de propósito único. Favorece la consistencia visual y reduce la superficie de código CSS personalizado que debe mantenerse.
*   **FilePond:** Librería de JavaScript especializada en la gestión del proceso de carga de archivos. Implementa mecanismos de validación de formato y peso, previsualización, indicación de progreso y recuperación ante errores. Su adopción responde a la naturaleza de los archivos de entrada (audiogramas en formatos MAT, CSV o WAV), cuya carga exige un manejo fiable y con retroalimentación visual.
*   **Plotly.js:** Librería de visualización científica para entornos web. Permite renderizar gráficos interactivos —con capacidades de zoom, desplazamiento, selección de rangos y exportación— a partir de datos numéricos, ideal para series temporales, espectros de frecuencia y matrices de resultados. Comparte ecosistema con Plotly para Python, garantizando coherencia visual.
*   **PDF.js:** Herramienta para la visualización fluida de artículos científicos (*papers*) directamente en el navegador.
*   **pnpm:** Gestor de paquetes. Su diferencia central respecto a npm o yarn reside en su modelo de almacenamiento: en lugar de duplicar dependencias por proyecto, mantiene un único almacén global enlazado simbólicamente, reduciendo espacio en disco y tiempos de instalación. Relevante para librerías pesadas de visualización científica.

### 3.2. Backend y Base de Datos (Capa Central y APIs)
El Backend actúa como la capa de mediación central del sistema. Recibe solicitudes, valida autenticidad, orquesta operaciones contra las bases de datos y delega el procesamiento.

*   **FastAPI (Python):** Framework web orientado a construir APIs de alto rendimiento. Su arquitectura es nativa e asíncrona: puede procesar múltiples solicitudes concurrentes sin bloquearse a la espera de operaciones de I/O. Su rendimiento es comparable al de lenguajes compilados, y al estar en Python, comparte el ecosistema de librerías con el motor científico, simplificando la integración.
*   **JWT y OAuth2:** **JWT** es un estándar para tokens de seguridad firmados digitalmente. Permite al servidor verificar identidad sin consultar el repositorio en cada petición. **OAuth2** es el protocolo estándar que regula el flujo y roles para garantizar la seguridad del proceso.
*   **Supabase Auth:** Servicio de autenticación completo (registro, login con email, Google, soporte OAuth2). Exime al equipo de implementar infraestructura de autenticación desde cero, un dominio de alta complejidad y riesgo.
*   **PostgreSQL (a través de Supabase):** Sistema de gestión de bases de datos relacionales de código abierto. Permite consultas complejas, transacciones seguras y garantías de integridad referencial. Soporta arrays y JSON. En el sistema, **almacena datos de usuarios, simulaciones, parámetros de configuración, historial y permisos**.
*   **Supabase Storage:** Servicio de almacenamiento de objetos binarios. Alojamiento de **archivos del usuario, audiogramas, resultados, gráficos, MAT, CSV, y polos**. Aloja archivos de gran tamaño que no es eficiente almacenar en la base relacional. Los archivos se referencian desde PostgreSQL mediante URL. *A futuro, se contempla DVC + MinIO para reproducibilidad científica (invisible para la fonoaudióloga, solo backend). Supabase Storage y MinIO son alternativos, pero pueden coexistir si se quiere simplicidad + reproducibilidad.*
*   **uv:** Gestor de entornos virtuales y dependencias para Python. Resuelve el árbol de dependencias con menor latencia que `pip` y crea entornos aislados que garantizan que los paquetes requeridos no interfieran entre sí (vital para dependencias de machine learning).

### 3.3. Motor Científico (Servicio de Simulación)
El Motor Científico constituye el subsistema de procesamiento intensivo. Ejecuta el modelo de simulación biológica de *Verhulst et al.* produciendo resultados numéricos y gráficos.

*   **Procesamiento Asíncrono y Colas de Tareas:** Las simulaciones biológicas exceden la ventana de respuesta de una solicitud HTTP. La solución es el encolado: el Backend registra la tarea y responde con un identificador. Un *worker* consume la tarea y la ejecuta en segundo plano.
*   **Celery:** Sistema de gestión de colas de tareas (*task queue*). Permite definir funciones como tareas asíncronas, encolarlas y distribuirlas entre workers. Soporta reintentos automáticos, monitoreo de estado y encadenamiento.
*   **Redis:** Sistema de almacenamiento de datos en memoria. A diferencia de PostgreSQL, opera a latencias de microsegundos sobre estructuras simples. Actúa como el intermediario de mensajería (*broker*) de Celery para registrar tareas y estados.
*   **Verhulstetal2018Model (Python):** El modelo acústico/biofísico core implementado en Python.
*   **Pandas:** Librería estándar para manipulación de datos tabulares (DataFrame). Actúa como la capa de preparación, lectura (CSV, MAT, HDF5), filtrado y estructuración de los datos de entrada y salida del modelo.
*   **NumPy y SciPy:** Infraestructura matemática. **NumPy** provee arrays multidimensionales y operaciones algebraicas vectorizadas. **SciPy** extiende esto con resolución de ecuaciones diferenciales, álgebra lineal avanzada y procesamiento de señales. Ambas sostienen el modelo de Verhulst.
*   **Dask:** Librería de paralelismo y computación distribuida. Divide cómputo intensivo en subconjuntos y los ejecuta simultáneamente sobre múltiples núcleos/nodos. En Verhulst, Dask procesa en paralelo los múltiples canales de fibras nerviosas auditivas.
*   **Plotly (Python) y Matplotlib/Seaborn:** **Plotly Python** genera gráficos interactivos equivalentes a los del Frontend en el *worker*. **Matplotlib/Seaborn** son librerías estáticas de referencia para representaciones gráficas de alta resolución destinadas a reportes o publicaciones sin interactividad.
*   **Docker (Motor Científico):** El modelo de Verhulst presenta dependencias compiladas muy específicas (versiones exactas, binarios de bajo nivel) que hacen compleja su instalación reproducible. Docker encapsula el motor científico completo en una imagen inmutable, garantizando la reproducibilidad total.

### 3.4. Ecosistema LLM y Bibliográfico (Fase 2)
*   **LangChain:** Framework y orquestación del flujo de IA.
*   **ChromaDB:** Vector DB para alojar embeddings de documentos y papers.
*   **DeepSeek R1 + Qwen 2.5:** Modelos LLM *open-source* para el razonamiento y recuperación.
*   **Zotero API:** Interfaz para recuperación automatizada de metadatos de papers.
*   **Ray:** Paralelismo distribuido para clústeres y modelos LLMs (opcional, pero recomendado).

---

## 4. Arquitectura de Flujo (Cómo viajan los datos)

El siguiente esquema sintetiza la secuencia de interacciones entre los componentes del sistema durante un ciclo completo, extendido hasta la interacción de la Fase 2:

### Flujo Completo, Paso a Paso:
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
11. Usuario pregunta: *“¿Cómo se relaciona este EFR con el paper?”*
12. LangChain recupera contexto → LLM (DeepSeek/Qwen)
13. LLM responde → React muestra análisis

### Diagrama de Secuencia Integrado (Infraestructura Core):
```text
[Cliente — Navegador Web]
        |
        | (1) Carga de audiograma
        ▼
[Frontend: React + FilePond]
        |
        | (2) Solicitud HTTP autenticada con token JWT
        ▼
[Backend: FastAPI] ──── Validación de identidad con Supabase Auth
        |
        | (3) Escritura del audiograma en Supabase Storage
        | (4) Registro de tarea de simulación en Redis (vía Celery)
        | (5) Respuesta inmediata al cliente con identificador de tarea
        |
        ▼
[Worker Celery — Contenedor Docker]
        |
        | (6) Lectura del audiograma desde Supabase Storage
        | (7) Ejecución del modelo de Verhulst (NumPy / SciPy / Pandas)
        | (8) Distribución paralela del cómputo con Dask
        | (9) Generación de representaciones gráficas con Plotly Python
        |
        ▼
[Supabase Storage + PostgreSQL]  ← Persistencia de resultados y metadatos
        |
        ▼
[Backend: FastAPI] ──── Notificación de completitud al Frontend
        |
        ▼
[Frontend: Plotly.js] ← Visualización interactiva de los resultados
```

---

## 5. Arquitectura Recomendada (Resumen)

**React + FastAPI + Celery + Verhulst Model + Supabase (Auth + PostgreSQL + Storage) + LangChain + ChromaDB + DeepSeek/Qwen** es la arquitectura ideal para un laboratorio virtual moderno, científico, multiusuario y escalable.

| Tecnología       | Capa                  | Función Principal                                   |
|------------------|-----------------------|-----------------------------------------------------|
| React            | Frontend              | Construcción de interfaces de usuario por componentes |
| TailwindCSS      | Frontend              | Sistema de estilos *utility-first*                  |
| FilePond         | Frontend              | Gestión robusta de carga de archivos                |
| Plotly.js        | Frontend              | Visualización interactiva de datos científicos      |
| pnpm             | Frontend (tooling)    | Gestión eficiente de paquetes Node.js               |
| PDF.js           | Frontend              | Visualización de artículos científicos (*papers*)   |
| FastAPI          | Backend API           | API asíncrona de alto rendimiento en Python         |
| JWT / OAuth2     | Backend API           | Protocolo de autenticación mediante tokens firmados |
| Supabase Auth    | Backend API           | Servicio de autenticación y gestión de identidad    |
| PostgreSQL       | Base de Datos         | Persistencia estructurada de metadatos y registros  |
| Supabase Storage | Almacenamiento        | Repositorio de archivos binarios y resultados       |
| uv               | Backend (tooling)     | Gestión de entornos y dependencias Python           |
| Celery           | Motor Científico      | Sistema de colas de tareas asíncronas               |
| Redis            | Motor Científico      | Intermediario de mensajería en memoria para Celery  |
| Pandas           | Motor Científico      | Manipulación y estructuración de datos tabulares    |
| NumPy / SciPy    | Motor Científico      | Cómputo numérico y algoritmos científicos           |
| Dask             | Motor Científico      | Paralelismo y distribución del cómputo              |
| Plotly (Python)  | Motor Científico      | Generación de gráficos en el entorno del servidor   |
| Matplotlib       | Motor Científico      | Gráficos estáticos para reportes de alta resolución |
| Docker           | Infraestructura       | Contenedorización y reproducibilidad del entorno    |
| LangChain        | Fase 2 (LLM)          | Orquestación de IA y análisis                       |
| ChromaDB         | Fase 2 (LLM)          | Base de datos vectorial para embeddings             |
| DeepSeek / Qwen  | Fase 2 (LLM)          | Modelos de inferencia open-source                   |
| Zotero API       | Fase 2 (LLM)          | Extracción de metadatos bibliográficos              |
| MinIO / DVC      | Almacenamiento        | Reproducibilidad y versionado de datos              |
