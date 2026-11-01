Leí `skill/SKILL.md` y revisé `datos/t6/stock.csv`: es un CSV separado por `;`, con encabezado en la primera línea, sin preámbulo y sin fila de TOTAL (una búsqueda de "total" dio 0 coincidencias). Los acentos ("Artículo") pueden venir en UTF-8 o cp1252, así que el script prueba ambos. El script lee el archivo como bytes, descarta el encabezado y cuenta las filas que tienen algún campo con contenido, sin cambiar nada. Termina imprimiendo la cifra en la última línea.

```python
import csv
import io
import os
import sys

RUTA = os.path.join("datos", "t6", "stock.csv")


def leer_texto(ruta):
    with open(ruta, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise SystemExit("ERROR: no se pudo decodificar el archivo")


def main():
    if not os.path.isfile(RUTA):
        raise SystemExit("ERROR: no existe " + RUTA + " (ejecutar desde la carpeta raiz)")

    texto, enc = leer_texto(RUTA)
    print("Archivo:", RUTA, "| encoding:", enc)

    lector = csv.reader(io.StringIO(texto, newline=""), delimiter=";")
    filas = list(lector)
    if not filas:
        raise SystemExit("ERROR: archivo vacio")

    encabezado = [c.strip() for c in filas[0]]
    print("Encabezado:", encabezado)

    datos = filas[1:]
    con_contenido = [f for f in datos if any(c.strip() for c in f)]
    vacias = len(datos) - len(con_contenido)
    print("Filas tras encabezado:", len(datos))
    print("Filas vacias descartadas:", vacias)

    if not con_contenido:
        print("CIFRA: NO DETERMINABLE")
        return

    print("CIFRA:", len(con_contenido))


if __name__ == "__main__":
    main()
```
