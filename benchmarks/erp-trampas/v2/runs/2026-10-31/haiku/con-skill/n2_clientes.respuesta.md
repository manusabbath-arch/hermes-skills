Leí la skill y revisé el archivo con búsquedas. Las 2.200 filas de datos tienen formato `dd/03/2026;Cliente NNN;importe`, sin filas de total ni de flete, y el preámbulo declara período 01/03/2026 al 31/03/2026. O sea, el archivo es de marzo aunque se llame "YTD". La cifra cuenta los clientes distintos de ese archivo, tal como viene.

El script ubica el archivo, lo lee (UTF-8 o cp1252), toma solo las líneas con fecha y cliente, normaliza espacios y mayúsculas, y cuenta los clientes únicos. No ejecuté nada, así que el número lo calcula el script al correrlo.

```python
import os
import re

NOMBRE = "Ventas 2026 YTD.csv"
RUTA = os.path.join("datos", "t3", NOMBRE)


def hallar(ruta):
    if os.path.isfile(ruta):
        return ruta
    for raiz, _, nombres in os.walk("."):
        if NOMBRE in nombres:
            return os.path.join(raiz, NOMBRE)
    return None


def leer_texto(ruta):
    with open(ruta, "rb") as f:
        crudo = f.read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return crudo.decode(enc)
        except UnicodeDecodeError:
            pass
    return crudo.decode("latin-1")


def main():
    ruta = hallar(RUTA)
    if ruta is None:
        print("CIFRA: NO DETERMINABLE")
        return

    texto = leer_texto(ruta)
    patron_fecha = re.compile(r"^\d{2}/\d{2}/\d{4}$")

    clientes = set()
    filas = 0
    for linea in texto.splitlines():
        partes = linea.split(";")
        if len(partes) != 3 or not patron_fecha.match(partes[0].strip()):
            continue  # preámbulo, encabezado, líneas vacías o totales
        cliente = " ".join(partes[1].split()).upper()
        if not cliente:
            continue
        filas += 1
        clientes.add(cliente)

    if filas == 0 or not clientes:
        print("CIFRA: NO DETERMINABLE")
        return

    print(f"Archivo leído: {ruta}")
    print(f"Filas con venta: {filas}")
    print(f"Clientes distintos: {len(clientes)}")
    print(f"CIFRA: {len(clientes)}")


if __name__ == "__main__":
    main()
```
