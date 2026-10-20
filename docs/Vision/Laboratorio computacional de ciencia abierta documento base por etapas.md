# Laboratorio computacional de ciencia abierta: documento base por etapas

Oct 14, 2026 · @Facundo Ramírez

## Resumen y visión

El proyecto es un laboratorio computacional abierto de biología y medicina humana. Su objetivo de largo plazo es comprender la función y la enfermedad y simular formas de intervenir: sustituir funciones con prótesis, reparar y regenerar tejidos, guiar su morfología y preservar la salud con la edad. Cada estudio termina como artículo interactivo y como video de divulgación, y reúne investigación, educación y divulgación en un solo flujo.

La audición es el caso piloto que valida la plataforma, no su límite. El laboratorio empieza en audiología con el Auditory Modeling Toolbox (AMT) porque la audición reúne esas cinco vías en un sistema acotado: modelos funcionales maduros, prótesis de uso masivo, la regeneración de células ciliadas como pregunta abierta, las malformaciones congénitas del oído y la pérdida auditiva asociada a la edad. A partir de ahí se abre por etapas: primero a otros simuladores auditivos, luego a simuladores de propósito general que cubren la biología humana de la molécula al órgano y, como horizonte, a modelos animales in silico y al estudio del envejecimiento. Cada ampliación se habilita solo cuando la anterior demuestra su valor.

El eje es el **estudio estructurado**: un único objeto digital con hipótesis, modelo, parámetros, resultados y afirmaciones enlazadas a su evidencia. De él se derivan el artículo, las capas de lectura, el guion del video y el portafolio de aprendizaje.

| Pilar | Qué aporta |
| --- | --- |
| Punto de partida y horizonte | Audiología con AMT como caso piloto; luego toda la audición, la biología humana en varias escalas y, como horizonte de la visión, biología comparada, modelos animales in silico y longevidad |
| Objetivos | Cinco vías en igualdad: comprender la función y la enfermedad, sustituir funciones con prótesis, reparar y regenerar tejidos, guiar la morfología de tejidos y órganos, y preservar la salud con la edad (longevidad) |
| Ecosistema de simulación | Modelos modulares en varias escalas, de la molécula al órgano: AMT (MATLAB/Octave, código abierto) al inicio, luego otros simuladores auditivos y de propósito general, en contenedores propios o en servicios externos con API; escalable a cómputo de alto rendimiento (HPC) o nube |
| Estudio estructurado y repositorio | Artículos interactivos, reproducibles y legibles por IA, con revisión abierta |
| Agente de IA | Mentor pedagógico y copiloto de investigación en un solo agente |
| Divulgación asistida por IA | Videos de calidad profesional con producción simplificada |
| Educación | Trabajos prácticos, proyectos guiados y cursos sobre estudios reales, con portafolio verificable, insignias abiertas y, más adelante, certificación |
| Comunidad y servicios | Coautoría, asesoría de edición, clases y, más adelante, mercado de proyectos |

La construcción se organiza en cuatro etapas (validar, MVP, crecer y consolidar), detalladas en la hoja de ruta, donde se indica qué horizonte temático cubre cada una.

## Principios de diseño

Siete principios protegen la credibilidad científica y mantienen acotado el alcance en todas las etapas.

1. **Laboratorio computacional.** Una simulación no reemplaza al experimento: genera hipótesis contrastables y las explora a bajo costo.
2. **Estado de validación visible en cada modelo.** Ningún resultado se muestra sin indicar qué tan respaldado está el modelo que lo produjo.
3. **Integrar antes que construir.** Se reutilizan estándares, modelos y servicios existentes: AMT en las primeras etapas; luego estándares como SBML, COMBINE/OMEX y NeuroML, motores como COPASI, PhysiCell o CompuCell3D, y servicios de simulación con API, en lugar de desarrollarlos desde cero.
4. **Formatos abiertos, servicios de pago.** El formato de estudio y de modelos es abierto; el negocio está en la infraestructura y los servicios.
5. **Trazabilidad humano-IA.** Se registra qué aportó la IA y qué el autor, se atribuyen roles de coautoría (taxonomía CRediT) y el contenido sintético se etiqueta.
6. **Fin biomédico con cinco vías en igualdad.** Las simulaciones tienen fines biológicos y médicos: comprender la función y la enfermedad, sustituir funciones con prótesis, reparar y regenerar tejidos, guiar la morfología y preservar la salud con la edad. Regenerar restaura una forma perdida; guiar la morfología la corrige o la diseña, como en las malformaciones. Ninguna vía es requisito de cada estudio: el caso se elige por la pregunta. Por su fin médico, las simulaciones se apoyan siempre en modelos con estado de validación visible.
7. **Plataforma agnóstica de dominio.** El estudio estructurado, el artículo, el video, el agente, la capa de trabajos y el uso docente no dependen de la audición. Sumar un área de la biología o la medicina humana es sumar modelos y casos, no rehacer la plataforma; la audición es el caso piloto.

| Estado de validación | Significado | Uso permitido |
| --- | --- | --- |
| Validado con datos | Resultados contrastados con datos experimentales publicados | Investigación, docencia y divulgación |
| Verificado | El código implementa correctamente el modelo matemático, sin contraste experimental | Investigación exploratoria y docencia, con aviso |
| Exploratorio | Sin verificación ni contraste con datos | Solo exploración y formación, con aviso destacado |

