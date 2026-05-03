# Documentación del Modelo Verhulst (2018) en el Laboratorio Virtual Auditivo

Este documento sintetiza la visión general, el propósito y las funcionalidades detalladas del modelo computacional de Verhulst (2018) integrado en nuestra plataforma. Combina la teoría de funcionamiento, los casos de uso en fonoaudiología y el estado de factibilidad de cada utilidad.

---

## 1. ¿Qué es el EFR y qué hace el Modelo Verhulst?

**EFR (Envelope Following Response):** Es una métrica o biomarcador que refleja cómo el oído reacciona a un sonido y produce impulsos nerviosos sincronizados con la envolvente del estímulo. Es una señal eléctrica que se puede medir en el tronco cerebral. Permite evaluar la función auditiva en personas que no pueden reportar lo que escuchan (bebés, pacientes con dificultades de comunicación) y detectar daños ocultos que una audiometría convencional no registra.

**El Modelo Verhulst (2018):** Basado en los artículos "*A cochlear epiphenomenon or auditory nerve feature? Evaluating Envelope Following Responses (EFRs) in simulations and human listeners*" y "*Computational modeling of the human auditory periphery...*", es un simulador biológicamente informado de la vía auditiva periférica. Dado un estímulo de audio de entrada, el modelo computa el EFR que produciría un oído específico, sin necesidad de medirlo en una persona real.

### Entradas del Modelo:
1.  **Perfil auditivo (audiograma):** Refleja cómo escucha el paciente en diferentes frecuencias. Está representado mediante archivos de polos de Shera (ej. `Flat00`, `Flat20`, `Slope20`, etc.) que indican la pérdida de ganancia coclear (daño en las células ciliadas externas).
2.  **Parámetros biológicos/anatómicos:** Constantes biofísicas configurables (capacitancias, conductancias, tiempos de adaptación, tasas de disparo espontáneo, etc.). Están definidos extensamente en archivos específicos de la simulación:
    *   `inner_hair_cell2018.py` (células ciliadas internas)
    *   `auditory_nerve2018.py` (fibra del nervio auditivo)
    *   `ic_cn2018.py` (núcleo coclear y colículo inferior)
    Por defecto, toman los valores calibrados para un oído sano.
3.  **Estímulo de audio de entrada:** Puede ser un tono puro, un clic, un tono modulado en amplitud (RAM), o incluso voz. Se define en frecuencia, duración y nivel de presión sonora (dB SPL).

### Salidas del Modelo:
La salida principal es el valor del EFR simulado (amplitud en microvoltios, μV), generalmente a la frecuencia de modulación fundamental y sus armónicos. También se pueden obtener:
- Tasas de disparo de la fibra nerviosa (ANF).
- Potenciales de membrana de la célula ciliada.
- Respuestas del núcleo coclear y colículo inferior.
- Formas de onda de la ABR (respuesta auditiva del tronco cerebral: ondas W1, W3, W5).
- Velocidad de la membrana basilar (BM).

---

## 2. Limitación Fundamental y Verdadera Utilidad

**El modelo NO es útil como herramienta de diagnóstico clínico complementario en la práctica diaria.** 
Dado que requiere el audiograma como entrada, simular el EFR de una persona concreta implica que ya se debe haber realizado una medición real de su audiograma. Generar un EFR simulado no aporta información clínica nueva ni cambia el diagnóstico; el modelo no es un predictor inverso (no puede deducir el audiograma a partir del EFR). Su valor no está en reemplazar o mejorar la medición del EFR real.

**Su verdadera utilidad reside en la Investigación y Desarrollo (I+D).** 
Actúa como un **puente fundamental** entre el daño anatómico microscópico (invisible) y las ondas eléctricas (EFR/ABR) medibles. Se podría decir que el modelo es un vehículo para generar hipótesis sobre datos estadísticos, para luego poder generar estudios reales sobre estos temas. 

Al entender cómo una pérdida de sinapsis nerviosas (sordera oculta) modifica una señal, el modelo Verhulst permite a los investigadores crear pruebas más sensibles que algún día la fonoaudióloga sí instalará en su consultorio para identificar daños auditivos de manera muy temprana, antes de que lleguen a arruinar una audiometría estándar. Sirve como plataforma para diseñar, predecir y validar los exámenes auditivos del futuro.

---

## 3. Funcionalidades y Casos de Uso (Clasificación por Factibilidad)

