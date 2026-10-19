"""Hermetic tests for worktree_guard: throwaway git repos under tmp_path."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "worktree_guard.py"

spec = importlib.util.spec_from_file_location("worktree_guard", SCRIPT)
wg = importlib.util.module_from_spec(spec)
sys.modules["worktree_guard"] = wg
spec.loader.exec_module(wg)

ENV = {**wg.isolated_env(), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def sh(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                          text=True, env=ENV).stdout


def commit(cwd, name):
    (Path(cwd) / name).write_text(name, encoding="utf-8")
    sh(cwd, "add", name)
    sh(cwd, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", name)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    r = tmp_path / "repo"
    r.mkdir()
    sh(r, "init", "-q", "-b", "main")
    commit(r, "a.txt")
    return r


def verdicts(repo, base="main"):
    return {Path(v.worktree.path).name: v for v in
            (wg.classify(repo, wt, base) for wt in wg.list_worktrees(repo))}


def test_detached_with_unreachable_commit_is_red(repo, tmp_path):
    sh(repo, "worktree", "add", "-q", "--detach", str(tmp_path / "wt"))
    commit(tmp_path / "wt", "lost.txt")
    v = verdicts(repo)["wt"]
    assert v.level == "ROJO" and "1 commit" in v.detail


def test_detached_contained_in_a_branch_is_info(repo, tmp_path):
    sh(repo, "worktree", "add", "-q", "--detach", str(tmp_path / "wt"))
    assert verdicts(repo)["wt"].level == "INFO"


def test_switch_c_rescues_the_commit(repo, tmp_path):
    sh(repo, "worktree", "add", "-q", "--detach", str(tmp_path / "wt"))
    commit(tmp_path / "wt", "kept.txt")
    sh(tmp_path / "wt", "switch", "-q", "-c", "claude/tema")
    assert verdicts(repo)["wt"].level == "OK"


def test_merged_branch_worktree_is_info(repo, tmp_path):
    sh(repo, "worktree", "add", "-q", "-b", "claude/hecho", str(tmp_path / "wt"))
    assert "ya integrada" in verdicts(repo)["wt"].detail


def test_branch_with_new_work_is_ok(repo, tmp_path):
    sh(repo, "worktree", "add", "-q", "-b", "claude/vivo", str(tmp_path / "wt"))
    commit(tmp_path / "wt", "b.txt")
    assert verdicts(repo)["wt"].level == "OK"


def test_cli_exit_codes(repo, tmp_path):
    run = lambda: subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo)],
                                 capture_output=True, text=True, env=ENV)
    r = run()
    assert r.returncode == 0 and "1 worktree(s) revisados" in r.stdout
    sh(repo, "worktree", "add", "-q", "--detach", str(tmp_path / "wt"))
    commit(tmp_path / "wt", "lost.txt")
    r = run()
    assert r.returncode == 1 and "ROJO" in r.stdout


def test_cli_outside_a_repo_is_red(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(tmp_path / "nope")],
                       capture_output=True, text=True, env=ENV)
    assert r.returncode == 1


def test_inherited_index_file_does_not_leak(repo, monkeypatch):
    # El incidente de NG: GIT_INDEX_FILE heredado de un `git commit -- <paths>`.
    monkeypatch.setenv("GIT_INDEX_FILE", "/nonexistent/index")
    assert "GIT_INDEX_FILE" not in wg.isolated_env()
    assert len(wg.list_worktrees(repo)) == 1
