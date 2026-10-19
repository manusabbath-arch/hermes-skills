#!/usr/bin/env python3
"""
new_project.py — arranca un proyecto agent-ready desde el kit de este tap.

Copia `kit/` (AGENTS.md, CLAUDE.md, init.sh, pre-commit, CI, hook de producción,
feature_list, progress, plantillas de plan y decisión) y vendoriza las guardas de
`skills/agent-ready-project/scripts/` en `tools/guards/`, con el sha de cada una y la
versión del tap en `SOURCES.json`. La compuerta del proyecto nuevo marca rojo si
alguien edita una guarda a mano: el arreglo va al tap y se vuelve a copiar.

Nunca escribe sobre una carpeta que no esté vacía. Stdlib, sin red.

Uso:
  python3 scripts/new_project.py ../mi-proyecto --name mi-proyecto
  python3 scripts/new_project.py ../mi-proyecto --name mi-proyecto --python py
  cd ../mi-proyecto && bash init.sh

`--python` es el intérprete que usa el hook de Claude Code (por defecto `python3`;
en Windows suele ser `python` o `py`). init.sh lo prueba: si no existe, rojo.

Exit: 0 creado, 1 destino no vacío, 2 uso incorrecto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "kit"
GUARD_SOURCES = REPO / "skills" / "agent-ready-project" / "scripts"
GUARDS = ("phantom_wiring.py", "doc_verify.py", "worktree_guard.py", "prod_write_guard.py")
EXECUTABLES = ("init.sh", ".githooks/pre-commit")
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TAP = "manusabbath-arch/hermes-skills"


def tap_version() -> str:
    return json.loads((REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def render(text: str, values: dict[str, str], as_json: bool = False) -> str:
    # En un .json el valor va escapado: una ruta de Windows o un intérprete entre
    # comillas rompían .claude/settings.json y el hook quedaba sin registrar.
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", json.dumps(value)[1:-1] if as_json else value)
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dest", type=Path, help="carpeta del proyecto nuevo (vacía o inexistente)")
    ap.add_argument("--name", required=True, help="nombre del proyecto")
    ap.add_argument("--python", default="python3", help="intérprete del hook de Claude Code")
    args = ap.parse_args(argv)

    if not NAME.match(args.name):
        print(f"NEW-PROJECT: nombre inválido {args.name!r} (letras, dígitos, . _ -)", file=sys.stderr)
        return 2
    dest: Path = args.dest
    if dest.exists() and any(dest.iterdir()):
        print(f"NEW-PROJECT: {dest} no está vacía; no se escribe encima de nada", file=sys.stderr)
        return 1

    values = {"PROJECT": args.name, "PYTHON": args.python}
    for src in sorted(KIT.rglob("*")):
        if src.is_dir() or "__pycache__" in src.parts:
            continue
        out = dest / src.relative_to(KIT)
        out.parent.mkdir(parents=True, exist_ok=True)
        text = render(src.read_text(encoding="utf-8"), values, as_json=src.suffix == ".json")
        out.write_bytes(text.encode("utf-8"))

    guards_dir = dest / "tools" / "guards"
    files = {}
    for g in GUARDS:
        shutil.copyfile(GUARD_SOURCES / g, guards_dir / g)
        files[g] = hashlib.sha256((guards_dir / g).read_bytes()).hexdigest()
    sources = {"tap": TAP, "tap_version": tap_version(),
               "from": "skills/agent-ready-project/scripts", "files": files}
    (guards_dir / "SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")

    for rel in EXECUTABLES:
        p = dest / rel
        p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"NEW-PROJECT: {args.name} creado en {dest} (kit del tap v{sources['tap_version']})")
    print(f"  Siguiente: cd {dest} && bash init.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