A continuación se detallan todas las utilidades identificadas para el modelo en el ámbito de la fonoaudiología y audiología computacional, categorizadas según qué tan factible es implementarlas con la versión actual del código base.

### ✅ DIRECTAMENTE FACTIBLES (Implementadas en la plataforma actual)

**1. Estudiar mecanismos fisiológicos**
*   **En simple:** Entender cómo funciona cada pieza del oído interno independientemente y qué ocurre cuando falla.
*   **Caso de uso:** Investigar cómo el daño exclusivo en una conexión nerviosa (sinapsis) afecta la señal eléctrica al cerebro, un aislamiento que sería imposible o antiético de realizar en un paciente humano vivo.
*   **Parámetro manipulado:** `storeflag` controla qué etapa biológica se almacena; se aísla modificando polos de Shera (OHC) o fibras AN (nH, nM, nL) independientemente.
*   **Salida observada:** Cualquier etapa del pipeline (velocidad BM, potencial IHC, tasas de disparo AN, ondas ABR).

**2. Generar datos sintéticos controlados**
*   **En simple:** Crear miles de "pacientes virtuales" en segundos, configurando un daño auditivo exacto en cada uno para experimentos masivos.
*   **Caso de uso:** Generar gran cantidad de resultados EFR para probar si un nuevo software de diagnóstico lee bien los datos, ahorrando meses de reclutar pacientes.
*   **Parámetro manipulado:** Pipeline paralelo (`ParallelRAMSimulationsEFR.py`) + audiogramas individuales convertidos a polos vía `OHC_ind`.
*   **Salida observada:** CSV con valores de EFR por sujeto, archivos `.mat` con datos completos del modelo.

**3. Explorar hipótesis sobre pérdidas auditivas "ocultas"**
*   **En simple:** Investigar sorderas o dificultades auditivas (como entender habla en ruido) que la audiometría tradicional no logra detectar.
*   **Caso de uso:** Comprobar cambios en la señal nerviosa en pacientes expuestos crónicamente a ruidos fuertes con audiometría "normal" (sinaptopatía).
*   **Parámetro manipulado:** Reducción selectiva de fibras AN (`nH`, `nM`, `nL`) sin modificar los polos de Shera (cóclea sana).
*   **Salida observada:** EFR reducido con audiometría (polos) normal → firma de sinaptopatía coclear.

**4. Optimizar parámetros de estímulo**
*   **En simple:** Descubrir qué diseño exacto de sonido produce la lectura eléctrica más nítida.
*   **Caso de uso:** Configurar el modelo para reproducir miles de pitidos con diferentes modulaciones hasta encontrar el estímulo para los equipos de los consultorios.
*   **Parámetro manipulado:** Frecuencia portadora del estímulo RAM (`get_RAM_stims.py`), barrido de frecuencias y niveles.
*   **Salida observada:** Valor de EFR (µV) para cada configuración de estímulo. Limitación: solo estímulos RAM actualmente.

**5. Validar modelos con datos clínicos reales**
*   **En simple:** Cotejar que el simulador coincida fehacientemente con la forma en que escuchan especies reales.
*   **Caso de uso:** Comparar resultados virtuales sobre cómo se deforma un sonido con electroencefalogramas (EEGs) de pacientes reales para afinar la precisión del software.
*   **Parámetro manipulado:** Perfil de polos de Shera cargado desde audiogramas reales vía `OHC_ind`.
*   **Salida observada:** EFR, ondas ABR (W1, W3, W5) y velocidad BM exportados en `.mat` y CSV, comparables con registros clínicos reales.

**8. Entrenamiento de Inteligencia Artificial (Machine Learning)**
*   **En simple:** Alimentar algoritmos con datos para que aprendan a diagnosticar por cuenta propia.
*   **Caso de uso:** Proveer 10.000 curvas cocleares simuladas a una IA para que detecte patrones prematuros de deterioro que a un especialista le tomaría mucho tiempo y esfuerzo.
*   **Parámetro manipulado:** Pipeline paralelo con 33 perfiles precomputados + `OHC_ind` para audiogramas arbitrarios.
*   **Salida observada:** Datasets masivos de pares (perfil auditivo → EFR) en CSV, listos para ML.

