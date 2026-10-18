"""The SKILL.md says its code block is "validado, copia-pega": prove it every CI run.

Extracts the block, runs it in a fresh interpreter with DeprecationWarning as
error and a timeout (a process that hangs on exit is a failure too: duckdb 1.5
`.arrow()` streams written to Delta used to hang here). No skip when the stack
is missing: a skipped example is an empty green.
"""
import re
import subprocess
import sys
from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[1] / "SKILL.md"
HEADING = r"Código validado \(copia-pega\)"


def test_validated_code_block_runs(tmp_path):
    text = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(rf"## {HEADING}\n\n```python\n(.*?)```", text, re.S)
    assert m, "el bloque de código validado desapareció del SKILL.md"
    script = tmp_path / "example.py"
    script.write_text(m.group(1), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-I", "-W", "error::DeprecationWarning", str(script)],
        capture_output=True, text=True, timeout=120, cwd=tmp_path,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    assert r.stdout.strip(), "el ejemplo no imprimió nada"
