# Guía de pruebas: autenticación, cuenta y casos

Cómo probar todo lo que hace el sistema hoy (registro, inicio y cierre de sesión, bloqueo de cuentas, límites de pedidos, administradores y el módulo de casos), de menor a mayor detalle. Sirve para entender el flujo y para encontrar qué corregir.

Los comandos andan igual en bash, zsh y fish (se evitó a propósito la sintaxis propia de bash).

## 1. Preparación (una sola vez)

```bash
cp .env.example .env                  # si no existe; ya trae DATABASE_URL y COOKIE_SECURE=false
uv sync
pnpm --dir frontend install
docker compose up -d db               # PostgreSQL local
uv run alembic upgrade head           # crea las 10 tablas
uv run python -m backend.comandos.crear_admin   # opcional: pide email, nombre y contraseña
```

Para arrancar todo: `npm run dev` desde la raíz (backend, frontend y el **worker** que ejecuta las simulaciones) y abrir <http://localhost:5173>.
Swagger queda en <http://localhost:5173/api/docs> (o en `:8000/api/docs`).

Si algo no anda, ver la sección 7.

## 2. Qué pasa cuando hacés clic en "Iniciar sesión"

```
NAVEGADOR (localhost:5173)                        SERVIDOR (localhost:8000)
─────────────────────────                         ─────────────────────────
pages/Login.tsx
  └─ SesionContext.iniciarSesion()
      └─ services/auth.ts  ── POST /api/auth/login ──►  (Vite reenvía /api al backend)
                                                         views/autenticacion.py  login()
                                                           ├─ views/limites.py: ¿más de 5 intentos/min desde esta IP? → 429
                                                           └─ controller/autenticacion.py  iniciar_sesion()
                                                                ├─ datos/usuarios.py: busca el email
                                                                ├─ argon2: compara la contraseña con el hash
                                                                ├─ mal → registrar_fallo() (a los 10 bloquea 15 min)
                                                                └─ bien → token aleatorio
                                                                          datos/sesiones.py: guarda el HASH del token
                                                         views: pone la cookie en la respuesta
  ◄──────────── 200 + Set-Cookie: sesion=<token> ───────┘
  el navegador guarda la cookie (JavaScript no puede leerla)
  React guarda el usuario → el navbar cambia

PEDIDOS SIGUIENTES: la cookie viaja sola
  GET /api/auth/yo ──► views/dependencias.usuario_actual
                         └─ controller.usuario_de_sesion: hash(token) → busca en la tabla sesion → usuario
```

Puntos clave:
- **El token y su hash son distintos.** La cookie tiene el token; la base solo guarda su SHA-256. Quien lea la tabla `sesion` no puede usar las sesiones.
- **Si un intento falla, el contador sube aunque el servidor responda con error.** Por eso `iniciar_sesion` lanza el error *después* de cerrar la transacción.
- **El navegador nunca habla con el puerto 8000:** todo va por `:5173/api`. Es lo mismo que hará Caddy en producción.

## 3. Probar desde la interfaz

Abrí el **Panel de pruebas** (barra inferior, solo en desarrollo) y la pestaña **Red** de DevTools. En cada paso fijate en tres lugares: la pantalla, el panel y, cuando se indica, la base de datos (sección 5).

