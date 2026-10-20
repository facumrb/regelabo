# Laboratorio computacional abierto: resumen del proyecto

Oct 19, 2026 · @Facundo Ramírez

Es un **laboratorio computacional abierto de biología y medicina humana**: allí se simulan preguntas científicas y cada estudio termina como artículo interactivo y como video de divulgación. La audición es el caso piloto que valida la plataforma; desde ahí se amplía por etapas al resto de la biología y la medicina humana.

Este documento resume cada parte del documento base: Laboratorio computacional de ciencia abierta: documento base por etapas.

## Visión y principios

El laboratorio busca comprender la función y la enfermedad y simular cinco vías de intervención, todas en igualdad.

| Vía | Qué busca |
| --- | --- |
| Comprender | Entender cómo funciona el cuerpo y cómo enferma |
| Sustituir | Reemplazar una función con prótesis |
| Reparar y regenerar | Restaurar un tejido o una forma perdida |
| Guiar la morfología | Corregir o diseñar una forma, como en una malformación |
| Preservar | Cuidar la salud con la edad (longevidad) |

**Por qué la audición es el caso piloto:** las cinco vías aparecen ahí en un sistema acotado. Hay modelos funcionales maduros, audífonos e implantes de uso masivo, células ciliadas que no regeneran en mamíferos, malformaciones congénitas del oído y pérdida auditiva por edad.

**El eje es el estudio estructurado:** un único objeto digital con hipótesis, modelo, parámetros, resultados y evidencia. De él salen el artículo, los niveles de lectura, el guion del video y el portafolio del estudiante.

**Siete principios de diseño:**

- **Simular no es experimentar:** la simulación genera hipótesis, no reemplaza al experimento.
- **Estado de validación visible:** cada modelo muestra si está *Validado con datos*, *Verificado* o es *Exploratorio*, y eso limita para qué se puede usar.
- **Integrar antes que construir:** se reutiliza lo que ya existe.
- **Formatos abiertos, servicios de pago.**
- **Trazabilidad entre humano e IA:** queda registrado qué aportó cada uno.
- **Fin biomédico con las cinco vías en igualdad.**
- **Plataforma agnóstica de dominio:** nada de la arquitectura depende de la audición; sumar un área nueva es sumar modelos, no rehacer la plataforma.

## Artículo, video y agente de IA

El artículo deja de ser un PDF y pasa a tener seis características:

| Característica | Cómo se concreta |
| --- | --- |
| Legible por IA | Los datos van estructurados junto al texto |
| Reproducible | Un botón "reproducir" vuelve a correr la simulación |
| Interactivo | Deslizadores sobre resultados precalculados y en caché |
| Complejidad ajustable | Niveles de lectura para expertos y no expertos |
| Confiable | DOI y versionado |
| Interoperable | El formato apunta a ser un estándar abierto |

**Video asistido por IA:**

- **Cómo se arma:** el video sale del mismo estudio. La IA hace lo repetitivo (guion, edición, subtítulos) y el autor conserva el criterio.
- **Niveles de producción:** automático (clip de 60 a 90 s), semi-asistido y premium con un editor humano.
- **Regla:** las imágenes generadas por IA nunca muestran datos, y todo lo sintético se etiqueta.

**Agente de IA y colaboración:**

- **Un solo agente con dos modos:** mentor socrático para aprender y copiloto de investigación.
- **Colaboración:** el chat y las videollamadas se toman de herramientas existentes. Lo propio del laboratorio es la coautoría sobre el estudio.

## Uso docente

El laboratorio se usa para enseñar con estudios reales, en cualquier área de la biología y la medicina humana.

- **Destinatarios:** estudiantes de grado, docentes y profesionales en formación continua.
- **Formatos:** trabajo práctico sobre un estudio existente, proyecto guiado por el mentor y curso.
- **Roles:** el docente arma la actividad y evalúa; el estudiante formula, simula, interpreta y publica; el agente guía como mentor socrático.
- **Acreditación:** portafolio verificable, luego insignias abiertas y luego certificación universitaria.
- **Por etapa:** entrevistas a docentes (0), piloto con una cátedra (1), insignias e integración con el campus virtual (2), cursos de otras áreas y certificación (3).

