Leí `skill/SKILL.md` y revisé los dos archivos de `datos/t8/`. Ambos son exports de "Cobros" de la empresa A en pesos, sin marcas de U$S ni filas de ENVÍO. Los períodos se solapan: el archivo 1 cubre 01/09 al 10/09 y el 2 cubre 08/09 al 14/09. Por eso el script une ambos archivos y elimina las filas repetidas, en lugar de sumarlos sin más. También imprime, antes de la cifra, la suma de los días 08 a 10 de cada archivo, para verificar que el solapamiento coincide. No ejecuté el script.

```python
import os
from datetime import date
from decimal import Decimal
import re

ARCHIVOS = ["cobros_01_al_10.csv", "cobros_08_al_14.csv"]
DESDE = date(2026, 9, 1)
HASTA = date(2026, 9, 14)
SOLAPE_DESDE = date(2026, 9, 8)
SOLAPE_HASTA = date(2026, 9, 10)


def carpeta_datos():
    cwd = os.path.join(os.getcwd(), "datos", "t8")
    if os.path.isdir(cwd):
        return cwd
    aqui = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(aqui, "datos", "t8")


def leer_texto(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def parsear(linea):
    partes = linea.rstrip("\r\n").split(";")
    if len(partes) != 5:
        return None
    fecha_txt, serie, numero, cliente, importe_txt = [p.strip() for p in partes]
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", fecha_txt)
    if not m:
        return None  # encabezado u otra línea que no es un cobro
    fecha = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    importe = Decimal(importe_txt)  # falla si el importe está mal formado
    return fecha, serie, numero, cliente, importe


def main():
    carpeta = carpeta_datos()
    montos = {}        # clave completa -> importe (ya deduplicado entre archivos)
    leidas = {}
    sumas_solape = {}
    dup_dentro = 0
    dup_entre = 0

    for nombre in ARCHIVOS:
        path = os.path.join(carpeta, nombre)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        leidas[nombre] = 0
        sumas_solape[nombre] = Decimal(0)
        vistos = set()
        for linea in leer_texto(path).splitlines():
            if not linea.strip():
                continue
            reg = parsear(linea)
            if reg is None:
                continue
            fecha, serie, numero, cliente, importe = reg
            if not (DESDE <= fecha <= HASTA):
                continue
            leidas[nombre] += 1
            if SOLAPE_DESDE <= fecha <= SOLAPE_HASTA:
                sumas_solape[nombre] += importe
            clave = (fecha, serie, numero, cliente, importe)
            if clave in vistos:
                dup_dentro += 1
                continue
            vistos.add(clave)
            if clave in montos:
                dup_entre += 1
                continue
            montos[clave] = importe

    total = sum(montos.values(), Decimal(0))

    for nombre in ARCHIVOS:
        print(f"{nombre}: filas en rango={leidas[nombre]}, "
              f"suma 08/09 al 10/09={sumas_solape[nombre]}")
    print(f"Duplicados dentro de un archivo={dup_dentro}, "
          f"duplicados entre archivos={dup_entre}")
    print(f"Cobros únicos={len(montos)}")

    if total != total.to_integral_value():
        raise ValueError("El total no es entero; revisar importes")
    print(f"CIFRA: {int(total)}")


if __name__ == "__main__":
    main()
```

Qué hace: lee los dos CSV desde `datos/t8/`, descarta el encabezado y los registros fuera del 01/09 al 14/09, deduplica las filas repetidas por fecha, serie, número, cliente e importe, y suma los importes únicos en pesos. Los cobros no tienen columna de producto, así que el criterio de ENVÍO no afecta este cálculo.

Un punto que no pude verificar: no hay una fuente independiente (banco o caja) para cruzar el total, así que la cifra queda sin canario. Si el script imprime duplicados entre archivos distintos de 0 en los días 08 a 10, o sumas de solapamiento que no coinciden, conviene revisar antes de usar el número.
