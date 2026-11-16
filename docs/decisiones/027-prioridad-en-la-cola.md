# 027 — Prioridad en la cola de simulaciones

**Fecha:** 2026-11-10 · **Estado:** propuesta (definida en una sesión de preguntas; falta implementarla y medir los 2 workers)

Completa la [020](020-cola-de-simulaciones-en-detalle.md) (cola y worker) y la [009](009-roles-cupos-y-limites.md) (tipos de usuario y cupos). Agrega RN11 y RN12.

## Contexto
- Hay un solo worker y cada simulación tarda ~80 s, con ~1,1 GB de RAM y un núcleo. La cola es FIFO (`tomar_siguiente` toma la más vieja), así que la primera simulación de un usuario puede quedar detrás de muchas otras.
- Un fonoaudiólogo que usa la herramienta en serio queda en el mismo orden que cualquier estudiante.
- El `tipo_perfil` lo elige cada usuario al registrarse y nadie lo verifica. Si da prioridad, cualquiera puede declararse fonoaudiólogo.
- El servidor planificado (decisión 011: 2 núcleos, 4 GB, base en Supabase) podría correr 2 workers, pero falta medirlo.
- El volumen esperado para el TPI es bajo (hasta ~10 usuarios simultáneos); se diseña para eso, con margen.

## Decisión
- **Orden de la cola (RN11),** en `datos/simulaciones.tomar_siguiente`:
  1. **Tope de espera:** una simulación con más de 10 min en cola pasa adelante de todas, incluso de las de un fonoaudiólogo. Es una red de seguridad para que nadie espere sin límite, no el mecanismo normal. El valor va en `configuracion.py`.
  2. **Tipo de usuario:** fonoaudiólogo > investigador > estudiante.
  3. **Turnos:** dentro de un mismo tipo, primero quien inició menos simulaciones en los últimos 60 min (la misma ventana que RN5b). Así, la primera simulación de un usuario pasa adelante de las de su mismo nivel.
  4. **Antigüedad:** si hay empate, la más vieja.
- **Verificación del tipo (RN12):** quien se registra como investigador o fonoaudiólogo queda *pendiente* hasta que un admin lo apruebe. Mientras tanto cuenta como estudiante para el orden **y** para los cupos (RN5a y RN5b). El formulario de registro avisa: "Tu tipo de usuario queda pendiente de verificación; mientras tanto usás el sistema como estudiante." Requiere un campo nuevo en `usuario` y una migración. Los usuarios existentes quedan verificados en la migración. La pantalla de aprobación es parte del panel de admin (028, a definir).
- **Lo que ve el usuario:** "En cola · te avisamos cuando termine", sin posición ni tiempo estimado (con prioridades, ambos pueden empeorar mientras se mira). La API devuelve `posicion: null`. El aviso de simulación terminada (`AvisosSimulacion`) ya existe.
- **Precálculo del catálogo:** un comando en `backend/comandos/` encola los 9 perfiles del catálogo (decisión 026) con los valores por defecto del formulario, a nombre de un admin, y pasan por la cola y el worker como cualquier otra. Con la caché (RN10), la primera simulación con esos valores sale al instante. Se corre a mano después de cada cambio de `VERSION_MODELO`, y se documenta en `AGENTS.md`.
- **Dos workers:** se pasa a 2 si, con dos simulaciones en paralelo y un tope de 3,5 GB, cada una tarda ≤ ~100 s y el pico queda ≤ 3 GB. Si no, se sigue con 1. La medición queda para después.
- La consulta de estado cada 3 s se mantiene: cada una es una lectura simple y el costo real lo pone el worker.

## Alternativas descartadas
- **FIFO (lo de hoy):** un usuario nuevo espera todo lo que llegó antes.
- **Prioridad solo a la primera simulación:** ayuda al que recién entra, pero no reparte el worker entre los demás.
- **Turnos con peso según el cupo** (⅓ para profesionales): la primera simulación de un estudiante pasaba delante de un fonoaudiólogo, y se quiere lo contrario.
- **Mostrar posición o tiempo estimado:** el número puede subir de golpe cuando entra alguien con más prioridad, y confunde más de lo que ayuda.
- **Avisos del servidor (SSE/WebSocket) en lugar de consultar:** más complejidad sin necesidad para este volumen.
- **Precálculo automático al arrancar el worker:** agrega lógica a un proceso que hoy es muy simple, para algo que cambia poco.
- **Aceptar el tipo sin verificar:** con prioridad en juego, es fácil de aprovechar.
- **Verificar la matrícula profesional:** fuera del alcance del TPI.

## Consecuencias
- `tomar_siguiente` deja de ser una consulta trivial: necesita el tipo verificado del usuario y sus simulaciones de la última hora. Hay que testear cada criterio del orden por separado.
- Con muchos profesionales activos, un estudiante puede esperar hasta el tope de 10 min.
- El cálculo actual de `posicion` se abandona; el campo queda en la API en `null`.
- Depende del panel de admin (028) para aprobar tipos. Hasta entonces, la aprobación puede hacerse con un comando.
- **Pendiente:** revisar a futuro un sistema de colas más robusto (condición puesta al aceptar el tope de 10 min) y la medición de los 2 workers.
