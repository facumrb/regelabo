# Inventario técnico del código de regelabo y alineación con la Visión

Alcance: lectura de solo lectura del repo (HEAD `ed5f207`, rama `main`) contra los tres documentos de `docs/Vision/` (abreviados abajo: **Base** = "documento base por etapas", **Resumen**, **Simuladores**). Las "fuentes" son rutas de archivo con línea (relativas a la raíz del repo). Hecho verificado = visto en el código o en git. Inferencia = mi lectura, marcada como tal. No se ejecutó nada (ni app, ni tests, ni DB).

Convención de rutas: `tablas.py` = `backend/datos/tablas.py`; `motor.py` = `backend/simulacion/motor.py`; `ctrl/simulaciones.py` = `backend/controller/simulaciones.py`; etc.

---

## 1. Qué está implementado hoy, módulo por módulo

### Takeaway
regelabo es un monolito FastAPI + React en 3 capas, mono-modelo (Verhulst 2018): audiograma → perfil de polos → simulación en cola (worker + caché por huella) → EFR/ABR/FFT. Hay 10 tablas, pero 3 de ellas (`arquetipo`, `registro_abr`, `comparacion`) no tienen ningún código que las use todavía. No hay nada del lado "estudio / artículo / video / agente / docencia".

### Cited Findings

**Arquitectura y capas**
- `app.py` en la raíz crea la app con `backend.views.crear_app()`; 5 routers bajo `/api`: autenticación, casos, simulacion (health/profiles), simulaciones (cola), audiogramas — `backend/views/__init__.py:30-34`. Dependencias en un solo sentido views → controller → datos / simulacion — `AGENTS.md` (sección Arquitectura), `docs/decisiones/002-arquitectura-en-3-capas.md:8-16`.
- El diseño de 3 capas con nombres fijos viene de un checklist de la cátedra (TPI de Soporte, UTN FRRO); el prototipo previo eran 3 microservicios (core, simulation, llm) y se descartó "para que se vea como 3 capas en la corrección" — `docs/decisiones/002-arquitectura-en-3-capas.md:5,14-15`.

**Endpoints (todos bajo `/api`)**
- Auth: `POST /auth/registro|login|logout|contrasena`, `GET /auth/yo` — `backend/views/autenticacion.py:21,27,38,44,52`.
- Casos: CRUD `GET|POST /casos`, `GET|PUT|DELETE /casos/{id}` — `backend/views/casos.py:18-39`.
- Simulaciones: `POST /simulaciones` (202, solo encola), `GET /simulaciones` (paginado por cursor), `GET /simulaciones/{id}` — `backend/views/simulaciones.py:18-32`.
- Perfiles/estado: `GET /health` (sin sesión; informa `c_solver_available`), `GET /profiles`, `GET /profiles/{nombre}` — `backend/views/simulacion.py:19,25,39`.
- Audiogramas: `POST /audiogram/upload` (CSV/TXT) y `POST /audiogram/manual` — `backend/views/audiogramas.py:18,42`. No se persisten como entidad: devuelven un `AudiogramResponse` y generan una carpeta de perfil en disco (ver abajo).

**Las 10 tablas (`backend/datos/tablas.py`)**
1. `usuario` (:40-52): email, hash argon2, nombre, `tipo_perfil` ∈ {estudiante, investigador, fonoaudiologo}, `es_admin`, `aviso_aceptado_en` (RN9), intentos/bloqueo.
2. `sesion` (:55-60): hash SHA-256 del token de cookie, expiración.
3. `caso` (:63-71): alias, edad, sexo, notas, `borrado_en` (borrado lógico). Es un "caso de estudio" sin datos personales (decisión 008).
4. `audiograma` (:74-84): `caso_id`, origen (manual/archivo), `pta_db`, gravedad (normal/leve/moderada/severa), patrón (plano/pendiente), `perfil` (nombre de carpeta del perfil de polos generado).
5. `punto_audiograma` (:87-93): frecuencia_hz, perdida_db; único por (audiograma, frecuencia) (RN1).
6. `resultado_simulacion` (:96-107): **huella única** SHA-256 + `efr_uv`, `armonicos`, `espectro`, `ondas`, `metricas` (JSONB), `duracion_s`. Compartido entre simulaciones con la misma huella (RN10).
7. `simulacion` (:110-130): usuario, caso opcional, `perfil`, `frecuencia_portadora_hz`, `nivel_db_spl`, `frecuencia_modulacion_hz`, `n_h`, `n_m`, `n_l`, `huella`, `estado` ∈ {en_cola, ejecutando, completada, error}, `resultado_id`, `mensaje_error`, `iniciada_en`, `finalizada_en`.
8. `arquetipo` (:133-145): nombre, descripción, perfil, n_h/n_m/n_l, estímulo, ondas, métricas (biblioteca de patrones ABR simulados, decisión 007).
9. `registro_abr` (:148-154): ABR cargado por el usuario (señal normalizada) ligado a un caso.
10. `comparacion` (:157-168): top-3 de arquetipos con copia (RN8), `concluyente` (RN7), arquetipo elegido, `hipotesis` (texto libre "nunca diagnóstico").
- Hecho: `arquetipo`, `registro_abr`, `comparacion` solo aparecen en `tablas.py`, la migración inicial, el TRUNCATE de `backend/tests/conftest.py:50` y una tarjeta "Próximamente" en el frontend (`frontend/src/pages/Bienvenida.tsx:20-24`). Un `rg` sobre `backend/` y `frontend/src` no encontró controller, view ni datos que las lean o escriban.
- Hecho: `docs/decisiones/010-esquema-de-datos.md:7-8` confirma que el equipo creó el esquema completo "de una vez" y que la décima tabla (`sesion`) llegó con la autenticación.

**Controller (`backend/controller/`)**
- `simulaciones.py`: validación RN3 (:31-53), huella (:56-67), cupos y tope de cola RN5 (:86-96), caché RN10 (:84-86), `procesar_siguiente` / `recuperar_interrumpidas` para el worker (:123-155).
- `simulacion.py` (`SimulationService.execute_simulation`, :38-133): carga polos, llama `motor.ejecutar_modelo`, calcula EFR = suma de los primeros 4 armónicos de la FFT de `w1+w3+w5` (:70, :83-87), recorta el espectro a 0-1000 Hz (:97-101) y decima las ondas a <800 puntos (:104-113).
- `perfiles.py`: catálogo de perfiles con etiquetas para el profesional (:144-151), techo del modelo (:43-51), generación de polos desde un audiograma (:65-70), perfil personalizado `Custom_<hash>` (:164-171). Clasificación PTA 500/1k/2k/4k y grados RN2 (:26-27, :83-97).
- `audiogramas.py`: parseo CSV/TXT (:18-48), patrón plano/pendiente por RN2 (:67-72), llama a `perfiles.crear_personalizado` (:77).
- `autenticacion.py`, `casos.py`, `errores.py`, `modelos.py` (objetos Pydantic de negocio).
- `backend/comandos/`: `crear_admin.py`, `resetear_contrasena.py` (scripts de administración, solo llaman al controller).

**Datos (`backend/datos/`)**
- `casos.py`, `usuarios.py`, `sesiones.py`, `simulaciones.py` (cola con `FOR UPDATE SKIP LOCKED`, :126-139; `ON CONFLICT DO NOTHING` en el resultado, :63-72), `conexion.py` (`transaccion()`), migraciones Alembic (3 versiones).
- `perfiles.py`: **persistencia en disco**, no en DB: `simulacion/verhulst/data/Poles/<perfil>/StartingPoles.dat` (+ `profile.txt`, `perfil.json` en los personalizados) — `backend/datos/perfiles.py:4-8,17-21,66-72`.

