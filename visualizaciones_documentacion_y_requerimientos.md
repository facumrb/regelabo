# Visualizaciones Diagnósticas del Modelo de Verhulst — Documentación Fonoaudiológica y Requerimientos Web

---

# PARTE 1: Guía Fonoaudiológica de las Visualizaciones

---

## 1. Mapa de Calor Coclear (Ganancia OHC)

### ¿Qué es?

Es una representación gráfica bidimensional que muestra **cómo el amplificador coclear (las células ciliadas externas — OHC) trabaja en tiempo real** a lo largo de toda la cóclea. Cada punto del mapa representa el valor del **polo de Shera** en una sección coclear específica (eje Y, frecuencia) y en un instante de tiempo específico (eje X, milisegundos).

El polo de Shera es un parámetro que representa la ganancia local del amplificador coclear (OHC); en esta visualización se suele resumir en un valor escalar: valores bajos indican mayor ganancia y compresión activa (verde), mientras que valores altos indican menor ganancia o saturación (rojo).
- **Polo bajo** (verde en el mapa) → las OHC están amplificando activamente → el oído detecta sonidos suaves → **audición sana**.
- **Polo alto** (rojo en el mapa) → las OHC están saturadas o dañadas → el oído pierde sensibilidad → **pérdida auditiva**.

### ¿Cómo funciona internamente?

Durante la simulación, en cada uno de los ~40.000 pasos temporales (400 ms × 100 kHz), el modelo calcula el polo de Shera de las 401 secciones cocleares. Este valor cambia dinámicamente porque las OHC saturan con sonidos fuertes (compresión coclear) y vuelven a amplificar cuando el sonido baja. El mapa de calor almacena y muestra toda esta historia temporal.

### ¿Qué permite analizar?

| Observación en el mapa | Interpretación clínica |
|---|---|
| Todo el mapa verde con franjas rojas periódicas | **Oído sano** — las OHC comprimen durante los picos del estímulo RAM y se recuperan durante los silencios. El patrón periódico indica compresión activa. |
| Región de altas frecuencias permanentemente roja | **Pérdida en agudos** — las OHC de la base coclear están dañadas o ausentes. Corresponde a una hipoacusia neurosensorial de tipo pendiente descendente. |
| Todo el mapa uniformemente rojo | **Pérdida profunda** — las OHC están dañadas en toda la cóclea. Correlato de un audiograma con pérdida plana severa. |
| Mapa verde sin franjas periódicas | **Estímulo demasiado suave** — las OHC nunca saturan, la compresión no se activa. No hay información diagnóstica útil. |
| Transición gradual verde→rojo de graves a agudos | **Presbiacusia** — patrón clásico de pérdida progresiva por edad, donde las frecuencias altas se pierden primero. |

### ¿En qué contexto de trabajo se usa?

- **Investigación:** Para estudiar cómo diferentes perfiles de pérdida auditiva (Flat10, Slope25, etc.) afectan el patrón de compresión coclear en respuesta a un mismo estímulo.
- **Educación:** Para mostrar visualmente a estudiantes de fonoaudiología el concepto abstracto de "compresión coclear no lineal" y cómo difiere entre un oído sano y uno patológico.
- **Calibración de audífonos (potencial):** Para determinar en qué bandas frecuenciales la compresión biológica ha dejado de funcionar, indicando dónde el audífono debería compensar con compresión artificial.

### ¿Cómo se interpreta?

El fonoaudiólogo debe buscar tres cosas:
1. **¿Dónde está el rojo?** → indica las regiones frecuenciales dañadas.
2. **¿Hay alternancia periódica verde-rojo?** → indica que la compresión sigue activa (buen pronóstico).
3. **¿La transición verde-rojo es abrupta o gradual?** → abrupta indica daño focal (trauma acústico), gradual indica daño difuso (presbiacusia, ototoxicidad).

---

## 2. Panel de Vesículas Sinápticas — Fibras HSR (Dinámica del RRP)

### ¿Qué es?

Es un gráfico temporal que muestra el **estado de la sinapsis entre la célula ciliada interna (IHC) y el nervio auditivo** en tiempo real. Este panel visualiza específicamente la dinámica de las **fibras HSR (High Spontaneous Rate — alta tasa espontánea, umbral bajo)** en frecuencias seleccionadas:

- **qt (azul):** cantidad de vesículas en el RRP (Ready Releasable Pool), es decir, las vesículas "listas para disparar". Máximo: 14. Cuando un sonido llega, estas vesículas se liberan (exocitosis) y la fibra nerviosa dispara. Si se agotan, la fibra no puede responder.
- **wt (naranja):** cantidad de vesículas en el pool de reserva. Máximo: 60. Alimenta al RRP y se repone más lentamente.
- **available (verde):** fracción de fibras nerviosas que no están en período refractario, es decir, disponibles para disparar. Va de 0 (todas ocupadas recuperándose) a 1 (todas listas para disparar).

Las fibras HSR son las más sensibles del nervio auditivo (tasa espontánea: 68.5 sp/s, tasa pico: 3000 sp/s). Son las primeras en activarse ante sonidos suaves y las primeras en saturar ante sonidos fuertes.

### ¿Cómo funciona internamente?

El modelo simula un ciclo de vesículas sinápticas inspirado en la biofísica real:

```
Pool de Reserva (wt, 60 vesículas)
    ↓ tasa de reposición: 700/s
RRP (qt, 14 vesículas)
    ↓ exocitosis (gatillada por Ca²⁺)
Liberación de neurotransmisor → Disparo neural
    ↓ 
Período refractario (0.6 ms absoluto + relativo exponencial)
    ↓
Fibra disponible nuevamente
```

Este ciclo se ejecuta para cada muestra temporal y para cada sección coclear. El panel muestra la evolución de qt, wt y available a lo largo de los 400 ms de estimulación.

### ¿Qué permite analizar?

| Observación en el panel | Interpretación clínica |
|---|---|
| qt cae de 14 a ~5 al inicio y se estabiliza | **Adaptación sináptica normal** — la sinapsis se agota parcialmente con la estimulación sostenida pero mantiene un nivel funcional. |
| qt cae a ~0 y no se recupera | **Agotamiento sináptico** — la sinapsis no puede mantener la estimulación. Puede indicar que la tasa de estimulación es demasiado alta o que la sinapsis es deficiente. |
| qt fluctúa con periodicidad de ~9 ms | **Sincronización con el estímulo RAM** — las vesículas se agotan durante los pulsos del RAM - Rectangular Amplitude Modulation - (110 Hz ≈ 9.1 ms) y se reponen durante los silencios. Indica buena codificación temporal. |
| available cae por debajo de 0.5 sostenidamente | **Saturación de refractariedad** — más de la mitad de las fibras están "ocupadas" recuperándose. La tasa de disparo máxima está limitada. |
| wt decrece lentamente a lo largo de toda la simulación | **Depleción del pool de reserva** — la estimulación prolongada agota las reservas. Relevante para explicar la fatiga auditiva con exposición prolongada al ruido. |

### ¿En qué contexto de trabajo se usa?

- **Investigación en sordera oculta:** Comparar simulaciones con diferentes distribuciones de fibras HSR/MSR/LSR y observar cómo cambia la dinámica de las fibras HSR en el panel de vesículas.
- **Diseño de estímulos óptimos:** Determinar si una frecuencia de modulación diferente (por ejemplo, 40 Hz vs. 110 Hz) produce un patrón de agotamiento/recuperación que sea más sensible para detectar sinaptopatía.
- **Comprensión de la adaptación auditiva:** Explicar por qué un paciente puede oír bien un sonido breve pero tiene dificultad con la conversación sostenida (el pool de vesículas se agota).

### ¿Cómo se interpreta?

El fonoaudiólogo debe buscar:
1. **¿Cuánto cae qt al inicio?** → Caída profunda (a < 3) indica alta demanda vs. baja capacidad sináptica.
2. **¿Se recupera qt entre pulsos del RAM?** → Sí = buena reposición sináptica. No = sinapsis comprometida.
3. **¿La curva de available se mantiene estable?** → Sí = las fibras rotan bien. No = demasiadas fibras están refractarias simultáneamente.
4. **¿Cómo difiere entre frecuencias?** → Si qt se agota más rápido a 4 kHz que a 500 Hz, hay un problema frecuencia-específico en la sinapsis.

---

## 3. Panel de Vesículas Sinápticas — Fibras MSR (Dinámica del RRP)

### ¿Qué es?

Es el equivalente del panel HSR pero para las **fibras MSR (Medium Spontaneous Rate — tasa espontánea media)**. Estas fibras tienen un umbral intermedio (tasa espontánea: 10 sp/s, tasa pico: 1000 sp/s) y representan un eslabón funcional entre las fibras de baja y alta sensibilidad.

Muestra las mismas tres variables que el panel HSR (qt, wt y available), pero los valores reflejan la cinética sináptica particular de las fibras MSR: menor actividad espontánea y menor tasa pico que las HSR.

### ¿Cómo funciona internamente?

Utiliza el mismo modelo biofísico de dos pools de vesículas que el panel HSR (ver sección 2), pero con parámetros específicos de las fibras MSR:
- **Tasa espontánea (sp):** 10 sp/s (vs. 68.5 sp/s en HSR)
- **Tasa pico (psr):** 1000 sp/s (vs. 3000 sp/s en HSR)

Estas diferencias hacen que las fibras MSR tengan un estado estacionario diferente en reposo: menor actividad basal y menor agotamiento espontáneo del RRP.

### ¿Qué permite analizar?

| Observación | Interpretación |
|---|---|
| qt de MSR se mantiene más lleno que el de HSR durante estimulación | **Comportamiento esperado** — las MSR tienen menor tasa de liberación, por lo que depletan menos el RRP. |
| qt de MSR cae significativamente durante el estímulo | **Estímulo intenso o frecuencia de modulación alta** — incluso las fibras de umbral medio están siendo reclutadas agresivamente. |
| Patrón de available similar al de HSR | **Ambas poblaciones están bien reclutadas** — el estímulo es suficiente para activar fibras de sensibilidad media. |

### ¿En qué contexto de trabajo se usa?

- **Investigación en sinaptopatía selectiva:** Las fibras MSR pueden dañarse de forma independiente a las HSR. Visualizar su dinámica permite detectar patrones de daño que serían invisibles si solo se observan las HSR.
- **Calibración de protocolos de estimulación:** Permite verificar que el nivel del estímulo es suficiente para reclutar fibras MSR además de las HSR.