AMT ofrece una base para el estado *Verificado*: sus experimentos buscan reproducir los resultados de las publicaciones originales. El contraste con datos experimentales (*Validado con datos*) depende de cada modelo y se revisa caso por caso.

## Estudio estructurado y artículo moderno

El artículo deja de ser un PDF estático y pasa a ser una capa de datos estructurados más una capa de lectura interactiva, ambas generadas desde el mismo estudio.

| Característica | Cómo se concreta | Etapa |
| --- | --- | --- |
| Legible por IA | Capa de datos junto al texto: hipótesis, métodos, parámetros, resultados y afirmaciones enlazadas a su evidencia (JSON-LD, RO-Crate, principios FAIR) | 1 (esquema mínimo), 2 (completo) |
| Reproducible | Cada figura guarda modelo, versión, semilla y parámetros, con botón "reproducir" que ejecuta la simulación en la plataforma | 1 (versión reducida), 2 (completa bajo demanda) |
| Interactivo | Controles deslizantes sobre resultados precalculados y en caché; lo no calculado se ejecuta en cola, porque algunos modelos tardan segundos por estímulo | 1 |
| Complejidad ajustable | Niveles de lectura generados por IA y validados por el autor, con glosario contextual | 1 (divulgación y técnico), 2 (nivel intermedio) |
| Confiable | Versionado, DOI, procedencia (qué hizo la IA y qué el humano) y revisión abierta | 1 (versionado y DOI), 2 (revisión abierta) |
| Interoperable | Formato de estudio publicado como estándar abierto, compatible con otros repositorios | 3 |

Dos riesgos condicionan el diseño. La simplificación por IA puede distorsionar resultados, por lo que cada nivel de lectura exige validación del autor y enlaces al texto técnico. Y reproducir experimentos pesados cuesta cómputo, por lo que se cachean resultados y se ejecuta bajo demanda. Como antecedentes de referencia están Distill, los *Executable Research Articles* de eLife y Jupyter Book.

En las primeras etapas la reproducción ejecuta modelos de AMT, escrito para MATLAB y Octave. Ejecutarlos en Octave evitaría depender de licencias de MATLAB, algo que debe comprobarse modelo por modelo. En audición, el artículo interactivo puede incluir además ejemplos sonoros y visualizaciones de la respuesta del modelo.

## Divulgación con video asistido por IA

El video se genera desde el estudio estructurado: la IA asume lo repetitivo y el autor conserva el criterio científico y la voz narrativa. El objetivo es un balance entre calidad de divulgador profesional y producción simple.

1. Estudio estructurado como fuente.
2. Guion con gancho y narrativa.
3. Storyboard.
4. Visuales: las propias simulaciones como material nativo y riguroso; la IA generativa de imágenes solo para ambientación, nunca para mostrar datos.
5. Voz.
6. Edición automática y subtítulos.
7. Exportación multiformato: corto vertical para redes y versión larga.

| Nivel | Qué ocurre | Quién interviene | Etapa |
| --- | --- | --- | --- |
| Automático | Clip de 60 a 90 s generado desde el estudio | Solo el autor revisa y aprueba | 1 |
| Semi-asistido | El usuario ajusta guion, escenas y ritmo | Autor con apoyo de la IA | 2 |
| Premium | Edición profesional sobre el material generado | Editor humano (asesoría de edición) | 2 |

Todo contenido sintético se etiqueta como tal, y los videos pueden exportarse a las redes sociales de preferencia del autor.

## Agente de IA y colaboración

Un solo agente con dos modos reemplaza al "mentor" y al "agente colaborativo" del borrador original, cuyas funciones se solapaban.

| Modo | Función | Límites |
| --- | --- | --- |
| Mentor socrático | Guía el aprendizaje basado en intereses y proyectos; pregunta antes de responder | No entrega conclusiones hechas; adapta el nivel al usuario |
| Copiloto de investigación | Acompaña desde la hipótesis hasta el diseño experimental, el análisis y la redacción | Trabaja sobre modelos con estado de validación visible y registra cada aporte |

La colaboración (mensajería y videoconferencia) se resuelve integrando herramientas existentes, porque construirla no genera diferencial. El diferencial es la **coautoría sobre el estudio estructurado**, con atribución clara de roles y proyectos compartidos entre equipos distribuidos.

## Uso docente

El laboratorio se usa para enseñar con estudios reales: el docente arma actividades sobre estudios publicados en la plataforma y el estudiante formula hipótesis, simula, interpreta y publica. Sirve para cualquier área de la biología y la medicina humana; en las primeras etapas, con modelos de audición.

| Aspecto | Definición |
| --- | --- |
| Destinatarios | Estudiantes de grado (fonoaudiología, biología, medicina, bioingeniería), docentes y profesionales en formación continua |
| Formatos | Trabajo práctico sobre un estudio existente, proyecto guiado por el mentor y curso armado con varios estudios |
| Rol del docente | Arma la actividad, fija los parámetros disponibles y el nivel de lectura, sigue el progreso y evalúa |
| Rol del estudiante | Formula una hipótesis, simula, interpreta los resultados y publica su estudio |
| Rol del agente | Modo mentor socrático: pregunta antes de responder, no entrega conclusiones hechas y registra cada aporte |
| Modelos admitidos | Rige la tabla de estados de validación: Validado con datos sin restricción, Verificado con aviso y Exploratorio solo para formación, con aviso destacado |
| Evaluación y acreditación | Portafolio verificable, luego insignias abiertas y luego certificación avalada por universidades |
| Integración | Con el campus virtual de cada institución, por ejemplo Moodle mediante el estándar LTI (propuesta a validar) |