**Worker y configuración**
- `worker.py:21-30`: loop infinito, `recuperar_interrumpidas()` + `procesar_siguiente()`, pausa de 2 s sin trabajo; una simulación a la vez por proceso (~1,1 GB RAM y 1 núcleo, `worker.py:6`).
- `backend/configuracion.py:24-29`: cupos simultáneos por tipo de perfil (estudiante 1, investigador 3, fonoaudiólogo 3), cupo por hora (10/30/30), `TOPE_COLA=20`, `SIMULACION_MINUTOS_MAX=5`.
- `pyproject.toml:7`: `requires-python = ">=3.14"`; dependencias: fastapi, numpy, scipy, matplotlib, sqlalchemy, psycopg, alembic, argon2, slowapi (:8-17). Hay 7 archivos de tests en `backend/tests/` (PostgreSQL real, base `regelabo_test`).

**Qué es un "caso", una "simulación", un "perfil"**
- **Caso**: carpeta de trabajo personal del usuario con alias/edad/sexo/notas, sin datos que identifiquen a nadie; agrupa audiogramas y simulaciones; borrado lógico — `tablas.py:63-71`, `ctrl/modelos.py:61-74`, `docs/decisiones/008-caso-sin-datos-personales.md`.
- **Simulación**: un pedido de ejecución del modelo con 7 parámetros fijos (portadora, nivel SPL, f_mod, nH, nM, nL, perfil) que pasa por una cola con estados; opcionalmente ligada a un caso — `ctrl/modelos.py:83-110,194-209`, `tablas.py:110-130`.
- **Perfil**: vector de 1001 polos de Shera (1 de oído medio + 1000 secciones de la membrana basilar) que codifica la pérdida de células ciliadas externas; 33 carpetas en `verhulst/data/Poles/` (22 visibles tras filtrar duplicados) + `Custom_*` generados — `backend/datos/perfiles.py:4-8`, `backend/controller/perfiles.py:31-35`, `docs/decisiones/022-perfiles-auditivos.md:6`.

**Salidas del modelo**
- ABR ondas I, III y V (`w1`, `w3`, `w5`), `efr_wave = w1+w3+w5`, valor EFR (µV) = suma de amplitudes de los armónicos 1-4 de `f_mod`, espectro FFT 0-1000 Hz — `ctrl/simulacion.py:67-113`, `ctrl/modelos.py:117-147`. Los tipos del frontend replican esto: `frontend/src/services/tiposSimulacion.ts:3-40`.
- Hecho: `resultado_simulacion.metricas` se guarda siempre como `{}` — `backend/datos/simulaciones.py:69`; las métricas "latencias y amplitudes de W1, W3, W5" que el comentario de la columna promete (`tablas.py:106`) no se calculan hoy. MEMORY.md:37 lista "ventanas de latencia y amplitud de las ondas" como pendiente.

**Frontend (`frontend/src/`, React 18 + Vite + Tailwind + Plotly, TypeScript)**
- Rutas: `/login`, `/registro`, `/cuenta`, `/casos`, `/casos/nuevo`, `/casos/:id`, `/simulaciones`, `/simulaciones/:id`; el resto (`*`, o sea `/`) es el simulador del prototipo con pestañas "Simulación Biológica (EFR / ABR)" y audiograma, o `Bienvenida` si no hay sesión — `frontend/src/App.tsx:174-183`.
- Páginas: `Bienvenida`, `Login`, `Registro`, `MiCuenta`, `casos/{MisCasos,NuevoCaso,FichaCaso,FormularioCaso}`, `simulaciones/{Historial,DetalleSimulacion}`. Componentes del simulador: `SimulationControls`, `AudiogramManager`, `ResultsSummary`, `PlotsPanel`, `CurvasPerfil`, `PerfilSimulado`, `PanelPruebas` (solo desarrollo).
- Un "botón JSON" exporta el resultado (`ResultsSummary.tsx:26-34`), sin modelo/versión/semilla.

### Inferences
- El nivel de madurez es el de un "sprint 0" de TPI: autenticación, casos, cola y caché están completos y con tests; el dominio científico (arquetipos, comparación, ABR cargado) está esquematizado pero sin lógica. MEMORY.md:14-16 lo confirma (pasos 1-5 hechos; CI y documentación pendientes).
- Las 3 tablas de arquetipos son la única parte del esquema que anticipa "biblioteca de referencia contra la que comparar", y es un concepto de screening/ABR, no del "estudio estructurado" de la Visión.

### Gaps
- No leí el contenido de `autenticacion.py`, `datos/casos.py`, ni los tests más allá de nombres/cantidad; no son relevantes para la decisión.
- `AGENTS.md` está **desactualizado** respecto del código en un punto: dice que `Custom_<nombre>` se genera "copiando los polos del perfil base más cercano; todavía no usa OHC_ind", pero `controller/perfiles.py:9-11,65-70` y la decisión 022 (`docs/decisiones/022-perfiles-auditivos.md:12`) generan los polos interpolando una tabla dB HL→polo de los perfiles planos (no copian). También MEMORY.md:14 cita un "último commit 8ec683b" anterior al HEAD actual. Lo señalo porque quien lea AGENTS.md se llevaría una imagen más pobre del flujo de audiograma.

---

## 2. Motor de simulación: licencia, acoplamiento a Verhulst y costo de sumar o cambiar de motor

### Takeaway
El código Verhulst está copiado en el repo bajo la **UGent Academic License** (solo investigación académica no comercial; prohíbe distribuir o sublicenciar sin autorización escrita), mientras el repo se publica con LICENSE MIT. `motor.py` es una frontera real de *importación*, pero tiene forma de Verhulst (firma, constantes, salida w1/w3/w5); no hay interfaz de motor ni identificador de motor en la DB. Sumar un segundo motor Python es un trabajo moderado; sumar uno en Octave/contenedor exige construir la capa de ejecución que hoy no existe.

### Cited Findings

**Licencia y atribución**
- `backend/simulacion/verhulst/license.txt:1` abre con "UGent Academic License"; el §2 (:14) otorga licencia para usar el Work y preparar obras derivadas "for non-commercial academic research purposes" y dice textualmente "The Licensee shall not distribute or sub-license the Work to third parties without the prior written authorization of the Licensor". El §3 (:17-19) obliga al licenciatario a otorgar a UGent una licencia **exclusiva**, perpetua e irrevocable sobre las obras derivadas para uso comercial. El §4(c) (:25) exige conservar el aviso "© copyright 2017 Ghent University – Universiteit Gent, all rights reserved; ... subject to an UGent Academic License" en cualquier obra derivada distribuida; el §4(b) (:24) exige avisar en los archivos modificados.
- `backend/simulacion/verhulst/README.md:12`: "The model code and interface was written by Alessandro Altoè and Sarah Verhulst (copyright 2012,2014,2015,2016,2018) and is licensed under the UGent acadamic license". Versión 1.2 (:3-8); scripts Python actualizados por Brent Nissens en noviembre de 2025 (:14, :52).
- Atribución dentro del código: `src/model2018.py:1-13` ("Convertido desde MATLAB por Brent Nissens / Basado en el trabajo original de Alessandro Altoè y Sarah Verhulst"); `matlab/model2018.m:67-77` repite el aviso de licencia UGent.
- El repo raíz es **MIT**, "Copyright (c) 2026 Facundo Ramírez" — `LICENSE:1-3`. No encontré un NOTICE ni mención de la licencia UGent fuera de `verhulst/` y `MEMORY.md` (el `README.md` raíz solo dice "modelos de simulación biológica (Verhulst et al.)", `README.md:3`, y apunta a un repo "AleF-dot/verhulst2018-wrapper", :6).
- El propio equipo marca la licencia como problema abierto: "Pedir permiso antes de copiar archivos del repo oficial de Verhulst (licencia UGent sin resolver)" — `MEMORY.md:31`; "licencia de Verhulst (bloquea `OHC_ind`)" — `MEMORY.md:37`; la decisión 022 descarta "Esperar a `OHC_ind`: está bloqueado por la licencia" y evita los `.mat` — `docs/decisiones/022-perfiles-auditivos.md:12,31`.
- La Visión coincide: "Verhulst: solo académica" — Base:126; "Inutilizable en un servicio comercial sin acuerdo escrito" — Base:147; `license.txt` §2/§3 citados en Simuladores:40.
- Hecho: el código copiado no es el upstream puro. `src/model2018.py` pasó de 357 líneas (en `backend/services/simulation-service/...`) a 516 líneas en el commit `313f9fd` (autor Valentino Ortiz, `git diff 4f347ed 313f9fd`); hay `examples/orch_test.py`, `quick_plot_test.py`, `src/utils/plot_orchestrator.py` y `diagnostic_plots.py` que son trabajo del equipo (git log: "Modificaciones para lograr visualizaciones internas", "Primera versión del generador de gráficas en tiempo real"). Es decir, el repo contiene **obras derivadas** del Work, no solo una copia.

