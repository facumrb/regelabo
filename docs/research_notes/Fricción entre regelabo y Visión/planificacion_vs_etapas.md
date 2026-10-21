# Capa de planificación y documentación de regelabo frente a las etapas, horizontes, alcance y supuestos de la Visión

Fecha de las notas: 2026-10-19 (lectura del repositorio en el estado de `main` = `ed5f207`, más la carpeta sin seguimiento `backend/services/`).
Método: lectura completa de los tres documentos de Visión y de toda la capa de planificación (proposal, MEMORY, AGENTS, plan, RN, 21 decisiones, specs, guías, CC3D, trajectory, presentation_data), historial git de solo lectura, y verificación puntual en código cuando una afirmación de un documento lo requería. No se ejecutó nada (ni app, ni base, ni tests). `graphify-out/` no existe en el repo, así que no se usó `graphify`.

Convención de citas: `[X:líneas][X]` apunta al archivo definido en la leyenda final; los hashes de commit enlazan a GitHub (`origin` = facumrb/regelabo). Las secciones "Cited Findings" son hechos verificados en archivos; las "Inferences" son lectura mía y están marcadas como tales; "Gaps" es lo que no pude determinar.

Abreviaturas de los documentos de Visión: **VB** = documento base por etapas (14-oct-2026), **VR** = resumen (19-oct-2026), **VS** = Simuladores para disciplinas de audición.

---

## 1. Qué dicen los documentos de planificación que regelabo es, para quién es, qué viene, y cuáles son los requisitos y plazos académicos del TPI

### Takeaway
Regelabo se define en toda su capa de planificación vigente como **el TPI de la materia Soporte (UTN FRRO)**, un monolito en 3 capas (FastAPI + React + PostgreSQL) que ejecuta Verhulst 2018 a partir de audiogramas, para estudio y experimentación "no profesional", con entrega **a fin de 2026**, equipo de 3 y 4 módulos (usuarios, casos/audiogramas, simulación con historial, arquetipos). La IA/ML, el RAG y la integración hospitalaria están explícitamente **fuera de alcance** ("año próximo, fuera de la materia"). Ningún documento de planificación vigente menciona la Visión.

### Cited Findings
**Identidad y alcance**
- AGENTS.md define el proyecto como plataforma web "(FastAPI + React) que ejecuta el modelo biofísico de Verhulst et al. (2018) a partir de audiogramas y visualiza EFR, ABR y FFT", y como "el TPI de la materia Soporte (UTN FRRO)", que "debe cumplir la arquitectura en 3 capas con los nombres de carpeta del checklist de la cátedra" — [AGENTS.md:5][AGENTS].
- Decisión 001 (2026-10-13): el TPI cubre 4 módulos (autenticación/usuarios; casos y audiogramas con perfil auditivo propio vía `OHC_ind`; simulación con historial: cola, ondas W1/W3/W5, EFR, FFT, latencias y amplitudes; arquetipos: ~12 con nombre clínico, comparación del ABR cargado, registro de hipótesis de estudio) y define el sistema como "herramienta de **estudio y experimentación, no profesional**: muestra coincidencias, nunca diagnósticos (RN9)" — [001:6-14][D001].
- Alternativas descartadas en 001: el asistente de IA con papers ("queda para el año próximo, fuera de la materia") y el clasificador de ML entrenado ("evolución del módulo de arquetipos") — [001:17-20][D001]. Quedan "para después": exportar a PDF, comparación entre fenotipos, generación en lote, optimización de estímulos, click/tone burst, WebSocket e integración con hospitales (HL7 FHIR, leyes 25.326 y 26.529) — [001:22][D001].
- Plan de trabajo, fases: (1) Sprint 0 "la base" (en curso), (2) Despliegue en DigitalOcean + dominio `.me` + Caddy, (3) Módulos por persona, y "Futuro (año próximo, fuera de la materia)": clasificador ML con modelo preentrenado, IA para consultar papers, integración con hospitales — [PLAN:11-16][PLAN]. Origen del plan: "resumen consolidado del grilling del 2026-10-14, aprobado por el equipo antes de empezar a programar" — [PLAN:5][PLAN].
- Reparto: Valentino = Simulación + historial (CU3); Compañero A = Casos + audiogramas (CU2, perfil propio con `OHC_ind`); Compañero B = Arquetipos + comparación (CU4, CU5) — [PLAN:41-45][PLAN].

**Para quién es**
- Decisión 009: "3 tipos de usuario final (estudiante, investigador y fonoaudiólogo)"; `tipo_perfil` "cambia textos de ayuda y cupos, no permisos"; rol técnico admin — [009:6-11][D009]. Cupos RN5a: estudiante 1 simulación simultánea, investigador 3, fonoaudiólogo 3; RN5b por hora: 10/30/30 — [RN:11-12][RN].
- La propuesta original dice: "Permitir a fonoaudiólogos e investigadores científicos cargar audiogramas, ejecutar de forma remota simulaciones... y visualizar los resultados a la par que se consulta literatura científica... impulsada por un asistente de IA" — [PROP:9][PROP]. La versión para presentación: "fonoaudiólogas y profesionales de la audición... sin la necesidad de recurrir a profesionales de la simulación" — [PRES:9][PRES].
- `functionalitiesOverview.md` dice que el modelo **no** sirve como herramienta de diagnóstico complementario: "Su verdadera utilidad reside en la Investigación y Desarrollo (I+D)" como "puente" daño microscópico a ondas medibles — [FO:34-40][FO]. La presentación repite: "Generar un EFR simulado... no aporta información clínica nueva" — [PRES:51][PRES].
- Origen del proyecto según `trajectory.md`: interés inicial en terapias regenerativas, CompuCell3D "se descartó rápidamente por su lejanía de la práctica fonoaudiológica", aparece Verhulst; el estado del arte mostró que no se aplicó a escenarios de regeneración, lo que "provocó la suspensión del enfoque regenerativo para posterior aplicación" y la oportunidad de "una plataforma web que permita a profesionales sin formación técnica acceder y utilizar modelos cocleares" — [TRAY:3-7][TRAY]. Cierra: "Queda para la investigación a largo plazo el cómo adaptar modelos como el de CompuCell3D" — [TRAY:9][TRAY].

**Qué viene (estado y pendientes)**
- Estado al 2026-10-17/19: Sprint 0 en la rama `feature/setup-entorno`, pasos 1-5 hechos (capas, base, auth, Casos, frontend TS, cola + worker + caché + historial); pendientes: paso 6 (CI con GitHub Actions + `CONTRIBUTING.md`), 7 (documentación: `CLAUDE.md`, `PROYECTO.md`, `docs/arquitectura.md`, diagrama de dominio), 8 (issues y tag `semana-01`) — [MEM:13-15][MEM], [PLAN:24-35][PLAN]. Verificado: no existen `PROYECTO.md`, `.github/` ni `CONTRIBUTING.md` en el árbol (`git ls-files`).
- Pendientes abiertos del plan: licencia de Verhulst (UGent) — "el repo es público y contiene el código del modelo; la licencia prohíbe redistribuirlo sin autorización escrita. Hasta resolverlo con la cátedra, no se traen los `.mat` de `OHC_ind`"; `proposal.md` desactualizado; latencias y amplitudes de ondas I/III/V (definir con fonoaudiología); perfiles `Custom_*` compartidos entre usuarios — [PLAN:67-72][PLAN]. MEMORY.md repite: "licencia de Verhulst (bloquea `OHC_ind`), `proposal.md` desactualizado..." — [MEM:37][MEM] y "Pedir permiso antes de copiar archivos del repo oficial de Verhulst (licencia UGent sin resolver)" — [MEM:31][MEM].
- Frontend actual (verificado en `git ls-files`/`ls`): páginas Bienvenida, Login, Registro, MiCuenta, casos/(MisCasos, NuevoCaso, FichaCaso, FormularioCaso), simulaciones/(Historial, DetalleSimulacion). Backend: controller y datos de autenticación, casos, simulaciones, perfiles, audiogramas (prototipo). No hay controller/datos de arquetipos ni comparación aunque las tablas `arquetipo`, `registro_abr`, `comparacion` ya existen — [tablas.py:133-163][TABLAS].
- Decisión 020 deja `resultado_simulacion.metricas` vacío: latencias y amplitudes de W1/W3/W5 son "Pendiente (decidido dejarlo para después)" y las necesita la comparación con arquetipos — [020:25][D020].

