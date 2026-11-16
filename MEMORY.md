# MEMORY.md — regelabo (Laboratorio Virtual Auditivo)

Memoria del proyecto entre sesiones, para cualquier agente o persona del equipo. Máximo ~50 líneas: resumir o eliminar lo que ya no aporte. Las reglas permanentes van en `AGENTS.md` / `CLAUDE.md`, no acá.

## Dónde buscar
- Estado de cada paso y reparto: [docs/plan-de-trabajo.md](docs/plan-de-trabajo.md) (fuente de verdad del avance).
- Decisiones con alternativas descartadas: [docs/decisiones/](docs/decisiones/README.md). Reglas RN1–RN10: [docs/reglas-de-negocio.md](docs/reglas-de-negocio.md).
- Casos de uso y requerimientos: [docs/specs/](docs/specs/README.md). Cómo probar: [docs/guia-de-pruebas.md](docs/guia-de-pruebas.md).
- Mapa del código: `graphify-out/` (`graphify query "<pregunta>"` antes de buscar en archivos).
- Enunciado y checklists del TPI: `/mnt/datos/Electivas-Soporte/practica-2024/TPI` (fuera del repo).
- Visión de largo plazo (producto, no TPI): `docs/Vision/`. Fricción con regelabo y opciones A/B/C: `reports/Fricción entre regelabo y Visión.md` (notas en `research_notes/`).

