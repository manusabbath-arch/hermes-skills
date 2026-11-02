Revisé el export (`datos/t5/ventas_julio.csv`) y encontré lo siguiente:

- Hay 2200 filas de venta, todas con fecha de julio 2026, en dos monedas: `$` y `U$S`.
- Las primeras 5 líneas son título, empresa, período, una línea en blanco y el encabezado. No son ventas.
- No hay ninguna fila ENVÍO, ni columna de producto, ni notas de crédito ni importes negativos.

El script lee las filas con formato válido, descarta encabezados y líneas que no encajan, convierte los importes en `U$S` a pesos multiplicando por 40 y suma el total. Imprime las líneas descartadas antes de la cifra final. No pude ejecutarlo, así que no tengo el total todavía. Supuse que las filas en `U$S` están expresadas en dólares y que no hay duplicados que haya que quitar.

```python
import os
import re

RUTA = os.path.join("datos", "t5", "ventas_julio.csv")
TC = 40  # $ por U$S
PATRON = re.compile(r"^(\d{2})/(\d{2})/(\d{4});(Cliente \d+);(\$|U\$S);(\d+)$")
ENCABEZADOS = ("Informe", "Empresa", "Período", "Periodo", "Fecha;")

with open(RUTA, "rb") as f:
    raw = f.read()
try:
    texto = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    texto = raw.decode("latin-1")

total = 0
filas = 0
descartadas = []

for num, linea in enumerate(texto.splitlines(), 1):
    linea = linea.strip()
    if not linea or linea.startswith(ENCABEZADOS):
        continue
    m = PATRON.match(linea)
    if not m:
        descartadas.append((num, linea))
        continue
    dia, mes, anio, cliente, moneda, importe = m.groups()
    if mes != "07" or anio != "2026":
        descartadas.append((num, linea))
        continue
    importe = int(importe)
    if moneda == "U$S":
        importe *= TC
    total += importe
    filas += 1

print(f"Filas de venta de julio 2026 consideradas: {filas}")
print(f"Líneas descartadas: {len(descartadas)}")
for num, linea in descartadas[:20]:
    print(f"  linea {num}: {linea}")
print(f"Total ventas julio 2026 ($): {total}")
print(f"CIFRA: {total}")
```
