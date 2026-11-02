#!/usr/bin/env python3
"""
activacion.py — corre el paso 4 de EVALS.md §7 (activación) con `claude -p`, con tope de gasto.

  1. `scripts/activation_eval.py build --out <out> --seed <n>`: prompt.md (nombre y
     description de cada skill + pedidos barajados) y key.json, que el sujeto no ve.
  2. Por modelo, un sujeto recibe prompt.md por stdin en una carpeta vacía y devuelve el
     JSON de elecciones: <out>/answers/<modelo>.json (crudo tal cual; el puntaje extrae el
     objeto). Nada se corrige a mano.
  3. `activation_eval.py score` arma <out>/results-<modelo>.md; una respuesta incompleta
     sale en rojo y no se completa.

Uso:  python3 evals/activacion.py --out evals/runs/<fecha>/activation --tope-usd 0.6 \
          --modelos haiku,sonnet,opus --semilla 1
Exit: 0 terminó dentro del tope y todas las respuestas puntúan, 1 si no, 2 uso.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


ronda = _cargar("ronda_act", HERE / "ronda.py")
act = _cargar("activation_eval_act", REPO / "scripts" / "activation_eval.py")


def main() -> int:
    ap = argparse.ArgumentParser(description="Activación con claude -p (gasta dinero).")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tope-usd", type=float, required=True)
    ap.add_argument("--modelos", default="haiku,sonnet")
    ap.add_argument("--semilla", type=int, required=True)
    args = ap.parse_args()
    if args.tope_usd <= 0:
        print("[ERROR] --tope-usd tiene que ser > 0", file=sys.stderr)
        return 2
    act.build(args.out, args.semilla)
    prompt = (args.out / "prompt.md").read_text(encoding="utf-8")
    modelos = [m for m in args.modelos.split(",") if m]
    gastado, costos, falla = 0.0, [], False
    with tempfile.TemporaryDirectory(prefix="activacion-") as tmp:
        for i, m in enumerate(modelos):
            presupuesto = (args.tope_usd - gastado) / (len(modelos) - i)
            if presupuesto < 0.01:
                print(f"[TOPE] {gastado:.2f} de {args.tope_usd:.2f} USD: quedan {len(modelos) - i} sin correr")
                falla = True
                break
            try:
                texto, costo = ronda.llamar(Path(tmp), m, prompt, presupuesto)
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                print(f"[ERROR] {m}: {exc}", file=sys.stderr)
                falla = True
                continue
            gastado += costo
            costos.append({"modelo": m, "usd": round(costo, 4)})
            ronda.escribir(args.out / "answers" / f"{m}.json", texto)
            print(f"{m}: {costo:.3f} USD (acumulado {gastado:.2f})")
            rc = act.main(["score", "--key", str(args.out / "key.json"),
                           "--answers", str(args.out / "answers" / f"{m}.json")])
            falla |= rc != 0
    ronda.escribir(args.out / "costos.json", json.dumps(
        {"tope_usd": args.tope_usd, "gastado_usd": round(gastado, 4), "semilla": args.semilla,
         "llamadas": costos}, indent=2, ensure_ascii=False))
    return 1 if falla else 0


if __name__ == "__main__":
    raise SystemExit(main())
