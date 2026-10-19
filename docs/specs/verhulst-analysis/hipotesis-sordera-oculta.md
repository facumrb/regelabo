# Análisis Verhulst: Explorar Hipótesis sobre Sordera Oculta (Sinaptopatía)

> **Caso de uso #3:** Explorar hipótesis sobre pérdidas auditivas "ocultas"
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra Pura — Manipulación exclusiva de parámetros externos**

El modelo `model2018()` no requiere ninguna modificación interna. La sinaptopatía se simula reduciendo los parámetros `nH`, `nM`, `nL` (fibras AN) que ya son argumentos de la función orquestadora. El perfil de cóclea sana (`Flat00`) se carga con `np.loadtxt()` sin modificaciones. Todo el poder de esta funcionalidad proviene de la capacidad del modelo de **desacoplar la cóclea (OHC, polos de Shera) de la sinapsis (fibras AN)**, que es una característica intrínseca de `model2018()`.

> [!IMPORTANT]
> Esta es la funcionalidad que mejor ilustra por qué el modelo Verhulst es un **simulador biológicamente informado** y no una caja negra genérica. Los parámetros `nH`, `nM`, `nL` modelan tres subpoblaciones de fibras del nervio auditivo con diferente espontaneidad, y cada subpoblación tiene un rol diferente en la codificación del EFR.

---

## 2. Entradas al Modelo

| Parámetro | Valor para esta funcionalidad | Función/Archivo del Modelo | Descripción |
|---|---|---|---|
| `sheraP` | `np.loadtxt('data/Poles/Flat00/StartingPoles.dat')` | `model2018()` | **Fijo = Flat00** (cóclea completamente sana, sin pérdida OHC) — este es el "audiograma normal" |
| `nH` | Varía: 13 → 7 → 4 → 1 (por variante) | `model2018()` | Fibras de alta espontaneidad — las más sensibles para detectar sinaptopatía en EFR |
| `nM` | Varía: 3 → 3 → 2 → 1 (por variante) | `model2018()` | Fibras de media espontaneidad |
| `nL` | Varía: 3 → 3 → 2 → 1 (por variante) | `model2018()` | Fibras de baja espontaneidad |
| `sign` | RAM generado por `get_RAM_stims.py` | `model2018()` | Estímulo RAM (tipicamente: fc=4 kHz, fm=98 Hz, nivel=65 dB SPL) |
| `fs` | ~100 kHz | `model2018()` | Frecuencia de muestreo del estímulo |
| `storeflag` | `'bw'` o `'efr'` (a definir según lo que se quiera visualizar) | `model2018()` | Determina qué etapas del pipeline almacenar |
| `fc` | `'abr'` o array de frecuencias | `model2018()` | Frecuencias características a computar |

### Tabla de variantes (experimento comparativo típico)

| Variante | Perfil OHC | nH | nM | nL | Interpretación clínica |
|---|---|---|---|---|---|
| SANO | Flat00 | 13 | 3 | 3 | Referencia: oído completamente sano |
| SINAPTOPATÍA LEVE | Flat00 | 7 | 3 | 3 | ~50% pérdida de fibras nH (alta espontaneidad) |
| SINAPTOPATÍA MODERADA | Flat00 | 4 | 2 | 2 | ~70% pérdida de fibras nH + parcial nM/nL |
| SINAPTOPATÍA SEVERA | Flat00 | 1 | 1 | 1 | Destrucción casi total de sinapsis |
| DAÑO OHC (comparación) | Flat40 | 13 | 3 | 3 | Pérdida coclear clásica sin sinaptopatía |

---

## 3. Salidas del Modelo Consumidas

| Output | Nombre en código | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| EFR (magnitud) | FFT del compuesto `w1+w3+w5` a fm | float (µV) | **Métrica principal de comparación** — se espera caída con reducción de nH |
| Onda ABR nervio auditivo | `output.w1` | ndarray float | Comparación visual de morfología entre variantes |
| Onda ABR núcleo coclear | `output.w3` | ndarray float | Comparación visual de morfología entre variantes |
| Onda ABR colículo inferior | `output.w5` | ndarray float | Comparación visual de morfología entre variantes |