**Acoplamiento a Verhulst (qué es específico del modelo)**
- `motor.py:22-23` importa `model2018` y `get_RAM_stims` como módulos top-level, manipulando `sys.path` (:16-20). Es el único lugar que lo hace (docstring :4-7; coherente con `AGENTS.md`).
- Firma del adaptador: `ejecutar_modelo(polos, frecuencia_portadora, nivel_db_spl, frecuencia_modulacion, n_h, n_m, n_l) -> SalidaModelo(fs, w1, w3, w5)` — `motor.py:36-43,55-63`. Es una función concreta, no una interfaz/Protocol; no hay registro de motores, ni `engine_id`, ni parámetros genéricos (dict/JSON).
- La llamada interna fija todo lo demás: `fc='abr'`, `irregularities=1`, `storeflag='evihmlbw'`, `IrrPct=0.05`, `non_linear_type='vel'`, `subject=SEMILLA` — `motor.py:80-95`.
- El controller importa directamente `SEMILLA, VERSION_MODELO` de `motor.py` (`ctrl/simulaciones.py:25`) y `SimulationService` llama a `motor.ejecutar_modelo` con los 7 parámetros (`ctrl/simulacion.py:57-65`), calcula EFR sumando `w1+w3+w5` (:70) — lógica de post-proceso que asume la salida ABR del modelo.
- El esquema de la DB codifica los parámetros del motor como columnas: `frecuencia_portadora_hz`, `nivel_db_spl`, `frecuencia_modulacion_hz`, `n_h`, `n_m`, `n_l`, `perfil` — `tablas.py:114-121`; y las salidas como columnas/JSONB específicas: `efr_uv`, `armonicos`, `espectro`, `ondas` — `tablas.py:102-106`. El contrato de la API replica lo mismo — `ctrl/modelos.py:83-110,139-147`, `frontend/src/services/tiposSimulacion.ts:3-40`.
- Perfiles: los polos de Shera son concepto Verhulst; viven en `verhulst/data/Poles/` (`datos/perfiles.py:17-21`); los grados/techos, la tabla `NIVELES_PLANOS = [0..35]` y el reemplazo de `OHC_ind` son específicos de este modelo — `controller/perfiles.py:25-35,43-51,65-70`. El techo del modelo depende de la frecuencia (~20 dB HL en 250 Hz, ~35 dB en 4-8 kHz) y el modelo "solo representa la pérdida de las células ciliadas externas" — `controller/perfiles.py:4-8`, `docs/decisiones/022-perfiles-auditivos.md:8`.
- `OHC_ind` (que convierte audiograma→polos oficialmente) **no se usa**; el audiograma pasa por una tabla propia aproximada (error medio 0,18 dB, máx 4,7 dB según la decisión 022) — `controller/perfiles.py:9-11`; `docs/decisiones/022-perfiles-auditivos.md:12`. El propio `verhulst/src/utils/OHC_ind.py` está en el repo pero necesita `.mat` (`OHC_ind.py:30-32`) que están excluidos por `verhulst/.gitignore:1` (`*.mat`).
- Fibras: nH/nM/nL son parámetros del usuario con rangos propios 0-30 / 0-15 / 0-15 (`ctrl/simulaciones.py:35-37`), "los del prototipo", no del modelo.
- Efecto lateral relevante para concurrencia: el adaptador hace `os.chdir` a una carpeta temporal porque el modelo escribe `*_0.npz` en el cwd, y reconoce que `chdir` es global del proceso (`motor.py:73-95`); por eso un worker corre una simulación por vez. Además `model2018` arranca un `PlotOrchestrator` (hilo que sondea la carpeta cada 0,5 s y genera PNGs) en cada llamada, incluso en modo de un canal — `verhulst/src/model2018.py:458-468`, `utils/plot_orchestrator.py:31-45,144`.
- Dependencia de plataforma: el solver C `tridiag.so/.dll` debe compilarse (`verhulst/src/c_lib/build.sh|bat`); si no carga, el modelo cae a un fallback en Python (`core/cochlear_model2018.py:57-72`). `GET /health` informa cuál se usa (`views/simulacion.py:19-22`, `motor.py:46-52`).

**Costo de sumar/cambiar motor (hechos que lo determinan)**
- Para el despacho hoy hay exactamente un camino: `procesar_siguiente` llama a `SimulationService.execute_simulation(simulacion.parametros)` (`ctrl/simulaciones.py:133`). No hay columna de motor/servicio en `simulacion` (`tablas.py:110-130`).
- La huella incluye `SEMILLA` y `VERSION_MODELO` globales (`ctrl/simulaciones.py:61-66`), no por motor.
- `requires-python = ">=3.14"` (`pyproject.toml:7`), mientras que el Simuladores doc consigna que Verhulst corrió en Python 3.13, `cochlea` no instala en 3.13 y torch_amt podría exigir ≥3.14 (Simuladores:36,109) — es decir, hay un compromiso de versión de Python con consecuencias para otros paquetes.

### Inferences
- **¿`motor.py` es una frontera real o con forma de Verhulst?** Ambas cosas: es real como aislamiento de importación (el resto del backend no toca `model2018`/`core`/`utils`), pero su contrato (`polos`, `n_h/n_m/n_l`, `w1/w3/w5`) es el de Verhulst. Un segundo motor no cabe sin cambiar esa firma, el esquema `simulacion`/`resultado_simulacion`, `ParametrosSimulacion`, la huella y los tipos del frontend. La decisión de "motor genérico" no está tomada en ningún documento que yo haya visto (no busqué a fondo `docs/arquitectura.md`).
- **Sumar un motor Python permisivo (p. ej. pyclarity MSBG, pystoi):** esfuerzo medio. Se puede escribir otro módulo tipo `motor_msbg.py` en el mismo estilo, pero las entradas (audiograma + señal de audio) y salidas (audio degradado, índice de inteligibilidad) no son EFR/ABR/FFT: habría que parametrizar `Simulacion` (`parametros` JSON + `motor` + `version_motor`) y `ResultadoSimulacion` (JSON de salida por tipo), y generalizar `SimulationResponse` y el frontend. pyclarity 0.9.0 declara Python ≥3.11 (Simuladores:56), compatible con el `>=3.14` del proyecto (no verifiqué que sus dependencias lo soporten en 3.14).
- **Sumar un motor en Octave (AMT `bruce2018`):** esfuerzo alto. Hoy no hay ejecución de subprocesos/contenedores ni imagen Docker del worker (el `docker-compose.yml` solo levanta la DB según AGENTS.md, no verificado leyendo el archivo); habría que construir el adaptador de proceso/contenedor, empaquetar Octave+AMT y manejar licencias por modelo (Base:143,319). Ese adaptador es precisamente lo que la Visión llama "capa única de trabajos con adaptadores".
- **Riesgo legal (inferencia, requiere asesoría):** publicar un repo MIT que incluye código UGent y obras derivadas contradice, en la lectura literal del §2 y §4 de la licencia, la redistribución a terceros sin permiso escrito; el equipo ya lo sabe (MEMORY.md:31,37). Para un TPI académico no comercial el uso propio es plausible; para la plataforma comercial de la Visión es el bloqueo central que la Visión ya reconoce (Base:147; Resumen:75).

