Para responder leí `skill/SKILL.md` y revisé el export completo. Tiene 2.200 filas de venta de julio de 2026, todas con moneda `$` o `U$S`. No encontré filas de ENVÍO ni de TOTAL, y el encabezado es `Fecha;Cliente;Moneda;Importe`. Como el export mezcla pesos y dólares, cada `U$S` se convierte a pesos con el tipo de cambio de 40.

El script valida la entidad (A) y el período declarado, toma las columnas por nombre y excluye cualquier línea con ENVÍO por las dudas. Suma `$` tal cual y `U$S` multiplicado por 40. Si aparece una moneda desconocida, una fecha inválida o un importe que no se puede leer, responde `NO DETERMINABLE`. No pude ejecutarlo, así que el número final no lo verifiqué yo.

```python
import os
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation

TIPO_CAMBIO = Decimal("40")  # $ por U$S, referencia del período
ENTIDAD = "A"
RELATIVO = os.path.join("datos", "t5", "ventas_julio.csv")
ENCABEZADO = ["Fecha", "Cliente", "Moneda", "Importe"]


def no_determinable(motivo):
    print("MOTIVO: " + motivo)
    print("CIFRA: NO DETERMINABLE")
    sys.exit(0)


def hallar_archivo():
    aqui = os.path.dirname(os.path.abspath(__file__))
    for base in (os.getcwd(), aqui):
        p = os.path.join(base, RELATIVO)
        if os.path.isfile(p):
            return p
    return None


def leer_texto(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def main():
    path = hallar_archivo()
    if path is None:
        no_determinable("no existe datos/t5/ventas_julio.csv")

    lineas = leer_texto(path).splitlines()

    # Preámbulo: entidad y período declarados por el export
    preambulo = lineas[:10]
    if not any(l.strip() == "Empresa: " + ENTIDAD for l in preambulo):
        no_determinable("entidad no declarada como A")
    if not any(re.match(r"^Per\S*: 01/07/2026 al 31/07/2026\s*$", l.strip())
               for l in preambulo):
        no_determinable("período declarado distinto de julio 2026")

    # Encabezado de columnas, buscado por nombre
    idx = None
    for i, l in enumerate(lineas):
        if [c.strip() for c in l.split(";")] == ENCABEZADO:
            idx = i
            break
    if idx is None:
        no_determinable("no se encontró el encabezado Fecha;Cliente;Moneda;Importe")

    total = Decimal(0)
    filas = 0
    excluidas_envio = 0
    fuera_periodo = 0
    pesos_por_moneda = {"$": Decimal(0), "U$S": Decimal(0)}
    cuenta = {"$": 0, "U$S": 0}

    for num, linea in enumerate(lineas[idx + 1:], start=idx + 2):
        if not linea.strip():
            continue
        campos = [c.strip() for c in linea.split(";")]
        if len(campos) != 4:
            no_determinable(f"línea {num} con {len(campos)} campos")
        fecha, cliente, moneda, importe_txt = campos

        # El flete (ENVÍO) no es venta de mercadería
        if any("ENV" in c.upper() for c in campos):
            excluidas_envio += 1
            continue

        try:
            fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError:
            no_determinable(f"línea {num} con fecha inválida: {fecha}")
        if (fecha_dt.year, fecha_dt.month) != (2026, 7):
            fuera_periodo += 1
            continue

        if moneda not in pesos_por_moneda:
            no_determinable(f"línea {num} con moneda desconocida: {moneda}")
        try:
            importe = Decimal(importe_txt.replace(",", "."))
        except InvalidOperation:
            no_determinable(f"línea {num} con importe inválido: {importe_txt}")

        pesos = importe * TIPO_CAMBIO if moneda == "U$S" else importe
        pesos_por_moneda[moneda] += pesos
        cuenta[moneda] += 1
        total += pesos
        filas += 1

    if filas == 0:
        no_determinable("ninguna fila de julio 2026 válida")

    print(f"Filas de julio: {filas} (pesos: {cuenta['$']}, U$S: {cuenta['U$S']})")
    print(f"Excluidas por ENVÍO: {excluidas_envio}; fuera de período: {fuera_periodo}")
    print(f"Total en $ de filas $: {pesos_por_moneda['$']}")
    print(f"Total en $ de filas U$S convertidas a TC {TIPO_CAMBIO}: {pesos_por_moneda['U$S']}")

    cifra = str(int(total)) if total == total.to_integral_value() else str(total)
    print(f"CIFRA: {cifra}")


if __name__ == "__main__":
    main()
```
