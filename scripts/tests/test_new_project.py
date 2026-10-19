"""The starter kit: a generated project is green, and every guard it ships turns red when broken.

Criterio 4.1 del plan: generar + `init.sh` deja el proyecto en verde.
Criterio 4.2: cada guarda tiene su mutación; un kit con un check que no puede
fallar es justo lo que el kit dice que no hay que tener.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("new_project", SCRIPTS / "new_project.py")
np_ = importlib.util.module_from_spec(spec)
spec.loader.exec_module(np_)


PY = Path(sys.executable).as_posix()
ENV = {**os.environ, "PYTHON": PY}


def _check(proj: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/kit_check.py", *args],
        cwd=proj, capture_output=True, text=True, encoding="utf-8",
    )


@pytest.fixture
def proj(tmp_path):
    dest = tmp_path / "demo"
    assert np_.main([str(dest), "--name", "demo", "--python", f'"{PY}"']) == 0
    return dest


# --- 4.1: lo generado arranca en verde ---------------------------------------

def test_generated_project_is_green(proj):
    r = _check(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    for label in ("guardas vendorizadas", "phantom-wiring", "docs verificadas", "secretos",
                  "feature_list", "hook de producción"):
        assert label in r.stdout, label


def test_name_is_substituted_and_no_placeholder_survives(proj):
    assert "# demo" in (proj / "AGENTS.md").read_text(encoding="utf-8")
    leftovers = [p for p in proj.rglob("*") if p.is_file() and "{{" in p.read_text(encoding="utf-8", errors="ignore")]
    assert leftovers == []


def test_claude_md_points_to_agents_md(proj):
    assert "@AGENTS.md" in (proj / "CLAUDE.md").read_text(encoding="utf-8")


def test_agents_md_is_a_short_map(proj):
    assert len((proj / "AGENTS.md").read_text(encoding="utf-8").splitlines()) <= 120


def test_every_feature_starts_failing(proj):
    features = json.loads((proj / "feature_list.json").read_text(encoding="utf-8"))["features"]
    assert features and all(f["passes"] is False for f in features)


@pytest.mark.skipif(shutil.which("bash") is None or shutil.which("git") is None, reason="init.sh needs bash and git")
def test_init_sh_sets_hooks_and_ends_green(proj):
    r = subprocess.run(["bash", "init.sh"], cwd=proj, capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert r.returncode == 0, r.stdout + r.stderr
    hooks = subprocess.run(["git", "config", "core.hooksPath"], cwd=proj, capture_output=True, text=True)
    assert hooks.stdout.strip() == ".githooks"


def test_refuses_a_non_empty_destination(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "algo.txt").write_text("mío", encoding="utf-8")
    assert np_.main([str(tmp_path / "x"), "--name", "x"]) == 1
    assert (tmp_path / "x" / "algo.txt").read_text(encoding="utf-8") == "mío"


def test_sources_record_tap_version_and_sha(proj):
    src = json.loads((proj / "tools" / "guards" / "SOURCES.json").read_text(encoding="utf-8"))
    plugin = json.loads((SCRIPTS.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert src["tap_version"] == plugin["version"]
    assert set(src["files"]) == {"phantom_wiring.py", "doc_verify.py", "worktree_guard.py", "prod_write_guard.py"}


# --- 4.2: cada guarda, rota a propósito, da rojo -----------------------------

def _red(proj, label):
    r = _check(proj)
    assert r.returncode == 1, r.stdout
    assert label in r.stdout, r.stdout


def test_mutation_phantom_wiring(proj):
    (proj / "src" / "demo_app.py").write_text(
        "def f(o):\n    return getattr(o, 'nadie_lo_asigna', 0)\n", encoding="utf-8")
    _red(proj, "ROJO phantom-wiring")


@pytest.mark.skipif(shutil.which("bash") is None or shutil.which("git") is None, reason="needs bash and git")
def test_pre_commit_blocks_a_red_commit(proj):
    assert subprocess.run(["bash", "init.sh"], cwd=proj, capture_output=True, env=ENV).returncode == 0
    (proj / "src" / "demo_app.py").write_text(
        "def f(o):\n    return getattr(o, 'nadie_lo_asigna', 0)\n", encoding="utf-8")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "-A"], cwd=proj, check=True, capture_output=True)
    r = subprocess.run([*git, "commit", "-qm", "rojo"], cwd=proj, capture_output=True, text=True, env=ENV)
    assert r.returncode != 0, "el pre-commit dejó pasar un commit con una guarda en rojo"
    assert "phantom-wiring" in r.stdout + r.stderr


def test_mutation_phantom_scans_nothing(proj):
    for p in list((proj / "src").glob("*.py")) + list((proj / "tests").glob("*.py")):
        p.unlink()
    cfg = json.loads((proj / ".kit" / "config.json").read_text(encoding="utf-8"))
    cfg["python_paths"] = ["src"]
    (proj / ".kit" / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    _red(proj, "ROJO phantom-wiring")


def test_mutation_secret(proj):
    key = "AKIA" + "Q" * 16
    (proj / "src" / "settings.py").write_text(f"AWS = '{key}'\n", encoding="utf-8")
    _red(proj, "ROJO secretos")


def test_mutation_doc_number_drifts(proj):
    (proj / "tools" / "guards" / "extra.py").write_text("X = 1\n", encoding="utf-8")
    _red(proj, "ROJO docs verificadas")


def test_mutation_vendored_guard_edited(proj):
    g = proj / "tools" / "guards" / "phantom_wiring.py"
    g.write_text(g.read_text(encoding="utf-8") + "\n# retocado a mano\n", encoding="utf-8")
    _red(proj, "ROJO guardas vendorizadas")


def test_mutation_feature_passes_without_evidence(proj):
    fl = proj / "feature_list.json"
    data = json.loads(fl.read_text(encoding="utf-8"))
    data["features"][0]["passes"] = True
    fl.write_text(json.dumps(data), encoding="utf-8")
    _red(proj, "ROJO feature_list")


def test_feature_passes_with_evidence_is_green(proj):
    fl = proj / "feature_list.json"
    data = json.loads(fl.read_text(encoding="utf-8"))
    data["features"][0]["passes"] = True
    data["features"][0]["evidence"] = "python -m unittest tests.test_smoke  (commit abc1234)"
    fl.write_text(json.dumps(data), encoding="utf-8")
    assert _check(proj).returncode == 0


def test_mutation_empty_feature_list(proj):
    (proj / "feature_list.json").write_text(json.dumps({"features": []}), encoding="utf-8")
    _red(proj, "ROJO feature_list")


def test_mutation_prod_hook_unwired(proj):
    s = proj / ".claude" / "settings.json"
    s.write_text(json.dumps({"hooks": {}}), encoding="utf-8")
    _red(proj, "ROJO hook de producción")


def test_mutation_baseline_not_ratcheted_down(proj):
    cfg_path = proj / ".kit" / "baseline.json"
    cfg_path.write_text(json.dumps({"phantom_wiring": 3}), encoding="utf-8")
    _red(proj, "bajar la línea base")
    assert _check(proj, "--update-baseline").returncode == 0
    assert json.loads(cfg_path.read_text(encoding="utf-8"))["phantom_wiring"] == 0


def test_baseline_tolerates_known_debt_but_not_more(proj):
    (proj / "src" / "legacy.py").write_text(
        "def f(o):\n    return getattr(o, 'deuda_vieja', 0)\n", encoding="utf-8")
    (proj / ".kit" / "baseline.json").write_text(json.dumps({"phantom_wiring": 1}), encoding="utf-8")
    assert _check(proj).returncode == 0
    (proj / "src" / "nuevo.py").write_text(
        "def g(o):\n    return getattr(o, 'deuda_nueva', 0)\n", encoding="utf-8")
    _red(proj, "ROJO phantom-wiring")


def test_hook_with_a_missing_interpreter_is_red(tmp_path):
    # El caso de Windows: `python3` no existe y Claude Code toma el error del hook
    # como no bloqueante. La guarda quedaría apagada sin avisar.
    dest = tmp_path / "demo"
    assert np_.main([str(dest), "--name", "demo", "--python", "no-existe-este-python"]) == 0
    r = _check(dest)
    assert r.returncode == 1 and "ROJO hook de producción" in r.stdout


@pytest.mark.skipif(shutil.which("bash") is None or shutil.which("git") is None, reason="needs bash and git")
def test_worktree_guard_runs_once_there_are_commits(proj):
    assert subprocess.run(["bash", "init.sh"], cwd=proj, capture_output=True, env=ENV).returncode == 0
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "-A"], cwd=proj, check=True, capture_output=True)
    subprocess.run([*git, "commit", "-qm", "inicio"], cwd=proj, check=True, capture_output=True, env=ENV)
    r = _check(proj)
    assert r.returncode == 0, r.stdout
    assert "OK   worktrees" in r.stdout and "NO chequeado" not in r.stdout


@pytest.mark.skipif(shutil.which("bash") is None or shutil.which("git") is None, reason="needs bash and git")
def test_vendored_sha_survives_a_windows_checkout(proj):
    # Un compañero clona en Windows con autocrlf: las guardas no pueden volver en CRLF,
    # o su sha deja de coincidir con SOURCES.json y la compuerta da rojo en su máquina.
    assert subprocess.run(["bash", "init.sh"], cwd=proj, capture_output=True, env=ENV).returncode == 0
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=true"]
    subprocess.run([*git, "add", "-A"], cwd=proj, check=True, capture_output=True)
    subprocess.run([*git, "commit", "-qm", "inicio"], cwd=proj, check=True, capture_output=True, env=ENV)
    subprocess.run([*git, "rm", "-q", "-r", "--cached", "."], cwd=proj, check=True, capture_output=True)
    for p in (proj / "tools" / "guards").glob("*.py"):
        p.unlink()
    subprocess.run([*git, "reset", "-q", "--hard"], cwd=proj, check=True, capture_output=True)
    r = _check(proj)
    assert r.returncode == 0, r.stdout
