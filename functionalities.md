# Funcionalidades del Laboratorio Virtual Auditivo
# Clasificación según Factibilidad con el Modelo Verhulst 2018

---

## ✅ DIRECTAMENTE FACTIBLES (implementadas en la plataforma)

Estas funcionalidades están soportadas directamente por el código actual del modelo Verhulst 2018 y forman parte de la plataforma.

### 1. Estudiar mecanismos fisiológicos

En simple: Entender cómo funciona cada una de las pequeñas piezas del oído interno de manera independiente y qué pasa cuando una sola de ellas falla.

Caso de uso: Una fonoaudióloga investigadora quiere averiguar exactamente de qué manera el daño exclusivo en una conexión nerviosa (sinapsis) afecta el envío de la señal eléctrica al cerebro, un aislamiento que sería imposible o antiético de realizar en un paciente humano vivo.

Parámetro manipulado: `storeflag` controla qué etapa biológica se almacena; se aísla modificando polos de Shera (OHC) o fibras AN (nH, nM, nL) independientemente.

Salida observada: Cualquier etapa del pipeline (velocidad BM, potencial IHC, tasas de disparo AN, ondas ABR).


### 2. Generar datos sintéticos controlados

En simple: Crear miles de "pacientes virtuales" en segundos, configurando un daño auditivo exacto en cada uno para realizar experimentos de forma masiva.

Caso de uso: Generar una gran cantidad de resultados de EFR virtuales para probar si un nuevo software de diagnóstico está leyendo bien los datos, ahorrando meses de tener que reclutar pacientes para estudios clínicos.

Parámetro manipulado: Pipeline paralelo (`ParallelRAMSimulationsEFR.py`) + audiogramas individuales convertidos a polos vía `OHC_ind`.

Salida observada: CSV con valores de EFR por sujeto, archivos `.mat` con datos completos del modelo.


### 3. Explorar hipótesis sobre pérdidas auditivas "ocultas"

En simple: Investigar tipos de sordera o dificultades auditivas (como entender el habla en ambientes ruidosos) que las pruebas clásicas (la audiometría de tonos puros) no logran detectar.

Caso de uso: Comprobar cómo cambia la señal nerviosa en pacientes expuestos crónicamente al ruido fuerte —como obreros o músicos— que se quejan de no entender en lugares concurridos, a pesar de que su audiometría tradicional de control dio "normal" (sinaptopatía).

Parámetro manipulado: Reducción selectiva de fibras AN (`nH`, `nM`, `nL`) sin modificar los polos de Shera (cóclea sana).

Salida observada: EFR reducido con audiometría (polos) normal → firma de sinaptopatía coclear.


### 4. Optimizar parámetros de estímulo

En simple: Descubrir qué tipo de sonido exacto arroja la mejor y más clara respuesta en las pruebas auditivas.

Caso de uso: Configurar el modelo para reproducir miles de pitidos con diferentes modulaciones hasta encontrar el diseño de estímulo que consiga "despertar" la lectura eléctrica (EFR) más fuerte y nítida. Una vez hallado, las fonoaudiólogas pueden empezar a usar ese sonido específico en los equipos de sus consultorios.

Parámetro manipulado: Frecuencia portadora del estímulo RAM (`get_RAM_stims.py`), barrido de frecuencias y niveles.

Salida observada: Valor de EFR (µV) para cada configuración de estímulo. Limitación: solo estímulos RAM actualmente.


### 5. Validar modelos animales o humanos

En simple: Cotejar que lo que dice la computadora corresponde fehacientemente con la forma en la que escuchan las especies reales.

Caso de uso: Comparar los resultados del modelo virtual sobre cómo se deforma un sonido complejo con los resultados de electroencefalogramas (EEGs) de pacientes de la clínica real para afinar la precisión del software.

Parámetro manipulado: Perfil de polos de Shera cargado desde audiogramas reales vía `OHC_ind`.

Salida observada: EFR, ondas ABR (W1, W3, W5) y velocidad BM exportados en `.mat` y CSV, comparables con registros clínicos reales.


### 8. Entrenamiento de Inteligencia Artificial (Machine Learning)

En simple: Alimentar con datos a ciertos programas informáticos inteligentes para que aprendan a diagnosticar por cuenta propia.

Caso de uso: Proveer 10.000 curvas cocleares simuladas a un algoritmo de Inteligencia Artificial para entrenarlo a detectar patrones prematuros de deterioro auditivo que a un especialista humano le tomaría demasiado tiempo y esfuerzo visual analizar individualmente en los estudios clínicos.

Parámetro manipulado: Pipeline paralelo con 33 perfiles precomputados + `OHC_ind` para audiogramas arbitrarios.

Salida observada: Datasets masivos de pares (perfil auditivo → EFR) en CSV, listos para ML.


### 9. Investigación en Screening Neonatal (BERA/ABR)

En simple: Usar el simulador para estudiar las ondas cerebrales exactas que se le miden a los bebés recién nacidos para detectar sorderas de nacimiento.

