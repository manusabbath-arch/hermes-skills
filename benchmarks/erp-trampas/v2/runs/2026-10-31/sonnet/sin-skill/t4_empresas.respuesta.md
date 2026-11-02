El único archivo es `datos/t4/ventas_junio.csv`, un informe "Ventas por cliente". Tiene las columnas Empresa, Fecha, Cliente e Importe, y mezcla las empresas A y B.

Las ventas de la empresa A se pueden sumar. El problema es que el informe no trae la columna de producto, así que no se puede separar el flete (ENVÍO), que no es venta de mercadería. Un total de A podría incluir flete sin que haya forma de saberlo. Por eso, la cifra de venta de mercadería no se puede determinar con este archivo.

El script hace lo siguiente:
- Lee el CSV y verifica si existe una columna de producto o concepto.
- Suma como referencia el total de la empresa A en junio, con el flete posiblemente incluido. Ese total se imprime como información y no como respuesta.
- Si no hay columna de producto, imprime `CIFRA: NO DETERMINABLE`.
- Si hubiera columna de producto, excluiría ENVÍO y devolvería la suma.

No pude ejecutar nada, así que no vi el total de referencia.

```python
import csv

path = "datos/t4/ventas_junio.csv"
with open(path, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f, delimiter=";"))

# localizar encabezado
hi = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Empresa" and "Importe" in [c.strip() for c in r])
header = [c.strip() for c in rows[hi]]
data = [r for r in rows[hi + 1:] if len(r) == len(header)]

ie = header.index("Empresa")
ii = header.index("Importe")
prod_col = next((i for i, c in enumerate(header)
                 if c.lower() in ("producto", "articulo", "artículo", "concepto", "item", "descripcion", "descripción")), None)

def num(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)

total_A = 0.0
total_A_sin_envio = 0.0
for r in data:
    if r[ie].strip() != "A":
        continue
    try:
        v = num(r[ii])
    except ValueError:
        continue
    total_A += v
    if prod_col is not None and "ENV" in r[prod_col].upper():
        continue
    total_A_sin_envio += v

print("Columnas:", header)
print("Total empresa A (referencia, puede incluir flete):", total_A)

if prod_col is None:
    print("El export no tiene columna de producto: no se puede excluir ENVÍO.")
    print("CIFRA: NO DETERMINABLE")
else:
    v = total_A_sin_envio
    print("CIFRA: %s" % (int(v) if v == int(v) else v))
```
