#!/usr/bin/env python3
"""
doc_verify.py — fail the build when a doc asserts a number that is no longer true.

Docs may still assert numbers. The number just has to be GENERATED AND CHECKED,
not typed and trusted. Prose that depends on somebody remembering to update it
does not get updated - and the damage is not a bug, it is that the next person
(or the next agent) makes decisions from a stale map.

Block format (any markdown file):

    <!-- verify
    id: main-py-loc
    kind: loc
    target: src/main.py
    expect: 1317
    tolerance: 2%
    -->

Kinds:
  loc     lines of `target` (a file, or a directory glob like `src/**/*.py`)
  files   number of files matching `target` (glob, relative to --root)
  matches occurrences of regex `pattern` across the files in `target`
  command stdout of `command`, parsed as a number (opt-in: needs --allow-command)

`tolerance` is optional: an absolute number (`5`) or a percentage (`2%`).
Missing tolerance means exact match.

Usage:
  python3 doc_verify.py --root . --docs README.md docs/
  python3 doc_verify.py --root . --docs docs/ --update   # rewrite expect values
  echo $?   # 0 all blocks true, 1 at least one drifted, 2 malformed block

Paths are anchored to --root (default: cwd), never to the caller's cwd.
"""
from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

BLOCK_RE = re.compile(r"<!--\s*verify\n(.*?)\n\s*-->", re.S)
REQUIRED = ("id", "kind", "expect")
VALID_KINDS = ("loc", "files", "matches", "command")


class BlockError(Exception):
    """A block that cannot be evaluated. Never silently skipped."""