### Gaps
- No verifiqué si los archivos modificados por el equipo llevan el aviso del §4(b) de "modified files" (no auditoría línea a línea).
- No verifiqué si el repo en GitHub es público (solo vi remotos: `fork` → `giani1233/regelaboForked`, y merges que mencionan `facumrb/regelabo`).
- No leí `docs/arquitectura.md` ni `proposal.md` (marcado como desactualizado en MEMORY.md:37).

---

## 3. "Plataforma agnóstica de dominio": qué es específico de audición y qué es genérico

### Takeaway
La infraestructura (usuarios, sesiones, cupos, cola, caché por huella, paginación, caso como contenedor) es genérica en su *forma*; pero el esquema de simulación, la API, el dominio de Casos (con audiogramas/PTA), los arquetipos, los textos y toda la UI están cableados a audición y a un único modelo. Hoy el principio 7 de la Visión (Base:36) **no** se cumple en el código, y no hay una costura clara para cumplirlo.

### Cited Findings
- **Genérico (la forma):** `usuario`/`sesion` (`tablas.py:40-60`); máquina de estados de trabajo `en_cola → ejecutando → completada|error` con `SKIP LOCKED` (`tablas.py:123-126`, `datos/simulaciones.py:126-139`); cupos y tope de cola (`configuracion.py:24-29`); huella única y compartida (`tablas.py:99-101`); `caso` con alias/edad/sexo/notas sin identificadores (`tablas.py:63-71`); paginación por cursor; errores `ErrorDeNegocio` con código (`views/errores.py`). Los tests de casos son una "plantilla para módulos nuevos" — `AGENTS.md` (sección "Módulo de ejemplo").
- **Específico de audición en el esquema:** `audiograma`, `punto_audiograma` (frecuencia_hz, perdida_db), `pta_db`, gravedad, patrón — `tablas.py:74-93`; `registro_abr`, `arquetipo`, `comparacion` — `tablas.py:133-168`; `usuario.tipo_perfil = fonoaudiologo` — `tablas.py:46-48`; `ctrl/modelos.py:11`.
- **Específico del modelo Verhulst en el esquema:** columnas `frecuencia_portadora_hz`, `nivel_db_spl`, `frecuencia_modulacion_hz`, `n_h/n_m/n_l`, `perfil` en `simulacion` (`tablas.py:114-121`); `efr_uv`, `armonicos`, `espectro`, `ondas` en `resultado_simulacion` (`tablas.py:102-106`). Parámetros no están en JSON: cualquier modelo nuevo exige migración Alembic.
- **Específico en el controller:** RN2 (grados de pérdida por PTA, patrón plano/pendiente) — `controller/perfiles.py:83-97`, `controller/audiogramas.py:67-75`; el post-proceso EFR/FFT — `controller/simulacion.py:67-113`; RN3 con rangos de dB SPL/Hz — `ctrl/simulaciones.py:31-38`.
- **Específico en el frontend:** `tiposSimulacion.ts` (todo audición), `Bienvenida.tsx` (copy sobre audiogramas, EFR, ABR), `ResultsSummary.tsx:8-24` (etiquetas de "Sinaptopatía", "Sincronización Neural Degradada" por umbral de EFR), `PlotsPanel.tsx` (FFT y ondas I/III/V).
- **Metadatos de producto:** título FastAPI "Laboratorio Virtual Auditivo", descripción "basada en el modelo Verhulst et al. 2018" — `views/__init__.py:19-25`; `/api/` responde "Motor de Simulación Biológica Verhulst 2018" — `views/__init__.py:36-42`; `pyproject.toml:4`.
- **Roles:** solo estudiante / investigador / fonoaudiólogo / admin (`tablas.py:46-49`); no existe rol docente, ni actividades, ni cursos, ni portafolio (la Visión los exige en Base:98-116).
- **Alcance explícito del TPI:** `docs/decisiones/001-alcance-del-tpi.md` (citada por MEMORY.md:19: "IA/ML para el año próximo"); el nombre del producto y el alcance son de audición por diseño.

### Inferences
- La parte *reutilizable tal cual* para una plataforma agnóstica es: auth/sesiones, cola+worker+huella, cupos, convenciones de API/errores, paginación, estructura de módulos por capas (`views/controller/datos`), plantilla Casos y Bruno/tests. Es valiosa: buena parte del backend actual (infraestructura) no es de audición.
- Lo que habría que *reabstraer* para cumplir el principio 7: `simulacion.parametros` → JSON validado por esquema de cada modelo; `resultado_simulacion` → JSON de salida + `tipo_salida`; entidad `modelo`/`motor` (id, versión, licencia, estado de validación); `ParametrosSimulacion` y `SimulationResponse` por modelo; UI de resultados por "visualizadores" registrados. Nada de eso existe.
- El vocabulario "caso" es reutilizable (en la Visión sería un caso de estudio biomédico), pero hoy está definido como "paciente anónimo" (alias/edad/sexo): rasgo clínico/screening, no de "pregunta de investigación".

### Gaps
- No existe en el repo ningún documento de diseño genérico/agnóstico; no sé si el equipo lo contempla (no era mi alcance revisar planificación en profundidad).

---

## 4. "Capa única de trabajos" y "Reproducible": cola + worker + huella + caché frente a la Visión

### Takeaway
regelabo ya tiene un embrión sólido de capa de trabajos *propia* (cola en Postgres, worker, huella, caché, recuperación de interrumpidas), pero sin adaptadores (todo es in-process, un solo motor) y **no registra por resultado el modelo, la versión ni la semilla**: solo los mezcla dentro de un hash irrecuperable, y los parámetros de perfil dependen de archivos en disco no versionados. Para el criterio "Reproducible" de la Visión (Base:53) falta persistir esa procedencia.

