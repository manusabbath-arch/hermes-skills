#!/usr/bin/env python3
"""
generar.py — exports sintéticos de un ERP con una trampa sembrada en cada uno.

Todo es ficticio: clientes, productos, empresas e importes salen de una semilla fija.
Cada trampa es una de las que el proyecto de origen pagó con una cifra publicada mal
(ver `skills/erp-business-analysis`): la cifra ingenua es la que sale de leer el
archivo "como viene"; la correcta, la que sale de leerlo bien.

El generador escribe los archivos en `datos/` y su propia verdad en `verdad.json`
(calculada en memoria, mientras arma las filas). `referencia.py` vuelve a calcular las
cifras **leyendo los archivos**, sin mirar `verdad.json`, y el test exige que las dos
coincidan: es el canario del benchmark.

Uso:  python3 generar.py [--out <dir>]   (por defecto, junto a este script)
Exit: 0.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

SEMILLA = 20261031
HERE = Path(__file__).resolve().parent
CLIENTES = ["Almacén Norte", "Kiosco Sur", "Super Centro", "Panadería Este", "Bar Oeste",
            "Autoservicio Plaza", "Minimercado Río", "Cantina Puerto"]
PRODUCTOS = ["Galletas 200g", "Pan lactal", "Agua 2L", "Yerba 1kg", "Arroz 1kg",
             "Aceite 900ml", "Fideos 500g", "Azúcar 1kg"]


def importe(rng: random.Random) -> int:
    return rng.randrange(40, 400, 5)


def escribir(path: Path, lineas: list[str], encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\n".join(lineas) + "\n").encode(encoding))


def t1_total_general(rng, d: Path) -> dict:
    filas = [(c, importe(rng)) for c in rng.sample(CLIENTES, 8) for _ in range(2)]
    total = sum(v for _, v in filas)
    lineas = ["Informe: Ventas por cliente", "Empresa: A",
              "Período: 01/03/2026 al 31/03/2026", "", "Cliente;Importe"]
    lineas += [f"{c};{v}" for c, v in filas] + [f"TOTAL GENERAL;{total}"]
    escribir(d / "t1_total_general" / "ventas_marzo.csv", lineas)
    return {"correcta": total, "ingenua": 2 * total}


def t2_columnas(rng, d: Path) -> dict:
    abril = [(f"{rng.randint(1, 30):02d}/04/2026", rng.choice(CLIENTES), rng.choice(PRODUCTOS),
              importe(rng), rng.randint(1, 12)) for _ in range(12)]
    mayo = [(f"{rng.randint(1, 31):02d}/05/2026", rng.choice(CLIENTES), rng.choice(PRODUCTOS),
             rng.randint(1, 12), importe(rng)) for _ in range(12)]
    escribir(d / "t2_columnas" / "ventas_abril.csv",
             ["Fecha;Cliente;Producto;Importe;Cantidad"] + [";".join(map(str, f)) for f in abril])
    # El reexport de mayo cambió el orden de las columnas.
    escribir(d / "t2_columnas" / "ventas_mayo.csv",
             ["Fecha;Cliente;Producto;Cantidad;Importe"] + [";".join(map(str, f)) for f in mayo])
    correcta = sum(f[3] for f in abril) + sum(f[4] for f in mayo)
    ingenua = sum(f[3] for f in abril) + sum(f[3] for f in mayo)   # posición 3 en los dos
    return {"correcta": correcta, "ingenua": ingenua}


def t3_periodo(rng, d: Path) -> dict:
    filas = [(f"{dia:02d}/03/2026", rng.choice(CLIENTES), importe(rng)) for dia in range(1, 32)]
    total = sum(v for *_, v in filas)
    lineas = ["Informe: Ventas por día", "Empresa: A", "Período: 01/03/2026 al 31/03/2026", "",
              "Fecha;Cliente;Importe"] + [f"{a};{b};{c}" for a, b, c in filas]
    escribir(d / "t3_periodo" / "Ventas 2026 YTD.csv", lineas)
    # El nombre promete el año hasta la fecha (01/01 al 31/03 = 90 días); el preámbulo, 31.
    return {"correcta": round(total / 31, 2), "ingenua": round(total / 90, 2)}


def t4_empresas(rng, d: Path) -> dict:
    filas = [(rng.choice("AB"), rng.choice(CLIENTES), importe(rng)) for _ in range(20)]
    lineas = ["Informe: Ventas por cliente", "Empresa: (todas)", "Período: 01/06/2026 al 30/06/2026",
              "", "Empresa;Cliente;Importe"] + [f"{e};{c};{v}" for e, c, v in filas]
    escribir(d / "t4_empresas" / "ventas_junio.csv", lineas)
    return {"correcta": sum(v for e, _, v in filas if e == "A"), "ingenua": sum(v for *_, v in filas)}


def t5_monedas(rng, d: Path) -> dict:
    filas = [(rng.choice(CLIENTES), "$", importe(rng)) for _ in range(14)]
    filas += [(rng.choice(CLIENTES), "U$S", rng.randrange(10, 60, 5)) for _ in range(4)]
    rng.shuffle(filas)
    lineas = ["Informe: Ventas por cliente", "Empresa: A", "Período: 01/07/2026 al 31/07/2026", "",
              "Cliente;Moneda;Importe"] + [f"{c};{m};{v}" for c, m, v in filas]
    escribir(d / "t5_monedas" / "ventas_julio.csv", lineas)
    return {"correcta": sum(v for _, m, v in filas if m == "$"), "ingenua": sum(v for *_, v in filas)}


def t6_campos_muertos(rng, d: Path) -> dict:
    filas = [(f"P{i:03d}", p, rng.randint(3, 90)) for i, p in enumerate(PRODUCTOS, 1)]
    lineas = ["Codigo;Producto;Stock;StockMinimo;StockMaximo"]
    lineas += [f"{c};{p};{s};0.00;0.00" for c, p, s in filas]
    escribir(d / "t6_campos_muertos" / "stock.csv", lineas)
    # Ingenua: "ningún producto está por debajo del mínimo". Correcta: no se puede saber,
    # el mínimo está en 0.00 en el 100% de las filas (campo que nadie carga).
    return {"correcta": None, "ingenua": sum(1 for *_, s in filas if s < 0)}


def t7_encoding(rng, d: Path) -> dict:
    filas = [(rng.choice(CLIENTES), rng.choice(PRODUCTOS), importe(rng)) for _ in range(14)]
    filas += [(rng.choice(CLIENTES), "ENVÍO", rng.randrange(20, 60, 5)) for _ in range(4)]
    rng.shuffle(filas)
    lineas = ["Informe: Ventas por producto", "Empresa: A", "Período: 01/08/2026 al 31/08/2026", "",
              "Cliente;Producto;Importe"] + [f"{c};{p};{v}" for c, p, v in filas]
    escribir(d / "t7_encoding" / "ventas_agosto.csv", lineas, encoding="cp1252")
    # Leído como UTF-8, "ENVÍO" no coincide con el nombre del flete y el flete queda adentro.
    return {"correcta": sum(v for _, p, v in filas if p != "ENVÍO"),
            "ingenua": sum(v for *_, v in filas)}


def t8_duplicados(rng, d: Path) -> dict:
    docs = []
    for dia in range(1, 15):
        for _ in range(2):
            docs.append((f"{dia:02d}/09/2026", rng.choice("AB"), rng.randint(100, 140),
                         rng.choice(CLIENTES), importe(rng)))
    # Claves únicas por (serie, número); el mismo número en otra serie es otro documento.
    vistos, unicos = set(), []
    for doc in docs:
        if (doc[1], doc[2]) not in vistos:
            vistos.add((doc[1], doc[2]))
            unicos.append(doc)
    primero = [x for x in unicos if int(x[0][:2]) <= 10]
    segundo = [x for x in unicos if int(x[0][:2]) >= 8]       # se solapa del 8 al 10
    enc = "Fecha;Serie;Numero;Cliente;Importe"
    lineas = ["Informe: Cobros (unión de dos exports: 01-10/09 y 08-14/09)", "Empresa: A", "", enc]
    lineas += [";".join(map(str, x)) for x in primero] + [enc] + [";".join(map(str, x)) for x in segundo]
    escribir(d / "t8_duplicados" / "cobros_1_al_14.csv", lineas)
    por_numero: dict[int, int] = {}
    for x in primero + segundo:
        por_numero.setdefault(x[2], x[4])
    return {"correcta": sum(x[4] for x in unicos),
            "ingenua": sum(x[4] for x in primero + segundo),
            "dedup_por_numero": sum(por_numero.values())}


TRAMPAS = [t1_total_general, t2_columnas, t3_periodo, t4_empresas, t5_monedas,
           t6_campos_muertos, t7_encoding, t8_duplicados]


def generar(out: Path) -> dict:
    rng = random.Random(SEMILLA)
    datos = out / "datos"
    verdad = {f.__name__: f(rng, datos) for f in TRAMPAS}
    (out / "verdad.json").write_text(json.dumps(verdad, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8", newline="\n")
    return verdad


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera los exports sintéticos del benchmark.")
    ap.add_argument("--out", type=Path, default=HERE)
    args = ap.parse_args()
    verdad = generar(args.out)
    print(f"{len(verdad)} trampas generadas en {args.out / 'datos'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
