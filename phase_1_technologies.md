# Conceptos Fundamentales — Fase 1: Infraestructura y Motor Científico

Este documento constituye una guía conceptual sobre el *stack* tecnológico adoptado en la **Fase 1** del Laboratorio Virtual Auditivo. Su propósito no es servir como manual de uso, sino establecer una comprensión precisa de los principios que rigen cada tecnología seleccionada, habilitando a todos los integrantes del equipo —independientemente de su perfil técnico— a interpretar correctamente las decisiones de arquitectura y el flujo de datos del sistema.

---

## Conceptos Transversales

Antes de abordar cada componente de forma individual, es necesario establecer tres conceptos estructurales que atraviesan todas las capas del sistema.

### Interfaz de Programación de Aplicaciones (API)

Una **API** (*Application Programming Interface*) es un contrato formal de comunicación entre dos sistemas de software. Define de manera precisa qué operaciones pueden solicitarse, qué parámetros deben acompañar cada solicitud y qué formato tendrá la respuesta, sin exponer los detalles internos de implementación del sistema receptor.

En la presente plataforma, el Frontend se comunica con el Backend de forma exclusiva a través de una API REST. Esta separación garantiza que ambas capas puedan evolucionar de forma independiente sin alterar la interfaz de intercambio.

### Arquitectura Orientada a Servicios (SOA)

En lugar de un sistema monolítico —donde toda la lógica reside en un único bloque de código—, la plataforma se estructura en **servicios especializados** que se comunican entre sí a través de interfaces definidas. Cada servicio tiene una responsabilidad acotada y puede escalar, actualizarse o reemplazarse de forma autónoma sin afectar el conjunto del sistema.

### Contenedor (Docker)

Un **contenedor** es una unidad de empaquetado de software que incluye el código de una aplicación junto con todas sus dependencias, configuraciones y versiones de entorno de ejecución. Su principal atributo es la **portabilidad**: un contenedor se comporta de manera idéntica en cualquier máquina donde se ejecute, eliminando las inconsistencias originadas por diferencias entre entornos de desarrollo, prueba y producción.

---

## 1. Frontend (Interfaz Científica)

La capa de Frontend constituye la interfaz de interacción directa con el usuario. Se ejecuta íntegramente en el navegador del cliente y es responsable de la organización de la experiencia de usuario, la carga de archivos y la visualización de resultados.

### React

**React** es una biblioteca de JavaScript orientada a la construcción de interfaces de usuario. Su unidad fundamental es el **componente**: una pieza de interfaz encapsulada, reutilizable e independiente (un formulario, un gráfico, un panel de control) que puede combinarse con otras para conformar la aplicación completa. React gestiona de forma eficiente la actualización del estado visual ante cambios en los datos subyacentes, sin necesidad de recargar la página en su totalidad.

Es el estándar prevalente en el desarrollo de *Single Page Applications* (SPA) y cuenta con un ecosistema de herramientas y librerías que facilita la construcción de interfaces científicas complejas de manera ordenada y mantenible.

### TailwindCSS

**TailwindCSS** es un framework de CSS basado en el paradigma *utility-first*. En lugar de definir estilos en hojas de estilo externas, los estilos se aplican directamente en el marcado mediante clases de propósito único y predefinidas. Este enfoque favorece la consistencia visual a lo largo de toda la aplicación y reduce la superficie de código CSS personalizado que debe mantenerse.

### FilePond

**FilePond** es una librería de JavaScript especializada en la gestión del proceso de carga de archivos desde el navegador. Implementa mecanismos de validación de formato y peso, previsualización, indicación de progreso y recuperación ante errores de red, ofreciendo una experiencia de carga robusta sin requerir desarrollo ad hoc de estas funcionalidades.

Su adopción responde a la naturaleza de los archivos de entrada del sistema (audiogramas en formatos MAT, CSV o WAV), cuya carga exige un manejo fiable y con retroalimentación visual al usuario.

### Plotly.js

**Plotly.js** es una librería de visualización científica para entornos web. Permite renderizar gráficos interactivos —con capacidades de zoom, desplazamiento, selección de rangos y exportación— a partir de datos numéricos, siendo particularmente adecuada para series temporales, espectros de frecuencia y matrices de resultados.

Su ecosistema es compartido con Plotly para Python, lo que garantiza coherencia entre los gráficos generados en el backend y los renderizados en el frontend.

### pnpm

**pnpm** es un gestor de paquetes para el ecosistema JavaScript/Node.js. Su diferencia central respecto a alternativas como `npm` o `yarn` reside en su modelo de almacenamiento: en lugar de duplicar las dependencias por proyecto, mantiene un único almacén global enlazado simbólicamente, reduciendo significativamente el espacio en disco y los tiempos de instalación. Esto es especialmente relevante en proyectos con dependencias de gran tamaño, como es el caso de las librerías de visualización científica.