def parse_block(raw: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise BlockError(f"línea sin `clave: valor` -> {line!r}")
        fields[key.strip()] = value.strip()
    for key in REQUIRED:
        if key not in fields:
            raise BlockError(f"falta `{key}`")
    if fields["kind"] not in VALID_KINDS:
        raise BlockError(f"kind desconocido '{fields['kind']}' (validos: {', '.join(VALID_KINDS)})")
    return fields


def _iter_targets(root: Path, target: str) -> list[Path]:
    """Resolve a target to real files, refusing to escape --root."""
    if any(ch in target for ch in "*?["):
        paths = sorted(root.glob(target))
    else:
        paths = [root / target]
    out = []
    for p in paths:
        try:
            p.resolve().relative_to(root.resolve())
        except ValueError:
            raise BlockError(f"target fuera de --root: {target}")
        if p.is_file():
            out.append(p)
    return out


def measure(fields: dict[str, str], root: Path, allow_command: bool) -> float:
    kind = fields["kind"]

    if kind == "command":
        if not allow_command:
            raise BlockError("kind=command requiere --allow-command (ejecuta un proceso)")
        cmd = fields.get("command")
        if not cmd:
            raise BlockError("kind=command sin `command`")
        proc = subprocess.run(
            shlex.split(cmd), cwd=root, capture_output=True, text=True, timeout=60
        )
        if proc.returncode != 0:
            raise BlockError(f"command fallo (exit {proc.returncode}): {proc.stderr.strip()[:200]}")
        text = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        try:
            return float(text.split()[0])
        except (ValueError, IndexError):
            raise BlockError(f"command no devolvio un numero: {text!r}")

    target = fields.get("target")
    if not target:
        raise BlockError(f"kind={kind} sin `target`")

    if kind == "files":
        if any(ch in target for ch in "*?["):
            return float(len(sorted(root.glob(target))))
        raise BlockError("kind=files necesita un glob en `target`")

    paths = _iter_targets(root, target)
    if not paths:
        # Un target que no existe NUNCA da verde: es el drift mas grave.
        raise BlockError(f"target no existe o no matchea archivos: {target}")

    if kind == "loc":
        return float(sum(p.read_text(encoding="utf-8", errors="replace").count("\n") + 1 for p in paths))

    # kind == "matches"
    pattern = fields.get("pattern")
    if not pattern:
        raise BlockError("kind=matches sin `pattern`")
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise BlockError(f"pattern invalido: {exc}")
    return float(sum(len(rx.findall(p.read_text(encoding="utf-8", errors="replace"))) for p in paths))


def within_tolerance(actual: float, expect: float, tolerance: str | None) -> bool:
    if not tolerance:
        return actual == expect
    tolerance = tolerance.strip()
    if tolerance.endswith("%"):
        try:
            pct = float(tolerance[:-1])
        except ValueError:
            raise BlockError(f"tolerance invalida: {tolerance!r}")
        return abs(actual - expect) <= abs(expect) * pct / 100.0
    try:
        return abs(actual - expect) <= float(tolerance)
    except ValueError:
        raise BlockError(f"tolerance invalida: {tolerance!r}")


def collect_docs(root: Path, docs: list[str]) -> list[Path]:
    found: list[Path] = []
    for entry in docs:
        p = root / entry
        if p.is_dir():
            found.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            found.append(p)
    return found


def run(root: Path, docs: list[str], allow_command: bool, update: bool):
    report: list[str] = []
    drifted = 0
    malformed = 0
    checked = 0
    seen_ids: dict[str, Path] = {}

    for doc in collect_docs(root, docs):
        text = doc.read_text(encoding="utf-8")
        rewritten = text
        rel = doc.relative_to(root)

        for match in BLOCK_RE.finditer(text):
            checked += 1
            try:
                fields = parse_block(match.group(1))
            except BlockError as exc:
                report.append(f"[ERROR] {rel}: bloque malformado -> {exc}")
                malformed += 1
                continue

            bid = fields["id"]
            if bid in seen_ids:
                report.append(f"[ERROR] {rel}: id duplicado '{bid}' (ya en {seen_ids[bid]})")
                malformed += 1
                continue
            seen_ids[bid] = rel

            try:
                expect = float(fields["expect"])
                actual = measure(fields, root, allow_command)
                ok = within_tolerance(actual, expect, fields.get("tolerance"))
            except BlockError as exc:
                report.append(f"[ERROR] {rel}#{bid}: {exc}")
                malformed += 1
                continue
            except (subprocess.SubprocessError, OSError) as exc:
                report.append(f"[ERROR] {rel}#{bid}: fallo al medir -> {exc}")
                malformed += 1
                continue

            if ok:
                report.append(f"[OK] {rel}#{bid}: {actual:g} (afirma {expect:g})")
            elif update:
                rewritten = rewritten.replace(
                    match.group(0),
                    re.sub(r"(?m)^(\s*expect:).*$", rf"\1 {actual:g}", match.group(0), count=1),
                    1,
                )
                report.append(f"[UPDATE] {rel}#{bid}: {expect:g} -> {actual:g}")
            else:
                report.append(
                    f"[DRIFT] {rel}#{bid}: la doc afirma {expect:g}, el valor real es {actual:g}"
                )
                drifted += 1

        if update and rewritten != text:
            doc.write_text(rewritten, encoding="utf-8")

    if malformed:
        exit_code = 2
        head = f"DOC-VERIFY: {checked} bloque(s), {drifted} drift, {malformed} malformado(s)"
    elif drifted:
        exit_code = 1
        head = f"DOC-VERIFY: {checked} bloque(s), {drifted} drift -> la doc miente"
    else:
        exit_code = 0
        head = f"DOC-VERIFY: {checked} bloque(s), todos verdes"

    return exit_code, [head] + report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica bloques <!-- verify --> en markdown")
    parser.add_argument("--root", default=".", help="raiz del proyecto (default: cwd)")
    parser.add_argument("--docs", nargs="+", required=True, help="archivos o directorios .md")
    parser.add_argument("--allow-command", action="store_true", help="habilita kind=command")
    parser.add_argument("--update", action="store_true", help="reescribe los expect en vez de fallar")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"DOC-VERIFY: --root no es un directorio: {root}", file=sys.stderr)
        return 2

    # En modo --update un drift se reescribe y nunca se cuenta como drift,
    # asi que el exit code de run() ya es el correcto en ambos modos.
    exit_code, report = run(root, args.docs, args.allow_command, args.update)
    for line in report:
        print(line)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
