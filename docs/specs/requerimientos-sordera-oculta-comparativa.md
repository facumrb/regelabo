# Casos de Uso y Requerimientos: Sordera Oculta — Edad vs. Trauma Acústico

> Documento derivado de `verhulst-analysis/sordera-oculta-comparativa.md` y `activity-diagrams/sordera-oculta-comparativa.md`

---

## 1. Casos de Uso

| ID | Nombre | Actor Principal | Descripción | Precondiciones | Postcondiciones |
|----|--------|-----------------|-------------|----------------|-----------------|
| CU-01 | Configurar Estímulo de Evaluación | Investigador | El usuario define el tipo de estímulo acústico (RAM, Click), frecuencia y nivel en dB SPL bajo los cuales se realizará la comparación | La tabla `precomputed_profiles` contiene datos para el estímulo seleccionado | Los dropdowns de configuración de fenotipos se habilitan según disponibilidad en la DB |
| CU-02 | Configurar Fenotipo Envejecimiento | Investigador | El usuario selecciona la severidad de la presbiacusia (Leve, Moderada, Severa), que se mapea a un perfil `Slope` con fibras AN normales | CU-01 completado | El sistema registra el perfil del Fenotipo A: `SlopeXX + nH=13, nM=3, nL=3` |
| CU-03 | Configurar Fenotipo Trauma Acústico | Investigador | El usuario selecciona la severidad del trauma sináptico (Leve, Moderado, Severo), que se mapea a perfil `Flat00` con fibras AN reducidas | CU-01 completado | El sistema registra el perfil del Fenotipo B: `Flat00 + nH/nM/nL reducido` |
| CU-04 | Ejecutar Comparación de Fenotipos | Investigador | El usuario inicia la consulta dual a la base de datos y espera el resultado de ambos perfiles simultáneamente | CU-02 y CU-03 completados | El backend retorna los datos de EFR, W1, W3, W5 para ambos fenotipos |
| CU-05 | Visualizar Comparativa de EFR | Investigador | El usuario observa en un gráfico de barras la amplitud del EFR (µV) de ambos fenotipos lado a lado, junto con el porcentaje de caída relativa | CU-04 completado exitosamente | Gráfico de barras renderizado con Plotly.js |
| CU-06 | Analizar Morfología ABR Diferencial | Investigador | El usuario superpone las ondas W1, W3 y W5 de ambos fenotipos para identificar en qué etapa de la vía auditiva cada patología deja su huella más distintiva | CU-04 completado exitosamente | Gráfico de líneas superpuestas renderizado con Plotly.js con leyenda por fenotipo y onda |
| CU-07 | Exportar Reporte Comparativo | Investigador | El usuario genera y descarga un reporte que incluye los gráficos de EFR y ABR junto con la tabla de metadatos de configuración de cada fenotipo | CU-05 o CU-06 completados | Reporte en PDF y datos crudos en CSV generados y disponibles para descarga |
| CU-08 | Resetear y Re-configurar Comparación | Investigador | El usuario limpia la sesión actual para explorar una nueva combinación de fenotipos (ej. cambiar de "Trauma Leve" a "Trauma Severo") | - | La UI vuelve al estado inicial sin resultados previos visibles |

---

## 2. Requerimientos Funcionales

