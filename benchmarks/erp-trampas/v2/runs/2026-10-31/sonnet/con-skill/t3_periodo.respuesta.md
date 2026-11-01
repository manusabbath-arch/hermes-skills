El archivo se llama "Ventas 2026 YTD", pero el preámbulo declara el período **01/03/2026 al 31/03/2026**, es decir 31 días. Los datos son de la empresa A, con importes enteros en pesos. En una revisión por patrón no encontré filas con fechas fuera de marzo ni importes no numéricos, ni totales ni filas de ENVÍO.

El script hace esto:
- Lee el período del preámbulo, no del nombre del archivo.
- Ignora subtotales y filas de flete (ENVÍO), por si aparecen.
- Suma los importes de las filas de detalle que caen dentro del período.
- Divide esa suma por los días calendario del período, incluidos los días sin ventas.

```python
import csv, re, sys, glob
from datetime import datetime, date

path = glob.glob("datos/t3/*.csv")[0]
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    text = raw.decode("cp1252")
lines = text.splitlines()

m = None
for l in lines[:10]:
    m = re.search(r"(\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})", l)
    if m:
        break
if not m:
    print("CIFRA: NO DETERMINABLE"); sys.exit()
d0 = datetime.strptime(m.group(1), "%d/%m/%Y").date()
d1 = datetime.strptime(m.group(2), "%d/%m/%Y").date()
ndays = (d1 - d0).days + 1

hdr = next(i for i, l in enumerate(lines) if l.lower().startswith("fecha;"))
rows = list(csv.reader(lines[hdr:], delimiter=";"))
cols = [c.strip().lower() for c in rows[0]]
if, ic, im = cols.index("fecha"), cols.index("cliente"), cols.index("importe")

def num(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)

total = 0.0
read = skipped = out = 0
for r in rows[1:]:
    if not r or len(r) <= max(if, ic, im):
        continue
    if re.search(r"total|env[ií]o", ";".join(r), re.I):
        skipped += 1
        continue
    try:
        d = datetime.strptime(r[if].strip(), "%d/%m/%Y").date()
        v = num(r[im])
    except Exception:
        skipped += 1
        continue
    if not (d0 <= d <= d1):
        out += 1
        continue
    total += v
    read += 1

print(f"archivo={path} periodo={d0}..{d1} dias={ndays} filas={read} descartadas={skipped} fuera_periodo={out} total={total}")
if read == 0:
    print("CIFRA: NO DETERMINABLE")
else:
    print(f"CIFRA: {total / ndays:.2f}")
```
