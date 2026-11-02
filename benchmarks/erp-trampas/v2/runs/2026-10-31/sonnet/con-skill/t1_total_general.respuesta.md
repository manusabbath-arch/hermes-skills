El export de marzo (`datos/t1/ventas_marzo.csv`) tiene tres líneas de encabezado (informe, empresa A, período 01/03 al 31/03/2026). Después vienen las columnas `Fecha;Cliente;Importe` y una fila final `TOTAL GENERAL`. No tiene columna de producto, así que no hay fletes (ENVÍO) que sacar. Todo está en pesos.

El script hace esto:
- Lee el archivo y se queda solo con las filas de detalle, que tienen una fecha válida de marzo de 2026 y un importe numérico. Descarta `TOTAL GENERAL` para no duplicar la suma.
- Suma los importes de esas filas.
- Compara esa suma con el `TOTAL GENERAL` del mismo archivo. Si no coinciden, lo avisa por stderr.
- Imprime la cifra como última línea.

```python
import csv, re, sys
from datetime import datetime

path = "datos/t1/ventas_marzo.csv"
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    text = raw.decode("cp1252")

total = 0.0
total_declarado = None
n = 0
descartadas = []
for line in text.splitlines():
    parts = line.split(";")
    if len(parts) < 3:
        continue
    fecha, cliente, imp = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if "TOTAL" in cliente.upper() or "TOTAL" in fecha.upper():
        try:
            total_declarado = float(imp)
        except ValueError:
            pass
        continue
    try:
        d = datetime.strptime(fecha, "%d/%m/%Y")
        v = float(imp)
    except ValueError:
        descartadas.append(line)
        continue
    if d.year != 2026 or d.month != 3:
        descartadas.append(line)
        continue
    total += v
    n += 1

print("filas sumadas:", n, file=sys.stderr)
print("filas descartadas:", len(descartadas), descartadas[:10], file=sys.stderr)
print("total declarado en el export:", total_declarado, file=sys.stderr)
print("suma detalle:", total, file=sys.stderr)
if total_declarado is not None and abs(total - total_declarado) > 0.5:
    print("ATENCION: el detalle no cierra con TOTAL GENERAL", file=sys.stderr)

print("CIFRA: %d" % round(total) if abs(total - round(total)) < 1e-9 else "CIFRA: %s" % total)
```
