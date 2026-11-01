"""La v2 se sostiene sola: datos reproducibles, canario, trampas que trampean en archivos
que no se leen enteros, y un pipeline (script -> salida -> puntuación) que distingue."""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
V2 = BASE / "v2"


def cargar(nombre, carpeta):
    spec = importlib.util.spec_from_file_location(f"{nombre}_{carpeta.name}_t", carpeta / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gen = cargar("generar", V2)
ref = cargar("referencia", V2)
pun = cargar("puntuar", BASE)
corr = cargar("correr", BASE)
CASOS, MODO, CONTEXTO = corr.cargar_casos(V2)
TRAMPAS = [c["id"] for c in CASOS if not c.get("negativo")]


def test_los_datos_publicados_salen_del_generador(tmp_path):
    gen.generar(tmp_path)
    publicados = sorted(p.relative_to(V2 / "datos") for p in (V2 / "datos").rglob("*") if p.is_file())
    nuevos = sorted(p.relative_to(tmp_path / "datos") for p in (tmp_path / "datos").rglob("*") if p.is_file())
    assert publicados == nuevos
    for rel in publicados:
        assert (V2 / "datos" / rel).read_bytes() == (tmp_path / "datos" / rel).read_bytes(), rel
    assert (V2 / "verdad.json").read_bytes() == (tmp_path / "verdad.json").read_bytes()


def test_canario_la_referencia_coincide_con_la_verdad_del_generador():
    assert ref.calcular(V2 / "datos") == json.loads((V2 / "verdad.json").read_text(encoding="utf-8"))


def test_semilla_nueva_y_ocho_trampas_en_modo_script():
    assert gen.SEMILLA != cargar("generar", BASE).SEMILLA      # la v1 y sus respuestas son públicas
    assert MODO == "script" and len(TRAMPAS) == 8
    assert set(TRAMPAS) == set(ref.calcular(V2 / "datos"))


@pytest.mark.parametrize("trampa", TRAMPAS)
def test_cada_trampa_trampea(trampa):
    r = ref.calcular(V2 / "datos")[trampa]
    assert r["ingenua"] != r["correcta"]


def test_ningun_export_se_suma_a_mano():
    """Lo que la v1 no tenía: ningún archivo se suma leyéndolo."""
    for f in (V2 / "datos").rglob("*.csv"):
        assert len(f.read_bytes().splitlines()) > 1000, f.name


def test_las_preguntas_no_nombran_la_trampa():
    """La v1 decía "de la empresa A", "en pesos", "sin contar el flete" en la pregunta."""
    prohibidas = ["empresa", "pesos", "moneda", "flete", "envío", "total general", "duplic",
                  "encoding", "columna", "ytd", "solap", "serie"]
    for c in CASOS:
        if not c.get("negativo"):
            assert not [p for p in prohibidas if p in c["pregunta"].lower()], c["id"]


def test_el_tipo_de_cambio_del_contexto_es_el_de_la_referencia():
    assert f"{ref.TIPO_DE_CAMBIO} $ por U$S" in CONTEXTO and ref.TIPO_DE_CAMBIO == gen.TIPO_DE_CAMBIO


def test_los_negativos_salen_de_los_archivos():
    stock = list(csv.reader((V2 / "datos/t6/stock.csv").open(encoding="utf-8"), delimiter=";"))
    ventas = (V2 / "datos/t3/Ventas 2026 YTD.csv").read_text(encoding="utf-8").splitlines()[5:]
    esperado = {"n1_filas": len(stock) - 1, "n2_clientes": len({x.split(";")[1] for x in ventas})}
    assert {c["id"]: c["correcta"] for c in CASOS if c.get("negativo")} == esperado


# --- El runner del modo script ------------------------------------------------

def test_extrae_el_ultimo_bloque_python():
    texto = "uno\n```python\nprint(1)\n```\notro\n```python\nprint(2)\n```\n"
    assert corr.extraer_script(texto) == "print(2)\n"
    assert corr.extraer_script("sin bloque") is None


@pytest.mark.parametrize("script", [
    "import subprocess\n", "import socket\n", "from urllib.request import urlopen\n",
    "import shutil\n", "import os\nos.remove('x')\n", "open('x', 'w')\n", "open('x', mode='a')\n",
    "m = 'w'\nopen('x', m)\n", "exec('1')\n", "__import__('os')\n", "getattr(1, 'x')\n",
    "from pathlib import Path\nPath('x').unlink()\n", "Path('x').write_text('y')\n",
    "def (:\n",
])
def test_rechaza_lo_peligroso_o_roto(script):
    assert corr.rechazo(script)


def test_un_metodo_con_nombre_de_builtin_no_es_el_builtin():
    """El ensayo lo encontró: `re.compile` no es `compile`, ni `str.replace` es `os.replace`."""
    assert corr.rechazo("import re\nre.compile('x')\n") is None
    assert corr.rechazo("compile('1', 'f', 'exec')\n")
    assert corr.rechazo("import os\nos.system('x')\n")
    assert corr.rechazo("from pathlib import Path\nPath('x').open('w')\n")
    assert corr.rechazo("import io\nio.open('datos/a.csv', 'a')\n")
    assert corr.rechazo("from pathlib import Path\nPath('datos/a.csv').open(encoding='cp1252')\n") is None
    assert corr.rechazo("import io\nio.open('datos/a.csv', 'r', encoding='latin-1')\n") is None


def test_acepta_un_script_de_lectura():
    script = ("import csv, re, os\nfrom pathlib import Path\nfrom collections import Counter\n"
              "with open('datos/x.csv', encoding='cp1252', newline='') as f:\n    pass\n"
              "print(os.path.join('a', 'b'), Path('.').glob('*'))\n")
    assert corr.rechazo(script) is None


INGENUO_T1 = """
import csv
with open('datos/t1/ventas_marzo.csv', encoding='utf-8') as f:
    filas = list(csv.reader(f, delimiter=';'))[5:]
print('CIFRA:', sum(int(x[2]) for x in filas))
"""
CORRECTO_T1 = INGENUO_T1.replace("for x in filas)", "for x in filas if 'TOTAL' not in x[1])")


@pytest.mark.parametrize("script,esperado", [(INGENUO_T1, "I"), (CORRECTO_T1, "C"),
                                             ("print('CIFRA: 1')", "O"), ("1/0", "-"),
                                             ("import socket", "-")])
def test_el_pipeline_distingue_ingenuo_de_correcto(tmp_path, script, esperado):
    """Respuesta con script -> se corre en una copia de datos -> se puntúa su salida."""
    destino = tmp_path / "t1_total_general.txt"
    salida = corr.guardar_y_correr(f"Explico.\n```python\n{script}\n```\n", destino, V2)
    r = ref.calcular(V2 / "datos")["t1_total_general"]
    assert pun.clasificar(salida, r["correcta"], r["ingenua"]) == esperado
    assert destino.with_suffix(".respuesta.md").is_file() and destino.with_suffix(".err").is_file()


def test_un_script_rechazado_no_se_ejecuta(tmp_path):
    salida, err = corr.correr_script("import socket\nprint('CIFRA: 1')\n", tmp_path)
    assert salida == "" and err.startswith("[RECHAZADO]")


def test_el_script_corre_en_una_copia_descartable_no_en_la_suite(tmp_path):
    salida = corr.guardar_y_correr(
        "```python\nimport os\nprint(os.getcwd())\nprint(open('datos/t6/stock.csv').read()[:6])\n```",
        tmp_path / "x.txt", V2)
    cwd, inicio = salida.splitlines()[:2]
    assert inicio == "Codigo" and Path(cwd).resolve() != V2.resolve()
    assert not Path(cwd).exists()                      # la copia se borró al terminar


def test_v2_puntua_con_su_propia_referencia(tmp_path):
    for c in ("con-skill", "sin-skill"):
        d = tmp_path / "haiku" / c
        d.mkdir(parents=True)
        for caso in CASOS:
            (d / f"{caso['id']}.txt").write_text("CIFRA: NO DETERMINABLE\n", encoding="utf-8")
        t1 = ref.calcular(V2 / "datos")["t1_total_general"]
        (d / "t1_total_general.txt").write_text(f"CIFRA: {t1['correcta' if c == 'con-skill' else 'ingenua']}\n",
                                                encoding="utf-8")
    tabla, completa = pun.puntuar(tmp_path, V2)
    assert completa and "| t6_campos_muertos | C | C |" in tabla and "| t1_total_general | C | I |" in tabla
