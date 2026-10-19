# Casos de Uso y Requerimientos: Estudiar Mecanismos Fisiológicos

> Documento derivado de `verhulst-analysis/mecanismos-fisiologicos.md` y `activity-diagrams/mecanismos-fisiologicos.md`

---

## 1. Casos de Uso

| ID | Nombre | Actor Principal | Descripción | Precondiciones | Postcondiciones |
|----|--------|-----------------|-------------|----------------|-----------------|
| CU-01 | Seleccionar Etapa Biológica a Estudiar | Investigador | El usuario elige qué etapa del pipeline de la vía auditiva desea observar como salida del experimento: Velocidad BM, Potencial IHC, Tasas de disparo AN, Respuesta CN, Respuesta IC (W5), o ABR completo (W1, W3, W5) | El usuario ha accedido al módulo "Exploración de Mecanismos Fisiológicos" | El sistema registra el `storeflag` correspondiente a la etapa elegida |
| CU-02 | Configurar Daño en Cóclea (OHC) | Investigador | El usuario selecciona un perfil de polos de Shera (ej. `Flat20`, `Slope15`) para simular una degradación exclusiva de las células ciliadas externas, manteniendo las fibras del nervio auditivo en sus valores normales | CU-01 completado | El sistema carga el array `sheraP` del perfil seleccionado con `nH=13, nM=3, nL=3` por defecto |
| CU-03 | Configurar Daño en Nervio Auditivo (AN) | Investigador | El usuario configura la reducción específica de fibras de alta, media y baja tasa de disparo (`nH`, `nM`, `nL`) manteniendo el perfil coclear sano (`Flat00`) para simular una sinaptopatía pura | CU-01 completado | El sistema registra el set de fibras reducido con `sheraP` de `Flat00` |
| CU-04 | Configurar Estímulo de Entrada | Investigador | El usuario define las características del sonido inyectado: tipo (click, tono puro, RAM), frecuencia portadora, nivel en dB SPL y duración | CU-02 o CU-03 completado | Los parámetros del estímulo quedan asociados a la configuración del experimento |
| CU-05 | Incluir Perfil Sano como Referencia | Investigador | El usuario activa la opción de ejecutar una segunda simulación en paralelo con un oído sano (`Flat00` + fibras normales) para poder comparar visualmente la señal sana vs. la dañada | CU-04 completado | El backend encola dos tareas Celery: una para el perfil dañado y otra para el perfil sano |
| CU-06 | Ejecutar Experimento de Simulación | Investigador | El usuario inicia la ejecución del modelo Verhulst con toda la configuración previa. El sistema valida los parámetros y encola la tarea en el worker Celery del `simulation-service` | CU-04 completado; configuración válida | La tarea se encola; el frontend muestra estado de progreso en tiempo real via WebSocket |
| CU-07 | Visualizar Señal de la Etapa Específica | Investigador | El usuario observa el gráfico interactivo con la señal de la etapa biológica elegida en el paso CU-01: BM (velocidad vs. frecuencia), IHC (potencial vs. tiempo por canal), AN (tasas de disparo o PSTH), CN/IC (ondas temporales), ABR (W1, W3, W5) | CU-06 completado exitosamente | Gráfico Plotly.js renderizado según el tipo de señal solicitado |
| CU-08 | Comparar Señal Sana vs. Patológica | Investigador | Si se eligió incluir el perfil sano (CU-05), el usuario ve ambas señales superpuestas en el mismo gráfico con colores diferenciados para identificar en qué punto del pipeline el daño comienza a distorsionar la señal | CU-05 y CU-06 completados | Superposición de trazas sana (secundaria) y dañada (primaria) en el gráfico |
| CU-09 | Re-ejecutar con Parámetros Modificados | Investigador | El usuario ajusta cualquier parámetro (etapa, tipo de daño, perfil, estímulo) y vuelve a ejecutar para iterar sobre su hipótesis de investigación | Al menos una simulación previa completada | Se inicia un nuevo ciclo de experimentación desde CU-01 o CU-04 según lo que se modifique |
| CU-10 | Exportar Señales y Gráficos | Investigador | El usuario descarga los datos crudos de la etapa observada (array de tiempo y amplitud) en formato CSV y el gráfico en formato PNG o SVG para uso en publicaciones o análisis externos | CU-07 completado | Archivo descargado por el navegador |

---

## 2. Requerimientos Funcionales

