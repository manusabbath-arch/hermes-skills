El script lee `datos/t6/stock.csv` con el módulo `csv` (separador `;`, codificación utf-8-sig por si hay BOM). Salta el encabezado y cuenta las filas que tienen código de producto, ignorando las líneas vacías. Al mirar el archivo, la primera fila de datos es P00001 y la última es P02200, así que el resultado esperado es 2200.

```python
import csv

n = 0
with open("datos/t6/stock.csv", encoding="utf-8-sig", newline="") as f:
    r = csv.reader(f, delimiter=";")
    next(r)  # encabezado
    for row in r:
        if row and row[0].strip():
            n += 1

print(f"CIFRA: {n}")
```
