Antes de escribir el script, revisé los dos exports. Cada uno tiene 1200 filas de datos, todas con fecha de abril o mayo de 2026 y montos enteros. El orden de columnas cambia entre archivos: abril es `Importe;Cantidad` y mayo es `Cantidad;Importe`. No encontré "ENVÍO" en el texto ni caracteres no ASCII.

El script lee cada columna por nombre de encabezado, no por posición. Filtra abril y mayo de 2026 por la fecha de cada fila y excluye cualquier producto cuyo nombre sea ENVÍO (comparado sin tilde). Suma `Importe` en pesos, sin conversión, porque no hay ninguna marca de moneda distinta. No elimina duplicados exactos: solo los cuenta como diagnóstico, porque no hay evidencia de que sean errores de carga. La última línea imprime `CIFRA:`.

```python
import csv
import io
import os
import unicodedata
from collections import Counter
from decimal import Decimal

BASE = os.path.join(os.getcwd(), "datos", "t2")
ARCHIVOS = ["ventas_abril.csv", "ventas_mayo.csv"]
PERIODO = {(2026, 4), (2026, 5)}
COLUMNAS = ["Fecha", "Producto", "Importe"]


def leer_texto(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def normalizar(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().upper()


def monto(s):
    s = s.strip()
    if not s:
        raise ValueError("importe vacio")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return Decimal(s)


def fecha(s):
    partes = s.strip().split("/")
    if len(partes) != 3:
        raise ValueError("fecha no reconocida: " + s)
    d, m, a = (int(x) for x in partes)
    return a, m, d


def main():
    total = Decimal(0)
    leidas = 0
    fuera_periodo = 0
    envio_excluido = 0
    envio_monto = Decimal(0)
    claves = Counter()

    for nombre in ARCHIVOS:
        path = os.path.join(BASE, nombre)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        texto = leer_texto(path)
        lector = csv.reader(io.StringIO(texto), delimiter=";")
        encabezado = [h.strip() for h in next(lector)]
        for c in COLUMNAS:
            if c not in encabezado:
                raise ValueError(nombre + ": falta columna " + c)
        i_fecha = encabezado.index("Fecha")
        i_prod = encabezado.index("Producto")
        i_imp = encabezado.index("Importe")

        filas_archivo = 0
        for row in lector:
            if not any(x.strip() for x in row):
                continue
            filas_archivo += 1
            leidas += 1
            claves[tuple(x.strip() for x in row)] += 1

            a, m, _ = fecha(row[i_fecha])
            if (a, m) not in PERIODO:
                fuera_periodo += 1
                continue

            imp = monto(row[i_imp])
            if "ENVIO" in normalizar(row[i_prod]):
                envio_excluido += 1
                envio_monto += imp
                continue

            total += imp

        if filas_archivo == 0:
            raise ValueError(nombre + ": cero filas")
        print(nombre + ": filas de datos = " + str(filas_archivo))

    duplicadas = sum(n - 1 for n in claves.values() if n > 1)
    print("filas leidas total = " + str(leidas))
    print("fuera de abril-mayo 2026 = " + str(fuera_periodo))
    print("ENVIO excluidas = " + str(envio_excluido) + " por $" + format(envio_monto, "f"))
    print("filas repetidas exactas (no eliminadas) = " + str(duplicadas))
    print("venta abril-mayo 2026 en $ = " + format(total, "f"))

    if total == total.to_integral_value():
        salida = str(int(total))
    else:
        salida = format(total, "f")
    print("CIFRA: " + salida)


if __name__ == "__main__":
    main()
```

Corre desde la carpeta `con-skill` con `python3 script.py`. Si `datos/t2` no existe desde el directorio actual, el script falla con `FileNotFoundError` y no imprime `CIFRA`.