### ¿Cómo se interpreta?

El fonoaudiólogo debe comparar este panel con el de HSR (sección 2):
1. **¿El qt de MSR depleta menos que el de HSR?** → Sí = las MSR no están saturadas, comportamiento esperable.
2. **¿Las MSR muestran periodicidad con el RAM?** → Sí = las MSR están sincronizadas con el estímulo. No = el estímulo puede ser insuficiente para activarlas.

---

## 4. Panel de Vesículas Sinápticas — Fibras LSR (Dinámica del RRP)

### ¿Qué es?

Es el equivalente del panel HSR pero para las **fibras LSR (Low Spontaneous Rate — tasa espontánea baja, umbral alto)**. Estas fibras tienen la menor tasa espontánea (1 sp/s) y la menor tasa pico (800 sp/s), pero son **las más importantes para entender el habla en entornos ruidosos**.

Muestra las mismas tres variables que el panel HSR (qt, wt y available), reflejando la cinética sináptica particular de las fibras LSR.

### ¿Cómo funciona internamente?

Utiliza el mismo modelo biofísico de dos pools (ver sección 2), con parámetros específicos de las fibras LSR:
- **Tasa espontánea (sp):** 1 sp/s (vs. 68.5 sp/s en HSR, 10 sp/s en MSR)
- **Tasa pico (psr):** 800 sp/s (vs. 3000 sp/s en HSR, 1000 sp/s en MSR)

Las fibras LSR tienen el RRP más lleno en reposo (menor actividad espontánea = menor consumo basal de vesículas), pero son las primeras en verse afectadas ante **sinaptopatía coclear (pérdida auditiva oculta)** y envejecimiento.

### ¿Qué permite analizar?

| Observación | Interpretación |
|---|---|
| qt de LSR se mantiene cercano a 14 durante todo el estímulo | **Comportamiento esperado** — las LSR tienen umbral alto, solo se activan significativamente ante sonidos intensos. |
| qt de LSR no depleta en absoluto ante el estímulo | **Estímulo por debajo del umbral de las LSR** — el nivel del RAM puede ser demasiado bajo para activar fibras de alto umbral. |
| qt de LSR depleta de forma similar a HSR | **Estímulo de alta intensidad o patología** — las LSR están siendo reclutadas tan agresivamente como las HSR, lo que podría indicar un estímulo excesivamente fuerte o un desbalance en la codificación. |
| qt de LSR no se recupera entre pulsos del RAM | **Indicador de fatiga sináptica en LSR** — relevante para explicar dificultades de comprensión en ruido prolongado. |

### ¿En qué contexto de trabajo se usa?

- **Diagnóstico de pérdida auditiva oculta (sinaptopatía):** Las fibras LSR son las primeras en degenerarse ante exposición a ruido o envejecimiento. Un paciente con audiograma normal pero fibras LSR dañadas tendrá dificultad para entender el habla en ruido de fondo. Este panel permite visualizar directamente esa vulnerabilidad.
- **Investigación en codificación en ruido:** Las LSR tienen un amplio rango dinámico y no saturan fácilmente, lo que las hace esenciales para codificar señales de habla embebidas en ruido competitivo.
- **Simulación de pérdida selectiva de fibras LSR:** Configurando `numL=0` (simula la degeneración total o pérdida selectiva de las fibras LSR) en el modelo, se puede observar la desaparición de la dinámica vesicular de las LSR y medir el impacto sobre la respuesta total del nervio auditivo.

### ¿Cómo se interpreta?

El fonoaudiólogo debe comparar este panel con los de HSR y MSR:
1. **¿Las LSR están activas ante el estímulo?** → Si no muestran depleción, el estímulo es demasiado suave para reclutarlas.
2. **¿Las LSR muestran un patrón diferente al de HSR?** → Sí = las diferentes poblaciones están codificando aspectos distintos del sonido. Esto es el comportamiento sano esperado.
3. **¿Las LSR están ausentes (qt constante en 14)?** → Si se simuló una pérdida selectiva de LSR (`numL=0`), este panel lo confirma visualmente.

---

## 5. Panel Integrado de Vesículas — Comparación HSR / MSR / LSR

### ¿Qué es?

Es un gráfico que **superpone las curvas de depleción del RRP (qt) de las tres poblaciones de fibras** (HSR, MSR y LSR) en un solo panel para cada frecuencia seleccionada. Permite una comparación directa e inmediata de cómo cada tipo de fibra responde al mismo estímulo en el mismo instante temporal.

- **HSR (azul, línea continua):** Alta tasa espontánea (68.5 sp/s), umbral bajo.
- **MSR (naranja, línea discontinua):** Tasa espontánea media (10 sp/s), umbral intermedio.
- **LSR (rojo, línea punto-raya):** Baja tasa espontánea (1 sp/s), umbral alto.

### ¿Cómo funciona internamente?

El panel lee las matrices `qt_H`, `qt_M` y `qt_L` del `ModelOutput` (generadas cuando el modelo se ejecuta con `storeflag='d'`) y las grafica simultáneamente usando el mismo eje temporal y la misma escala de vesículas (0–14). Esto es posible porque las tres poblaciones comparten el mismo tamaño de RRP (`M=14`) y pool de reserva (`M2=60`), pero difieren en sus tasas de activación y liberación.