**Requisitos académicos y plazos del TPI (lo que consta en el repo)**
- Entrega: "a fin de 2026", grupo de 3 — [MEM:13][MEM], [001:6][D001]. No hay fecha exacta en ningún archivo (grep de `entrega|fecha|plazo` en docs de planificación: solo "fin de 2026"). Hoy es 2026-10-19: quedan del orden de 10 semanas (cálculo mío con fin de diciembre; ver Gaps).
- El enunciado y los checklists están **fuera del repo**: `/mnt/datos/Electivas-Soporte/practica-2024/TPI` — [MEM:10][MEM]. Lo que el repo reproduce de ellos, por decisiones y plan:
  - 3 capas con nombres de carpeta fijos (`views`, `controller` o `business`, `datos`) y `app.py` en la raíz — [002:6][D002]; las funciones de `datos/` devuelven objetos de negocio definidos en `controller/`, "como pide el checklist" — [010:10][D010].
  - Base SQL con acceso directo u ORM y negocio independiente del motor — [003:6][D003].
  - Contraseñas con hash; sesiones independientes entre ventana normal e incógnito (tokens/cookies); errores HTTP — [004:6][D004].
  - Sistema "online" (desplegado) — [011:6][D011].
  - Tag semanal `semana-NN` con changelog, "mencionando a los profesores (lo exige el enunciado)"; cambios por pull request con CI en verde; issues de GitHub con tablero — [PLAN:47-50][PLAN].
  - Plantilla `PROYECTO.md` ("template del TPI") — [PLAN:34][PLAN].
  - `proposal.md` en la raíz "porque lo pide la cátedra" (mensaje del commit [478b918](https://github.com/facumrb/regelabo/commit/478b918), 2026-08-02, que movió `docs/guias/proposal.md` a `proposal.md`).
- Reglas de convivencia con la IA fijadas en AGENTS.md: "Nunca tomar una decisión... por tu cuenta. Siempre consultar, dar opciones y justificación"; no ejecutar comandos de alta/modificación de git; no tocar la base — [AGENTS.md "Reglas"][AGENTS]. Todo el trabajo en español — [AGENTS.md "Idioma"][AGENTS].

### Inferences
- Todo lo que está en el camino crítico del TPI (3 capas, auth propia, base SQL, online, CI, tags semanales) es una **restricción dura externa** con fecha; la Visión no tiene calendario (ver sección 8) y por lo tanto no puede ordenar trabajo contra ese reloj. Cualquier reorientación hacia la Etapa 0 de la Visión que consuma las ~10 semanas compite con módulos aún sin hacer (audiogramas completos, arquetipos/comparación, métricas de ondas, CI, despliegue).
- Es probable (no verificado) que la "cátedra" y los profesores sean los primeros evaluadores/usuarios reales de regelabo; eso es un público muy distinto del "piloto docente con una cátedra de fonoaudiología" de la Visión.
- La documentación vigente está **dividida en dos estratos**: lo nuevo (AGENTS/MEMORY/plan/RN/decisiones, 2026-10-13 en adelante, autoría de commit de Valentino Ortiz) y un estrato legado anterior a la reorganización (proposal.md, README.md, docs/arquitectura.md, docs/prototype/*, docs/guias/sdd_methodology.md, partes de docs/specs/*) que todavía habla de SOA, Supabase Auth/Storage, Celery+Redis, LangChain/ChromaDB, DeepSeek/Qwen, microservicios `core/simulation/llm` (ver sección 9).

### Gaps
- El enunciado/checklist real del TPI, su fecha de entrega exacta y los criterios de evaluación no están en el repo. No pude confirmar si la cátedra aceptaría un cambio de foco o de modelo.
- No hay evidencia en el repo de que los otros dos integrantes (Compañero A y B, sin nombre en los docs) hayan leído o aceptado la Visión.

---

## 2. Registro de decisiones (docs/decisiones/): una línea por archivo

### Takeaway
Hay 21 archivos de decisión (001-020 y 022; **no existe 021**, y `git log --all -- 'docs/decisiones/021*'` no devuelve nada). Todas son decisiones de ingeniería del TPI tomadas entre 2026-10-13 y 2026-10-17; ninguna toca el modelo de negocio, la licencia comercial ni un cambio de modelo (AMT/Octave). Las tres que más interactúan con la Visión son 005/020 (cola), 006 (caché por huella) y 022 (perfiles auditivos), más 001 (alcance) y 002 (monolito).

### Cited Findings
Fuente común: [docs/decisiones/README.md][DREADME] (índice) y cada archivo.

| N.º | Fecha | Una línea |
|---|---|---|
| 001 | 10-13 | Alcance del TPI: 4 módulos; herramienta de estudio, no profesional; IA/RAG y ML quedan para el año próximo; hospitales/HL7 FHIR después — [001][D001] |
| 002 | 10-13 | Monolito modular en 3 capas (`views`/`controller`/`datos` + `simulacion/`) por checklist de la cátedra; se descartan los microservicios del prototipo (core, simulation, llm) — [002:6-13][D002] |
| 003 | 10-13 | SQLAlchemy 2 + Alembic + PostgreSQL; dev en Docker, producción en Supabase "solo como PostgreSQL"; backup diario propio con `pg_dump`; señales como JSON; se descarta Supabase Auth/Storage y `supabase-py` — [003][D003] |
| 004 | 10-13 | Autenticación propia con argon2 y cookie httpOnly (la sesión fue reemplazada por 013); se descarta Supabase Auth porque no permite mostrar hash ni lógica en la capa de negocio — [004][D004] |
| 005 | 10-13 | Cola en tabla `simulacion` + proceso worker con `SELECT … FOR UPDATE SKIP LOCKED` + polling; se descarta Celery+Redis y WebSocket; dato clave: ~75 s por simulación, 1,5-2,5 min estimados en servidor, ~1,1 GB de RAM, un solo núcleo — [005:6-18][D005] |
| 006 | 10-13 | Caché por huella SHA-256 (perfil, fibras, estímulo, semilla, versión del modelo); el modelo es determinista; los arquetipos son "caché precargada"; hay que cambiar la versión si se toca el código del modelo — [006:6-17][D006] |
| 007 | 10-13 | ~12 arquetipos con nombre clínico (Normal, Presbiacusia leve/mod/sev, Trauma sináptico leve/mod/sev, Pérdida plana, mixtas) con estímulo RAM 4 kHz/70 dB SPL; similitud por correlación de Pearson; ABR de prueba simulados; se descartan las 132 combinaciones y el clasificador ML — [007:6-18][D007] |
| 008 | 10-13 | Entidad "Caso" (alias, edad y sexo opcionales, notas), sin datos que identifiquen a una persona, por Leyes 25.326 y 26.529; migración futura a `Paciente` cifrado y adaptador HL7 FHIR — [008:6-19][D008] |
| 009 | 10-13 | `tipo_perfil` (estudiante/investigador/fonoaudiólogo) cambia cupos y textos, no permisos; admin; cupos RN5a/b/c; límites con slowapi — [009][D009] |
| 010 | 10-14 | Esquema de 9 tablas desde el inicio (la 10.ª `sesion` llegó después), UUIDv7, valores fijos con CHECK, borrado lógico de casos, `timestamptz`, transacciones explícitas — [010][D010] |
| 011 | 10-13 | Hosting provisorio: DigitalOcean x86 2 núcleos/4 GB (~US$24/mes) con crédito US$200 del Student Pack (~8 meses), dominio `.me` 1 año, Caddy con HTTPS; plan B Azure for Students (~3 meses) — [011:9-15][D011] |
| 012 | 10-13 | React + TypeScript + Vite + Tailwind + Plotly + react-router; migración de `.jsx` a `.tsx` el 10-16 — [012][D012] |
| 013 | 10-14 | Sesión en el servidor (token aleatorio, hash SHA-256 en tabla `sesion`, 12 h); reemplaza el JWT de 004 — [013][D013] |
| 014 | 10-14 | Todo bajo `/api`, errores con código estable, tests contra PostgreSQL real, endpoints del prototipo sin auth hasta reemplazarlos — [014][D014] |
| 015 | 10-14 | Páginas `/login` y `/registro`, TypeScript para código nuevo, contexto de sesión, panel de pruebas solo en dev — [015][D015] |
| 016 | 10-14 | Colección de Bruno en `docs/api/` (en lugar de Postman) — [016][D016] |
| 017 | 10-16 | Paginación por cursor (id UUIDv7) con "Cargar más" — [017][D017] |
| 018 | 10-16 | Cambio de contraseña con la actual, cierre de otras sesiones, reseteo por admin vía comando — [018][D018] |
| 019 | 10-16 | Endpoints del prototipo pasan a requerir sesión; `/health` público; pantalla de bienvenida; queda abierto que los `Custom_*` se comparten entre usuarios (contra RN4) — [019:19][D019] |
| 020 | 10-16 | Cola en detalle: `POST /api/simulaciones` responde 202, `GET` lista/detalle, worker en carpeta temporal, huella incluye hash del contenido del perfil, cupos, worker caído a 5 min, se elimina `POST /api/simulate`; pendientes las métricas de ondas — [020][D020] |
| 021 | — | **No existe** (hueco en la numeración) |
| 022 | 10-17 | Perfiles auditivos propios por aproximación desde los 8 perfiles planos (sin los `.mat` bloqueados por licencia), catálogo de 22 perfiles base, transparencia del "techo del modelo", personalizados con hash — [022][D022] |

Detalle de las tres que pidió el encargo:
- **022 (perfiles auditivos)**: el modelo no recibe audiogramas sino polos (`StartingPoles.dat`); el repo trae 33 perfiles con 11 duplicados; el flujo previo copiaba el perfil más cercano y perdía la forma de la curva — [022:6-7][D022]. **Techo**: "Solo representa la pérdida de las células ciliadas externas: el polo se satura en el daño máximo (0,302) a ~20 dB HL en 250 Hz, 25 en 500 Hz, 30 en 1-2 kHz y 35 en 4-8 kHz", y `OHC_ind` también recorta — [022:8][D022]. Solución: tabla "dB HL → polo" de los 8 perfiles planos; reconstruye los 24 perfiles no planos con error medio 0,18 dB y máximo 4,7 dB (`tests/test_perfiles.py`) — [022:11][D022]; cartel fijo y aviso final con la curva pedida y la simulada si se recorta más de 5 dB — [022:12][D022]. Alternativa descartada "Esperar a `OHC_ind`: bloqueado por la licencia y tendría el mismo techo" — [022:20][D022].
- **020/005 (cola)**: ver tabla; el worker es un proceso Python en el mismo entorno que la API, una simulación a la vez por proceso — [020:11][D020]; "Se puede pasar a Celery más adelante sin tocar la capa de negocio" — [005:18][D005].
- **006/020 (huella/caché)**: huella = SHA-256 de perfil, hash del contenido del perfil, frecuencias, nivel, fibras, semilla y versión del modelo; `SEMILLA=1` y `VERSION_MODELO="verhulst2018-1"` en `backend/simulacion/motor.py`; lo reutilizado no consume cupo — [020:12-13][D020], [motor.py:27-33][MOTOR].

Reglas de negocio (RN1-RN10) — [RN:7-18][RN]: RN1 audiograma válido (125-8000 Hz, −10 a 120 dB HL, incluye 500/1k/2k/4k); RN2 gravedad por PTA (normal ≤20, leve ≤40, moderada ≤70, severa >70) y patrón plano/pendiente; RN3 rangos de parámetros (nivel 0-100 dB SPL, portadora 125-8000, modulación 20-1000, fibras nH≤30/nM≤15/nL≤15); RN4 aislamiento por dueño (404, no 403); RN5a/b/c cupos y tope global de cola (503 con ≥20 pendientes); RN6 registro ABR válido (`time`,`amplitude`, ≥10 ms, ≥10 kHz); RN7 top 3 por Pearson, concluyente si >70 % y ≥5 puntos sobre el segundo; RN8 solo admin edita arquetipos, la comparación guarda copia de los arquetipos; RN9 aviso "Coincidencia morfológica con un arquetipo simulado. No constituye un diagnóstico clínico", palabra "diagnóstico" prohibida en la UI, se guarda aceptación del aviso de uso no profesional con fecha; RN10 huella/caché.

### Inferences
- El patrón de las 21 decisiones es consistente: **minimizar piezas de infraestructura** (sin Celery/Redis/WebSocket/microservicios/Supabase Auth) por razones de costo, evaluación en cátedra y equipo de 3. La Visión, en cambio, asume en Etapa 1 "cola de trabajos y dos contenedores" (VB:264); la decisión 005 ya dejó explícitamente la puerta a reemplazar el mecanismo de cola sin tocar el negocio, lo que reduce el costo de alinear.
- La decisión 022 es el hallazgo técnico más valioso para la Visión: es el primer **mapeo audiograma a parámetros del modelo** documentado y validado del proyecto, y mide un límite estructural de Verhulst que la Visión no menciona.
- Falta una decisión sobre licencia y sobre la relación con UGent: aparece como "pendiente" pero no tiene archivo de decisión con alternativas.

### Gaps
- No hay decisión sobre qué hacer con la licencia UGent (pedir permiso a UGent vs a la cátedra vs retirar el código del repo público); `docs/decisiones/` no tiene entrada para eso.
- Número 021: no pude determinar por qué falta (no hay rastro en git).

---

## 3. Historial git y relación documental con la Visión

### Takeaway
Los tres documentos de Visión entraron en **un solo commit** (`0ccca91`, 2026-10-19 22:57, autor Facundo = cuenta facumrb) que solo agrega esos tres archivos (601 inserciones) y no toca `proposal.md`, `MEMORY.md`, `AGENTS.md`, el plan ni ninguna decisión. Diez segundos después (`ed5f207`, 22:57:37) un merge los integra con el trabajo del Sprint 0 de Valentino. **Ningún documento de planificación vigente referencia la Visión**, y la Visión no referencia a regelabo.

### Cited Findings
- `0ccca91` "Visión completa a largo plazo", Facundo, lun 2026-10-19 22:57:27 -0300: 3 archivos nuevos en `docs/Vision/` (+601 líneas) — [commit 0ccca91](https://github.com/facumrb/regelabo/commit/0ccca91962ea453ebc2fca9287c89e9b75d59a45) (verificado con `git show --stat`).
- `ed5f207` "Merge branch 'main' of https://github.com/facumrb/regelabo", Facundo, 2026-10-19 22:57:37, padres `0ccca91` y `3d66fb7`; `3d66fb7` es el "Merge pull request #4 from facumrb/feature/setup-entorno" de Valentino del mismo día (con `5ffac42` "Agregar perfiles auditivos (decisión 022)") — [commit ed5f207](https://github.com/facumrb/regelabo/commit/ed5f2074ca47060121fc8225daf04c48259fc157). El diff del merge respecto del padre Visión es el Sprint 0 completo (capas, auth, AGENTS.md, MEMORY.md...), no cambios de la Visión.
- Búsqueda en todo el repo (excluyendo `node_modules`, `.venv`): los términos `Visión`, `Octave`, `bruce2018`, `zilany`, `AMT`, `pyclarity`, `pystoi`, `ciencia abierta`, `biología humana` aparecen únicamente en `docs/Vision/*` (74 coincidencias, 4 archivos) y una coincidencia incidental en `proposal.md:43` ("Visión a Futuro: ... DVC y MinIO") que no se refiere a la Visión nueva — [PROP:43][PROP].
- Búsqueda inversa: `regelabo|TPI|UTN|Valentino|FastAPI|Laboratorio Virtual Auditivo|proposal` en `docs/Vision/`: **0 coincidencias**.
- Cronología relevante (de `git log`): primer commit 2026-02-13 (Facundo Ramírez); estructura base y entidad Usuarios 2026-04-13; propuesta para presentación 2026-04-14; CC3D "Orden" 2026-05-07; specs/diagramas de actividad por Laureano Oliva y Valentino entre 2026-05 y 2026-08; `proposal` movido a la raíz 2026-08-02; plan de cuellos de botella 2026-06-24; prototipo inicial 2026-10-14 (`0ac3603`); reorganización en 3 capas 2026-10-14 (`313f9fd`, que "saca CC3D y los microservicios"); BD+decisiones 2026-10-14 (`0691642`); auth+Casos+frontend 2026-10-16 (`9016e45`); cola 2026-10-17 (`8ec683b`); AGENTS+MEMORY 2026-10-17 (`f9a9f6b`); perfiles 2026-10-19 (`5ffac42`). Autores por cantidad de commits: Facundo 55 (+5 como "Facundo Ramírez"), Valentino Ortiz 18, Laureano Oliva 11, Juli 1, giani1233 1. Remotos: `origin` facumrb/regelabo y `fork` giani1233/regelaboForked.
- El documento base de la Visión está firmado "Oct 14, 2026 · @Facundo Ramírez" [VB:3][VB] y el resumen "Oct 19, 2026 · @Facundo Ramírez" [VR:3][VR]; el plan de trabajo toma su "origen" en un grilling con la misma fecha (2026-10-14) [PLAN:5][PLAN]. Son dos líneas de trabajo del mismo día, redactadas por personas distintas según los commits (Visión: cuenta facumrb; Sprint 0 y plan: Valentino Ortiz).

### Inferences
- La Visión se escribió en paralelo y no se reconcilió con la capa de planificación: el commit del 19-oct es un "depósito" de documentos, no una modificación de AGENTS/MEMORY/plan. Si se decide que la Visión gobierna, **hay que escribir explícitamente el puente** (hoy no existe en ningún archivo).
- El hecho de que la Visión se versione dentro de `docs/` del mismo repo del TPI significa que un evaluador de la cátedra que abra el repo la verá junto al TPI; con la licencia de Verhulst sin resolver (sección 6) esto puede leerse como alcance mucho mayor que el entregable.

### Gaps
- No sé qué se habló fuera del repo (chat, reuniones). No hay issue ni PR que justifique la Visión.

---

## 4. Mapa etapa por etapa: dónde cae lo construido y lo planificado de regelabo

### Takeaway
Regelabo **no está en ninguna etapa de la Visión**: hizo gran parte de lo que la Visión pone en la Etapa 1 (cola de trabajos, caché, historial, autenticación, gobernanza mínima de privacidad y avisos) **sin haber hecho nada de la Etapa 0** (compuerta técnica AMT/Octave, compuerta legal con UGent, caso único con inteligibilidad, prototipos manuales, entrevistas). Además construyó exactamente lo que la Etapa 0 declara "pospuesto": plataforma propia. Y lo hizo sobre el modelo (Verhulst 2018) que la Visión manda tratar como "no disponible" mientras no haya licencia.

### Cited Findings
Textos de la Visión usados como vara:
- Etapa 0 "Validar" — compuerta técnica (zilany2014, bruce2018, habla y localización en Octave en contenedor, medir tiempo por estímulo), compuerta legal (auditar con `amt_info`; consultar a UGent por licencia comercial de Verhulst/CoNNear y si un piloto docente cuenta como uso académico no comercial; revisión legal del copyleft de red), caso único (audiograma → parámetros de bruce2018 partiendo de `bruce2018_fitaudiogram`, "el mapeo es trabajo propio a documentar" → respuesta periférica → índice de inteligibilidad con pyclarity o pystoi), prototipos (estudio estructurado, artículo interactivo, video asistido por IA "armados casi a mano"), entrevistas (audiólogos, docentes, investigadores). Criterio de avance: un modelo AMT corre en Octave con licencia apta, un estudio es reproducido por un tercero y hay interés docente confirmado. **Se pospone: plataforma propia, mercado y certificaciones** — [VB:249-259][VB]. VS titula la Etapa 0 "validar (antes de escribir código de plataforma)" — [VS:91][VS].
- Etapa 1 "MVP" — cola de trabajos y dos contenedores (Octave/AMT y Python permisivo con pyclarity, pystoi, NeuroVoc, phastc, pyfar; GPL/AGPL aislados), repositorio con DOI y versionado, artículo interactivo (precalculado/caché, ejemplos sonoros, reproducción en cola de lo no calculado, dos niveles de lectura), agente en modo mentor, video automático de 60-90 s, piloto docente con una cátedra; horizonte H1; se posponen copiloto, colaboración, revista, reproducción completa, mercado, certificación — [VB:261-271][VB].
- Etapa 2 — revisión abierta, reproducción completa con créditos, nivel intermedio, video semi-asistido/premium, portafolio e insignias, suscripciones institucionales, **puente estado coclear → parámetros**, cadena OpenEar→Gmsh→Code_Aster, gEAR; H2 y comienzo de H3 — [VB:273-277][VB]. Etapa 3 — mercado, certificación, estándar abierto, otros tejidos, convenios clínicos; H3 — [VB:279-282][VB].

Estado de regelabo contra cada ítem (hecho verificado en repo/docs):

| Ítem de la Visión | Etapa | Regelabo hoy | Evidencia |
|---|---|---|---|
| Probar zilany2014/bruce2018 en Octave en contenedor, medir tiempo | 0 | **No hecho.** Cero apariciones de Octave/AMT fuera de `docs/Vision/`; el único contenedor del repo es PostgreSQL | grep global; [docker-compose.yml][COMPOSE] solo define `db` |
| Auditar licencias con `amt_info` | 0 | **No hecho** | grep global |
| Consultar a UGent (licencia comercial; ¿piloto docente = académico no comercial?) | 0 | **No hecho.** Se planea "resolverlo con la cátedra", no con UGent | [PLAN:69][PLAN] |
| Revisión legal del copyleft de red | 0 | No hecho; regelabo usa licencia MIT en la raíz (`LICENSE`, "Copyright (c) 2026 Facundo Ramírez") | `LICENSE` |
| Caso único audiograma → modelo periférico → índice de inteligibilidad | 0 | **Análogo parcial**: audiograma → perfil de polos (decisión 022) → Verhulst → EFR/ABR/FFT. Otro modelo (Verhulst, no bruce2018), mapeo ya documentado y validado, **sin índice de inteligibilidad** (no hay pyclarity/pystoi en `pyproject.toml`) | [022:11][D022], [pyproject.toml:7-18][PYPROJECT] |
| Prototipos manuales: estudio estructurado, artículo interactivo, video con IA | 0 | **No hecho.** Lo más cercano: historial y detalle de simulación con gráficos Plotly (`Historial.tsx`, `DetalleSimulacion.tsx`) | árbol frontend |
| Entrevistas a audiólogos/docentes/investigadores | 0 | **No hay registro.** Los casos de uso se derivaron con agentes (`speckit.analyze`, `.opencode/agent/analisis-requerimientos.md`) y revisión de literatura; D020 deja "definir con fonoaudiología" como pendiente | [020:25][D020], [spec README][SPECSREADME] |
| Plataforma propia pospuesta | 0 | **Construida** (usuarios, roles, cupos, cola, caché, 10 tablas, historial, frontend con rutas) | decisiones 003-020 |
| Cola de trabajos | 1 | **Hecha**, sobre PostgreSQL + worker | [005][D005], [020][D020] |
| Dos contenedores (Octave+AMT y Python permisivo) | 1 | No; un solo proceso worker en el mismo entorno Python ≥3.14 | [pyproject.toml:6][PYPROJECT] |
| Caché / resultados precalculados | 1 | **Hecha** (huella, RN10); arquetipos planificados como caché precargada | [006:17][D006] |
| Repositorio de estudios con DOI/versionado | 1 | No | — |
| Artículo interactivo con niveles de lectura | 1 | No | — |
| Agente mentor socrático | 1 | No. La IA planificada es otra cosa (RAG sobre papers + clasificador ML), y está fuera de alcance | [001:18][D001], [PROP:39-43][PROP] |
| Video automático 60-90 s | 1 | No | — |
| Piloto docente con una cátedra | 1 | No. Hay rol "estudiante" con menores cupos, pero no concepto de cátedra/curso/docente | [009][D009] |
| Gobernanza: privacidad de datos de usuarios | 1 | **Hecha en lo mínimo**: "Caso" sin datos identificatorios, RN4, hash argon2, aviso de uso no profesional con fecha | [008][D008], [RN:10,17][RN] |
| Gobernanza: aviso de que no reemplaza evaluación clínica | 1 | **Hecha** (RN9) | [RN:17][RN] |
| Estado de validación visible por modelo | 1 | Parcial: RN9 y el cartel de "techo del modelo" de 022; **no** hay la taxonomía Validado/Verificado/Exploratorio | [022:12][D022] |
| Gobernanza: licencias de modelos y qué es abierto | 1 | Pendiente reconocido, sin decisión | [PLAN:69][PLAN] |
| Modelo de negocio (pilotos en E1, suscripción en E2) | 1-2 | Inexistente; hosting con crédito estudiantil (~8 meses) | [011:9][D011] |
| Puente estado coclear → parámetros del modelo | 2 | Embrión: audiograma → polos OHC (022) y fibras nH/nM/nL editables (RN3); no hay módulo biológico previo | [022][D022], [modelos.py:105-110][MODELOS] |
| Cadena de oído medio, gEAR, malformaciones | 2 | Fuera de alcance: no figuran en ningún spec | [spec README][SPECSREADME] |
| Otros modelos de AMT y de otras áreas | 2 | No; sin embargo `functionalitiesOverview` ya marca como "no factible con Verhulst" implantes (#6), gemelo digital (#7), tinnitus (#11), latencia binaural (#13) y como "parcial" habla en ruido (#10), audífonos (#14), seguimiento del habla (#15) — justo los huecos que el catálogo de la Visión cubre con otros modelos | [FO:106-158][FO], [spec README:45-62][SPECSREADME] |
| Convenios clínicos / hospitales | 3 | Mencionado como futuro (HL7 FHIR, leyes 25.326/26.529), sin plan | [001:22][D001], [008:15-19][D008] |
| Regeneración / CompuCell3D | 3 (H3) | **Descartado por ahora** en regelabo: carpeta `docs/CC3D/` como referencia; "suspensión del enfoque regenerativo para posterior aplicación" | [TRAY:3-7][TRAY], [CC3D idea][CC3D], [AGENTS "Otros directorios"][AGENTS] |

Cosas que regelabo hizo y que la Visión pone **más tarde**: cola y caché (E1), plataforma propia (pospuesta en E0), usuarios con roles y cupos por tipo de perfil (el "crédito de cómputo" de E2 es su equivalente conceptual), hosting con dominio.
Cosas que la Visión pone **primero** y regelabo no hizo: compuerta técnica (AMT/Octave), compuerta legal (UGent, `amt_info`, copyleft), caso único con inteligibilidad, prototipos manuales de estudio/artículo/video, entrevistas, y la definición de criterios de avance.

### Inferences
- Visto desde la Visión, regelabo es una **Etapa 1 parcial construida sobre una Etapa 0 no cursada**: el criterio de avance 0→1 (modelo AMT en Octave con licencia apta; un estudio reproducido por un tercero; interés docente confirmado) no se cumple en ninguno de los tres puntos.
- Visto desde regelabo, la Etapa 0 de la Visión equivale a un **nuevo proyecto de investigación** (prueba de AMT en Octave, consulta legal, entrevistas, tres prototipos manuales), no a trabajo de plataforma; no reutiliza casi nada del código salvo la idea del job queue y la lógica de cupos/caché.
- Lo que sí es transferible casi 1 a 1 hacia la Etapa 1 de la Visión: auth + sesiones + roles, cola con `SKIP LOCKED`, caché por huella, aislamiento por dueño (RN4), paginación por cursor, errores con código estable, colección Bruno, disciplina de decisiones, tests contra PostgreSQL. Lo que NO es transferible sin refactor: el esquema de `simulacion` (ver sección 5, principio 7).
- La propia sección de "no factible/parcial" de `functionalitiesOverview.md` coincide casi punto a punto con la lista de "disciplinas sin simulador" de la Visión; las dos líneas de análisis llegaron independientemente a "Verhulst solo cubre periferia hasta IC".

### Gaps
- No sé si el equipo considera que la Etapa 0 se puede reducir a un "informe de viabilidad" dentro del TPI (p. ej. como documento de trabajo futuro) o si pretende ejecutarla.
- No se midió nada de Octave; no puedo decir si el hueco técnico es grande o pequeño.

---

## 5. Mapa principio por principio (los siete principios de diseño) y pilares de la Visión

### Takeaway
Hay **alineación fuerte** en principios de ciencia responsable (1, 2 parcial, 5 parcial-no aplicable, 6 en el aviso clínico) y en "formatos abiertos/licencia permisiva propia" (4); **fricción** en "integrar antes que construir" (3), en "plataforma agnóstica de dominio" (7: el esquema está atado a Verhulst) y en el eje central de la Visión, el **estudio estructurado**, que no tiene análogo en regelabo.

### Cited Findings
| Principio / pilar (Visión) | Qué dice la Visión | Estado en regelabo | Alineación / fricción |
|---|---|---|---|
| 1. Laboratorio computacional | La simulación no reemplaza al experimento, genera hipótesis contrastables — [VB:30][VB] | RN9 impone "hipótesis de estudio" y prohíbe "diagnóstico"; FO:37 dice que el modelo sirve "para generar hipótesis" — [RN:17][RN], [FO:38][FO] | **Alineado** (mismo léxico) |
| 2. Estado de validación visible | Tres niveles; ningún resultado sin indicar respaldo — [VB:31,38-44][VB] | No hay taxonomía; sí avisos: RN9 y el cartel del techo del modelo de 022 — [022:12][D022]; FO:34 admite la limitación clínica; VS:64 documenta que ZBC/Verhulst no está validado con EFR humanos | **Parcial.** Hoy toda salida de regelabo sería "Exploratorio/Verificado" sin que el producto lo diga |
| 3. Integrar antes que construir | Reutilizar AMT y estándares (SBML, COMBINE/OMEX, NeuroML), no desarrollar — [VB:32][VB] | Regelabo integra **un** modelo copiado dentro del repo (`backend/simulacion/verhulst/`, con `license.txt` UGent) y construyó plataforma propia (auth, cola, caché) en vez de integrar servicios; la mitad de la capa de simulación (adaptador `motor.py`) sí está aislada | **Fricción de secuencia** (build vs integrate), compensada por el adaptador único |
| 4. Formatos abiertos, servicios de pago | Formato abierto; negocio en infraestructura y servicios — [VB:33][VB] | Licencia MIT en la raíz; sin modelo de negocio; el código de Verhulst dentro del repo está bajo UGent Academic License | **Alineado en MIT propio; contradicción interna** con el código UGent redistribuido (VS:40: la sección 2 prohíbe distribuir sin autorización escrita) |
| 5. Trazabilidad humano-IA | Registrar aporte de IA y autor, CRediT, etiquetar sintético — [VB:34][VB] | Regelabo no genera contenido con IA en producto; el **desarrollo** usa IA (decisión 012: "el desarrollo se apoya en IA"), AGENTS.md y MEMORY.md regulan agentes. No hay registro de procedencia en los datos | **No aplica aún**; dato curioso: el repo ya aplica trazabilidad de IA para código (AGENTS/MEMORY), no para estudios |
| 6. Fin biomédico, cinco vías | Comprender, sustituir, reparar/regenerar, guiar morfología, preservar — [VB:35][VB] | Spec cubre "comprender" (mecanismos), "preservar" (sordera oculta edad/trauma, #12) y parcialmente "sustituir" (audífonos/implantes marcados no factibles). "Reparar/regenerar" **suspendido** (trayectoria). "Guiar morfología" no aparece | Alineación parcial con comprender/preservar; **la quinta vía y regenerar no existen en regelabo** |
| 7. Plataforma agnóstica de dominio | "Sumar un área es sumar modelos y casos, no rehacer la plataforma" — [VB:36][VB] | `simulacion` tiene columnas `perfil`, `frecuencia_portadora_hz`, `nivel_db_spl`, `frecuencia_modulacion_hz`, `n_h`, `n_m`, `n_l` y `resultado_simulacion` guarda `efr_uv`, `armonicos`, `espectro`, `ondas`, `metricas` de W1/W3/W5; **no hay columna de modelo ni de versión** (la versión solo entra en el hash de la huella) — [tablas.py:96-130][TABLAS]; la validación RN3 está escrita para Verhulst; el adaptador `motor.py` es el único punto que toca el modelo — [AGENTS "Arquitectura"][AGENTS] | **Fricción real**: la lógica está acoplada al modelo; refactor a "modelo + parámetros genéricos + versión" es necesario para la Etapa 1 de la Visión |
| Pilar: estudio estructurado (eje) | Objeto único con hipótesis, modelo, parámetros, resultados y afirmaciones enlazadas — [VB:11][VB] | No existe. "Caso" es un registro anonimizado de sujeto con audiogramas (decisión 008); "Comparación" guarda top-3 y una copia de arquetipos para reproducir (RN8) — es el germen más cercano | **Brecha mayor**: el eje de la Visión no tiene contraparte |
| Pilar: reproducibilidad (semilla, versión, parámetros) | Cada figura guarda modelo, versión, semilla, parámetros — [VB:53][VB] | Determinismo y semilla fija (006); huella con versión; RN8 copia de arquetipos | **Alineado en el principio**; falta persistir modelo/versión/semilla como datos visibles |
| Pilar: ecosistema / capa única de trabajos con adaptadores | Adaptadores para contenedores propios y servicios externos — [VB:232][VB] | Cola propia con un solo tipo de trabajo; `motor.py` como adaptador | **Base reutilizable** si se generaliza |
| Pilar: agente de IA | Mentor socrático + copiloto — [VB:83-92][VB] | IA planificada = RAG de papers (LangChain/ChromaDB/DeepSeek/Qwen) en `proposal.md` y ML en 001 | **Divergente en forma**: ambos postergan la IA, pero a funciones distintas |
| Pilar: video con IA / artículo moderno / repositorio con DOI | VB:46-81 | No existe nada comparable (PDF y export `CU-07` en specs de arquetipos, fase 1) — [requerimientos-diagnostico-arquetipos:21][REQARQ] | Brecha total |
| Gobernanza (privacidad, IP, IA responsable) | "Desde la Etapa 1" — [VB:295-307][VB] | Privacidad cubierta con criterio local (Leyes 25.326/26.529, decisión 008); IP/licencias abierto; IA responsable n/a | **Parcial**; regelabo aporta el marco legal argentino que la Visión no cita |
| Riesgo: "abarcar demasiado a la vez" | Segundo riesgo mayor — [VB:311,318][VB] | Decisión 001 y la regla "No re-litigar decisiones" aplican exactamente ese control para el TPI | **Alineado en actitud** |

### Inferences
- El principio 7 es el que más compromete: la Visión lo convierte en promesa de arquitectura (VR:33), y el esquema actual, con diez tablas creadas de una vez (decisión 010: "el equipo prefirió el esquema completo desde el inicio"), consolidó supuestos de Verhulst. Cambiarlo ahora es barato (solo hay migraciones iniciales, `alembic` en 3 versiones); después de que los módulos A y B copien el patrón de Casos, será más caro. (Inferencia mía basada en [010:Alternativas][D010] y la lista de migraciones.)
- La contradicción "MIT en la raíz + código UGent dentro del repo público" es independiente de la Visión, pero la Visión la vuelve más visible porque convierte la licencia UGent en un "obstáculo principal... de licencia, no técnico" (VS:3).

### Gaps
- No verifiqué si el frontend muestra el aviso RN9 en todas las pantallas ni si implementa los carteles descritos en 022 (eso lo cubre otro investigador del código).

---

## 6. Qué evidencia aporta regelabo a favor o en contra de los supuestos y riesgos de la Visión

### Takeaway
Regelabo aporta **la única evidencia de ejecución real** de Verhulst 2018 en servidor headless dentro del conjunto de documentos (el modelo que la Visión solo probó localmente con estímulos de 30 ms): corre bajo Python ≥3.14, con solver C compilado, en un worker encolado, ~75 s por simulación de 0,4 s de estímulo, 1,1 GB y un núcleo. También aporta tres hallazgos que la Visión no registra: el **techo de saturación OHC**, la dependencia de `.mat` bloqueados por licencia en `OHC_ind`, y un mapeo audiograma→polos validado. No aporta nada sobre AMT/Octave.

### Cited Findings
- **Headless/servidor**. La Visión: "En ejecución sin interfaz gráfica solo se probó localmente Verhulst 2018 v1.2 (Python 3.13, 8 a 11 s por estímulo de 30 ms)" [VS:3][VS]; detalle: 401 frecuencias características, 2 CPU, 7 GB de RAM, 8-11 s por simulación de 30 ms [VS:36][VS]. Regelabo: estímulo de 0,4 s a 100 kHz [motor.py:27-28][MOTOR]; "Una simulación tarda ~75 s en una notebook (i7 de 11.ª gen.)... se estiman entre 1,5 y 2,5 min en el servidor; usa ~1,1 GB de RAM y un solo núcleo" [005:6][D005]; `requires-python = ">=3.14"` [pyproject.toml:6][PYPROJECT]; `GET /api/health` expone `c_solver_available` [AGENTS "Comandos"][AGENTS]. El plan de cuellos de botella (2026-06-24) estimaba "2-10 min" [Plan de Mitigación:13][PMIT] (estimación previa, no medición).
- **Determinismo y caché** (VB:54 interactivo sobre "resultados precalculados y en caché"; VS:64 "modelo IHC-AN determinista"): regelabo lo implementa y lo documenta: `subject`/`SEMILLA=1`, huella SHA-256, `resultado_simulacion.huella` único, varios `simulacion` apuntando al mismo resultado — [006:6-9][D006], [tablas.py:96-110][TABLAS].
- **Parámetros por defecto de fibras**: código de regelabo `nH=13` (HSR), `nM=3` (MSR), `nL=3` (LSR) — [modelos.py:105-110][MODELOS]; el plan de cuellos de botella usa también "Normal (nH=13, nM=3, nL=3)" — [PMIT:41][PMIT]. Esto desambigua el "3, 3 y 13" de VB:157 vs "13/3/3" de VS:16 (ver sección 8).
- **Mapeo audiograma → parámetros** (la Visión lo da por "trabajo propio a documentar": VB:254; VS:91, VS:135 "el mapeo audiograma → parámetros de modelo no está documentado en ninguna fuente verificada"): decisión 022 lo resuelve para Verhulst por aproximación y lo valida (error medio 0,18 dB, máx 4,7 dB) — [022:11][D022].
- **Límite estructural de Verhulst**: saturación a ~20/25/30/35 dB HL según frecuencia; "Solo representa la pérdida de las células ciliadas externas" — [022:8][D022]. La Visión sí consigna "Sin parámetro de potencial endococlear" [VB:126][VB] y "la presbiacusia metabólica queda fuera" [VB:270][VB], pero **no** el techo del polo (moderada/severa no se reproducen). Esto toca directamente el supuesto "Las vías... pueden expresarse como parámetros de los modelos auditivos sin sobreprometer" [VB:329][VB].
- **Dependencia de `.mat`**: el plan de mitigación ya listaba "Archivos `.mat` requeridos por `ohc_ind()`" como riesgo medio [PMIT:15][PMIT]; el plan de trabajo reporta que la licencia UGent los bloquea y deja sin resolver el perfil propio vía `OHC_ind` [PLAN:69][PLAN]. La Visión solo menciona que `OHC_ind.py` convierte un audiograma en perfil [VS:60][VS], sin esa dependencia.
- **Licencia, caso concreto**: el repo es público y contiene el modelo con su `license.txt` UGent (`backend/simulacion/verhulst/license.txt` presente; el README del modelo declara "licensed under the UGent acadamic license") — [PLAN:69][PLAN]. Lo que la Visión llama "obstáculo principal" [VS:3][VS] y "tratar a Verhulst como una licencia por negociar" [VS:3][VS] ya es, en regelabo, una **dependencia en producción**.
- **Interés en no-técnicos**: `trajectory.md` formula la misma oportunidad que la Visión ("no existe una interfaz [que] abstraiga las funcionalidades técnicas... democratizar") — [TRAY:7][TRAY].
- **Python/entornos**: regelabo exige Python ≥3.14; la Visión registra phastc para Python 3.9-3.12 y pyclarity para Python ≥3.11 [VS:56][VS], y el README de Verhulst solo declara 2.7/3.6 [VS:117][VS]. Contenedores separados (propuestos en VB:264) serían necesarios.
- **Complejidad ciudadana**: regelabo cuantifica el costo de cómputo con cupos y tope global de cola (RN5), equivalente funcional a los "créditos de cómputo por uso" de VB:286 sin cobro.

### Inferences
- Escalado lineal (mío, no medido): 0,4 s / 0,03 s ≈ 13,3 veces; 8-11 s × 13,3 ≈ 107-147 s en el hardware de la Visión, contra ~75 s en una notebook i7 11.ª gen. de regelabo; son magnitudes compatibles, lo que sugiere que "algunos modelos tardan segundos por estímulo" (VB:54) subestima a Verhulst para estímulos de duración clínica. Requiere medición con el mismo estímulo.
- Regelabo ofrece, sin proponérselo, **un caso de datos para la compuerta técnica de la Visión** (tiempo por estímulo, memoria, headless con C) pero sobre el modelo "no disponible"; para la Etapa 0 de la Visión sirve como contraste, no como sustituto.
- La experiencia del techo OHC sugiere que el riesgo "sobrepromesa" (VB:315) es concreto y ya ocurrió en regelabo: "La pantalla mostraba 'moderada' y simulaba una pérdida menor, sin avisar" [022:8][D022].

### Gaps
- No hay mediciones de latencia en el servidor (todavía sin despliegue; PLAN:14 "Pendiente").
- No sé si UGent respondería distinto a un uso académico (TPI) frente al piloto docente de la Visión; ninguna consulta se hizo.

---

## 7. Audiencia y casos de uso definidos por specs y guías

### Takeaway
Las specs de regelabo orbitan al **fonoaudiólogo/investigador** con foco en I+D de pruebas (EFR/ABR, sordera oculta, arquetipos); la docencia aparece como caso de uso secundario en las guías de visualización (CU4 "Herramienta Docente Interactiva") y como rol "estudiante" con menor cupo, pero no hay concepto de cátedra, curso, trabajo práctico, portafolio ni docente como rol. La Visión pone la docencia con cátedras, estudios publicados por estudiantes y suscripciones institucionales en el centro.

### Cited Findings
- Tabla de factibilidad de 16 funcionalidades (9 con análisis completo: mecanismos fisiológicos, datos sintéticos, sordera oculta, optimización de estímulos, validación con datos clínicos, ML, screening neonatal, edad vs trauma, arquetipos; 3 parciales; 4 no factibles) — [spec README:45-62][SPECSREADME]. Actualizado 2026-05-12 — [spec README:5][SPECSREADME].
- Actores: "Fonoaudiólogo" en los CU de arquetipos [REQARQ:13-22][REQARQ]; "Investigador" en mecanismos fisiológicos: "Su usuario es principalmente un investigador (no necesariamente un clínico)" — [mecanismos-fisiologicos (activity)][ACTMEC] (línea 35 del archivo); en ML: "El investigador de ML no interactúa directamente con la simulación" — [entrenamiento-ml activity:34].
- Docencia: `visualizaciones_CU.md` — "Caso de Uso 4: Herramienta Docente Interactiva: Un docente de fonoaudiología utiliza la plataforma en clase..." — [visualizaciones_CU:358-361][VISCU]; el documento de requerimientos de visualizaciones define "REQ-4.1 a REQ-4.7 — Modo docente completo" con "presets docentes" y caché para "escenarios docentes más comunes... para evitar esperas en clase" — [visualizaciones_documentacion_y_requerimientos:430,505,532][VISREQ]. Educación también figura como beneficio de las visualizaciones internas — [visualizaciones_CU:36][VISCU]. Esa guía de visualizaciones es **anterior a la reorganización** (usa `/api/presets/teaching`, microservicios) y no está en el plan de módulos del TPI.
- Presentación: "fonoaudióloga investigadora o educadora" y "Impacto Esperado en la Fonoaudiología y la Investigación Audiológica" — [PRES:81,111-115][PRES]; la hipótesis de la visualización interna es "mejorar su capacidad de análisis clínico y educativo" — [PRES:65][PRES].
- Perfiles de usuario implementados: estudiante / investigador / fonoaudiólogo, solo para cupos y textos — [009:6-9][D009], [RN:11-12][RN].
- Contra-ejemplo en `docs/CC3D/documentation.txt`: laboratorio multiusuario para estudiantes con subdominios por alumno, noVNC y JupyterLab (2026-02-12) — es la única parte del repo diseñada alrededor de estudiantes con entorno propio; AGENTS.md la clasifica como "idea descartada... solo referencia". Su `idea.md` indica "Licencias: Académicas/no-comerciales (ver repos)" para el conjunto CompuCell3D/Verhulst/CoNNear — [CC3D idea:97][CC3D].
- Visión (para contraste): destinatarios "Estudiantes de grado (fonoaudiología, biología, medicina, bioingeniería), docentes y profesionales en formación continua"; roles docente/estudiante/agente; evaluación con portafolio, insignias y certificación; integración con campus virtual (Moodle/LTI) — [VB:98-107][VB]; ingresos por "suscripción institucional más créditos de cómputo" — [VB:286][VB]; clientes de pilotos: "carreras de fonoaudiología y laboratorios de audición" — [VB:291][VB].

### Inferences
- Superposición real: **fonoaudiología**, **investigadores en audición**, **docencia en audiología** y el concepto de **estudio hipótesis → simulación → interpretación**. Divergencias: la Visión es institucional y multi-cátedra; regelabo es individual y de cuenta propia; la Visión parte de estudios "reales publicados" y la autoría compartida (coautoría, CRediT), regelabo prohíbe incluso datos reales (decisión 008) y tiene un único dueño por registro (RN4, el admin ni siquiera ve contenido ajeno — RN:10).
- RN4 (aislamiento total entre usuarios) **choca** con la lógica de "estudios publicados" y "proyectos compartidos entre equipos" de la Visión (VB:92, VB:101-104): la Visión exige compartir, regelabo por diseño no. Resolver exige un modelo de permisos nuevo (curso/grupo/publicación), no solo un rol.
- La relevancia clínica que la Visión cuida con "Exploratorio" y avisos es la misma que regelabo cuida con RN9, pero regelabo además ofrece "Apoyo Diagnóstico por Arquetipos" (título de las specs) y ranking de coincidencias (D007:6: "sugerir posibles patologías con un nivel de confianza"), que la Visión no contempla y que se acerca más a decisión clínica de lo que la Visión permitiría para un modelo no validado.

### Gaps
- No encontré encuestas, entrevistas ni feedback de usuarios reales en ningún archivo. No sé si "fonoaudiólogo" en las specs se validó con profesionales (los diagramas de actividad "del fonoaudiólogo" parecen generados con agentes).

---

## 8. Consistencia interna de los tres documentos de Visión y lo que omiten de la situación real de regelabo

### Takeaway
Los tres documentos son mayormente coherentes entre sí (conteos, etapas, licencias) y reconocen incertidumbres propias, pero tienen **contradicciones menores verificables** (orden de los conteos de fibras, fecha de cabecera, alcance H2 vs Etapa 2, dependencia de Python en AMT) y **omiten por completo** que existe un prototipo funcional sobre Verhulst, que hay un TPI con plazo, y que la Etapa 0 "antes de escribir código de plataforma" ya fue superada por los hechos.

### Cited Findings
**Contradicciones o ambigüedades internas (verificadas)**
1. **Orden de los conteos de fibras de Verhulst.** VB:157: "fibras de baja, media y alta tasa espontánea (por defecto 3, 3 y 13)", VS:60: "(por defecto 3, 3 y 13)" y VS:16: "Variación del número de fibras **L/M/H** en Verhulst (por defecto **13/3/3**)". El código de regelabo fija `nH=13`, `nM=3`, `nL=3` [modelos.py:105-110][MODELOS]. Por lo tanto "13/3/3" es el orden H/M/L; rotulado "L/M/H" en VS:16 es incorrecto (o mal ordenado) y contradice VS:60 y VB:157. El resumen VR no da conteos.
2. **Fecha de cabecera vs contenido del documento base.** VB tiene cabecera "Oct 14, 2026" [VB:3][VB] pero incluye la quinta vía "guiar la morfología" y la sección de morfogénesis, que VS dice haber agregado "el 19 de octubre de 2026, cuando el laboratorio incorporó 'guiar la morfología' como quinta vía" [VS:68][VS]; además las fuentes se declaran "consultadas al Oct 15, 2026" [VB:239][VB] y VS dice que "la búsqueda se hizo el 15 de octubre" [VS:68][VS]. La fecha de VB es anterior a su propio contenido.
3. **H2 "las catorce disciplinas" vs alcance de la Etapa 2.** La tabla de horizontes dice H2 = "Audición completa: las catorce disciplinas del catálogo" [VB:174][VB], pero el alcance de la Etapa 2 (VB:275-276) enumera implantes/audífonos, ototoxicidad/ruido/presbiacusia, puente, oído medio, gEAR, malformaciones y morfogénesis; no menciona vestibular, cribado pediátrico, acúfenos/TPA ni hiperacusia (hiperacusia ni siquiera tuvo búsqueda dedicada: VS:21 y VS:133). Las 14 disciplinas son 14 en las dos tablas (contadas), pero 8 carecen de simulador abierto [VR:73][VR], [VS:3][VS].
4. **Estado de AMT en Octave vs. Python.** VB:61 y VB:319 plantean ejecutar AMT en Octave para "evitar depender de licencias de MATLAB"; VS:108 (tabla de conflictos): "algunos modelos exigen Python con numpy 1.x, scipy y torch" y "Los modelos de Verhulst necesitan Python además de Octave". Es decir, el contenedor "Octave + AMT" de la Etapa 1 no es solo Octave si se incluye Verhulst o torch_amt.
5. **Caso único de Etapa 0 con eslabón no especificado.** VB:254: "respuesta periférica → índice de inteligibilidad con pyclarity o pystoi (MIT)". VS:56 describe pyclarity como simulador de pérdida MSBG/HASPI/HASQI/HAAQI/MBSTOI y pystoi como STOI; ambos trabajan sobre señales de audio. Ningún documento de Visión explica cómo la "respuesta periférica" de bruce2018 (tasas del nervio) se convierte en entrada de esos índices (NeuroVoc, que reconstruye audio desde neurogramas, VS:56, no se nombra en Etapa 0). Hay un salto lógico sin definir. (Mi lectura de qué entradas aceptan STOI/HASPI es de conocimiento general, **no verificada contra las fuentes** en esta sesión.)
6. **Etapa 1: alcance diferente entre documentos.** VB:263-271 lista seis ítems (servicio de simulación con cola y 2 contenedores, repositorio con DOI, artículo interactivo, agente mentor, video automático, piloto docente). VR:99 resume la Etapa 1 como "MVP acotado: resultados precalculados, agente en modo mentor y un piloto con una cátedra", omitiendo repositorio/DOI, video y contenedores (aunque VR:49-52 sí presenta el video por niveles). VS:93 describe la Etapa 1 como "Servicio con cola de trabajos y dos tipos de contenedor... La regeneración entra como módulo didáctico propio" y **no** menciona repositorio, artículo, agente, video ni piloto (es el recorte técnico). Además VB:270 incluye en Etapa 1 "escenarios 'qué pasaría si' de recuperación de células ciliadas o de sinapsis" como cambios de parámetros, mientras que VS:95 sitúa en Etapa 2 la comparación de "escenarios de sinaptopatía y de recuperación sináptica tipo OTOF contra ABR/EFR simulados" tras implementar el puente. Las dos descripciones de qué entra de "reparar/regenerar" en la Etapa 1 no coinciden exactamente.
7. **Verhulst: "no disponible" vs. pieza central del puente.** VS:91 manda "mientras tanto, tratar esos modelos como no disponibles", pero el puente de la Etapa 2 asume que "el modelo mejor parametrizado para recibir ese estado es el que tiene la licencia académica" [VS:64][VS] y propone la alternativa ZBC/BEZ "si la UGent no acepta" [VS:95,141][VS]. Es consistente, pero la Etapa 1 declara cubrir 4 de 5 vías con "pérdida de células ciliadas y de sinapsis" como cambio de parámetros [VB:270][VB] **con modelos AMT** (bruce2018 `lossL/M/H`); los números de fibras de bruce2018 están marcados sin verificar licencia ni compatibilidad con Octave [VB:163][VB].
8. **Incertidumbres declaradas (no son contradicciones, pero son abiertas):** versión de AMT 1.6.0 vs 1.3.0, "más de 50" vs "más de 60" modelos [VB:163][VB], [VS:105-107][VS]; y VR:125-128 lista como abiertos probar AMT en Octave, confirmar licencias y precios.
9. **Suposición de recepción del producto.** VR:103-106 y VB:284-293 fijan modelo de negocio (suscripción institucional + créditos) antes de validar disposición a pagar; VB:326-331 solo valida "valoran publicar y enseñar", no "pagan".
10. **Sin calendario.** En los tres documentos no aparecen fechas futuras ni duraciones por etapa (búsqueda de `meses|semanas|trimestre|cronograma|plazo|2027|2028` solo da coincidencias en "largo plazo", fechas de fuentes y tiempos de simulación). Los "criterios de avance" son cualitativos y "propuestos, a ajustar" [VB:243,247][VB].
11. **Conteos internos: coherentes.** 14 disciplinas (2 tablas), 8 sin simulador, 12 herramientas de morfogénesis, 11 servicios con API, 6 escalas, 4 horizontes, 4 etapas y 7 principios coinciden entre VB, VR y VS (conté filas).

**Qué omiten sobre la situación real de regelabo (verificado por ausencia)**
- Ninguno de los tres menciona regelabo, el TPI, UTN FRRO, FastAPI/React/PostgreSQL, `proposal.md`, ni que ya existe un prototipo operativo basado en Verhulst (0 coincidencias, ver sección 3). El único modelo que los documentos dan por probado headless (Verhulst) es el que ya sirve a un producto en el repo.
- No hay plazo, equipo (3 integrantes), presupuesto (crédito US$200 ≈ 8 meses de DigitalOcean, dominio `.me` 1 año: D011), ni restricción académica (checklist de la cátedra) que condicionan el calendario real.
- No explican el origen: `trajectory.md` documenta que el proyecto nació del interés regenerativo, descartó CompuCell3D y luego se orientó a fonoaudiología con Verhulst [TRAY:3-7][TRAY]; la Visión retoma regeneración y CC3D sin referir esa trayectoria. En particular, la propia nota de CC3D de regelabo describe su flujo "CompuCell3D → parámetros → Verhulst/CoNNear (puente unidireccional)" [CC3D idea:17-25][CC3D], que es el mismo "puente" que la Visión llama "propuesta de diseño, no una práctica publicada" [VB:159][VB]; no hay mención cruzada. Además `idea.md` dice "Licencias: Académicas/no-comerciales" y la Visión dice CompuCell3D = GPL [VB:199][VB]: no queda claro si la nota de regelabo se refiere al conjunto (Verhulst/CoNNear) o a CC3D.
- No incluyen el contexto legal local ya relevado (Leyes 25.326 y 26.529, decisión 008), ni la política de cuentas/cupos.
- No describen los hallazgos de ingeniería que contradicen o matizan (techo OHC, `.mat` bloqueados, 75 s por simulación).

### Inferences
- Los puntos 1-2 son errores editoriales de bajo costo (arreglables sin discusión). Los puntos 3, 5 y 6 son **ambigüedades de alcance** que sí cambiarían decisiones de planificación.
- La omisión del prototipo existente es la brecha más grande de la Visión como documento de decisión: al leerla, un tercero concluiría que no hay nada construido y que "antes de escribir código de plataforma" debe resolverse la licencia. En la realidad hay 33 archivos versionados en `frontend/src`, 21 decisiones, 10 tablas y 7 archivos de test en `backend/tests/`.
- Un lector de la Visión **no sabría** que: (a) hay un TPI con fecha; (b) el modelo "no disponible" ya está embebido y servido; (c) existe un mapeo audiograma→polos validado; (d) el techo del modelo ya se midió; (e) la IA planificada del equipo es RAG/ML y no mentor/copiloto; (f) la CC3D ya fue evaluada y puesta en pausa; (g) hay documentación legada contradictoria; (h) quién es el equipo.

### Gaps
- No tengo acceso al "borrador original" que la Visión menciona ("El borrador original no cubría estos temas": VB:297) ni a los informes completos entregados "aparte".
- No puedo confirmar si las tablas de VS se basan en fuentes verificadas (es un informe de investigación; no verifiqué enlaces).

---

## 9. Contexto adicional: carpeta `backend/services/`, documentación legada y CC3D

### Takeaway
La carpeta sin seguimiento `backend/services/` **no la explica ningún documento de planificación**: es un resto de la estructura de microservicios eliminada en el commit `313f9fd`. Además hay al menos seis documentos legados que contradicen las decisiones vigentes y que un lector de la Visión (o un evaluador) puede confundir con el estado actual.

### Cited Findings
- `git status` al inicio: `?? backend/services/`. Contiene 49 archivos: `__pycache__` (core-service y simulation-service), `Poles.mat` de unos 33 perfiles bajo `simulation-service/src/Verhulst/data/Poles/*`, y un archivo en `c_lib/`. El commit `313f9fd` ("Reorganizar el backend en 3 capas") borró del árbol versionado `backend/services/core-service`, `llm-service`, etc. (`git show --stat`). Ninguno de AGENTS.md, MEMORY.md, CLAUDE.md, proposal.md, README.md, plan, RN, decisiones ni `docs/arquitectura.md` menciona `backend/services`, `core-service`, `llm-service` o `simulation-service` (grep sin resultados en esos archivos). El plan solo dice, para el paso 1: "Sacar CC3D y los microservicios" — [PLAN:26][PLAN].
- Los `Poles.mat` sin versionar son relevantes: MEMORY.md dice que no se deben "copiar archivos del repo oficial de Verhulst" por la licencia [MEM:31][MEM] y el plan que no se traen los `.mat` de `OHC_ind` [PLAN:69][PLAN]; no sé si los `Poles.mat` residuales son los mismos archivos o distintos (ver Gaps).
- Documentos legados que contradicen las decisiones vigentes (verificado por lectura): `proposal.md` (Supabase Auth/Storage, Celery+Redis, Dask, Ray, LangChain/ChromaDB, DeepSeek/Qwen, Zotero, DVC+MinIO; "dos grandes etapas"; CompuCell3D como futuro) — [PROP:29-43,46-65][PROP] (última modificación 2026-08-02); `README.md` (SOA, `backend/src/*`, Supabase, Celery) — [README:10-16,45][README]; `docs/arquitectura.md` (8 módulos incluidos Supabase Auth/Storage, Celery+Redis, ChromaDB, DeepSeek/Qwen) — [arquitectura.md:9-19][ARQ]; `docs/prototype/architectureAndTechnologies.md` (SOA, microservicios); `docs/guias/sdd_methodology.md` (estructura `backend/src/api|db|simulation|llm|services`); `docs/specs/functionalitiesOverview.md:100` (arquetipos con `pgvector` en Supabase) y `requerimientos-*.md` (microservicios `core-service`/`llm-service`, "arquitectura de Facundo", ChromaDB, Fase 2 "cuya implementación está postergada indefinidamente" — [REQARQ:7][REQARQ]). MEMORY.md señala solo `proposal.md` como desactualizado [MEM:37][MEM]; el plan menciona además `docs/arquitectura.md` en el paso 7 [PLAN:34][PLAN].
- Tres vocabularios de "fases" conviven: proposal "Fase 1/Fase 2" [PROP:46-65]; plan "Fase 1/2/3/Futuro" [PLAN:11-16]; requerimientos "[FASE 1]/[FASE 2 — FUTURA]" [REQARQ:7]; Visión "Etapa 0-3" y "H1-H4". Ninguna tabla de equivalencias existe.
- Decisión 007 referencia `docs/ejemplos/abr/` para ABR de prueba, carpeta que **no existe** en el árbol [007:12][D007] (verificado con `ls`).
- El plan de trabajo no incluye la decisión 022 ni el trabajo de perfiles auditivos (cerrado el 2026-10-19) como paso; MEMORY.md dice "Último commit `8ec683b`" cuando HEAD está tres commits más adelante — [MEM:14][MEM].
- CC3D: `docs/CC3D/` (Dockerfile, compose multi-estudiante con Traefik/noVNC/Jupyter, idea.md, documentation.txt) fue ordenada el 2026-05-07 y movida a `docs/` el 2026-10-14 (`313f9fd`); AGENTS.md: "idea descartada de CompuCell3D (solo referencia)". La Visión pone CompuCell3D en H3/Etapa 3 y en la tabla de morfogénesis como herramienta GPL con "Aplicación al oído verificada: No" [VB:199][VB], [VS:72][VS]; la nota de regelabo afirma que el flujo CC3D→Verhulst es "técnicamente posible y novedosa (no existe integración publicada)" [CC3D idea:64][CC3D].

### Inferences
- `backend/services/` probablemente quedó como residuo local de un cambio de rama/reorganización; no tiene valor documental. Conviene verificar con Valentino (autor de `313f9fd`) antes de borrarlo, porque podría contener los únicos `.mat` locales que hoy están "bloqueados" por la política de licencia (hipótesis).
- La coexistencia de documentación contradictoria hace que, para cualquier decisión "modificar la Visión vs redirigir regelabo", la fuente de verdad del estado real sean únicamente AGENTS.md, MEMORY.md, el plan, RN y las decisiones; el resto debe tratarse como histórico.

### Gaps
- No inspeccioné el contenido de los `Poles.mat` de `backend/services` ni si coinciden con los archivos del repo oficial.
- No verifiqué quién creó esa carpeta ni cuándo (no está en git).

---

## 10. Síntesis para la decisión: modificar los documentos de Visión o reorientar regelabo

### Takeaway
Las dos piezas **no son incompatibles en el largo plazo pero sí en la secuencia y el calendario**. La Visión asume una Etapa 0 de validación sin plataforma, con AMT/Octave y sin Verhulst; regelabo es una plataforma ya construida sobre Verhulst con fecha de entrega académica a fin de 2026. Lo que hoy entra en conflicto no es el destino sino qué se hace en las próximas ~10 semanas y qué se afirma sobre el pasado. Esto es una lectura mía; la regla del repo exige consultar antes de decidir.

### Cited Findings
- Regla del repo: "Nunca tomar una decisión... por tu cuenta. Siempre consultar, dar opciones y justificación" — [AGENTS.md "Reglas"][AGENTS]; "No re-litigar estas decisiones: se cambian con una decisión nueva en `docs/decisiones/`" — [MEM:25][MEM].
- Puntos de fricción por categoría (cada uno con su evidencia arriba):
  - **Secuencia/alcance**: plataforma pospuesta en Etapa 0 (VB:259) vs plataforma construida; Etapa 1 lista cola+caché que regelabo ya tiene (sec. 4).
  - **Tecnología**: AMT/Octave/contenedores (VB:252, 264) vs Python ≥3.14 monolito sin Octave (PYPROJECT, D002); esquema acoplado a Verhulst (TABLAS) vs principio 7.
  - **Licencias**: "tratar Verhulst como no disponible" (VS:91) vs dependencia productiva con código UGent en repo público y `.mat` bloqueados (PLAN:69).
  - **Público**: cátedras e instituciones, estudios compartidos (VB:98-107) vs usuarios aislados por RN4 y evaluación académica del TPI.
  - **Calendario**: sin fechas (Visión) vs "fin de 2026" (MEM:13).
  - **IA**: mentor/copiloto/video (VB:83-92) vs RAG de papers + ML (PROP:39-43, D001).
  - **Dominio**: regeneración/CC3D (H2-H3) vs "suspensión del enfoque regenerativo" (TRAY:7).

### Inferences (opciones y tradeoffs; no son decisiones)
1. **Modificar la Visión (reconocer el prototipo y reordenar la Etapa 0).** Agregar a los documentos de Visión: la existencia de regelabo/TPI y su plazo; reclasificar Verhulst como "prototipo bajo licencia académica (uso TPI)" en vez de "no disponible"; mover "plataforma propia" fuera del listado "se pospone" de Etapa 0 o crear una Etapa "-1/0a" que describa lo ya hecho; corregir las contradicciones de la sección 8 (fibras, fecha, H2 vs Etapa 2, Python en AMT); explicitar el salto bruce2018→pyclarity. Ventajas: no toca el TPI, cuesta poco, mejora honestidad del documento. Costos: la Visión pierde parte de su claridad de "validar antes de construir" y obliga a justificar por qué la compuerta legal sigue pendiente.
2. **Redirigir regelabo hacia la Etapa 0 (AMT/Octave, bruce2018, caso único).** Ventajas: alinea con la Visión y baja el riesgo de licencia. Costos: choca con la entrega del TPI (3 capas, módulos pendientes, CI, despliegue) y con 21 decisiones aceptadas; el equipo de 3 tiene reparto fijo; requiere decisión nueva en `docs/decisiones/` y compromiso de los compañeros; además la cátedra no tiene por qué aceptar un cambio de modelo. Solo viable como **trabajo posterior al TPI** o como un paralelo mínimo (spike).
3. **Híbrido por fases (propuesta de ordenamiento).** Cerrar el TPI como "Etapa 1 parcial sobre Verhulst" sin tocar el alcance; ejecutar en paralelo y fuera del camino crítico las compuertas de bajo costo de la Etapa 0 (consulta a UGent, `amt_info`, un spike de bruce2018 en Octave en contenedor); y recién después decidir si migrar el motor. Ventajas: protege el calendario y avanza sobre lo que la Visión llama "mayor incertidumbre técnica". Costos: el esquema acoplado a Verhulst puede consolidarse si los módulos A/B siguen copiando el patrón de Casos antes de generalizar `simulacion`; hay que decidir si generalizar el esquema (modelo+versión+parámetros) ahora o después.
4. **Independiente de cuál se elija**, los riesgos concretos a tratar pronto: (a) licencia UGent con repo público (decisión nueva en `docs/decisiones/`); (b) columna de modelo/versión en `simulacion`/`resultado_simulacion` (decisión 021 libre); (c) alinear/archivar documentación legada; (d) mantener `proposal.md` (la cátedra lo exige) coherente con el estado real.

### Gaps
- No tengo información sobre las prioridades personales/institucionales de Facundo (autor de la Visión) frente a las del equipo del TPI.
- La conveniencia legal de cualquiera de las opciones requiere asesoría; no la emito.

---

## Leyenda de fuentes (rutas relativas a la raíz del repo)

[VB]: docs/Vision/Laboratorio%20computacional%20de%20ciencia%20abierta%20documento%20base%20por%20etapas.md
[VR]: docs/Vision/Laboratorio%20computacional%20abierto%20resumen%20del%20proyecto.md
[VS]: docs/Vision/Simuladores%20para%20disciplinas%20de%20audici%C3%B3n.md
[PROP]: proposal.md
[MEM]: MEMORY.md
[AGENTS]: AGENTS.md
[PLAN]: docs/plan-de-trabajo.md
[RN]: docs/reglas-de-negocio.md
[DREADME]: docs/decisiones/README.md
[D001]: docs/decisiones/001-alcance-del-tpi.md
[D002]: docs/decisiones/002-arquitectura-en-3-capas.md
[D003]: docs/decisiones/003-base-de-datos.md
[D004]: docs/decisiones/004-autenticacion-propia.md
[D005]: docs/decisiones/005-cola-de-simulaciones.md
[D006]: docs/decisiones/006-cache-de-resultados.md
[D007]: docs/decisiones/007-arquetipos-y-similitud.md
[D008]: docs/decisiones/008-caso-sin-datos-personales.md
[D009]: docs/decisiones/009-roles-cupos-y-limites.md
[D010]: docs/decisiones/010-esquema-de-datos.md
[D011]: docs/decisiones/011-infraestructura.md
[D012]: docs/decisiones/012-frontend.md
[D013]: docs/decisiones/013-sesion-en-el-servidor.md
[D014]: docs/decisiones/014-convenciones-de-la-api.md
[D015]: docs/decisiones/015-interfaz-de-autenticacion.md
[D016]: docs/decisiones/016-coleccion-de-bruno.md
[D017]: docs/decisiones/017-paginacion-por-cursor.md
[D018]: docs/decisiones/018-cambio-de-contrasena.md
[D019]: docs/decisiones/019-endpoints-del-prototipo-con-sesion.md
[D020]: docs/decisiones/020-cola-de-simulaciones-en-detalle.md
[D022]: docs/decisiones/022-perfiles-auditivos.md
[FO]: docs/specs/functionalitiesOverview.md
[SPECSREADME]: docs/specs/README.md
[REQARQ]: docs/specs/requerimientos-diagnostico-arquetipos.md
[ACTMEC]: docs/specs/activity-diagrams/mecanismos-fisiologicos.md
[PMIT]: docs/specs/Plan%20de%20Mitigaci%C3%B3n%20de%20Cuellos%20de%20Botella.md
[VISCU]: docs/guias/visualizaciones_CU.md
[VISREQ]: docs/guias/visualizaciones_documentacion_y_requerimientos.md
[TRAY]: docs/trajectory.md
[PRES]: docs/presentation_data.md
[CC3D]: docs/CC3D/idea.md
[ARQ]: docs/arquitectura.md
[README]: README.md
[TABLAS]: backend/datos/tablas.py
[MOTOR]: backend/simulacion/motor.py
[MODELOS]: backend/controller/modelos.py
[PYPROJECT]: pyproject.toml
[COMPOSE]: docker-compose.yml
