# Análisis de Metas y Mapeo de Datos: Screening Neonatal (BERA/ABR)

> **Caso de uso #9:** Investigación en Screening Neonatal (BERA/ABR)
> **Fecha:** 2026-05-06 | **Revisión:** v2 (2026-05-06 — Verhulst como caja negra)
> **Fuentes:** [Integration Points Bera Abr.md](./Integration%20Points%20Bera%20Abr.md), [functionalitiesOverview.md](../../functionalitiesOverview.md)

---

## 1. Clasificación de la Meta

### Veredicto: **SUB-META del EFR**

El Screening BERA/ABR es una **Sub-meta** de la Meta Principal "Simulación EFR mediante modelo Verhulst". No es independiente ni es meta principal por sí misma.

### Justificación Anatómica y de Código

**Relación anatómica EFR ↔ ABR:**

| Aspecto | EFR (Meta Principal) | ABR/BERA (Sub-meta) |
|---|---|---|
| **Qué mide** | Sincronización neural con la *envolvente* del estímulo | Respuesta evocada a estímulos transitorios (clics/tonos breves) |
| **Señal de interés** | `EFR = W1 + W3 + W5` (suma compuesta) | `W1`, `W3`, `W5` **individuales** (latencia y amplitud por onda) |
| **Pipeline del modelo** | `stim → cóclea → IHC → AN → CN → IC → W1+W3+W5` | **Exactamente el mismo pipeline** |
| **Función orquestadora** | `model2018()` | `model2018()` — **la misma** |
| **Diferencia real** | Análisis de magnitud espectral del EFR compuesto | Análisis temporal de morfología, latencia y amplitud de ondas individuales |

**Implicancia en reutilización de código:**

La cadena computacional es **idéntica**. Ambos casos usan:
- `ohc_ind()` → conversión de perfil auditivo a polos de Shera
- `model2018()` → simulación completa con `storeflag='bw'`, `fc='abr'`
- Salidas `output.w1`, `output.w3`, `output.w5`

Lo que cambia es **exclusivamente la capa de presentación y análisis post-simulación**:
- EFR → FFT del compuesto, magnitud espectral a la frecuencia de modulación
- ABR → visualización temporal de ondas individuales, medición de latencias pico I-III-V, amplitudes

> [!IMPORTANT]
> Esto significa que el `simulation-service` no necesita un endpoint nuevo para ABR. El mismo endpoint de simulación sirve para ambos. La diferenciación ocurre en el **frontend** (qué gráfico renderiza) y opcionalmente en un servicio de análisis post-procesamiento.

### Taxonomía resultante

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Screening Neonatal BERA/ABR  ← esta
├── Sub-meta: Sordera Oculta (Sinaptopatía)
├── Sub-meta: Optimización de Estímulos
├── Sub-meta: Generación de Datos Sintéticos (ML)
└── Sub-meta: Validación contra datos reales
```

---

## 2. Mapeo de E/S y Flujo de Datos

### Consideración clínica clave: El neonato no responde audiometrías

En un adulto, el flujo estándar es: `audiograma clínico → ohc_ind() → polos → simulación`.

En un **neonato**, no existe audiograma conductual. Por lo tanto, los inputs son:
1. **Perfiles patológicos paramétricos pre-computados** (Flat/Slope) que representan hipótesis de pérdida
2. **Datos crudos en MAT/CSV** importados de equipos BERA reales (para validación/comparación)

### 2.1. Entradas

| # | Input | Origen | Formato | Destino en código |
|---|---|---|---|---|
| **E1** | Perfil patológico del neonato | Selección de UI (dropdown/slider) | `string` → nombre de perfil pre-computado (ej. `"Flat20"`, `"Slope15"`) | `np.loadtxt(f'data/Poles/{perfil}/StartingPoles.dat')` → `sheraP` |
| **E2** | Audiograma hipotético personalizado (opcional) | Formulario paramétrico en frontend | `{freqs: float[], dB: float[]}` JSON | `ohc_ind(name, hl_freqs_hz, hl_db, base_dir, show_figs=False)` |
| **E3** | Configuración de fibras AN | Sliders o presets en UI | `{nH: int, nM: int, nL: int}` JSON | Parámetros de `model2018()` |
| **E4** | Tipo de estímulo | Selector en UI | `string` → `"click"` / `"tone_burst"` / `"RAM"` | Generación de `np.ndarray` 1D como `sign` |
| **E5** | Datos BERA reales (opcional, para comparación) | Upload de archivo | `.mat` o `.csv` con columnas `time, amplitude` | Pandas → overlay en gráfico Plotly |
| **E6** | Metadatos del caso | Formulario | `{nombre_caso: str, notas: str, edad_gestacional?: int}` | PostgreSQL → tabla `simulations` |

> [!NOTE]
> **E1 y E2 son mutuamente excluyentes.** El sistema presenta una bifurcación: o se usa un perfil pre-computado, o se construye uno personalizado. Nunca ambos.

### 2.2. Proceso (Ciclo de vida de datos)

```
[Capa]              [Acción]                              [Dato transformado]
─────────────────────────────────────────────────────────────────────────────
Controlador     →   Recibe POST /simulate/abr             JSON request body
                →   Valida schema (Pydantic)               SimulationRequest DTO
                →   Delega a servicio                      —

