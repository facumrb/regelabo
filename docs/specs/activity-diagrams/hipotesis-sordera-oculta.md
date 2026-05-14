# Diagrama de Actividad: Explorar Hipótesis sobre Sordera Oculta (Sinaptopatía)

> **Caso de uso #3:** Explorar hipótesis sobre pérdidas auditivas "ocultas"
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Investigar y demostrar que un paciente con audiometría aparentemente **normal** puede tener daño nervioso (sinaptopatía coclear) detectable a través del EFR/ABR simulado, explorando el efecto de reducir selectivamente las fibras del nervio auditivo manteniendo la cóclea sana.

### Sub-metas / Objetivos intermedios

- **M1:** Configurar un "paciente con cóclea sana" (polos Flat00 sin degradación de OHC).
- **M2:** Reducir selectivamente la cantidad de fibras AN (nH, nM, nL) para simular distintos grados de sinaptopatía.
- **M3:** Observar cómo cae el EFR y/o la morfología ABR a pesar de que el audiograma es "normal".
- **M4:** Comparar visualmente el EFR/ABR del perfil sano vs. el perfil sinaptopatía.
- **M5:** Generar evidencia de que la sinaptopatía no es detectable con audiometría estándar pero sí con el simulador.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Explorar hipótesis sordera oculta (sinaptopatía)  ← esta
│   ├── M1: Definir perfil de cóclea sana (Flat00)
│   ├── M2: Barrido de fibras AN (nH, nM, nL)
│   ├── M3: Comparar EFR/ABR entre configuraciones
│   └── M4: Generar evidencia de sinaptopatía
├── Sub-meta: Screening Neonatal BERA/ABR
├── Sub-meta: Sordera Oculta Edad vs Trauma (#12)
└── Sub-meta: Entrenamiento ML
```

> [!NOTE]
> La sinaptopatía coclear es un daño que **NO modifica el audiograma convencional** (OHC intactas), pero sí reduce las fibras del nervio auditivo. Es el caso paradigmático donde el modelo Verhulst aporta información que la clínica estándar no puede capturar.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `╔═══╗` = Actividad compuesta (caja negra)

### Flujo principal

```
[●] INICIO
  │
  ▼
[1. Investigador accede al módulo "Hipótesis de Sordera Oculta"]
  │
  ▼
[2. Sistema presenta configuración de experimento comparativo]
  │
  ▼
[3. Investigador selecciona perfil de cóclea: Flat00 (normal / sin pérdida OHC)
    — El audiograma base es "sano" para aislar el efecto de sinaptopatía]
  │
  ▼
[4. Selecciona tipo de estímulo EFR (RAM):
     Frecuencia portadora (ej. 4000 Hz), frecuencia de modulación (ej. 98 Hz),
     nivel (ej. 65 dB SPL)]
  │
  ▼
[5. Configura las variantes de fibras AN a comparar:
    - Perfil SANO: nH=13, nM=3, nL=3 (valores normativos)
    - Perfil SINAPTOPATÍA LEVE: nH=7, nM=3, nL=3
    - Perfil SINAPTOPATÍA MODERADA: nH=4, nM=2, nL=2
    - Perfil SINAPTOPATÍA SEVERA: nH=1, nM=1, nL=1
    (El investigador puede agregar/quitar perfiles y editar valores)]
  │
  ▼
<6. ¿Desea incluir variante con pérdida OHC para comparación adicional?>
  │                               │
  │ Sí                            │ No → continuar
  ▼                               │
[6a. Selecciona también un perfil │
  con OHC degradadas (ej. Flat40) │
  para distinguir sinaptopatía    │
  de daño coclear clásico]        │
  │                               │
  ▼                               ▼
[7. Investigador presiona "Ejecutar experimento comparativo"
    (N simulaciones: una por cada variante de fibras AN configurada)]
  │
  ▼
[8. Sistema valida configuración:
     - Todos los perfiles de fibras tienen valores en rango válido (nH/nM/nL > 0)
     - Perfil de cóclea seleccionado existe en catálogo
     - Estímulo configurado correctamente]
  │
  ▼
<9. ¿Configuración válida?>
  │           │
  │ Sí        │ No → [Mostrar errores de validación] → volver a 5
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  10. PIPELINE VERHULST × N VARIANTES (CAJA NEGRA)         ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: Flat00 (sheraP fijo) + N configs (nH,nM,nL)     ║
║           + estímulo RAM común                             ║
║  Salida:  N × {EFR (µV), w1[], w3[], w5[]}                 ║
║                                                             ║
║  Ver verhulst-analysis/hipotesis-sordera-oculta.md          ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error en alguna variante
  │            ▼
  │      [10a. Registrar error, marcar variante fallida,
  │       continuar con las exitosas si N-fallidas < N]
  │
  ▼
[11. Frontend recibe resultados de las N variantes]
  │
  ▼
[12. Plotly.js renderiza gráfico comparativo:
      - Panel izquierdo: curvas EFR por variante (amplitud vs. config fibras)
      - Panel derecho (opcional): ondas ABR superpuestas de todas las variantes
      - Código de color: cada variante de nH/nM/nL tiene su color]
  │
  ▼
[13. Sistema calcula y muestra tabla de métricas comparativas:
      - EFR (µV) por variante
      - Reducción porcentual respecto al perfil sano
      - Latencias pico ABR por variante
      - Diferencias interpico]
  │
  ▼
[14. Investigador analiza:
      - Verifica caída de EFR con audiograma normal (Flat00 sin cambio)
      - Identifica el "umbral de sinaptopatía detectable"
      - Evalúa si la pérdida de fibras nH (alta espontaneidad) es más
        sensible que nL para el EFR]
  │
  ▼
<15. ¿Desea ajustar los parámetros del experimento y re-ejecutar?>
  │                    │
  │ Sí → volver a 5    │ No
                        │
                        ▼
                       [16. Investigador exporta resultados:
                             CSV con tabla comparativa
                             PNG/SVG del gráfico]
                        │
                        ▼
                       [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 6 | ¿Incluir variante OHC degradada? | Sí → agregar perfil Flat40 | No → continuar solo con Flat00 |
| 9 | ¿Configuración válida? | Sí → ejecutar | No → mostrar errores, volver |
| 10 | Pipeline N variantes | OK → visualizar | Error parcial → registrar, continuar con exitosas |
| 15 | ¿Re-ejecutar con ajustes? | Sí → loop a paso 5 | No → exportar y fin |

---

## 3. Nota Clínica de Contexto

> [!NOTE]
> **El punto central de este experimento:** El módulo debe poder demostrar visualmente que **nH=13 vs nH=7 con Flat00 produce EFR diferente aunque el audiograma sea el mismo**. Esta es la "prueba de fuego" de la hipótesis de sinaptopatía. El módulo UI debe comunicar claramente este concepto al fonoaudiólogo que no tiene background computacional.
