# Plan de Mitigación de Cuellos de Botella - Screening BERA/ABR

> **Documento relacionado:** [Integration Points Bera Abr.md](./Integration%20Points%20Bera%20Abr.md)
> **Fecha:** 2026-06-24
> **Objetivo:** Detallar un plan técnico para resolver los cuellos de botella del modelo Verhulst integrado al screening BERA/ABR.

---

## 1. Recapitulación de Cuellos de Botella

| Cuello de botella | Severidad | Impacto principal |
|---|---|---|
| Tiempo de cómputo | 🔴 Alta | Experiencia de usuario deficiente (espera de 2-10 min) |
| Librería C compilada (`tridiag.dll`/`tridiag.so`) | 🟡 Media | Falta de portabilidad entre arquitecturas/sistemas operativos |
| Archivos `.mat` requeridos por `ohc_ind()` | 🟡 Media | Riesgo de fallos por archivos faltantes/mal ubicados |
| Multiprocessing interno del modelo | 🟢 Baja | No requiere cambios, es compatible con workers asíncronos |

---

## 2. Plan de Mitigación Detallado

---

### 2.1 Tiempo de cómputo (🔴 Alta Severidad)
Este es el cuello de botella crítico. Se soluciona con **tres capas de optimización**:

#### 2.1.1 Colas de tareas asíncronas (Celery + Redis/RabbitMQ)
- **Herramienta:** Celery (con Redis como broker y backend de resultados)
- **Funcionamiento:**
  1. El frontend envía la solicitud al backend API.
  2. El backend API crea una tarea Celery y la envía a la cola.
  3. El frontend recibe un `task_id` inmediatamente.
  4. Un worker Celery recoge la tarea y ejecuta la simulación (2-10 min).
  5. Cuando la tarea termina, se guarda el resultado en el backend.
- **Ventajas:**
  - Permite escalar horizontalmente (agregar más workers Celery).
  - Desacopla la simulación del ciclo de solicitud-respuesta HTTP.

#### 2.1.2 Pre-computación de perfiles comunes
- **Perfiles a pre-computar:** Los 33 perfiles OHC existentes (`Flat00` a `Flat35`, `Slope00` a `Slope35_5`, combinados) + 4 variantes de fibras AN por perfil:
  1. Normal (`nH=13, nM=3, nL=3`)
  2. Sinaptopatía leve (`nH=7, nM=3, nL=3`)
  3. Sinaptopatía moderada (`nH=4, nM=2, nL=2`)
  4. Sinaptopatía severa (`nH=1, nM=1, nL=1`)
- **Total de perfiles pre-computados:** 33 × 4 = **132 perfiles**
- **Estímulo estándar para pre-computación:** RAM de 4 kHz, 65 dB SPL (el más común en fonoaudiología)
- **Recursos estimados:**
  - 132 simulaciones × 5 min promedio = 660 min (11 horas) en un solo worker.
  - Con 4 workers paralelos: ~2.75 horas.
  - Almacenamiento: ~132 × 1 MB = 132 MB total (solo resultados relevantes: `w1`, `w3`, `w5`, `abr`, `fs_abr`, `time_axis`, `efr`).

#### 2.1.3 Cacheo de resultados
- **Herramienta:** Redis (o la misma base de datos PostgreSQL)
- **Estrategia:**
  - Cada vez que se ejecuta una simulación (pre-computada o on-demand), se guarda el resultado en caché con una clave única:
    ```
    clave = f"sim:{perfil_ohc}:{nH}:{nM}:{nL}:{stimulo_tipo}:{stimulo_params}"
    ```
  - Tiempo de expiración de la caché: 30 días (o indefinido para perfiles pre-computados).

---

### 2.2 Librería C compilada (`tridiag.dll`/`tridiag.so`) (🟡 Media Severidad)
Solucionado con **Dockerización completa del servicio de simulación**:

#### 2.2.1 Dockerfile para el servicio de simulación
```dockerfile
# Usar una imagen base de Python con compilador C
FROM python:3.11-slim-bullseye

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    gfortran \
    make \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código del modelo Verhulst
COPY backend/services/simulation-service/src/Verhulst /app/Verhulst

# Compilar la librería tridiag
RUN cd /app/Verhulst/src/core && make

# Instalar dependencias de Python
COPY backend/services/simulation-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos .mat necesarios
COPY backend/services/simulation-service/src/Verhulst/data/mat files /app/Verhulst/data/mat files
COPY backend/services/simulation-service/src/Verhulst/data/Poles /app/Verhulst/data/Poles

# Comando de inicio (ej: worker Celery)
CMD ["celery", "-A", "simulation_worker", "worker", "--loglevel=info"]
```

- **Ventajas:**
  - Se compila la librería `tridiag` una sola vez para la arquitectura del contenedor (linux/amd64 o linux/arm64).
  - Portabilidad total: funciona en cualquier sistema operativo que soporte Docker.

---

### 2.3 Archivos `.mat` requeridos por `ohc_ind()` (🟡 Media Severidad)
Solucionado con **empaquetado en Docker y acceso garantizado**:

- Los 5 archivos `.mat` (`PoleTrajs.mat`, `cf.mat`, `ModelQ.mat`, `Powerlawpar.mat`, `BWrange.mat`) se copian directamente en la imagen Docker (ver Dockerfile arriba).
- **Alternativa para desarrollo/entornos sin Docker:** Almacenar los archivos en un almacenamiento de objetos (MinIO/S3) y descargarlos automáticamente al iniciar el servicio si no están presentes localmente.

---

### 2.4 Multiprocessing interno del modelo (🟢 Baja Severidad)
**No requiere cambios**:
- El modelo usa `multiprocessing.Pool` internamente para múltiples canales de audio.
- Para el screening BERA (1 solo canal/estímulo), se ejecuta secuencialmente.
- Perfectamente compatible con workers Celery (cada worker ejecuta una simulación completa, y el modelo maneja su propio multiprocessing interno si es necesario).

---

## 3. Base de Datos de Perfiles Pre-computados

### 3.1 Diseño de la Base de Datos (PostgreSQL)
```sql
-- Tabla de perfiles pre-computados
CREATE TABLE precomputed_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_ohc VARCHAR(50) NOT NULL, -- ej: "Flat20", "Slope15"
    nH INTEGER NOT NULL DEFAULT 13,
    nM INTEGER NOT NULL DEFAULT 3,
    nL INTEGER NOT NULL DEFAULT 3,
    stimulus_type VARCHAR(20) NOT NULL, -- ej: "RAM", "click"
    stimulus_params JSONB NOT NULL, -- ej: {"fc": 4000, "fm": 98, "level": 65}
    w1 JSONB NOT NULL, -- Array de floats (µV)
    w3 JSONB NOT NULL,
    w5 JSONB NOT NULL,
    abr JSONB NOT NULL,
    fs_abr REAL NOT NULL,
    time_axis JSONB NOT NULL,
    efr REAL, -- Magnitud del EFR en µV
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(profile_ohc, nH, nM, nL, stimulus_type, stimulus_params)
);

-- Índice para búsquedas rápidas
CREATE INDEX idx_precomputed_profiles ON precomputed_profiles(profile_ohc, nH, nM, nL);
```

### 3.2 Flujo de Pre-computación
1. Crear un script Python `precompute_profiles.py` que:
   - Iterar sobre los 33 perfiles OHC.
   - Iterar sobre las 4 variantes de fibras AN.
   - Generar el estímulo estándar.
   - Ejecutar la simulación.
   - Guardar el resultado en la tabla `precomputed_profiles`.
2. Ejecutar el script en un entorno con recursos suficientes (4 workers Celery).
3. Verificar que todos los 132 perfiles se hayan guardado correctamente.

---

## 4. Arquitectura General del Sistema (Mermaid)
```mermaid
graph TD
    FE[Frontend] -->|POST /simulate/abr + WebSocket| API[Backend API]
    API -->|1. Envía task a cola| Broker[(Redis Broker)]
    API -->|2. Retorna task_id| FE
    Worker[Celery Worker] -->|3. Recoge task| Broker
    Worker -->|4a. Busca en caché/DB| Cache[(Redis Cache)]
    Worker -->|4b. Si no está: ejecuta simulación| Modelo[Modelo Verhulst (Docker)]
    Worker -->|5. Guarda resultado| DB[(PostgreSQL)]
    Worker -->|6. Notifica resultado| Broker
    API -->|7. Escucha notificación| Broker
    API -->|8. Envía resultado por WebSocket| FE
```

---

## 5. Pasos de Implementación (Fases)

### Fase 1: Dockerización y portabilidad
- [ ] Crear el Dockerfile para el servicio de simulación.
- [ ] Probar la compilación de `tridiag` en el contenedor.
- [ ] Probar que el modelo se ejecuta correctamente en Docker.

### Fase 2: Colas de tareas y WebSocket
- [ ] Configurar Celery + Redis en el backend.
- [ ] Implementar el endpoint `/simulate/abr` que crea una tarea Celery.
- [ ] Implementar WebSocket en el backend para notificar resultados.
- [ ] Implementar polling como fallback si WebSocket no está disponible.
- [ ] Probar la integración frontend-backend.

### Fase 3: Pre-computación y cacheo
- [ ] Escribir el script `precompute_profiles.py`.
- [ ] Ejecutar el script y pre-computar los 132 perfiles.
- [ ] Implementar la lógica de caché en el worker Celery.
- [ ] Probar que las solicitudes de perfiles pre-computados se resuelvan instantáneamente.

---

## 6. Conclusión y Siguientes Pasos
- **Resultado esperado:**
  - 90%+ de las solicitudes se resuelven instantáneamente (perfiles pre-computados).
  - Las solicitudes on-demand (audiogramas personalizados) se ejecutan en segundo plano sin bloquear el frontend.
  - Portabilidad total del sistema gracias a Docker.
- **Siguientes pasos inmediatos:**
  1. Empezar con la Fase 1 (Dockerización).
  2. Consultar con el equipo de fonoaudiología para validar los 132 perfiles pre-computados.
  3. Definir el stack técnico exacto del backend (FastAPI, Django, etc.).
