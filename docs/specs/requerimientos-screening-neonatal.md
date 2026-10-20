# Casos de Uso y Requerimientos: Screening Neonatal BERA/ABR

> Documento derivado de `analisisScreeningNeonatal.md` y `Integration Points Bera Abr.md`

---

## 1. Casos de Uso

| ID | Nombre | Actor Principal | Descripción | Precondiciones | Postcondiciones |
|----|--------|-----------------|-------------|----------------|-----------------|
| CU-01 | Configurar Simulación con Perfil Pre-computado | Fonoaudiólogo | El usuario selecciona un perfil patológico pre-computado (Flat, Slope o combinado) para definir el estado auditivo del neonato | El sistema tiene acceso a la carpeta `data/Poles/` con perfiles pre-computados | El perfil se carga y está listo para ser usado en la simulación |
| CU-02 | Configurar Simulación con Audiograma Hipotético | Fonoaudiólogo | El usuario ingresa manualmente frecuencias y pérdidas auditivas para crear un perfil personalizado | El usuario tiene conocimientos básicos de audiología | El sistema genera un archivo `StartingPoles.dat` personalizado |
| CU-03 | Configurar Parámetros de Simulación | Fonoaudiólogo | El usuario configura la distribución de fibras del nervio auditivo (nH, nM, nL) y el tipo de estímulo | El perfil auditivo ya está definido (CU-01 o CU-02 completados) | Los parámetros se guardan y se asocian a la simulación |
| CU-04 | Subir Datos BERA Reales | Fonoaudiólogo | El usuario carga un archivo MAT o CSV con datos de BERA real para comparar con la simulación | El usuario tiene un archivo de datos en formato compatible | El archivo se valida y se almacena para overlay en la visualización |
| CU-05 | Ejecutar Simulación | Fonoaudiólogo | El usuario inicia la ejecución del modelo Verhulst | Todos los parámetros de entrada están completos y válidos | La tarea se encola y el frontend muestra estado "Simulando..." |
| CU-06 | Visualizar Resultados de Simulación | Fonoaudiólogo | El usuario ve un gráfico interactivo con las ondas W1, W3, W5 y el ABR compuesto | La simulación se completó exitosamente | El gráfico se renderiza con Plotly.js y está listo para análisis |
| CU-07 | Analizar Presencia/Ausencia de Ondas | Fonoaudiólogo | El usuario identifica si las ondas I, III y V están presentes | El gráfico de resultados está visible | El usuario puede marcar visualmente la presencia/ausencia de cada onda |
| CU-08 | Medir Latencias y Amplitudes | Fonoaudiólogo | El sistema calcula automáticamente latencias absolutas, intervalos interpico y amplitudes | El gráfico de resultados está visible | Se muestra un panel con todas las métricas calculadas |
| CU-09 | Comparar con Valores Normativos Neonatales | Fonoaudiólogo | El usuario compara las métricas calculadas con valores de referencia | El panel de métricas está visible | Se resaltan las desviaciones de los valores normativos |
| CU-10 | Comparar Simulación vs Datos Reales | Fonoaudiólogo | El usuario superpone los datos de BERA reales con la simulación | El usuario completó CU-04 y CU-06 | Ambos conjuntos de datos se muestran en el mismo gráfico |
| CU-11 | Guardar/Exportar Resultados | Fonoaudiólogo | El usuario guarda el gráfico y las métricas para seguimiento | El análisis está completo | Los resultados se almacenan en DB y se pueden exportar como PNG/SVG/CSV |
| CU-12 | Repetir Simulación con Parámetros Diferentes | Fonoaudiólogo | El usuario modifica parámetros y ejecuta una nueva simulación | La primera simulación se completó | Se inicia un nuevo flujo de simulación con los nuevos parámetros |

---

## 2. Requerimientos Funcionales

