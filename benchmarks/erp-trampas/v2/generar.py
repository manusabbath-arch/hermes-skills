#!/usr/bin/env python3
"""
generar.py (v2) — las mismas ocho trampas, en exports que no se pueden leer enteros.

La v1 (`../generar.py`) no discriminó: con 20 filas el sujeto ve la fila mala, y la
pregunta nombraba la dimensión de la trampa (ver `../runs/2026-10-31/LECTURA.md`). En la
v2 cada export tiene más de 2.000 filas de datos (más de lo que una lectura muestra de una
vez), así que el sujeto tiene que escribir código, que es como la trampa mordió en el
proyecto de origen. Las preguntas están en `casos.json` y no nombran la trampa.

Todo es ficticio (semilla fija). Escribe `datos/` y `verdad.json`; `referencia.py` vuelve a
calcular desde los archivos y el test exige que coincidan (canario).

Uso:  python3 generar.py [--out <dir>]
Exit: 0.
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 20261101
FILAS = 2200
TIPO_DE_CAMBIO = 40          # $ por U$S, el que da el contexto de `casos.json`
HERE = Path(__file__).resolve().parent
CLIENTES = [f"Cliente {i:03d}" for i in range(1, 181)]
PRODUCTOS = [f"Producto {i:04d}" for i in range(1, 401)]


def importe(rng: random.Random) -> int:
    return rng.randrange(40, 400, 5)


def dia(rng: random.Random, anio: int, mes: int, hasta: int) -> str:
    return f"{rng.randint(1, hasta):02d}/{mes:02d}/{anio}"


def escribir(path: Path, lineas: list[str], encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\n".join(lineas) + "\n").encode(encoding))


def preambulo(informe: str, empresa: str, desde: str, hasta: str) -> list[str]:
    return [f"Informe: {informe}", f"Empresa: {empresa}", f"Período: {desde} al {hasta}", ""]


def t1_total_general(rng, d: Path) -> dict:
    filas = [(dia(rng, 2026, 3, 31), rng.choice(CLIENTES), importe(rng)) for _ in range(FILAS)]
    total = sum(v for *_, v in filas)
    lineas = preambulo("Ventas por cliente", "A", "01/03/2026", "31/03/2026") + ["Fecha;Cliente;Importe"]
    lineas += [f"{a};{b};{c}" for a, b, c in filas] + [f";TOTAL GENERAL;{total}"]
    escribir(d / "t1" / "ventas_marzo.csv", lineas)
    return {"correcta": total, "ingenua": 2 * total}


def t2_columnas(rng, d: Path) -> dict:
    n = FILAS // 2 + 100
    abril = [(dia(rng, 2026, 4, 30), rng.choice(CLIENTES), rng.choice(PRODUCTOS),
              importe(rng), rng.randint(1, 12)) for _ in range(n)]
    mayo = [(dia(rng, 2026, 5, 31), rng.choice(CLIENTES), rng.choice(PRODUCTOS),
             rng.randint(1, 12), importe(rng)) for _ in range(n)]
    escribir(d / "t2" / "ventas_abril.csv",
             ["Fecha;Cliente;Producto;Importe;Cantidad"] + [";".join(map(str, f)) for f in abril])
    escribir(d / "t2" / "ventas_mayo.csv",          # el reexport cambió el orden de columnas
             ["Fecha;Cliente;Producto;Cantidad;Importe"] + [";".join(map(str, f)) for f in mayo])
    return {"correcta": sum(f[3] for f in abril) + sum(f[4] for f in mayo),
            "ingenua": sum(f[3] for f in abril) + sum(f[3] for f in mayo)}


def t3_periodo(rng, d: Path) -> dict:
    filas = [(dia(rng, 2026, 3, 31), rng.choice(CLIENTES), importe(rng)) for _ in range(FILAS)]
    total = sum(v for *_, v in filas)
    lineas = preambulo("Ventas por día", "A", "01/03/2026", "31/03/2026") + ["Fecha;Cliente;Importe"]
    lineas += [f"{a};{b};{c}" for a, b, c in filas]
    escribir(d / "t3" / "Ventas 2026 YTD.csv", lineas)
    return {"correcta": round(total / 31, 2), "ingenua": round(total / 90, 2)}


def t4_empresas(rng, d: Path) -> dict:
    filas = [(rng.choice("AB"), dia(rng, 2026, 6, 30), rng.choice(CLIENTES), importe(rng))
             for _ in range(FILAS)]
    lineas = preambulo("Ventas por cliente", "(todas)", "01/06/2026", "30/06/2026")
    lineas += ["Empresa;Fecha;Cliente;Importe"] + [";".join(map(str, f)) for f in filas]
    escribir(d / "t4" / "ventas_junio.csv", lineas)
    return {"correcta": sum(f[3] for f in filas if f[0] == "A"), "ingenua": sum(f[3] for f in filas)}


def t5_monedas(rng, d: Path) -> dict:
    filas = []
    for _ in range(FILAS):
        if rng.random() < 0.15:
            filas.append((dia(rng, 2026, 7, 31), rng.choice(CLIENTES), "U$S", rng.randrange(10, 60, 5)))
        else:
            filas.append((dia(rng, 2026, 7, 31), rng.choice(CLIENTES), "$", importe(rng)))
    lineas = preambulo("Ventas por cliente", "A", "01/07/2026", "31/07/2026")
    lineas += ["Fecha;Cliente;Moneda;Importe"] + [";".join(map(str, f)) for f in filas]
    escribir(d / "t5" / "ventas_julio.csv", lineas)
    pesos = sum(f[3] for f in filas if f[2] == "$")
    dolares = sum(f[3] for f in filas if f[2] == "U$S")
    return {"correcta": pesos + TIPO_DE_CAMBIO * dolares, "ingenua": pesos + dolares}


def t6_campos_muertos(rng, d: Path) -> dict:
    filas = [(f"P{i:05d}", f"Artículo {i:05d}", rng.randint(0, 90)) for i in range(1, FILAS + 1)]
    lineas = ["Codigo;Producto;Stock;StockMinimo;StockMaximo"]
    lineas += [f"{c};{p};{s};0.00;0.00" for c, p, s in filas]
    escribir(d / "t6" / "stock.csv", lineas)
    # Ingenua: stock < mínimo con el mínimo en 0.00 -> 0 productos. Correcta: no se puede
    # saber, el mínimo es 0.00 en el 100% de las filas (campo que nadie carga).
    return {"correcta": None, "ingenua": sum(1 for *_, s in filas if s < 0)}


def t7_encoding(rng, d: Path) -> dict:
    filas = []
    for _ in range(FILAS):
        if rng.random() < 0.12:
            filas.append((dia(rng, 2026, 8, 31), rng.choice(CLIENTES), "ENVÍO", rng.randrange(20, 60, 5)))
        else:
            filas.append((dia(rng, 2026, 8, 31), rng.choice(CLIENTES), rng.choice(PRODUCTOS), importe(rng)))
    lineas = preambulo("Ventas por producto", "A", "01/08/2026", "31/08/2026")
    lineas += ["Fecha;Cliente;Producto;Importe"] + [";".join(map(str, f)) for f in filas]
    escribir(d / "t7" / "ventas_agosto.csv", lineas, encoding="cp1252")
    # Leído como UTF-8 con reemplazo, "ENVÍO" no coincide y el flete queda adentro.
    return {"correcta": sum(f[3] for f in filas if f[2] != "ENVÍO"),
            "ingenua": sum(f[3] for f in filas)}


def t8_duplicados(rng, d: Path) -> dict:
    docs, vistos = [], set()
    inicio = date(2026, 9, 1)
    while len(docs) < FILAS:
        serie, numero = rng.choice("AB"), rng.randint(10000, 12000)
        if (serie, numero) in vistos:
            continue
        vistos.add((serie, numero))
        fecha = inicio + timedelta(days=rng.randint(0, 13))
        docs.append((fecha.strftime("%d/%m/%Y"), serie, numero, rng.choice(CLIENTES), importe(rng)))
    primero = [x for x in docs if int(x[0][:2]) <= 10]
    segundo = [x for x in docs if int(x[0][:2]) >= 8]        # se solapan del 8 al 10
    enc = "Fecha;Serie;Numero;Cliente;Importe"
    escribir(d / "t8" / "cobros_01_al_10.csv",
             preambulo("Cobros", "A", "01/09/2026", "10/09/2026") + [enc] + [";".join(map(str, x)) for x in primero])
    escribir(d / "t8" / "cobros_08_al_14.csv",
             preambulo("Cobros", "A", "08/09/2026", "14/09/2026") + [enc] + [";".join(map(str, x)) for x in segundo])
    por_numero: dict[int, int] = {}
    for x in primero + segundo:
        por_numero.setdefault(x[2], x[4])
    return {"correcta": sum(x[4] for x in docs),
            "ingenua": sum(x[4] for x in primero + segundo),
            "dedup_por_numero": sum(por_numero.values())}


TRAMPAS = [t1_total_general, t2_columnas, t3_periodo, t4_empresas, t5_monedas,
           t6_campos_muertos, t7_encoding, t8_duplicados]


def generar(out: Path) -> dict:
    rng = random.Random(SEMILLA)
    verdad = {f.__name__: f(rng, out / "datos") for f in TRAMPAS}
    (out / "verdad.json").write_text(json.dumps(verdad, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8", newline="\n")
    return verdad


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera los exports sintéticos de la v2.")
    ap.add_argument("--out", type=Path, default=HERE)
    args = ap.parse_args()
    verdad = generar(args.out)
    print(f"{len(verdad)} trampas generadas en {args.out / 'datos'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
