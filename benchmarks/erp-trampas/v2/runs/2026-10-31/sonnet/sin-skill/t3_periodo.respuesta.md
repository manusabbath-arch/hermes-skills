El export es de ventas de marzo 2026 (01/03 al 31/03). Tiene columnas Fecha, Cliente e Importe, ya en pesos, y no trae columna de producto, así que no hay fletes (ENVÍO) para excluir. Las 2200 filas de datos tienen todas el mismo formato.

El script lee el período del encabezado y suma los importes de las filas cuya fecha cae dentro de ese período. Divide el total por la cantidad de días calendario del período, 31, y no por los días con ventas. Así los días sin ventas cuentan como cero.

```python
import csv, re, glob
from datetime import datetime, timedelta

path = glob.glob("datos/t3/*.csv")[0]
with open(path, encoding="utf-8-sig", newline="") as f:
    lines = f.read().splitlines()

ini = fin = None
total = 0.0
for ln in lines:
    m = re.search(r"Per[ií]odo:\s*(\d{2}/\d{2}/\d{4})\s*al\s*(\d{2}/\d{2}/\d{4})", ln)
    if m:
        ini = datetime.strptime(m.group(1), "%d/%m/%Y")
        fin = datetime.strptime(m.group(2), "%d/%m/%Y")
        break

rows = []
for ln in lines:
    p = ln.split(";")
    if len(p) != 3:
        continue
    try:
        d = datetime.strptime(p[0].strip(), "%d/%m/%Y")
        imp = float(p[2].strip().replace(",", "."))
    except ValueError:
        continue
    rows.append((d, imp))

if ini is None or not rows:
    print("CIFRA: NO DETERMINABLE")
else:
    total = sum(i for d, i in rows if ini <= d <= fin)
    dias = (fin - ini).days + 1
    print("Total:", total, "Días:", dias)
    print(f"CIFRA: {total / dias:.2f}")
```