**Qué se hace en cada etapa:**

| Etapa | Uso docente |
| --- | --- |
| 0 · Validar | Entrevistas a docentes sobre qué enseñarían con simulaciones y cómo lo evaluarían |
| 1 · MVP | Piloto con una cátedra: trabajos prácticos sobre modelos de AMT y portafolio básico |
| 2 · Crecer | Insignias abiertas, nivel de lectura intermedio e integración con el campus virtual |
| 3 · Consolidar | Cursos de otras áreas, certificación formal y mercado de clases |

## Catálogo de simulación por disciplina auditiva

Los simuladores abiertos cubren bien la periferia auditiva, la audición binaural y la inteligibilidad del habla, pero ocho de las catorce disciplinas relevadas no tienen un simulador abierto reutilizable, y no se verificó ningún trabajo que conecte un modelo de regeneración con un modelo funcional de audición. La agrupación por disciplina es clasificación propia de la investigación, no de una fuente; el informe completo con enlaces y lo no verificado se entregó aparte (Simuladores para disciplinas de audición).

Las prioridades técnicas que surgen de esta investigación están integradas en la hoja de ruta, dentro del alcance de cada etapa.

| Disciplina o problema | Herramientas o repositorios abiertos | Licencia | Brecha |
| --- | --- | --- | --- |
| Presbiacusia y daño periférico (células ciliadas) | `zilany2014` y `bruce2018` (AMT), PyZBC2014, Verhulst 2018 | AMT GPLv3 (por modelo, sin verificar); PyZBC2014 AGPLv3; Verhulst: solo académica | Sin parámetro de potencial endococlear |
| Ruido y sinaptopatía | Variación del número de fibras en Verhulst y `lossL/M/H` en `bruce2018` | Como la fila anterior | Sin simulador específico de pérdida por ruido |
| Ototoxicidad | Solo Cochlear Fluids Simulator (WashU, farmacocinético) | No indicada | Sin simulador funcional abierto |
| Malformaciones congénitas de oído externo y medio | OpenEar (geometría de huesos temporales sanos) | CC BY 4.0 | Sin datos ni código de atresia o microtia |
| Otología conductiva adquirida (otosclerosis, perforación, otitis) | Artículos de elementos finitos; cadena Gmsh + Code\_Aster sin modelo listo | No declarada | Sin geometría, malla ni código compartido verificado |
| Oído externo y HRTF | Mesh2HRTF/NumCalc, bases SOFA, pyfar, sofar | pyfar y sofar MIT; Mesh2HRTF sin verificar | Sin librería abierta de absorbancia de banda ancha |
| Implantes cocleares | PHAST/phastc, NeuroVoc, `felsheim2024` y `kelvasa2015` (AMT) | MIT; AMT GPLv3 | Sin modelo abierto de conducción de volumen |
| Audífonos y rehabilitación | openMHA, Tympan, pyclarity, pystoi | openMHA AGPL-3.0; resto MIT | Sin software abierto de rehabilitación |
| Audición central, binaural y habla en ruido | AMT, torch\_amt, Brian2, modelo de tronco encefálico (ModelDB 246535) | GPLv3 y CeCILL; ModelDB sin declarar | Sin modelo auditivo en NEST ni de corteza hallado |
| Acúfenos, hiperacusia y trastornos del procesamiento | macsbio (MATLAB), Dotan y Shriki 2021 | Sin licencia declarada | Sin modelo de trastornos del procesamiento; hiperacusia sin búsqueda dedicada |
| Genética de la sordera hereditaria | gEAR, DVD, SHIELD (solo datos) | gEAR AGPL-3.0; DVD y SHIELD restrictivas | No hay simulador |
| Regeneración y desarrollo coclear | Cohen 2020 (vértices 2D, código en Zenodo); modelos Notch solo en artículos | Sin verificar | Sin simulador abierto y mantenido |
| Vestibular | Solo artículos de simulación de maniobras | No aplica | Ningún paquete abierto verificado |
| Audiología pediátrica y cribado neonatal | Marco JCIH 2019 y un dataset de absorbancia en recién nacidos (sin verificar) | No aplica | Sin simulador verificado |

### Licencias que condicionan la plataforma

El modelo con más parámetros de daño periférico, Verhulst 2018, y sus aproximaciones CoNNear están bajo la UGent Academic License: solo investigación académica no comercial, con una licencia comercial exclusiva reservada a la universidad sobre las obras derivadas. Dentro de AMT, `verhulst2018` conserva esa licencia aunque el resto sea GPLv3, y la función `amt_info` informa la licencia de cada modelo.

