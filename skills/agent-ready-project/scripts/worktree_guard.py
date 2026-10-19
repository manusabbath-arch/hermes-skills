#!/usr/bin/env python3
"""
worktree_guard.py — el commit que no quedó en ninguna rama.

Algunas herramientas de agentes crean su propio worktree en HEAD detached. Ahí
un commit sale con exit 0 y no queda en ninguna rama: se pierde al desmontar el
worktree (salvo reflog) y `git status` se ve normal. En NG, una sesión trabajó
así días enteros sin que nada lo notara.

Clasifica cada worktree del repo:
  ROJO  detached con commits que ninguna rama (local ni remota) alcanza — lo
        único irreversible;
  INFO  detached contenido en una rama (`git worktree add --detach` para
        inspeccionar es legítimo);
  INFO  rama ya integrada en la base (--base) y worktree sin limpiar;
  OK    el resto.

El reporte lleva su denominador (worktrees revisados) y sale ROJO si no pudo
listar ninguno: un check que no miró nada está apagado.

Uso:  python3 worktree_guard.py [--repo .] [--base main]
Exit: 0 sin rojos, 1 al menos un rojo o git no respondió.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# `git commit -- <paths>` exporta estas variables a los hooks y a sus
# subprocesos; heredadas, un git sobre OTRO repo lee el índice/identidad ajenos.
INHERITED_GIT_ENV = (
    "GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_PREFIX",
    "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
    "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE",
)


def isolated_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k not in INHERITED_GIT_ENV}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True, env=isolated_env(),
    ).stdout


@dataclass(frozen=True)
class Worktree:
    path: str
    head: str
    branch: str | None  # None = detached


@dataclass(frozen=True)
class Verdict:
    level: str  # ROJO | INFO | OK
    worktree: Worktree
    detail: str


def list_worktrees(repo: Path) -> list[Worktree]:
    out, cur = [], {}
    for line in git(repo, "worktree", "list", "--porcelain").splitlines() + [""]:
        if not line:
            if cur.get("worktree") and cur.get("HEAD"):
                branch = cur.get("branch")
                out.append(Worktree(cur["worktree"], cur["HEAD"],
                                    branch.removeprefix("refs/heads/") if branch else None))
            cur = {}
            continue
        key, _, value = line.partition(" ")
        cur[key] = value
    return out


def unreachable_commits(repo: Path, head: str) -> int:
    """Commits de HEAD que ninguna rama (local o remota) contiene."""
    return int(git(repo, "rev-list", "--count", head, "--not", "--branches", "--remotes").strip())


def classify(repo: Path, wt: Worktree, base: str | None) -> Verdict:
    if wt.branch is None:
        n = unreachable_commits(repo, wt.head)
        if n:
            return Verdict("ROJO", wt, f"detached con {n} commit(s) que ninguna rama alcanza: "
                                       f"`git -C {wt.path} switch -c <agente>/<tema>`")
        return Verdict("INFO", wt, "detached contenido en una rama (inspección)")
    if base and wt.branch != base:
        merged = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", wt.head, base],
            capture_output=True, env=isolated_env(),
        ).returncode == 0
        if merged:
            return Verdict("INFO", wt, f"rama {wt.branch!r} ya integrada en {base!r}: "
                                       "`git worktree remove` + `git branch -d`")
    return Verdict("OK", wt, f"rama {wt.branch!r}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--base", default="main", help="rama de integración ('' para no mirar)")
    args = ap.parse_args(argv)
    try:
        worktrees = list_worktrees(args.repo)
        verdicts = [classify(args.repo, wt, args.base or None) for wt in worktrees]
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"WORKTREE-GUARD: ROJO, git no respondió ({exc})", file=sys.stderr)
        return 1
    print(f"WORKTREE-GUARD: {len(verdicts)} worktree(s) revisados")
    if not verdicts:
        print("  ROJO: no se listó ningún worktree (un check que no miró nada está apagado)")
        return 1
    for v in verdicts:
        print(f"  {v.level:<4} {v.worktree.path}: {v.detail}")
    return 1 if any(v.level == "ROJO" for v in verdicts) else 0


if __name__ == "__main__":
    sys.exit(main())
