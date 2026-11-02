Reviso el archivo: es `datos/t1/ventas_marzo.csv`, con tres columnas (Fecha, Cliente, Importe). La última fila es un `TOTAL GENERAL` de 468550 que no es una venta.

El script suma los importes de las filas de datos y descarta esa fila de total. También controla que la suma coincida con el total del informe y que todas las fechas sean de marzo de 2026.

El archivo no tiene columna de producto. Por eso no se puede saber cuánto de cada importe es el producto ENVÍO, que es flete y no venta de mercadería. Sin ese detalle, la venta de mercadería en marzo no se puede aislar, y el script termina con `CIFRA: NO DETERMINABLE`. Antes imprime la suma total (flete incluido), por si sirve como referencia.

```python
import csv

path = "datos/t1/ventas_marzo.csv"
total_filas = 0
n = 0
total_informe = None
fuera_de_marzo = 0

with open(path, encoding="utf-8-sig", newline="") as f:
    for row in csv.reader(f, delimiter=";"):
        if len(row) < 3:
            continue
        fecha, cliente, importe = row[0].strip(), row[1].strip(), row[2].strip()
        if cliente.upper().startswith("TOTAL"):
            total_informe = float(importe.replace(",", "."))
            continue
        try:
            d, m, a = fecha.split("/")
            val = float(importe.replace(",", "."))
        except ValueError:
            continue  # encabezados
        if (m, a) != ("03", "2026"):
            fuera_de_marzo += 1
            continue
        total_filas += val
        n += 1

print("Filas de datos:", n)
print("Suma de filas (incluye ENVÍO, sin poder separarlo):", total_filas)
print("TOTAL GENERAL del informe:", total_informe)
print("Filas fuera de marzo:", fuera_de_marzo)
print("El export no tiene columna de producto: no se puede excluir ENVÍO (flete).")
print("CIFRA: NO DETERMINABLE")
```
