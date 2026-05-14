# Análisis Verhulst: Sordera Oculta — Envejecimiento vs. Trauma Acústico

> **Caso de uso #12:** Sordera Oculta: Edad vs. Trauma Acústico
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra Pura — Manipulación dual de parámetros externos**

El modelo `model2018()` no requiere ninguna modificación interna. Los dos perfiles clínicos (envejecimiento y trauma acústico) se modelan cambiando combinaciones de parámetros que **ya existen** en la API pública del modelo:
- **Envejecimiento:** `sheraP` degradado (OHC dañadas → polos Slope) + fibras AN normales.
- **Trauma acústico:** `sheraP` sano (Flat00) + fibras AN drásticamente reducidas (`nL=0`, `nM=0`).

> [!IMPORTANT]
> El poder diagnóstico de esta funcionalidad emerge del **desacoplamiento biológico** que el modelo ya implementa: los polos de Shera (cóclea) y las fibras AN (sinapsis) son parámetros independientes. Esta separación es una característica arquitectónica del modelo Verhulst, no algo que debamos agregar.

---

## 2. Entradas al Modelo

### Perfil A: Paciente Envejecido (Presbiacusia)

| Parámetro | Valor | Descripción |
|---|---|---|
| `sheraP` | `np.loadtxt('Poles/Slope20/StartingPoles.dat')` (o Slope30/45) | OHC degradadas gradualmente, especialmente en frecuencias altas |
| `nH` | 13 | Fibras AN de alta espontaneidad — **sin reducción** (sinapsis preservadas) |
| `nM` | 3 | Fibras AN de media espontaneidad — sin reducción |
| `nL` | 3 | Fibras AN de baja espontaneidad — sin reducción |
| `sign` | RAM (compartido con Perfil B) | Mismo estímulo para comparación controlada |
| `storeflag` | `'bw'` | Almacenar ondas ABR |
| `fc` | `'abr'` | Frecuencias características estándar |

### Perfil B: Paciente con Trauma Acústico (Sinaptopatía)

| Parámetro | Valor | Descripción |
|---|---|---|
| `sheraP` | `np.loadtxt('Poles/Flat00/StartingPoles.dat')` | OHC **sanas** — audiograma normal |
| `nH` | 1 (o 0) | Fibras nH destruidas por sobreexposición — reducción severa |
| `nM` | 0 | Fibras nM destruidas |
| `nL` | 0 | Fibras nL destruidas |
| `sign` | RAM (compartido con Perfil A) | Mismo estímulo |
| `storeflag` | `'bw'` | Almacenar ondas ABR |
| `fc` | `'abr'` | Frecuencias características estándar |

> [!NOTE]
> Los valores `nM=0`, `nL=0` son el extremo del modelo para simular destrucción sináptica total en fibras de media y baja espontaneidad. En la práctica el investigador puede explorar valores intermedios.

### Perfil C (Referencia Sana, opcional)

| Parámetro | Valor |
|---|---|
| `sheraP` | Flat00 |
| `nH`, `nM`, `nL` | 13, 3, 3 |

---

## 3. Salidas del Modelo Consumidas

| Output | Nombre en código | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| EFR | FFT de `w1+w3+w5` a fm | float (µV) | Métrica comparativa principal entre perfil A y B |
| Onda ABR nervio auditivo | `output.w1` | ndarray float | Comparación morfológica y de latencia |
| Onda ABR núcleo coclear | `output.w3` | ndarray float | Comparación morfológica y de latencia |
| Onda ABR colículo inferior | `output.w5` | ndarray float | Comparación morfológica y de latencia |

### Hipótesis de diferenciación esperada

```
Métrica          │ Envejecimiento (Slope)  │ Trauma Acústico (Flat00 + nH≈0)
─────────────────┼─────────────────────────┼──────────────────────────────────
EFR (µV)         │ Reducido moderadamente  │ Reducido marcadamente
Latencia W1      │ Aumentada               │ Normal (OHC sana)
Latencia W3/W5   │ Aumentada               │ Normal / mínimamente alterada
Amplitud W1      │ Reducida                │ Reducida severamente
Audiograma       │ Pérdida en agudos       │ Normal (Flat00 = sin pérdida)
```

Esta diferenciación de latencias es el mecanismo diagnóstico clave: en el trauma acústico, la latencia W1 puede ser **normal** (cóclea intacta) pero la amplitud W1 está severamente reducida (sinapsis destruidas).

---

## 4. Interfaz API Requerida

Esta funcionalidad reutiliza el endpoint comparativo definido en la funcionalidad #3:

| Endpoint | Método | Descripción |
|---|---|---|
| `/simulate/comparative` | POST | Ejecuta N perfiles con un estímulo común |
| `/simulate/comparative/{job_id}` | GET | Estado del experimento |
| `/simulate/comparative/{job_id}/results` | GET | Resultados de todos los perfiles |

### DTO de Request (especialización del comparativo)

```python
class AgingVsTraumaRequest(BaseModel):
    # Perfil A: envejecimiento
    aging_profile: str = "Slope20"          # Perfil OHC degradado
    aging_fibers: FibersConfig = FibersConfig(nH=13, nM=3, nL=3)

    # Perfil B: trauma acústico
    trauma_fibers: FibersConfig = FibersConfig(nH=1, nM=0, nL=0)
    # trauma usa Flat00 (OHC sana) — hardcoded en este endpoint

    # Estímulo común
    stimulus: StimulusConfig

    # Perfil C: referencia sana (opcional)
    include_healthy_reference: bool = True

    metadata: SimulationMetadata | None = None
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- **2 perfiles (A + B):** 4–20 minutos en paralelo.
- **3 perfiles (A + B + C sano):** 6–30 minutos en paralelo.

### Paralelismo

Los 2 o 3 perfiles del experimento son completamente independientes → se ejecutan en paralelo con workers Celery distintos.

### Persistencia

- Guardar los resultados agrupados por `experiment_id` en la tabla `comparative_simulations`.
- Almacenar las ondas completas (w1, w3, w5) en object storage para exportación.
- La tabla de métricas agregadas (EFR, latencias) se guarda en PostgreSQL para consultas rápidas.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #3 (Hipótesis Sordera Oculta) | Comparte infraestructura comparativa; esta es una especialización con narrativa clínica específica (presbiacusia vs. trauma) |
| #16 (Arquetipos Clínicos) | Los resultados de este experimento alimentan el catálogo de arquetipos de sinaptopatía y presbiacusia |
| #2 (Datos Sintéticos) | Esta funcionalidad puede verse como un lote de 2-3 simulaciones con propósito diagnóstico diferencial |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Edad vs. Trauma |
|---|---|---|
| N° de simulaciones | 1 | 2 o 3 (A, B, [C]) en paralelo |
| `sheraP` | Variable (elegido por usuario) | **Dos valores distintos**: Slope para edad, Flat00 para trauma |
| `nH`, `nM`, `nL` | Default normativo (13/3/3) | **Variable**: normativo para A, drasticamente reducido para B |
| Salidas principales | w1, w3, w5 + latencias ABR | EFR + latencias ABR **comparadas entre perfiles** |
| Visualización | Una sola traza ABR | Panel comparativo superpuesto |
| Modificación interna | No | No |
| Insight clínico | Qué hace un perfil patológico conocido | **Distinguir dos mecanismos distintos de pérdida oculta** |