| # | Qué hacer | Qué deberías ver |
|---|---|---|
| A | **Registrarse** con datos válidos y la casilla tildada | Pasa a *Iniciar sesión* con el email cargado y el aviso "Cuenta creada". Panel: `POST /auth/registro` → **201**. El usuario **no** queda con sesión iniciada. |
| B1 | Registrarse **sin tildar** la casilla | "Tenés que aceptar el aviso de uso no profesional." → **400** `aviso_no_aceptado` |
| B2 | Contraseña de menos de 8 caracteres | "La contraseña debe tener entre 8 y 128 caracteres." → **400** `contrasena_invalida` |
| B3 | Repetir un email ya registrado (probá también con mayúsculas: `ANA@…`) | "Ya existe una cuenta con ese email." → **409** `email_ya_registrado` |
| B4 | Email mal escrito, por ejemplo `ana@` | "Datos inválidos: …" → **422**. El detalle viene en inglés porque lo genera FastAPI, no nosotros. |
| C | **Iniciar sesión** correctamente | Vuelve al inicio; el navbar muestra tu nombre, tu email y perfil, y **Cerrar sesión**. Panel: `POST /auth/login` → **200**. |
| C2 | **Recargar** la página (F5) | Seguís con la sesión. Panel: aparece solo un `GET /auth/yo` → **200**. |
| D | Contraseña incorrecta | "Email o contraseña incorrectos." → **401**. Probá con un email que no existe: **el mismo mensaje y estado** (no se puede averiguar qué emails existen). |
| E | **Bloqueo de cuenta** (ver abajo) | A los 10 fallos seguidos: "Demasiados intentos fallidos. Reintentá en 15 minutos." → **429** `cuenta_bloqueada` |
| F | **Límite por IP**: 6 intentos de login en menos de un minuto | El 6.º: "Demasiados pedidos. Esperá un momento y reintentá." → **429** `demasiados_pedidos`. Se libera en un minuto. |
| G | **Cerrar sesión** | El navbar vuelve a los dos botones. Panel: `POST /auth/logout` → **204**. En la base, la fila de `sesion` desaparece. |
| H | **Dos ventanas**: sesión en una ventana normal y abrí otra de incógnito | La de incógnito **no** tiene sesión. Iniciá sesión en ella con otro usuario: cada ventana ve el suyo. |
| I | **Sesión vencida**: vencela con SQL (sección 5) y apretá "Probar sesión" | **401** y el navbar vuelve a los botones. |
| J | **Admin**: crealo con el comando e iniciá sesión | El navbar muestra la insignia **admin**. |
| S | Clic en **tu nombre** en el navbar | Página *Mi cuenta* con tus datos y el formulario para cambiar la contraseña. |
| S1 | Cambiar con la actual **incorrecta** | "La contraseña actual no es correcta." → **400** `contrasena_actual_incorrecta`. En la base, `intentos_fallidos` sube 1. |
| S2 | Nueva de menos de 8 caracteres, o igual a la actual | **400** `contrasena_invalida` o `contrasena_repetida`. |
| S3 | Nueva y repetición distintas | "Las contraseñas nuevas no coinciden." **No** sale ningún pedido (se controla en la pantalla). |
| S4 | **Cambio correcto**, con otra sesión abierta en incógnito | "Contraseña actualizada. Cerramos tus otras sesiones." → **204**. Esta ventana sigue con sesión; en la de incógnito, "Probar sesión" da **401**. Cerrá sesión y entrá con la nueva. |
| S5 | **Reseteo por el admin**: `uv run python -m backend.comandos.resetear_contrasena` | Pide email y contraseña nueva (dos veces). El usuario queda desbloqueado y sin ninguna sesión abierta. |

**Cómo llegar al bloqueo (E).** El límite de 5 intentos por minuto por IP salta *antes* que el bloqueo de 10 fallos. Hacé 5 intentos fallidos, **esperá un minuto**, y hacé 5 más. El 11.º intento, aunque la contraseña sea correcta, dice "cuenta bloqueada". Para desbloquear sin esperar 15 minutos: `update usuario set bloqueado_hasta = null, intentos_fallidos = 0 where email = '...';`

**Qué se prueba en el servidor y no en la pantalla.** Los formularios no validan nada en el navegador a propósito (`noValidate`): todo llega al servidor, así B1 a B4 ejercitan sus reglas de verdad.

### Simulaciones

Hace falta el worker (lo levanta `npm run dev`). Una simulación tarda ~80 s.

