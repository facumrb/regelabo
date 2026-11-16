#!/usr/bin/env bash
# Deja una VM Ubuntu vacía con regelabo andando (decisión 029). Se corre una sola vez, en la VM,
# desde la carpeta del repo clonado:
#
#   git clone https://github.com/facumrb/regelabo.git
#   cd regelabo
#   ./deploy/instalar.sh regelabo.duckdns.org
#
# Se puede volver a correr sin romper nada: cada paso revisa si ya está hecho.
set -euo pipefail

DOMINIO="${1:?Uso: ./deploy/instalar.sh <dominio>   (ej. regelabo.duckdns.org)}"
cd "$(dirname "$0")/.."
# Un worker por cada ~4 GB de RAM, máximo 2 (decisión 029): Azure B2s → 1, Oracle A1 12 GB → 2
RAM_GB=$(awk '/MemTotal/ {print int($2 / 1024 / 1024)}' /proc/meminfo)
WORKERS=$(( RAM_GB >= 8 ? 2 : 1 ))
COMPOSE="sudo docker compose -f compose.prod.yaml"

echo "== 1/6 Instalando Docker y rclone"
sudo apt-get update -q
sudo apt-get install -y -q docker.io docker-compose-v2 rclone
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"   # para usar docker sin sudo desde la próxima sesión

echo "== 2/6 Abriendo los puertos 80 y 443 en el firewall de la VM"
# Las imágenes de Ubuntu de Oracle traen iptables cerrado salvo SSH. Esto se suma a la
# Security List del panel de Oracle: hacen falta las dos.
for puerto in 80 443; do
  if ! sudo iptables -C INPUT -p tcp --dport "$puerto" -j ACCEPT 2>/dev/null; then
    sudo iptables -I INPUT -p tcp --dport "$puerto" -j ACCEPT
  fi
done
if command -v netfilter-persistent >/dev/null; then
  sudo netfilter-persistent save   # que sobreviva a un reinicio
fi

echo "== 3/6 Archivo .env de producción"
if [ ! -f .env ]; then
  umask 077   # solo lo puede leer este usuario
  cat > .env <<EOF
DOMINIO=$DOMINIO
POSTGRES_PASSWORD=$(openssl rand -hex 24)
WORKERS=$WORKERS
EOF
  echo "   Creado. Copiá su contenido a Bitwarden: es la única copia de la contraseña de la base."
else
  echo "   Ya existe: no se toca."
fi

echo "== 4/6 Construyendo las imágenes (tarda varios minutos la primera vez)"
$COMPOSE build
sudo docker builder prune -f   # la caché de build no hace falta después y ocupa GB

echo "== 5/6 Migraciones y arranque"
$COMPOSE up -d db
$COMPOSE run --rm api alembic upgrade head
$COMPOSE up -d

echo "== 6/6 Backup diario (04:00 UTC)"
LINEA="0 4 * * * cd $PWD && ./deploy/backup.sh >> $PWD/backups/backup.log 2>&1"
mkdir -p backups
if ! crontab -l 2>/dev/null | grep -qF "deploy/backup.sh"; then
  (crontab -l 2>/dev/null; echo "$LINEA") | crontab -
fi

echo
echo "Listo. Comprobá https://$DOMINIO/api/health (c_solver_available tiene que ser true)."
echo "Pendiente a mano (ver docs/despliegue.md):"
echo "  - Crear el admin:      $COMPOSE exec api python -m backend.comandos.crear_admin"
echo "  - Conectar el Drive:   rclone config   (remoto 'drive', carpeta regelabo-backups)"
