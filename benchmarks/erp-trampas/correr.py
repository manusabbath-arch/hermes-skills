#!/usr/bin/env python3
"""
correr.py — corre los casos del benchmark con y sin `erp-business-analysis`.

GASTA DINERO: cada caso es una llamada a un modelo. Por eso:
  - `--tope-usd` es obligatorio y es el tope de TODA la corrida; cada llamada lleva
    `--max-budget-usd` = lo que queda del tope repartido entre las llamadas que faltan.
    Al pasarlo se corta, y los casos que quedan puntúan como fallo (`-`).
  - Nunca se programa: lo corre una persona, en el momento.

Aislamiento: cada (modelo, condición) trabaja en una carpeta propia que solo tiene una
copia de `datos/` (y, con skill, una copia de la skill en `skill/`). Se usa
`claude -p --bare` (sin CLAUDE.md, hooks, memoria ni plugins de la máquina), solo con
Read/Glob/Grep y sin MCP: el sujeto sin skill no puede encontrarla, y ninguno puede
correr código (la trampa tiene que verse leyendo, como se ve en una planilla).

Salida: `<out>/<modelo>/<con-skill|sin-skill>/<caso>.txt` y `<out>/costos.json`. Después:
`python3 puntuar.py --run <out>`.

Uso:  python3 correr.py --out <dir> --tope-usd 5 [--modelos haiku,sonnet,opus] [--casos t1_total_general,...]
Exit: 0 terminó dentro del tope, 1 cortó por tope o por error de una llamada, 2 uso.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent / "skills" / "erp-business-analysis"

INSTRUCCION = (
    "Sos un analista. Respondé la pregunta usando solo los archivos de esta carpeta "
    "(no podés ejecutar código: leé los archivos y hacé las cuentas a mano, con cuidado). "
    "Explicá en pocas líneas cómo llegaste. La ÚLTIMA línea de tu respuesta tiene que ser "
    "exactamente `CIFRA: <número>` (sin unidades ni separador de miles), o "
    "`CIFRA: NO DETERMINABLE` si los datos no permiten responder."
)
CON_SKILL = ("Antes de responder, leé `skill/SKILL.md` y aplicá lo que corresponda "
             "(podés leer también sus `references/` y `templates/`). ")


def preparar(base: Path, con_skill: bool) -> Path:
    shutil.copytree(HERE / "datos", base / "datos")
    if con_skill:
        shutil.copytree(SKILL, base / "skill", ignore=shutil.ignore_patterns("evals", "tests", "__pycache__"))
    return base


def llamar(cwd: Path, modelo: str, prompt: str, presupuesto: float) -> tuple[str, float]:
    cmd = ["claude", "-p", prompt, "--bare", "--model", modelo, "--tools", "Read,Glob,Grep",
           "--strict-mcp-config", "--no-session-persistence", "--output-format", "json",
           "--max-budget-usd", f"{presupuesto:.2f}"]
    exe = shutil.which(cmd[0])
    if exe is None:
        raise RuntimeError("no se encontró `claude` en el PATH")
    proc = subprocess.run([exe, *cmd[1:]], cwd=cwd, capture_output=True, timeout=900)
    salida = proc.stdout.decode("utf-8", errors="replace")
    try:
        data = json.loads(salida)
    except json.JSONDecodeError:
        raise RuntimeError(f"salida no es JSON (exit {proc.returncode}): "
                           f"{proc.stderr.decode('utf-8', errors='replace')[:300]}") from None
    return str(data.get("result", "")), float(data.get("total_cost_usd", 0.0))


def main() -> int:
    ap = argparse.ArgumentParser(description="Corre el benchmark (gasta dinero).")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tope-usd", type=float, required=True)
    ap.add_argument("--modelos", default="haiku,sonnet,opus")
    ap.add_argument("--casos", default="")
    args = ap.parse_args()
    if args.tope_usd <= 0:
        print("[ERROR] --tope-usd tiene que ser > 0", file=sys.stderr)
        return 2
    casos = json.loads((HERE / "casos.json").read_text(encoding="utf-8"))
    if args.casos:
        pedidos = set(args.casos.split(","))
        casos = [c for c in casos if c["id"] in pedidos]
    modelos = [m for m in args.modelos.split(",") if m]
    tareas = [(m, c, caso) for m in modelos for c in ("con-skill", "sin-skill") for caso in casos]
    gastado, costos, cortado = 0.0, [], False
    with tempfile.TemporaryDirectory(prefix="erp-trampas-") as tmp:
        dirs = {(m, c): preparar(Path(tmp) / m / c, c == "con-skill") for m in modelos for c in ("con-skill", "sin-skill")}
        for i, (m, c, caso) in enumerate(tareas):
            restante = args.tope_usd - gastado
            presupuesto = restante / (len(tareas) - i)
            if presupuesto < 0.01:
                cortado = True
                print(f"[TOPE] {gastado:.2f} de {args.tope_usd:.2f} USD: quedan {len(tareas) - i} sin correr")
                break
            prompt = (CON_SKILL if c == "con-skill" else "") + INSTRUCCION + "\n\nPregunta: " + caso["pregunta"]
            try:
                texto, costo = llamar(dirs[(m, c)], m, prompt, presupuesto)
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                print(f"[ERROR] {m}/{c}/{caso['id']}: {exc}", file=sys.stderr)
                cortado = True
                continue
            gastado += costo
            destino = args.out / m / c / f"{caso['id']}.txt"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto + "\n", encoding="utf-8", newline="\n")
            costos.append({"modelo": m, "condicion": c, "caso": caso["id"], "usd": round(costo, 4)})
            print(f"{m}/{c}/{caso['id']}: {costo:.3f} USD (acumulado {gastado:.2f})")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "costos.json").write_text(
        json.dumps({"tope_usd": args.tope_usd, "gastado_usd": round(gastado, 4), "llamadas": costos},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return 1 if cortado else 0


if __name__ == "__main__":
    raise SystemExit(main())