| # | Qué hacer | Qué deberías ver |
|---|---|---|
| T1 | En el simulador, **Ejecutar Simulación Biológica** | El botón dice "En cola (lugar 1)…" y enseguida "Simulando modelo biológico… (Ns)". A los ~75 s aparecen el EFR y los gráficos. En la base, el estado pasó de `en_cola` a `ejecutando` y a `completada`. |
| T2 | **Repetir** exactamente los mismos parámetros | El resultado aparece **al instante**, sin pasar por la cola. En el historial figura como "Resultado reutilizado" (RN10). |
| T3 | Cambiar un parámetro (por ejemplo, el nivel) y simular | Es una simulación nueva: pasa por la cola. |
| T4 | **Cupo (RN5a)**: como estudiante, lanzar una simulación y, **desde otra pestaña**, otra distinta | "Ya tenés el máximo de simulaciones en curso…" → **429** `cupo_agotado`. Al terminar la primera, se puede volver a pedir. (Un investigador o fonoaudiólogo admite 3.) |
| T5 | **Salir de la página mientras corre**: ir a *Ver historial de simulaciones* | La simulación figura "Ejecutando". Abrila: la página se actualiza sola y muestra los gráficos al terminar. |
| T6 | **Historial** (`/simulaciones`) | Lista de la más nueva a la más vieja, con estado, parámetros y fecha; clic en una abre su detalle. Con más de 20, aparece **Cargar más** (igual que *Mis casos*). |
| T7 | Elegir un **caso** en el selector antes de simular, y luego filtrar el historial por ese caso | La simulación queda ligada al caso; el filtro "Todos los casos" / un caso la muestra u oculta. Es opcional: se puede simular sin caso. |
| T8 | Pedir una simulación con el **worker apagado** (Ctrl+C solo del worker, o `npm run dev:backend` y `npm run dev:frontend` por separado) | Queda "En cola" y no avanza. Al levantar el worker (`npm run dev:worker`), la toma. |
| T9 | **Worker caído a mitad**: matalo mientras ejecuta, vencé la simulación con SQL (sección 5) y reiniciá el worker | Pasa a **Error** ("La simulación se interrumpió. Podés volver a pedirla.") y libera el cupo. |
| T10 | **RN4**: copiar la dirección de una simulación (`/simulaciones/<id>`), entrar con otro usuario y pegarla | "Simulación no encontrada" → **404**, igual que con un id inventado. |
| T11 | **Estados internos** (decisión 023): al terminar una simulación, abrir el panel *Estados internos* debajo de los gráficos (también en el detalle del historial) | Recién al abrirlo pide `GET /api/simulaciones/{id}/estados-internos` (~4,6 MB). Muestra las 7 figuras; cada una declara frecuencia solicitada y característica efectiva, muestreo, ventana y unidades. Los selectores cambian el canal de las figuras 2 y 7 (1 o 4 kHz) y de la 3 a la 6 (500 Hz a 8 kHz). |
| T12 | Abrir el panel en una simulación hecha **antes** de esta versión del modelo | "Esta simulación no tiene estados internos…" → **404** `estados_internos_no_disponibles`. |

### Casos

Con sesión iniciada, botón **Mis casos** en el navbar (`/casos`).

| # | Qué hacer | Qué deberías ver |
|---|---|---|
| K0 | Abrir <http://localhost:5173/> **sin sesión** | Pantalla de bienvenida: título, cuatro tarjetas con lo que se puede hacer (la de arquetipos dice *Próximamente*), botones *Crear una cuenta* e *Iniciar sesión*, y el aviso de uso. En DevTools → Red: se pide `/api/health`, **no** `/api/profiles`. |
| K1 | Iniciar sesión y volver a `/` | Ahora es el simulador, con los perfiles cargados. Cerrar sesión vuelve a la bienvenida. |
| K2 | Con la sesión cerrada, pedir `curl -s -w ' [%{http_code}]\n' localhost:5173/api/profiles` | **401** `no_autenticado`. `/api/health` sigue respondiendo 200. |
| K | Entrar a <http://localhost:5173/casos> **sin sesión** | Te manda a *Iniciar sesión*. |
| L | **Mis casos** sin casos todavía | "Todavía no creaste casos." Panel: `GET /casos` → **200**. |
| M | **+ Nuevo caso** con solo el alias | Abre la ficha del caso. Panel: `POST /casos` → **201**. Edad y sexo quedan sin cargar. |
| N1 | Nuevo caso con alias vacío, edad `130` o `-1` | "Datos inválidos: …" → **422** y no se crea nada. |
| N2 | Notas de más de 2000 caracteres | **422**. |
| O | En la ficha, **Editar**: cambiá el alias y vaciá la edad | La ficha muestra los datos nuevos. Panel: `PUT /casos/<id>` → **200**. |
| P | Crear **25 casos** (por ejemplo con el SQL de la sección 5) y entrar a *Mis casos* | Muestra 20, del más nuevo al más viejo, y el botón **Cargar más**. Al apretarlo aparecen los 5 restantes y el botón desaparece. Panel: el segundo pedido lleva `despues_de=<id>`. |
| Q | **Borrar** un caso y confirmar | Vuelve a la lista sin ese caso. Panel: `DELETE /casos/<id>` → **204**. En la base sigue la fila, con `borrado_en` cargado. Si volvés a su dirección (atrás en el navegador): "Caso no encontrado". |
| R | **RN4**: copiá la dirección de un caso, cerrá sesión, entrá con **otro usuario** y pegala | "Caso no encontrado" → **404** `caso_no_encontrado`, igual que con un id inventado. El caso tampoco aparece en su lista. |