### ¿Qué permite analizar?

| Observación | Interpretación |
|---|---|
| HSR depleta mucho, MSR moderadamente, LSR poco o nada | **Comportamiento normal para estímulos moderados** — las fibras se reclutan proporcionalmente a su sensibilidad. |
| Las tres curvas depletan de forma similar | **Estímulo muy intenso** — todas las fibras están siendo reclutadas al máximo, indicando saturación. |
| HSR y MSR depletan pero LSR permanece en 14 | **El estímulo no alcanza el umbral de las LSR** — normal para niveles bajos/moderados. |
| HSR depleta normalmente pero MSR y/o LSR no depletan (en un escenario con `numM` o `numL` reducidos) | **Sinaptopatía selectiva** — la ausencia de actividad en MSR/LSR es diagnóstica de pérdida sináptica oculta. |
| Las tres curvas se separan más en frecuencias altas que en frecuencias bajas | **Daño frecuencia-específico** — la separación diferencial entre tipos de fibra varía según la región coclear. |

### ¿En qué contexto de trabajo se usa?

- **Diagnóstico diferencial de sinaptopatía:** Este es el gráfico más potente para **visualizar la pérdida auditiva oculta**. El fonoaudiólogo puede ver directamente qué población de fibras está afectada y en qué grado, algo imposible de determinar con un audiograma convencional.
- **Educación fonoaudiológica:** Mostrar visualmente la diferencia entre las tres poblaciones de fibras y cómo la misma señal acústica es procesada de forma diferente por cada una.
- **Investigación en estratificación de fibras:** Estudiar cómo diferentes configuraciones de daño sináptico (pérdida selectiva de LSR vs. pérdida uniforme) producen patrones diferenciables en este panel.

### ¿Cómo se interpreta?

El fonoaudiólogo debe observar:
1. **¿Las tres curvas están presentes?** → Si falta alguna, esa población de fibras no se simuló o tiene `num=0`.
2. **¿Existe una jerarquía clara de depleción (HSR > MSR > LSR)?** → Sí = comportamiento fisiológico normal. No = posible artefacto o estímulo atípico.
3. **¿La separación entre curvas cambia según la frecuencia?** → Comparar el panel a 500 Hz vs. 4000 Hz para detectar patrones frecuencia-específicos.
4. **¿La forma del agotamiento difiere entre fibras?** → HSR debería deplectar más rápido pero también recuperarse más rápido que LSR por su mayor tasa de recarga.

---

## 6. Corrientes Iónicas de la IHC

### ¿Qué es?

Es un gráfico que muestra las **tres corrientes eléctricas** que fluyen a través de la membrana de la célula ciliada interna (IHC) mientras procesa sonido. Estas corrientes son la "maquinaria eléctrica" que convierte la vibración mecánica de la membrana basilar en una señal eléctrica (el potencial de membrana Vm) que luego dispara la liberación de neurotransmisor.

Siendo **Cm** la capacitancia de la membrana de la IHC, **dVm/dt** la derivada temporal del potencial de membrana y **Vm** el potencial resultante, entonces las corrientes **Imet**, **Ikf** e **Iks** representan la corriente de transducción MET (Mecanoeléctrica), la corriente de potasio rápida y la corriente de potasio lenta, respectivamente.
La ecuación
`Cm × dVm/dt = - (Imet + Ikf + Iks)` 
usa la convención de que las corrientes salientes son positivas; por eso una corriente entrante aparece con signo negativo y produce depolarización de Vm.

- **Imet (azul):** Corriente de transducción MET (Mecanoeléctrica). Entra cuando los estereocilios se deflectan → despolariza la IHC. Es la "señal de entrada" de la transducción.
- **Ikf (naranja):** Corriente de K⁺ rápida. Sale de la célula con τ = 0.3 ms → repolariza rápidamente. Permite que la IHC siga modulaciones temporales rápidas.
- **Iks (rojo):** Corriente de K⁺ lenta. Sale de la célula con τ = 8 ms → produce adaptación lenta. Reduce gradualmente la respuesta ante estimulación sostenida.
- **Vm (línea negra):** Potencial de membrana resultante. Es la "salida" de la IHC que controla la liberación vesicular.

### ¿Cómo funciona internamente?

La IHC se modela como un circuito eléctrico:

```
Cm × dVm/dt = -(Imet + Ikf + Iks)
```

- Imet es **despolarizante** (empuja Vm hacia arriba)
- Ikf e Iks son **repolarizantes** (empujan Vm hacia abajo)
- El equilibrio entre las tres determina Vm en cada instante

Se muestra una ventana de 50 ms para poder ver los ciclos individuales de las corrientes.

### ¿Qué permite analizar?

| Observación | Interpretación |
|---|---|
| Imet oscila simétricamente alrededor de cero | **Frecuencia baja** — la IHC sigue cada ciclo del sonido (phase-locking activo). |
| Imet tiene un offset DC positivo (componente constante) | **Frecuencia alta** — la IHC no puede seguir cada ciclo; solo produce una despolarización tónica. Esto es normal por encima de ~3 kHz. |
| Ikf domina sobre Iks | **Buena codificación temporal** — la repolarización rápida permite que la IHC "resetee" rápidamente entre ciclos. |
| Iks crece y domina con el tiempo | **Adaptación excesiva** — la componente lenta reduce la amplitud de Vm. Después de unos milisegundos, la IHC responde menos al mismo estímulo. |
| Vm oscila poco (casi plano) | **Señal débil o pérdida severa** — la vibración de la BM no es suficiente para abrir los canales MET significativamente. |

