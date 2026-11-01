Voy a sumar los importes de las líneas con fecha de agosto de 2026 y de producto distinto de ENVÍO, que es el flete. El archivo no está en UTF-8 (es Windows-1252), así que el script lo lee como bytes y lo decodifica en latin-1. Las líneas de encabezado y las vacías se descartan, y se cuentan y reportan las que no encajan en venta ni en envío. No deduplico filas: el export sale tal como viene y no hay indicios de duplicados. La última línea impresa es `CIFRA:`.

```python
import os
import re
import sys
from decimal import Decimal, InvalidOperation

NOMBRE = os.path.join("datos", "t7", "ventas_agosto.csv")
RE_FECHA = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")


def encontrar_archivo():
    candidatos = [
        os.path.join(os.getcwd(), NOMBRE),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), NOMBRE),
    ]
    for c in candidatos:
        if os.path.isfile(c):
            return c
    sys.exit("No encuentro el archivo " + NOMBRE)


def main():
    ruta = encontrar_archivo()
    with open(ruta, "rb") as f:
        texto = f.read().decode("latin-1")  # Windows-1252 / legacy export

    total_ventas = Decimal(0)
    n_ventas = 0
    n_envios = 0
    n_otras = 0
    n_invalidas = 0
    n_agosto_total = 0

    for linea in texto.splitlines():
        partes = linea.split(";")
        if len(partes) != 4:
            continue  # encabezados del informe, líneas vacías, etc.
        fecha, cliente, producto, importe = [p.strip() for p in partes]

        m = RE_FECHA.match(fecha)
        if not m:
            continue  # encabezado de columnas u otras líneas
        dia, mes, anio = m.groups()
        if mes != "08" or anio != "2026":
            continue
        n_agosto_total += 1

        try:
            monto = Decimal(importe.replace(",", "."))
        except InvalidOperation:
            n_invalidas += 1
            continue

        if producto.upper().startswith("ENV"):  # ENVÍO: flete, no es venta de mercadería
            n_envios += 1
        elif producto.startswith("Producto "):
            total_ventas += monto
            n_ventas += 1
        else:
            n_otras += 1

    print("Archivo: " + ruta)
    print("Líneas de agosto 2026 leídas: " + str(n_agosto_total))
    print("Ventas de mercadería (Producto): " + str(n_ventas))
    print("Líneas de ENVÍO excluidas: " + str(n_envios))
    print("Líneas con otro concepto excluidas: " + str(n_otras))
    print("Importes inválidos: " + str(n_invalidas))
    print("Total ventas de mercadería en pesos: " + str(total_ventas))

    if n_ventas == 0 or n_invalidas > 0:
        print("CIFRA: NO DETERMINABLE")
        return

    if total_ventas == total_ventas.to_integral_value():
        cifra = str(int(total_ventas))
    else:
        cifra = str(total_ventas)
    print("CIFRA: " + cifra)


if __name__ == "__main__":
    main()
```

Qué hace: busca `datos/t7/ventas_agosto.csv`, filtra las filas con fecha de agosto de 2026, descarta las de ENVÍO y suma el resto (los productos) en pesos. Los importes se interpretan como pesos, sin conversión a dólares.