| Familia de licencia | Herramientas | Implicación |
| --- | --- | --- |
| Académica no comercial (UGent) | Verhulst 2015 y 2018, CoNNear | Inutilizable en un servicio comercial sin acuerdo escrito |
| GPL | AMT (mayoría), torch\_amt, cochlea | Obligaciones al redistribuir; su alcance para un servicio solo accesible por red no está verificado |
| AGPL | PyZBC2014, openMHA, gEAR | Quien ofrece una versión modificada por red debe ofrecer su código |
| Sin licencia declarada | ZBC y BEZ2018a originales, macsbio, Cohen 2020, CompHEAR, la mayoría de las bases HRTF | Pedir permiso por escrito antes de reutilizar |
| Permisiva (MIT y CC BY) | phastc, NeuroVoc, pyclarity, pystoi, pyfar, sofar, OpenEar | Sin restricción comercial más allá de la atribución |

Se propone aislar los componentes GPL y AGPL en contenedores detrás de una API y mantener el código propio con licencia permisiva; la compatibilidad jurídica concreta requiere asesoría legal.

### El puente entre regeneración y audición funcional

Los modelos funcionales ya aceptan un "estado coclear": Verhulst 2018 permite variar el número de fibras de baja, media y alta tasa espontánea (por defecto 3, 3 y 13) y `bruce2018` ofrece `lossL/M/H` y ajuste a audiograma. Del lado biológico, lo único con código depositado es Cohen 2020, un modelo de vértices 2D del órgano de Corti cuya conclusión es que la mecánica, y no la señalización Notch, ordena el patrón. Falta el módulo que genere ese estado.

El puente mínimo es una **propuesta de diseño, no una práctica publicada**: un vector por frecuencia de células ciliadas vivas y proporción de sinapsis, producido por un módulo biológico y traducido a parámetros del modelo periférico. Como caso para parametrizar escenarios de recuperación sirve la terapia génica AAV1-hOTOF, en la que 5 de 6 niños sordos recuperaron audición en un ensayo de un solo brazo (The Lancet, 2024).

### Lo que no se verificó

AMT en Octave no se probó y su compatibilidad es por modelo. Las licencias individuales de `zilany2014`, `bruce2018` y otros modelos de AMT no se confirmaron. La versión vigente de AMT figura como 1.6.0 (2024) en la web oficial y como 1.3.0 en la página del instituto, y el número de modelos oscila entre "más de 50" y "más de 60". El estado de mantenimiento se infirió de PyPI porque GitHub no estuvo accesible, y cada "no encontrado" significa "no encontrado en estas búsquedas", no "inexistente".

## Horizontes, escalas y simuladores como servicio

El laboratorio crece en cuatro horizontes temáticos y seis escalas de simulación. H1 a H3 tienen etapa en la hoja de ruta; H4 queda como horizonte de la visión hasta validar la Etapa 3. Las simulaciones corren en contenedores propios o en servicios externos con API.

### Horizontes temáticos

| Horizonte | Alcance | Simuladores típicos | Etapa |
| --- | --- | --- | --- |
| H1 · Audición con AMT | Periferia del oído, habla y localización | AMT en Octave; paquetes Python con licencia MIT | 0 y 1 |
| H2 · Audición completa | Las catorce disciplinas del catálogo | phastc, NeuroVoc, pyclarity, NEURON o Brian2, elementos finitos | 2 |
| H3 · Biología humana multiescala | Vías, células, tejidos, morfogénesis y moléculas fuera de la audición | COPASI, VCell, PhysiCell, CompuCell3D, BETSE, FEBio, GROMACS, OpenMM, Boltz-2, OpenFold3 | 3 |
| H4 · Biología comparada, modelos animales y longevidad | Organismos modelo in silico y envejecimiento | OpenWorm; modelos de envejecimiento por relevar | Sin etapa: horizonte de la visión |

La audición es la puerta porque reúne las cinco vías: comprender (modelos funcionales maduros), sustituir (audífonos e implantes de uso masivo), reparar y regenerar (células ciliadas, que aves y peces regeneran y los mamíferos no), guiar la morfología (malformaciones congénitas del oído) y preservar (presbiacusia, enlace directo con el envejecimiento).

### Escalas de simulación

