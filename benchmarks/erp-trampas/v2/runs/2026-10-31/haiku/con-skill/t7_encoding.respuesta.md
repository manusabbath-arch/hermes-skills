Antes de escribir el script revisé el archivo con búsquedas: tiene 2.200 filas de datos (más el encabezado), todas con fecha de agosto de 2026. Hay 1.945 líneas de `Producto` y 255 de `ENV` (flete), que no es mercadería. Los importes son enteros, no hay filas `TOTAL` y no hay negativos. El archivo está en cp1252 (`ENVÍO` aparece como `ENV�O`), así que el script lo lee como latin-1 y reconoce el flete por el prefijo `ENV`.

El script suma los importes de las filas de producto, excluyendo `ENV`, valida el período por fecha, verifica que cada fila tenga 4 campos y avisa si hay líneas idénticas (sin eliminarlas, porque el export no trae número de comprobante). No lo pude ejecutar, así que el resultado sale de ejecutarlo en la carpeta `datos/t7`.

```python
# Ventas de mercadería de agosto 2026 (empresa A) desde datos/t7/ventas_agosto.csv.
# Excluye las filas de ENVÍO (flete), que no son venta de mercadería.
from decimal import Decimal, InvalidOperation
from collections import Counter

ARCHIVO = "ventas_agosto.csv"
MES, ANIO = "08", "2026"


def main():
    with open(ARCHIVO, "rb") as f:
        texto = f.read().decode("latin-1")  # export en cp1252; latin-1 nunca falla
    lineas = texto.splitlines()

    idx = next(i for i, l in enumerate(lineas) if l.startswith("Fecha;"))
    cabecera = lineas[idx].split(";")
    assert cabecera == ["Fecha", "Cliente", "Producto", "Importe"], cabecera

    total = Decimal(0)
    filas_producto = 0
    filas_envio = 0
    fuera_periodo = 0
    total_envio = Decimal(0)
    vistas = Counter()

    for linea in lineas[idx + 1:]:
        if not linea.strip():
            continue
        campos = linea.split(";")
        if len(campos) != 4:
            raise ValueError(f"fila con {len(campos)} campos: {linea!r}")
        fecha, cliente, producto, importe = campos
        dia, mes, anio = fecha.split("/")
        if (mes, anio) != (MES, ANIO):
            fuera_periodo += 1
            continue
        try:
            monto = Decimal(importe.strip().replace(",", "."))
        except InvalidOperation:
            raise ValueError(f"importe no numérico: {linea!r}")
        if producto.startswith("ENV"):
            filas_envio += 1
            total_envio += monto
            continue
        filas_producto += 1
        total += monto
        vistas[linea] += 1

    duplicadas = sum(c - 1 for c in vistas.values() if c > 1)
    print(f"filas de mercadería: {filas_producto}")
    print(f"filas de ENVÍO excluidas: {filas_envio} (monto {total_envio})")
    print(f"filas fuera de agosto 2026: {fuera_periodo}")
    print(f"líneas repetidas (no eliminadas): {duplicadas}")
    print(f"total mercadería: {total}")

    if total != total.to_integral_value():
        raise ValueError(f"total no entero: {total}")
    print(f"CIFRA: {int(total)}")


main()
```

Decisiones que tomé:
- El flete se excluye solo por el prefijo `ENV` del producto, no por el encoding.
- Las líneas repetidas se cuentan pero se suman igual, porque sin número de comprobante no hay forma de distinguir una venta duplicada de dos ventas iguales.
- El tipo de cambio de 40 $/U$S no se usa: el export no trae columna de moneda y todo está en pesos.
