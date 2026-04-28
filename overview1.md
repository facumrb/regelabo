
1. ¿QUÉ ES EL EFR (ENVELOPE FOLLOWING RESPONSE)?

EFR es una métrica o biomarcador que refleja cómo el oído reacciona a un sonido y produce impulsos nerviosos sincronizados con la envolvente del estímulo. Es una señal eléctrica que se puede medir en el tronco cerebral.

Utilidad principal:
- Evaluar la función auditiva en personas que no pueden reportar lo que escuchan (bebés, pacientes con dificultades de comunicación, etc.).
- Detectar posibles daños auditivos que no aparecen en una audiometría convencional (ej. pérdida auditiva oculta o sinapotopatía).

--------------------------------

2. ¿QUÉ HACE EL MODELO VERHULST?

El modelo simula el EFR sin necesidad de medirlo en una persona real. Dado un estímulo de audio de entrada, el modelo computa el EFR que produciría un oído, teniendo en cuenta tres grupos de parámetros:

   a) Perfil auditivo (audiograma):
   - Refleja cómo escucha el paciente en diferentes frecuencias.
   - Se define mediante archivos de "poles" (ej. Flat00, Flat20, Slope20, etc.).
   - Representa la pérdida de ganancia coclear (daño en células ciliadas externas).

   b) Parámetros biológicos y anatómicos de la simulación:
   - Son extensos y están definidos en los archivos:
      * inner_hair_cell2018.py   (células ciliadas internas)
      * auditory_nerve2018.py    (fibra del nervio auditivo)
      * ic_cn2018.py             (núcleo coclear y colículo inferior)
   - Incluyen constantes como capacitancias, conductancias, tiempos de adaptación, tasas de disparo espontáneo, etc.
   - Por ahora se toman los valores por defecto (calibrados para oído sano).

   c) Estímulo de audio de entrada:
   - Puede ser un tono puro, un clic, un tono modulado en amplitud (RAM), o incluso voz.
   - Se define en frecuencia, duración, nivel de presión sonora (dB SPL), etc.

---------------------------------

3. ¿CUÁL ES LA SALIDA DEL MODELO?

La salida principal es el valor del EFR simulado (amplitud en microvoltios, μV), generalmente a la frecuencia de modulación fundamental y sus armónicos. También se pueden obtener:
- Tasas de disparo de la fibra nerviosa (ANF)
- Potenciales de membrana de la célula ciliada
- Respuestas del núcleo coclear y colículo inferior
- Formas de onda de la ABR (respuesta auditiva del tronco cerebral)

-----------------------------------------------------------------------------------

4. LIMITACIÓN FUNDAMENTAL: BAJA UTILIDAD CLÍNICA CUANDO YA SE CONOCE EL AUDIOGRAMA

El modelo requiere como entrada el perfil auditivo (audiograma) del "paciente". Es decir, para simular el EFR de una persona concreta, **ya se debe haber realizado una medición real de su audiograma**.

En ese contexto, **generar un EFR simulado a partir del audiograma no aporta información clínica nueva**. El paciente ya ha sido diagnosticado (el audiograma indica su pérdida auditiva). Simular su EFR no cambia el diagnóstico ni revela nada que no se sepa ya, porque el modelo no es un predictor inverso (no puede deducir el audiograma a partir del EFR).

Por lo tanto, el modelo **no es útil como herramienta de diagnóstico complementario** en la práctica clínica diaria. Su valor no está en reemplazar o mejorar la medición del EFR real, sino en otros ámbitos (hay que explorarlo).

--------------------------------------------------------------
5. VERDADERA UTILIDAD DEL MODELO (INVESTIGACIÓN Y DESARROLLO)

El modelo es valioso para:

   a) Estudiar mecanismos fisiológicos:
   - Permite aislar y modificar parámetros biológicos (ej. adaptación de la célula ciliada, tasas de disparo neuronal, sinapotopatía) para ver cómo afectan al EFR. Esto no se puede hacer en humanos reales.

   b) Generar datos sintéticos controlados:
   - Se puede producir EFR para cualquier combinación de perfil auditivo, estímulo y nivel de daño, sin necesidad de reclutar pacientes. Útil para probar algoritmos de procesamiento de señales o entrenar modelos de machine learning.

   c) Explorar hipótesis sobre pérdidas auditivas "ocultas":
   - Por ejemplo, simular sinapotopatía (daño en la conexión entre célula ciliada y nervio) y ver cómo cambia el EFR, algo que el audiograma convencional no detecta.

   d) Optimizar parámetros de estímulo:
   - Encontrar qué frecuencias de modulación o qué niveles de sonido maximizan la sensibilidad del EFR a cierto tipo de daño.

   e) Validar modelos animales o humanos:
   - Comparar simulaciones con mediciones reales para ajustar y mejorar el modelo.

