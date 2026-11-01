Filtré el archivo a la empresa A (la que representamos) y sumé el campo `Importe` de junio, en pesos. El tipo de cambio no se usa porque los importes ya están en pesos. El archivo no tiene columna de producto, así que no puedo excluir ENVÍO por ese campo. Revisé las filas con búsquedas y todas las líneas de datos tienen el mismo formato (2200), así que no hay filas raras que descartar. El script igual cuenta y muestra las líneas no reconocidas.

```python
import re

RUTA = "datos/t4/ventas_junio.csv"
EMPRESA = "A"
# Empresa;Fecha;Cliente;Importe  ->  A;25/06/2026;Cliente 058;355
PATRON = re.compile(r"^(A|B);(\d{2})/(\d{2})/(\d{4});(Cliente \d{3});(\d+)$")

total = 0
filas_empresa = 0
filas_otra_empresa = 0
fuera_de_junio = 0
no_reconocidas = []

with open(RUTA, encoding="latin-1") as f:
    for linea in f:
        linea = linea.strip()
        if not linea:
            continue
        m = PATRON.match(linea)
        if not m:
            # encabezado, título, período, etc.
            no_reconocidas.append(linea)
            continue
        emp, dd, mm, yyyy, cliente, importe = m.groups()
        if mm != "06" or yyyy != "2026":
            fuera_de_junio += 1
            continue
        if emp != EMPRESA:
            filas_otra_empresa += 1
            continue
        filas_empresa += 1
        total += int(importe)

print(f"Filas de junio, empresa {EMPRESA}: {filas_empresa}")
print(f"Filas de otra empresa (excluidas): {filas_otra_empresa}")
print(f"Filas fuera de junio (excluidas): {fuera_de_junio}")
print(f"Líneas no reconocidas (encabezados, etc.): {len(no_reconocidas)}")
for l in no_reconocidas[:10]:
    print("  ", l)
print(f"Total ventas empresa {EMPRESA}, junio 2026: ${total}")
print(f"Equivalente en U$S (40 $/U$S): {total / 40:.2f}")
print(f"CIFRA: {total}")
```

Qué hace: lee `datos/t4/ventas_junio.csv`, deja las filas de la empresa A con fecha en junio de 2026 y suma `Importe` en pesos. Imprime los contadores y el equivalente en dólares como control. La última línea es `CIFRA: <total>`.

Supuestos:
- **Empresa:** el informe dice "Empresa: (todas)" y trae filas de A y de B. Tomé solo la A porque trabajamos para ella. Si B forma parte de nuestras ventas, habría que sumarla.
- **ENVÍO:** no hay columna de producto, así que no excluyo fletes. Si algún importe corresponde a ENVÍO, quedaría incluido.
- **Duplicados:** no deduplico. Sin número de comprobante no puedo distinguir un duplicado de dos ventas reales al mismo cliente.

No pude ejecutar el script; el resultado queda para cuando lo corras desde la carpeta del proyecto.
