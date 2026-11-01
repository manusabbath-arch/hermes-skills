#!/usr/bin/env python3
"""
ronda.py — corre una ronda de evals con/sin skill y evaluador ciego, con tope de gasto.

Automatiza los pasos 1-3 de EVALS.md §7 con `claude -p`:
  1. Foto de los escenarios: <out>/evals/<skill>.json (solo los pedidos elegidos).
  2. Por modelo, la letra de la skill se sortea con --semilla y queda en <out>/<modelo>/key.json.
  3. Sujetos: uno con la skill (copia de la carpeta, sin evals/ ni tests/) y uno sin nada,
     con Read/Glob/Grep sobre su carpeta y sin comandos ni web. Responden todos los pedidos
     de la skill en una llamada: <out>/<modelo>/answers/<skill>.<A|B>.md.
  4. Evaluador ciego (--evaluador): recibe criterios y las respuestas A y B, sin la clave;
     escribe <out>/<modelo>/grades/<skill>.json. Un JSON que no se puede leer queda en
     .crudo.txt y la tabla sale en rojo: no se completa a mano.
La tabla la arma `scripts/eval_report.py`, igual que las rondas anteriores.

Gasto: --tope-usd es obligatorio y es el tope de TODA la ronda; cada llamada lleva
`--max-budget-usd` = lo que queda repartido entre las que faltan. Nunca se programa.

Uso:  python3 evals/ronda.py --out evals/runs/<fecha> --tope-usd 3 --modelos haiku,sonnet \
          --skills erp-business-analysis:7,8,9,designing-mechanical-guards [--semilla 1]
Exit: 0 terminó dentro del tope, 1 cortó por tope o por error, 2 uso.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"

SUJETO = """Respondé los pedidos de abajo como en una conversación con quien los hace: no hay \
archivos adjuntos ni podés correr comandos. Respondé cada uno bajo su propio encabezado \
`## Pedido <n>`, en el idioma del pedido, sin nombrar ni citar archivos de esta carpeta.
"""
CON_SKILL = """En `skill/` tenés una skill: leé `skill/SKILL.md` antes de responder y las \
referencias que te indique para cada pedido. Aplicala solo donde corresponda.

"""
EVALUADOR = """Sos un evaluador ciego. Para cada pedido hay criterios numerados y dos \
respuestas, A y B, de dos asistentes distintos. Para cada criterio decidí si A lo cumple y si \
B lo cumple, de forma independiente: no es una comparación, las dos pueden cumplirlo o no.

