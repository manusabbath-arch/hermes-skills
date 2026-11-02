El archivo se llama "2026 YTD", pero el encabezado dice que cubre solo del 01/03/2026 al 31/03/2026. La pregunta es cuántos clientes aparecen *en ese archivo*, así que cuento los clientes distintos del archivo completo y aviso del período. Las filas de datos tienen todas el formato `fecha;Cliente NNN;importe`. El script lee el archivo, ignora el preámbulo y las filas en blanco, normaliza espacios y mayúsculas en el nombre del cliente, y cuenta los nombres distintos. También imprime el período declarado y las filas leídas como control.

```python
import csv, re

path = "datos/t3/Ventas 2026 YTD.csv"
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    text = raw.decode("cp1252")

lines = text.splitlines()
periodo = next((l for l in lines if l.lower().startswith("per")), "?")

clientes = set()
filas = 0
header_seen = False
for row in csv.reader(lines, delimiter=";"):
    if not row:
        continue
    if not header_seen:
        if [c.strip().lower() for c in row[:2]] == ["fecha", "cliente"]:
            header_seen = True
        continue
    if len(row) < 2:
        continue
    nombre = re.sub(r"\s+", " ", row[1]).strip().upper()
    if not nombre or nombre.startswith("TOTAL"):
        continue
    filas += 1
    clientes.add(nombre)

print("Período declarado:", periodo)
print("Filas de datos:", filas)
print("CIFRA: %d" % len(clientes))
```