### ¿En qué contexto de trabajo se usa?

- **Educación avanzada:** Es la visualización más "biofísica" del conjunto. Ideal para cursos de posgrado o seminarios donde se necesita mostrar exactamente cómo funciona la transducción mecano-eléctrica.
- **Investigación sobre canalopatías:** Hipotéticamente, alteraciones en los canales de K⁺ (por ejemplo, mutaciones que afecten KCNQ4) cambiarían la relación Ikf/Iks. Esta visualización permitiría modelar ese escenario. Es importante aclarar que la hipótesis sería conceptual ya que no se cuenta con una simulación genética literal.
- **Comprensión de la codificación temporal:** Para explicar por qué la IHC puede codificar temporalmente sonidos de baja frecuencia (el Vm oscila ciclo a ciclo) pero no de alta frecuencia (solo genera un DC).

### ¿Cómo se interpreta?

El fonoaudiólogo debe observar:
1. **¿Imet tiene modulación visible?** → Sí = la BM está vibrando en esa sección = el sonido llega a esa frecuencia.
2. **¿El Vm oscila o es plano?** → Oscilación = codificación temporal activa. Plano = solo codificación de tasa (rate coding).
3. **¿Iks crece con el tiempo?** → Es normal que crezca (adaptación). Si crece demasiado, la IHC pierde rango dinámico temporal.

---

## 7. Balance Excitación/Inhibición del Tronco Encefálico

### ¿Qué es?

Son dos paneles que muestran las **componentes excitatoria e inhibitoria** de la respuesta neural en las dos estaciones principales del tronco encefálico auditivo:
- **Núcleo Coclear (CN):** Primera estación de relevo post-nervio auditivo. Genera la **Onda III** del ABR.
- **Colículo Inferior (IC):** Estación de integración superior. Genera la **Onda V** del ABR, el pico más importante clínicamente.

Cada panel muestra:
- **Área verde:** Componente excitatoria (señal directa del AN -gráfica Núcleo Coclear- o CN -gráfica Colículo Inferior-).
- **Área roja (invertida):** Componente inhibitoria (señal retardada y filtrada que frena la excitación).
- **Línea negra:** Resultado neto (excitación − inhibición), que es lo que realmente genera las ondas del ABR.

### ¿Cómo funciona internamente?

Ambos núcleos implementan un modelo de excitación-inhibición con retardo:

```
Respuesta = Ganancia × [Excitación(señal) − Peso_inh × Inhibición(señal_retardada)]
```
Según los valores actuales del modelo de Verhulst:

| Parámetro | CN | IC |
|---|---|---|
| Ganancia excitatoria | 1.5 | 1.0 |
| Peso inhibitorio | 0.6 | **1.5** |
| Retardo de inhibición | 1 ms | **2 ms** |

La inhibición del IC es 2.5× más fuerte que la del CN, lo que explica por qué la Onda V es tan "afilada" y bien definida clínicamente.

### ¿Qué permite analizar?

| Observación | Interpretación |
|---|---|
| Excitación domina ampliamente sobre inhibición en CN | **CN responde fuertemente** — hay suficiente actividad del nervio auditivo. |
| Inhibición en IC casi cancela la excitación | **IC filtra agresivamente** — comportamiento normal. La Onda V es un pico estrecho porque la inhibición "recorta" la excitación. |
| Excitación reducida en CN con inhibición normal | **Reducción de input del nervio auditivo** — consistente con pérdida periférica (OHC o sináptica). |
| Excitación e inhibición reducidas proporcionalmente | **Atenuación general** — toda la cadena recibe menos señal. |
| Inhibición más fuerte que excitación (neto negativo) | **Artefacto o patología severa** — en un oído funcional esto no debería ocurrir sostenidamente. |

### ¿En qué contexto de trabajo se usa?

- **Investigación en procesamiento auditivo central:** Para estudiar cómo el balance exc/inh del tronco encefálico cambia con distintos tipos de pérdida periférica.
- **Estudio de hiperacusia:** Si se reduce la inhibición (hipotéticamente bajando Scn o Sic), la excitación neta aumenta, modelando una posible base neural de la hipersensibilidad al sonido.
- **Interpretación de ondas ABR:** Para entender por qué la Onda V tiene la latencia y forma que tiene, y qué pasa cuando las ondas se alteran en un ABR clínico.

### ¿Cómo se interpreta?

El fonoaudiólogo debe observar:
1. **¿La excitación es periódica?** → Sí = el tronco sigue la modulación del estímulo RAM. No = la codificación temporal se perdió en etapas anteriores.
2. **¿La inhibición sigue a la excitación con retardo visible?** → 1 ms en CN, 2 ms en IC. Si el retardo parece mayor, hay un problema en el modelo, no en la biología.
3. **¿El neto (línea negra) tiene picos claros?** → Picos claros = ondas ABR bien definidas. Picos borrosos = las ondas serán pequeñas o difusas.
4. **¿Cómo difiere CN vs. IC?** → El IC debe ser más "recortado" que el CN. Si ambos se ven iguales, los parámetros de inhibición del IC pueden necesitar revisión.

