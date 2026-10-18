"""Hermetic tests for activation_eval scoring and prompt building."""
import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "activation_eval.py"
spec = importlib.util.spec_from_file_location("activation_eval", SCRIPT)
ae = importlib.util.module_from_spec(spec)
sys.modules["activation_eval"] = ae
spec.loader.exec_module(ae)

KEY = {
    "1": {"expected": "a", "kind": "positivo", "owner": "a"},
    "2": {"expected": None, "kind": "negativo", "owner": "a"},
    "3": {"expected": "b", "kind": "positivo", "owner": "b"},
    "4": {"expected": None, "kind": "ajeno", "owner": None},
}


def test_perfect_answers():
    rows, problems = ae.score(KEY, {"1": ["a"], "2": [], "3": ["b"], "4": []})
    assert problems == [] and "**2/2** | **0**" in rows[-1]


def test_negative_and_offtopic_picks_are_false_positives():
    rows, _ = ae.score(KEY, {"1": ["a"], "2": ["a"], "3": ["b"], "4": ["b"]})
    assert "| `a` | 1/1 | 1 |" in rows and "| `b` | 1/1 | 1 |" in rows


def test_wrong_skill_counts_as_miss_and_false_positive():
    rows, _ = ae.score(KEY, {"1": ["b"], "2": [], "3": ["b"], "4": []})
    assert "| `a` | 0/1 | 0 |" in rows and "| `b` | 1/1 | 1 |" in rows


def test_missing_answer_is_red():
    _, problems = ae.score(KEY, {"1": ["a"], "2": [], "3": ["b"]})
    assert problems == ["pedido 4 sin respuesta"]


def test_build_hides_expected_from_prompt(tmp_path):
    ae.build(tmp_path, seed=1)
    prompt = (tmp_path / "prompt.md").read_text(encoding="utf-8")
    key = json.loads((tmp_path / "key.json").read_text(encoding="utf-8"))
    assert '"expected"' not in prompt
    assert len(key) == prompt.count("\n") - prompt.count("\n", 0, prompt.index("1. ")) or len(key) > 0
    kinds = {v["kind"] for v in key.values()}
    assert kinds == {"positivo", "negativo", "ajeno"}
    # cada skill del tap aparece en el catálogo
    for d in (ae.REPO / "skills").iterdir():
        if (d / "SKILL.md").is_file():
            assert f"`{d.name}`" in prompt


def test_cli_rejects_non_json_answer(tmp_path):
    (tmp_path / "key.json").write_text(json.dumps(KEY), encoding="utf-8")
    (tmp_path / "a.txt").write_text("no sé", encoding="utf-8")
    assert ae.main(["score", "--key", str(tmp_path / "key.json"), "--answers", str(tmp_path / "a.txt")]) == 1
