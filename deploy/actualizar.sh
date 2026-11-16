#!/usr/bin/env bash
# Sube a producción lo último de la rama que tiene clonada la VM (main) (decisión 029).
# Se corre a mano en la VM, desde la carpeta del repo:   ./deploy/actualizar.sh
set -euo pipefail
cd "$(dirname "$0")/.."
COMPOSE="sudo docker compose -f compose.prod.yaml"

echo "== 1/4 Backup antes de migrar"
# Si falla la subida al Drive se sigue igual: el dump local alcanza para volver atrás
./deploy/backup.sh || echo "   (sin subida al Drive: el dump quedó en backups/)"

echo "== 2/4 Trayendo el código"
git pull --ff-only

echo "== 3/4 Construyendo las imágenes"
$COMPOSE build
sudo docker builder prune -f

echo "== 4/4 Migraciones y reinicio"
$COMPOSE run --rm api alembic upgrade head
$COMPOSE up -d

echo "Listo. Comprobá /api/health."
