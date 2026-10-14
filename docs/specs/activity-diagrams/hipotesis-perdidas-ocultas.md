# Diagrama de Actividad: Explorar Pérdidas Auditivas Ocultas

> **Caso de uso #3:** Explorar hipótesis sobre pérdidas auditivas "ocultas"
> **Fecha:** 2026-08-04 | **Revisión:** v2
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Demostrar clínicamente que un daño exclusivo en las sinapsis del nervio auditivo (sinaptopatía coclear) produce una caída mensurable en la amplitud del biomarcador EFR (Envelope Following Response), evidenciando una "sordera oculta" que un audiograma estándar es incapaz de detectar.

### Sub-metas / Objetivos intermedios

- **M1:** Definir un paciente de control (Baseline) con audición totalmente normal.
- **M2:** Simular diferentes grados de sinaptopatía (pérdida progresiva de fibras de baja y media tasa de disparo espontáneo) manteniendo la cóclea intacta.
- **M3:** Visualizar la caída relativa de la amplitud del EFR entre el baseline y el paciente simulado.
- **M4:** Contrastar la morfología de la onda ABR para observar los efectos en la latencia y amplitud de los picos.

### Clasificación en la taxonomía del proyecto

```text
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Explorar hipótesis de pérdidas ocultas  ← esta
│   ├── M1: Selección de baseline normativo (Flat00)
│   ├── M2: Configuración de degradación sináptica (nH, nM, nL)
│   ├── M3: Comparación de amplitud EFR
│   └── M4: Comparación morfológica ABR
└── [Base metodológica de todas las demás funcionalidades]
```

> [!NOTE]
> Esta funcionalidad tiene un propósito altamente educativo y de investigación. Se nutre íntegramente de perfiles pre-computados, por lo que la velocidad de respuesta debe ser instantánea.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `╔═══╗` = Actividad compuesta (caja negra / microservicio)

### Flujo principal

```text
[●] INICIO
  │
  ▼
[1. Fonoaudiólogo accede al módulo "Evaluación de Sordera Oculta"]
  │
  ▼
[2. Sistema carga automáticamente el perfil de Control Baseline (Sano):
    ○ Perfil OHC: Flat00 (0 dB HL)
    ○ Fibras AN: Normales (nH=13, nM=3, nL=3)]
  │
  ▼
[3. Fonoaudiólogo configura el estímulo acústico de evaluación:
    ○ Tipo: RAM (por defecto, el más sensible para sordera oculta)
    ○ Frecuencia portadora: 4 kHz (por defecto)
    ○ Nivel: 65 dB SPL (por defecto)]
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  4. VALIDACIÓN DE DISPONIBILIDAD EN DB (BACKEND)             ║
║  ─────────────────────────────────────────────────────────   ║
║  El `core-service` verifica que existan perfiles             ║
║  pre-computados en `precomputed_profiles` para el estímulo   ║
║  seleccionado. Si no existen, deshabilita las opciones       ║
║  de gravedad que no tengan datos.                            ║
╚══════════════════════════════════════════════════════════════╝
  │
  ▼
[5. Fonoaudiólogo selecciona el grado de "Sinaptopatía Hipotética" a explorar:
    ○ Leve (Reducción de nH=7, nM=3, nL=3)
    ○ Moderada (Reducción de nH=4, nM=2, nL=2)
    ○ Severa (Reducción de nH=1, nM=1, nL=1)]
  │
  ▼
[6. Fonoaudiólogo hace clic en "Comparar Firmas Eléctricas"]
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  7. PIPELINE DE CONSULTA (BACKEND / REDIS / POSTGRESQL)      ║
║  ─────────────────────────────────────────────────────────   ║
║  Entrada: Estímulo + Grado seleccionado (Leve, Mod, Sev)     ║
║  Proceso: `core-service` busca en `precomputed_profiles`     ║
║           el baseline (`Flat00` + Normal) y el target        ║
║           (`Flat00` + Reducido) para ese estímulo.           ║
║  Salida: Arrays JSON de EFR, W1, W3, W5 para ambos casos.    ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error → [Mostrar mensaje: "Perfil no disponible"] → volver a 5
  │
  ▼
[8. Frontend calcula la caída porcentual de amplitud EFR:
    (EFR_sano - EFR_dañado) / EFR_sano * 100]
  │
  ▼
[9. Frontend renderiza las visualizaciones comparativas:
    - Panel A: Gráfico de barras mostrando la caída de amplitud EFR (µV)
    - Panel B: Gráfico de líneas con la superposición ABR temporal]
  │
  ▼
[10. Fonoaudiólogo observa la "Firma de Sinaptopatía" (Caída EFR con cóclea sana)]
  │
  ▼
<11. ¿Desea explorar otro grado de severidad o cambiar el estímulo?>
  │                    │
  │ Sí → volver a 3    │ No
                       │
                       ▼
                      [12. Exportar reporte PDF de la comparación]
                       │
                       ▼
                      [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 4 | ¿Estímulo disponible en DB? | Sí → habilita opciones de gravedad | No → deshabilita opciones sin datos |
| 7 | Resultado del pipeline DB | OK → renderizar gráficos | Error → mostrar mensaje, volver a 5 |
| 11 | ¿Explorar otro grado o estímulo? | Sí → volver a 3 (cambia estímulo) o 5 (cambia gravedad) | No → exportar, fin |