Caso de uso: Someter al modelo a diferentes problemas congénitos y analizar cómo se deforman las ondas ABR resultantes. Esto ayuda a los fonoaudiólogos a leer los estudios BERA de los bebés reales con más precisión para identificar el problema anatómico exacto.

Parámetro manipulado: Distintos perfiles patológicos de polos de Shera (Flat, Slope y combinaciones).

Salida observada: Ondas W1 (nervio auditivo), W3 (núcleo coclear), W5 (colículo inferior) del ABR ante cada perfil.


### 12. Sordera Oculta: Edad vs. Trauma Acústico

En simple: Determinar si el desgaste natural del oído por la edad arruina las conexiones nerviosas de la misma manera que lo hace un ruido extremadamente fuerte y repentino.

Caso de uso: Generar dos pacientes virtuales: uno envejecido paulatinamente y otro con un trauma acústico súbito. Evaluar si la caída en la señal eléctrica (EFR) es biológicamente igual en ambos casos, permitiendo afinar el diagnóstico según el historial de vida del paciente.

Parámetro manipulado: Paciente "envejecido" = polos Slope (OHC degradadas gradualmente). Paciente "trauma" = polos normales + fibras AN reducidas (nL=0, nM=0).

Salida observada: Comparación de EFR y formas de onda ABR entre ambos perfiles.

---

## ⚠️ PARCIALMENTE FACTIBLES (próxima posible implementación con extensión del modelo)

Estas funcionalidades son parcialmente soportadas por el modelo actual. Para su implementación completa, requieren extensiones específicas al código.

### 10. Estudio de Percepción de "Habla en Ruido"

En simple: Evaluar por qué las personas (especialmente los mayores) escuchan los sonidos pero no logran entender las palabras cuando hay ruido de fondo.

Caso de uso: Configurar el modelo con sordera por edad y pasarle un archivo de audio real con voz humana mezclada con ruido de restaurante. Medir qué porcentaje del nervio logra disparar a tiempo con las consonantes, ayudando a diseñar estrategias que mejoren la comprensión.

Estado actual: El modelo acepta cualquier señal acústica 1D como entrada (`sign` en `model2018()`), por lo que técnicamente se puede inyectar habla+ruido. Sin embargo, el modelo solo simula hasta el Colículo Inferior (IC); no modela la corteza auditiva ni la percepción de habla.

Extensión necesaria: Agregar un módulo de procesamiento cortical o métricas de representación temporal (TRF - Temporal Response Function) post-IC para cuantificar la calidad de la codificación neural del habla.


### 14. Beneficio de Audífonos

En simple: Predecir qué tipo de sordera responde mejor a un audífono comparando perfiles "planos" vs. "pendiente".

Estado actual: Se puede simular el efecto de un audífono indirectamente, amplificando la señal de entrada antes de pasarla al modelo (pre-procesamiento externo con ganancia lineal simple).

Extensión necesaria: Implementar un módulo de procesamiento de audífono que modele compresión dinámica multicanal (WDRC), reducción de ruido, control de feedback y prescripción de ganancia (NAL-NL2 o DSL v5).


### 15. Seguimiento del Habla

En simple: Medir cómo una pérdida auditiva destruye la capacidad del cerebro para seguir el ritmo del habla.

Estado actual: Se puede observar la sincronización neural con la envolvente de estímulos complejos a nivel subcortical (salida del IC).

Extensión necesaria: Implementar métricas de seguimiento temporal del habla post-IC, como análisis TRF (Temporal Response Function) o correlación cruzada envolvente-respuesta neural, que requieren un modelo cortical simplificado.

---

## ❌ NO FACTIBLES ACTUALMENTE (posible mejora futura con extensiones)

Estas funcionalidades están fuera del alcance del modelo Verhulst 2018 actual. Su implementación requiere el desarrollo de módulos enteramente nuevos.

### 6. Optimización y evaluación de Audífonos e Implantes Cocleares

En simple: Simular los efectos de dispositivos de corrección auditiva sobre un oído dañado.

Caso de uso: Antes de lanzar un nuevo implante coclear al mercado, los ingenieros biomédicos y audiólogos utilizan el modelo para predecir si una nueva estrategia de estimulación eléctrica ayudará al paciente a distinguir mejor las consonantes en medio del ruido de un restaurante.

Por qué no es factible: No existe ningún módulo de estimulación eléctrica (implante coclear) ni de procesamiento de señal de audífono en el código. El modelo simula la fisiología natural del oído; no acepta electrodos virtuales ni estrategias de codificación como CIS, ACE, etc.

Extensiones necesarias:
- Módulo de estimulación eléctrica coclear (electrodos virtuales, corriente pulsátil, distribución de campo eléctrico).
- Implementación de estrategias de codificación (CIS, ACE, FSP) que conviertan audio en patrones de pulsos eléctricos.
- Módulo de procesamiento de señal de audífono (compresión WDRC, reducción de ruido, prescripción de ganancia).


