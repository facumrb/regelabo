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
