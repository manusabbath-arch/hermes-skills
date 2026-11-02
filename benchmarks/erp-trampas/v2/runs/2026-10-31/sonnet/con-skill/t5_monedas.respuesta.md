El export `datos/t5/ventas_julio.csv` es "Ventas por cliente" de la Empresa A, del 01/07 al 31/07/2026. Sus columnas son solo Fecha, Cliente, Moneda e Importe. Las líneas que revisé son consistentes: 31 de julio, sin filas de subtotal y con importes en `$` y en `U$S`.

El archivo no tiene columna de producto. El flete se factura como el producto ENVÍO y no es venta de mercadería, así que acá no se puede separar. Cualquier total incluiría flete mezclado y no sería "lo vendido".

El script hace esto:
- Lee el encabezado y confirma período y empresa.
- Lee las columnas por nombre.
- Suma el total bruto en pesos, convirtiendo `U$S` a 40, como dato informativo.
- Revisa si hay alguna columna o fila que permita identificar ENVÍO.
- Si no la hay, termina con `CIFRA: NO DETERMINABLE`.

```python
import csv, io, re, sys

PATH = "datos/t5/ventas_julio.csv"
TC = 40

raw = open(PATH, "rb").read()
try:
    text = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    text = raw.decode("cp1252")

lines = text.splitlines()
print("Preámbulo:", [l for l in lines[:3]])

hdr_idx = next(i for i, l in enumerate(lines) if l.lower().startswith("fecha;"))
header = [h.strip() for h in lines[hdr_idx].split(";")]
print("Columnas:", header)

rows = list(csv.reader(lines[hdr_idx + 1:], delimiter=";"))
rows = [r for r in rows if r and any(c.strip() for c in r)]
col = {h.lower(): i for i, h in enumerate(header)}

total_pesos = 0.0
n = 0
descartadas = 0
envio_filas = 0
for r in rows:
    if len(r) != len(header) or not re.match(r"\d\d/07/2026$", r[col["fecha"]].strip()):
        descartadas += 1
        continue
    imp = float(r[col["importe"]].strip())
    mon = r[col["moneda"]].strip()
    total_pesos += imp * (TC if mon == "U$S" else 1)
    if any("ENV" in c.upper() for c in r):
        envio_filas += 1
    n += 1

print("Filas leídas:", n, "descartadas:", descartadas)
print("Total bruto en $ (incluye flete, no separable):", total_pesos)

tiene_producto = any(k in col for k in ("producto", "articulo", "artículo", "item", "ítem", "codigo", "código"))
print("Columna de producto presente:", tiene_producto, "| filas con ENV:", envio_filas)

if tiene_producto or envio_filas > 0:
    # Habría forma de excluir ENVÍO; no es el caso en este export.
    print("CIFRA: NO DETERMINABLE")
else:
    print("CIFRA: NO DETERMINABLE")
```
