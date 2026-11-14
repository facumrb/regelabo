# 029 — Despliegue en producción

**Fecha:** 2026-11-12 · **Estado:** aceptada; ajustada el 2026-11-13 (arranque en Azure, ver abajo)

Reemplaza la [011](011-infraestructura.md) (hosting y dominio) y, en lo que hace a producción, la [003](003-base-de-datos.md) (Supabase como base). Ajusta la cantidad de workers de la [027](027-prioridad-en-la-cola.md).

## Contexto
- El checklist de la cátedra exige el sistema **desplegado, online y accesible desde cualquier dispositivo**. La entrega es la semana del 2026-11-16 y todavía no hay nada desplegado (ni siquiera un `Dockerfile`).
- **Presupuesto cero:** no se puede pagar nada, ni siquiera con crédito que requiera gastar.
- Cada simulación usa ~1,1 GB de RAM y un núcleo durante ~80 s; con `storeflag` `d` completo el pico llega a ~6 GB (023). Cada una guarda ~4,6 MB de estados internos.
- Un integrante propuso repartir el sistema en 5 servicios gratuitos (ver alternativas).
- Ningún integrante hizo un despliegue antes: se prioriza pocas piezas y un procedimiento escrito.
- Si se pierde la máquina o la cuenta, hay que poder recuperar el sistema o mudarlo.