## 4. Probar sin interfaz

**Swagger** (`/api/docs`): *Try it out* en `POST /auth/registro`, luego `POST /auth/login` y después `GET /auth/yo`. Swagger es del mismo origen, así que la cookie se guarda y se envía sola.

**curl**, simulando dos ventanas con dos archivos de cookies (`ventana-normal.txt` e `incognito.txt`):

```bash
curl -s -w ' [%{http_code}]\n' -H 'content-type: application/json' -X POST localhost:5173/api/auth/registro -d '{"email":"ana@example.com","password":"clave-larga-1","nombre":"Ana","tipo_perfil":"estudiante","acepta_aviso":true}'
curl -s -w ' [%{http_code}]\n' -H 'content-type: application/json' -c ventana-normal.txt -X POST localhost:5173/api/auth/login -d '{"email":"ana@example.com","password":"clave-larga-1"}'
curl -s -w ' [%{http_code}]\n' -b ventana-normal.txt localhost:5173/api/auth/yo    # 200: la ventana normal tiene sesión
curl -s -w ' [%{http_code}]\n' -b incognito.txt localhost:5173/api/auth/yo        # 401: la de incógnito no (otro archivo de cookies)
```

**El logout invalida el token de verdad**, aunque alguien lo haya copiado:

```bash
grep sesion ventana-normal.txt                      # la última columna es el valor de la cookie (el token): copialo
curl -s -X POST -b ventana-normal.txt localhost:5173/api/auth/logout
curl -s -w ' [%{http_code}]\n' -H 'Cookie: sesion=PEGÁ_ACÁ_EL_TOKEN' localhost:5173/api/auth/yo    # 401
```

Los archivos `.txt` de cookies se crean en la carpeta donde estés parado; borralos al terminar.

**Bruno**: la colección de `docs/api/` hace todo esto con requests guardadas y aserciones (flujo feliz, errores, estado del backend), desde la aplicación o por terminal. Ver `docs/api/README.md`.

**DevTools → Aplicación → Cookies** (`localhost`): la cookie `sesion` debe tener *HttpOnly* ✓, *Path* `/api` y *SameSite* `Lax`. En **Red**, el login muestra la cabecera `Set-Cookie` en la respuesta. Una nota: las cookies no distinguen puertos, así que la sesión iniciada en `:5173` también viaja a `:8000`.

## 5. Mirar la base de datos

```bash
docker compose exec db psql -U regelabo -d regelabo
```

