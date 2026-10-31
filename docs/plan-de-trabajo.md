# Plan de trabajo

Documento vivo: se actualiza al cerrar cada paso. Las decisiones de fondo están en `docs/decisiones/` y las reglas en `docs/reglas-de-negocio.md`; este archivo dice en qué orden se hace el trabajo, quién lo hace y en qué estado está.

Origen: resumen consolidado del grilling del 2026-10-14, aprobado por el equipo antes de empezar a programar.

---

## 1. Fases del proyecto

| Fase | Qué incluye | Quién | Estado |
|---|---|---|---|
| **1. Sprint 0: la base** | Arquitectura en 3 capas, base de datos, autenticación, un módulo de ejemplo completo, la cola de simulaciones, CI y documentación. Detalle en la sección 2. | Valentino (con Claude) | En curso |
| **2. Despliegue** | DigitalOcean (4 GB, GitHub Student Pack; plan B: Azure for Students), dominio `.me` de Namecheap y Caddy para HTTPS, sirviendo frontend y `/api` bajo el mismo dominio. | Valentino | Pendiente |
| **3. Módulos por persona** | Cada integrante toma un módulo de punta a punta (vista, negocio, datos, tests y pantalla de React), copiando el módulo de ejemplo. Detalle en la sección 3. | Los 3 | Pendiente |
| **Futuro (año próximo, fuera de la materia)** | Clasificador de ML con un modelo preentrenado sobre salidas de la simulación (reemplaza la similitud por correlación de los arquetipos); IA para consultar papers; integración con hospitales (HL7 FHIR, leyes 25.326 y 26.529). | — | Fuera de alcance (decisión 001) |

---

## 2. Sprint 0 (rama `feature/setup-entorno`)

Cada paso queda funcionando antes del siguiente. Al terminar, cada compañero solo tiene que "llenar" su módulo copiando un ejemplo que ya anda.

| Paso | Qué | Estado | Commit |
|---|---|---|---|
| 1 | Reorganizar carpetas: `app.py` en la raíz, `backend/{views,controller,datos,simulacion}`, `pyproject.toml`. Sacar CC3D y los microservicios. | Hecho | `313f9fd` |
| 2 | Docker compose + PostgreSQL + SQLAlchemy + Alembic, con las 9 tablas. | Hecho | `0691642` |
| 3 | Autenticación, roles y límites de frecuencia (decisiones 013–016: sesión en servidor, convenciones de la API, pantallas de login y registro, colección de Bruno). | Hecho, sin commitear. Falta el límite general de 120 pedidos/min por usuario. | — |
| 4 | **Módulo de ejemplo completo: Casos** (con RN4), de punta a punta, con tests y pantalla en React + TypeScript: CRUD con borrado lógico, `sexo` con valores fijos, paginación por cursor (decisión 017). | Hecho, sin commitear | — |
| 4a | Cambio de contraseña con la sesión iniciada, página *Mi cuenta* y comando de reseteo para el admin (decisión 018). Agregado el 2026-10-16. | Hecho, sin commitear | — |
| 4b | Pasar el frontend del prototipo a TypeScript (`App`, `Header` y los 4 componentes de simulación y audiogramas). Separado del paso 4 por decisión del 2026-10-16. | Hecho, sin commitear | — |
| 5 | Simulación: cola en la tabla `simulacion`, proceso trabajador (`worker.py`), caché por huella (RN10), RN3 y RN5, consulta del estado desde el frontend e historial (decisión 020). Quedan para después las latencias y amplitudes de las ondas. | Hecho, sin commitear | — |
| 6 | Integración continua con GitHub Actions (Flake8 + pytest) y `CONTRIBUTING.md` con las reglas de capas. | Pendiente | — |
| 7 | Actualizar la documentación: `CLAUDE.md`, `PROYECTO.md` (template del TPI), `docs/arquitectura.md`, el diagrama de dominio y `docs/decisiones/`. | Parcial: `CLAUDE.md` y `docs/decisiones/` al día. | — |
| 8 | Conectar GitHub a la sesión de Claude, crear las issues de los 3 módulos y el tag `semana-01`. | Pendiente | — |
| 9 | Estados internos del modelo (decisión 023), rama `feat/estados-internos`: núcleo con solo los canales graficados, tabla `estados_internos`, `GET /api/simulaciones/{id}/estados-internos` y panel con las 7 figuras. Agregado el 2026-10-27. | Hecho, sin commitear. Revisión por fonoaudiología pendiente (no bloquea). | — |

