"""Hermetic tests for invariant_guard. No host files, no network, no clock."""
import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parents[1] / "invariant_guard.py"

spec = importlib.util.spec_from_file_location("invariant_guard", GUARD)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def _db(tmp_path, rows):
    """Build a throwaway sqlite db with a signals table."""
    path = tmp_path / "t.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE signals (id INTEGER PRIMARY KEY, edge REAL)")
    conn.executemany("INSERT INTO signals (edge) VALUES (?)", [(r,) for r in rows])
    conn.commit()
    conn.close()
    return str(path)


def _contract(**over):
    c = {
        "etapa": "model",
        "consumidor": "signals",
        "campo": "edge",
        "check": "not_null_ratio",
        "min_ratio": 0.5,
        "null_es_defecto": True,
        "query": "SELECT COUNT(*) AS total, COUNT(edge) AS poblado FROM signals",
    }
    c.update(over)
    return {"contracts": [c]}


def test_fully_populated_is_green(tmp_path):
    code, report = guard.run_contract(_contract(), _db(tmp_path, [0.1, 0.2, 0.3]))
    assert code == 0, report
    assert any("[OK]" in line for line in report)


def test_unpopulated_field_is_red_and_fails_build(tmp_path):
    code, report = guard.run_contract(_contract(), _db(tmp_path, [None, None, None]))
    assert code == 1, report
    assert any("[ROJO]" in line for line in report)


def test_measured_zero_is_legitimate_data_not_a_defect(tmp_path):
    """NULL != 0: a field measured as 0.0 is data, never a defect."""
    code, report = guard.run_contract(_contract(), _db(tmp_path, [0.0, 0.0, 0.0]))
    assert code == 0, report


def test_empty_table_is_never_green_even_when_null_is_legitimate(tmp_path):
    """presence != utility: no post-deploy rows cannot attest anything.

    Regression: the nulo_es_0 branch returned OK before the total==0 check,
    so an empty table passed the guard.
    """
    code, report = guard.run_contract(_contract(nulo_es_0=True), _db(tmp_path, []))
    assert code != 0, report
    assert any("ROJO" in line for line in report)


def test_empty_table_is_red_on_the_default_path(tmp_path):
    code, report = guard.run_contract(_contract(), _db(tmp_path, []))
    assert code == 2, report


def test_missing_db_is_red_never_silently_green(tmp_path):
    code, report = guard.run_contract(_contract(), str(tmp_path / "nope.db"))
    assert code == 2, report


def test_no_db_at_all_is_red(tmp_path):
    code, report = guard.run_contract(_contract(), None)
    assert code == 2, report


def test_broken_query_is_red_never_swallowed(tmp_path):
    code, report = guard.run_contract(
        _contract(query="SELECT * FROM no_such_table"), _db(tmp_path, [0.1])
    )
    assert code == 2, report


def test_unknown_check_is_red(tmp_path):
    code, report = guard.run_contract(_contract(check="invented"), _db(tmp_path, [0.1]))
    assert code == 1, report


def test_guard_does_not_leak_connections(tmp_path, monkeypatch):
    """Every sqlite connection the guard opens must be closed.

    Regression: _connect_db was called twice per contract and the probe
    connection was discarded without close().
    """
    opened, closed = [], []
    real_connect = sqlite3.connect

    class Tracked:
        def __init__(self, conn):
            self._conn = conn

        def __getattr__(self, name):
            return getattr(self._conn, name)

        def close(self):
            closed.append(self)
            self._conn.close()

    def tracking_connect(*a, **kw):
        t = Tracked(real_connect(*a, **kw))
        opened.append(t)
        return t

    monkeypatch.setattr(guard.sqlite3, "connect", tracking_connect)
    guard.run_contract(_contract(), _db(tmp_path, [0.1, 0.2]))
    assert len(closed) == len(opened), f"{len(opened)} abiertas, {len(closed)} cerradas"


def test_cli_exit_code_propagates(tmp_path):
    """The build-failing contract is the CLI exit code, not the stdout text."""
    contract_path = tmp_path / "c.json"
    contract_path.write_text(json.dumps(_contract()), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(GUARD), "--contract", str(contract_path),
         "--db", _db(tmp_path, [None, None])],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_cli_invalid_contract_exits_2(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(GUARD), "--contract", str(bad)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr


def test_shipped_example_contract_is_valid_json():
    example = GUARD.parent / "contract-example.json"
    data = json.loads(example.read_text(encoding="utf-8"))
    assert data.get("contracts"), "el ejemplo debe traer al menos un contrato"
    for c in data["contracts"]:
        assert c.get("check"), c
        assert c.get("query"), c
