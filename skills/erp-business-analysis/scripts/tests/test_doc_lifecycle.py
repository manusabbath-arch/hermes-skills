"""Hermetic tests for doc_lifecycle. Only tmp_path notes."""
import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "doc_lifecycle.py"
TEMPLATES = Path(__file__).resolve().parents[2] / "templates"

spec = importlib.util.spec_from_file_location("doc_lifecycle", SCRIPT)
dl = importlib.util.module_from_spec(spec)
sys.modules["doc_lifecycle"] = dl
spec.loader.exec_module(dl)


def note(d, name, **fm):
    body = "---\n" + "".join(f"{k}: {v}\n" for k, v in fm.items()) + "---\n# x\n"
    (d / f"{name}.md").write_text(body, encoding="utf-8")


def reds(d):
    return dl.check(dl.load([d]))


def test_depending_on_retracted_note_is_red(tmp_path):
    note(tmp_path, "margen", retractado='"bug row[4]"')
    note(tmp_path, "informe", depends_on='"[[margen]]"')
    r = reds(tmp_path)
    assert len(r) == 1 and "margen" in r[0] and "bug row[4]" in r[0]


def test_retracted_note_citing_retracted_note_is_fine(tmp_path):
    note(tmp_path, "margen", retractado='"bug"')
    note(tmp_path, "correccion", retractado='"tambien"', depends_on="margen.md")
    assert reds(tmp_path) == []


def test_stale_counts_as_retracted_and_lists_resolve(tmp_path):
    note(tmp_path, "a", estado="stale")
    note(tmp_path, "b")
    note(tmp_path, "c", depends_on="[b, a]")
    r = reds(tmp_path)
    assert len(r) == 1 and "'a'" in r[0]


def test_missing_dependency_is_red(tmp_path):
    note(tmp_path, "c", depends_on='"[[fantasma]]"')
    assert "no existe" in reds(tmp_path)[0]


def test_open_decision_needs_owner_and_trigger(tmp_path):
    note(tmp_path, "d1", estado="abierta", **{"dueño": '""'}, fecha_limite='""', disparador_revision='""')
    r = reds(tmp_path)
    assert any("sin dueño" in x for x in r) and any("disparador" in x for x in r)


def test_open_decision_with_trigger_only_is_ok(tmp_path):
    note(tmp_path, "d1", estado="abierta", **{"dueño": "Manu"}, fecha_limite='""',
         disparador_revision='"llega el export de octubre"')
    assert reds(tmp_path) == []


def test_closed_decision_that_promised_a_measure_must_report_it(tmp_path):
    note(tmp_path, "d1", estado="decidida", **{"dueño": "Manu"},
         hipotesis='"baja la merma"', metrica_esperada='"merma < 2%"', resultado_observado='""')
    assert "sin resultado" in reds(tmp_path)[0]
    note(tmp_path, "d1", estado="decidida", **{"dueño": "Manu"},
         hipotesis='"baja la merma"', metrica_esperada='"merma < 2%"',
         resultado_observado='"1,7%"', estado_evaluacion="confirmada")
    assert reds(tmp_path) == []


def test_inline_comments_in_frontmatter_are_ignored(tmp_path):
    (tmp_path / "v.md").write_text(
        '---\nestado: pendiente          # pendiente | pass\nretractado: ""             # motivo\n---\n',
        encoding="utf-8")
    n = dl.load([tmp_path])[0]
    assert n.get("estado") == "pendiente" and not n.retracted


def test_shipped_templates_parse_and_are_not_red(tmp_path):
    # Las plantillas del skill tienen que pasar su propio chequeo una vez completadas.
    notes = dl.load([TEMPLATES / "validation-note.md", TEMPLATES / "decision-note.md"])
    assert len(notes) == 2
    assert all("depends_on" not in r for r in dl.check(notes))


def test_cli_zero_notes_is_red(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1 and "0 nota(s)" in r.stdout


def test_cli_green(tmp_path):
    note(tmp_path, "a", estado="pass")
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