| ID | Nombre | Descripción | Casos de Uso Relacionados |
|----|--------|-------------|---------------------------|
| RF-01 | Selección de Storeflag por Etapa | El frontend debe mapear la selección de etapa biológica del usuario a los valores de `storeflag` válidos para `model2018()`: `'b'` (BM), `'i'` (IHC), `'a'` (AN), `'w'` (ondas ABR), o combinaciones. El `core-service` enviará el flag correcto al `simulation-service`. | CU-01 |
| RF-02 | Listado de Perfiles OHC Disponibles | El sistema debe listar todos los perfiles de polos de Shera disponibles en `data/Poles/` (Flat00 a Flat80, Slope15 a Slope80) para que el usuario elija el grado de daño coclear. | CU-02 |
| RF-03 | Aislamiento Paramétrico (OHC vs. AN) | El sistema debe garantizar que cuando el usuario configura daño OHC, las fibras AN se fuercen a sus valores normativos (nH=13, nM=3, nL=3), y viceversa: cuando configura daño AN, el perfil OHC se fuerza a `Flat00`. Esto asegura el aislamiento experimental correcto. | CU-02, CU-03 |
| RF-04 | Validación de Parámetros del Experimento | El `core-service` debe validar que los valores de `nH`, `nM`, `nL` sean enteros no negativos con `nH + nM + nL > 0`, y que el perfil OHC exista en `data/Poles/`. En caso de error, retornar un mensaje descriptivo. | CU-06 |
| RF-05 | Ejecución On-Demand via Celery | El `simulation-service` debe aceptar la tarea de simulación encolada por Celery y ejecutar `model2018()` con el `storeflag` recibido. Si se solicitó perfil sano como referencia (CU-05), debe ejecutar dos instancias de `model2018()` de manera independiente. | CU-05, CU-06 |
| RF-06 | Notificación de Estado via WebSocket | El `core-service` debe notificar al frontend en tiempo real el estado de cada tarea (en cola, ejecutándose, completada, error) mediante WebSocket, dado que las simulaciones on-demand pueden demorar entre 2 y 10 minutos. | CU-06 |
| RF-07 | Renderizado Adaptativo por Tipo de Señal | El frontend debe renderizar el gráfico Plotly.js adecuado según la etapa elegida: (a) BM: eje X = frecuencia coclear, eje Y = velocidad (m/s); (b) IHC/CN/IC: eje X = tiempo (ms), eje Y = potencial (mV); (c) AN: rasterplot o PSTH con tasa de disparo (spikes/s); (d) ABR: eje X = tiempo (ms), eje Y = amplitud (µV). | CU-07 |
| RF-08 | Superposición de Perfiles (Sano vs. Patológico) | Cuando el usuario eligió incluir la referencia sana (CU-05), el gráfico debe superponer la traza del perfil sano (gris punteado, color secundario) y la del perfil dañado (color sólido primario), con leyenda que identifique cada una. | CU-08 |
| RF-09 | Loop de Re-ejecución sin Recarga | El sistema debe permitir al investigador modificar cualquier parámetro y re-ejecutar desde el mismo panel sin necesidad de recargar la página ni perder la configuración actual. | CU-09 |
| RF-10 | Exportación de Datos Crudos y Gráficos | El backend debe empaquetar el array de la señal (tiempo + valores de la etapa observada) en un CSV y proveer el gráfico como PNG/SVG para su descarga desde el frontend. | CU-10 |

---

## 3. Requerimientos No Funcionales

| ID | Categoría | Descripción | Relación con la Arquitectura |
|----|-----------|-------------|------------------------------|
| RNF-01 | Rendimiento | Las simulaciones on-demand de este módulo tienen un tiempo de cómputo esperado de 2 a 10 minutos. No existe una base de datos de perfiles pre-computados para este módulo dado el espacio de parámetros prácticamente infinito (cualquier combinación de storeflag, perfil, fibras y estímulo). | El `simulation-service` (Docker + Celery) es el único camino. No hay atajo de pre-cómputo como en otras funcionalidades. |
| RNF-02 | Experiencia de Usuario durante la Espera | Dado el tiempo de cómputo prolongado, el frontend debe mantener al investigador informado mediante un indicador de progreso en tiempo real (WebSocket) con los estados: "En cola", "Compilando", "Ejecutando (etapa X/N)", "Completado". | Requiere integración de WebSocket en el `core-service`. |
| RNF-03 | Reproducibilidad Científica | El mismo conjunto de parámetros (sheraP, nH, nM, nL, estímulo, storeflag) debe producir siempre los mismos resultados numéricos, para garantizar que el investigador pueda replicar sus experimentos. Los resultados se almacenan en PostgreSQL con hash de parámetros como clave única. | Hereda la propiedad determinista del modelo Verhulst. |
| RNF-04 | Manejo de Errores del Pipeline Verhulst | Si el `simulation-service` falla (ej. error de compilación de `tridiag.so`, memoria insuficiente), el sistema debe registrar el error con stack trace en los logs, notificar al frontend con un mensaje claro y liberar el worker para la próxima tarea de la cola. | Responsabilidad del `simulation-service` + monitor de Celery. |
| RNF-05 | Concurrencia | El `simulation-service` debe poder manejar al menos 2 experimentos de este módulo simultáneamente (cada uno puede generar 2 simulaciones si el usuario eligió incluir el perfil sano). Con 4 workers Celery disponibles esto es factible sin degradación. | Alineado con la capacidad definida en el Plan de Mitigación. |

---

## 4. Diagrama de Relación entre Casos de Uso

```mermaid
useCaseDiagram
    actor "Investigador" as Inv
    package "Exploración de Mecanismos Fisiológicos" {
        usecase "CU-01: Seleccionar Etapa Biológica" as CU01
        usecase "CU-02: Configurar Daño OHC" as CU02
        usecase "CU-03: Configurar Daño AN" as CU03
        usecase "CU-04: Configurar Estímulo" as CU04
        usecase "CU-05: Incluir Perfil Sano" as CU05
        usecase "CU-06: Ejecutar Experimento" as CU06
        usecase "CU-07: Visualizar Señal" as CU07
        usecase "CU-08: Comparar Sano vs. Patológico" as CU08
        usecase "CU-09: Re-ejecutar con Modificaciones" as CU09
        usecase "CU-10: Exportar Señales y Gráficos" as CU10
    }

    Inv --> CU01
    CU01 --> CU02 : <<extends>>
    CU01 --> CU03 : <<extends>>
    CU02 --> CU04 : <<includes>>
    CU03 --> CU04 : <<includes>>
    CU04 --> CU05 : <<extends>>
    CU04 --> CU06 : <<includes>>
    CU05 --> CU06 : <<includes>>
    CU06 --> CU07 : <<includes>>
    CU05 --> CU08 : <<extends>>
    CU07 --> CU09 : <<extends>>
    CU07 --> CU10 : <<extends>>
```
