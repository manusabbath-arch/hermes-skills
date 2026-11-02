El export tiene un preámbulo de 4 líneas y las columnas `Fecha;Cliente;Producto;Importe`. Está en cp1252 y declara Empresa A, período 01/08/2026 al 31/08/2026. Hay filas `ENVÍO` (flete).

El script hace lo siguiente:
- Lee el archivo en cp1252 y busca el encabezado por nombre de columna.
- Descarta subtotales y totales.
- Excluye `ENVÍO`, porque es flete y no mercadería.
- Se queda con las fechas de agosto de 2026.
- Parsea los importes con cuidado, sin `replace` a ciegas.
- Suma los importes en pesos.
- Imprime diagnósticos: filas leídas, descartadas y de envío, y la suma de control.

Antes de la cifra, el script imprime el detalle de las filas raras que descarta.

```python
import csv, re, unicodedata
from decimal import Decimal, InvalidOperation

PATH = "datos/t7/ventas_agosto.csv"

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.upper().strip()

def parse_amount(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if not s:
        raise InvalidOperation
    if "," in s and "." in s:
        # el último separador es el decimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    return Decimal(s)

with open(PATH, "r", encoding="cp1252", newline="") as f:
    lines = f.read().splitlines()

hdr_idx = None
for i, l in enumerate(lines):
    cols = [norm(c) for c in l.split(";")]
    if "FECHA" in cols and "IMPORTE" in cols and "PRODUCTO" in cols:
        hdr_idx = i
        break
if hdr_idx is None:
    raise SystemExit("sin encabezado")

header = [norm(c) for c in lines[hdr_idx].split(";")]
iF, iP, iI = header.index("FECHA"), header.index("PRODUCTO"), header.index("IMPORTE")
print("Preambulo:", lines[:hdr_idx])
print("Encabezado:", header)

total = Decimal(0)
envio = Decimal(0)
n_ok = n_env = n_desc = 0
for l in lines[hdr_idx + 1:]:
    if not l.strip():
        continue
    parts = l.split(";")
    if len(parts) <= max(iF, iP, iI):
        n_desc += 1
        print("DESCARTADA (cols):", l)
        continue
    fecha, prod, imp = parts[iF].strip(), parts[iP].strip(), parts[iI]
    if "TOTAL" in norm(l):
        n_desc += 1
        print("DESCARTADA (total):", l)
        continue
    m = re.fullmatch(r"(\d\d)/(\d\d)/(\d{4})", fecha)
    if not m or m.group(2) != "08" or m.group(3) != "2026":
        n_desc += 1
        print("DESCARTADA (fecha):", l)
        continue
    try:
        v = parse_amount(imp)
    except InvalidOperation:
        n_desc += 1
        print("DESCARTADA (importe):", l)
        continue
    if norm(prod) == "ENVIO":
        envio += v
        n_env += 1
        continue
    total += v
    n_ok += 1

print("filas mercaderia:", n_ok, "| filas envio:", n_env, "| descartadas:", n_desc)
print("envio excluido ($):", envio)
print("mercaderia ($):", total)
out = total
if out == out.to_integral_value():
    out = int(out)
print(f"CIFRA: {out}")
```
