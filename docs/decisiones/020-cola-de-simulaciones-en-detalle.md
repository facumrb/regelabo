# 020 — La cola de simulaciones en detalle

**Fecha:** 2026-10-16 · **Estado:** aceptada

Completa la [005](005-cola-de-simulaciones.md) (cola en la base y worker), la [006](006-cache-de-resultados.md) (caché por huella) y la [009](009-roles-cupos-y-limites.md) (cupos).

## Decisión
- **API:** `POST /api/simulaciones` responde 202 enseguida (`en_cola`, o `completada` si el resultado ya existía); `GET /api/simulaciones` lista las del usuario (cursor, decisión 017; filtro opcional `caso_id`; sin las señales); `GET /api/simulaciones/{id}` da el estado y, si terminó, el resultado. Una ajena responde 404 (RN4). Se **eliminó** `POST /api/simulate`.
- **Caso opcional:** una simulación puede ligarse a un caso del usuario o no.
- **Worker:** `worker.py` (en `npm run dev` corre como tercer proceso, o `uv run python worker.py`) toma la más vieja con `FOR UPDATE SKIP LOCKED`, la ejecuta y guarda el resultado. Una simulación a la vez por proceso.
- **Cada simulación corre en una carpeta temporal:** el modelo deja archivos `*_0.npz` en el directorio de trabajo; así dos workers no se pisan y no se ensucia el repo.
- **Huella (RN10):** SHA-256 de perfil, **hash del contenido del perfil**, frecuencias, nivel, fibras, semilla y versión del modelo. Se incluye el contenido porque los perfiles `Custom_*` se pueden regenerar con el mismo nombre. La semilla y la versión (`SEMILLA`, `VERSION_MODELO`) están en `simulacion/motor.py`: **hay que cambiar la versión si se modifica el código del modelo.**
- **Cupos** (`configuracion.py`): RN5a (en curso por tipo de perfil), RN5b (por hora, ventana móvil) y RN5c (tope de 20 en cola, 503). Lo reutilizado de la caché **no cuenta**. Se verifican con la fila del usuario bloqueada, así dos pedidos suyos simultáneos no se saltean el cupo.
- **RN3:** rangos validados en el controller (400). Se mantuvieron los máximos del prototipo para las fibras (nH 30, nM 15, nL 15), que RN3 no fijaba, para que un pedido desmesurado no ocupe el servidor.
- **Worker caído:** una simulación `ejecutando` hace más de 5 minutos (`SIMULACION_MINUTOS_MAX`) pasa a `error` ("se interrumpió") y libera su cupo; el worker lo verifica al arrancar y cada vez que no tiene trabajo.
- **Errores del motor:** el usuario ve un mensaje genérico; el detalle va al log.
- **Frontend:** el simulador pide y consulta el estado cada 3 s; `/simulaciones` es el historial y `/simulaciones/:id` el detalle.

## Alternativas descartadas
- **Un tope temporal de simulaciones a la vez en el servidor** antes de esta cola: se descartaba con este paso.
- **Cancelar una simulación en cola:** requiere un estado nuevo (`cancelada`) y una migración; queda para después.
- **Huella solo con el nombre del perfil:** un `Custom_*` regenerado devolvería un resultado viejo.

## Consecuencias
- **Pendiente (decidido dejarlo para después):** las latencias y amplitudes de las ondas I, III y V. `resultado_simulacion.metricas` queda vacío. Hay que definir con fonoaudiología la ventana de búsqueda de cada pico, el criterio de amplitud (desde cero o de pico a valle) y tener en cuenta que las ondas se repiten cada ciclo de modulación y que el eje tiene una resolución de 0,5 ms. Las usará la comparación con arquetipos.
- El tope global de cola (RN5c) no se bloquea: con pedidos simultáneos de varios usuarios puede pasarse por poco.
- Dos simulaciones idénticas pedidas a la vez se calculan dos veces; el segundo resultado reutiliza el primero al guardarse.
- Los perfiles `Custom_*` siguen compartidos entre usuarios (decisión 019).