### Cited Findings
- **Cola:** tabla `simulacion` con `estado`; el worker toma la más vieja con `FOR UPDATE SKIP LOCKED` (`datos/simulaciones.py:126-139`), permite varios workers (`worker.py:6`; `docs/decisiones/005-cola-de-simulaciones.md:11-12`). Se descartó Celery+Redis explícitamente (`005…md:14`). Escalar = levantar más workers; se podría pasar a Celery "sin tocar la capa de negocio" (`005…md:21`).
- **Recuperación:** simulaciones "ejecutando" por más de `SIMULACION_MINUTOS_MAX=5` se marcan error y liberan cupo — `ctrl/simulaciones.py:149-155`, `configuracion.py:28-29`.
- **Huella (RN10):** `calcular_huella` hashea `perfil` (nombre), SHA-256 del contenido de los polos, `carrier_freq`, `spl_level`, `f_mod`, `nH`, `nM`, `nL`, `semilla`, `version_modelo` — `ctrl/simulaciones.py:56-67`. Incluir el hash del contenido del perfil es deliberado: los `Custom_*` pueden regenerarse con el mismo nombre (`:58-60`).
- **Caché:** si existe `resultado_simulacion` con esa huella, la simulación nace `completada` sin pasar por cola ni consumir cupo — `ctrl/simulaciones.py:84-86,98-99`, `datos/simulaciones.py:75-87`; `reutilizada` se deduce de `completada` + `iniciada_en IS NULL` (`datos/simulaciones.py:54`). `ResultadoSimulacion` es compartido por muchas simulaciones y no es por usuario — `tablas.py:96-107`.
- **Constantes de procedencia:** `SEMILLA = 1` y `VERSION_MODELO = "verhulst2018-1"` son constantes de módulo en `motor.py:29-33`, con comentario "Cambiarla si se modifica el código del modelo". `docs/decisiones/006-cache-de-resultados.md` dice: "Si se modifica el código del modelo, hay que cambiar la versión incluida en la huella".
- **Qué se guarda por simulación/resultado:** `simulacion` guarda los 7 parámetros como columnas y la `huella` (`tablas.py:114-122`); `resultado_simulacion` guarda salidas, `duracion_s` y `huella` (`tablas.py:100-107`). **No hay columnas `motor`, `version_modelo` ni `semilla`.** La API devuelve `parameters_used` reconstruido desde las columnas de la simulación (`datos/simulaciones.py:28-36`) y no incluye versión ni semilla (`ctrl/simulacion.py:124-132`). La `huella` se excluye de la API (`ctrl/modelos.py:208-209`).
- **Persistencia del perfil fuera de la DB:** los polos viven en carpetas del disco, `Custom_*` están en `.gitignore` (AGENTS.md, "Detalles") y la decisión 022 descartó una tabla `perfil` ("requiere migración y sincronizarla con las carpetas", `022…md:33`). Los `Custom_*` generados antes de 022 siguen simulando pero su `GET /profiles/{nombre}` da 404 (`022…md:42`).
- **Artefactos que quedan a medias:** `metricas` queda `{}` (`datos/simulaciones.py:69`).
- **Adaptadores:** no hay. El worker invoca código Python en el mismo proceso (`ctrl/simulaciones.py:133`). No hay API externa, ni contenedor propio, ni cliente de servicio (`rg` no muestra nada parecido).
- **Reproducción:** el flujo "pedir otra vez los mismos parámetros" devuelve el resultado en caché instantáneamente (RN10); no hay botón/flujo de "re-ejecutar" ni bypass de la caché. El resultado se puede exportar como JSON desde el navegador (`ResultsSummary.tsx:26-34`), sin identificadores de versión.
- **Determinismo:** documentado y usado como base de la caché — "el ruido de la cóclea usa la semilla `subject`, así que mismos parámetros ⇒ mismo resultado" (AGENTS.md "Detalles"; `motor.py:29`, `docs/decisiones/006…md:5`).
- **Contra la Visión:** Base:232 pide "enviar, consultar y recibir resultados con adaptadores para contenedores propios (AMT) y servicios externos. El estudio estructurado registra servicio, versión y parámetros"; Base:53 "Cada figura guarda modelo, versión, semilla y parámetros, con botón 'reproducir'"; Base:54 "resultados precalculados y en caché; lo no calculado se ejecuta en cola".

### Inferences
- El patrón cola+worker+caché de regelabo **coincide casi 1:1 con la mecánica de "Interactivo" de la Visión** (Base:54: resultados en caché, lo no calculado en cola) y con la mitigación de costos variables (Base:321 "caché de resultados y ejecución bajo demanda"). Es el activo más alineado del repo.
- Para convertirla en "capa única de trabajos" faltan: (a) identidad de motor/servicio y su versión por trabajo; (b) interfaz de adaptador (proceso local, contenedor, API externa) con métodos enviar/consultar/recibir; (c) parámetros y salidas como JSON; (d) persistir `version_modelo`, `semilla`, hash de entradas externas (los polos) *junto al resultado* y no sólo dentro de la huella; (e) una distinción entre "reutilizar" y "re-ejecutar para verificar". Esto es incremental sobre lo hecho: no exige reescribir la cola.
- Una consecuencia sutil: como `VERSION_MODELO` está en el hash pero no en la fila, tras bumpear la versión no hay cómo saber con qué versión se calculó un `resultado_simulacion` viejo (solo se sabe que su huella ya no coincide). Los resultados viejos quedan huérfanos pero no etiquetados.

### Gaps
- No verifiqué si `docs/arquitectura.md` o los docs de `docs/specs/` ya planean registrar versión/semilla.

---

## 5. "Estudio estructurado": equivalencia en regelabo

### Takeaway
No existe una entidad equivalente al estudio estructurado. Lo más cercano es `caso` (contenedor personal de audiogramas y simulaciones) y, en el esquema sin implementar, `comparacion.hipotesis`. Faltan hipótesis de primera clase, modelo versionado, afirmaciones enlazadas a evidencia, procedencia humano/IA, versionado/DOI y publicación.

### Cited Findings
- `caso`: alias, edad, sexo, notas, `borrado_en` — `tablas.py:63-71`. Agrupa `audiograma` (por `caso_id`) y `simulacion` (por `caso_id` opcional, `tablas.py:114`) y `registro_abr` (`tablas.py:151`). Es privado del usuario (RN4: "Ningún usuario tiene permiso sobre casos, simulaciones o comparaciones de otro" — `docs/reglas-de-negocio.md`, fila RN4), sin publicación, comentarios ni coautoría.
- `comparacion.hipotesis`: un `Text` opcional "hipótesis de estudio, nunca diagnóstico" — `tablas.py:168`; tabla sin código que la use (ver §1). `comparacion.coincidencias` guarda una copia del top-3 de arquetipos para reproducir aunque el arquetipo cambie (RN8, `tablas.py:163`): es un patrón de *inmutabilidad de evidencia*, parecido en espíritu a "afirmaciones enlazadas a evidencia", pero solo para comparaciones de ABR.
- Texto de producto: "Cada caso reúne sus audiogramas y simulaciones, y es solo tuyo" — `frontend/src/pages/Bienvenida.tsx:16-18`; "registrá tu hipótesis de estudio" (marcado "Próximamente") — `:20-24`.
- No hay en el repo (backend ni frontend): artículo, niveles de lectura, glosario, JSON-LD / RO-Crate, DOI, versionado de entidades, roles CRediT, registro de aportes de IA, revisión abierta, coautoría, video, agente de IA, exportación a formato abierto. Verificado por `rg -i` de "reproduc|hipótesis|DOI|validad|exploratori|verificad|diagnóstic" en `backend/` y `frontend/src` (solo coincidencias en `tablas.py:168`, `Bienvenida.tsx`, textos RN9 y la aceptación del aviso).
- La Visión define el estudio como "un único objeto digital con hipótesis, modelo, parámetros, resultados y afirmaciones enlazadas a su evidencia" — Base:11; con capa de datos JSON-LD/RO-Crate (Base:52), procedencia (Base:56) y trazabilidad humano-IA (Base:34).

### Inferences
- Campos que faltarían para que `caso` (o una entidad nueva `estudio`) cumpla la definición de la Visión: pregunta/hipótesis estructurada; referencia a modelo (id + versión + licencia + estado de validación); parámetros como JSON; lista ordenada de simulaciones/resultados que sustentan cada afirmación; afirmaciones (texto + enlace a resultado/figura); versión del estudio + identificador persistente (DOI); autores y roles (CRediT); procedencia de aportes de IA; visibilidad (privado/publicado/revisión); niveles de lectura; metadatos de licencia de los datos y del modelo.
- `caso` tal como está es un contenedor de *datos de entrada de un paciente simulado* (edad, sexo, notas), no de una pregunta científica; la reinterpretación hacia "estudio" cambia el concepto, no solo agrega columnas. Ver también el punto de vista de la decisión 008 (sin datos personales) que va en la dirección de la Visión (no enviar datos de pacientes a terceros, Base:320).
- `simulacion` + `resultado_simulacion` + `huella` pueden ser los *bloques de evidencia* del estudio con poco cambio; el cuello de botella es el esquema genérico de parámetros/salidas (ver §3-4).