```sql
select email, nombre, tipo_perfil, es_admin, intentos_fallidos, bloqueado_hasta from usuario;
select u.email, left(s.token_hash, 12) as hash, s.expira_en from sesion s join usuario u on u.id = s.usuario_id;
select email, left(password_hash, 30) as hash from usuario;     -- empieza con $argon2id$: nunca la contraseña
update sesion set expira_en = now() - interval '1 second';       -- vence todas las sesiones (prueba I)
select alias, edad, sexo, borrado_en from caso order by id desc; -- casos, del más nuevo al más viejo
select estado, perfil, left(huella, 10) as huella, iniciada_en, finalizada_en, mensaje_error from simulacion order by id desc;   -- la cola y el historial
update simulacion set iniciada_en = now() - interval '6 minutes' where estado = 'ejecutando';   -- vence las que están ejecutando (prueba T9)
-- 25 casos para la prueba P (cambiá el email). PostgreSQL 17 no trae uuidv7(): la expresión
-- arma uno con la hora actual + n milisegundos, así quedan en orden como los que crea la API
insert into caso (id, usuario_id, alias)
  select encode(set_bit(set_bit(overlay(uuid_send(gen_random_uuid()) placing
           substring(int8send((extract(epoch from clock_timestamp()) * 1000)::bigint + n) from 3) from 1 for 6),
           52, 1), 53, 1), 'hex')::uuid,
         u.id, 'Caso ' || n
  from usuario u, generate_series(1, 25) n where u.email = 'ana@example.com';
truncate usuario cascade;                                         -- borra todo (solo desarrollo)
```

**Comprobar que la base guarda el hash y no el token:** copiá el valor de la cookie `sesion` desde DevTools y ejecutá `printf %s 'EL_TOKEN' | sha256sum`. Tiene que coincidir con `token_hash` de la tabla (la consulta de arriba muestra los primeros 12 caracteres). Las fechas salen en hora de Argentina porque la migración inicial configura la zona de la base.

## 6. Tests automáticos

```bash
uv run pytest -v                                  # 107 tests, ~10 s; crea y usa la base regelabo_test
uv run flake8                                     # estilo
pnpm --dir frontend run typecheck
pnpm --dir frontend run build
```

| Archivo | Qué verifica |
|---|---|
| `test_autenticacion_reglas.py` | Largo de contraseña, `requiere_admin`, que el hash no salga al serializar. Sin base de datos. |
| `test_autenticacion_api.py` | Registro y sus errores, hash argon2 en la base, cookie `httpOnly`, token no guardado en claro, login con la misma respuesta exista o no el email, bloqueo a los 10 fallos y desbloqueo, logout que invalida el token, sesión vencida, dos ventanas independientes, límite de 5 por minuto, creación y promoción de admin. |
| `test_cambio_contrasena.py` | Cambio exitoso (la vieja deja de servir), cierra las demás sesiones y conserva la actual, actual incorrecta suma fallos y bloquea, el cambio reinicia los fallos, nueva corta o repetida, sin sesión, reseteo por comando (desbloquea y cierra todas las sesiones). |
| `test_endpoints_protegidos.py` | `/health` público; `/profiles`, `/simulaciones` (también `/estados-internos`) y `/audiogram/*` dan 401 sin sesión; nombre de perfil inválido, 422. |
| `test_simulaciones.py` | Con el motor reemplazado por uno falso: RN3 (rangos, sin fibras, perfil inexistente), pedir deja en cola, el worker la ejecuta y la deja completada, orden de llegada, error del motor (mensaje genérico, libera el cupo), **RN10** (pedido idéntico reutilizado, sin cupo, la huella depende del contenido del perfil), **RN5a/b/c** (cupos por tipo, por hora, tope del sistema), **RN4**, caso opcional y filtro, paginación por cursor, recuperación de las interrumpidas y **estados internos** (se guardan aparte, no se duplican con RN10, endpoint propio con RN4). |
| `test_estados_internos.py` | Marca `lento`, fuera del `pytest` normal: corre el modelo real y verifica que w1/w3/w5 no cambian al guardar estados internos. `systemd-run --user --scope -p MemoryMax=3G -p MemorySwapMax=0 uv run pytest -m lento`. |
| `test_casos_api.py` | Crear, ver, editar (PUT reemplaza todo) y borrar (lógico) casos; validación de alias, edad, sexo y notas; orden y paginación por cursor (25 casos de a 10, sin repetir ni saltear); **RN4** (otro usuario recibe 404 al ver, editar o borrar, igual que con un id inexistente); sin sesión, 401. |

No hay tests automáticos del frontend: sus páginas se verifican con la tabla de la sección 3.

## 7. Si algo falla