**9. Investigación en Screening Neonatal (BERA/ABR)**
*   **En simple:** Estudiar ondas cerebrales medidas en recién nacidos para detectar sorderas congénitas.
*   **Caso de uso:** Someter el modelo a defectos patológicos para ver cómo se deforman las ondas ABR, ayudando a los fonoaudiólogos a leer estudios BERA con más precisión.
*   **Parámetro manipulado:** Distintos perfiles patológicos de polos de Shera (Flat, Slope y combinaciones).
*   **Salida observada:** Ondas W1 (nervio auditivo), W3 (núcleo coclear), W5 (colículo inferior) del ABR ante cada perfil.

**12. Sordera Oculta: Edad vs. Trauma Acústico**
*   **En simple:** Determinar si el desgaste natural por edad arruina las conexiones nerviosas igual que un ruido fuerte repentino.
*   **Caso de uso:** Generar paciente "envejecido" y paciente con "trauma súbito" para evaluar si la caída de la señal es biológicamente igual, afinando el diagnóstico.
*   **Parámetro manipulado:** Paciente "envejecido" = polos Slope (OHC degradadas gradualmente). Paciente "trauma" = polos normales + fibras AN reducidas (nL=0, nM=0).
*   **Salida observada:** Comparación de EFR y formas de onda ABR entre ambos perfiles.

---

### ⚠️ PARCIALMENTE FACTIBLES (Requieren extensión menor del modelo)

**10. Estudio de Percepción de "Habla en Ruido"**
*   **En simple:** Evaluar por qué las personas escuchan sonidos pero no logran entender palabras cuando hay ruido de fondo.
*   **Estado actual:** El modelo acepta cualquier señal acústica 1D como entrada (`sign` en `model2018()`), por lo que técnicamente se puede inyectar habla+ruido. Sin embargo, el modelo solo simula hasta el Colículo Inferior (IC); no modela la corteza auditiva ni la percepción de habla.
*   **Extensión necesaria:** Agregar un módulo de procesamiento cortical o métricas de representación temporal (TRF - Temporal Response Function) post-IC para cuantificar la calidad de la codificación neural del habla.

**14. Beneficio de Audífonos**
*   **En simple:** Predecir qué tipo de sordera responde mejor a un audífono comparando perfiles "planos" vs. "pendiente".
*   **Estado actual:** Se puede simular el efecto de un audífono indirectamente, amplificando la señal de entrada pasivamente (pre-procesamiento externo con ganancia lineal simple).
*   **Extensión necesaria:** Implementar un módulo de procesamiento de audífono que modele compresión dinámica multicanal (WDRC), reducción de ruido, control de feedback y prescripción de ganancia (NAL-NL2 o DSL v5).

**15. Seguimiento del Habla**
*   **En simple:** Medir cómo una pérdida auditiva destruye la capacidad del cerebro para seguir el ritmo del habla.
*   **Estado actual:** Se puede observar la sincronización neural con la envolvente de estímulos complejos a nivel subcortical (salida del IC).
*   **Extensión necesaria:** Implementar métricas de seguimiento temporal del habla post-IC, como análisis TRF (Temporal Response Function) o correlación cruzada envolvente-respuesta neural, que requieren un modelo cortical simplificado.

---

### ❌ NO FACTIBLES ACTUALMENTE (Requieren módulos completamente nuevos)

**6. Optimización y evaluación de Audífonos e Implantes Cocleares**
*   **En simple / Caso de uso:** Predecir si una nueva estrategia eléctrica de implante mejorará la comprensión en ruido antes de lanzar un dispositivo al mercado.
*   **Por qué no:** El modelo simula la fisiología natural del oído; no acepta electrodos virtuales ni estrategias de codificación como CIS, ACE, etc.
*   **Extensiones necesarias:** 
    * Módulo de estimulación eléctrica coclear (electrodos virtuales, corriente pulsátil, distribución de campo eléctrico).
    * Implementación de estrategias de codificación (CIS, ACE, FSP) que conviertan audio en patrones de pulsos eléctricos.
    * Módulo de procesamiento de señal de audífono (compresión WDRC, reducción de ruido, prescripción de ganancia).

**7. Audiología de Precisión y Ajuste Personalizado**
*   **En simple / Caso de uso:** Usar una réplica digital del oído para ajustar tratamientos médicos y parámetros de dispositivos "a medida" (calibrar audífonos virtuales para reducir visitas del paciente).
*   **Por qué no:** La parte de crear un "gemelo digital del oído" ya existe (`OHC_ind` convierte audiograma en perfil coclear). Pero la parte de ajustar configuraciones falla porque no hay modelo de audífono ni implante integrado.
*   **Extensiones necesarias:**
    * Los mismos módulos de dispositivos mencionados en la funcionalidad #6.
    * Interfaz de ajuste paramétrico de dispositivos con retroalimentación visual inmediata.
    * Base de datos de perfiles de pacientes con historial de ajustes.