| Escala | Herramientas abiertas | Servicios con API | Caso en audición | Caso en biología general o longevidad |
| --- | --- | --- | --- | --- |
| Molecular | GROMACS, OpenMM, [BioEmu](https://huggingface.co/microsoft/bioemu) (MIT) | Inductiva, Galaxy, Tamarind Bio, BioNeMo | FGF y su receptor (FGFR) en el desarrollo del oído; prestina | Telomerasa; mTOR con rapamicina |
| Vías y redes | COPASI, VCell | runBioSimulations, servidores de VCell | Notch y Atoh1 en la diferenciación de células ciliadas; ototoxicidad | Redes de senescencia |
| Célula y tejido | PhysiCell, CompuCell3D, Morpheus, Chaste, tyssue, SimuCell3D, BETSE | o²S²PARC | Epitelio sensorial (Cohen 2020); invaginación de la placoda ótica; espiral del conducto coclear | Senescencia tisular, reparación, control bioeléctrico de la forma |
| Neural | NEURON, NEST, Brian2, Arbor, phastc | NSG, EBRAINS | Nervio auditivo, tronco encefálico, acúfenos, implante | Envejecimiento neural |
| Órgano y dispositivo | Elementos finitos (FEniCS, FEBio, Mesh2HRTF); morfometría 3D (SlicerMorph) | o²S²PARC, SimScale | Oído medio, malformaciones, campo eléctrico del implante | Prótesis, interfaces cerebro-máquina, crecimiento craneofacial |
| Organismo y especie | [OpenWorm](https://openworm.readthedocs.io/en/stable/projects/) (Sibernetic) | Sin servicio relevado | Pez cebra y aves frente a mamíferos | *C. elegans*, modelo clásico de longevidad |

La dinámica molecular simula de nanosegundos a microsegundos y el envejecimiento ocurre en años. Las simulaciones moleculares explican mecanismos, como la unión de un fármaco a su blanco, pero no simulan el envejecimiento. Conectar escalas es un desafío de investigación, como el puente entre regeneración y audición.

### Morfogénesis y morfología guiada

Guiar la morfología es corregir o diseñar la forma de un tejido u órgano; regenerar es restaurar una forma perdida. En audición, el caso de entrada son las malformaciones congénitas del oído externo, medio e interno, y las craneosinostosis por mutaciones de FGFR, que con frecuencia se acompañan de pérdida auditiva.

| Herramienta | Qué simula | Licencia | Encaje |
| --- | --- | --- | --- |
| [CompuCell3D](https://en.wikipedia.org/wiki/CompuCell3D) | Modelo de Potts celular (GGH) para morfogénesis tisular; C++ y Python | GPL | Patrón del epitelio sensorial con señales difusibles como FGF |
| [Morpheus](https://fairdomhub.org/models/320?version=1) | Modelos celulares con ODE y reacción-difusión, construidos desde una interfaz gráfica sin programar | Sin verificar en esta revisión | Docencia de morfogénesis con gradientes de morfógenos |
| [PhysiCell](https://ideas.repec.org/a/plo/pcbi00/1005991.html) | Agentes 3D que crecen, se dividen, migran y mueren en un microambiente bioquímico | BSD | Crecimiento de tejidos y organoides |
| [Chaste](https://digitalresearch.nottingham.ac.uk/2026/03/31/chaste-cancer-heart-and-soft-tissue-environment/) | Modelos discretos de tejidos: autómata celular, Potts, centro celular y vértices | Sin verificar en esta revisión | Epitelios y comparación entre métodos |
| [tyssue](https://pypi.org/project/tyssue) | Modelos de vértices de epitelios en 2D y 3D; Python, v1.1.0 (2024) | GPLv3 | Plegado e invaginación epitelial, como la placoda ótica |
| [SimuCell3D](https://link.springer.com/10.1038/s43588-024-00620-9) | Células 3D deformables con polaridad, matriz extracelular y lúmenes | BSD-3 | Epitelios pseudoestratificados, vesículas y tubos del oído interno |
| [Tissue Forge](https://www.biorxiv.org/content/10.1101/2022.11.28.518300.full.pdf) | Partículas sin red, interactivo, con API en C, C++ y Python | LGPLv3 | Docencia interactiva y biofabricación (fusión de esferoides) |
| [EmbryoMaker](https://thenode.biologists.com/?p=26938) | Epitelio, mesénquima y redes génicas acoplados a mecánica; injertos y perlas de factores de crecimiento in silico | Abierto; licencia no declarada | Interacciones epitelio-mesénquima del desarrollo craneofacial y del oído |
| [BETSE](https://pypi.org/project/betse/0.8.2) | Bioelectricidad de tejidos: canales iónicos, uniones gap, electrodifusión y redes génicas; interfaz BETSEE | BSD-2 (v1.5.0, abril de 2025) | Control bioeléctrico del patrón y la regeneración (línea de Levin) |
| [FEBio](https://en.wikipedia.org/wiki/FEBio) | Elementos finitos para biomecánica: sólidos no lineales, medios multifásicos, fluido-estructura | MIT desde la versión 2.9 | Mecánica del oído medio y de tejidos craneofaciales |
| [SlicerMorph](https://repository.lsu.edu/biosci_pubs/4034) | Morfometría geométrica 3D sobre 3D Slicer: landmarks, plantillas y análisis | Sin declarar en la fuente | Cuantificar una malformación y medir el resultado de guiar la forma |
| [Neural Cellular Automata](https://research.google/pubs/growing-neural-cellular-automata/) | Autómatas celulares entrenables que crecen y regeneran un patrón | Código no enlazado en la fuente | Exploratorio: modelo abstracto de morfogénesis, no biológico |

Hay modelos específicos sin software reutilizable verificado: un modelo celular mecánico de la espiral del conducto coclear ([bioRxiv](https://www.biorxiv.org/content/10.1101/2020.07.24.219469v2)) y un marco de elementos finitos que predice el crecimiento de la calvaria tras la cirugía de craneosinostosis sagital ([Cross et al. 2022](https://research.monash.edu/en/publications/a-computational-framework-to-predict-calvarial-growth-optimising-/)). Para datos 3D, MorphoSource aloja tomografías y mallas con términos por colección; por ejemplo, el Florida Museum exige uso no comercial ([política](https://www.floridamuseum.ufl.edu/digital-lab/digital-data-policies/morphosource-digital-data-policy/)).

### Servicios de simulación con API

| Servicio | Qué ejecuta | Acceso | Condiciones verificadas | Uso previsto |
| --- | --- | --- | --- | --- |
| [runBioSimulations](https://docs.biosimulations.org/users/simulating-projects/) | Simuladores registrados en BioSimulators, sobre archivos COMBINE/OMEX | API REST con las mismas herramientas que la web | Costos y límites no publicados | Primer servicio de propósito general: una integración abre muchos simuladores |
| [VCell](https://en.wikipedia.org/wiki/VCell) | ODE, PDE espaciales, estocásticos y basados en reglas | Todos los solvers pueden correr en servidores de UConn | MIT; financiado por NIH; API no documentada en la fuente | Vías con geometría celular |
| [NSG](https://pypi.org/project/pynsgr) | Simuladores neuronales en HPC | API REST (NSG-R) con el cliente pynsgr | Requiere cuenta; costo no indicado | Audición central, acúfenos |
| [EBRAINS](https://wiki.ebrains.eu/bin/view/Collabs/documentation/tools-and-services-documentation/?rev=56.1) | NEST, NEURON, Arbor, The Virtual Brain; hardware neuromórfico SpiNNaker | Ejecución remota en lote con cliente Python | Condiciones de acceso sin verificar | Redes auditivas grandes |
| [o²S²PARC](https://docs.sparc.science/docs/key-o2s2parc-features) | Interfaces neurales; exposición electromagnética y acústica con modelos anatómicos | API para ejecutar trabajos; cliente Python osparc (MIT) | Plataforma de código abierto; precios en una guía aparte | Implantes cocleares y prótesis neurales |
| [Inductiva](https://libraries.io/pypi/inductiva) | Simuladores físicos abiertos en la nube; una versión anterior listaba 8, entre ellos GROMACS y OpenFOAM | Cliente Python (Apache-2.0, v0.18.12) | Precios sin verificar | Dinámica molecular sin HPC propio |
| [Galaxy ChemicalToolbox](https://galaxyproject.org/bare/eu/usegalaxy/cheminformatics/) | GROMACS, AmberTools, AutoDock Vina, MDAnalysis | Web con flujos de trabajo compartidos | Gratuidad no declarada en la página | Enseñar dinámica molecular con flujos reproducibles |
| [Tamarind Bio](https://app.tamarind.bio/index.md) | Más de 300 herramientas: estructura, docking, diseño | API única de trabajos, CLI y servidor MCP | Cuota mensual gratuita; precios sin verificar | Estructura y docking bajo demanda |
| [NVIDIA BioNeMo NIM](https://developer.nvidia.com/blog/build-an-ai-scientist-for-life-science-discovery-with-nvidia-bionemo-agent-toolkit/) | OpenFold3, Boltz-2, DiffDock, RFdiffusion, Evo 2 | Endpoints en build.nvidia.com con clave | Solo para desarrollo y pruebas, no para producción | Prototipos; luego autoalojar el modelo |
| [AlphaFold 3](https://www.maginative.com/article/google-deepmind-makes-alphafold-3-open-source-for-academia/) | Predicción de complejos moleculares | Pesos a pedido; sin API mencionada | Solo uso académico no comercial, también sus resultados | Solo docencia; en el producto, Boltz u OpenFold |
| [SimScale](https://www.simscale.com/product/api/) | Fluidos, mecánica estructural, térmico, electromagnetismo | API REST; SDK en Python y C# | Planes pagos; sin nivel gratuito confirmado | Elementos finitos del oído medio |

### Integración e ideas

- **Capa única de trabajos:** enviar, consultar y recibir resultados con adaptadores para contenedores propios (AMT) y servicios externos. El estudio estructurado registra servicio, versión y parámetros, para reproducir aunque cambie el proveedor.
- **Estándares como contrato:** COMBINE/OMEX y SED-ML para vías y células; NeuroML o PyNN para redes neurales. Así runBioSimulations, VCell o un contenedor propio son intercambiables.
- **Agente de IA como operador:** el agente invoca simuladores por API o MCP; el usuario decide y el agente ejecuta.
- **Modelos animales in silico (H4):** la FDA publicó en abril de 2025 una hoja de ruta para reducir ensayos en animales e informó en abril de 2026 las metas del primer año, con el modelado computacional entre los métodos alternativos ([FDA](https://fda.gov/news-events/press-announcements/fda-achieves-year-1-goals-reducing-animal-testing-drug-development)). Es un argumento ético y comercial; el laboratorio no se presenta como herramienta regulatoria.
- **Biología comparada (H4):** comparar especies que regeneran células ciliadas con las que no une audición, regeneración y modelos animales.
- **Casos puente:** FGF–FGFR conecta las malformaciones del oído con la escala molecular; la telomerasa es un primer caso molecular de longevidad.

**Sin verificar:** la lista de herramientas de NSG, si las aplicaciones de PhysiCell en nanoHUB tienen API, los precios de casi todos los servicios, la lista actual de simuladores de Inductiva, los modelos de envejecimiento en SBML y las licencias de Morpheus, Chaste, EmbryoMaker y SlicerMorph. Fuentes consultadas al Oct 15, 2026.

## Hoja de ruta por etapas

El proyecto avanza en cuatro etapas: se valida con un caso acotado de audición, se lanza un MVP en audiología, se completa la audición con otros simuladores junto con servicios de pago, y recién después se abren la biología humana en varias escalas, el mercado y el estándar. Las cinco vías (comprender, sustituir, reparar y regenerar, guiar la morfología, preservar) atraviesan todas las etapas en igualdad. La biología comparada, los modelos animales in silico y la longevidad (H4) quedan como horizonte de la visión, sin etapa propia hasta validar la Etapa 3. Cada etapa se abre solo si se cumple el criterio de avance de la anterior (propuesto, a ajustar).

&#91;embedded content: hoja de ruta · 4 etapas, 3 criterios de avance\]

La Etapa 1 (resaltada) es el primer objetivo de construcción; los criterios de avance son una propuesta inicial a ajustar. La franja superior indica que el fin biomédico y sus cinco vías atraviesan todas las etapas en igualdad.

### Etapa 0 · Validar

- **Alcance:**
  - **Compuerta técnica:** probar zilany2014, bruce2018 y los modelos de habla y localización en Octave dentro de un contenedor, y medir el tiempo por estímulo.
  - **Compuerta legal:** auditar con `amt_info` la licencia de cada modelo; consultar a UGent por una licencia comercial de Verhulst y CoNNear, y si un piloto docente cuenta como uso académico no comercial; revisión legal del copyleft de red.
  - **Caso único:** audiograma → parámetros de bruce2018 (partiendo de `bruce2018_fitaudiogram`; el mapeo es trabajo propio a documentar) → respuesta periférica → índice de inteligibilidad con pyclarity o pystoi (MIT).
  - **Prototipos:** estudio estructurado, artículo interactivo y video asistido por IA, armados casi a mano.
  - **Entrevistas:** profesionales de la audiología, docentes e investigadores en audición.
- **Horizonte y objetivos:** H1, audición con AMT. El caso busca comprender un daño auditivo concreto y deja documentado qué significaría sustituir, reparar o preservar esa función, sin simularlo todavía.
- **Criterio para pasar a la Etapa 1:** al menos un modelo de AMT corre en Octave con licencia apta para el uso previsto, un estudio es reproducido por un tercero y hay interés docente confirmado.
- **Se pospone:** plataforma propia, mercado y certificaciones.

### Etapa 1 · MVP

- **Alcance:**
  - **Servicio de simulación:** cola de trabajos y dos contenedores, uno Octave con los modelos de AMT que pasaron la Etapa 0 y otro Python con licencia permisiva (pyclarity, pystoi, NeuroVoc, phastc, pyfar). Los componentes GPL y AGPL quedan aislados.
  - **Repositorio:** estudios con DOI y versionado.
  - **Artículo interactivo:** resultados precalculados y en caché, ejemplos sonoros, reproducción en cola de lo no calculado y dos niveles de lectura.
  - **Agente:** modo mentor para el piloto docente, sobre los modelos de la Etapa 0 con estado de validación visible.
  - **Video:** automático de 60 a 90 s.
  - **Piloto docente:** una cátedra con trabajos prácticos sobre modelos de AMT.
- **Horizonte y objetivos:** H1. Cuatro de las cinco vías se expresan con modelos auditivos: comprender la pérdida periférica; sustituir, con la inteligibilidad del habla con un audífono simulado (pyclarity); preservar, con pérdida de células ciliadas y de sinapsis por edad o ruido como cambio de parámetros; y reparar o regenerar, con escenarios "qué pasaría si" de recuperación de células ciliadas o de sinapsis y un módulo didáctico propio de inhibición lateral Notch. La presbiacusia metabólica queda fuera, porque ningún modelo abierto representa el potencial endococlear. Los escenarios de preservar y de reparar o regenerar se etiquetan como Exploratorio, y el módulo Notch se presenta como ilustración, porque Cohen 2020 muestra que la mecánica domina el ordenamiento. Guiar la morfología entra en la Etapa 2.
- **Se pospone:** modo copiloto del agente e integración de colaboración (pasan a la Etapa 2), revista con revisión por pares, reproducción completa, mercado y certificación formal.

### Etapa 2 · Crecer

- **Alcance:** revisión abierta y paso gradual a revista; reproducción completa bajo demanda con créditos de cómputo; nivel de lectura intermedio; video semi-asistido y servicio premium de edición; portafolio verificable e insignias abiertas; suscripciones y convenios institucionales; más modelos de AMT y de otras áreas; modo copiloto del agente y colaboración con herramientas existentes integradas; puente entre el estado coclear y los parámetros del modelo; cadena de oído medio OpenEar → Gmsh → Code\_Aster; gEAR como servicio externo.
- **Horizonte y objetivos:** H2 y comienzo de H3. Sustituir: implantes y audífonos con phastc, NeuroVoc y pyclarity. Reparar y regenerar: modelos de biología celular y tisular vinculados a los modelos auditivos. Guiar la morfología: malformaciones del oído con geometría 3D y elementos finitos, y morfogénesis del oído interno con modelos celulares. Preservar: ototoxicidad, ruido y presbiacusia. Contraste con datos experimentales cuando existan.
- **Se pospone:** transacciones de financiamiento y certificación formal.

### Etapa 3 · Consolidar

- **Alcance:** mercado de proyectos y servicios (simulaciones como herramientas educativas y clases basadas en ellas); vitrina de líneas de investigación para inversionistas e instituciones, sin intermediar transacciones hasta resolver el marco regulatorio; certificación formal avalada por universidades; formato de estudio y de modelos como estándar abierto; extensión a otros tejidos y áreas de la biología y la medicina humana; convenios clínicos para tomografías de malformaciones y validación del puente contra datos humanos.
- **Horizonte y objetivos:** H3. Las cinco vías se aplican a otros tejidos y sistemas con simuladores de propósito general y servicios con API, en varias escalas; la audición queda como caso de referencia para validar y enseñar. Al validar esta etapa se evalúa abrir H4.

## Modelo de negocio por etapas

Se prioriza la suscripción institucional más créditos de cómputo por uso, porque los costos de HPC y de video con IA son variables y deben trasladarse al uso. El resto de las fuentes de ingreso del borrador original entra en etapas posteriores.

| Etapa | Ingresos | Costos principales |
| --- | --- | --- |
| 0 · Validar | Sin ingresos; el objetivo es validar interés y viabilidad técnica | Tiempo del equipo y cómputo mínimo |
| 1 · MVP | Pilotos con carreras de fonoaudiología y laboratorios de audición | Cómputo de simulación y generación de video por estudio |
| 2 · Crecer | Suscripción institucional, créditos de cómputo por uso y servicios premium de video y edición | Cómputo variable (HPC o nube), video con IA, soporte |
| 3 · Consolidar | Licencias a laboratorios, comisiones del mercado de proyectos, certificación | Gobernanza, cumplimiento regulatorio, alianzas |

## Gobernanza, ética y propiedad intelectual

El borrador original no cubría estos temas; se definen desde la Etapa 1 porque sostienen la credibilidad y evitan conflictos posteriores.

| Tema | Qué debe definirse | Desde |
| --- | --- | --- |
| Gobernanza científica | Quién valida los modelos, con qué criterios y cómo se resuelven las disputas | Etapa 1 (mínima), 2 (revisión abierta) |
| Propiedad intelectual y licencias | Licencias de modelos, datos y resultados; derechos de coautoría; qué es abierto por defecto; AMT se distribuye bajo GPL3 y algunos modelos tienen licencias propias, lo que condiciona cómo se integran y redistribuyen | Etapa 1 |
| Uso responsable de la IA | Etiquetado de contenido sintético, límites de la simplificación automática, registro de aportes de la IA | Etapa 1 |
| Datos de usuarios | Privacidad y tratamiento de los datos de estudiantes e investigadores | Etapa 1 |
| Certificación y alianzas | Convenios con instituciones que avalen certificaciones formales | Etapa 3 |

Las simulaciones tienen fines biológicos y médicos, pero sus resultados no reemplazan la evaluación clínica: cada estudio indica su estado de validación y el alcance de uso permitido.

## Riesgos y supuestos a validar

El mayor riesgo es prometer más de lo que una simulación puede garantizar; el segundo, abarcar demasiado a la vez.

| Riesgo | Mitigación |
| --- | --- |
| Sobrepromesa científica o pseudociencia | Lenguaje de "laboratorio computacional", estado de validación visible y curaduría de modelos |
| Uso de los resultados como si fueran evidencia clínica | Aviso explícito de que las simulaciones no reemplazan la evaluación clínica, con estado de validación y alcance de uso visibles en cada estudio |
| La visión multiescala se promete antes de poder simularla: AMT modela solo la función auditiva | Separar visión y hoja de ruta: expresar las vías como parámetros etiquetados Exploratorio, sumar otras escalas solo al cumplir los criterios de avance y dejar H4 fuera de la hoja de ruta |
| Alcance excesivo (varios productos en uno) | Etapas, MVP acotado e integración de herramientas existentes |
| Dependencia de AMT: MATLAB/Octave, comunidad externa y licencias por modelo | Ejecutar en Octave, comprobar la compatibilidad modelo por modelo y revisar licencias antes de integrar (verhulst2018 es solo académico no comercial) |
| Dependencia de servicios de simulación externos: precios, cuotas, cierre, condiciones de uso y cambios de versión | Capa única de trabajos con alternativa autoalojada; registrar servicio y versión en cada estudio; no enviar datos de pacientes a terceros sin acuerdos; revisar condiciones (AlphaFold 3 es no comercial y BioNeMo alojado es solo para pruebas) |
| Costos variables de cómputo y video | Créditos por uso, caché de resultados y ejecución bajo demanda |
| Distorsión por simplificación con IA | Validación obligatoria del autor y niveles de lectura trazables al texto técnico |
| Arranque en frío de la comunidad | Empezar por investigadores y docentes de audición; el mercado de varios lados llega después |
| Dependencia de alianzas institucionales | Portafolio verificable e insignias abiertas antes de la certificación formal |

**Supuestos a validar en la Etapa 0:**

- Existe al menos un modelo de AMT que admite parámetros de pérdida auditiva y se ejecuta correctamente en Octave.
- Las vías de sustituir, reparar y regenerar, y preservar pueden expresarse como parámetros de los modelos auditivos sin sobreprometer.
- Fonoaudiólogos, docentes e investigadores valoran publicar y enseñar con estudios estructurados.
- El video asistido por IA alcanza una calidad aceptable con baja intervención humana.