---

# PARTE 2: Requerimientos por Caso de Uso para la Plataforma Web

---

## Caso de Uso 1: Comparador de Perfiles Auditivos

### Descripción
El fonoaudiólogo selecciona dos perfiles auditivos (por ejemplo, "Flat00" vs. "Slope25") y la plataforma ejecuta ambas simulaciones y muestra las 7 visualizaciones lado a lado para comparación directa.

### Requerimientos

#### Backend
- **REQ-1.1:** Endpoint `POST /api/simulation/compare` que reciba dos perfiles auditivos y ejecute ambas simulaciones con `storeflag='evihmlbwd'`.
- **REQ-1.2:** Procesamiento asíncrono con cola de tareas (Celery o similar), ya que cada simulación puede tardar varios minutos.
- **REQ-1.3:** Endpoint `GET /api/simulation/{task_id}/status` para consultar el progreso de la simulación.
- **REQ-1.4:** Almacenamiento temporal de los `ModelOutput` en disco (pickle o HDF5) para evitar re-simulaciones.
- **REQ-1.5:** Endpoint `GET /api/simulation/{task_id}/data/{variable}` que retorne los datos de una variable específica (sheraPt, qt_H, qt_M, qt_L, etc.) en formato JSON o binario (msgpack/protobuf) para graficación en el frontend.
- **REQ-1.6:** Decimación server-side de los datos de alta resolución temporal (100 kHz → puntos graficables) para enviar al frontend sin saturar el ancho de banda.

#### Frontend
- **REQ-1.7:** Selector de perfiles auditivos con los 33 perfiles precomputados disponibles, agrupados por tipo (Flat, Slope, Flat+Slope, Normal).
- **REQ-1.8:** Layout de comparación lado a lado (split-view) con scroll sincronizado y zoom sincronizado entre ambas visualizaciones.
- **REQ-1.9:** Indicador de progreso de la simulación con estimación de tiempo restante.
- **REQ-1.10:** Renderizado de las 7 visualizaciones usando una librería de gráficos interactiva (Plotly.js o Chart.js) que permita zoom, pan, y tooltips con valores exactos.
- **REQ-1.11:** Toggle para mostrar/ocultar cada visualización individualmente.
- **REQ-1.12:** Anotaciones textuales automáticas sobre las gráficas indicando diferencias clave entre los dos perfiles (por ejemplo, "Pérdida de ganancia en región 2-8 kHz"). - ¿es posible hacerlo con Python sin modelos de lenguaje? ¿futura implementación con modelos de lenguaje? Se debe priorizar la calidad funcional para fonoaudiología.. si es necesario entonces en una segunda etapa se implementa con modelos de lenguaje -

---

## Caso de Uso 2: Detector de Sordera Oculta (Sinaptopatía Coclear)

### Descripción
El fonoaudiólogo ingresa un perfil con audiograma normal (Flat00) pero modifica el número de fibras del nervio auditivo (nH, nM, nL) para simular pérdida sináptica selectiva. La plataforma muestra cómo esta pérdida invisible en el audiograma se manifiesta en las variables internas del modelo.

### Requerimientos

#### Backend
- **REQ-2.1:** Endpoint `POST /api/simulation/synaptopathy` que reciba perfil auditivo + configuración de fibras (nH, nM, nL) personalizados.
- **REQ-2.2:** Ejecución de al menos 2 simulaciones simultáneas: una "sana" (13/3/3) y una "patológica" (con fibras reducidas) para comparación directa.
- **REQ-2.3:** Cálculo automático del EFR (suma de armónicos a 110 Hz) para ambas simulaciones.
- **REQ-2.4:** Cálculo de métricas de diferencia: porcentaje de reducción de EFR, profundidad de agotamiento de qt, y tasa de recuperación vesicular.

#### Frontend
- **REQ-2.5:** Controles deslizantes (sliders) para nH (0–13), nM (0–3), nL (0–3) con indicadores visuales del porcentaje de pérdida.
- **REQ-2.6:** Presets predefinidos de escenarios clínicos comunes:
  - "Sinaptopatía leve" (10/2/2)
  - "Sinaptopatía moderada" (7/1/1)
  - "Sinaptopatía severa" (4/0/0)
  - "Pérdida selectiva LSR" (13/3/0) — modela dificultad en ruido sin pérdida de sensibilidad.
- **REQ-2.7:** Paneles de vesículas individuales (visualizaciones 2, 3 y 4) y panel comparativo integrado (visualización 5) como gráficas principales, con indicadores numéricos de:
  - Profundidad de agotamiento de qt por tipo de fibra (HSR, MSR, LSR: mínimo alcanzado)
  - Tiempo de recuperación de qt al 80% de su valor basal para cada tipo de fibra
  - Valor de EFR resultante en µV
- **REQ-2.8:** Semáforo visual (verde/amarillo/rojo) basado en la reducción de EFR respecto al caso sano:
  - Verde: reducción < 10% → "Sin indicadores de sinaptopatía"
  - Amarillo: reducción 10-30% → "Posible sinaptopatía leve"
  - Rojo: reducción > 30% → "Indicadores compatibles con sinaptopatía significativa"
