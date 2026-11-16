# Despliegue

Cómo poner regelabo online (decisión [029](decisiones/029-despliegue.md)). Todo usa los mismos archivos: `Dockerfile`, `compose.prod.yaml` y `deploy/`.

## Provisorio: GitHub Codespaces

Para tener el sistema online sin servidor (presentación, corrección, pruebas). Es gratis: 120 horas-núcleo por mes con una cuenta común y 180 con el Student Pack (~90 h en una máquina de 2 núcleos). **No queda prendido siempre:** se apaga tras un rato sin uso (máximo 4 h) y hay que volver a prenderlo.

### Una sola vez
1. **Tiempo de apagado:** en GitHub, *Settings → Codespaces → Default idle timeout*, poner `240` (minutos).
2. **Crear el codespace:** en el repo, *Code → Codespaces → `...` → New with options*. Elegir la rama que tenga el `Dockerfile` y la máquina de **4 núcleos** (2 simulaciones a la vez) o de **2 núcleos** (gasta la mitad de horas, 1 simulación).
3. En la terminal del codespace, crear el `.env` (cambiar `WORKERS` a `1` en la máquina de 2 núcleos):
   ```bash
   printf 'DOMINIO=:80\nPOSTGRES_PASSWORD=%s\nWORKERS=2\n' "$(openssl rand -hex 24)" > .env
   ```
   Para los mails (decisión 030), agregar al `.env` las líneas de **Mails** (más abajo), con `URL_PUBLICA` igual a la dirección `https://...app.github.dev` del paso 5. Sin ellas, los mails solo quedan en el log (`docker compose -f compose.prod.yaml logs api`).
4. Construir y arrancar (la primera vez tarda varios minutos):
   ```bash
   docker compose -f compose.prod.yaml build
   docker compose -f compose.prod.yaml up -d db
   docker compose -f compose.prod.yaml run --rm api alembic upgrade head
   docker compose -f compose.prod.yaml up -d
   docker compose -f compose.prod.yaml exec api python -m backend.comandos.crear_admin
   ```
5. **Hacerlo público:** pestaña *Ports* (al lado de *Terminal*). Si no aparece el puerto `80`, *Add Port* → `80`. Clic derecho sobre él → *Port Visibility* → **Public**. La columna *Forwarded Address* tiene la dirección `https://...app.github.dev` para compartir.
6. Comprobar `https://<esa dirección>/api/health` (`c_solver_available` tiene que ser `true`).

### Cada vez que se usa
- **Prender:** github.com/codespaces → el codespace → *Open*. Los contenedores arrancan solos (`restart: unless-stopped`); si no, `docker compose -f compose.prod.yaml up -d`. La dirección y la base se mantienen.
- **Revisar que el puerto 80 siga en Public**: a veces vuelve a *Private* al reiniciar.
- **Apagar al terminar:** github.com/codespaces → `...` → *Stop codespace*, para no gastar horas.
- **No borrar el codespace:** se pierde la base de datos y cambia la dirección.

### Límites conocidos
- Todas las visitas llegan desde el proxy de GitHub: el límite de 5 logins/registros por minuto (009) puede ser compartido entre todos. Si molesta en la presentación, avisar antes de entrar todos juntos.
- Sin backups: es provisorio. Lo que se cargue acá no se muda al servidor definitivo.

## Servidor definitivo (VM Ubuntu: Azure, Oracle, VPS o la de la cátedra)

### Instalar
1. Crear la VM (Ubuntu 24.04) y abrir los puertos 22, 80 y 443 en el firewall del proveedor (*Network Security Group* en Azure, *Security List* en Oracle).
2. En DuckDNS, apuntar `regelabo.duckdns.org` a la IP pública de la VM.
3. Por SSH, en la VM:
   ```bash
   git clone https://github.com/facumrb/regelabo.git
   cd regelabo
   ./deploy/instalar.sh regelabo.duckdns.org
   sudo docker compose -f compose.prod.yaml exec api python -m backend.comandos.crear_admin
   ```