---

## 2. Backend y Base de Datos (Capa Central y APIs)

El Backend actúa como la capa de mediación central del sistema. Recibe todas las solicitudes del Frontend, valida su autenticidad, orquesta las operaciones contra las bases de datos y delega el procesamiento científico al motor de simulación.

### FastAPI (Python)

**FastAPI** es un framework web para Python orientado a la construcción de APIs de alto rendimiento. Su arquitectura es nativa e **asíncrona**: puede procesar múltiples solicitudes concurrentes sin bloquearse a la espera de que cada operación de entrada/salida (lectura de base de datos, escritura en storage) complete antes de atender la siguiente.

Su adopción está justificada por dos razones: primero, su rendimiento es comparable al de frameworks construidos sobre lenguajes compilados; segundo, al estar implementado en Python, comparte el ecosistema de librerías con el motor científico, simplificando la integración entre ambas capas.

### JWT y OAuth2

**JWT** (*JSON Web Token*) es un estándar de formato para tokens de seguridad. Tras una autenticación exitosa, el sistema emite al usuario un token firmado digitalmente que codifica su identidad y permisos. En solicitudes subsiguientes, el cliente presenta dicho token como credencial, permitiendo al servidor verificar la identidad sin necesidad de consultar el repositorio de usuarios en cada petición.

**OAuth2** es el protocolo estándar que regula el flujo de emisión, presentación y validación de estos tokens. Define los roles (servidor de autorización, servidor de recursos, cliente) y los flujos de intercambio que garantizan la seguridad del proceso de autenticación.

### Supabase Auth

**Supabase Auth** es un servicio de autenticación completo —registro, inicio de sesión, recuperación de credenciales y soporte OAuth2— construido sobre los estándares JWT/OAuth2 descritos anteriormente. Su adopción exime al equipo de implementar y mantener la infraestructura de autenticación desde cero, un dominio de alta complejidad y riesgo de seguridad.

### PostgreSQL (a través de Supabase)

**PostgreSQL** es un sistema de gestión de bases de datos relacionales de código abierto. Los datos se organizan en tablas con filas y columnas interrelacionadas mediante claves, permitiendo consultas complejas, transacciones seguras y garantías de integridad referencial. Soporta tipos de datos avanzados como arrays y estructuras JSON, lo que lo hace adecuado tanto para metadatos estructurados como para registros semi-estructurados.

En el sistema, PostgreSQL almacena los datos de usuarios, los parámetros de configuración de cada simulación, el historial de resultados y las referencias a los archivos binarios alojados en el servicio de almacenamiento.

### Supabase Storage

**Supabase Storage** es un servicio de almacenamiento de objetos binarios, funcionalmente equivalente a soluciones como AWS S3. Está diseñado para alojar archivos de gran tamaño —audiogramas de entrada, resultados de simulación en formato MAT/CSV, gráficos exportados— que no es eficiente ni apropiado almacenar directamente en una base de datos relacional. Los archivos se referencian desde PostgreSQL mediante su URL de acceso.

### uv

**uv** es un gestor de entornos virtuales y dependencias para Python. Resuelve el árbol de dependencias con menor latencia que las herramientas tradicionales basadas en `pip`, y crea entornos de ejecución aislados que garantizan que los paquetes requeridos por cada servicio no interfieran entre sí. Su adopción es particularmente relevante en el contexto del motor científico, donde las dependencias de machine learning y cómputo numérico son numerosas y de versiones específicas.

---

## 3. Motor Científico (Servicio de Simulación)

El Motor Científico constituye el subsistema de procesamiento intensivo de la plataforma. Su función es ejecutar el modelo de simulación biológica de *Verhulst et al.* a partir de los audiogramas de entrada, produciendo los resultados numéricos y gráficos que el usuario visualizará en el Frontend.

### Procesamiento Asíncrono y Colas de Tareas

Las simulaciones biológicas de alta complejidad tienen tiempos de ejecución que exceden ampliamente la ventana de respuesta tolerable para una solicitud HTTP estándar. La solución arquitectónica a este problema es el **procesamiento asíncrono mediante colas de tareas**: al recibir una solicitud de simulación, el Backend no ejecuta el proceso directamente sino que lo registra en una cola y responde de inmediato con un identificador de tarea. Un proceso independiente (*worker*) consume la tarea de la cola y la ejecuta en segundo plano, notificando su completitud al finalizar.

### Celery

