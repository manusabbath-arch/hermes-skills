#!/usr/bin/env python3
"""
release_manifest.py — checksums de lo que el tap publica, para verificar lo instalado.

Una skill es código que un agente ejecuta y obedece. Quien la instala tiene que
poder comprobar que recibió exactamente lo publicado en un tag, y no una copia
alterada en el camino o en un mirror. Este script:

  - genera un manifiesto SHA256SUMS (formato `sha256sum`) de cada archivo bajo
    skills/ y kit/, ordenado y con rutas POSIX, para adjuntar al release;
  - verifica un árbol contra ese manifiesto: falla si un archivo cambió, falta,
    o sobra (un archivo agregado que nadie publicó es justo lo que hay que ver).

Excluye artefactos que no se publican (`__pycache__`, `.pyc`). Stdlib, sin red.

Uso:
  python3 scripts/release_manifest.py > SHA256SUMS
  python3 scripts/release_manifest.py --root <copia-instalada> --check SHA256SUMS
  python3 scripts/release_manifest.py --root <copia> --check SHA256SUMS --only skills  # sin kit/

Exit: 0 manifiesto emitido o árbol idéntico, 1 diferencias, 2 uso incorrecto.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc"}


PUBLISHED_ROOTS = ("skills", "kit")


def published_files(root: Path, only: tuple[str, ...] = PUBLISHED_ROOTS) -> list[Path]:
    return sorted(
        p for base in only for p in (root / base).rglob("*")
        if p.is_file()
        and not EXCLUDED_PARTS.intersection(p.relative_to(root).parts)
        and p.suffix not in EXCLUDED_SUFFIXES
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(root: Path, only: tuple[str, ...] = PUBLISHED_ROOTS) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha256(p) for p in published_files(root, only)}


def render(entries: dict[str, str]) -> str:
    return "".join(f"{digest}  {path}\n" for path, digest in sorted(entries.items()))


def parse(text: str) -> dict[str, str]:
    out = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        digest, sep, path = line.partition("  ")
        if not sep or len(digest) != 64:
            raise ValueError(f"línea {n} del manifiesto mal formada: {line!r}")
        out[path] = digest
    return out


def compare(expected: dict[str, str], actual: dict[str, str]) -> list[str]:
    problems = []
    for path in sorted(expected.keys() - actual.keys()):
        problems.append(f"FALTA     {path}")
    for path in sorted(actual.keys() - expected.keys()):
        problems.append(f"SOBRA     {path} (no está en el manifiesto publicado)")
    for path in sorted(expected.keys() & actual.keys()):
        if expected[path] != actual[path]:
            problems.append(f"CAMBIÓ    {path}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=REPO, help="raíz que contiene skills/ y kit/")
    ap.add_argument("--check", type=Path, help="manifiesto SHA256SUMS contra el cual verificar")
    ap.add_argument("--only", choices=PUBLISHED_ROOTS, action="append",
                    help="verificar solo esta parte (una instalación de skills no trae kit/)")
    args = ap.parse_args(argv)
    only = tuple(args.only) if args.only else PUBLISHED_ROOTS

    actual = manifest(args.root, only)
    if not actual:
        print(f"RELEASE-MANIFEST: ROJO, no hay archivos bajo {', '.join(only)} en {args.root}", file=sys.stderr)
        return 1
    if args.check is None:
        sys.stdout.write(render(actual))
        return 0
    try:
        expected = {k: v for k, v in parse(args.check.read_text(encoding="utf-8")).items()
                    if k.split("/", 1)[0] in only}
    except (OSError, ValueError) as exc:
        print(f"RELEASE-MANIFEST: ROJO, no se pudo leer el manifiesto ({exc})", file=sys.stderr)
        return 1
    problems = compare(expected, actual)
    print(f"RELEASE-MANIFEST: {len(actual)} archivo(s) verificados contra {len(expected)} publicados")
    for p in problems:
        print(f"  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