**En resumen:** El modelo no sirve para diagnosticar a un paciente del que ya se tiene el audiograma. Sirve para investigar cómo distintos tipos de daño (definidos arbitrariamente) afectan el EFR, lo cual puede guiar el desarrollo de nuevas pruebas diagnósticas o mejorar la interpretación de mediciones reales. Para eso es necesario entender los parámetros del modelo y las patologías que el modelo permite simular.

Se podría decir que el modelo es un vehículo para generar hipótesis sobre datos estadísticos, para luego poder generar estudios reales sobre estos temas. 

----------------------------------------------
6. LO QUE NOS FALTA (PENDIENTE / POR DEFINIR)

A. Con respecto al objetivo (prioritario, va a informar el resto de puntos): 
- No hemos definido claramente qué hipótesis queremos explorar o qué patrón buscamos visualizar con los datos generados.
- Posibles objetivos (a discutir):
    - ¿Mostrar cómo disminuye la amplitud del EFR al aumentar la pérdida auditiva (FlatXX)?
    - ¿Comparar el efecto de diferentes tipos de pérdida (plana vs. en pendiente) sobre la respuesta a distintas frecuencias de modulación?
    - ¿Explorar si el modelo es sensible a parámetros biológicos (ej. sinapotopatía) que el audiograma no refleja?
    - ¿Construir una herramienta interactiva que permita a un investigador "jugar" con los parámetros y ver el EFR resultante?
        
> Sin un objetivo claro, la infraestructura de datos y el dashboard no tendrán un propósito definido. Esto debe resolverse antes de avanzar con el diseño de la base de datos y el frontend.

B. Con respecto al modelo:
   - Entender en detalle los parámetros biológicos (por ahora usamos valores por defecto). No sabemos cuáles modificar para simular diferentes patologías (ej. sinapotopatía).
   - Definir qué estímulos de audio vamos a usar sistemáticamente (frecuencias, niveles, duración).
   - Decidir qué perfiles de pérdida auditiva vamos a simular (FlatXX, SlopeXX, personalizados con OHC_ind.py).

C. Con respecto a la generación de datos:
   - Falta diseñar una grilla de simulaciones (combinación de perfiles, niveles, frecuencias de modulación).
   - Automatizar la ejecución en lote (actualmente se corre una simulación por vez).
   - Almacenar los resultados en una base de datos (esquema a definir).

D. Con respecto a la infraestructura y visualización (depende del punto A):
   - Definir el esquema de base de datos (tablas: simulaciones, parámetros, resultados).
   - Implementar un backend que consulte los datos (FastAPI, etc.).
   - Diseñar el frontend (dashboard interactivo con gráficos: EFR vs. perfil auditivo, vs. nivel, vs. frecuencia de modulación).

----------------------------
7. PRÓXIMOS PASOS INMEDIATOS

- 1. **Definir el objetivo del proyecto (PRIORITARIO):**  
   Acordar qué pregunta queremos responder con los datos. Por ejemplo: ¿cómo varía el EFR con distintos perfiles de pérdida auditiva? ¿Qué tipo de gráficos necesitamos para explorar esa relación? Sin esto, no podemos avanzar.

- 2. **Diseñar una grilla pequeña de simulaciones:**  
   Elegir un subconjunto manejable (ej. 3 perfiles auditivos × 3 niveles de sonido × 2 frecuencias de modulación) que sea coherente con el objetivo definido.

- 3. **Ejecutar esas simulaciones** y guardar resultados. 

- 4. **Construir un prototipo de dashboard** que muestre los primeros gráficos según el objetivo definido (ej. EFR vs. perfil auditivo, vs. nivel, vs. frecuencia de modulación).

- 5. **Reunión para revisar los resultados** y ajustar los parámetros o el objetivo si es necesario.