**Celery** es el sistema de gestión de colas de tareas (*task queue*) adoptado para implementar el patrón descrito anteriormente. Permite definir funciones Python como tareas asíncronas, encolarlas desde el Backend y distribuirlas entre uno o varios procesos *workers* que las ejecutan de forma independiente. Soporta reintentos automáticos, monitoreo de estado y encadenamiento de tareas.

### Redis

**Redis** es un sistema de almacenamiento de datos en memoria (*in-memory data store*). A diferencia de PostgreSQL, no está optimizado para persistir grandes volúmenes de datos relacionales, sino para ejecutar operaciones de lectura y escritura a latencias de microsegundos sobre estructuras de datos simples. En el contexto del motor científico, Redis opera como el intermediario de mensajería (*broker*) de Celery: es el repositorio donde se registran las tareas en cola, su estado y sus resultados intermedios.

### Pandas

**Pandas** es la librería Python estándar para la manipulación y análisis de datos tabulares mediante la abstracción del *DataFrame*. Provee herramientas para la lectura de archivos en múltiples formatos (CSV, MAT, HDF5), la transformación y filtrado de datos, y la exportación de resultados. En el pipeline de simulación, Pandas actúa como la capa de preparación y estructuración de los datos de entrada y salida del modelo.

### NumPy y SciPy

**NumPy** es la librería fundamental para el cómputo numérico en Python. Provee estructuras de datos multidimensionales de alto rendimiento (*arrays* y matrices) y operaciones algebraicas vectorizadas que son la base de prácticamente toda la computación científica en el ecosistema Python.

**SciPy** extiende NumPy con implementaciones de algoritmos científicos de mayor nivel: resolución de ecuaciones diferenciales ordinarias y parciales, álgebra lineal avanzada, procesamiento de señales y estadística. Ambas librerías constituyen la infraestructura matemática sobre la que se implementa el modelo de *Verhulst et al.*

### Dask

**Dask** es una librería de paralelismo y computación distribuida para Python. Su función es dividir operaciones de cómputo intensivo en subconjuntos independientes y ejecutarlos de forma simultánea sobre múltiples núcleos del procesador o múltiples nodos de un clúster, reduciendo el tiempo total de ejecución de forma proporcional a los recursos disponibles.

En el contexto del modelo de Verhulst, Dask permite procesar en paralelo los múltiples canales de fibras nerviosas auditivas que componen una simulación completa, transformando lo que sería una operación secuencial en una ejecución distribuida de significativamente menor duración.

### Plotly (Python) y Matplotlib/Seaborn

**Plotly para Python** es la contraparte del lado del servidor de Plotly.js. Permite generar gráficos interactivos equivalentes a los del Frontend ejecutando el proceso de renderizado en el *worker* de simulación, produciendo como salida archivos HTML exportables o imágenes en formato PNG.

**Matplotlib** y su extensión estadística **Seaborn** son las librerías de visualización estática de referencia en el ecosistema científico Python. Se reservan para la generación de representaciones gráficas de alta resolución destinadas a reportes o publicaciones, donde la interactividad no es un requisito.

### Docker (aplicado al Motor Científico)

El modelo de *Verhulst et al.* presenta un conjunto de dependencias compiladas de alta especificidad —versiones exactas de librerías, binarios de bajo nivel, configuraciones de entorno— que hacen particularmente compleja su instalación manual reproducible. Docker resuelve este problema encapsulando el motor científico completo en una imagen inmutable que puede desplegarse de forma idéntica en cualquier entorno de ejecución, garantizando la reproducibilidad de los resultados de simulación independientemente de la infraestructura subyacente.

---

## Flujo Integrado de Datos

El siguiente esquema sintetiza la secuencia de interacciones entre los componentes del sistema durante un ciclo completo de simulación:

```
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

## Tabla Resumen

| Tecnología       | Capa                  | Función Principal                                   |
|------------------|-----------------------|-----------------------------------------------------|
| React            | Frontend              | Construcción de interfaces de usuario por componentes |
| TailwindCSS      | Frontend              | Sistema de estilos *utility-first*                  |
| FilePond         | Frontend              | Gestión robusta de carga de archivos                |
| Plotly.js        | Frontend              | Visualización interactiva de datos científicos      |
| pnpm             | Frontend (tooling)    | Gestión eficiente de paquetes Node.js               |
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
| Docker           | Infraestructura       | Contenedorización y reproducibilidad del entorno    |

---

> **Nota:** Las tecnologías correspondientes al ecosistema de Inteligencia Artificial y Análisis Bibliográfico (LangChain, ChromaDB, DeepSeek, Zotero, PDF.js, Ray) pertenecen a la **Fase 2** del proyecto y serán documentadas en su oportunidad.