## Catálogo, horizontes y simuladores

**Catálogo auditivo:** releva 14 disciplinas de la audición, cada una con sus simuladores, licencias y brechas.

- **Hallazgo:** la periferia del oído y el habla están bien cubiertas, pero 8 de las 14 disciplinas no tienen un simulador abierto reutilizable.
- **El puente:** no existe nada que conecte la regeneración con la audición funcional; ese puente queda como propuesta de diseño propia.
- **Alerta de licencias:** Verhulst 2018 es solo para uso académico, y los componentes GPL y AGPL deben aislarse.

**Cuatro horizontes temáticos:**

| Horizonte | Contenido | Estado |
| --- | --- | --- |
| H1 | Audición con AMT | En la hoja de ruta |
| H2 | Toda la audición | En la hoja de ruta |
| H3 | Biología humana en varias escalas | En la hoja de ruta |
| H4 | Biología comparada, modelos animales y longevidad | Solo en la visión, por ahora |

**Escalas y herramientas:**

- **Seis escalas:** de la molécula al organismo, cada una con sus herramientas, un caso en audición y un caso en biología general o longevidad.
- **Morfogénesis:** 12 herramientas para guiar la forma de tejidos y órganos, como CompuCell3D, tyssue, SimuCell3D, BETSE, FEBio y SlicerMorph.
- **Servicios con API:** 11 servicios para enviar simulaciones y recibir resultados, como runBioSimulations, NSG, o²S²PARC y Tamarind.
- **Ideas de integración:** una capa única de trabajos y estándares como contrato, para no depender de un solo proveedor.

## Hoja de ruta

El proyecto avanza en cuatro etapas, y cada una se abre solo si se cumple el criterio de avance de la anterior.

&#91;embedded content: hoja de ruta · 4 etapas, 3 criterios de avance\]

La Etapa 0 resuelve primero lo que la investigación dejó abierto: qué modelos de AMT corren en Octave y con qué licencias. La Etapa 1 (resaltada) es un MVP acotado: resultados precalculados, agente en modo mentor y un piloto con una cátedra; el modo copiloto y la colaboración pasan a la Etapa 2. Al validar la Etapa 3 se evalúa abrir H4: biología comparada, modelos animales y longevidad.

## Negocio, gobernanza y riesgos

**Modelo de negocio:**

- **Ingreso principal:** suscripción institucional más créditos de cómputo por uso, porque el cómputo y el video tienen costos variables.
- **Más adelante:** licencias, comisiones del mercado de proyectos y certificación.

**Gobernanza, ética y propiedad intelectual:**

- **Qué se define desde la Etapa 1:** quién valida los modelos, el régimen de licencias, el uso responsable de la IA y la privacidad de los datos.
- **Aviso clave:** las simulaciones no reemplazan la evaluación clínica.

**Riesgos y supuestos:**

- **Riesgos principales:** prometer más de lo que una simulación puede garantizar y abarcar demasiado a la vez.
- **Riesgos de dependencia:** depender de AMT y de servicios externos.
- **Supuestos a validar en la Etapa 0:**
  - que AMT funcione en Octave;
  - que las vías se puedan expresar como parámetros sin sobreprometer;
  - que la comunidad audiológica valore este formato;
  - que el video con IA tenga una calidad aceptable.

## Lo que todavía está abierto

Ninguno de estos puntos frena el plan, pero conviene resolverlos en la Etapa 0:

- [ ] Probar AMT en Octave.
- [ ] Confirmar las licencias pendientes, entre ellas las de modelos de AMT, Morpheus y Chaste.
- [ ] Verificar los precios de la mayoría de los servicios de simulación con API.
