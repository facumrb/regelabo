# Diagrama de Actividad: Sordera Oculta — Envejecimiento vs. Trauma Acústico

> **Caso de uso #12:** Sordera Oculta: Edad vs. Trauma Acústico
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Determinar si el deterioro auditivo por **envejecimiento natural** (presbiacusia) produce una firma EFR/ABR biológicamente distinguible del deterioro por **trauma acústico agudo** (ej. exposición a ruido fuerte), para afinar el diagnóstico diferencial de pérdidas auditivas ocultas.

### Sub-metas / Objetivos intermedios

- **M1:** Configurar el "paciente envejecido" como daño coclear gradual (OHC degradadas → polos Slope).
- **M2:** Configurar el "paciente con trauma acústico" como daño sináptico (OHC sanas → fibras AN reducidas).
- **M3:** Ejecutar ambas simulaciones con el mismo estímulo para que la comparación sea justa.
- **M4:** Visualizar superposición de EFR y ondas ABR de ambos perfiles.
- **M5:** Identificar si la firma eléctrica permite distinguir un mecanismo del otro.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Sordera Oculta: Edad vs. Trauma Acústico  ← esta
│   ├── M1: Perfil "Envejecido" (Slope OHC)
│   ├── M2: Perfil "Trauma Acústico" (fibras AN reducidas)
│   ├── M3: Comparación con mismo estímulo
│   └── M4: Diagnóstico diferencial
└── Sub-meta: Hipótesis Sordera Oculta (#3) [relacionada]
```

> [!NOTE]
> Esta funcionalidad es un caso específico del experimento comparativo (#3), pero con una narrativa clínica precisa: **envejecimiento = daño OHC gradual** vs. **trauma acústico = daño sináptico AN**. La distinción es fundamental para el fonoaudiólogo porque ambos se presentan con queja de "escucho mal en ruido" pero con audiometría casi normal.

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
[1. Fonoaudiólogo accede al módulo "Diagnóstico Diferencial: Edad vs. Trauma"]
  │
  ▼
[2. Sistema presenta panel de configuración de dos perfiles paralelos]
  │
  ▼
══════════ CONFIGURACIÓN PERFIL A: ENVEJECIMIENTO ══════════
  │
  ▼
[3. Define el perfil del "Paciente Envejecido":
     - Perfil OHC: Slope (ej. Slope20, Slope30, Slope45)
       → simula pérdida coclear gradual típica de presbiacusia
     - Fibras AN: nH=13, nM=3, nL=3 (normales, sinapsis preservadas)]
  │
  ▼
══════════ CONFIGURACIÓN PERFIL B: TRAUMA ACÚSTICO ══════════
  │
  ▼
[4. Define el perfil del "Paciente con Trauma":
     - Perfil OHC: Flat00 (cóclea sana, audiograma normal)
       → simula que el trauma no llegó a dañar OHC
     - Fibras AN: nH=1, nM=0, nL=0 o similar
       → simula destrucción selectiva de sinapsis por sobreexposición]
  │
  ▼
══════════ CONFIGURACIÓN COMPARTIDA ══════════
  │
  ▼
[5. Selecciona el estímulo común para ambos perfiles:
     Tipo RAM, frecuencia portadora, frecuencia de modulación, nivel dB SPL
     (mismo para A y B para que la comparación sea controlada)]
  │
  ▼
<6. ¿Desea agregar un perfil C de referencia "Sano"?>
  │               │
  │ Sí            │ No → continuar
  ▼               │
[6a. Agrega perfil SANO:
  OHC = Flat00 + nH=13, nM=3, nL=3]
  │               │
  ▼               ▼
[7. Fonoaudiólogo presiona "Comparar perfiles"]
  │
  ▼
[8. Sistema valida:
     - Ambos perfiles tienen valores definidos y en rango
     - El estímulo está configurado]
  │
  ▼
<9. ¿Configuración válida?>
  │           │
  │ Sí        │ No → [Mostrar errores] → volver a 3
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  10. PIPELINE VERHULST × 2 (o 3) PERFILES (CAJA NEGRA)    ║
║  ─────────────────────────────────────────────────────────  ║
║  Perfil A: sheraP=Slope + nH=13,nM=3,nL=3                 ║
║  Perfil B: sheraP=Flat00 + nH=1,nM=0,nL=0                 ║
║  [Perfil C: sheraP=Flat00 + nH=13,nM=3,nL=3] (opcional)   ║
║  Estímulo RAM: igual para todos                             ║
║  Salida: EFR, w1, w3, w5 por perfil                        ║
║                                                             ║
║  Ver verhulst-analysis/sordera-oculta-edad-trauma.md        ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error
  │            ▼
  │      [10a. Registrar error, notificar] → FIN
  │
  ▼
[11. Frontend renderiza panel comparativo con dos (o tres) columnas:]
     │
     ├── [11a. Gráfico EFR comparativo:
     │         Barra o línea de EFR (µV) por perfil]
     │
     ├── [11b. Overlay de ondas ABR:
     │         Perfil A (línea sólida, color naranja = edad)
     │         Perfil B (línea sólida, color rojo = trauma)
     │         [Perfil C (línea punteada, color verde = sano)]]
     │
     └── [11c. Tabla de métricas:
               EFR (µV), latencias W1/W3/W5, amplitudes pico-a-pico
               por perfil y diferencia absoluta/porcentual]
  │
  ▼
[12. Fonoaudiólogo interpreta:
      - ¿Qué perfil tiene mayor caída de EFR?
      - ¿Las latencias ABR difieren entre A y B?
      - ¿Se puede distinguir el "daño OHC" del "daño sináptico" por la firma?]
  │
  ▼
<13. ¿Desea ajustar perfiles y re-comparar?>
  │                    │
  │ Sí → volver a 3    │ No
                        │
                        ▼
                       [14. Exporta informe comparativo:
                             CSV con métricas + imagen del gráfico]
                        │
                        ▼
                       [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 6 | ¿Agregar perfil sano de referencia? | Sí → 3 perfiles en comparación | No → solo A y B |
| 9 | ¿Configuración válida? | Sí → ejecutar | No → mostrar errores, volver |
| 10 | Pipeline 2-3 perfiles | OK → visualizar | Error → registrar, fin |
| 13 | ¿Re-comparar con ajustes? | Sí → loop a 3 | No → exportar, fin |