### Gaps
- No leí `docs/specs/requerimientos-*.md` en detalle (otro investigador cubre planificación); pueden existir requisitos que se aproximen a "estudio".

---

## 6. "Estado de validación visible" (Validado con datos / Verificado / Exploratorio)

### Takeaway
No hay nada equivalente. Lo que existe son avisos de "uso no profesional / no es diagnóstico clínico" (genéricos) y un aviso de recorte del techo del modelo (parcial, específico de perfiles). No hay estado de validación por modelo, y el único elemento que parece una clasificación clínica (badges de EFR) va en dirección opuesta al principio.

### Cited Findings
- Aviso genérico en registro, con fecha de aceptación persistida (RN9): `frontend/src/pages/Registro.tsx:66-70`, `tablas.py:50`, `controller/autenticacion.py:56-57`. Texto de bienvenida: "Herramienta de estudio y experimentación. No es de uso profesional y sus resultados no constituyen un diagnóstico clínico" — `Bienvenida.tsx:66-69`.
- Aviso de limitación del modelo (parcial): el modelo "solo representa la pérdida de las células ciliadas externas" y tiene techo por frecuencia; si se simula >5 dB menos de lo pedido hay un cartel fijo antes de simular y un aviso final con las dos curvas pedida/simulada — `controller/perfiles.py:4-8,28`, `controller/audiogramas.py:79-81`, `frontend/src/components/CurvasPerfil.tsx:8-30`, `SimulationControls.tsx:54,287-289`, `PerfilSimulado.tsx:4-12`, `docs/decisiones/022…md:13`. Esto es transparencia de una limitación, no un estado de validación del modelo.
- Elemento a contramano: `ResultsSummary.tsx:8-24` asigna etiquetas tipo clínico a umbrales de EFR (`< 0.08` "Sincronización Neural Severamente Degradada"; `< 0.18` "Respuesta Atenuada (Pérdida / Sinaptopatía)"; si no, "Respuesta Neural Robusta (Normal)"). Los umbrales son constantes de código sin cita. La Visión: "Ningún resultado se muestra sin indicar qué tan respaldado está el modelo que lo produjo" (principio 2, Base:31); y en el Simuladores doc, los propios autores de Verhulst declaran respuestas "sin unidades físicas" y que el modelo mejor parametrizado "no está validado con EFR humanos" para ZBC (Simuladores:64).
- Regla del equipo: no usar la palabra "diagnóstico" en la UI (RN9, `MEMORY.md:32`). Hay una excepción residual en la API: el campo `clinical_classification` (`ctrl/modelos.py:186`, `tiposSimulacion.ts:68`) y el comentario "Clasificación clínica didáctica" en `ResultsSummary.tsx:8`.
- No existe ningún campo `estado_validacion`, `validado`, `exploratorio`, `verificado` ni tabla de modelos (confirmado con `rg -i` en backend/frontend; solo coincide "verificada" en `SesionContext.tsx:20,33`, que es otra cosa).
- Visión: tabla de estados y usos permitidos en Base:38-42; "Los escenarios de preservar y de reparar o regenerar se etiquetan como Exploratorio" (Base:270).

### Inferences
- Verhulst 2018 es el candidato natural a *Verificado* (el código implementa el modelo publicado), y algunos aspectos son *Validado con datos* en el paper, pero el repo no registra ninguna evidencia: habría que agregar una entidad `modelo` con campo de estado y un banner en los componentes de resultado. La barra de implementación es baja en UI (un badge) y media en datos (nueva tabla o config).
- La mayor fricción de contenido está en `ResultsSummary.tsx`, que hoy emite juicios cuasi-clínicos con umbrales no referenciados; con la Visión habría que rotularlos como Exploratorio o quitarlos.

### Gaps
- No verifiqué contra el paper de Verhulst qué resultados están contrastados con datos (fuera de alcance).

---

## 7. Rendimiento: ~75 s y ~1,1 GB vs 8–11 s por estímulo de 30 ms con 401 CF

### Takeaway
La diferencia se explica sobre todo por la duración del estímulo: regelabo simula 400 ms a 100 kHz (40 000 muestras) con 401 secciones sondeadas ('abr') y las 1000 secciones cocleares, mientras la prueba citada en la Visión usaba 30 ms. Escalado lineal da 107–147 s; la medición de ~75 s en un i7 de 11.ª gen está en el mismo orden de magnitud.

### Cited Findings
- Estímulo: `DURACION_ESTIMULO_S = 0.4` y `FS_ESTIMULO = 1e5` — `motor.py:25-27`; `get_RAM_stims(..., dur=0.4)` por defecto — `verhulst/src/utils/get_RAM_stims.py:4`. Documentado: "~40.000 pasos temporales (400 ms × 100 kHz)... 401 secciones cocleares" — `docs/guias/visualizaciones_CU.md:21`.
- CF: `fc='abr'` → 401 secciones guardadas (`model2018.py:396-398`, docstring :312-313); el modelo resuelve `sectionsNo = 1000` secciones en la línea de transmisión coclear (`model2018.py:375`).
- Recomendación del propio README de Verhulst: estímulos de 100–200 ms ("Keep the stimuli short! 100-200ms stimuli work well") — `verhulst/README.md:47`. regelabo usa 400 ms (2–4× la recomendación).
- Un solo canal (un estímulo) → ejecución secuencial en un solo núcleo (`model2018.py:450-468`; `worker.py:6`). Con varios canales el modelo usaría `mp.Pool(mp.cpu_count())` (`model2018.py:474`), que regelabo no usa.
- Se activa en cada corrida un `PlotOrchestrator` con hilo de sondeo y generación de PNGs diagnósticos (`model2018.py:458-468`, `utils/plot_orchestrator.py:31-45`) y se guardan salidas con `storeflag='evihmlbw'` (`motor.py:85`), es decir, almacena BM velocity, IHC, ANF H/M/L, emisión, CN, IC y ondas: más memoria/IO que lo estrictamente necesario para el EFR.
- Mediciones del equipo: ~75 s en notebook i7 11.ª gen, ~1,1 GB, un núcleo; 1,5–2,5 min estimados en el servidor — `docs/decisiones/005-cola-de-simulaciones.md:6`; `docs/guia-de-pruebas.md:87`.
- Medición en Simuladores:36: Verhulst v1.2, Python 3.13, 401 CF, 2 CPU, 7 GB RAM, "cada simulación de 30 ms tardó 8 a 11 s".

### Inferences
- 400 ms / 30 ms ≈ 13,3×; 8–11 s × 13,3 ≈ 107–147 s. El ~75 s medido es ~30–50 % menor: compatible dado diferencias de hardware, solver C vs fallback, y que el costo no es exactamente lineal. Es una estimación mía, no una medición.
- Implicación para la Visión: "algunos modelos tardan segundos por estímulo" (Base:54) es correcto para estímulos de 30 ms, pero el estímulo EFR clínico estándar (400 ms) cuesta más de un minuto: la caché y la cola son necesarias, no opcionales, para la experiencia interactiva. Con la Visión (créditos de cómputo por uso, Base:286), 75 s × 1,1 GB por corrida es el coste unitario real que hoy se observa.
- Un estímulo de 100–200 ms bajaría el tiempo a ~20–40 s, pero cambia la resolución espectral del EFR (inferencia; no verificado).