| ID | Nombre | Descripción | Casos de Uso Relacionados |
|----|--------|-------------|---------------------------|
| RF-01 | Cargar Perfiles Pre-computados | El sistema debe listar y cargar perfiles patológicos desde `data/Poles/` (Flat00 a Flat35, Slope00 a Slope35, y combinados) | CU-01 |
| RF-02 | Validar Audiograma Hipotético | El sistema debe validar que: <ul><li>Las listas `freqs` y `dB` tengan la misma longitud</li><li>Las frecuencias estén en el rango 125-8000 Hz</li><li>Los valores de dB HL estén entre 0 y 120</li></ul> | CU-02 |
| RF-03 | Convertir Audiograma a Polos | El sistema debe usar `ohc_ind()` para convertir un audiograma a un archivo `StartingPoles.dat` personalizado | CU-02 |
| RF-04 | Configurar Parámetros de Fibras | El sistema debe permitir configurar `nH`, `nM`, `nL` con valores enteros y defaults 13/3/3 | CU-03 |
| RF-05 | Seleccionar Tipo de Estímulo | El sistema debe permitir seleccionar entre `click`, `tone_burst` y `RAM` | CU-03 |
| RF-06 | Validar Archivos BERA Reales | El sistema debe validar que los archivos MAT/CSV tengan columnas `time` y `amplitude` | CU-04 |
| RF-07 | Encolar Tareas Asíncronas | El sistema debe usar una cola de tareas (Celery) para ejecutar `model2018()` | CU-05 |
| RF-08 | Notificar Estado de Simulación | El sistema debe notificar al frontend el estado de la tarea (en cola, ejecutándose, completada, error) | CU-05 |
| RF-09 | Renderizar Gráfico Plotly.js | El sistema debe renderizar un gráfico con 4 trazas: W1 (verde), W3 (azul), W5 (violeta), ABR (negro) | CU-06 |
| RF-10 | Detectar Picos Automáticamente | El sistema debe detectar los picos de W1, W3 y W5 y mostrar sus latencias en ms | CU-07, CU-08 |
| RF-11 | Calcular Métricas | El sistema debe calcular: <ul><li>Latencias absolutas W1, W3, W5</li><li>Intervalos interpico I-III, III-V, I-V</li><li>Amplitudes pico-a-pico</li></ul> | CU-08 |
| RF-12 | Mostrar Valores Normativos | El sistema debe mostrar valores normativos neonatales ajustados por edad gestacional y resaltar desviaciones | CU-09 |
| RF-13 | Superponer Datos Reales | El sistema debe superponer los datos de BERA reales como traza punteada | CU-10 |
| RF-14 | Exportar Resultados | El sistema debe permitir exportar: <ul><li>Gráfico como PNG/SVG</li><li>Métricas como CSV/JSON</li></ul> | CU-11 |
| RF-15 | Almacenar Resultados en DB | El sistema debe almacenar en una base de datos: <ul><li>Parámetros de entrada</li><li>Resultados de la simulación</li><li>Métricas calculadas</li><li>Archivos exportados</li></ul> | CU-11 |
| RF-16 | Resetear Parámetros | El sistema debe permitir resetear todos los parámetros para iniciar una nueva simulación | CU-12 |

---

## 3. Requerimientos No Funcionales

| ID | Categoría | Descripción |
|----|-----------|-------------|
| RNF-01 | Rendimiento | El tiempo de carga de perfiles pre-computados debe ser < 1 segundo |
| RNF-02 | Rendimiento | La conversión de audiograma a polos (`ohc_ind()`) debe completarse en < 5 segundos |
| RNF-03 | Rendimiento | El sistema debe manejar múltiples simulaciones en paralelo (al menos 5 concurrentes) |
| RNF-04 | Usabilidad | El formulario de configuración debe ser intuitivo para fonoaudiólogos sin experiencia en programación |
| RNF-05 | Usabilidad | El gráfico Plotly.js debe ser interactivo (zoom, pan, hover con información detallada) |
| RNF-06 | Fiabilidad | El sistema debe manejar errores gracefully (ej: fallo de simulación) y notificar al usuario |
| RNF-07 | Fiabilidad | Los resultados de las simulaciones deben ser reproducibles (mismos parámetros → mismos resultados) |
| RNF-08 | Escalabilidad | El sistema debe poder escalar horizontalmente para manejar más simulaciones concurrentes |
| RNF-09 | Seguridad | Los archivos subidos por el usuario deben ser validados para evitar ejecución de código malicioso |
| RNF-10 | Compatibilidad | El frontend debe ser compatible con navegadores modernos (Chrome ≥ 90, Firefox ≥ 88, Safari ≥ 14) |
| RNF-11 | Disponibilidad | El servicio de simulación debe tener una disponibilidad ≥ 99% durante horas laborales |
| RNF-12 | Mantenibilidad | El código debe estar documentado y seguir convenciones de estilo (PEP8 para Python, ESLint para JS) |

---

## 4. Diagrama de Relación entre Casos de Uso

```mermaid
useCaseDiagram
    actor "Fonoaudiólogo" as Fono
    package "Screening Neonatal BERA/ABR" {
        usecase "CU-01: Configurar con Perfil Pre-computado" as CU01
        usecase "CU-02: Configurar con Audiograma Hipotético" as CU02
        usecase "CU-03: Configurar Parámetros de Simulación" as CU03
        usecase "CU-04: Subir Datos BERA Reales" as CU04
        usecase "CU-05: Ejecutar Simulación" as CU05
        usecase "CU-06: Visualizar Resultados" as CU06
        usecase "CU-07: Analizar Presencia/Ausencia de Ondas" as CU07
        usecase "CU-08: Medir Latencias y Amplitudes" as CU08
        usecase "CU-09: Comparar con Valores Normativos" as CU09
        usecase "CU-10: Comparar vs Datos Reales" as CU10
        usecase "CU-11: Guardar/Exportar Resultados" as CU11
        usecase "CU-12: Repetir Simulación" as CU12
    }
    
    Fono --> CU01
    Fono --> CU02
    CU01 --> CU03 : <<includes>>
    CU02 --> CU03 : <<includes>>
    Fono --> CU04
    CU03 --> CU05 : <<includes>>
    CU05 --> CU06 : <<includes>>
    CU06 --> CU07 : <<includes>>
    CU06 --> CU08 : <<includes>>
    CU08 --> CU09 : <<includes>>
    CU04 --> CU10 : <<extends>>
    CU06 --> CU10 : <<includes>>
    CU07 --> CU11 : <<extends>>
    CU08 --> CU11 : <<extends>>
    CU09 --> CU11 : <<extends>>
    CU10 --> CU11 : <<extends>>
    CU11 --> CU12 : <<extends>>
```