| ID | Nombre | Descripción | Casos de Uso Relacionados |
|----|--------|-------------|---------------------------|
| RF-01 | Mapeo Clínico de Fenotipos | El frontend debe traducir las etiquetas clínicas ("Envejecimiento Leve", "Trauma Severo") a los parámetros técnicos del modelo (`profile_ohc`, `nH`, `nM`, `nL`) sin exponer los valores numéricos al usuario. El `core-service` usará esos parámetros para filtrar la tabla `precomputed_profiles`. | CU-02, CU-03 |
| RF-02 | Consulta Dual a la Base de Datos | El `core-service` debe ejecutar dos consultas simultáneas e independientes a `precomputed_profiles` (una por fenotipo) y empaquetar ambas respuestas en un único payload JSON para el frontend. | CU-04 |
| RF-03 | Filtrado Dinámico por Estímulo | El sistema debe deshabilitar dinámicamente las opciones de fenotipo que no tengan perfiles pre-computados disponibles para el estímulo seleccionado, para evitar que el usuario llegue a un estado de error. | CU-01 |
| RF-04 | Gráfico de Barras EFR Comparativo | El gráfico (Plotly.js) debe mostrar las barras de EFR de ambos fenotipos en colores claramente diferenciados y etiquetados, con el porcentaje de diferencia relativa entre ambos como texto sobre el gráfico. | CU-05 |
| RF-05 | Superposición ABR Multi-Trazo | El gráfico de ondas debe renderizar hasta 6 trazas (W1, W3 y W5 por cada uno de los 2 fenotipos) con una leyenda clara y un tooltip que al hacer hover muestre: el nombre de la onda, el fenotipo, la amplitud µV y la latencia ms en ese punto. | CU-06 |
| RF-06 | Exportación Consolidada | El sistema debe generar un reporte que incluya: (a) captura de los gráficos en PDF, (b) tabla CSV con los arrays crudos de EFR y ABR de ambos fenotipos, y (c) tabla de metadatos con los parámetros de configuración de cada fenotipo. | CU-07 |
| RF-07 | Resetear Vista | El frontend debe contar con un botón "Nueva Comparación" que limpie todos los resultados, gráficos y dropdowns seleccionados para reiniciar el flujo desde CU-01. | CU-08 |

---

## 3. Requerimientos No Funcionales

| ID | Categoría | Descripción | Relación con la Arquitectura |
|----|-----------|-------------|------------------------------|
| RNF-01 | Rendimiento | La consulta dual a la base de datos debe retornar ambos perfiles combinados en menos de 800 milisegundos, dado que el payload es mayor (6 arrays de ondas en total). | Requiere que `precomputed_profiles` esté correctamente indexada por `(profile_ohc, nH, nM, nL, stimulus_type)`. |
| RNF-02 | Escalabilidad | La carga simultánea de la herramienta por múltiples investigadores solo impacta al `core-service` (lectura de DB) y no al `simulation-service`, que puede seguir procesando otras simulaciones en paralelo. | Aislamiento correcto entre microservicios de la arquitectura de Facundo. |
| RNF-03 | Diferenciabilidad Visual | Los colores asignados a cada fenotipo deben mantenerse consistentes entre el Panel A (barras) y el Panel B (ondas), de modo que el investigador pueda identificar visualmente el Fenotipo A y el B sin releer la leyenda en cada gráfico. | Consistencia del Design System del frontend. |
| RNF-04 | Reproducibilidad | Dado que ambos fenotipos provienen de perfiles pre-computados deterministas, la comparación para una misma combinación de parámetros siempre debe retornar los mismos resultados numéricos. | Propiedad inherente del modelo Verhulst (RNF-07 de Screening Neonatal). |

---

## 4. Diagrama de Relación entre Casos de Uso

```mermaid
useCaseDiagram
    actor "Investigador" as Inv
    package "Análisis Comparativo de Fenotipos" {
        usecase "CU-01: Configurar Estímulo" as CU01
        usecase "CU-02: Configurar Fenotipo Envejecimiento" as CU02
        usecase "CU-03: Configurar Fenotipo Trauma" as CU03
        usecase "CU-04: Ejecutar Comparación" as CU04
        usecase "CU-05: Visualizar Comparativa EFR" as CU05
        usecase "CU-06: Analizar Morfología ABR" as CU06
        usecase "CU-07: Exportar Reporte" as CU07
        usecase "CU-08: Resetear Comparación" as CU08
    }

    Inv --> CU01
    CU01 --> CU02 : <<includes>>
    CU01 --> CU03 : <<includes>>
    CU02 --> CU04 : <<includes>>
    CU03 --> CU04 : <<includes>>
    CU04 --> CU05 : <<includes>>
    CU04 --> CU06 : <<extends>>
    CU05 --> CU07 : <<extends>>
    CU06 --> CU07 : <<extends>>
    Inv --> CU08
```