| Síntoma | Causa y arreglo |
|---|---|
| `permission denied ... docker.sock` | Tu usuario no está en el grupo `docker` en esta sesión. Reiniciá la sesión del sistema. |
| `KeyError: 'DATABASE_URL'` | Falta el `.env`: `cp .env.example .env`. |
| La página dice "No se pudo conectar con el servidor" o "Backend Desconectado", pero el backend y Vite están corriendo | `frontend/.env` define `VITE_API_URL=http://localhost:8000` (lo traían versiones viejas del `.env.example`). Eso hace que el navegador le pegue directo al puerto 8000, sin `/api` y sin CORS. Comentá esa línea y recargá con Ctrl+Shift+R. |
| `[vite] http proxy error ... ECONNREFUSED` | El backend está apagado o todavía arrancando. Esperá unos segundos. |
| Iniciás sesión y al recargar volvés a no tener sesión | La cookie no se guardó. Revisá que `COOKIE_SECURE=false` esté en tu `.env` (con `true` solo viaja por HTTPS). |
| 429 todo el tiempo | Esperá un minuto (límite por IP) o 15 minutos (cuenta bloqueada); o desbloqueá con SQL. |
| Los tests fallan al conectarse | Falta `docker compose up -d db`. |
| La simulación se queda en "En cola" y no avanza | El worker no está corriendo. Con `npm run dev` arranca solo; si lo levantás por partes, `npm run dev:worker` (o `uv run python worker.py`). No se recarga solo: si cambiás código del backend, reinicialo. |
| Una simulación falla con "Perfil … no encontrado" o similar | El perfil se borró o cambió de nombre después de pedirla; ver el mensaje en el detalle. |

## 8. Dónde corregir cada cosa

| Quiero cambiar… | Archivo |
|---|---|
| Texto del aviso de uso no profesional | `frontend/src/pages/Registro.tsx` |
| Duración de la sesión, intentos máximos, minutos de bloqueo | `.env` (`SESION_HORAS`, `INTENTOS_MAX`, `BLOQUEO_MINUTOS`) |
| Límite de intentos por minuto | `LIMITE_INTENTOS` en `backend/views/autenticacion.py` |
| Largo de la contraseña, mensajes de error, reglas del cambio de contraseña | `backend/controller/autenticacion.py` |
| Pantalla *Mi cuenta* | `frontend/src/pages/MiCuenta.tsx` |
| Estado HTTP de cada error | `backend/views/errores.py` |
| Cookie (nombre, atributos) | `backend/views/autenticacion.py` y `backend/views/dependencias.py` |
| Colores de los botones | `frontend/src/components/estilos.ts` |
| Botones y datos del navbar | `frontend/src/components/BotonesSesion.tsx` |
| Requests y aserciones de Bruno | `docs/api/` |
| Campos de un caso y sus límites (alias, edad, sexo, notas) | `backend/controller/modelos.py` (`CasoInput`); si cambia una columna, también `backend/datos/tablas.py` y una migración |
| Qué casos ve cada usuario (RN4), orden y paginación | `backend/datos/casos.py` |
| Tamaño de página por defecto y máximo | `listar` en `backend/views/casos.py` y `backend/views/simulaciones.py` (servidor), y `casosApi.listar` / `simulacionesApi.listar` en `frontend/src/services/` |
| Cupos de simulaciones, tope de la cola, minutos para dar por interrumpida una simulación | `backend/configuracion.py` (`CUPO_SIMULTANEAS`, `CUPO_POR_HORA`, `TOPE_COLA`, `SIMULACION_MINUTOS_MAX`) |
| Rangos válidos de los parámetros (RN3) | `RANGOS` en `backend/controller/simulaciones.py` |
| Versión del modelo (invalida la caché) y semilla | `VERSION_MODELO` y `SEMILLA` en `backend/services/motor.py` |
| Cada cuánto se consulta el estado de una simulación | `INTERVALO_CONSULTA_MS` en `frontend/src/services/simulaciones.ts` |
| Pantallas de casos | `frontend/src/pages/casos/` |

## 9. Lo que todavía no está

- Los perfiles `Custom_*` del audiograma son compartidos entre usuarios (decisión 019): se resuelve en el módulo de audiogramas.
- No hay límite general de 120 pedidos por minuto por usuario (solo el de login y registro).
- Un admin todavía no tiene pantallas propias: solo se distingue por la insignia.
