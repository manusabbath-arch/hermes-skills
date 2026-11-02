Miré `datos/t6/stock.csv` (2200 productos, separador `;`) y el hallazgo que decide la respuesta es este: **todos los productos tienen StockMinimo = 0.00 y StockMaximo = 0.00**. Los stocks son enteros no negativos, sin filas duplicadas ni formatos raros. Con mínimos en cero, ningún producto puede estar por debajo de su mínimo, así que el conteo literal da 0. Pero que todos los mínimos y máximos sean cero sugiere que el ERP no tiene esos parámetros cargados, y entonces la pregunta no se puede responder con estos datos. Por eso el script devuelve `NO DETERMINABLE`. Si preferís la lectura literal, cambiá la condición del bloque de mínimos.

El script lee el CSV (probando UTF-8 y luego cp1252), convierte los números aceptando coma o punto decimal, y revisa si hay algún StockMinimo distinto de cero. Si todos son cero o vacíos, imprime `NO DETERMINABLE`. Si no, cuenta los códigos únicos con Stock < StockMinimo.

```python
import csv
import os
import sys

RUTA = os.path.join("datos", "t6", "stock.csv")


def leer_filas(ruta):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(ruta, encoding=enc, newline="") as f:
                return list(csv.DictReader(f, delimiter=";"))
        except UnicodeDecodeError:
            continue
    raise SystemExit("No se pudo leer el archivo con utf-8 ni cp1252")


def num(s):
    s = (s or "").strip().replace(" ", "")
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


filas = leer_filas(RUTA)
print(f"Filas leidas: {len(filas)}")

minimos = [num(f.get("StockMinimo")) for f in filas]
validos = [m for m in minimos if m is not None]

if not validos or all(m == 0 for m in validos):
    print("Todos los StockMinimo son 0.00 o vacios: el export no tiene minimos configurados.")
    print("CIFRA: NO DETERMINABLE")
    sys.exit(0)

por_debajo = set()
for f, m in zip(filas, minimos):
    stock = num(f.get("Stock"))
    if stock is None or m is None:
        continue
    if stock < m:
        por_debajo.add(f.get("Codigo"))

print(f"Productos con Stock < StockMinimo: {len(por_debajo)}")
print(f"CIFRA: {len(por_debajo)}")
```
