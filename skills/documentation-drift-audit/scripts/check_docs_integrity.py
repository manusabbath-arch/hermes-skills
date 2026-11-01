#!/usr/bin/env python3
"""Mechanical integrity check for a documentation tree / markdown vault.

Two checks, both machine-verifiable, both invisible to a casual read:

  1. Broken wikilinks  -- a [[Note]] whose target note does not exist. Almost always
     caused by a note being renamed or deleted after the link was written.
  2. Orphan documents  -- a note under an indexed directory that no index file links
     to, so a reader who lands on the entry point never discovers it exists.

This is the gate to run at the START of a documentation pass (to find what to fix)
and again at the END (to prove the pass broke nothing). It exits non-zero when
either check finds something.

Usage
-----
    python check_docs_integrity.py <vault-root>
    python check_docs_integrity.py <vault-root> --entry README.md
    python check_docs_integrity.py <vault-root> --strict

The root defaults to the current directory. The entry file defaults to the only
top-level .md file that is not a README, LICENSE or CHANGELOG; pass --entry when
that guess is wrong.

By default the orphan check scans the conventional document directories (any
top-level directory that contains .md files). Pass --dirs a,b to scan only those.

No third-party dependencies: stdlib only, so it runs under a bare interpreter.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Directories never treated as documentation: tooling, VCS, caches.
SKIP_DIRS = {
    ".git",
    ".obsidian",
    ".hermes",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}

# A wikilink: [[Note]] or [[Note|alias]] or [[Note#heading]].
WIKILINK = re.compile(r"\[\[([^\]|#]+)")

# Files that are plumbing, not documentation, when guessing the entry point.
NON_ENTRY = {"readme", "license", "licence", "changelog", "contributing"}


def iter_notes(root: Path):
    """Yield every .md path under root, skipping tooling directories."""
    for p in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def guess_entry(root: Path, notes: list[Path]) -> Path | None:
    """The single top-level note that is not plumbing."""
    top = [p for p in notes if p.parent == root and p.stem.lower() not in NON_ENTRY]
    if len(top) == 1:
        return top[0]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Check a docs tree for broken links and orphans")
    ap.add_argument("root", nargs="?", default=".", help="vault / docs root")
    ap.add_argument("--entry", help="entry-point note, relative to root")
    ap.add_argument("--dirs", help="comma-separated dirs to scan for orphans")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="also fail when no entry point could be determined",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    notes = list(iter_notes(root))
    if not notes:
        print(f"no markdown notes found under {root}")
        return 2

    # --- note names, for link resolution -------------------------------------
    # Obsidian resolves [[Note]] by basename regardless of folder, so the lookup
    # key is the stem. Two notes sharing a stem is itself worth reporting.
    by_stem: dict[str, list[Path]] = {}
    for p in notes:
        by_stem.setdefault(p.stem, []).append(p)

    # --- check 1: broken wikilinks -------------------------------------------
    rotos: dict[str, set[str]] = {}
    for p in notes:
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in WIKILINK.finditer(text):
            target = m.group(1).strip()
            if target and target not in by_stem:
                rotos.setdefault(target, set()).add(str(p.relative_to(root)))

    print(f"Notes scanned: {len(notes)}")
    print()
    print(f"BROKEN WIKILINKS: {len(rotos)}")
    for target in sorted(rotos):
        where = sorted(rotos[target])[:3]
        extra = "" if len(rotos[target]) <= 3 else f" (+{len(rotos[target]) - 3} more)"
        print(f"  [[{target}]]  <-  {', '.join(where)}{extra}")

    # --- entry point ---------------------------------------------------------
    entry = None
    if args.entry:
        candidate = root / args.entry
        if candidate.is_file():
            entry = candidate
        else:
            print(f"\nentry not found: {candidate}")
    else:
        entry = guess_entry(root, notes)

    print()
    if entry is None:
        print("ENTRY POINT: could not be determined -- pass --entry")
    else:
        print(f"ENTRY POINT: {entry.relative_to(root)}")

    # --- check 2: orphan documents -------------------------------------------
    if entry is None:
        print("\nORPHANS: skipped (no entry point)")
        orphans: list[str] = []
    else:
        entry_text = entry.read_text(encoding="utf-8", errors="replace")
        linked = {m.group(1).strip() for m in WIKILINK.finditer(entry_text)}

        if args.dirs:
            wanted = {d.strip() for d in args.dirs.split(",") if d.strip()}
            subdirs = [root / d for d in sorted(wanted)]
        else:
            # any top-level dir holding at least one note
            subdirs = sorted(
                {p.parent for p in notes if p.parent != root and p.parent.parent == root}
            )

        orphans = []
        for d in subdirs:
            for p in sorted(d.glob("*.md")):
                if p.stem not in linked:
                    orphans.append(str(p.relative_to(root)))

        print(f"ORPHAN DOCUMENTS (not linked from the entry point): {len(orphans)}")
        for o in orphans:
            print(f"  {o}")

    print()
    ok = not rotos and not orphans and (entry is not None or not args.strict)
    print("OK" if ok else "NOT OK -- fix the items above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