- **REQ-2.9:** Selector de tipo de fibra (HSR/MSR/LSR/Combinado) para los paneles de vesículas, permitiendo al fonoaudiólogo alternar entre vistas individuales y el panel comparativo integrado.
- **REQ-2.10:** Indicadores numéricos en el panel combinado (visualización 5) que muestren la diferencia de depleción entre fibras: Δqt(HSR-MSR), Δqt(HSR-LSR), como porcentaje de la capacidad total del RRP.

> [!WARNING]
> El semáforo es orientativo para investigación, no tiene valor diagnóstico clínico directo. Debe incluir una nota aclaratoria visible.

---

## Caso de Uso 3: Explorador de Parámetros del Estímulo

### Descripción
El investigador o fonoaudiólogo explora cómo diferentes estímulos (frecuencia portadora, frecuencia de modulación, nivel en dB SPL, tipo de modulación) afectan las respuestas internas del modelo. Esto permite diseñar protocolos de medición de EFR óptimos.

### Requerimientos

#### Backend
- **REQ-3.1:** Endpoint `POST /api/simulation/explore` que reciba parámetros del estímulo (carrier_freq, fMod, level_dB, mod_type) además del perfil auditivo.
- **REQ-3.2:** Soporte para batches: ejecutar una grilla de simulaciones (por ejemplo, fMod = [40, 80, 110, 150, 200] Hz × level = [50, 60, 70, 80] dB SPL) como una sola tarea.
- **REQ-3.3:** Almacenamiento de resultados del batch en una estructura que permita consultar resultados individuales sin re-simular.
- **REQ-3.4:** Endpoint `GET /api/simulation/batch/{batch_id}/summary` que retorne una tabla resumen con el EFR y métricas clave de cada combinación de parámetros.

#### Frontend
- **REQ-3.5:** Formulario de configuración con:
  - Selector de frecuencia portadora: 500, 1000, 2000, 4000, 8000 Hz
  - Selector de frecuencia de modulación: rango libre 20–300 Hz con presets en 40, 80, 110 Hz
  - Selector de nivel: rango 30–90 dB SPL con step de 10 dB
  - Selector de perfil auditivo
- **REQ-3.6:** Tabla de resultados del batch con celdas coloreadas (heatmap tabular) donde el color indica la magnitud del EFR.
- **REQ-3.7:** Clic en una celda de la tabla para ver las 4 visualizaciones detalladas de esa combinación específica de parámetros.
- **REQ-3.8:** Gráfico de líneas "EFR vs. frecuencia de modulación" y "EFR vs. nivel" generados automáticamente a partir del batch.

---

## Caso de Uso 4: Herramienta Docente Interactiva

### Descripción
Un docente de fonoaudiología utiliza la plataforma en clase para mostrar paso a paso cómo el sonido se procesa desde el canal auditivo hasta el tronco encefálico, con las visualizaciones internas como material didáctico interactivo.

### Requerimientos

#### Backend
- **REQ-4.1:** Cache de simulaciones pre-calculadas para los escenarios docentes más comunes (oído sano a 70 dB, pérdida plana 30 dB, sinaptopatía moderada) para evitar esperas en clase.
- **REQ-4.2:** Endpoint `GET /api/presets/teaching` que liste los escenarios pre-calculados disponibles.

#### Frontend
- **REQ-4.3:** Modo "Presentación" con visualizaciones a pantalla completa, tipografía grande, y navegación simplificada (flechas o botones de "Siguiente etapa").
- **REQ-4.4:** Flujo guiado que presente las visualizaciones en orden del pipeline biológico:
  1. Estímulo de entrada (forma de onda RAM)
  2. Mapa de calor coclear (cómo la cóclea amplifica/comprime)
  3. Corrientes de la IHC (cómo se transforma en señal eléctrica)
  4. Panel de vesículas HSR (cómo la sinapsis transmite al nervio — fibras más sensibles)
  5. Panel de vesículas MSR (fibras de sensibilidad media)
  6. Panel de vesículas LSR (fibras de umbral alto — esenciales para comprensión en ruido)
  7. Panel integrado HSR/MSR/LSR (comparación directa de la depleción diferencial)
  8. Balance exc/inh (cómo el tronco encefálico integra)
  9. EFR resultante (lo que mediríamos en la clínica)
- **REQ-4.5:** Anotaciones didácticas en cada visualización:
  - Flechas señalando los elementos clave
  - Texto explicativo contextual con lenguaje adecuado para estudiantes
  - Opción de mostrar/ocultar las anotaciones
- **REQ-4.6:** Botón "Comparar con patología" que superpone o coloca lado a lado la misma visualización para un oído sano y uno patológico.
- **REQ-4.7:** Glosario interactivo: al hacer hover sobre términos técnicos (OHC, RRP, phase-locking, etc.) se muestra una definición breve.

---

## Caso de Uso 5: Generador de Reportes de Simulación

### Descripción
Tras ejecutar una simulación, el fonoaudiólogo genera un reporte en PDF o HTML que documenta los parámetros usados, las 7 visualizaciones, las métricas calculadas, y una interpretación automática de los resultados.

### Requerimientos

