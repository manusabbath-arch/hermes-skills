# Elige un Python >= 3.10. Lo usan init.sh y el pre-commit; respeta $PYTHON.
# En Windows, `python3` puede ser el atajo de la Store que no ejecuta nada: se prueba.
if [ -z "${PYTHON:-}" ]; then
  for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
      PYTHON="$c"; break
    fi
  done
fi
if [ -z "${PYTHON:-}" ]; then
  echo "no hay Python >= 3.10 en el PATH (o definir PYTHON=/ruta/a/python)" >&2
  exit 1
fi
