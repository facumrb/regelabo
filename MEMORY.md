# MEMORY.md — regelabo (Laboratorio Virtual Auditivo)

Memoria del proyecto entre sesiones, para cualquier agente o persona del equipo. Máximo ~50 líneas: resumir o eliminar lo que ya no aporte. Las reglas permanentes van en `AGENTS.md` / `CLAUDE.md`, no acá.

## Dónde buscar
- Estado de cada paso y reparto: [docs/plan-de-trabajo.md](docs/plan-de-trabajo.md) (fuente de verdad del avance).
- Decisiones con alternativas descartadas: [docs/decisiones/](docs/decisiones/README.md). Reglas RN1–RN10: [docs/reglas-de-negocio.md](docs/reglas-de-negocio.md).
- Casos de uso y requerimientos: [docs/specs/](docs/specs/README.md). Cómo probar: [docs/guia-de-pruebas.md](docs/guia-de-pruebas.md).
- Mapa del código: `graphify-out/` (`graphify query "<pregunta>"` antes de buscar en archivos).
- Enunciado y checklists del TPI: `/mnt/datos/Electivas-Soporte/practica-2024/TPI` (fuera del repo).

## Estado actual
- TPI de Soporte (UTN FRRO), grupo de 3, entrega a fin de 2026. Valentino arma el sprint 0; después cada integrante toma un módulo copiando Casos.
- Sprint 0 en `feature/setup-entorno`: pasos 1–5 hechos (capas, base, auth, Casos, frontend TS, cola + worker + caché + historial). Último commit `8ec683b`.
- Pendientes del sprint 0: paso 6 (CI + `CONTRIBUTING.md`), paso 7 (documentación final), paso 8 (issues y tag `semana-01`).
- `AGENTS.md` es la única fuente de instrucciones; `CLAUDE.md` solo lo importa (`@AGENTS.md`).

## Decisiones (y por qué)
- Alcance y arquitectura: [001](docs/decisiones/001-alcance-del-tpi.md) alcance (IA/ML para el año próximo) · [002](docs/decisiones/002-arquitectura-en-3-capas.md) monolito en 3 capas.
- Datos: [003](docs/decisiones/003-base-de-datos.md) PostgreSQL (Docker en desarrollo, Supabase solo como base en producción) · [010](docs/decisiones/010-esquema-de-datos.md) esquema · [017](docs/decisiones/017-paginacion-por-cursor.md) paginación por cursor.
- Autenticación: [004](docs/decisiones/004-autenticacion-propia.md) propia con argon2 · [013](docs/decisiones/013-sesion-en-el-servidor.md) sesión en servidor · [015](docs/decisiones/015-interfaz-de-autenticacion.md) pantallas · [018](docs/decisiones/018-cambio-de-contrasena.md) cambio de contraseña.
- Simulación: [005](docs/decisiones/005-cola-de-simulaciones.md) cola en tabla sin Celery · [006](docs/decisiones/006-cache-de-resultados.md) caché por huella · [020](docs/decisiones/020-cola-de-simulaciones-en-detalle.md) detalle de cola y worker · [019](docs/decisiones/019-endpoints-del-prototipo-con-sesion.md) prototipo con sesión.
- Dominio: [007](docs/decisiones/007-arquetipos-y-similitud.md) ~12 arquetipos y Pearson · [008](docs/decisiones/008-caso-sin-datos-personales.md) caso sin datos personales · [009](docs/decisiones/009-roles-cupos-y-limites.md) roles, cupos y límites.
- Estados internos: [023](docs/decisiones/023-estados-internos.md) 7 figuras del paper del piloto; el núcleo guarda solo los canales graficados (con `d` completo, ~6 GB de pico). Glosario en `CONTEXT.md`, cambios en `CHANGELOG.md`.
- Resto: [011](docs/decisiones/011-infraestructura.md) DigitalOcean + Caddy · [012](docs/decisiones/012-frontend.md) React TS · [014](docs/decisiones/014-convenciones-de-la-api.md) convenciones de la API · [016](docs/decisiones/016-coleccion-de-bruno.md) Bruno.
- No re-litigar estas decisiones: se cambian con una decisión nueva en `docs/decisiones/`.

## Aprendizajes y errores a evitar
- Valentino usa **fish**: los comandos que se le pasan no llevan subshells `( ... )`, `VAR=valor`, `export` ni `cd x && ...` (usar `pnpm --dir frontend ...`). Validar con `fish -n`. La herramienta Bash del agente no corre en fish, así que no detecta el error.
- Se acumularon 6 bloques de trabajo sin commitear y no se pudieron separar por tema: cerrar cada paso con su commit antes de empezar el siguiente.
- Al preparar staged, usar rutas explícitas y dejar afuera `.claude/settings.json` (hook local de graphify).
- Pedir permiso antes de copiar archivos del repo oficial de Verhulst (licencia UGent sin resolver).
- Nunca usar la palabra "diagnóstico" en la UI (RN9).
- `backend/simulacion/` se renombró a `backend/services/`: las rutas a `verhulst/` armadas a mano (`datos/perfiles.py`, `.flake8`) no las detectan los imports; al mover carpetas, buscar también strings de rutas.
- Correr el modelo siempre con tope de memoria (`systemd-run --user --scope -p MemoryMax=3G ...`): una corrida con `storeflag` `d` dejó sin RAM una máquina de 16 GB.
- No agregar `Co-Authored-By: Claude` en commits ni PRs: hizo aparecer a Claude como contribuyente en GitHub.

## Próximos pasos
- Estados internos (decisión 023): plan en 5 etapas (núcleo → datos → API → frontend → docs), pendiente de confirmación. `validacionPlanAnalisis/` está en `.gitignore` pero sigue versionada: falta `git rm -r --cached`.
- Paso 6: CI con GitHub Actions (Flake8 + pytest) y `CONTRIBUTING.md`.
- Paso 8: antes de crear las issues, conectar GitHub a la sesión del agente.
- Abiertos: licencia de Verhulst (bloquea `OHC_ind`), `proposal.md` desactualizado, ventanas de latencia y amplitud de las ondas, perfiles `Custom_*` compartidos.
