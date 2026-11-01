Leí `skill/SKILL.md` y revisé `datos/t1/ventas_marzo.csv` antes de escribir el script. Lo que encontré:

- **Preámbulo:** `Empresa: A`, `Período: 01/03/2026 al 31/03/2026`.
- **Filas:** 2.200 filas de detalle, todas con fecha dd/03/2026 y formato `Cliente NNN;importe` entero.
- **Sin ENVÍO:** no hay ninguna línea de flete para excluir.
- **Total del propio export:** la línea final `;TOTAL GENERAL;468550`.

No pude sumar las 2.200 filas a mano, así que el script se controla a sí mismo: suma el detalle y compara contra el `TOTAL GENERAL` del archivo. Si no cierra, o si hay filas fuera de marzo o mal formadas, imprime `CIFRA: NO DETERMINABLE` en lugar de un número.

El script lee el archivo desde la carpeta de trabajo o desde la carpeta del script, usa UTF-8 con respaldo en cp1252, y no escribe nada.

```python
import csv
import os
import re
import sys

REL = os.path.join("datos", "t1", "ventas_marzo.csv")


def hallar_archivo():
    candidatos = [
        os.path.join(os.getcwd(), REL),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), REL),
    ]
    for c in candidatos:
        if os.path.isfile(c):
            return c
    sys.exit("No se encuentra " + REL)


def leer_texto(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def main():
    path = hallar_archivo()
    lineas = leer_texto(path).splitlines()

    # 1) Período declarado en el preámbulo (no el nombre del archivo)
    periodo = next((l for l in lineas if l.startswith("Período:")), "")
    print("Archivo:", path)
    print("Preámbulo:", periodo)
    if "01/03/2026 al 31/03/2026" not in periodo:
        print("Período distinto de marzo 2026.")
        print("CIFRA: NO DETERMINABLE")
        return

    # 2) Encabezado de columnas
    idx = next((i for i, l in enumerate(lineas) if l.strip() == "Fecha;Cliente;Importe"), None)
    if idx is None:
        print("No se encontró el encabezado Fecha;Cliente;Importe.")
        print("CIFRA: NO DETERMINABLE")
        return

    re_fecha = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
    re_monto = re.compile(r"^-?\d+$")

    suma = 0
    filas = 0
    total_declarado = None
    fuera_de_periodo = []
    malformadas = []

    for n, linea in enumerate(lineas[idx + 1:], start=idx + 2):
        if not linea.strip():
            continue
        partes = linea.split(";")
        if len(partes) != 3:
            malformadas.append((n, linea))
            continue
        fecha, cliente, importe = (p.strip() for p in partes)

        if fecha == "" and cliente.upper() == "TOTAL GENERAL":
            if re_monto.match(importe):
                total_declarado = int(importe)
            else:
                malformadas.append((n, linea))
            continue

        m = re_fecha.match(fecha)
        if not m:
            malformadas.append((n, linea))
            continue
        _, mes, anio = m.groups()
        if mes != "03" or anio != "2026":
            fuera_de_periodo.append((n, linea))
            continue
        if not re_monto.match(importe):
            malformadas.append((n, linea))
            continue

        suma += int(importe)
        filas += 1

    print("Filas de detalle sumadas:", filas)
    print("Total de control del export (TOTAL GENERAL):", total_declarado)
    print("Suma del detalle:", suma)
    print("Filas fuera de marzo 2026:", len(fuera_de_periodo))
    print("Filas malformadas:", len(malformadas))
    for n, l in (fuera_de_periodo + malformadas)[:10]:
        print("  línea", n, "->", l)

    # 3) Guardas: el export tiene que cerrar consigo mismo
    if total_declarado is None or filas == 0:
        print("CIFRA: NO DETERMINABLE")
        return
    if fuera_de_periodo or malformadas:
        print("CIFRA: NO DETERMINABLE")
        return
    if suma != total_declarado:
        print("El detalle no cierra con TOTAL GENERAL.")
        print("CIFRA: NO DETERMINABLE")
        return

    print("Ventas de marzo 2026, en $ (sin ENVÍO; el archivo no tiene esa línea):", suma)
    print(f"CIFRA: {suma}")


if __name__ == "__main__":
    main()
```

Si el script imprime `CIFRA: 468550`, ese es el total de marzo en pesos, y coincide con el `TOTAL GENERAL` del export. Si imprime `NO DETERMINABLE`, el detalle no cierra con el total del archivo, y el motivo queda en las líneas previas a la cifra.
