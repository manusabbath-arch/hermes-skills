#!/usr/bin/env python3
"""
referencia.py (v2) — la cifra ingenua y la correcta de cada trampa, leyendo los archivos.

No importa al generador ni lee `verdad.json`. Camino ingenuo: leer como viene (por
posición, sin mirar preámbulo, empresa, moneda, encoding ni claves). Camino correcto: lo
que manda `skills/erp-business-analysis`.

Uso:  python3 referencia.py [--datos <dir>]   → JSON {trampa: {correcta, ingenua}}
Exit: 0.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIPO_DE_CAMBIO = 40     # el que da el contexto de casos.json, no el generador


def lineas(path: Path, encoding: str = "utf-8") -> list[str]:
    return path.read_bytes().decode(encoding, errors="replace").splitlines()


def tabla(ls: list[str], encabezado: str) -> tuple[list[str], list[list[str]]]:
    i = next(n for n, x in enumerate(ls) if x.startswith(encabezado))
    return ls[i].split(";"), [x.split(";") for x in ls[i + 1:] if x.strip()]


def periodo_en_dias(ls: list[str]) -> int:
    m = next(re.search(r"(\d\d)/(\d\d)/(\d{4}) al (\d\d)/(\d\d)/(\d{4})", x) for x in ls
             if x.startswith("Período:"))
    return (date(int(m[6]), int(m[5]), int(m[4])) - date(int(m[3]), int(m[2]), int(m[1]))).days + 1


def t1_total_general(d: Path) -> dict:
    _, filas = tabla(lineas(d / "t1" / "ventas_marzo.csv"), "Fecha;")
    return {"correcta": sum(int(f[2]) for f in filas if not f[1].upper().startswith("TOTAL")),
            "ingenua": sum(int(f[2]) for f in filas)}


def t2_columnas(d: Path) -> dict:
    ingenua = correcta = 0
    for nombre in ("ventas_abril.csv", "ventas_mayo.csv"):
        cols, filas = tabla(lineas(d / "t2" / nombre), "Fecha;")
        ingenua += sum(int(f[3]) for f in filas)
        correcta += sum(int(f[cols.index("Importe")]) for f in filas)
    return {"correcta": correcta, "ingenua": ingenua}


def t3_periodo(d: Path) -> dict:
    ls = lineas(d / "t3" / "Ventas 2026 YTD.csv")
    total = sum(int(f[2]) for f in tabla(ls, "Fecha;")[1])
    ytd = (date(2026, 3, 31) - date(2026, 1, 1)).days + 1      # lo que promete el nombre
    return {"correcta": round(total / periodo_en_dias(ls), 2), "ingenua": round(total / ytd, 2)}


def t4_empresas(d: Path) -> dict:
    _, filas = tabla(lineas(d / "t4" / "ventas_junio.csv"), "Empresa;")
    return {"correcta": sum(int(f[3]) for f in filas if f[0] == "A"),
            "ingenua": sum(int(f[3]) for f in filas)}


def t5_monedas(d: Path) -> dict:
    _, filas = tabla(lineas(d / "t5" / "ventas_julio.csv"), "Fecha;")
    return {"correcta": sum(int(f[3]) * (TIPO_DE_CAMBIO if f[2] == "U$S" else 1) for f in filas),
            "ingenua": sum(int(f[3]) for f in filas)}


def t6_campos_muertos(d: Path) -> dict:
    _, filas = tabla(lineas(d / "t6" / "stock.csv"), "Codigo;")
    ingenua = sum(1 for f in filas if float(f[2]) < float(f[3]))
    muerto = all(float(f[3]) == 0 for f in filas)
    return {"correcta": None if muerto else ingenua, "ingenua": ingenua}


def t7_encoding(d: Path) -> dict:
    path = d / "t7" / "ventas_agosto.csv"
    _, mal = tabla(lineas(path, "utf-8"), "Fecha;")
    _, bien = tabla(lineas(path, "cp1252"), "Fecha;")
    return {"correcta": sum(int(f[3]) for f in bien if f[2] != "ENVÍO"),
            "ingenua": sum(int(f[3]) for f in mal if f[2] != "ENVÍO")}


def t8_duplicados(d: Path) -> dict:
    datos = []
    for nombre in ("cobros_01_al_10.csv", "cobros_08_al_14.csv"):
        datos += tabla(lineas(d / "t8" / nombre), "Fecha;")[1]
    por_clave: dict[tuple[str, str], int] = {}
    por_numero: dict[str, int] = {}
    for f in datos:
        por_clave.setdefault((f[1], f[2]), int(f[4]))
        por_numero.setdefault(f[2], int(f[4]))
    return {"correcta": sum(por_clave.values()), "ingenua": sum(int(f[4]) for f in datos),
            "dedup_por_numero": sum(por_numero.values())}


TRAMPAS = [t1_total_general, t2_columnas, t3_periodo, t4_empresas, t5_monedas,
           t6_campos_muertos, t7_encoding, t8_duplicados]


def calcular(datos: Path) -> dict:
    return {f.__name__: f(datos) for f in TRAMPAS}


def main() -> int:
    ap = argparse.ArgumentParser(description="Cifras de referencia de la v2.")
    ap.add_argument("--datos", type=Path, default=HERE / "datos")
    args = ap.parse_args()
    print(json.dumps(calcular(args.datos), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
