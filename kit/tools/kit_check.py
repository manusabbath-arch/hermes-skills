#!/usr/bin/env python3
"""
kit_check.py — la compuerta del proyecto: la corren el pre-commit, init.sh y el CI.

Cada guarda imprime su denominador (cuánto miró) y sale ROJO si no miró nada: un
check que aprueba sobre cero elementos está apagado, no verde.

  guardas vendorizadas  tools/guards/*.py idénticos a los sha de SOURCES.json
  phantom-wiring        getattr con default sobre nombres que nadie asigna, con
                        línea base de trinquete (.kit/baseline.json): no puede
                        subir, y cuando baja hay que bajarla (--update-baseline)
  docs verificadas      los bloques <!-- verify --> de AGENTS.md y docs/
  secretos              claves y tokens en cualquier archivo de texto; sin línea
                        base: un secreto no es deuda que se tolera
  feature_list          cada feature con id, pasos y passes; passes=true exige
                        `evidence` (comando o commit): un "anda" sin prueba no cuenta
  hook de producción    ejecuta el comando del hook PreToolUse de .claude/settings.json
                        con una escritura de prueba y exige que la bloquee (exit 2)
  worktrees             ningún commit en HEAD detached que ninguna rama alcance

Stdlib. Exit: 0 todo verde, 1 al menos un rojo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARDS = ROOT / "tools" / "guards"
sys.path.insert(0, str(GUARDS))

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
SECRET_PATTERNS = [
    ("clave de AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("clave privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("token de GitHub", re.compile(r"\b(?:ghp|gho|ghu|ghs)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{50,}")),
    ("clave de Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("token de Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("credencial en texto", re.compile(
        r"(?i)\b(?:password|passwd|contraseña|secret|api_?key|token)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]")),
]
SECRET_ALLOW = "kit-allow-secret"
PROBE_PAYLOAD = {"tool_input": {"command": "{client} -c \"DROP TABLE kit_probe\""}}


class Report:
    def __init__(self) -> None:
        self.red = False

    def line(self, ok: bool, label: str, detail: str, extra: list[str] | None = None) -> None:
        self.red |= not ok
        print(f"{'OK  ' if ok else 'ROJO'} {label}: {detail}")
        for e in extra or []:
            print(f"       {e}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_files() -> list[Path]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        out.extend(Path(dirpath) / f for f in filenames)
    return sorted(out)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


# --- guardas -----------------------------------------------------------------

def check_vendored(r: Report) -> None:
    src_path = GUARDS / "SOURCES.json"
    if not src_path.is_file():
        r.line(False, "guardas vendorizadas", "falta tools/guards/SOURCES.json")
        return
    src = load_json(src_path)
    expected = src.get("files", {})
    problems = []
    for name, digest in sorted(expected.items()):
        p = GUARDS / name
        if not p.is_file():
            problems.append(f"FALTA  {name}")
        elif sha256(p) != digest:
            problems.append(f"CAMBIÓ {name} (se arregla en el tap y se re-vendoriza, no a mano)")
    extra = sorted(p.name for p in GUARDS.glob("*.py") if p.name not in expected)
    problems += [f"SOBRA  {n} (no está en SOURCES.json)" for n in extra]
    ok = bool(expected) and not problems
    r.line(ok, "guardas vendorizadas",
           f"{len(expected)} archivo(s) contra {src.get('tap', '?')} v{src.get('tap_version', '?')}", problems)


def check_phantom(r: Report, cfg: dict, update_baseline: bool) -> None:
    import phantom_wiring  # vendorizado en tools/guards

    targets = [ROOT / p for p in cfg.get("python_paths", []) if (ROOT / p).exists()]
    a = phantom_wiring.analyze(targets, ROOT)
    base_path = ROOT / ".kit" / "baseline.json"
    baseline = load_json(base_path) if base_path.is_file() else {}
    base = int(baseline.get("phantom_wiring", 0))
    n = len(a.findings)
    detail = f"{a.files} archivo(s), {n} hallazgo(s), línea base {base}"
    extra = [f"ilegible: {u}" for u in a.unreadable]
    extra += [f"{f.file}:{f.line} getattr(..., {f.name!r}, default) y nadie asigna {f.name!r}" for f in a.findings]
    if a.files == 0:
        r.line(False, "phantom-wiring", "no se revisó ningún .py (python_paths en .kit/config.json)", extra)
    elif a.unreadable or n > base:
        r.line(False, "phantom-wiring", detail, extra)
    elif n < base:
        if update_baseline:
            baseline["phantom_wiring"] = n
            base_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
            r.line(True, "phantom-wiring", f"{detail} -> línea base bajada a {n}")
        else:
            r.line(False, "phantom-wiring", f"{detail}: mejoró, bajar la línea base a {n} "
                                            "(python tools/kit_check.py --update-baseline)")
    else:
        r.line(True, "phantom-wiring", detail, extra)


def check_docs(r: Report, cfg: dict, python: str) -> None:
    docs = [d for d in cfg.get("docs", []) if (ROOT / d).exists()]
    if not docs:
        r.line(False, "docs verificadas", "ningún doc para verificar (docs en .kit/config.json)")
        return
    p = subprocess.run([python, str(GUARDS / "doc_verify.py"), "--root", str(ROOT), "--docs", *docs],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    blocks = sum(1 for ln in lines if ln.startswith(("[OK]", "[DRIFT]", "[ROJO]", "[ERROR]")))
    if p.returncode == 0 and blocks == 0:
        r.line(False, "docs verificadas", "0 bloques verify: nadie comprueba ningún número de los docs")
        return
    r.line(p.returncode == 0, "docs verificadas", f"{blocks} bloque(s) en {', '.join(docs)}",
           [] if p.returncode == 0 else lines + p.stderr.splitlines())


def check_secrets(r: Report) -> None:
    files = 0
    hits = []
    for path in text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binario
        files += 1
        for n, line in enumerate(text.splitlines(), 1):
            if SECRET_ALLOW in line:
                continue
            for what, pat in SECRET_PATTERNS:
                if pat.search(line):
                    hits.append(f"{rel(path)}:{n}: {what}")
    if files == 0:
        r.line(False, "secretos", "no se leyó ningún archivo")
    else:
        r.line(not hits, "secretos", f"{files} archivo(s) de texto, {len(hits)} hallazgo(s)", hits)


def check_features(r: Report) -> None:
    path = ROOT / "feature_list.json"
    try:
        features = load_json(path)["features"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        r.line(False, "feature_list", f"no se pudo leer feature_list.json ({exc})")
        return
    problems, seen = [], set()
    for i, f in enumerate(features):
        fid = f.get("id") if isinstance(f, dict) else None
        if not fid:
            problems.append(f"#{i}: sin id")
            continue
        if fid in seen:
            problems.append(f"{fid}: id repetido")
        seen.add(fid)
        if not f.get("description") or not f.get("steps"):
            problems.append(f"{fid}: sin description o sin steps")
        if not isinstance(f.get("passes"), bool):
            problems.append(f"{fid}: passes tiene que ser true o false")
        elif f["passes"] and not str(f.get("evidence", "")).strip():
            problems.append(f"{fid}: passes=true sin evidence (el comando o commit que lo prueba)")
    done = sum(1 for f in features if isinstance(f, dict) and f.get("passes") is True)
    if not features:
        problems.append("ninguna feature: el arnés no tiene qué seguir")
    r.line(not problems, "feature_list", f"{done}/{len(features)} con passes=true", problems)


def check_prod_hook(r: Report) -> None:
    settings = ROOT / ".claude" / "settings.json"
    try:
        entries = load_json(settings).get("hooks", {}).get("PreToolUse", [])
    except (OSError, ValueError) as exc:
        r.line(False, "hook de producción", f"no se pudo leer .claude/settings.json ({exc})")
        return
    commands = [h.get("command", "") for e in entries for h in e.get("hooks", [])
                if "prod_write_guard.py" in h.get("command", "")]
    if not commands:
        r.line(False, "hook de producción", "prod_write_guard.py no está registrado en PreToolUse")
        return
    try:
        clients = load_json(GUARDS / "prod_write_guard.json").get("sql_clients") or []
    except (OSError, ValueError) as exc:
        r.line(False, "hook de producción", f"config ilegible: tools/guards/prod_write_guard.json ({exc})")
        return
    bash = shutil.which("bash")
    if not clients or not bash:
        r.line(False, "hook de producción", "sin sql_clients en la config o sin bash para probar el hook")
        return
    payload = json.dumps(PROBE_PAYLOAD).replace("{client}", clients[0])
    env = {**os.environ, "CLAUDE_PROJECT_DIR": ROOT.as_posix()}
    p = subprocess.run([bash, "-c", commands[0]], input=payload, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    ok = p.returncode == 2
    r.line(ok, "hook de producción",
           f"un DROP TABLE de prueba con {clients[0]} -> exit {p.returncode} (se espera 2, bloqueado)",
           [] if ok else [f"comando: {commands[0]}", *p.stderr.strip().splitlines()[-3:]])


def check_worktrees(r: Report, cfg: dict, python: str) -> None:
    has_commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "-q", "HEAD"],
                                capture_output=True).returncode == 0 if shutil.which("git") else False
    if not has_commit:
        print("INFO worktrees: NO chequeado (sin git o sin commits todavía)")
        return
    p = subprocess.run([python, str(GUARDS / "worktree_guard.py"), "--repo", str(ROOT),
                        "--base", cfg.get("base_branch", "main")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    r.line(p.returncode == 0, "worktrees", lines[0] if lines else "sin salida",
           [] if p.returncode == 0 else lines[1:] + p.stderr.splitlines())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--update-baseline", action="store_true",
                    help="bajar la línea base de phantom-wiring si mejoró (nunca la sube)")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_json(ROOT / ".kit" / "config.json")
    python = sys.executable
    r = Report()
    check_vendored(r)
    check_phantom(r, cfg, args.update_baseline)
    check_docs(r, cfg, python)
    check_secrets(r)
    check_features(r)
    check_prod_hook(r)
    check_worktrees(r, cfg, python)
    print("KIT-CHECK: " + ("ROJO" if r.red else "verde"))
    return 1 if r.red else 0


if __name__ == "__main__":
    sys.exit(main())
