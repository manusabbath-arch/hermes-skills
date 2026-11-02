"""evals/activacion.py sin gastar: el modelo se reemplaza por una función."""
import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "evals" / "activacion.py"
spec = importlib.util.spec_from_file_location("activacion_t", SCRIPT)
activacion = importlib.util.module_from_spec(spec)
sys.modules["activacion_t"] = activacion
spec.loader.exec_module(activacion)


def _correr(monkeypatch, tmp_path, tope, respuesta, costo=0.1, modelos="haiku,sonnet"):
    llamadas = []

    def falso(cwd, modelo, prompt, presupuesto):
        llamadas.append((modelo, round(presupuesto, 4), "Tenés instaladas" in prompt))
        return respuesta(prompt), costo

    monkeypatch.setattr(activacion.ronda, "llamar", falso)
    monkeypatch.setattr(sys, "argv", ["activacion.py", "--out", str(tmp_path), "--tope-usd", str(tope),
                                      "--modelos", modelos, "--semilla", "3"])
    return activacion.main(), llamadas


def _todas_vacias(prompt):
    n = sum(1 for l in prompt.splitlines() if l[:1].isdigit() and ". " in l)
    return json.dumps({str(i): [] for i in range(1, n + 1)})


def test_complete_answers_score_and_costs_are_recorded(monkeypatch, tmp_path):
    rc, llamadas = _correr(monkeypatch, tmp_path, 1.0, _todas_vacias)
    assert rc == 0 and [m for m, _, _ in llamadas] == ["haiku", "sonnet"]
    assert all(vio_prompt for _, _, vio_prompt in llamadas)
    assert llamadas[0][1] == 0.5 and llamadas[1][1] == 0.9      # el tope se reparte en lo que queda
    costos = json.loads((tmp_path / "costos.json").read_text(encoding="utf-8"))
    assert costos["gastado_usd"] == 0.2 and (tmp_path / "answers" / "sonnet.json").is_file()


def test_incomplete_answer_is_red(monkeypatch, tmp_path):
    rc, _ = _correr(monkeypatch, tmp_path, 1.0, lambda p: '{"1": []}')
    assert rc == 1


def test_budget_exhausted_stops_before_calling(monkeypatch, tmp_path):
    rc, llamadas = _correr(monkeypatch, tmp_path, 0.105, _todas_vacias, costo=0.1)
    assert rc == 1 and [m for m, _, _ in llamadas] == ["haiku"]


def test_zero_budget_is_a_usage_error(monkeypatch, tmp_path):
    rc, llamadas = _correr(monkeypatch, tmp_path, 0, _todas_vacias)
    assert rc == 2 and llamadas == []