4. Copiar el `.env` que generó `instalar.sh` a Bitwarden.

### Mails (verificación y recuperación, decisión 030)
**Sin SMTP el sistema funciona igual**, pero los mails no salen (quedan en `logs api`) y los usuarios nuevos no pueden simular hasta verificar su email (RN15). Mientras tanto, el admin los destraba desde **Administración → Usuarios → Verificar email**, y los pedidos de "olvidé mi contraseña" le aparecen en el mismo panel.

Agregar al `.env` de la VM (y a Bitwarden) y reiniciar con `sudo docker compose -f compose.prod.yaml up -d`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USUARIO=<gmail del proyecto>
SMTP_CONTRASENA=<contraseña de aplicación>
```
La contraseña de aplicación se crea en la cuenta de Google del proyecto: *Seguridad* → activar la verificación en 2 pasos → *Contraseñas de aplicaciones* → crear una llamada "regelabo". `URL_PUBLICA` (la dirección que va en los enlaces) toma `https://<DOMINIO>` sola; solo hace falta definirla en el Codespace. Probar con "¿Olvidaste tu contraseña?" usando un email real registrado; si no llega, el error está en `sudo docker compose -f compose.prod.yaml logs api`.

### Conectar el Drive para los backups
La VM no tiene navegador, así que el permiso se da desde una PC que tenga `rclone` instalado:
1. En la VM: `rclone config` → `n` (nuevo) → nombre `drive` → tipo `drive` → *client_id* y *client_secret* vacíos → *scope* `1` (acceso completo) → Enter en lo demás hasta *Use web browser to automatically authenticate?* → **`n`**.
2. rclone muestra un comando `rclone authorize "drive" "..."`. Correrlo en la PC: abre el navegador, entrar con la **cuenta de Google del proyecto** y aceptar.
3. La PC imprime un token (un bloque `{...}`): pegarlo en la VM y terminar con Enter / `y`.
4. Probar: `./deploy/backup.sh` tiene que terminar con `subido a drive:regelabo-backups`.

Los backups quedan en `backups/` (en la VM) y en la carpeta `regelabo-backups` del Drive: los últimos 7 en cada lado. El log del cron está en `backups/backup.log`.

### Actualizar
```bash
cd regelabo && ./deploy/actualizar.sh
```
Hace un backup, `git pull`, construye, migra y reinicia. Si algo sale mal después de migrar, restaurar el dump que acaba de hacer (ver abajo).

### Restaurar un backup
```bash
COMPOSE="sudo docker compose -f compose.prod.yaml"
rclone copy drive:regelabo-backups/<archivo>.dump backups/     # si no está ya en backups/
$COMPOSE stop api worker
$COMPOSE exec -T db pg_restore -U regelabo -d regelabo --clean --if-exists < backups/<archivo>.dump
$COMPOSE up -d
```

### Mudarse a otra VM (objetivo: menos de 1 hora)
1. En la VM vieja, si sigue viva: `./deploy/backup.sh` y copiar los perfiles generados por audiogramas: `sudo docker compose -f compose.prod.yaml cp api:/app/backend/services/verhulst/data/Poles ./polos`. Bajar esa carpeta con `scp`.
2. VM nueva: pasos de **Instalar** (sin `crear_admin`: el admin viene en el backup) y **Conectar el Drive**.
3. **Restaurar** el último backup.
4. Si se trajo `polos/`: `sudo docker compose -f compose.prod.yaml cp ./polos/. api:/app/backend/services/verhulst/data/Poles`. Sin esa carpeta, los casos con audiograma cargado hay que volver a subirles el audiograma.
5. Cambiar la IP en DuckDNS. El certificado HTTPS lo saca Caddy solo cuando el dominio ya apunta a la VM nueva.
6. Comprobar `/api/health` y entrar con el admin. Recién ahí apagar la VM vieja.
