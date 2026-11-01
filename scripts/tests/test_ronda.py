"""evals/ronda.py sin gastar: la foto, el sorteo, los prompts y la lectura de notas."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "evals" / "ronda.py"
spec = importlib.util.spec_from_file_location("ronda_t", SCRIPT)
ronda = importlib.util.module_from_spec(spec)
sys.modules["ronda_t"] = ronda
spec.loader.exec_module(ronda)

EV = [{"query": "¿Uno?", "expected_behavior": ["c1", "c2"]},
      {"query": "¿Dos?", "expected_behavior": ["c3"]}]


def test_parse_skills_with_and_without_subset():
    assert ronda.parse_skills("a:7,8,b,c:1") == [("a", [7, 8]), ("b", None), ("c", [1])]
    with pytest.raises(ValueError):
        ronda.parse_skills("b,3")


def test_foto_takes_one_based_subset():
    todos = ronda.foto("erp-business-analysis", None)
    assert ronda.foto("erp-business-analysis", [1, len(todos)]) == [todos[0], todos[-1]]


def test_sorteo_is_reproducible_balanced_and_per_model():
    k = ronda.sortear(["x", "y", "z"], 7, "haiku")
    assert k == ronda.sortear(["z", "y", "x"], 7, "haiku")
    assert all({v["with_skill"], v["without_skill"]} == {"A", "B"} for v in k.values())
    claves = [ronda.sortear([f"s{i}" for i in range(20)], 7, m) for m in ("haiku", "sonnet")]
    assert claves[0] != claves[1]


def test_only_the_with_skill_prompt_mentions_the_skill():
    assert "skill/SKILL.md" in ronda.prompt_sujeto(EV, True)
    sin = ronda.prompt_sujeto(EV, False)
    assert "skill" not in sin.lower() and "## Pedido 2\n\n¿Dos?" in sin


def test_evaluator_prompt_has_criteria_and_no_key():
    p = ronda.prompt_evaluador(EV, "resp a", "resp b")
    assert "  2. c2" in p and "resp a" in p and "resp b" in p
    assert "with_skill" not in p and "con la skill" not in p.lower()


def _bloque(notas):
    return "texto\n```json\n" + json.dumps(notas) + "\n```\n"


COMPLETAS = [{"pedido": 1, "criterio": 1, "A": True, "B": False, "nota": ""},
             {"pedido": 1, "criterio": 2, "A": False, "B": False, "nota": ""},
             {"pedido": 2, "criterio": 1, "A": True, "B": True, "nota": ""}]


def test_reads_complete_grades():
    assert ronda.leer_notas(_bloque(COMPLETAS), EV) == COMPLETAS


@pytest.mark.parametrize("notas", [
    COMPLETAS[:2],                                                     # falta un criterio
    COMPLETAS + [COMPLETAS[0]],                                        # repetido
    [dict(COMPLETAS[0], A="sí")] + COMPLETAS[1:],                      # no booleano
    [dict(COMPLETAS[0], pedido=3)] + COMPLETAS[1:],                    # pedido inexistente
])
def test_incomplete_or_malformed_grades_are_rejected(notas):
    assert ronda.leer_notas(_bloque(notas), EV) is None


def test_no_json_block_is_rejected():
    assert ronda.leer_notas(json.dumps(COMPLETAS), EV) is None
