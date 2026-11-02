El script lee el CSV, que tiene 4 líneas de encabezado de informe y después la fila de columnas `Fecha;Cliente;Importe`. Toma la columna Cliente, le saca espacios y normaliza mayúsculas, ignora las filas vacías o sin cliente y cuenta los valores distintos.

El archivo dice "Período: 01/03/2026 al 31/03/2026" aunque se llama "YTD". La pregunta es sobre lo que aparece en el archivo, así que cuento los clientes del archivo tal como está.

```python
import csv, io

path = "datos/t3/Ventas 2026 YTD.csv"
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    text = raw.decode("latin-1")

rows = list(csv.reader(io.StringIO(text), delimiter=";"))
hdr = None
for i, r in enumerate(rows):
    cells = [c.strip().lower() for c in r]
    if "cliente" in cells and "fecha" in cells:
        hdr = i
        col = cells.index("cliente")
        break

clientes = set()
for r in rows[hdr + 1:]:
    if len(r) <= col:
        continue
    c = " ".join(r[col].split()).casefold()
    if not c or c.startswith("total"):
        continue
    clientes.add(c)

print("CIFRA: %d" % len(clientes))
```
