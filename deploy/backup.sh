#!/usr/bin/env bash
# Copia de la base (decisión 029): pg_dump en backups/ y subida al Drive del proyecto con rclone
# (remoto "drive", carpeta regelabo-backups). Guarda los últimos 7 en cada lado.
# La corre el cron que programa instalar.sh (04:00 UTC) y actualizar.sh antes de migrar.
set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE="sudo docker compose -f compose.prod.yaml"
DESTINO="drive:regelabo-backups"
ARCHIVO="backups/regelabo-$(date -u +%Y%m%d-%H%M%S).dump"
mkdir -p backups

# Se escribe en .tmp y se renombra al final: un dump cortado nunca queda como si fuera bueno
$COMPOSE exec -T db pg_dump -U regelabo -Fc regelabo > "$ARCHIVO.tmp"
mv "$ARCHIVO.tmp" "$ARCHIVO"
echo "$(date -u '+%F %T') dump local: $ARCHIVO"
ls -1 backups/*.dump | head -n -7 | xargs -r rm --

if ! rclone listremotes | grep -qx "drive:"; then
  echo "AVISO: no hay remoto 'drive' en rclone (ver docs/despliegue.md); el dump quedó solo en la VM." >&2
  exit 1
fi
rclone copy "$ARCHIVO" "$DESTINO"
rclone lsf "$DESTINO" --files-only | sort | head -n -7 | while read -r viejo; do
  rclone deletefile "$DESTINO/$viejo"
done
echo "$(date -u '+%F %T') subido a $DESTINO"
