El archivo es un único CSV con separador `;`, codificado en Windows-1252 y con 4 líneas de encabezado. El script suma la columna Importe de todas las filas de agosto y excluye las filas con producto ENVÍO, porque son flete y no mercadería. Es defensivo con los datos:

- Convierte los importes aceptando coma o punto decimal.
- Ignora las líneas que no tienen formato de dato, como títulos o totales.
- Elimina duplicados exactos, solo si el archivo los trae.
- Descarta las filas con fecha fuera de agosto de 2026.

Los importes ya están en pesos, así que no aplica el tipo de cambio.

```python
import csv, re, io
from datetime import datetime
from decimal import Decimal

path = "datos/t7/ventas_agosto.csv"
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("cp1252")

def norm(s):
    s = s.strip().upper()
    return s.replace("Í", "I")

def num(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return Decimal(s)

total = Decimal(0)
envio = Decimal(0)
n = 0
seen = set()
for row in csv.reader(io.StringIO(text), delimiter=";"):
    if len(row) < 4:
        continue
    try:
        f = datetime.strptime(row[0].strip(), "%d/%m/%Y")
        imp = num(row[3])
    except Exception:
        continue
    if f.year != 2026 or f.month != 8:
        continue
    key = tuple(x.strip() for x in row[:4])
    if key in seen:
        continue
    seen.add(key)
    if norm(row[2]) == "ENVIO":
        envio += imp
        continue
    total += imp
    n += 1

print("filas mercadería:", n, "| envíos excluidos:", envio)
v = total.normalize()
print("CIFRA: " + format(v, "f"))
```
