Hay dos exports que se solapan: `cobros_01_al_10.csv` y `cobros_08_al_14.csv` tienen las mismas filas para el 08 y 09/09. El script lee ambos, descarta las filas idénticas repetidas, filtra las fechas del 01/09 al 14/09 de 2026 y suma los importes en pesos (no hace falta convertir moneda, no hay marcas de U$S ni de ENVÍO en los archivos). Si encuentra importes no numéricos, responde `NO DETERMINABLE`.

```python
import csv
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def carpeta_datos():
    candidatos = [
        os.path.join("datos", "t8"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "t8"),
    ]
    for c in candidatos:
        if os.path.isdir(c):
            return c
    return None


def parse_importe(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def main():
    d = carpeta_datos()
    if d is None:
        print("CIFRA: NO DETERMINABLE")
        return

    desde, hasta = date(2026, 9, 1), date(2026, 9, 14)
    archivos = sorted(f for f in os.listdir(d) if f.lower().endswith(".csv"))

    vistos = set()          # filas exactas ya contadas (exports solapados)
    por_comprobante = {}    # (serie, numero) -> fila completa, para detectar conflictos
    total = Decimal(0)
    n_filas = n_dup = n_conflicto = n_fuera = n_malos = 0

    for fn in archivos:
        ruta = os.path.join(d, fn)
        with open(ruta, encoding="latin-1", newline="") as fh:
            for row in csv.reader(fh, delimiter=";"):
                if len(row) < 5:
                    continue
                try:
                    fecha = datetime.strptime(row[0].strip(), "%d/%m/%Y").date()
                except ValueError:
                    continue  # encabezados y títulos del informe
                importe = parse_importe(row[4])
                if importe is None:
                    n_malos += 1
                    continue
                if not (desde <= fecha <= hasta):
                    n_fuera += 1
                    continue

                serie = row[1].strip()
                numero = row[2].strip()
                cliente = row[3].strip()
                clave = (fecha, serie, numero, cliente, importe)

                if clave in vistos:
                    n_dup += 1
                    continue
                vistos.add(clave)

                comp = (serie, numero)
                if comp in por_comprobante and por_comprobante[comp] != clave:
                    n_conflicto += 1
                por_comprobante.setdefault(comp, clave)

                total += importe
                n_filas += 1

    print(f"Archivos leidos: {archivos}")
    print(f"Filas contadas: {n_filas}")
    print(f"Duplicados exactos descartados (solapamiento): {n_dup}")
    print(f"Mismo comprobante con datos distintos: {n_conflicto}")
    print(f"Filas fuera del periodo: {n_fuera}")
    print(f"Importes no numericos: {n_malos}")
    print(f"Total cobrado 01/09 al 14/09 ($): {total}")

    if n_filas == 0 or n_malos > 0:
        print("CIFRA: NO DETERMINABLE")
        return

    if total == total.to_integral_value():
        print(f"CIFRA: {int(total)}")
    else:
        print("CIFRA: NO DETERMINABLE")


if __name__ == "__main__":
    main()
```

Cómo lo resuelve: el total son los cobros únicos del 01/09 al 14/09 en pesos. Si el script detecta importes no numéricos, o si no encuentra ninguna fila válida, imprime `CIFRA: NO DETERMINABLE`. No pude ejecutarlo, así que el número final sale de la corrida.
