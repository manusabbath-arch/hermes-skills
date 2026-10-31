"""El benchmark se sostiene solo: datos reproducibles, canario, y una trampa que trampea."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, HERE / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


gen = cargar("generar")
ref = cargar("referencia")
pun = cargar("puntuar")
CASOS = json.loads((HERE / "casos.json").read_text(encoding="utf-8"))
TRAMPAS = [c["id"] for c in CASOS if not c.get("negativo")]


def test_los_datos_publicados_salen_del_generador(tmp_path):
    gen.generar(tmp_path)
    publicados = sorted(p.relative_to(HERE / "datos") for p in (HERE / "datos").rglob("*") if p.is_file())
    nuevos = sorted(p.relative_to(tmp_path / "datos") for p in (tmp_path / "datos").rglob("*") if p.is_file())
    assert publicados == nuevos
    for rel in publicados:
        assert (HERE / "datos" / rel).read_bytes() == (tmp_path / "datos" / rel).read_bytes(), rel
    assert (HERE / "verdad.json").read_bytes() == (tmp_path / "verdad.json").read_bytes()


def test_canario_la_referencia_coincide_con_la_verdad_del_generador():
    """Dos cálculos independientes: el generador en memoria, la referencia desde el archivo."""
    verdad = json.loads((HERE / "verdad.json").read_text(encoding="utf-8"))
    assert ref.calcular(HERE / "datos") == verdad


def test_son_ocho_trampas_y_cada_una_tiene_su_caso():
    assert len(TRAMPAS) == 8
    assert set(TRAMPAS) == set(ref.calcular(HERE / "datos"))


@pytest.mark.parametrize("trampa", TRAMPAS)
def test_cada_trampa_trampea(trampa):
    """Si la ingenua coincide con la correcta, la trampa no discrimina."""
    r = ref.calcular(HERE / "datos")[trampa]
    assert r["ingenua"] != r["correcta"]


def test_identidades_independientes():
    r = ref.calcular(HERE / "datos")
    assert r["t1_total_general"]["ingenua"] == 2 * r["t1_total_general"]["correcta"]
    assert r["t3_periodo"]["correcta"] == pytest.approx(r["t3_periodo"]["ingenua"] * 90 / 31, abs=0.02)
    # la clave por número solo es otra cifra: hay números repetidos entre series
    assert r["t8_duplicados"]["dedup_por_numero"] != r["t8_duplicados"]["correcta"]


def test_el_archivo_de_encoding_no_es_utf8():
    raw = (HERE / "datos" / "t7_encoding" / "ventas_agosto.csv").read_bytes()
    with pytest.raises(UnicodeDecodeError):
        raw.decode("utf-8")
    assert "ENVÍO" in raw.decode("cp1252")


@pytest.mark.parametrize("texto,esperado", [
    ("CIFRA: 3030", 3030.0), ("CIFRA: 3.030", 3030.0), ("CIFRA: 3,030", 3030.0),
    ("**CIFRA:** 237,74", 237.74), ("CIFRA: 237.74", 237.74), ("CIFRA: $ 1.234,5", 1234.5),  # ficticio
    ("CIFRA: NO DETERMINABLE", None),
])
def test_lee_la_cifra(texto, esperado):
    assert pun.numero(pun.CIFRA.findall(texto)[-1]) == esperado


def test_clasifica():
    assert pun.clasificar("bla\nCIFRA: 3030", 3030, 6060) == "C"
    assert pun.clasificar("CIFRA: 6060", 3030, 6060) == "I"
    assert pun.clasificar("CIFRA: 1", 3030, 6060) == "O"
    assert pun.clasificar("sin cifra", 3030, 6060) == "-"
    assert pun.clasificar(None, 3030, 6060) == "-"
    assert pun.clasificar("CIFRA: NO DETERMINABLE", None, 0) == "C"
    assert pun.clasificar("CIFRA: 0", None, 0) == "I"


def test_una_respuesta_que_falta_es_rojo(tmp_path):
    (tmp_path / "haiku" / "con-skill").mkdir(parents=True)
    (tmp_path / "haiku" / "sin-skill").mkdir(parents=True)
    (tmp_path / "haiku" / "con-skill" / "t1_total_general.txt").write_text("CIFRA: 3030", encoding="utf-8")
    tabla, completa = pun.puntuar(tmp_path)
    assert not completa and "INCOMPLETA" in tabla


def test_una_corrida_sin_modelos_no_es_verde(tmp_path):
    assert pun.puntuar(tmp_path)[1] is False


def test_correr_exige_tope():
    corr = cargar("correr")
    with pytest.raises(SystemExit):
        sys.argv = ["correr.py", "--out", "x"]
        corr.main()
