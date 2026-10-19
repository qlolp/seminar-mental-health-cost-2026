#!/bin/sh
# Собирает PDF доклада. Нужен Chromium (путь можно задать переменной CHROME).
set -e
cd "$(dirname "$0")"
python3 figures.py
CHROME="${CHROME:-$(ls /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1)}"
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="../Сколько_стоит_достойная_жизнь_доклад_2026.pdf" "file://$PWD/report.html"
