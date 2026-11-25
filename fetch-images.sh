#!/usr/bin/env bash
# Скачивает скриншоты кейсов из старого портфолио в assets/cases/,
# чтобы страницы не зависели от keprah.github.io.
# Запуск (из папки проекта):  bash fetch-images.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets/cases
BASE="https://keprah.github.io/portfolio/assets/img"
KEYS="crm_pc crm_phone crm_flow crm_meet fin_main fin_sales fin_plan fin_anim fin_proto fin_wire fin_layout ds_vars"
n=0
for k in $KEYS; do
  curl -fsSL "$BASE/$k.webp" -o "assets/cases/$k.webp" && n=$((n+1)) || echo "не удалось: $k"
done
echo "Готово: $n из 12 файлов в assets/cases/"
