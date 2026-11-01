Revisé el archivo: hay 2201 líneas con `;`, que son 1 encabezado de columnas y 2200 filas, y todas las 2200 cumplen el formato `dd/mm/aaaa;Cliente NNN;importe`. No hay clientes vacíos ni ENVÍO/flete. Hay que contar con cuidado solo la columna Cliente, sin el encabezado del informe.

Qué hace el script: lee el CSV (saltea las líneas de título hasta la fila `Fecha;Cliente;Importe`), toma la columna Cliente de cada fila de datos, normaliza espacios y mayúsculas, y cuenta los valores distintos. Como el encabezado y las filas están bien formados, no hace falta más limpieza. Nota: el archivo dice "YTD" en el nombre, pero el período declarado es solo 01/03/2026 al 31/03/2026. La pregunta es sobre el archivo, así que cuento lo que contiene.

```python
import os

RUTA = os.path.join("datos", "t3", "Ventas 2026 YTD.csv")


def leer_lineas(ruta):
    with open(ruta, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc).splitlines()
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1").splitlines()


def main():
    lineas = leer_lineas(RUTA)

    clientes = set()
    en_datos = False
    for linea in lineas:
        partes = linea.split(";")
        if not en_datos:
            # La fila de columnas es la que tiene "Cliente" en la segunda posición
            if len(partes) >= 2 and partes[1].strip().lower() == "cliente":
                en_datos = True
            continue
        if len(partes) < 3:
            continue
        cliente = " ".join(partes[1].split()).upper()
        if not cliente:
            continue
        clientes.add(cliente)

    if not clientes:
        print("CIFRA: NO DETERMINABLE")
        return

    print(f"Clientes distintos: {len(clientes)}")
    print(f"CIFRA: {len(clientes)}")


if __name__ == "__main__":
    main()
```