#### Backend
- **REQ-5.1:** Endpoint `GET /api/simulation/{task_id}/report` que genere un reporte en formato PDF (usando WeasyPrint o ReportLab) o HTML.
- **REQ-5.2:** El reporte debe incluir:
  - Encabezado con fecha, parámetros de la simulación (perfil, estímulo, fibras)
  - Las 7 visualizaciones como imágenes de alta resolución (300 dpi)
  - Tabla de métricas: EFR (µV), amplitudes de W1/W3/W5, profundidad de agotamiento de qt por tipo de fibra (HSR, MSR, LSR), tiempo de recuperación por tipo de fibra
  - Interpretación automática basada en reglas (por ejemplo: "El agotamiento de qt en fibras HSR a 4 kHz es del 78% mientras que las LSR mantienen el 95% de su capacidad, consistente con un reclutamiento diferencial normal" o "Las fibras LSR no muestran actividad, consistente con sinaptopatía selectiva de fibras de bajo umbral")
- **REQ-5.3:** Generación de imágenes server-side usando matplotlib con el módulo `diagnostic_plots.py` ya implementado (sin necesidad de un navegador).

#### Frontend
- **REQ-5.4:** Botón "Generar Reporte" visible después de completar una simulación.
- **REQ-5.5:** Vista previa del reporte en el navegador antes de descargar.
- **REQ-5.6:** Opción de agregar notas manuales del fonoaudiólogo al reporte antes de la generación final.

---

## Caso de Uso 6: Monitoreo de Progresión Temporal

### Descripción
El investigador ejecuta múltiples simulaciones con perfiles que representan una progresión temporal de pérdida auditiva (por ejemplo, Flat00 → Flat10 → Flat20 → Flat30) para visualizar cómo las variables internas se degradan progresivamente.

### Requerimientos

#### Backend
- **REQ-6.1:** Endpoint `POST /api/simulation/progression` que reciba una lista ordenada de perfiles auditivos.
- **REQ-6.2:** Ejecución secuencial o paralela de todas las simulaciones con los mismos parámetros de estímulo.
- **REQ-6.3:** Cálculo de métricas de tendencia: pendiente de degradación del EFR, punto de inflexión (nivel de pérdida donde el EFR cae más rápido).

#### Frontend
- **REQ-6.4:** Vista de "timeline" que muestra la progresión horizontal de izquierda (sano) a derecha (más pérdida).
- **REQ-6.5:** Para cada punto de la progresión, miniatura clickeable de cada visualización.
- **REQ-6.6:** Gráfico de tendencia superpuesto: EFR vs. grado de pérdida, con marcadores en cada perfil simulado.
- **REQ-6.7:** Animación opcional que transiciona suavemente entre los mapas de calor cocleares de cada perfil, mostrando cómo el "rojo" se expande progresivamente.

---

## Resumen de Endpoints API

| Endpoint | Método | Caso de Uso | Descripción |
|---|---|---|---|
| `/api/simulation/compare` | POST | CU-1 | Comparar dos perfiles auditivos |
| `/api/simulation/synaptopathy` | POST | CU-2 | Simular sordera oculta |
| `/api/simulation/explore` | POST | CU-3 | Explorar parámetros del estímulo |
| `/api/simulation/batch/{id}/summary` | GET | CU-3 | Resumen de batch de simulaciones |
| `/api/presets/teaching` | GET | CU-4 | Listar presets docentes |
| `/api/simulation/{id}/status` | GET | Todos | Estado de una simulación |
| `/api/simulation/{id}/data/{variable}` | GET | Todos | Datos de una variable específica (qt_H, qt_M, qt_L, sheraPt, etc.) |
| `/api/simulation/{id}/report` | GET | CU-5 | Generar reporte PDF/HTML con las 7 visualizaciones |
| `/api/simulation/progression` | POST | CU-6 | Simular progresión temporal |
| `/api/profiles` | GET | Todos | Listar perfiles auditivos disponibles |

---

## Resumen de Requerimientos por Prioridad

### Prioridad Alta (MVP)
- REQ-1.1, REQ-1.2, REQ-1.3, REQ-1.5 — Ejecución y consulta de simulaciones
- REQ-1.7, REQ-1.10, REQ-1.11 — Selector de perfiles y renderizado de las 7 visualizaciones
- REQ-2.1, REQ-2.5, REQ-2.6, REQ-2.7 — Simulación de sinaptopatía con paneles HSR/MSR/LSR y combinado
- REQ-2.9 — Selector de tipo de fibra para paneles de vesículas
- REQ-1.6 — Decimación de datos para rendimiento

### Prioridad Media (v1.1)
- REQ-1.8, REQ-1.12 — Comparación lado a lado con anotaciones
- REQ-2.8 — Semáforo de sinaptopatía
- REQ-2.10 — Indicadores de depleción diferencial entre fibras en panel combinado
- REQ-3.1, REQ-3.5, REQ-3.6 — Exploración de parámetros
- REQ-5.1, REQ-5.2, REQ-5.4 — Generación de reportes con las 7 visualizaciones

### Prioridad Baja (v2.0)
- REQ-3.2, REQ-3.3, REQ-3.4 — Batches de simulaciones
- REQ-4.1 a REQ-4.7 — Modo docente completo
- REQ-6.1 a REQ-6.7 — Monitoreo de progresión temporal
