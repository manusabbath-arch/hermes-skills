#!/usr/bin/env python3
"""
activation_eval.py — ¿el agente elige la skill correcta solo por su description?

Las evals con/sin skill le DAN la skill al agente. En uso real, el agente ve solo
el `name` y la `description` de cada skill instalada y decide cuál cargar. Esta
prueba mide esa decisión:

  build  arma un prompt con las descriptions de todas las skills y una lista
         barajada de pedidos: los de cada evals.json (los positivos esperan su
         skill; los `"negativo": true` esperan ninguna) más pedidos ajenos al tap
         (esperan ninguna). Escribe el prompt y la clave por separado: el agente
         que responde nunca ve la clave.
  score  cruza la respuesta del agente ({"1": ["skill"], "2": [], ...}) con la
         clave y arma la tabla por skill: aciertos sobre sus positivos, y falsos
         positivos (la skill elegida donde no correspondía). Un pedido sin
         respuesta es ROJO.

Uso:
  python3 scripts/activation_eval.py build --out <dir>
  python3 scripts/activation_eval.py score --key <dir>/key.json --answers <answers.json>
Exit: 0 ok, 1 respuesta incompleta o ilegible.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Pedidos que ninguna skill del tap debería tomar. Fijos y versionados: si cambian,
# cambia la prueba.
OFF_TOPIC = [
    "Escribime un mail para pedirle a un cliente que confirme la reunión del martes.",
    "¿Cuál es la capital de Australia?",
    "Traducí al inglés: 'el pedido sale mañana a primera hora'.",
    "Armame un CSS para centrar un div vertical y horizontalmente.",
    "¿Qué receta puedo hacer con arroz, huevo y cebolla?",
    "Resumime en tres líneas qué es la fotosíntesis.",
    "¿Cómo configuro una regla de reenvío en Gmail?",
]


def description(skill_md: Path) -> str:
    m = re.search(r'^description:\s*"(.*)"\s*$', skill_md.read_text(encoding="utf-8"), re.M)
    if not m:
        raise SystemExit(f"{skill_md}: sin description entre comillas")
    return m.group(1)


def build(out: Path, seed: int | None) -> None:
    skills = sorted(p.name for p in (REPO / "skills").iterdir() if (p / "SKILL.md").is_file())
    items = []
    for s in skills:
        for ev in json.loads((REPO / "skills" / s / "evals" / "evals.json").read_text(encoding="utf-8")):
            items.append({"query": ev["query"], "expected": None if ev.get("negativo") else s,
                          "kind": "negativo" if ev.get("negativo") else "positivo", "owner": s})
    items += [{"query": q, "expected": None, "kind": "ajeno", "owner": None} for q in OFF_TOPIC]
    random.Random(seed).shuffle(items)

    catalog = "\n".join(f"- `{s}`: {description(REPO / 'skills' / s / 'SKILL.md')}" for s in skills)
    pedidos = "\n".join(f"{i}. {it['query']}" for i, it in enumerate(items, 1))
    prompt = f"""Tenés instaladas estas skills. De cada una solo ves su nombre y su descripción:

{catalog}

Para cada pedido de abajo, decidí qué skills cargarías antes de responderlo. Cargá una
skill solo si de verdad cambia cómo responderías; si el pedido se responde bien sin
ninguna, la lista va vacía. No respondas los pedidos: solo decidí.

{pedidos}

Respondé SOLO con un objeto JSON {{"1": ["nombre-de-skill"], "2": [], ...}} con una
entrada por pedido, usando los nombres exactos de las skills.
"""
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    key = {str(i): {k: it[k] for k in ("expected", "kind", "owner")} for i, it in enumerate(items, 1)}
    (out / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} pedidos ({sum(it['kind'] == 'positivo' for it in items)} positivos) -> {out}")


def score(key: dict, answers: dict) -> tuple[list[str], list[str]]:
    skills = sorted({v["owner"] for v in key.values() if v["owner"]})
    hits = {s: 0 for s in skills}
    pos = {s: 0 for s in skills}
    fp = {s: 0 for s in skills}
    problems = []
    for n, k in key.items():
        chosen = answers.get(n)
        if not isinstance(chosen, list):
            problems.append(f"pedido {n} sin respuesta")
            continue
        chosen = set(chosen)
        if k["expected"]:
            pos[k["expected"]] += 1
            hits[k["expected"]] += k["expected"] in chosen
        for s in chosen & set(skills):
            if s != k["expected"]:
                fp[s] += 1
    rows = ["| Skill | Elegida en sus pedidos | Falsos positivos |", "|---|---|---|"]
    rows += [f"| `{s}` | {hits[s]}/{pos[s]} | {fp[s]} |" for s in skills]
    rows.append(f"| **Total** | **{sum(hits.values())}/{sum(pos.values())}** | **{sum(fp.values())}** |")
    return rows, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--seed", type=int)
    s = sub.add_parser("score")
    s.add_argument("--key", type=Path, required=True)
    s.add_argument("--answers", type=Path, required=True)
    args = ap.parse_args(argv)

    if args.cmd == "build":
        build(args.out, args.seed)
        return 0
    key = json.loads(args.key.read_text(encoding="utf-8"))
    text = args.answers.read_text(encoding="utf-8")
    m = re.search(r"\{.*\}", text, re.S)
    try:
        answers = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        answers = None
    if not isinstance(answers, dict):
        print("ACTIVATION: ROJO, la respuesta no es un objeto JSON", file=sys.stderr)
        return 1
    rows, problems = score(key, answers)
    print("\n".join(rows))
    for p in problems:
        print(f"ROJO {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
