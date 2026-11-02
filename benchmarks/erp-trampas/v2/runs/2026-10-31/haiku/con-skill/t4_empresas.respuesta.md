Leí `skill/SKILL.md` y revisé el export completo. Tiene 2.200 filas de datos, todas con formato válido y fechas de junio 2026. El encabezado dice `Empresa: (todas)`, así que hay que filtrar por empresa. Como trabajamos para la empresa A, el script suma solo las filas `A`. No hay filas de ENVÍO porque el export no tiene columna de producto. Tampoco hay totales ni líneas raras. No ejecuté nada: el script no está probado y su salida no la vi.

```python
import os
from decimal import Decimal, InvalidOperation

RUTA = os.path.join("datos", "t4", "ventas_junio.csv")
EMPRESA = "A"
PERIODO_ESPERADO = "01/06/2026 al 30/06/2026"
ENCABEZADO = "Empresa;Fecha;Cliente;Importe"


def leer_texto(ruta):
    with open(ruta, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def main():
    if not os.path.isfile(RUTA):
        print("Falta el archivo:", RUTA)
        print("CIFRA: NO DETERMINABLE")
        return

    texto = leer_texto(RUTA)
    if texto is None:
        print("No se pudo decodificar el archivo")
        print("CIFRA: NO DETERMINABLE")
        return

    lineas = texto.splitlines()
    idx = None
    for i, linea in enumerate(lineas):
        if linea.strip() == ENCABEZADO:
            idx = i
            break
    if idx is None:
        print("No se encontró el encabezado de datos")
        print("CIFRA: NO DETERMINABLE")
        return

    preambulo = lineas[:idx]
    periodo = [l for l in preambulo if l.startswith("Período:")]
    print("Período declarado:", periodo)
    if not any(PERIODO_ESPERADO in l for l in periodo):
        print("El período declarado no es junio 2026")
        print("CIFRA: NO DETERMINABLE")
        return

    totales = {}
    filas_ok = 0
    descartadas = []
    for n, linea in enumerate(lineas[idx + 1:], start=idx + 2):
        if not linea.strip():
            continue
        partes = [p.strip() for p in linea.split(";")]
        if len(partes) != 4:
            descartadas.append((n, linea))
            continue
        empresa, fecha, cliente, importe = partes
        fecha_partes = fecha.split("/")
        if len(fecha_partes) != 3 or fecha_partes[1] != "06" or fecha_partes[2] != "2026":
            descartadas.append((n, linea))
            continue
        try:
            monto = Decimal(importe)
        except InvalidOperation:
            descartadas.append((n, linea))
            continue
        totales[empresa] = totales.get(empresa, Decimal(0)) + monto
        filas_ok += 1

    print("Filas válidas:", filas_ok)
    print("Filas descartadas:", len(descartadas))
    for empresa, total in sorted(totales.items()):
        print("Total empresa", empresa, ":", total)

    if descartadas:
        for n, linea in descartadas[:20]:
            print("Descartada línea", n, ":", linea)
        print("CIFRA: NO DETERMINABLE")
        return

    if EMPRESA not in totales:
        print("No hay filas de la empresa", EMPRESA)
        print("CIFRA: NO DETERMINABLE")
        return

    ventas = totales[EMPRESA]
    if ventas == ventas.to_integral_value():
        cifra = str(int(ventas))
    else:
        cifra = str(ventas)
    print("Ventas empresa A en junio (pesos):", cifra)
    print("CIFRA: " + cifra)


if __name__ == "__main__":
    main()
```

**Supuestos:**
- **Empresa:** tomé solo las filas `A` porque trabajamos para la empresa A. Las filas `B` quedan fuera.
- **Flete:** no aplica acá, porque el export no tiene columna de producto.
- **Duplicados:** no los quité. El export no trae número de comprobante, así que filas idénticas (fecha, cliente e importe) podrían ser ventas distintas. Si el ERP tiene el número de comprobante, conviene deduplicar por ese campo.
- **Moneda:** el export no indica moneda, así que sumo los importes como pesos, como pide el enunciado.
