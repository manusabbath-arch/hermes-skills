El script lee los dos CSV (separador `;`) y ubica las columnas por el nombre del encabezado. Esto hace falta porque abril y mayo traen `Importe` y `Cantidad` en orden distinto. Excluye el producto ENVÍO (flete) y suma `Importe` de las ventas de abril y mayo de 2026. Ignora filas mal formadas o fuera de esas fechas. No encontré ENVÍO ni importes en dólares en una búsqueda previa, pero el script los maneja por si acaso.

```python
import csv, glob, unicodedata
from datetime import datetime

def norm(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().strip().upper()

def num(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)

total = 0.0
for f in sorted(glob.glob("datos/t2/ventas_*.csv")):
    with open(f, encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh, delimiter=";")
        hdr = [norm(h) for h in next(rd)]
        iF, iP, iI = hdr.index("FECHA"), hdr.index("PRODUCTO"), hdr.index("IMPORTE")
        for r in rd:
            if len(r) <= max(iF, iP, iI):
                continue
            try:
                d = datetime.strptime(r[iF].strip(), "%d/%m/%Y")
                imp = num(r[iI])
            except ValueError:
                continue
            if d.year != 2026 or d.month not in (4, 5):
                continue
            if norm(r[iP]) == "ENVIO":
                continue
            total += imp

if total == int(total):
    total = int(total)
print("CIFRA: %s" % total)
```