### Relación esperada (hipótesis a demostrar)

```
EFR (µV)
  │
  ●  ← Sano (nH=13, Flat00)     → EFR máximo
  │
  ●  ← Sinaptopatía Leve (nH=7) → EFR reducido ~30-40%
  │
  ●  ← Sinaptopatía Mod. (nH=4) → EFR reducido ~60-70%
  │
  ●  ← Sinaptopatía Sev. (nH=1) → EFR mínimo
  │
  ─────────────────────────────────────────
  Nota: audiograma (Flat00) sin cambio en todos los casos
```

---

## 4. Interfaz API Requerida

| Endpoint | Método | Descripción |
|---|---|---|
| `/simulate/comparative` | POST | Ejecuta N simulaciones con el mismo perfil OHC y distintas configs de fibras AN |
| `/simulate/comparative/{job_id}` | GET | Polling del estado del experimento comparativo |
| `/simulate/comparative/{job_id}/results` | GET | Obtener todos los resultados de las variantes |

### DTO de Request

```python
class ComparativeSimulationRequest(BaseModel):
    base_profile: str = "Flat00"           # Perfil OHC fijo
    fiber_variants: list[FibersConfig]     # [{nH:13,nM:3,nL:3}, {nH:7,...}, ...]
    stimulus: StimulusConfig               # Estímulo RAM compartido por todas las variantes
    outputs_requested: list[OutputFlag] = ["efr", "w1", "w3", "w5"]
    variant_labels: list[str] | None = None  # ["Sano", "Sinaptopatía Leve", ...]
    include_ohc_comparison: bool = False    # Si True, agrega variante con OHC degradada
    comparison_profile: str | None = None  # ej. "Flat40" si include_ohc_comparison=True
    metadata: SimulationMetadata | None = None
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- **Por variante:** 2–10 minutos.
- **Experimento típico (4 variantes):** 8–40 minutos (paralelo con 4 workers).
- **Con comparación OHC adicional (5 variantes):** 10–50 minutos.

### Paralelismo

Las N variantes de un experimento comparativo son completamente **independientes** entre sí (mismo estímulo, mismo perfil OHC → solo cambian nH/nM/nL). Se pueden ejecutar en paralelo trivialmente usando el pool de workers Celery.

### Persistencia

- Cada variante genera una fila en la tabla `simulations` con `comparative_job_id` como FK.
- El resultado EFR por variante se almacena como columna escalar para consultas rápidas.
- Los arrays completos (w1, w3, w5) se almacenan en object storage referenciados por `simulation_id`.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #12 (Sordera Oculta: Edad vs. Trauma) | Comparte el concepto de experimento comparativo. Diferencia: en #12 se comparan perfiles OHC degradados (edad) vs. sinaptopatía (fibras), no solo sinaptopatía pura |
| #9 (Screening Neonatal) | Comparte el pipeline individual; el endpoint comparativo es una extensión |
| #2 (Datos Sintéticos en Lote) | Esta funcionalidad puede verse como un lote pequeño con propósito exploratorio |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Hipótesis Sordera Oculta |
|---|---|---|
| N° de simulaciones | 1 | N (una por variante de fibras AN) |
| `sheraP` | Variable (elegido por usuario) | **Fijo = Flat00** (cóclea sana — condición experimental) |
| `nH`, `nM`, `nL` | Fijo (default normativo) | **Variable** — es el parámetro manipulado del experimento |
| `storeflag` | `'bw'` | `'bw'` o `'efr'` según lo que se visualice |
| Salidas principales | w1, w3, w5 + latencias ABR | **EFR (µV) como métrica principal** + morfología ABR secundaria |
| Visualización | Gráfico temporal de ondas ABR | Gráfico comparativo EFR por configuración de fibras + overlay ABR |
| Modificación interna | No | No |
| Insight clínico | Diagnóstico de perfil patológico conocido | **Demostración de sinaptopatía con audiograma normal** |
