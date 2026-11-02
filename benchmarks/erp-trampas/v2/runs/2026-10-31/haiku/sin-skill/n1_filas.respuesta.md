Revisé `datos/t6/stock.csv` con búsquedas: es un CSV separado por `;`, con encabezado en la línea 1 y 2200 líneas que empiezan con un código de producto `P#####`. No hay otras líneas con contenido ni totales. Por eso la cuenta esperada es 2200. El script es la forma de confirmarla al correrlo.

El script lee el archivo con detección de BOM y fallback a latin-1, saltea el encabezado y las líneas vacías, y cuenta las filas de datos. No cuenta códigos distintos: la pregunta pide filas.

```python
import csv
import os
import sys

RUTA = "datos/t6/stock.csv"


def leer_lineas(ruta):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(ruta, "r", encoding=enc, newline="") as f:
                return list(csv.reader(f, delimiter=";"))
        except UnicodeDecodeError:
            continue
    raise RuntimeError("No se pudo decodificar el archivo")


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, RUTA)
    if not os.path.isfile(ruta):
        ruta = RUTA  # fallback: relativo al directorio actual
    if not os.path.isfile(ruta):
        print("CIFRA: NO DETERMINABLE")
        return

    filas = leer_lineas(ruta)
    if not filas:
        print("CIFRA: NO DETERMINABLE")
        return

    encabezado = [c.strip().lower() for c in filas[0]]
    if encabezado[:1] != ["codigo"]:
        print("CIFRA: NO DETERMINABLE")
        return

    datos = [
        f for f in filas[1:]
        if any(c.strip() for c in f)
    ]
    print(f"Filas de datos (sin encabezado ni vacías): {len(datos)}")
    print(f"CIFRA: {len(datos)}")


if __name__ == "__main__":
    main()
```