**11. Origen y Modelado del Tinnitus (Zumbido)**
*   **En simple / Caso de uso:** Modificar parámetros de daño celular hasta que el nervio envíe "señales fantasma" (disparo espontáneo alterado) en silencio total.
*   **Por qué no:** El modelo de Verhulst 2018 calcula respuestas *evocadas* (ante sonido). No simula la actividad espontánea patológica ni la plasticidad neuronal o ganancia central adaptativa.
*   **Extensiones necesarias:**
    * Modelo de actividad espontánea del nervio auditivo (tasa de disparo en reposo, distribución de intervalos inter-spike).
    * Modelo de ganancia central adaptativa (homeostasis sináptica que aumenta la ganancia cuando disminuye la entrada periférica).
    * Simulación de la percepción en ausencia de estímulo (condición de silencio).

**13. Latencia Binaural (Equilibrio y Localización de Sonido)**
*   **En simple / Caso de uso:** Estudiar el "retraso" de la señal eléctrica cuando un oído está sano y el otro dañado (monoaural vs binaural).
*   **Por qué no:** El modelo es exclusivamente monoaural; carece de módulos de integración binaural en la Oliva Superior.
*   **Workaround parcial:** Se pueden ejecutar dos simulaciones monoaurales independientes y comparar manualmente las latencias de las ondas W5. Esto da una estimación del *interaural time difference* (ITD), aunque no modela la integración binaural real.
*   **Extensiones necesarias:**
    * Módulo de procesamiento binaural (Oliva Superior Medial y Lateral: MSO para ITD, LSO para ILD).
    * Framework para ejecutar dos instancias del modelo simultáneamente y cruzar las salidas.
    * Modelo de integración binaural que compare latencias y amplitudes entre ambos oídos.

---

## 4. Próximos Pasos del Proyecto (Pendientes)

La infraestructura de datos y el panel de visualización no tendrán propósito sin un objetivo científico claro. Las áreas clave a definir y ejecutar son:

**A. Objetivo Científico (Prioridad #1):**
*   No se ha definido claramente la hipótesis o patrón a visualizar con los datos generados. Sin esto, la base de datos y el frontend carecerán de propósito. Posibles objetivos a debatir:
    *   ¿Mostrar cómo disminuye la amplitud del EFR al aumentar la pérdida auditiva (FlatXX)?
    *   ¿Comparar el efecto de diferentes tipos de pérdida (plana vs. en pendiente) sobre la respuesta a distintas frecuencias de modulación?
    *   ¿Explorar si el modelo es sensible a parámetros biológicos (ej. sinaptopatía) que el audiograma no refleja?
    *   ¿Construir una herramienta interactiva que permita a un investigador "jugar" con los parámetros libremente y ver el EFR resultante?

**B. Parametrización del Modelo:**
*   Entender en detalle los parámetros biológicos (actualmente se usan valores por defecto). No sabemos cuáles modificar para simular diferentes patologías (ej. sinaptopatía).
*   Definir los estímulos sistemáticos de audio a usar (frecuencias, niveles, duración).
*   Decidir qué perfiles de pérdida se van a simular sistemáticamente (`FlatXX`, `SlopeXX`, o personalizados con `OHC_ind.py`).

**C. Generación de Datos y Simulación:**
*   Diseñar una grilla pequeña de simulaciones (combinación manejable: ej. 3 perfiles × 3 niveles de sonido × 2 frecuencias de modulación) coherente con el objetivo definido.
*   Automatizar la ejecución en lote (actualmente se corre una simulación por vez).
*   Almacenar los resultados en una base de datos (esquema a definir).

**D. Infraestructura y Visualización:**
*   Definir el esquema exacto de base de datos (tablas: simulaciones, parámetros, resultados).
*   Implementar un backend/API que consulte estos datos (FastAPI, etc.).
*   Desarrollar un prototipo de dashboard interactivo para contrastar gráficamente las variables clave (EFR vs. perfil auditivo, vs. nivel, vs. frecuencia de modulación).
*   Programar reuniones iterativas de revisión de resultados para ajustar parámetros u objetivos según sea necesario.
