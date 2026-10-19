"""Hermetic tests for phantom_wiring. Only tmp_path files."""
import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "phantom_wiring.py"

spec = importlib.util.spec_from_file_location("phantom_wiring", SCRIPT)
pw = importlib.util.module_from_spec(spec)
sys.modules["phantom_wiring"] = pw  # @dataclass resolves its module through sys.modules
spec.loader.exec_module(pw)


def _py(tmp_path, name, src):
    p = tmp_path / name
    p.write_text(src, encoding="utf-8")
    return p


def test_getattr_default_on_unassigned_name_is_a_finding(tmp_path):
    _py(tmp_path, "a.py", "def f(o):\n    return getattr(o, 'cached_book', {})\n")
    a = pw.analyze([tmp_path], tmp_path)
    assert [(f.file, f.line, f.name) for f in a.findings] == [("a.py", 2, "cached_book")]
    assert not a.ok


def test_assignment_in_another_file_clears_it(tmp_path):
    _py(tmp_path, "a.py", "def f(o):\n    return getattr(o, 'cached_book', {})\n")
    _py(tmp_path, "b.py", "class C:\n    def __init__(self):\n        self.cached_book = {}\n")
    a = pw.analyze([tmp_path], tmp_path)
    assert a.findings == [] and a.ok
    assert a.files == 2


def test_setattr_and_def_count_as_assignment(tmp_path):
    _py(tmp_path, "a.py",
        "def f(o):\n    setattr(o, 'x', 1)\n    return getattr(o, 'x', 0), getattr(o, 'g', None)\n"
        "def g():\n    pass\n")
    assert pw.analyze([tmp_path], tmp_path).findings == []


def test_getattr_without_default_is_not_a_candidate(tmp_path):
    _py(tmp_path, "a.py", "def f(o):\n    return getattr(o, 'never')\n")
    assert pw.analyze([tmp_path], tmp_path).ok


def test_unreadable_file_is_red_even_without_findings(tmp_path):
    _py(tmp_path, "ok.py", "x = 1\n")
    _py(tmp_path, "broken.py", "def (:\n")
    a = pw.analyze([tmp_path], tmp_path)
    assert a.unreadable == ["broken.py"]
    assert a.findings == []
    assert not a.ok


def test_nothing_scanned_is_red_not_empty_green(tmp_path):
    a = pw.analyze([tmp_path], tmp_path)
    assert a.files == 0 and not a.ok
    assert "no se revisó ningún archivo" in pw.report(a)


def test_pycache_is_excluded(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    _py(tmp_path / "__pycache__", "junk.py", "getattr(o, 'z', 1)\n")
    _py(tmp_path, "a.py", "x = 1\n")
    a = pw.analyze([tmp_path], tmp_path)
    assert a.files == 1 and a.ok


def test_report_carries_denominator(tmp_path):
    _py(tmp_path, "a.py", "x = 1\ny = 2\n")
    out = pw.report(pw.analyze([tmp_path], tmp_path))
    assert "1 archivo(s) revisados, 2 nombre(s) asignados" in out


def test_cli_exit_codes(tmp_path):
    _py(tmp_path, "a.py", "def f(o):\n    return getattr(o, 'ghost', 0)\n")
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), "--root", str(tmp_path)],
                       capture_output=True)
    assert r.returncode == 1 and b"ghost" in r.stdout
    _py(tmp_path, "b.py", "ghost = 1\n")
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True)
    assert r.returncode == 0