## Estado actual
- TPI de Soporte (UTN FRRO), grupo de 3, **entrega la semana del 2026-11-16** (corregido el 2026-11-12; antes decía fin de 2026). Despliegue: provisorio en GitHub Codespaces (ver Ramas). Valentino arma el sprint 0; después cada integrante toma un módulo copiando Casos.
- Sprint 0 (mergeado a `main` en el PR #4): pasos 1–5 hechos (capas, base, auth, Casos, frontend TS, cola + worker + caché + historial). Último commit `ed5f207`.
- Pendientes del sprint 0: paso 6 (CI + `CONTRIBUTING.md`), paso 7 (documentación final), paso 8 (issues y tag `semana-01`).
- `AGENTS.md` es la única fuente de instrucciones; `CLAUDE.md` solo lo importa (`@AGENTS.md`).

## Decisiones (y por qué)
- Alcance y arquitectura: [001](docs/decisiones/001-alcance-del-tpi.md) alcance (IA/ML para el año próximo) · [002](docs/decisiones/002-arquitectura-en-3-capas.md) monolito en 3 capas.
- Datos: [003](docs/decisiones/003-base-de-datos.md) PostgreSQL (Docker en desarrollo, Supabase solo como base en producción) · [010](docs/decisiones/010-esquema-de-datos.md) esquema · [017](docs/decisiones/017-paginacion-por-cursor.md) paginación por cursor.
- Autenticación: [004](docs/decisiones/004-autenticacion-propia.md) propia con argon2 · [013](docs/decisiones/013-sesion-en-el-servidor.md) sesión en servidor · [015](docs/decisiones/015-interfaz-de-autenticacion.md) pantallas · [018](docs/decisiones/018-cambio-de-contrasena.md) cambio de contraseña.
- Simulación: [005](docs/decisiones/005-cola-de-simulaciones.md) cola en tabla sin Celery · [006](docs/decisiones/006-cache-de-resultados.md) caché por huella · [020](docs/decisiones/020-cola-de-simulaciones-en-detalle.md) detalle de cola y worker · [019](docs/decisiones/019-endpoints-del-prototipo-con-sesion.md) prototipo con sesión.
- Dominio: [007](docs/decisiones/007-arquetipos-y-similitud.md) ~12 arquetipos y Pearson · [008](docs/decisiones/008-caso-sin-datos-personales.md) caso sin datos personales · [009](docs/decisiones/009-roles-cupos-y-limites.md) roles, cupos y límites.
- Estados internos: [023](docs/decisiones/023-estados-internos.md) 7 figuras del paper del piloto; el núcleo guarda solo los canales graficados (con `d` completo, ~6 GB de pico). Glosario en `CONTEXT.md`, cambios en `CHANGELOG.md`.
- Interfaz: [024](docs/decisiones/024-rediseno-de-la-interfaz.md) rediseño (paleta turquesa, claro/oscuro, `ui.tsx`, `graficos.ts`) · [026](docs/decisiones/026-etiquetas-clinicas-de-los-perfiles.md) etiquetas clínicas y catálogo de 9.
- Resto: [012](docs/decisiones/012-frontend.md) React TS · [014](docs/decisiones/014-convenciones-de-la-api.md) convenciones de la API · [016](docs/decisiones/016-coleccion-de-bruno.md) Bruno.
- No re-litigar estas decisiones: se cambian con una decisión nueva en `docs/decisiones/`.

## Aprendizajes y errores a evitar
- Valentino usa **fish**: los comandos que se le pasan no llevan subshells `( ... )`, `VAR=valor`, `export` ni `cd x && ...` (usar `pnpm --dir frontend ...`). Validar con `fish -n`. La herramienta Bash del agente no corre en fish, así que no detecta el error.
- Se acumularon 6 bloques de trabajo sin commitear y no se pudieron separar por tema: cerrar cada paso con su commit antes de empezar el siguiente.
- Al preparar staged, usar rutas explícitas y dejar afuera `.claude/settings.json` (hook local de graphify).
- Pedir permiso antes de copiar archivos del repo oficial de Verhulst (licencia UGent sin resolver).
- Nunca usar la palabra "diagnóstico" en la UI (RN9).
- Un rediseño es solo de aspecto: no sacar ni reescribir textos, datos ni controles de la versión anterior (en el rediseño se perdieron y hubo que restaurarlos). Antes de cerrar, comparar los textos con `git show HEAD:<archivo>`, incluidos los de varias líneas.
- `backend/simulacion/` se renombró a `backend/services/`: las rutas a `verhulst/` armadas a mano (`datos/perfiles.py`, `.flake8`) no las detectan los imports; al mover carpetas, buscar también strings de rutas.
- No agregar `Co-Authored-By: Claude` en commits ni PRs: hizo aparecer a Claude como contribuyente en GitHub.
- pytest lee el `.env`: con SMTP configurado mandó ~100 mails reales (rebotes). `conftest.py` ya vacía `SMTP_HOST`; no sacarlo.
- `SlowAPIMiddleware` no ve las rutas de los routers con FastAPI 0.143: los límites por defecto van como dependencia global.

## Ramas (2026-11-16), cada una sobre la anterior; mergear en este orden
- `feat/despliegue` ([029](docs/decisiones/029-despliegue.md), pusheada, sin PR; la despliega un compañero): Compose + Caddy, `instalar.sh`, `backup.sh` (Drive con rclone), `actualizar.sh`. Hoy corre provisorio en GitHub Codespaces (cuenta de Valentino; se apaga tras 4 h, nunca borrarlo). Destino definitivo sin resolver: Azure de un compañero, VPS o VM de la cátedra (Oracle y Azure propio descartados por tarjeta/cuenta).
- `feat/email` ([030](docs/decisiones/030-verificacion-y-recuperacion-por-email.md), pusheada): verificación (sin verificar no simula) y recuperación por enlace. SMTP: en local, Gmail personal de Valentino en el `.env`; falta el del proyecto (la contraseña de aplicación la tiene que crear quien tiene la llave de acceso).
- `feat/panel-admin` (sin pushear): panel [028](docs/decisiones/028-panel-de-administracion.md) con comentarios (RN13), usuarios (desbloquear, verificar email, contraseña temporal solo con pedido, por `mailto:`), pestaña Cola y contador cada 60 s; [031](docs/decisiones/031-cambio-obligatorio-de-contrasena-temporal.md) cambio obligatorio tras la temporal.
- `feat/superponer` (sin pushear): [025](docs/decisiones/025-comparar-simulaciones.md), de 2 a 4 simulaciones, CSV e impresión.
- `feat/pendientes` (sin pushear): límite general 120/min por sesión (ajuste en la 009), varias simulaciones a la vez desde Simular (cambio en la 024), [032](docs/decisiones/032-audiogramas-en-el-caso.md) audiogramas guardados en el caso, comparativas guardadas (cambio en la 025, tablas `comparativa` y `comparativa_simulacion`).
- **Base local:** faltan 4 migraciones (`c4a1e2d9f310`, `d2b7f0a4c8e1`, `e5c3a9b1d7f2`, `f7a2c4e6b9d1`); hasta `uv run alembic upgrade head` el backend falla al tocar usuarios. Nada de esto se probó en el navegador; pytest 196 en verde.

## Próximos pasos
- Para la entrega: Bruno `6-simulaciones` falla en 03 (usuario sin verificar), paso 6 (CI + `CONTRIBUTING.md`), paso 7 (documentación final), paso 8 (issues y tag `semana-01`; antes conectar GitHub a la sesión).
- Post-entrega: etapa 2 del panel (aprobación de tipos, RN12/RN14) junto con la cola con prioridad ([027](docs/decisiones/027-prioridad-en-la-cola.md)); validación completa de RN1 y `OHC_ind` en el módulo de audiogramas.
- Revisión por fonoaudiología pendiente: panel de estados internos (023), etiquetas de perfiles (026), ventanas de latencia y amplitud de las ondas.
- Sin decidir (ver el informe de fricción): el repo público con licencia MIT contiene código de Verhulst bajo la licencia UGent, cuya sección 2 prohíbe distribuir sin permiso escrito (urgente; responde UGent o un abogado; borrador en `reports/Contención licencia Verhulst.md`; el fork `giani1233/regelaboForked` también tiene el modelo); relación TPI–Visión (A/B/C); `proposal.md` desactualizado; `validacionPlanAnalisis/` sigue versionada (falta `git rm -r --cached`).
