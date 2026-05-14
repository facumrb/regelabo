# Análisis Verhulst: Optimizar Parámetros de Estímulo

> **Caso de uso #4:** Optimizar parámetros de estímulo
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra Pura + Paralelismo en lote (especialización del pipeline #2)**

Esta funcionalidad es estructuralmente idéntica a la generación de datos sintéticos en lote (#2), pero con una diferencia semántica: el **perfil OHC está fijo** y lo que varía es el espacio de parámetros del **estímulo** (fc, fm, nivel). El objetivo no es generar un dataset, sino encontrar el **óptimo del EFR** como función del espacio de estímulos. No se toca el código del modelo.

---

## 2. Entradas al Modelo

| Parámetro | Valor para esta funcionalidad | Descripción |
|---|---|---|
| `sheraP` | **Fijo** — perfil base elegido por el investigador (ej. Flat00) | La cóclea es constante durante todo el barrido |
| `nH`, `nM`, `nL` | **Fijo** — default o configurado al inicio | Las fibras AN son constantes durante el barrido |
| `sign` | **Variable** — generado por `get_RAM_stims.py` para cada combinación (fc, fm, nivel) | Este es el parámetro que se barre |
| `fs` | ~100 kHz | Frecuencia de muestreo del estímulo RAM |
| `storeflag` | `'bw'` | Solo se necesita ABR para calcular EFR |
| `fc` | `'abr'` o array | Frecuencias características |

### Espacio de búsqueda del estímulo (parámetros variables)

| Parámetro del estímulo | Rango típico | Paso típico | N valores típico |
|---|---|---|---|
| `fc` (frecuencia portadora) | 1000–8000 Hz | 1000 Hz | 8 |
| `fm` (frecuencia de modulación) | 80–200 Hz | 20 Hz | 7 |
| `nivel` (dB SPL) | 50–80 dB | 5 dB | 7 |
| **Total combinaciones** | | | **8 × 7 × 7 = 392 sims** |

> [!WARNING]
> Un barrido completo de 392 simulaciones a 2-10 min cada una representa 13-65 horas de cómputo. El investigador debe definir un espacio de búsqueda razonable para la primera exploración (ej. 3×3×3 = 27 sims = 1-4 horas).

---

## 3. Salidas del Modelo Consumidas

| Output | Nombre en código | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| EFR (magnitud a fm) | FFT de `w1+w3+w5` a fm | float (µV) | **Métrica de optimización** — se maximiza sobre el espacio de estímulos |

> Las ondas individuales (w1, w3, w5) se almacenan en storage pero no son la métrica principal. Solo el EFR escalar entra en el análisis de optimización.

### Función objetivo

```
EFR_óptimo = argmax_{(fc, fm, nivel)} EFR(sheraP_fijo, nH_fijo, nM_fijo, nL_fijo, RAM(fc, fm, nivel))
```

---

## 4. Interfaz API Requerida

Reutiliza el endpoint de lote de la funcionalidad #2 con perfil fijo y espacio de estímulos variable:

| Endpoint | Método | Descripción |
|---|---|---|
| `/batches/` | POST | Crear lote de barrido de estímulos (perfil fijo, estímulos variables) |
| `/batches/{batch_id}` | GET | Estado del barrido |
| `/batches/{batch_id}/optimize` | GET | Resultado del análisis de optimización (máximo EFR + parámetros) |
| `/batches/{batch_id}/heatmap` | GET | Datos para renderizar heatmap EFR(fc, fm) o EFR(fc, nivel) |

### DTO especializado

```python
class StimulusSweepRequest(BaseModel):
    # Perfil fijo
    base_profile: str = "Flat00"
    n_fibers: FibersConfig = FibersConfig()

    # Espacio de búsqueda del estímulo
    stimulus_type: Literal["RAM"] = "RAM"   # Actualmente solo RAM soportado
    fc_range: list[float]                    # [1000, 2000, 4000, 8000] Hz
    fm_range: list[float]                    # [80, 98, 120, 150, 200] Hz
    level_range: list[float]                 # [50, 65, 80] dB SPL

    # Solo almacenar EFR escalar (no arrays completos) para eficiencia
    store_full_abr: bool = False

    metadata: BatchMetadata | None = None
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- Depende del tamaño del espacio de búsqueda.
- Recomendación: comenzar con una grilla 3×3×3 (27 sims ≈ 1–4 horas) y afinar.

### Eficiencia de almacenamiento

A diferencia del lote general (#2), en este caso **solo interesa el EFR escalar** de cada simulación. No es necesario almacenar los arrays w1, w3, w5 completos en storage (ahorra ~99% de espacio). El flag `store_full_abr=False` en el DTO activa esta optimización.

### Visualización: Heatmap

El resultado principal es un **heatmap EFR(fc, fm)** para un nivel fijo, similar a las figuras de papers de Verhulst. El frontend debe poder generar este gráfico interactivo con Plotly.js.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #2 (Datos Sintéticos) | **Comparte infraestructura de lote** — este es un caso especial donde perfil=fijo, estímulo=variable |
| #9 (Screening Neonatal) | Los parámetros óptimos encontrados aquí se usan para configurar el estímulo del screening |
| #3 (Hipótesis Sordera Oculta) | En #3 se puede combinar con optimización: ¿cuál es el mejor estímulo para detectar sinaptopatía? |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Optimización de Estímulo |
|---|---|---|
| N° de simulaciones | 1 | N = |fc| × |fm| × |nivel| |
| `sheraP` | Variable (elegido por usuario) | **Fijo** (perfil base del experimento) |
| Estímulo (`sign`) | Fijo (elegido por usuario) | **Variable** — es el eje de optimización |
| Métrica principal | Latencias y morfología ABR | **EFR (µV) — maximizar** |
| Visualización | Trazas ABR temporales | Heatmap EFR(fc, fm) |
| Modificación interna | No | No |
| Output exportable | ABR + latencias del caso clínico | Parámetros óptimos del estímulo (JSON para equipo clínico) |
