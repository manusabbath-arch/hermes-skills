El export `stock.csv` tiene las columnas `Codigo;Producto;Stock;StockMinimo;StockMaximo`, con 2.200 productos. Con una búsqueda en el archivo vi que, salvo el encabezado, ninguna fila tiene un `StockMinimo` distinto de `0.00`. Un `0.00` en un campo que nadie carga no es un stock mínimo real. Si lo tomara como dato, ningún producto estaría "bajo el mínimo", y esa cifra sería falsa pero se vería creíble.

El script hace lo siguiente:
- Lee el CSV con `;` como separador.
- Cuenta cuántos productos tienen un mínimo cargado (mayor que 0).
- Si no hay ninguno, imprime `CIFRA: NO DETERMINABLE`.
- Si hubiera mínimos cargados, cuenta los productos con `Stock < StockMinimo`, considerando solo los que tienen mínimo mayor que 0.

```python
import csv

ruta = "datos/t6/stock.csv"
filas = 0
con_minimo = 0
bajo = set()

with open(ruta, encoding="utf-8-sig", newline="") as f:
    rd = csv.DictReader(f, delimiter=";")
    print("Columnas:", rd.fieldnames)
    for r in rd:
        cod = (r.get("Codigo") or "").strip()
        if not cod or cod.upper().startswith("TOTAL"):
            continue
        filas += 1
        try:
            mn = float((r.get("StockMinimo") or "").strip().replace(",", "."))
            st = float((r.get("Stock") or "").strip().replace(",", "."))
        except ValueError:
            continue
        if mn > 0:
            con_minimo += 1
            if st < mn:
                bajo.add(cod)

print("Filas leídas:", filas)
print("Productos con stock mínimo cargado (>0):", con_minimo)

if filas == 0 or con_minimo == 0:
    print("El stock mínimo no está cargado en el ERP (todo 0.00): no se puede determinar.")
    print("CIFRA: NO DETERMINABLE")
else:
    print("CIFRA: %d" % len(bajo))
```
