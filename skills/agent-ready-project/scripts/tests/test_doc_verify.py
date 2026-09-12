"""Hermetic tests for doc_verify. No host files, no network, no clock."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "doc_verify.py"
spec = importlib.util.spec_from_file_location("doc_verify", SCRIPT)
dv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dv)


def block(**fields):
    body = "\n".join(f"{k}: {v}" for k, v in fields.items())
    return f"<!-- verify\n{body}\n-->\n"


def project(tmp_path, doc_text, code_lines=10):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("x = 1\n" * code_lines, encoding="utf-8")
    (tmp_path / "README.md").write_text(doc_text, encoding="utf-8")
    return tmp_path


def test_accurate_number_is_green(tmp_path):
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py", expect=11))
    code, report = dv.run(root, ["README.md"], False, False)
    assert code == 0, report


def test_stale_number_fails_the_build(tmp_path):
    """The doc says 4541, the file is 11. Nobody lied - the doc was not touched."""
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py", expect=4541))
    code, report = dv.run(root, ["README.md"], False, False)
    assert code == 1, report
    assert any("DRIFT" in line for line in report)


def test_tolerance_percent_absorbs_small_moves(tmp_path):
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py",
                                   expect=10, tolerance="20%"))
    assert dv.run(root, ["README.md"], False, False)[0] == 0


def test_tolerance_percent_still_catches_a_real_drift(tmp_path):
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py",
                                   expect=10, tolerance="2%"))
    assert dv.run(root, ["README.md"], False, False)[0] == 1


def test_absolute_tolerance(tmp_path):
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py",
                                   expect=9, tolerance="2"))
    assert dv.run(root, ["README.md"], False, False)[0] == 0


def test_missing_target_is_never_green(tmp_path):
    """A target that vanished is the worst drift: the map lost its territory."""
    root = project(tmp_path, block(id="loc", kind="loc", target="src/gone.py", expect=11))
    code, report = dv.run(root, ["README.md"], False, False)
    assert code == 2, report
    assert any("no existe" in line for line in report)


def test_target_cannot_escape_root(tmp_path):
    root = project(tmp_path, block(id="esc", kind="loc", target="../secrets.txt", expect=1))
    (tmp_path.parent / "secrets.txt").write_text("token\n", encoding="utf-8")
    code, report = dv.run(root, ["README.md"], False, False)
    assert code == 2, report


def test_malformed_block_is_an_error_not_a_skip(tmp_path):
    root = project(tmp_path, "<!-- verify\nthis is not a field\n-->\n")
    code, report = dv.run(root, ["README.md"], False, False)
    assert code == 2, report


def test_unknown_kind_is_an_error(tmp_path):
    root = project(tmp_path, block(id="x", kind="vibes", target="src/main.py", expect=1))
    assert dv.run(root, ["README.md"], False, False)[0] == 2


def test_duplicate_id_is_an_error(tmp_path):
    doc = (block(id="dup", kind="loc", target="src/main.py", expect=11)
           + block(id="dup", kind="loc", target="src/main.py", expect=11))
    root = project(tmp_path, doc)
    code, report = dv.run(root, ["README.md"], False, False)
    assert code == 2, report
    assert any("duplicado" in line for line in report)


def test_matches_counts_a_pattern(tmp_path):
    root = project(tmp_path, block(id="todos", kind="matches", target="src/*.py",
                                   pattern="x = ", expect=10))
    assert dv.run(root, ["README.md"], False, False)[0] == 0


def test_files_counts_a_glob(tmp_path):
    root = project(tmp_path, block(id="n", kind="files", target="src/*.py", expect=1))
    assert dv.run(root, ["README.md"], False, False)[0] == 0


def test_command_kind_is_opt_in(tmp_path):
    root = project(tmp_path, block(id="c", kind="command", command="echo 11", expect=11))
    assert dv.run(root, ["README.md"], False, False)[0] == 2, "sin --allow-command debe ser error"
    assert dv.run(root, ["README.md"], True, False)[0] == 0


def test_update_rewrites_the_expect_value(tmp_path):
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py", expect=4541))
    code, report = dv.run(root, ["README.md"], False, True)
    assert code == 0, report          # un drift reescrito no es un drift
    assert any("UPDATE" in line for line in report)
    assert "expect: 11" in (root / "README.md").read_text(encoding="utf-8")
    assert dv.run(root, ["README.md"], False, False)[0] == 0


def test_directory_of_docs_is_walked(tmp_path):
    root = project(tmp_path, "sin bloques\n")
    (root / "docs").mkdir()
    (root / "docs" / "a.md").write_text(
        block(id="a", kind="loc", target="src/main.py", expect=999), encoding="utf-8")
    assert dv.run(root, ["docs"], False, False)[0] == 1


def test_cli_exit_code_propagates(tmp_path):
    root = project(tmp_path, block(id="loc", kind="loc", target="src/main.py", expect=4541))
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--docs", "README.md"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "DRIFT" in proc.stdout
