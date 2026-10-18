#!/usr/bin/env python3
"""
eval_report.py — junta las notas de un evaluador ciego y arma la tabla con/sin skill.

Cada skill trae evals/evals.json (pedido + comportamiento esperado). Una corrida
de evaluación produce, por skill, dos respuestas anónimas (A y B: una con la skill
cargada, otra sin) y un archivo de notas del evaluador, que no sabe cuál es cuál:

  grades/<skill>.json = [{"pedido": 1, "criterio": 1, "A": true, "B": false}, ...]

La clave que revela qué letra tuvo la skill vive aparte (key.json) y solo la lee
este script. Salida: una tabla Markdown por skill con criterios cumplidos con y sin
skill, y el delta. Una skill sin notas, o con criterios sin calificar, es ROJO: un
reporte que no midió algo no puede mostrarlo como medido.

Uso:  python3 scripts/eval_report.py --grades <dir> --key <key.json>
Exit: 0 tabla completa, 1 faltan notas o criterios.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def expected_counts(skill: str) -> list[int]:
    evals = json.loads((REPO / "skills" / skill / "evals" / "evals.json").read_text(encoding="utf-8"))
    return [len(e["expected_behavior"]) for e in evals]


def score(skill: str, grades: list[dict], key: dict) -> tuple[int, int, int, list[str]]:
    """(cumplidos con skill, cumplidos sin skill, total, problemas)."""
    w, wo = key["with_skill"], key["without_skill"]
    problems: list[str] = []
    seen = {(g["pedido"], g["criterio"]): g for g in grades}
    total = with_ok = without_ok = 0
    for p, n in enumerate(expected_counts(skill), 1):
        for c in range(1, n + 1):
            g = seen.get((p, c))
            if g is None or not isinstance(g.get(w), bool) or not isinstance(g.get(wo), bool):
                problems.append(f"{skill}: pedido {p} criterio {c} sin calificar")
                continue
            total += 1
            with_ok += g[w]
            without_ok += g[wo]
    return with_ok, without_ok, total, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--grades", type=Path, required=True)
    ap.add_argument("--key", type=Path, required=True)
    args = ap.parse_args(argv)
    keys = json.loads(args.key.read_text(encoding="utf-8"))

    rows, problems = [], []
    tw = two = tt = 0
    for skill in sorted(keys):
        f = args.grades / f"{skill}.json"
        if not f.is_file():
            problems.append(f"{skill}: sin archivo de notas")
            continue
        w, wo, t, probs = score(skill, json.loads(f.read_text(encoding="utf-8")), keys[skill])
        problems += probs
        tw, two, tt = tw + w, two + wo, tt + t
        rows.append(f"| `{skill}` | {w}/{t} | {wo}/{t} | {w - wo:+d} |")

    print("| Skill | Con skill | Sin skill | Delta |")
    print("|---|---|---|---|")
    print("\n".join(rows))
    print(f"| **Total** | **{tw}/{tt}** | **{two}/{tt}** | **{tw - two:+d}** |")
    for p in problems:
        print(f"ROJO {p}", file=sys.stderr)
    return 1 if problems or tt == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
