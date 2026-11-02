#!/usr/bin/env python3
"""
check_baseline.py — la compuerta que distingue una regresión de un rojo conocido.

Un repo con muchos chequeos siempre tiene alguno en rojo por motivos legítimos (un
dato que falta, un pedido a un tercero). Si la compuerta bloquea todo rojo, el equipo
la apaga; si no bloquea ninguno, el próximo defecto real entra a la lista sin que nadie
lo vea. La salida es comparar contra una línea base sellada:

  REGRESIÓN    un chequeo está peor que en la base (PASS < WARN < FAIL < ERROR).
               Un chequeo que la base no conoce cuenta como si viniera de PASS:
               el que nace rojo bloquea, salvo que se declare en el mismo commit.
  DESAPARECIDO un chequeo de la base no corrió. Un chequeo que deja de correr es
               un chequeo apagado.
  DECLARADO    rojo con motivo y condición de salida: no bloquea, se imprime.
  SIN DECLARAR rojo que ya estaba en la base pero nadie explicó: no bloquea, avisa.
  ARREGLADO    mejor que en la base; si estaba declarado, la declaración sobra.

Bloquean (exit 1): regresiones, desaparecidos, una declaración sin motivo o sin
condición de salida, y una corrida con cero chequeos (un control que no miró nada no
es un control).

Sellar (--seal) MEZCLA la corrida en la base, no la reemplaza: en el proyecto de origen
un sellado con una corrida filtrada dejó 1 entrada de 23 y convirtió los rojos
declarados de todos en regresiones. Declarar (--declare) exige motivo y condición de
salida, y rechaza declarar un chequeo que está en PASS.

Formatos:
  resultados  {"<chequeo>": "PASS" | "WARN" | "FAIL" | "ERROR", ...}
  base        {"sellado": "AAAA-MM-DD", "chequeos": {...mismo formato...},
               "declarados": {"<chequeo>": {"motivo": "...", "condicion_salida": "...",
                                            "revisado": "AAAA-MM-DD"}}}

Uso:
  python3 check_baseline.py --results r.json --baseline base.json
  python3 check_baseline.py --results r.json --baseline base.json --seal
  python3 check_baseline.py --baseline base.json --declare <chequeo> \\
          --reason "motivo" --exit-condition "qué lo cierra" --results r.json
Exit: 0 sin bloqueos, 1 bloqueo, 2 uso o archivo inválido.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

SEVERITY = {"PASS": 0, "WARN": 1, "FAIL": 2, "ERROR": 3}
RED = {"FAIL", "ERROR"}


class UsageError(Exception):
    pass


def load_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        if default is not None:
            return default
        raise UsageError(f"{path}: no existe")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        # Un archivo corrupto no es un archivo ausente: no se arranca de cero.
        raise UsageError(f"{path}: JSON inválido ({exc})") from exc
    if not isinstance(data, dict):
        raise UsageError(f"{path}: se esperaba un objeto")
    return data


def validate_results(results: dict) -> None:
    for name, verdict in results.items():
        if verdict not in SEVERITY:
            raise UsageError(f"chequeo {name!r}: veredicto desconocido {verdict!r}")


def compare(results: dict, baseline: dict) -> dict[str, list[str]]:
    base = baseline.get("chequeos", {})
    declared = baseline.get("declarados", {})
    out: dict[str, list[str]] = {k: [] for k in (
        "regresion", "desaparecido", "declaracion_incompleta", "declarado",
        "sin_declarar", "arreglado", "declaracion_sobra")}
    for name in sorted(set(base) - set(results)):
        out["desaparecido"].append(name)
    for name, now in sorted(results.items()):
        before = base.get(name, "PASS")
        d = declared.get(name)
        if d is not None and not (str(d.get("motivo", "")).strip()
                                  and str(d.get("condicion_salida", "")).strip()):
            out["declaracion_incompleta"].append(name)
        if now in RED and d is not None:
            out["declarado"].append(name)
        elif SEVERITY[now] > SEVERITY[before]:
            out["regresion"].append(f"{name}: {before} -> {now}")
        elif now in RED:
            out["sin_declarar"].append(name)
        if SEVERITY[now] < SEVERITY[before]:
            out["arreglado"].append(f"{name}: {before} -> {now}")
        if now not in RED and d is not None:
            out["declaracion_sobra"].append(name)
    return out


BLOCKING = ("regresion", "desaparecido", "declaracion_incompleta")
TITLES = {
    "regresion": "REGRESIONES contra la línea base",
    "desaparecido": "chequeos de la base que no corrieron",
    "declaracion_incompleta": "declaraciones sin motivo o sin condición de salida",
    "declarado": "rojos DECLARADOS (no bloquean)",
    "sin_declarar": "rojos conocidos SIN DECLARAR (no bloquean; declararlos o arreglarlos)",
    "arreglado": "mejoraron respecto de la base (sellar para fijarlo)",
    "declaracion_sobra": "declaraciones que sobran (el chequeo ya no está en rojo)",
}


def report(results: dict, baseline: dict) -> int:
    if not results:
        print("[ROJO] 0 chequeos en la corrida: un control que no miró nada no es un control")
        return 1
    out = compare(results, baseline)
    declared = baseline.get("declarados", {})
    blocked = any(out[k] for k in BLOCKING)
    for key, title in TITLES.items():
        if not out[key]:
            continue
        print(f"{'[ROJO]' if key in BLOCKING else '[INFO]'} {len(out[key])} {title}:")
        for item in out[key]:
            line = f"    - {item}"
            if key == "declarado":
                d = declared[item]
                line += (f" ({results[item]} hoy) — motivo al {d.get('revisado', '?')}: {d.get('motivo')}"
                         f" | sale cuando: {d.get('condicion_salida')}")
            print(line)
    reds = sum(1 for v in results.values() if v in RED)
    print(f"{'BLOQUEA' if blocked else 'OK'}: {len(results)} chequeos comparados contra "
          f"{len(baseline.get('chequeos', {}))} de la base; {reds} en rojo")
    return 1 if blocked else 0


def seal(results: dict, baseline: dict, today: str) -> dict:
    merged = dict(baseline.get("chequeos", {}))
    merged.update(results)
    return {**baseline, "sellado": today, "chequeos": merged}


def declare(baseline: dict, results: dict, name: str, reason: str, exit_condition: str,
            today: str) -> dict:
    if not reason.strip():
        raise UsageError("un rojo declarado sin motivo es un rojo silenciado: falta --reason")
    if name not in results:
        raise UsageError(f"{name!r} no está en la corrida: no se declara lo que no se midió")
    if results[name] not in RED:
        raise UsageError(f"{name!r} está en {results[name]}: solo se declara un rojo")
    declared = dict(baseline.get("declarados", {}))
    prev = declared.get(name, {})
    cond = exit_condition.strip() or str(prev.get("condicion_salida", "")).strip()
    if not cond:
        raise UsageError("falta --exit-condition: qué tiene que pasar para que deje de estar rojo")
    declared[name] = {"motivo": reason.strip(), "condicion_salida": cond, "revisado": today}
    return {**baseline, "declarados": declared}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--seal", action="store_true")
    ap.add_argument("--declare", metavar="CHEQUEO")
    ap.add_argument("--reason", default="")
    ap.add_argument("--exit-condition", default="")
    args = ap.parse_args(argv)
    today = dt.date.today().isoformat()
    try:
        results = load_json(args.results)
        validate_results(results)
        empty = {"sellado": None, "chequeos": {}, "declarados": {}}
        baseline = load_json(args.baseline, default=empty)
        if args.declare:
            new = declare(baseline, results, args.declare, args.reason, args.exit_condition, today)
            args.baseline.write_text(json.dumps(new, indent=2, ensure_ascii=False, sort_keys=True)
                                     + "\n", encoding="utf-8")
            print(f"declarado: {args.declare}")
            return 0
        if args.seal:
            if not results:
                raise UsageError("no se sella una corrida con 0 chequeos")
            new = seal(results, baseline, today)
            args.baseline.write_text(json.dumps(new, indent=2, ensure_ascii=False, sort_keys=True)
                                     + "\n", encoding="utf-8")
            print(f"sellado: {len(new['chequeos'])} chequeos en la base "
                  f"({len(results)} de esta corrida)")
            return 0
        return report(results, baseline)
    except UsageError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