Servicio        →   Determina fuente de polos              perfil | audiograma
                →   Si audiograma: ohc_ind()               → StartingPoles.dat (1001 floats)
                →   Si perfil: np.loadtxt()                → sheraP ndarray (1001,)
                →   Genera estímulo                        → stim ndarray 1D
                →   Encola tarea Celery                    → task_id

Worker          →   model2018(stim, fs, sheraP, ...)       — [2-10 min CPU]
                →   Extrae w1, w3, w5                      3x ndarray (N_samples,)
                →   Calcula ABR compuesto                  w1+w3+w5
                →   Calcula eje temporal                   t = arange(N) / fs_abr
                →   Serializa a JSON                       dict con listas

Controlador     →   Retorna JSON al frontend               SimulationResponse DTO
```

### 2.3. Salidas

| # | Output | Formato API (JSON) | Uso en Frontend (Plotly.js) |
|---|---|---|---|
| **S1** | Onda W1 (Nervio Auditivo) | `w1: float[]` | Traza individual, color verde |
| **S2** | Onda W3 (Núcleo Coclear) | `w3: float[]` | Traza individual, color azul |
| **S3** | Onda W5 (Colículo Inferior) | `w5: float[]` | Traza individual, color violeta |
| **S4** | ABR compuesto | `abr: float[]` | Traza superpuesta principal |
| **S5** | Frecuencia de muestreo | `fs: float` (típico: 20000 Hz) | Escalado del eje X |
| **S6** | Eje temporal | `time_axis: float[]` (segundos) | Eje X del gráfico |
| **S7** | Frecuencias características | `cf: float[]` | Tooltip informativo |
| **S8** | Metadatos de simulación | `{simulation_id, status, params_used, duration_s}` | Panel de estado |

**Transformación a gráficos interactivos (Plotly.js):**

El frontend recibe los arrays crudos y construye:
1. **Gráfico principal:** 4 trazas superpuestas (W1, W3, W5, ABR) vs. tiempo (ms)
2. **Marcadores interactivos:** Picos de latencia (I, III, V) detectados automáticamente con anotaciones hover
3. **Panel de métricas:** Latencia absoluta W1/W3/W5, intervalos interpico I-III / III-V / I-V, amplitudes pico
4. **Overlay opcional:** Si se subió BERA real (E5), se superpone como traza punteada para comparación

---

## 3. Secuencia para el Diagrama de Actividad (DA)

### Nomenclatura para el diagrama

- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `║` = Barra de sincronización (fork/join)
- `╔═══╗` = Actividad compuesta (caja negra, ver subdiagrama)

### Flujo principal (Verhulst como caja negra)

> [!NOTE]
> El pipeline del modelo Verhulst (paso 10) se trata como una **actividad opaca** desde la perspectiva del caso de uso. El actor (fonoaudiólogo) solo interactúa con la entrada de parámetros y la visualización de resultados. El detalle interno se documenta en el [Subdiagrama: Pipeline de Simulación Verhulst](#subdiagrama-pipeline-de-simulación-verhulst).

```
[●] INICIO
  │
  ▼
