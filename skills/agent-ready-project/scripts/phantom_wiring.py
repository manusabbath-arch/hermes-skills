#!/usr/bin/env python3
"""
phantom_wiring.py — estado que se lee con un default "seguro" y nadie asigna.

El patrón: `getattr(obj, "attr", default)` donde ningún archivo del proyecto
asigna `attr` (`self.attr = ...`, `attr = ...` ni `def attr`). El default es
justo lo que oculta el bug: nada crashea, nada loguea, el caller opera sobre
estado vacío para siempre. En polymarket-trading-bot tuvo >=6 ocurrencias y una
dejó el trailing-stop sin activarse nunca en producción; NG lo portó como check
de su compuerta.

Reglas del check (las de "verde vacío"):
  - el mensaje lleva su denominador: archivos revisados y nombres asignados;
  - un .py que no parsea es ROJO (si no, encoge universo y denominador a la vez
    y el check sale verde sin haber mirado);
  - cero archivos revisados es ROJO, no "0 hallazgos".

Agnóstico y stdlib-only. Uso:
  python3 phantom_wiring.py src/ app.py
  python3 phantom_wiring.py --root . src/

Exit codes: 0 sin hallazgos, 1 hallazgos / ilegibles / nada revisado.
"""
from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXCLUDED_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    name: str


@dataclass
class Analysis:
    files: int = 0
    names: int = 0
    findings: list[Finding] = field(default_factory=list)
    unreadable: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.files > 0 and not self.findings and not self.unreadable


def python_files(targets: list[Path]) -> list[Path]:
    out: list[Path] = []
    for t in targets:
        if t.is_file() and t.suffix == ".py":
            out.append(t)
        elif t.is_dir():
            out += [
                p for p in sorted(t.rglob("*.py"))
                if not EXCLUDED_DIRS.intersection(p.parts)
            ]
    return out


def scan(tree: ast.AST) -> tuple[set[str], list[tuple[str, int]]]:
    """Un solo recorrido: (nombres asignados, getattr con default y nombre literal)."""
    assigned: set[str] = set()
    candidates: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            assigned.add(node.attr)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            assigned.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            assigned.add(node.name)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "setattr" and len(node.args) >= 2:
                arg = node.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    assigned.add(arg.value)
            elif node.func.id == "getattr" and len(node.args) == 3:
                # Sin default no es candidato: el AttributeError se ve.
                arg = node.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    candidates.append((arg.value, node.lineno))
    return assigned, candidates


def analyze(targets: list[Path], root: Path) -> Analysis:
    result = Analysis()
    universe: set[str] = set()
    per_file: dict[Path, list[tuple[str, int]]] = {}
    for path in python_files(targets):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError, OSError):
            result.unreadable.append(_rel(path, root))
            continue
        assigned, candidates = scan(tree)
        universe |= assigned
        per_file[path] = candidates
    result.files = len(per_file)
    result.names = len(universe)
    result.findings = sorted(
        (Finding(_rel(p, root), line, name)
         for p, cands in per_file.items() for name, line in cands
         if name not in universe),
        key=lambda f: (f.file, f.line),
    )
    result.unreadable.sort()
    return result


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def report(a: Analysis) -> str:
    lines = [f"PHANTOM-WIRING: {a.files} archivo(s) revisados, {a.names} nombre(s) asignados"]
    if a.files == 0 and not a.unreadable:
        lines.append("  ROJO: no se revisó ningún archivo (un check que no miró nada está apagado)")
    for u in a.unreadable:
        lines.append(f"  ROJO ilegible: {u} (sale del universo y del denominador a la vez)")
    for f in a.findings:
        lines.append(f"  ROJO {f.file}:{f.line}  getattr(..., {f.name!r}, default) y nadie asigna {f.name!r}")
    if a.findings:
        lines.append(
            "  Arreglo: pasar el valor como parámetro explícito o asignarlo donde nace; "
            "no reconectar el atributo con otro default."
        )
    if a.ok:
        lines.append("  OK: ningún getattr con default sobre un nombre que nadie asigna")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("targets", nargs="+", type=Path, help="archivos .py o directorios")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="para rutas relativas en el reporte")
    args = ap.parse_args(argv)
    a = analyze(args.targets, args.root)
    print(report(a))
    return 0 if a.ok else 1


if __name__ == "__main__":
    sys.exit(main())
