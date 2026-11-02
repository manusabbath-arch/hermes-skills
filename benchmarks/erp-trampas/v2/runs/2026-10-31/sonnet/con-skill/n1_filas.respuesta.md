El archivo tiene encabezado `Codigo;Producto;Stock;StockMinimo;StockMaximo`, delimitador `;` y no tiene filas de TOTAL ni líneas vacías (lo busqué con Grep). El script lo lee con el módulo `csv`, que respeta los saltos de línea dentro de campos entre comillas. Cuenta las filas de datos con código no vacío, descarta cualquier fila que parezca un total e imprime cuántas filas descartó y cuántos códigos están repetidos. Al final imprime la cifra.

```python
import csv

ruta = "datos/t6/stock.csv"

with open(ruta, "rb") as f:
    raw = f.read()
try:
    texto = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    texto = raw.decode("cp1252", errors="replace")

lector = csv.reader(texto.splitlines(), delimiter=";")
encabezado = next(lector)
print("Encabezado:", encabezado)

filas = 0
descartadas = 0
codigos = set()
for r in lector:
    if not r or not any(c.strip() for c in r):
        descartadas += 1
        continue
    if "total" in r[0].strip().lower() or (len(r) > 1 and "total" in r[1].strip().lower()):
        descartadas += 1
        continue
    if not r[0].strip():
        descartadas += 1
        continue
    filas += 1
    codigos.add(r[0].strip())

print("Filas descartadas (vacías/total):", descartadas)
print("Códigos distintos:", len(codigos))
print(f"CIFRA: {filas}")
```