[1. Fonoaudiólogo accede al módulo "Screening BERA/ABR"]
  │
  ▼
[2. Sistema presenta formulario de configuración]
  │
  ▼
<3. ¿Cómo define el perfil auditivo del neonato?>
  │                                    │
  │ [Perfil pre-computado]             │ [Audiograma hipotético]
  ▼                                    ▼
[3a. Selecciona perfil               [3b. Ingresa frecuencias (Hz)
 del catálogo (Flat/Slope)]           y pérdidas (dB HL) manualmente]
  │                                    │
  │                                    ▼
  │                              [3b.1 Sistema valida:
  │                               - misma longitud freq/dB
  │                               - rango válido (125-8000 Hz)
  │                               - dB HL entre 0 y 120]
  │                                    │
  │                                    ▼
  │                              <3b.2 ¿Validación OK?>
  │                                │           │
  │                                │ Sí        │ No
  │                                │           ▼
  │                                │    [Mostrar error,
  │                                │     volver a 3b]
  │                                │
  ▼                                ▼
[4. Configura fibras AN: nH, nM, nL (sliders con defaults 13/3/3)]
  │
  ▼
[5. Selecciona tipo de estímulo (click / tone burst / RAM)]
  │
  ▼
<6. ¿Tiene datos BERA reales para comparar?>
  │                         │
  │ No                      │ Sí
  │                         ▼
  │                   [6a. Sube archivo MAT/CSV]
  │                         │
  │                         ▼
  │                   <6b. ¿Formato válido?>
  │                     │           │
  │                     │ Sí        │ No
  │                     │           ▼
  │                     │    [Mostrar error formato,
  │                     │     volver a 6a]
  │                     │
  ▼                     ▼
[7. Fonoaudiólogo presiona "Ejecutar Simulación"]
  │
  ▼
[8. Controlador valida request completo (Pydantic schema)]
  │
  ▼
<9. ¿Request válido?>
  │           │
  │ Sí        │ No → [Retornar HTTP 422 + detalle de error] → FIN
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  10. PIPELINE DE SIMULACIÓN VERHULST (CAJA NEGRA)          ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: perfil auditivo, config fibras, tipo estímulo    ║
║  Salida:  w1[], w3[], w5[], abr[], time_axis[], fs, cf[]   ║
║                                                             ║
║  Ver subdiagrama para detalle interno                       ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error
  │            ▼
  │      [10a. Registrar error en DB,
  │       notificar frontend → "Error en simulación"] → FIN
  │
  ▼
[11. Frontend recibe notificación de completitud (polling / WebSocket)]
  │
  ▼
[12. Plotly.js renderiza gráfico interactivo con 4 trazas (W1, W3, W5, ABR)]
  │
  ▼
<13. ¿Se subieron datos BERA reales (E5)?>
  │                    │
  │ No                 │ Sí
  │                    ▼
  │              [13a. Superponer traza BERA real
  │               como línea punteada en el gráfico]
  │                    │
  ▼                    ▼
[14. Sistema calcula automáticamente:
     - Latencias pico W1, W3, W5 (ms)
     - Intervalos interpico I-III, III-V, I-V (ms)
     - Amplitudes pico-a-pico (µV)]
  │
  ▼
[15. Fonoaudiólogo analiza visualmente las ondas I, III y V:
     - Identifica presencia/ausencia de cada onda
     - Evalúa morfología y replicabilidad
     - Compara latencias contra valores normativos neonatales
     - Interpreta si el perfil patológico explica la deformación]
  │
  ▼
<16. ¿Desea ejecutar otra simulación con parámetros diferentes?>
  │                    │
  │ No                 │ Sí → volver a paso 3
  │
  ▼