---

## 3. Reparto posterior

| Integrante | Módulo | Funcionalidad del TPI |
|---|---|---|
| Valentino | Simulación + historial | Ondas W1, W3 y W5, EFR, FFT, latencias y amplitudes. Caso de uso principal: CU3. |
| Compañero A | Casos + audiogramas | Carga CSV o manual, PTA, clasificación (RN1, RN2) y perfil propio con `OHC_ind`. CU2. |
| Compañero B | Arquetipos + comparación | ~12 arquetipos con nombre clínico, similitud de Pearson (RN7), hipótesis de estudio (RN8, RN9). CU4 y CU5. |

**Forma de trabajo:**
- Issues de GitHub con un tablero simple.
- Un tag semanal `semana-NN` con el changelog, mencionando a los profesores (lo exige el enunciado).
- Todo cambio entra por pull request, con la integración continua en verde antes de mergear.

---

## 4. Relación con el plan de cuellos de botella

El [Plan de Mitigación de Cuellos de Botella](specs/Plan%20de%20Mitigación%20de%20Cuellos%20de%20Botella.md) (junio de 2026) se revisó en el grilling. Sus tres "fases" técnicas quedaron absorbidas así:

| Propuesta del plan | Qué se decidió | Dónde |
|---|---|---|
| Celery + Redis + WebSocket | Cola en la tabla `simulacion` + proceso trabajador, con polling desde el frontend | Decisión 005, paso 5 |
| Precomputar 132 perfiles | ~12 arquetipos con nombre clínico | Decisión 007, fase 3 (módulo de arquetipos) |
| Caché en Redis | Caché por huella en PostgreSQL (RN10) | Decisión 006, paso 5 |
| Compilar `tridiag` en Docker | Igual: se compila dentro de la imagen | Decisión 011, fase 2 |

---

## 5. Pendientes abiertos

- **Licencia de Verhulst (UGent):** el repo es público y contiene el código del modelo; la licencia prohíbe redistribuirlo sin autorización escrita. Hasta resolverlo con la cátedra, no se traen los `.mat` de `OHC_ind`, lo que bloquea el perfil propio del módulo de casos y audiogramas.
- **`proposal.md` desactualizado:** su sección 4 habla de Celery, Supabase Auth y Storage. Hay que alinearlo con las decisiones.
- **Latencias y amplitudes de las ondas I, III y V**: definir con fonoaudiología las ventanas de búsqueda y el criterio de amplitud (decisión 020). Las necesita la comparación con arquetipos.
- **Revisión del panel de estados internos por fonoaudiología** (nomenclatura y legibilidad de las 7 figuras): pendiente por falta de disponibilidad; no bloquea el merge (decisión 023). Suma las etiquetas clínicas de los perfiles y el recorte del catálogo (decisión 026).
- **Comparar simulaciones entre sí** (decisión 025, propuesta): próxima funcionalidad tras el rediseño; falta diseñarla y asignarla. Distinta de la comparación con arquetipos.
- **Varias simulaciones a la vez desde Simular** (cupo de 3 para investigadores): hoy el formulario espera una por pestaña; se revisa junto con la 025.
- **Perfiles `Custom_*` compartidos entre usuarios** (se pisan por nombre y `/profiles` los muestra a todos): se resuelve en el módulo de audiogramas, ligándolos a un caso (decisión 019).

---

## 6. Cómo se actualiza

- Al cerrar un paso, cambiar su estado y poner el commit.
- Al tomar una decisión nueva, agregar una entrada en `docs/decisiones/` y enlazarla acá.
- Al cambiar el reparto o la forma de trabajo, avisar al equipo y actualizar la sección 3.
