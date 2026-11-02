#!/usr/bin/env python3
"""
puntuar.py — ¿el agente cayó en la trampa? Tabla con y sin skill, sin evaluador.

Cada respuesta termina con una línea `CIFRA: <número>` o `CIFRA: NO DETERMINABLE`.
La cifra se compara con la de `referencia.py` (tolerancia 0,5%):

  C  correcta (o NO DETERMINABLE donde la correcta es indeterminable)
  I  ingenua: la cifra de leer el archivo como viene (cayó en la trampa)
  O  otra cifra (ni la correcta ni la ingenua: error propio)
  -  sin línea CIFRA, o la respuesta no existe: cuenta como fallo, no se saltea

Una corrida es `<run>/<modelo>/<con-skill|sin-skill>/<caso>.txt`. Los negativos (pedidos simples
donde la skill no debería cambiar nada) se puntúan igual y además se cuentan sus
palabras: la skill no debería alargar una respuesta trivial.

Uso:  python3 puntuar.py --run <dir> [--suite v2]   → tabla Markdown por stdout
Exit: 0 tabla completa, 1 falta alguna respuesta (la tabla sale igual, marcada).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cargar_suite(suite: Path):
    """(casos, módulo referencia) de una suite: la v1 es esta carpeta, la v2 `v2/`."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"referencia_{suite.name}", suite / "referencia.py")
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    data = json.loads((suite / "casos.json").read_text(encoding="utf-8"))
    return (data if isinstance(data, list) else data["casos"]), ref

TOL = 0.005
CIFRA = re.compile(r"^\W*CIFRA\W*:\s*(.+?)\s*$", re.I | re.M)


def numero(texto: str) -> float | None:
    t = texto.strip().strip("*`$ ").replace("U$S", "").strip()
    if re.search(r"no\s+determinable", t, re.I):
        return None
    m = re.search(r"-?\d[\d.,]*", t)
    if not m:
        raise ValueError(t)
    s = m.group(0).rstrip(".,")
    if "," in s and "." in s:                       # 1.234,56 o 1,234.56
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if len(s.split(",")[-1]) <= 2 else s.replace(",", "")
    elif s.count(".") == 1 and len(s.split(".")[-1]) == 3:
        s = s.replace(".", "")                      # 3.030 = tres mil treinta
    elif s.count(".") > 1:
        s = s.replace(".", "")
    return float(s)


def cerca(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= TOL * max(abs(b), 1)


def clasificar(respuesta: str | None, correcta, ingenua) -> str:
    if respuesta is None:
        return "-"
    m = CIFRA.findall(respuesta)
    if not m:
        return "-"
    try:
        valor = numero(m[-1])
    except ValueError:
        return "-"
    if cerca(valor, correcta):
        return "C"
    if ingenua is not None and cerca(valor, ingenua):
        return "I"
    return "O"


def puntuar(run: Path, suite: Path = HERE) -> tuple[str, bool]:
    casos, referencia = cargar_suite(suite)
    ref = referencia.calcular(suite / "datos")
    modelos = sorted(p.name for p in run.iterdir() if p.is_dir())
    completa = bool(modelos)
    cab = "| Caso | " + " | ".join(f"{m} con skill | {m} sin skill" for m in modelos) + " |"
    out = [cab, "|" + "---|" * (1 + 2 * len(modelos))]
    tot = {(m, c): {"C": 0, "I": 0, "O": 0, "-": 0} for m in modelos for c in ("con-skill", "sin-skill")}
    palabras = {(m, c): 0 for m in modelos for c in ("con-skill", "sin-skill")}
    for caso in casos:
        cid = caso["id"]
        correcta = caso.get("correcta", ref.get(cid, {}).get("correcta"))
        ingenua = ref.get(cid, {}).get("ingenua")
        celdas = []
        for m in modelos:
            for c in ("con-skill", "sin-skill"):
                f = run / m / c / f"{cid}.txt"
                texto = f.read_text(encoding="utf-8") if f.is_file() else None
                completa &= texto is not None
                k = clasificar(texto, correcta, ingenua)
                if not caso.get("negativo"):
                    tot[(m, c)][k] += 1
                elif texto is not None:
                    # En modo script lo que se alarga es la respuesta, no la salida del script.
                    larga = f.with_suffix(".respuesta.md")
                    palabras[(m, c)] += len((larga.read_text(encoding="utf-8") if larga.is_file()
                                             else texto).split())
                celdas.append(k)
        etiqueta = f"{cid} (negativo)" if caso.get("negativo") else cid
        out.append(f"| {etiqueta} | " + " | ".join(celdas) + " |")
    n = sum(1 for c in casos if not c.get("negativo"))
    for clave, nombre in (("C", "correctas"), ("I", "cayó en la trampa"), ("O", "otra cifra"),
                          ("-", "sin cifra")):
        out.append(f"| **{nombre} (de {n})** | "
                   + " | ".join(str(tot[(m, c)][clave]) for m in modelos for c in ("con-skill", "sin-skill")) + " |")
    out.append("| palabras en negativos | "
               + " | ".join(str(palabras[(m, c)]) for m in modelos for c in ("con-skill", "sin-skill")) + " |")
    out.append("")
    out.append("C correcta · I ingenua (la trampa) · O otra cifra · - sin cifra o sin respuesta")
    if not completa:
        out.append("")
        out.append("**INCOMPLETA:** falta al menos una respuesta; cuenta como fallo.")
    return "\n".join(out) + "\n", completa


def main() -> int:
    ap = argparse.ArgumentParser(description="Puntúa una corrida del benchmark.")
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--suite", default="", help="subcarpeta de la suite (p. ej. v2); vacío = v1")
    args = ap.parse_args()
    tabla, completa = puntuar(args.run, HERE / args.suite if args.suite else HERE)
    sys.stdout.write(tabla)
    return 0 if completa else 1


if __name__ == "__main__":
    raise SystemExit(main())
