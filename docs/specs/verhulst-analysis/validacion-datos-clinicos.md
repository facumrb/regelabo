# Análisis Verhulst: Validar Modelos con Datos Clínicos Reales

> **Caso de uso #5:** Validar modelos con datos clínicos reales
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra con Config. Externa — `ohc_ind()` como puente audiograma real → simulación**

Esta funcionalidad requiere el uso de `ohc_ind()` (la función de conversión de audiograma a polos de Shera) para generar un perfil coclear personalizado desde el audiograma real del paciente. El modelo `model2018()` se invoca con ese perfil sin ninguna modificación interna. La pieza clave es la **fidelidad de la réplica del estímulo**: el estímulo usado en la simulación debe replicar exactamente el estímulo del equipo clínico real.

---

## 2. Entradas al Modelo

| Parámetro | Origen | Función/Archivo | Descripción |
|---|---|---|---|
| `sheraP` | Audiograma real del paciente → `ohc_ind(name, hl_freqs_hz, hl_db, base_dir)` | `OHC_ind.py` → `model2018()` | Perfil coclear derivado del audiograma clínico real |
| `nH`, `nM`, `nL` | Default normativo o ajustado por investigador | `model2018()` | Fibras AN — inicialmente normativas, ajustables si hay sospecha de sinaptopatía |
| `sign` | Réplica del estímulo del equipo clínico (RAM, click, tono) | `model2018()` | Debe replicar exactamente el estímulo usado durante la medición real |
| `fs` | Del estímulo replicado | `model2018()` | Debe coincidir con la fs del equipo clínico o normalizar |
| `storeflag` | `'bw'` (si se compara ABR) o `'efr'` (si se compara EFR) | `model2018()` | Según tipo de señal clínica disponible |
| `fc` | `'abr'` (ABR) o array de frecuencias (EFR) | `model2018()` | Según tipo de señal clínica |

### Uso de `ohc_ind()` — Función de conversión audiograma → polos

```python
# Flujo de datos de la conversión
audiogram = {
    "freqs_hz": [250, 500, 1000, 2000, 4000, 8000],  # Del equipo de audiometría real
    "dB_HL":    [10,  15,   20,   30,   45,   60]     # Umbrales medidos
}

# ohc_ind() genera un archivo StartingPoles.dat en el directorio del paciente
ohc_ind(
    name=patient_id,
    hl_freqs_hz=audiogram["freqs_hz"],
    hl_db=audiogram["dB_HL"],
    base_dir=simulation_data_dir,
    show_figs=False
)

# Luego se carga como sheraP
sheraP = np.loadtxt(f'{simulation_data_dir}/{patient_id}/StartingPoles.dat')
```

---

## 3. Salidas del Modelo Consumidas

| Output | Nombre en código | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| ABR compuesto simulado | `output.w1 + output.w3 + output.w5` | ndarray float | Traza a comparar vs. ABR real del paciente |
| Onda W1 | `output.w1` | ndarray float | Comparación de latencia nervio auditivo |
| Onda W3 | `output.w3` | ndarray float | Comparación de latencia núcleo coclear |
| Onda W5 | `output.w5` | ndarray float | Comparación de latencia colículo inferior |
| EFR (si aplica) | FFT de compuesto a fm | float (µV) | Si la señal real es EFR: comparar amplitud EFR |

### Métricas de concordancia calculadas post-simulación

| Métrica | Descripción | Umbral de "buen ajuste" (referencia) |
|---|---|---|
| Correlación de Pearson | Similitud morfológica señal simulada vs. real | r > 0.85 |
| RMS Error (µV) | Error cuadrático medio punto a punto | < 20% de la amplitud pico real |
| ΔLatencia W1 (ms) | Diferencia latencia pico | < ±0.5 ms |
| ΔLatencia W3 (ms) | Diferencia latencia pico | < ±0.5 ms |
| ΔLatencia W5 (ms) | Diferencia latencia pico | < ±0.5 ms |
| ΔEFR (µV) | Diferencia amplitud EFR | < ±20% |

---

## 4. Interfaz API Requerida

| Endpoint | Método | Descripción |
|---|---|---|
| `/simulate/validate` | POST | Simulación personalizada (audiograma real → ohc_ind → model2018) |
| `/simulate/validate/{task_id}` | GET | Polling del resultado |
| `/validate/compare` | POST | Subir señal real + resultado simulado → calcular métricas de concordancia |

### DTO de Request

```python
class ValidationSimulationRequest(BaseModel):
    # Audiograma real del paciente
    audiogram: AudiogramDTO                  # {freqs_hz: [250, 500, ...], dB_HL: [10, 15, ...]}
    patient_id: str                          # Identificador del paciente para persistencia

    # Configuración de fibras AN
    n_fibers: FibersConfig = FibersConfig()  # Default normativo

    # Estímulo (debe replicar el del equipo clínico)
    stimulus: StimulusConfig

    # Señal clínica real para comparación (puede subirse ahora o después)
    real_signal_url: str | None = None       # URL al archivo MAT/CSV ya subido
    real_fs_hz: float | None = None          # fs del equipo clínico

    metadata: SimulationMetadata | None = None

class AudiogramDTO(BaseModel):
    freqs_hz: list[float]     # [250, 500, 1000, 2000, 4000, 8000]
    dB_HL: list[float]        # mismo largo que freqs_hz
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- Mismo que Screening BERA: 2–10 minutos para una simulación individual.
- `ohc_ind()` agrega ~30 segundos extra (conversión audiograma → polos).

### Fidelidad del estímulo

> [!IMPORTANT]
> La validación solo es significativa si el estímulo simulado es **idéntico** al del equipo clínico. Esto requiere documentar exactamente: tipo de estímulo, frecuencia, nivel, duración, tasa de presentación, y condiciones de medición del ABR real. Si hay diferencias de estímulo, las discrepancias simulación/real no son interpretables.

### Normalización temporal

El equipo clínico y el modelo Verhulst pueden tener frecuencias de muestreo diferentes. El sistema debe normalizar ambas señales al mismo eje temporal antes de calcular métricas de concordancia.

### Persistencia

- Guardar el audiograma original y el `sheraP` generado vinculados al `patient_id`.
- Si el paciente vuelve para un nuevo estudio, `ohc_ind()` puede omitirse si el `sheraP` ya está cacheado.
- Guardar el informe de validación (métricas + overlay) como PDF exportable.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #9 (Screening Neonatal) | Comparte `ohc_ind()` como función de conversión y el endpoint `/simulate`; validación es el paso posterior a la simulación del screening |
| #16 (Arquetipos) | Los ABR reales cargados aquí son candidatos para buscar arquetipos en la biblioteca |
| #7 (Gemelo Digital) | Esta funcionalidad es el primer paso del "gemelo digital": construir el perfil personalizado via `ohc_ind()` |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Validación Clínica |
|---|---|---|
| Fuente de `sheraP` | Pre-computado (catálogo) o `ohc_ind()` con valores hipotéticos | **`ohc_ind()` con audiograma real del paciente** |
| Señal de entrada real | Opcional (upload para comparación) | **Obligatoria** — es la señal contra la que se valida |
| Objetivo | Estudiar un perfil patológico hipotético | **Verificar que el modelo predice la señal real** |
| Métricas adicionales | Latencias, amplitudes | **Métricas de concordancia**: correlación, RMS error, ΔLatencia |
| Modificación interna | No | No |
| Caso de uso científico | Investigación hipotética | **Validación experimental del modelo** |
