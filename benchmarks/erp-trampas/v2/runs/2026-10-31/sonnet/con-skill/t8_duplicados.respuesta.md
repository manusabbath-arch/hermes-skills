Los dos exports se solapan del 08 al 10/09. Si sumara ambos, esos cobros entrarían dos veces. El script deduplica por comprobante (Serie + Número).

El script hace lo siguiente:
- Lee los dos CSV (`;` como separador, el encabezado real está en la fila `Fecha;...`).
- Descarta los subtotales y las filas que no tengan fecha válida.
- Se queda con las fechas del 01/09/2026 al 14/09/2026.
- Cuenta una sola vez cada comprobante, aunque aparezca en los dos archivos.
- Imprime diagnósticos (filas leídas, duplicados, conflictos) y termina con `CIFRA:`.

```python
import csv, io, sys
from datetime import date, datetime
from decimal import Decimal

ARCHIVOS = ["datos/t8/cobros_01_al_10.csv", "datos/t8/cobros_08_al_14.csv"]
DESDE, HASTA = date(2026, 9, 1), date(2026, 9, 14)

def leer(path):
    raw = open(path, "rb").read()
    try:
        txt = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        txt = raw.decode("cp1252")
    return txt.splitlines()

def monto(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return Decimal(s)

vistos = {}
total_filas = 0
descartadas = 0
duplicados = 0
conflictos = 0
for path in ARCHIVOS:
    lineas = leer(path)
    idx = next(i for i, l in enumerate(lineas) if l.startswith("Fecha;"))
    n = 0
    for fila in csv.reader(lineas[idx + 1:], delimiter=";"):
        if len(fila) < 5:
            descartadas += 1
            continue
        try:
            f = datetime.strptime(fila[0].strip(), "%d/%m/%Y").date()
            imp = monto(fila[4])
        except Exception:
            descartadas += 1  # TOTAL, vacías, etc.
            continue
        n += 1
        total_filas += 1
        clave = (fila[1].strip(), fila[2].strip())
        val = (f, fila[3].strip(), imp)
        if clave in vistos:
            duplicados += 1
            if vistos[clave] != val:
                conflictos += 1
            continue
        vistos[clave] = val
    print(f"{path}: {n} filas de datos", file=sys.stderr)

total = sum(v[2] for v in vistos.values() if DESDE <= v[0] <= HASTA)
fuera = sum(1 for v in vistos.values() if not (DESDE <= v[0] <= HASTA))
print(f"filas leídas={total_filas} descartadas={descartadas} duplicados={duplicados} "
      f"conflictos={conflictos} comprobantes únicos={len(vistos)} fuera de rango={fuera}")
total = total.normalize() if total != total.to_integral() else total.quantize(Decimal(1))
print(f"CIFRA: {total}")
```