### 7. Audiología de Precisión y Ajuste Personalizado

En simple: Ajustar tratamientos médicos y parámetros de dispositivos "a medida" usando una réplica digital del oído del paciente.

Caso de uso: Un paciente con implante coclear asiste a la clínica; la fonoaudióloga carga los detalles del daño anatómico del paciente en el modelo computacional para "ensayar" docenas de configuraciones eléctricas de sus audífonos en un entorno virtual, reduciendo enormemente la cantidad de visitas de calibración del paciente.

Por qué no es factible: Si bien la creación de una "réplica digital del oído" SÍ es factible (mediante `OHC_ind` + manipulación de fibras AN), la parte de ajustar configuraciones de dispositivos no lo es porque no hay modelo de audífono ni implante.

Extensiones necesarias:
- Los mismos módulos de dispositivos mencionados en la funcionalidad #6.
- Interfaz de ajuste paramétrico de dispositivos con retroalimentación visual inmediata.
- Base de datos de perfiles de pacientes con historial de ajustes.

Nota: La parte de "gemelo digital del oído" ya existe (OHC_ind convierte audiograma → perfil coclear).


### 11. Origen y Modelado del Tinnitus (Zumbido)

En simple: Descubrir qué niveles exactos de daño en las células del oído provocan que el nervio comience a enviar "señales fantasma" al cerebro cuando hay silencio absoluto.

Caso de uso: Modificar los parámetros de daño celular en el simulador hasta que el nervio auditivo comience a tener un "disparo espontáneo" alterado. Esto aporta datos vitales para entender cómo se desencadena biológicamente el tinnitus y cómo probar terapias sonoras para cancelarlo.

Por qué no es factible: El tinnitus se origina por actividad espontánea anormal del nervio auditivo y ganancia central adaptativa. El modelo de Verhulst 2018 calcula la respuesta evocada (ante un estímulo); no modela la actividad espontánea del nervio ni la plasticidad de ganancia central.

Extensiones necesarias:
- Modelo de actividad espontánea del nervio auditivo (tasa de disparo en reposo, distribución de intervalos inter-spike).
- Modelo de ganancia central adaptativa (homeostasis sináptica que aumenta la ganancia cuando disminuye la entrada periférica).
- Simulación de la percepción en ausencia de estímulo (condición de silencio).


### 13. Latencia Binaural (Equilibrio y Localización de Sonido)

En simple: Estudiar el "retraso" de la señal eléctrica cuando una persona tiene un oído sano y el otro dañado, lo cual arruina la capacidad de saber de dónde viene un sonido.

Caso de uso: Ejecutar el simulador simultáneamente para un oído izquierdo sano y un derecho dañado. Reproducir un sonido estéreo y medir el retraso en milisegundos con el que cada señal llega al cerebro, usando esos datos para programar mejor los audífonos unilaterales.

Por qué no es factible: El modelo es monoaural (un solo oído a la vez). No existe un modelo de interacción binaural (oliva superior, MSO, LSO) en el código.

Extensiones necesarias:
- Módulo de procesamiento binaural (Oliva Superior Medial y Lateral: MSO para ITD, LSO para ILD).
- Framework para ejecutar dos instancias del modelo simultáneamente y cruzar las salidas.
- Modelo de integración binaural que compare latencias y amplitudes entre ambos oídos.

Workaround parcial: Se pueden ejecutar dos simulaciones monoaurales independientes y comparar las latencias de W5 manualmente. Esto da una estimación del interaural time difference (ITD), aunque no modela la integración binaural real.

---

## Categorías Actualizadas

### Implementadas (directamente factibles):

**Investigación mecanicista:**
- 1. Estudiar mecanismos fisiológicos
- 5. Validar modelos animales o humanos

**Simulación y datos:**
- 2. Generar datos sintéticos controlados
- 8. Entrenamiento de Inteligencia Artificial (Machine Learning)

**Sordera oculta:**
- 3. Explorar hipótesis sobre pérdidas auditivas "ocultas"
- 12. Sordera Oculta: Edad vs. Trauma Acústico

**Diseño de estímulos:**
- 4. Optimizar parámetros de estímulo

**Screening neonatal:**
- 9. Investigación en Screening Neonatal (BERA/ABR)


### Próximas implementaciones (requieren extensión del modelo):
- 10. Estudio de Percepción de "Habla en Ruido" → extensión: modelo cortical
- 14. Beneficio de Audífonos → extensión: módulo de procesamiento de audífono
- 15. Seguimiento del Habla → extensión: métricas TRF post-IC


### Mejoras futuras (requieren módulos nuevos):
- 6. Audífonos e Implantes Cocleares → módulo de estimulación eléctrica + procesamiento HA
- 7. Audiología de Precisión → módulos de dispositivos + interfaz de ajuste
- 11. Modelado del Tinnitus → modelo de actividad espontánea + ganancia central
- 13. Latencia Binaural → módulo de procesamiento binaural (MSO/LSO)