### Gaps
- No medí nada (restricción de solo lectura); los números de tiempo son los reportados por el equipo.
- No verifiqué si el solver C está compilado en la máquina actual: en `backend/simulacion/verhulst/src/c_lib/` hay `cochlea_utils.c`, `build.sh`, `build.bat` pero ningún `tridiag.dll/.so`; el `tridiag.dll` existe solo en la carpeta untracked `backend/services/...` (ver §9). Si no está compilado en el destino correcto, el modelo usaría el fallback en Python (más lento) — solo aplicable a esta máquina.

---

## 8. Inconsistencia en las Visión: fibras por defecto "3, 3 y 13" vs "13/3/3"

### Takeaway
**Los valores son los mismos y correctos; el error está en el orden de la etiqueta de la tabla de Simuladores.** El código define nH=13 (alta tasa espontánea, HSR), nM=3 (media), nL=3 (baja). Base:157 ("baja, media y alta (por defecto 3, 3 y 13)") es correcto. Simuladores:16 ("L/M/H (por defecto 13/3/3)") tiene la etiqueta invertida: 13/3/3 es el orden H/M/L, o sea L/M/H = 3/3/13.

### Cited Findings
- Defaults del modelo Python: `nH: ... = 13, nM: ... = 3, nL: ... = 3` — `backend/simulacion/verhulst/src/model2018.py:295-297`; docstring: "Number of high, medium and low spont. fibers ... Default 13,3,3" — `model2018.py:336-338`.
- Defaults en MATLAB: `nL=3` (`matlab/model2018.m:88`), `nM=3` (:91), `nH=13` (:94); comentario "nH,nM,nL= number of high, medium and low spont. fibers ... Default 13,3,3" — `model2018.m:28-29`.
- Ejemplo oficial: `nH=13` "Fibras HSR por IHC (alta tasa espontánea)", `nM=3`, `nL=3` — `verhulst/examples/ExampleSimulation.py:189,203-205`.
- Defaults de regelabo, coherentes: `nH=13, nM=3, nL=3` — `ctrl/modelos.py:105-110`; `frontend/src/App.tsx:44-52`.
- Base:157: "número de fibras de baja, media y alta tasa espontánea ... (por defecto 3, 3 y 13)" → L=3, M=3, H=13: **correcto**. Simuladores:60 dice lo mismo ("baja, media y alta ... por defecto 3, 3 y 13"). Simuladores:16: "Variación del número de fibras L/M/H en Verhulst (por defecto 13/3/3)" → implica L=13, M=3, H=3: **incorrecto como etiqueta** (confunde el orden nH/nM/nL con L/M/H).
- Observación adicional: el propio documento Simuladores es internamente inconsistente (:16 vs :60); el Base no lo es.

### Inferences
- Corrección mínima sugerida: en Simuladores:16 escribir "H/M/L (por defecto 13/3/3)" o "L/M/H (por defecto 3/3/13)".
- Pequeña precisión de texto: en Verhulst los conteos son fibras "por IHC" / por canal (ExampleSimulation.py:203), no totales.

### Gaps
- Ninguno relevante para esta pregunta.

---

## 9. La carpeta `backend/services/` (untracked)

### Takeaway
Es un **resto local sin versionar de la estructura de microservicios anterior** (core/llm/simulation-service). Todo lo que estaba versionado se eliminó en el commit `313f9fd` (reorganización en 3 capas, 2026-10-14); lo que queda en disco son solo archivos ignorados o generados: `__pycache__`, `Poles.mat`, `tridiag.dll`. No tiene código `.py` ni duplica el Verhulst vigente (que está en `backend/simulacion/verhulst/`). No es importada por nada, pero rompe la limpieza del árbol frente a la regla de 3 capas.

### Cited Findings
- `git status` muestra solo `?? backend/services/`. En disco hay 49 archivos (1,1 MB): `__pycache__` de `core-service` (cpython-312) y de `simulation-service/src/Verhulst/src/{,core,utils}` (cpython-314), `src/Verhulst/src/c_lib/tridiag.dll`, y `Poles.mat` en cada carpeta de `src/Verhulst/data/Poles/*`. No hay ningún `.py` (verificado con `find ... -name '*.py'`: sin resultados).
- Historia git: la carpeta nace en `13138c6` (2026-04-27, "Primera re-organización para sdd"; ese commit crea `backend/services/{core,llm,simulation}-service`), el Verhulst se "mueve de lugar" en `4f347ed` (2026-04-27), y `313f9fd` (2026-10-14, Valentino Ortiz, "Reorganizar el backend en 3 capas") borra `backend/services/**` (Dockerfiles, `main.py`, `requirements.txt` de cada servicio, `simulation_controller.py`) y mueve el Verhulst a `backend/simulacion/verhulst/` con `git mv` (`R` en el stat).
- Origen de los residuos: `Poles.mat` nunca estuvo versionado (`git log --all -- '*Poles.mat'` no devuelve commits); el `.gitignore` de Verhulst ignora `*.mat`, `*.dll`, `*.so` (`backend/simulacion/verhulst/.gitignore:1,4,5`). Inferencia: el `.gitignore` viejo de esa carpeta fue borrado en `313f9fd`, por eso ahora git ve los restos como untracked; los archivos versionados desaparecieron del disco al cambiar de commit y quedaron solo los no versionados.
- Importante: los `Poles.mat` están en esa carpeta y no en el Verhulst actual; son exactamente los `.mat` que `OHC_ind` necesita (`OHC_ind.py:30-32`) y que MEMORY.md:37 / decisión 022 dicen que no están disponibles. Quedan fuera del control de versiones por `*.mat`.
- Regla de capas: AGENTS.md pide `views/ controller/ datos/` (+ `simulacion/`, `comandos/`, `configuracion.py`); `backend/services/` no es ninguna de esas y no está importada ni referenciada: un `rg` por `backend.services|backend/services` en `*.py`, `*.toml`, `*.ini`, `*.json` (excluyendo la propia carpeta) no dio resultados.
- `README.md:13-15` (raíz) todavía describe la vieja arquitectura de servicios ("Capa central... Gestiona múltiples sub-servicios... `backend/src/simulation`... Celery") — documentación desactualizada que alimenta la confusión.

### Inferences
- Es seguro tratarla como basura local: no es duplicado funcional del Verhulst ni un microservicio vivo. Las únicas piezas con valor son (a) `Poles.mat` (si se resuelve la licencia o se pide permiso a UGent) y (b) el `tridiag.dll` compilado, que debería estar en `backend/simulacion/verhulst/src/c_lib/` para activar el solver C en Windows. Conviene que el equipo, antes de borrarla, mueva o preserve esos dos tipos de archivo; esa decisión es suya (la regla del proyecto es no tomar decisiones sin consultar).
- Para la decisión Visión/regelabo: no aporta evidencia a favor ni en contra; solo confirma que el equipo ya hizo el paso "microservicios → monolito" por exigencia del checklist (decisión 002), lo contrario de lo que la Visión sugiere a largo plazo (contenedores separados por licencia GPL/AGPL, Base:153) — ver matriz.

### Gaps
- No verifiqué qué contenía exactamente `core-service` y `llm-service` en sus versiones versionadas más allá de los nombres de archivo en el stat (varios eran vacíos: `celery_app.py`, `config.py`, `chroma_db.py`, `document_qa.py`).

---

## 10. Matriz de alineación y fricción, principio por principio

