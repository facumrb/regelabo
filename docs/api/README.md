# Colección de Bruno: API de regelabo

Requests con sus aserciones para probar la API a mano o por terminal. Son archivos de texto (`.bru`) que se versionan con el código: un `git clone` y el equipo ya la tiene.

## Abrirla

1. Instalar [Bruno](https://www.usebruno.com) (no está en los repos oficiales de Arch; instalarlo desde su sitio, Flatpak o AUR).
2. **Open Collection** y elegir la carpeta `docs/api`.
3. Arriba a la derecha, elegir el entorno:
   - `desarrollo`: le pega directo al backend, `http://localhost:8000/api`.
   - `vite`: pasa por el proxy de Vite, `http://localhost:5173/api` (como el navegador).
4. Para correrla toda: clic derecho sobre la colección → **Run**. Corre en orden las carpetas `0` a `6`, pero `4-casos`, `5-cuenta` y `6-simulaciones` van a dar 429 (ver *Límite de pedidos*): conviene correr `0`–`3`, y pasado un minuto cada una de las otras sola (clic derecho sobre la carpeta → **Run**).

El backend tiene que estar corriendo (`npm run dev`, o `uv run fastapi dev app.py`) y la base levantada (`docker compose up -d db`).

## Por terminal

```bash
cd docs/api
pnpm dlx @usebruno/cli run 0-estado 1-flujo-feliz 2-errores 3-manuales -r --env desarrollo
# pasado un minuto:
pnpm dlx @usebruno/cli run 4-casos -r --env desarrollo
# pasado otro minuto, cada una:
pnpm dlx @usebruno/cli run 5-cuenta -r --env desarrollo
pnpm dlx @usebruno/cli run 6-simulaciones -r --env desarrollo
```

Opciones útiles: `--env vite` para el otro entorno, `--env-var base_url=http://localhost:8010/api` para apuntar a otro backend, `--reporter-html resultado.html` para guardar un informe.

## Qué hay en cada carpeta

| Carpeta | Qué prueba |
|---|---|
| `0-estado` | El backend responde: `/health` y `/` (públicos), y `/profiles` **sin sesión da 401**. |
| `1-flujo-feliz` | Registro → login → `yo` → logout → `yo` con el **mismo token** (tiene que dar 401: el logout lo invalida en el servidor). |
| `2-errores` | Registro sin aviso (400), contraseña corta (400), email inválido (422), email repetido incluso en mayúsculas (409), login con clave incorrecta y con email inexistente (401, **respuestas idénticas**), `yo` sin sesión y con un token inventado (401). |
| `3-manuales` | El límite de 5 pedidos por minuto y el bloqueo de cuenta a los 10 fallos. Hay que enviarlas varias veces y esperar, así que **no están pensadas para correrse en bloque** (en una corrida completa responden 401 y pasan). El procedimiento está en la pestaña *Docs* de cada request. |
| `4-casos` | El módulo de ejemplo. Crea su propia dueña y un segundo usuario (no depende de las otras carpetas): crear → listar (paginación por cursor) → ver → editar (PUT reemplaza todo) → **RN4**: el otro usuario recibe 404 al ver o borrar el caso y no lo ve en su lista → borrar (lógico) → ver el borrado (404) → sexo inválido y límite fuera de rango (422) → sin sesión (401). |
| `6-simulaciones` | Pedir una simulación (202), listar, ver, RN3 (nivel fuera de rango, sin fibras, perfil inexistente, nombre inválido), RN4 (otro usuario recibe 404 y no la ve en su lista), sin sesión (401) y sus estados internos (200, o 404 si todavía no terminó). Con un worker corriendo (`npm run dev`) la simulación se ejecuta de verdad (~80 s). Los cupos, la caché y el worker los prueba pytest. |
| `5-cuenta` | Cambio de contraseña. Crea su propio usuario: actual incorrecta, nueva corta y nueva repetida (400) → cambio (204) → la sesión actual sigue → login con la vieja (401) y con la nueva (200) → sin sesión (401). Que se cierren las **otras** sesiones lo prueba pytest. |

Cada request verifica el estado HTTP, el `codigo` del error y, donde corresponde, la cookie. Los errores de formato (422) conservan el formato de FastAPI: `detail` es una lista.

## Cosas a tener en cuenta

- **Límite de pedidos.** El registro y el login admiten 5 pedidos por minuto por IP. Las carpetas `0`–`3` usan **5 de 5 en cada uno**, así que si las repetís antes de un minuto, varias requests van a dar 429. Esperá un minuto entre corridas (se comprobó: la segunda corrida inmediata falla y la siguiente, pasado el minuto, pasa). `4-casos` usa 2 registros y 2 logins más, y `5-cuenta` 1 registro y 3 logins: por eso cada una va en una corrida aparte.
- **Orden.** Las carpetas `2` y `3` dependen de la `1`: `1-flujo-feliz` crea el usuario (`bruno-<fecha>@example.com`) que usan las demás. Si corrés una request suelta de `2-errores` o `3-manuales`, correr antes el flujo feliz.
- **La cookie.** El login guarda el token en una variable (`token`, `token_ana`, `token_beto`) y las requests siguientes lo mandan en el header `Cookie`, para poder probar el token viejo después del logout. Ojo: Bruno **además** guarda la cookie del último login y la manda por su cuenta, por encima del header. Con dos usuarios eso mezcla las sesiones; por eso `4-casos` hace logout del segundo usuario (request 12) antes de volver a la dueña. Al escribir requests nuevas con dos usuarios, hacer lo mismo.
- **Datos que crea.** Usuarios `bruno-…@example.com` en la base a la que apunte el backend. `4-casos` además deja sus casos (borrados lógicamente). Para borrar todo:
  ```sql
  delete from caso where usuario_id in (select id from usuario where email like 'bruno-%');
  delete from usuario where email like 'bruno-%';
  ```

## Qué falta

Las rutas del prototipo `/audiogram/*` no tienen requests (piden sesión; `/profiles` sí, en `1-flujo-feliz`; `/simulate` ya no existe): las van a reemplazar los módulos de casos y simulación. Para traerlas igual, en Bruno: **Import Collection → OpenAPI** con `http://localhost:8000/api/openapi.json`.

Al sumar un módulo, agregarle su carpeta (`5-…`) con el flujo feliz y sus errores, tomando `4-casos` como modelo. Para crear una request nueva, copiar una existente y cambiar la ruta, el cuerpo y los `tests`.
