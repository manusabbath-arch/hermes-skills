"""Hermetic tests for check_baseline: every blocking rule has a case that must block."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "check_baseline.py"
spec = importlib.util.spec_from_file_location("check_baseline", SCRIPT)
cb = importlib.util.module_from_spec(spec)
sys.modules["check_baseline"] = cb
spec.loader.exec_module(cb)


def write(path: Path, data) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def run(tmp_path, results, baseline=None, *extra):
    r = write(tmp_path / "r.json", results)
    b = tmp_path / "base.json"
    if baseline is not None:
        write(b, baseline)
    return cb.main(["--results", str(r), "--baseline", str(b), *extra]), b


BASE = {"sellado": "2026-01-01", "chequeos": {"a": "PASS", "b": "FAIL"}, "declarados": {}}


class TestLoQueNoBloquea:
    def test_rojo_conocido_que_sigue_rojo(self, tmp_path):
        assert run(tmp_path, {"a": "PASS", "b": "FAIL"}, BASE)[0] == 0

    def test_rojo_declarado(self, tmp_path):
        base = {**BASE, "chequeos": {"a": "PASS"},
                "declarados": {"a": {"motivo": "falta el export", "condicion_salida": "llega"}}}
        assert run(tmp_path, {"a": "FAIL"}, base)[0] == 0

    def test_chequeo_nuevo_en_verde(self, tmp_path):
        assert run(tmp_path, {"a": "PASS", "b": "FAIL", "c": "PASS"}, BASE)[0] == 0

    def test_arreglado(self, tmp_path, capsys):
        assert run(tmp_path, {"a": "PASS", "b": "PASS"}, BASE)[0] == 0
        assert "b: FAIL -> PASS" in capsys.readouterr().out


class TestLoQueBloquea:
    def test_verde_que_se_vuelve_rojo(self, tmp_path):
        assert run(tmp_path, {"a": "FAIL", "b": "FAIL"}, BASE)[0] == 1

    def test_rojo_nuevo_no_se_perdona_porque_ya_habia_rojos(self, tmp_path):
        assert run(tmp_path, {"a": "PASS", "b": "FAIL", "c": "FAIL"}, BASE)[0] == 1

    def test_fail_que_empeora_a_error(self, tmp_path):
        assert run(tmp_path, {"a": "PASS", "b": "ERROR"}, BASE)[0] == 1

    def test_chequeo_de_la_base_que_no_corrio(self, tmp_path, capsys):
        assert run(tmp_path, {"a": "PASS"}, BASE)[0] == 1
        assert "no corrieron" in capsys.readouterr().out

    def test_corrida_vacia(self, tmp_path):
        assert run(tmp_path, {}, BASE)[0] == 1

    def test_corrida_vacia_sin_base(self, tmp_path):
        assert run(tmp_path, {})[0] == 1

    def test_declaracion_sin_condicion_de_salida(self, tmp_path):
        base = {**BASE, "declarados": {"b": {"motivo": "x", "condicion_salida": ""}}}
        assert run(tmp_path, {"a": "PASS", "b": "FAIL"}, base)[0] == 1


class TestArchivos:
    def test_base_corrupta_no_es_base_ausente(self, tmp_path):
        r = write(tmp_path / "r.json", {"a": "PASS"})
        b = tmp_path / "base.json"
        b.write_text("{roto", encoding="utf-8")
        assert cb.main(["--results", str(r), "--baseline", str(b)]) == 2

    def test_veredicto_desconocido(self, tmp_path):
        assert run(tmp_path, {"a": "OK"}, BASE)[0] == 2


class TestSellado:
    def test_sellar_mezcla_no_reemplaza(self, tmp_path):
        code, b = run(tmp_path, {"a": "WARN"}, BASE, "--seal")
        assert code == 0
        data = json.loads(b.read_text(encoding="utf-8"))
        assert data["chequeos"] == {"a": "WARN", "b": "FAIL"}

    def test_sellar_conserva_declarados(self, tmp_path):
        base = {**BASE, "declarados": {"b": {"motivo": "m", "condicion_salida": "c"}}}
        _, b = run(tmp_path, {"a": "PASS"}, base, "--seal")
        assert "b" in json.loads(b.read_text(encoding="utf-8"))["declarados"]

    def test_no_se_sella_una_corrida_vacia(self, tmp_path):
        assert run(tmp_path, {}, BASE, "--seal")[0] == 2


class TestDeclarar:
    def test_declarar_un_rojo_nuevo_en_el_mismo_commit(self, tmp_path):
        code, b = run(tmp_path, {"a": "PASS", "b": "FAIL", "c": "FAIL"}, BASE,
                      "--declare", "c", "--reason", "falta dato", "--exit-condition", "llega")
        assert code == 0
        r = tmp_path / "r.json"
        assert cb.main(["--results", str(r), "--baseline", str(b)]) == 0

    @pytest.mark.parametrize("extra", [
        ["--declare", "a", "--reason", "m", "--exit-condition", "c"],   # está en PASS
        ["--declare", "b", "--reason", "", "--exit-condition", "c"],    # sin motivo
        ["--declare", "b", "--reason", "m"],                            # sin condición
        ["--declare", "z", "--reason", "m", "--exit-condition", "c"],   # no se midió
    ])
    def test_declaraciones_rechazadas(self, tmp_path, extra):
        assert run(tmp_path, {"a": "PASS", "b": "FAIL"}, BASE, *extra)[0] == 2

    def test_redeclarar_conserva_la_condicion(self, tmp_path):
        base = {**BASE, "declarados": {"b": {"motivo": "viejo", "condicion_salida": "llega"}}}
        code, b = run(tmp_path, {"a": "PASS", "b": "FAIL"}, base,
                      "--declare", "b", "--reason", "nuevo")
        assert code == 0
        assert json.loads(b.read_text(encoding="utf-8"))["declarados"]["b"]["condicion_salida"] == "llega"
