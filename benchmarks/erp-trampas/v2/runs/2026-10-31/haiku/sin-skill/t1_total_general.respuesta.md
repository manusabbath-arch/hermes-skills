Lo que vi en `datos/t1/ventas_marzo.csv`: 4 líneas de encabezado, 2200 filas con formato `dd/mm/aaaa;Cliente NNN;importe` (todas en marzo de 2026, importes enteros) y una línea final `;TOTAL GENERAL;468550`. El archivo no tiene columna de producto, así que no hay filas de ENVÍO que excluir. El script suma las 2200 filas, controla la suma contra el TOTAL GENERAL del export e imprime ambos valores antes de la línea final.

```python
import os
import re

RUTA = os.path.join("datos", "t1", "ventas_marzo.csv")
# Fila de venta: fecha;cliente;importe (importe entero, posible signo)
PAT = re.compile(r"^(\d{2})/(\d{2})/(\d{4});([^;]*);(-?\d+)$")

total = 0
filas = 0
fuera_de_marzo = 0
total_informado = None

# latin-1 no falla con acentos ni con bytes raros; los importes son ASCII
with open(RUTA, "rb") as f:
    lineas = f.read().decode("latin-1").splitlines()

for linea in lineas:
    linea = linea.strip()
    if not linea:
        continue
    m = PAT.match(linea)
    if m:
        dd, mm, aaaa, cliente, importe = m.groups()
        if mm == "03" and aaaa == "2026":
            total += int(importe)
            filas += 1
        else:
            fuera_de_marzo += 1
        continue
    if "TOTAL GENERAL" in linea.upper():
        total_informado = int(linea.split(";")[-1])

print(f"Filas de marzo 2026 sumadas: {filas}")
print(f"Filas fuera de marzo ignoradas: {fuera_de_marzo}")
print(f"Suma calculada: {total}")
print(f"TOTAL GENERAL informado por el ERP: {total_informado}")
if total_informado is not None and total_informado != total:
    print("ATENCION: la suma no coincide con el TOTAL GENERAL del export")

print(f"CIFRA: {total}")
```

Qué hace: suma los importes de todas las filas de venta de marzo de 2026 (en pesos, sin conversión) y no toma la línea de TOTAL GENERAL como venta. Si la suma no coincide con el total del ERP, lo avisa antes de la cifra final. No deduplica filas, porque el export no trae un identificador de comprobante que permita detectar repeticiones.
