# 019 — Endpoints del prototipo con sesión

**Fecha:** 2026-10-16 · **Estado:** aceptada

## Contexto
`/api/profiles`, `/api/simulate` y `/api/audiogram/*` seguían abiertos a cualquiera. `/simulate` es síncrono y usa un núcleo y ~1,1 GB de RAM durante ~75 s, así que un anónimo podía tumbar el servidor.

## Decisión
- **Piden sesión** (`usuario_actual`; sin ella, 401 `no_autenticado`): `GET /profiles`, `POST /simulate`, `POST /audiogram/upload` y `POST /audiogram/manual`. `GET /health` queda **público**: la barra superior lo consulta antes de iniciar sesión y sirve a un monitor externo; solo informa si el motor está disponible.
- **`poles_profile` solo admite letras, números, guion y guion bajo** (máximo 100): el nombre se usa para armar una ruta de archivo, y `../x` ahora responde 422.
- **Frontend:** `/` sin sesión muestra una pantalla de bienvenida (`pages/Bienvenida.tsx`) que cuenta qué se puede hacer e invita a registrarse o iniciar sesión; con sesión, `/` es el simulador. Los perfiles se piden solo con sesión.

## Alternativas descartadas
- **Un tope temporal de 1 simulación a la vez en todo el servidor:** se descartaría en el paso 5, que trae la cola y los cupos (RN5); el servidor todavía no está desplegado.
- **`/` pública con un aviso en lugar de una pantalla propia:** una bienvenida que explica las funciones invita más a registrarse.
- **Proteger también `/health`:** la barra no podría mostrar el estado del servidor antes de iniciar sesión.

## Consecuencias
- **Siguen pendientes, para el módulo de audiogramas:** los perfiles `Custom_<nombre>` se guardan en una carpeta compartida con el nombre del paciente. Dos usuarios con el mismo nombre se pisan el perfil, y `/profiles` muestra a cada uno los de los demás (contra RN4). La solución es ligar cada perfil a un audiograma de un caso.
- Hasta el paso 5, cualquier usuario registrado puede lanzar simulaciones en paralelo.