[17. Fonoaudiólogo guarda/exporta resultados (opcional)]
  │
  ▼
[●] FIN
```

### Resumen de bifurcaciones del DA principal

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 3 | Fuente del perfil auditivo | Pre-computado → selección directa | Audiograma hipotético → validación |
| 6 | ¿Datos BERA reales? | No → continuar | Sí → upload + validación formato |
| 9 | ¿Request válido? | Sí → continuar | No → HTTP 422, fin |
| 10 | Pipeline Verhulst (caja negra) | OK → continuar | Error → registrar, notificar, fin |
| 13 | ¿Overlay BERA real? | No → solo simulado | Sí → superponer traza |
| 16 | ¿Otra simulación? | No → guardar/fin | Sí → loop a paso 3 |

---

### Subdiagrama: Pipeline de Simulación Verhulst

> [!IMPORTANT]
> Este subdiagrama detalla la actividad **10** del DA principal. Representa las operaciones internas que el sistema ejecuta de forma opaca para el fonoaudiólogo. Desde la perspectiva del caso de uso, todo esto es una **caja negra** cuya interfaz contractual es: recibe parámetros de simulación, devuelve ondas ABR o un error.

```
[●] INICIO (entrada desde DA principal, paso 10)
  │
  ▼
[S1. Servicio determina fuente de polos de Shera]
  │
  ▼
<S2. ¿Perfil pre-computado o audiograma custom?>
  │                                    │
  │ Pre-computado                      │ Custom
  ▼                                    ▼
[S2a. np.loadtxt(                    [S2b. ohc_ind(name, freqs,
 Poles/{perfil}/                       dB, base_dir,
 StartingPoles.dat)]                   show_figs=False)]
  │                                    │
  │                                    ▼
  │                              [S2b.1 Lee StartingPoles.dat
  │                               generado por ohc_ind()]
  │                                    │
  ▼                                    ▼
[S3. sheraP: ndarray (1001,) disponible]
  │
  ▼
[S4. Genera estímulo acústico (click/tone/RAM → ndarray 1D)]
  │
  ▼
[S5. Encola tarea Celery con parámetros completos]
  │
  ▼
[S6. Retorna task_id al frontend → UI muestra "Simulando..." con progress]
  │
  ▼
[S7. Worker Celery ejecuta model2018(stim, fs, sheraP, nH, nM, nL,
     fc='abr', storeflag='bw')]        ──── [2-10 min CPU]
  │
  ▼
<S8. ¿Simulación completada sin error?>
  │                    │
  │ Sí                 │ No → [Retornar señal de error al DA principal] → FIN
  │
  ▼
[S9. Extraer output.w1, output.w3, output.w5, output.fs_abr]
  │
  ▼
[S10. Calcular ABR = w1 + w3 + w5, time_axis = arange(N) / fs_abr]
  │
  ▼
[S11. Serializar a JSON {w1[], w3[], w5[], abr[], fs, time_axis[], cf[]}]
  │
  ▼
[S12. Persistir resultado en DB + Storage, actualizar estado tarea]
  │
  ▼
[●] FIN (retorna resultado al DA principal → paso 11)
```

**Bifurcaciones del subdiagrama:**

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| S2 | Tipo de polos | Pre-computado → `np.loadtxt` | Custom → `ohc_ind()` |
| S8 | ¿Simulación OK? | Sí → extraer y serializar | No → señal de error al DA principal |

---

## 4. Notas para Implementación

> [!TIP]
> **Reutilización máxima:** El endpoint `POST /simulate/abr` puede ser un alias o variante del endpoint EFR genérico. La única diferencia es que el frontend envía un flag `mode: "abr"` que indica al servicio usar `storeflag='bw'` y `fc='abr'`, y al frontend renderizar ondas individuales en vez del espectro EFR.

> [!WARNING]
> **Tiempo de cómputo:** La simulación toma 2-10 minutos. El DA debe reflejar que entre el paso 10 (pipeline caja negra, internamente S5→S6) y el 11 (notificación frontend) hay una espera asíncrona real. El frontend debe implementar polling o WebSocket.