### Takeaway
Hay 5 áreas alineadas o fácilmente alineables (infraestructura de cola/caché, determinismo/huella, privacidad de casos, transparencia de limitaciones, trazabilidad humano-sistema parcial), 4 con fricción media (modelo único, esquema cableado, "reproducir", validación) y 5 totalmente ausentes (estudio estructurado, artículo, video, agente, docencia/portafolio). La fricción más seria es de **licencia** (Verhulst/UGent vs MIT y vs. servicio comercial) y de **forma de la arquitectura** (monolito mono-modelo en proceso vs contenedores/adaptadores).

### Cited Findings (matriz)

| Principio / pieza de la Visión | Estado en regelabo | Evidencia | Fricción |
|---|---|---|---|
| 1. Laboratorio computacional (simular ≠ experimentar) | Parcial: avisos de "no diagnóstico" y "hipótesis de estudio" | `Registro.tsx:66-70`, `Bienvenida.tsx:66-69`, `tablas.py:168` | Baja. Pero `ResultsSummary.tsx:8-24` emite etiquetas casi clínicas |
| 2. Estado de validación visible | **Ausente** | rg sin coincidencias; §6 | Media: hay que agregar entidad modelo + banner; quitar/relabelar badges de EFR |
| 3. Integrar antes que construir (estándares, servicios, AMT) | Parcial: reutiliza Verhulst copiado; no usa AMT/Octave/SBML/OMEX/COMBINE | `motor.py:16-23`; `pyproject.toml` | Media. Se integra por *copia de código*, no por contenedor/API, y con licencia incompatible con servicio comercial |
| 4. Formatos abiertos, servicios de pago | No aplica aún | `LICENSE:1-3` (MIT propio) | Alta en lo legal: MIT + UGent Academic; exportación solo JSON ad hoc (`ResultsSummary.tsx:26-34`) |
| 5. Trazabilidad humano-IA (CRediT, etiquetado sintético) | Ausente (no hay IA en el producto; solo `aviso_aceptado_en`) | `tablas.py:50`; decisión 001: IA/ML "para el año próximo" (MEMORY.md:19) | Baja hoy; el esquema no tiene dónde guardar procedencia |
| 6. Fin biomédico, cinco vías | Solo "comprender" (daño periférico por OHC y fibras); no sustituir/reparar/guiar/preservar como escenarios | `controller/perfiles.py:4-8`; nH/nM/nL para sinaptopatía (`modelos.py:105-110`) | Media: la sinaptopatía vía nH/nM/nL ya es una palanca "preservar/comprender" (Base:270) pero sin etiquetas Exploratorio |
| 7. Plataforma agnóstica de dominio | **No cumple**: esquema y API cableados a audición/Verhulst; lo genérico está en la infraestructura | §3 | Alta (reabstraer parámetros/salidas a JSON y entidad modelo) |
| Estudio estructurado (objeto único) | **Ausente**; `caso` ≠ estudio | §5 | Alta (cambio de concepto) |
| Artículo interactivo (6 características) | Ausente. "Interactivo" parcial: caché+cola ya existen; "Reproducible" parcial: huella determinista | §4 | Media/Alta |
| Capa única de trabajos con adaptadores | Parcial: cola/worker/huella sí; adaptadores/servicios externos/contenedores no | `datos/simulaciones.py:126-139`, `ctrl/simulaciones.py:133` | Media (incremental sobre lo existente) |
| Reproducible: modelo, versión, semilla, parámetros por resultado | Parcial: parámetros sí (columnas); versión y semilla solo dentro del hash; perfil en disco | `tablas.py:100-122`, `motor.py:29-33` | Media |
| Interactivo: sliders sobre resultados precalculados | Parcial: caché RN10; `arquetipo` es "caché precargada" (decisión 006) sin implementar | `006…md:20` | Media |
| Video asistido por IA, agente de IA | Ausentes | rg | — |
| Uso docente (roles, actividades, portafolio, LTI) | Ausente; solo `tipo_perfil` y cupos por rol | `configuracion.py:25-26` | Alta (no hay rol docente ni actividades) |
| Ecosistema: contenedores propios / servicios externos | Ausente (todo en proceso). Se descartó explícitamente la arquitectura de microservicios por el checklist del TPI | `002…md:14-15`; `005…md:14` | **Alta de forma, pero reversible**: la capa `motor.py` es el punto de extensión |
| Aislar GPL/AGPL en contenedores; código propio permisivo | No aplica hoy (solo Verhulst UGent); el diseño en monolito no los aísla | Base:153; `motor.py` | Media |
| Licencias (UGent) | **Fricción principal**: Verhulst en el repo bajo MIT | §2 | Alta (legal) |
| Caso piloto audición: audiograma → modelo → respuesta periférica | Sí, con Verhulst en lugar de bruce2018; sin etapa de inteligibilidad | `controller/audiogramas.py`, Base:254 | Baja/Media: mismo concepto, otro modelo y sin pyclarity/pystoi |
| Privacidad: "no enviar datos de pacientes a terceros" | Alineado por diseño: caso sin datos personales (decisión 008), nombres de perfil sin datos reales | `008…md`; `022…md:22` ("pide no usar nombres reales") | Baja |
| Modelo de negocio (suscripción + créditos de cómputo) | Parcial: cupos por rol y por hora ya existen; no hay créditos ni facturación | `configuracion.py:24-27` | Media (base útil: cupos = embrión de créditos) |

### Inferences
- **Lo que parece reusable tal cual**: auth/sesiones/limites, Casos como plantilla de módulo, cola+worker+huella+caché, convenciones de API, tests con Postgres real, Bruno. Esto es lo que más acerca a la capa de trabajos y a la parte "Interactivo / Confiable" de la Visión.
- **Lo que choca con la Visión de fondo**: (i) el acoplamiento a Verhulst y la decisión de 3 capas monolíticas con el modelo *en proceso* (la Visión quiere contenedores/adaptadores y, para componentes GPL/AGPL, aislamiento); (ii) la licencia UGent con el repo MIT; (iii) el concepto de "caso" como paciente anónimo frente al "estudio" como objeto de investigación. Ninguno es irreversible, pero (i) y (iii) son rediseño de esquema, no ajuste.
- **Lo que la Visión asume y el código ya contradice o ya resolvió**:
  - Base:54 "algunos modelos tardan segundos por estímulo" → con la configuración EFR de regelabo (400 ms) tarda >1 min por estímulo (§7).
  - Base:254 propone `bruce2018` como modelo del caso único; regelabo ya hizo el flujo audiograma→perfil con Verhulst (más parámetros de daño, pero licencia académica), así que la Etapa 0 de la Visión "probar AMT/Octave y medir tiempo" no se ha hecho en el repo.
  - Resumen:127-128 deja abiertas "probar AMT en Octave" y "confirmar licencias"; en regelabo la licencia de Verhulst ya figura como abierta (MEMORY.md:37), pero nadie probó AMT.
- Una redirección de regelabo hacia la Visión sería mayormente *aditiva* en infraestructura (adaptador de motor, JSON genérico, entidad modelo/estado de validación) y *conceptual* en el dominio (estudio). Una modificación de la Visión para reflejar regelabo implicaría reconocer que el punto de partida real es Verhulst-en-proceso y que el piloto es TPI académico con vencimiento a fin de 2026 (MEMORY.md:14), no una plataforma comercial.

### Gaps
- No evalué la hoja de ruta (`docs/plan-de-trabajo.md`, `docs/specs/`) ni `proposal.md`, a pedido (otro investigador).
- No vi `docker-compose.yml` ni `docs/arquitectura.md` (la afirmación sobre "solo DB" proviene de AGENTS.md).
- No pude validar que `OHC_ind.py` esté inutilizable sin los `.mat` más allá de su `try` de carga (`OHC_ind.py:30-32`) y lo que afirma la decisión 022.
