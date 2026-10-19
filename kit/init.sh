#!/usr/bin/env bash
# Arranque de cada sesión: deja el entorno listo y prueba que está sano.
# Mismo comando en la máquina de cualquiera y en el CI.
set -euo pipefail
cd "$(dirname "$0")"
. tools/find_python.sh

if [ ! -d .git ]; then
  git init -q -b main
fi
git config core.hooksPath .githooks

"$PYTHON" tools/kit_check.py
"$PYTHON" -m unittest discover -s tests -q

echo
echo "init.sh: verde. Siguiente: leer progress.md y elegir UNA feature con passes=false"
echo "en feature_list.json."