## Decisión
- **Máquina:** Oracle Cloud Always Free, instancia ARM (Ampere A1) de **2 núcleos y 12 GB** (el plan gratis se redujo a la mitad en 2026), región **Santiago** (`sa-santiago-1`), Ubuntu. **Sin Pay As You Go.** La cuenta usa el mail del proyecto; la tarjeta de verificación es de un integrante (Oracle no acepta prepagas ni virtuales).
- **Servicios**, en un `compose.prod.yaml` con reinicio automático:
  - `caddy`: HTTPS automático (Let's Encrypt), sirve el frontend compilado y reenvía `/api` a la API en el mismo dominio (sin CORS, cookie `SameSite=Lax` intacta).
  - `api`: FastAPI.
  - `worker` ×2, con prioridad baja (`nice`) para que la API responda aunque haya 2 simulaciones corriendo. La cola ya permite varios workers (`skip_locked`).
  - `db`: PostgreSQL 17 con un volumen persistente.
- **Imágenes:** un `Dockerfile` para el backend (compila el solver C adentro; la misma imagen para `api` y `worker`) y una etapa que compila el frontend. Se construyen **en la VM**, así el mismo repo anda en ARM y en x86.
- **Dominio:** `regelabo.duckdns.org` (DuckDNS, gratis) apuntando a una **IP pública reservada**. Puertos 80 y 443 abiertos en la *Security List* de Oracle **y** en el `iptables` de la imagen de Ubuntu.
- **Backups:** `pg_dump` diario (`cron`) comprimido y subido con `rclone` al Google Drive del proyecto, guardando los últimos 7; además, un dump antes de cada migración. Fuera de Oracle a propósito: si se pierde la cuenta, el backup sigue.
- **Monitoreo:** UptimeRobot (gratis) consulta `GET /api/health` cada 5 min y avisa por mail al proyecto.
- **Mudanza:** `deploy/instalar.sh` deja una Ubuntu vacía con el sistema andando; `docs/despliegue.md` describe cómo mudarse (VM nueva → `instalar.sh` → restaurar el último dump → cambiar la IP en DuckDNS) en menos de 1 hora. La restauración se prueba una vez antes de la entrega. **Plan B:** Azure for Students (sin tarjeta, con el mail de la facultad).
- **Actualizaciones:** a mano, por SSH, con `deploy/actualizar.sh` (dump → `git pull` de `main` → build → `alembic upgrade head`). El despliegue automático llega con el CI del paso 6.
- **Swagger** (`/api/docs` y `/api/openapi.json`): solo con sesión de admin. No hace secreta la API (se ve desde el navegador), pero no entrega un mapa listo.
- **Admin de producción:** con el comando `crear_admin`; una cuenta aparte para la cátedra si la pide.
- **Cuentas y secretos:** Oracle, DuckDNS, Google Drive y UptimeRobot con el mail del proyecto. Cada integrante entra por SSH con su propia clave. Las contraseñas, el token de DuckDNS y los códigos de recuperación del segundo factor de Oracle van a una bóveda de Bitwarden del proyecto. El `.env` de producción existe solo en la VM (y en la bóveda), con `COOKIE_SECURE=true`.

## Ajuste del 2026-11-13: arranque en Azure
- No hubo tarjeta disponible para verificar Oracle a tiempo, así que **el primer despliegue va a Azure for Students** (sin tarjeta, con el mail de la UTN): VM x86 B2s de 2 núcleos y 4 GB, Ubuntu 24.04. Oracle sigue siendo el destino cuando haya tarjeta, con el procedimiento de mudanza.
- La cantidad de workers pasa a `WORKERS` en el `.env` (`instalar.sh` la elige según la RAM): **1 en Azure**, 2 en Oracle.
- Los puertos 80, 443 y 22 se abren en el *Network Security Group* de Azure; el paso de `iptables` de `instalar.sh` no molesta ahí.
- DuckDNS se mantiene (Azure da un nombre propio, pero DuckDNS permite mudarse cambiando solo la IP).
- El crédito (US$100) alcanza para ~2,5–3 meses de VM, disco e IP.

## Alternativas descartadas
| Alternativa | Por qué no |
|---|---|
| **Propuesta de 5 servicios** (Cloudflare Pages + Workers, Oracle para el cómputo, Supabase Auth + base, Upstash Redis, Cloudflare Queues) | Obliga a reescribir autenticación (004, 013), cola y worker (005, 020, 027) y límites (009) en una semana. Supabase Auth rompe el ítem "el negocio seguiría funcionando si se cambiara el motor de base". Cloudflare Queues no tiene prioridad (RN11) y en el plan gratis borra mensajes a las 24 h. Supabase gratis da 500 MB (~100 simulaciones con estados internos) y se pausa tras 7 días sin uso. Upstash solo hace falta con varias instancias de la API (009). Cinco cuentas y paneles que operar. Queda como posible evolución si el sistema sigue después del TPI. |
| **DigitalOcean con el Student Pack** (011) | Pide tarjeta o PayPal y esperar la aprobación del Pack (días); el crédito se termina en ~8 meses. |
| **Azure for Students** | Sin tarjeta y se activa en el día, pero 4 GB (2 simulaciones justas) y el crédito dura ~3 meses. Es el plan B. |
| **Oracle con Pay As You Go** | Evita el reclamo por inactividad, pero deja la tarjeta expuesta a cobros por error. |
| **Supabase como base en producción** (003) | El límite de 500 MB alcanzaba para ~10 000 simulaciones antes de los estados internos; ahora, ~100. |
| **Postgres administrado de DigitalOcean** | ~US$15/mes. |
| **Backup en la VM o en Object Storage de Oracle** | Se pierde junto con la cuenta. Cloudflare R2 pide tarjeta. |
| **Cloudflare Pages + Worker como puerta de entrada** | Un Worker no puede llamar a una IP directa (error 1003): el backend necesita igual un nombre como el de DuckDNS. Suma piezas sin aportar para la entrega; queda como mejora (con el `.me` del Student Pack, si llega). |
| **Despliegue automático en cada merge** | Sin CI, sube a producción lo que llegue a `main`, incluso roto. |
| **Swagger público** | Entrega el mapa de la API a cualquiera. |

## Consecuencias
- **Riesgo aceptado:** sin Pay As You Go, Oracle puede reclamar la VM si queda ociosa (CPU, red y memoria por debajo del 20 % durante 7 días). Se cubre con el monitor y la mudanza documentada, no evitándolo.
- Oracle permite una sola cuenta gratis por persona: si rechaza la tarjeta, no se reintenta con otra cuenta; se pasa a Azure.
- La base y sus backups pasan a ser responsabilidad del equipo (lo que la 003 quería evitar).
- `worker.py` corre en 2 procesos sin haber hecho la medición que pedía la 027; se mide en la VM y se baja a 1 si la API se resiente.
- El solver C y las dependencias se compilan en ARM por primera vez: se prueba en la VM antes de dar el despliegue por hecho.
- Hay que crear `Dockerfile`, `compose.prod.yaml`, `Caddyfile`, `deploy/` (`instalar.sh`, `actualizar.sh`, `backup.sh`) y `docs/despliegue.md`, y proteger Swagger en `views/`.
