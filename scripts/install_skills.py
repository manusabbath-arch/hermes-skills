#!/usr/bin/env python3
"""
install_skills.py — copia las skills del tap a la carpeta de skills de un agente.

Para Claude Code está el plugin (ver README). Este script es para el resto:
Codex y Cursor leen `~/.agents/skills/`; Cursor también `~/.cursor/skills/`; Hermes
`~/.hermes/skills/`. Copia en vez de enlazar porque un symlink en Windows pide
permisos de administrador, y una copia se puede verificar.

Después de copiar, verifica cada archivo contra los SHA256 del árbol de origen (la
misma lógica que `release_manifest.py`): una instalación que no se verificó no se
da por instalada. Nunca pisa una skill que ya existe sin `--force`, y no toca las
skills ajenas que haya en el destino. Stdlib, sin red.

Uso:
  python3 scripts/install_skills.py --target agents          # Codex, Cursor, Amp
  python3 scripts/install_skills.py --target cursor --skill erp-business-analysis
  python3 scripts/install_skills.py --dest ./.agents/skills  # skills del proyecto
  python3 scripts/install_skills.py --target agents --force  # actualizar

Exit: 0 instalado y verificado, 1 conflicto o verificación fallida, 2 uso incorrecto.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from release_manifest import EXCLUDED_PARTS, EXCLUDED_SUFFIXES, compare, sha256

REPO = Path(__file__).resolve().parent.parent
TARGETS = {
    "agents": (".agents", "skills"),
    "cursor": (".cursor", "skills"),
    "claude": (".claude", "skills"),
    "hermes": (".hermes", "skills"),
}


def resolve_dest(target: str, home: Path | None = None) -> Path:
    return (home or Path.home()).joinpath(*TARGETS[target])


def available_skills() -> list[str]:
    return sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))


def _tree(base: Path, names: list[str]) -> dict[str, str]:
    """`<skill>/<ruta>` -> sha256 of every published file of `names` under `base`."""
    out = {}
    for n in names:
        for p in sorted((base / n).rglob("*")):
            rel = p.relative_to(base)
            if p.is_file() and not EXCLUDED_PARTS.intersection(rel.parts) and p.suffix not in EXCLUDED_SUFFIXES:
                out[rel.as_posix()] = sha256(p)
    return out


def verify(dest: Path, names: list[str]) -> list[str]:
    """Compare the installed copy of `names` under `dest` with the source tree."""
    return compare(_tree(REPO / "skills", names), _tree(dest, names))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    where = ap.add_mutually_exclusive_group(required=True)
    where.add_argument("--target", choices=sorted(TARGETS), help="carpeta de skills del agente, en el home")
    where.add_argument("--dest", type=Path, help="carpeta de skills explícita (por ejemplo la del proyecto)")
    ap.add_argument("--skill", action="append", help="instalar solo esta skill (repetible)")
    ap.add_argument("--force", action="store_true", help="reemplazar las skills que ya existan en el destino")
    args = ap.parse_args(argv)

    known = available_skills()
    names = sorted(set(args.skill)) if args.skill else known
    unknown = [n for n in names if n not in known]
    if unknown:
        print(f"INSTALL-SKILLS: no existe(n) {', '.join(unknown)}; disponibles: {', '.join(known)}", file=sys.stderr)
        return 2

    dest = args.dest if args.dest else resolve_dest(args.target)
    existing = [n for n in names if (dest / n).exists()]
    if existing and not args.force:
        print(f"INSTALL-SKILLS: ya existe(n) en {dest}: {', '.join(existing)} (usar --force para reemplazar)", file=sys.stderr)
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns(*EXCLUDED_PARTS, *(f"*{s}" for s in EXCLUDED_SUFFIXES))
    for n in names:
        if (dest / n).exists():
            shutil.rmtree(dest / n)
        shutil.copytree(REPO / "skills" / n, dest / n, ignore=ignore)

    errors = verify(dest, names)
    if errors:
        print(f"INSTALL-SKILLS: la copia en {dest} NO verifica:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"INSTALL-SKILLS: {len(names)} skill(s) en {dest}, verificadas contra el origen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
