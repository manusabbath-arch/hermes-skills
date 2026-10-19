"""Hermetic tests for prod_write_guard: real payload shapes of each agent."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "prod_write_guard.py"

spec = importlib.util.spec_from_file_location("prod_write_guard", SCRIPT)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

CFG = {"sql_clients": ["db2", "psql"], "protected_paths": ["C:\\erp", "/srv/erp"]}


def _claude(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


@pytest.mark.parametrize("cmd", [
    'db2 "UPDATE erp.cliente SET credito = 0"',
    "psql -c 'delete from facturas where id = 1'",
    'db2.exe "DROP TABLE x"',
    "cd /tmp && psql -c 'TRUNCATE ventas'",
])
def test_sql_writes_are_blocked(cmd):
    assert g.decide(_claude(cmd), CFG) is not None


@pytest.mark.parametrize("cmd", [
    'db2 "SELECT * FROM erp.cliente WHERE fecha_update > current date"',
    "psql -c 'select count(*) from ventas'",
    "git commit -m 'drop the old update path'",   # sin cliente SQL: no es SQL
    "python analizar.py --update-cache",
])
def test_reads_and_unrelated_commands_pass(cmd):
    assert g.decide(_claude(cmd), CFG) is None


def test_hermes_shape_with_fields_after_command_is_still_blocked():
    # El hueco del hook en sed: `command` seguido de session_id/cwd.
    payload = {"tool_input": {"command": "cp a.dat C:\\\\erp\\\\x.dat"}, "session_id": "s1", "cwd": "/w"}
    assert "ruta protegida" in g.decide(payload, CFG)


def test_antigravity_commandline_shape():
    assert g.decide({"CommandLine": "psql -c 'ALTER TABLE t ADD c int'", "stepIdx": 3}, CFG)


@pytest.mark.parametrize("target", ["C:/ERP/datos.dat", "c:\\erp\\sub\\x.txt", "/srv/erp/a"])
def test_file_tool_targets_under_protected_path_are_blocked(target):
    assert g.decide({"tool_name": "Write", "tool_input": {"file_path": target, "content": "x"}}, CFG)


def test_file_tool_content_mentioning_path_is_not_a_write():
    payload = {"tool_input": {"file_path": "/repo/docs/nota.md", "content": "no tocar C:/erp"}}
    assert g.decide(payload, CFG) is None


def test_sibling_prefix_is_not_protected():
    assert g.decide({"tool_input": {"file_path": "/srv/erp-backup/x"}}, CFG) is None


def test_v4a_patch_targets_are_checked():
    patch = "*** Begin Patch\n*** Update File: /srv/erp/conf.ini\n@@\n-a\n+b\n*** End Patch"
    assert g.decide({"tool_input": {"patch": patch}}, CFG)


def test_reading_a_protected_path_passes():
    assert g.decide(_claude("cat /srv/erp/log.txt | grep error"), CFG) is None


def _run(stdin: bytes, cfg_path=None):
    args = [sys.executable, str(SCRIPT)]
    if cfg_path:
        args += ["--config", str(cfg_path)]
    return subprocess.run(args, input=stdin, capture_output=True)


def test_cli_blocks_with_exit_2_and_reason(tmp_path):
    cfg = tmp_path / "g.json"
    cfg.write_text(json.dumps(CFG), encoding="utf-8")
    r = _run(json.dumps(_claude('db2 "DELETE FROM t"')).encode(), cfg)
    assert r.returncode == 2 and b"PROD-GUARD" in r.stderr


def test_cli_allows_with_exit_0(tmp_path):
    r = _run(json.dumps(_claude("ls -la")).encode())
    assert r.returncode == 0


def test_cli_unreadable_input_fails_closed():
    r = _run(b"{not json")
    assert r.returncode == 2 and b"no se pudo leer" in r.stderr