Devolvé SOLO un bloque ```json con una lista de objetos \
{"pedido": n, "criterio": k, "A": true|false, "B": true|false, "nota": "<una línea>"}, \
uno por cada criterio de cada pedido, sin omitir ninguno.
"""


def carpeta(con_skill: bool) -> str:
    # No "con": en Windows CON es un dispositivo reservado y mkdir falla (WinError 267).
    return "con-skill" if con_skill else "sin-skill"


def parse_skills(spec: str) -> list[tuple[str, list[int] | None]]:
    """`a:7,8,b` -> [("a", [7, 8]), ("b", None)]. Los números son 1-based en evals.json."""
    out: list[tuple[str, list[int] | None]] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if part.isdigit():
            if not out or out[-1][1] is None:
                raise ValueError(f"número {part} sin skill delante")
            out[-1][1].append(int(part))
        elif ":" in part:
            name, n = part.split(":", 1)
            out.append((name, [int(n)]))
        else:
            out.append((part, None))
    return out


def foto(skill: str, pedidos: list[int] | None) -> list[dict]:
    evals = json.loads((SKILLS / skill / "evals" / "evals.json").read_text(encoding="utf-8"))
    return evals if pedidos is None else [evals[i - 1] for i in pedidos]


def sortear(skills: list[str], semilla: int, modelo: str) -> dict:
    rng = random.Random(f"{semilla}:{modelo}")
    key = {}
    for s in sorted(skills):
        w = rng.choice("AB")
        key[s] = {"with_skill": w, "without_skill": "B" if w == "A" else "A"}
    return key


def prompt_sujeto(evals: list[dict], con_skill: bool) -> str:
    pedidos = "\n\n".join(f"## Pedido {i}\n\n{e['query']}" for i, e in enumerate(evals, 1))
    return (CON_SKILL if con_skill else "") + SUJETO + "\n" + pedidos + "\n"


def prompt_evaluador(evals: list[dict], a: str, b: str) -> str:
    partes = [EVALUADOR]
    for i, e in enumerate(evals, 1):
        crit = "\n".join(f"  {k}. {c}" for k, c in enumerate(e["expected_behavior"], 1))
        partes.append(f"### Pedido {i}: {e['query']}\nCriterios:\n{crit}")
    partes.append(f"=== RESPUESTA A ===\n{a}\n=== FIN A ===\n\n=== RESPUESTA B ===\n{b}\n=== FIN B ===")
    return "\n\n".join(partes) + "\n"


def leer_notas(texto: str, evals: list[dict]) -> list[dict] | None:
    """La lista del último bloque json, solo si trae exactamente los criterios pedidos."""
    bloques = re.findall(r"```json\s*\n(.*?)```", texto, re.S)
    if not bloques:
        return None
    try:
        notas = json.loads(bloques[-1])
    except json.JSONDecodeError:
        return None
    if not isinstance(notas, list):
        return None
    pedidos = {(i, k) for i, e in enumerate(evals, 1) for k in range(1, len(e["expected_behavior"]) + 1)}
    vistos = set()
    for n in notas:
        if not isinstance(n, dict) or not isinstance(n.get("A"), bool) or not isinstance(n.get("B"), bool):
            return None
        vistos.add((n.get("pedido"), n.get("criterio")))
    return notas if vistos == pedidos and len(notas) == len(pedidos) else None


def llamar(cwd: Path, modelo: str, prompt: str, presupuesto: float) -> tuple[str, float]:
    cmd = ["claude", "-p", "--setting-sources", "", "--disable-slash-commands", "--model", modelo,
           "--tools", "Read,Glob,Grep", "--strict-mcp-config", "--no-session-persistence",
           "--output-format", "json", "--max-budget-usd", f"{presupuesto:.2f}"]
    exe = shutil.which(cmd[0])
    if exe is None:
        raise RuntimeError("no se encontró `claude` en el PATH")
    # Prompt por stdin: en Windows `claude` es un .CMD y cmd.exe corta en el salto de línea.
    proc = subprocess.run([exe, *cmd[1:]], cwd=cwd, input=prompt.encode("utf-8"),
                          capture_output=True, timeout=900)
    try:
        data = json.loads(proc.stdout.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        raise RuntimeError(f"salida no es JSON (exit {proc.returncode}): "
                           f"{proc.stderr.decode('utf-8', errors='replace')[:300]}") from None
    return str(data.get("result", "")), float(data.get("total_cost_usd", 0.0))


def escribir(p: Path, texto: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Ronda de evals con/sin skill (gasta dinero).")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tope-usd", type=float, required=True)
    ap.add_argument("--modelos", default="haiku,sonnet")
    ap.add_argument("--skills", required=True)
    ap.add_argument("--evaluador", default="sonnet")
    ap.add_argument("--semilla", type=int, default=1)
    args = ap.parse_args()
    if args.tope_usd <= 0:
        print("[ERROR] --tope-usd tiene que ser > 0", file=sys.stderr)
        return 2
    elegidas = parse_skills(args.skills)
    modelos = [m for m in args.modelos.split(",") if m]
    fotos = {s: foto(s, p) for s, p in elegidas}
    for s, ev in fotos.items():
        escribir(args.out / "evals" / f"{s}.json", json.dumps(ev, indent=2, ensure_ascii=False))
    claves = {m: sortear(list(fotos), args.semilla, m) for m in modelos}
    for m in modelos:
        escribir(args.out / m / "key.json", json.dumps(claves[m], indent=1))

    n_llamadas = len(modelos) * len(fotos) * 3
    hechas, gastado, costos, cortado = 0, 0.0, [], False

    def presupuesto() -> float:
        return (args.tope_usd - gastado) / max(1, n_llamadas - hechas)

    with tempfile.TemporaryDirectory(prefix="ronda-") as tmp:
        tmp = Path(tmp)
        (tmp / "vacio").mkdir()
        for m in modelos:
            for s, ev in fotos.items():
                respuestas = {}
                for con in (True, False):
                    if presupuesto() < 0.01:
                        cortado = True
                        break
                    cwd = tmp / m / s / carpeta(con)
                    cwd.mkdir(parents=True)
                    if con:
                        shutil.copytree(SKILLS / s, cwd / "skill",
                                        ignore=shutil.ignore_patterns("evals", "tests", "__pycache__"))
                    try:
                        texto, costo = llamar(cwd, m, prompt_sujeto(ev, con), presupuesto())
                    except (RuntimeError, subprocess.TimeoutExpired) as exc:
                        print(f"[ERROR] {m}/{s}/{'con' if con else 'sin'}: {exc}", file=sys.stderr)
                        cortado = True
                        hechas += 1
                        continue
                    hechas += 1
                    gastado += costo
                    letra = claves[m][s]["with_skill" if con else "without_skill"]
                    respuestas[letra] = texto
                    escribir(args.out / m / "answers" / f"{s}.{letra}.md", texto)
                    costos.append({"rol": "sujeto", "modelo": m, "skill": s, "condicion": "con" if con else "sin",
                                   "usd": round(costo, 4)})
                    print(f"{m}/{s}/{'con' if con else 'sin'}: {costo:.3f} USD (acumulado {gastado:.2f})")
                if len(respuestas) < 2 or presupuesto() < 0.01:
                    cortado = True
                    hechas += 1
                    continue
                try:
                    texto, costo = llamar(tmp / "vacio", args.evaluador,
                                          prompt_evaluador(ev, respuestas["A"], respuestas["B"]), presupuesto())
                except (RuntimeError, subprocess.TimeoutExpired) as exc:
                    print(f"[ERROR] evaluador {m}/{s}: {exc}", file=sys.stderr)
                    cortado = True
                    hechas += 1
                    continue
                hechas += 1
                gastado += costo
                costos.append({"rol": "evaluador", "modelo": args.evaluador, "de": m, "skill": s,
                               "usd": round(costo, 4)})
                notas = leer_notas(texto, ev)
                if notas is None:
                    escribir(args.out / m / "grades" / f"{s}.crudo.txt", texto)
                    print(f"[ROJO] evaluador {m}/{s}: notas ilegibles o incompletas (.crudo.txt)")
                    cortado = True
                else:
                    escribir(args.out / m / "grades" / f"{s}.json", json.dumps(notas, indent=1, ensure_ascii=False))
                print(f"evaluador {m}/{s}: {costo:.3f} USD (acumulado {gastado:.2f})")
    escribir(args.out / "costos.json", json.dumps(
        {"tope_usd": args.tope_usd, "gastado_usd": round(gastado, 4), "evaluador": args.evaluador,
         "semilla": args.semilla, "llamadas": costos}, indent=2, ensure_ascii=False))
    return 1 if cortado else 0


if __name__ == "__main__":
    raise SystemExit(main())
