El export no trae producto ni moneda, así que no hay flete (ENVÍO) que separar. El archivo mezcla las empresas A y B, y la pregunta es por la empresa A. El script suma solo las filas de la empresa A con fecha de junio de 2026.

Antes de sumar, el script:
- lee el preámbulo y el encabezado por nombre de columna;
- descarta filas de total o subtotal y filas mal formadas, y las cuenta;
- avisa si hay filas duplicadas exactas o importes con decimales;
- imprime el desglose por empresa como control.

La última línea impresa es `CIFRA`.

```python
import csv, re, io
from collections import defaultdict
from decimal import Decimal, InvalidOperation

PATH = "datos/t4/ventas_junio.csv"
raw = open(PATH, "rb").read()
try:
    text = raw.decode("utf-8-sig")
except UnicodeDecodeError:
    text = raw.decode("cp1252")
lines = text.splitlines()

# preámbulo
for l in lines[:4]:
    print("PREAMBULO:", l)

# encabezado por nombre
hi = next(i for i, l in enumerate(lines) if l.split(";")[0].strip() == "Empresa" and "Importe" in l)
header = [h.strip() for h in lines[hi].split(";")]
ix = {h: header.index(h) for h in ("Empresa", "Fecha", "Cliente", "Importe")}
print("ENCABEZADO:", header)

def parse_amount(s):
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    return Decimal(s)

tot = defaultdict(Decimal)
cnt = defaultdict(int)
descartadas = []
fuera_periodo = 0
seen = defaultdict(int)
decimales = 0

for l in lines[hi + 1:]:
    if not l.strip():
        continue
    p = l.split(";")
    if len(p) < len(header):
        descartadas.append(l); continue
    emp = p[ix["Empresa"]].strip()
    fecha = p[ix["Fecha"]].strip()
    cli = p[ix["Cliente"]].strip()
    m = re.fullmatch(r"(\d\d)/(\d\d)/(\d{4})", fecha)
    if not m or re.search(r"total", l, re.I):
        descartadas.append(l); continue
    try:
        imp = parse_amount(p[ix["Importe"]])
    except InvalidOperation:
        descartadas.append(l); continue
    if (m.group(2), m.group(3)) != ("06", "2026"):
        fuera_periodo += 1
        continue
    if imp != imp.to_integral_value():
        decimales += 1
    seen[l.strip()] += 1
    tot[emp] += imp
    cnt[emp] += 1

print("FILAS POR EMPRESA:", dict(cnt))
print("TOTAL POR EMPRESA:", {k: str(v) for k, v in tot.items()})
print("DESCARTADAS:", len(descartadas), descartadas[:5])
print("FUERA DE PERIODO:", fuera_periodo)
print("IMPORTES CON DECIMALES:", decimales)
print("FILAS DUPLICADAS EXACTAS (informativo):", sum(1 for v in seen.values() if v > 1))

res = tot.get("A", Decimal(0))
if cnt.get("A", 0) == 0:
    print("CIFRA: NO DETERMINABLE")
else:
    out = res.normalize() if res != res.to_integral_value() else res.to_integral_value()
    print(f"CIFRA: {out}")
```
