#!/usr/bin/env python3
"""
correr.py — corre los casos del benchmark con y sin `erp-business-analysis`.

GASTA DINERO: cada caso es una llamada a un modelo. Por eso:
  - `--tope-usd` es obligatorio y es el tope de TODA la corrida; cada llamada lleva
    `--max-budget-usd` = lo que queda del tope repartido entre las llamadas que faltan.
    Al pasarlo se corta, y los casos que quedan puntúan como fallo (`-`).
  - Nunca se programa: lo corre una persona, en el momento.

Aislamiento: cada (modelo, condición) trabaja en una carpeta propia que solo tiene una
copia de `datos/` (y, con skill, una copia de la skill en `skill/`). Se usa
`claude -p` sin settings de usuario/proyecto (`--setting-sources ""`, así no cargan
hooks ni plugins), sin skills ni comandos (`--disable-slash-commands`), solo con
Read/Glob/Grep y sin MCP. `--bare` no sirve: no lee la credencial guardada. La carpeta
de trabajo está en el temporal del sistema, lejos de cualquier CLAUDE.md: el sujeto sin skill no puede encontrarla, y ninguno puede
correr código (la trampa tiene que verse leyendo, como se ve en una planilla).

Salida: `<out>/<modelo>/<con-skill|sin-skill>/<caso>.txt` y `<out>/costos.json`. Después:
`python3 puntuar.py --run <out>`.

Modo script (`--suite v2`): la suite trae `casos.json` como objeto con `"modo": "script"` y un
`contexto`. El sujeto puede mirar los archivos pero no ejecutar nada; entrega UN script
Python y este runner lo corre una sola vez en una copia nueva de `datos/` (`python -I`,
120 s), después de un chequeo estático: solo imports de una lista corta de la librería
estándar, sin builtins dinámicos, sin `open` para escribir y sin llamadas que borran,
renombran o lanzan procesos. Un script rechazado, que falla o que no imprime `CIFRA:`
puntúa `-`. Se guarda todo: `<caso>.respuesta.md` (el texto), `<caso>.script.txt`,
`<caso>.err` y `<caso>.txt` (la salida del script, que es lo que se puntúa).

Uso:  python3 correr.py --out <dir> --tope-usd 5 [--suite v2] [--modelos haiku,sonnet,opus] [--casos t1_total_general,...]
Exit: 0 terminó dentro del tope, 1 cortó por tope o por error de una llamada, 2 uso.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent / "skills" / "erp-business-analysis"

INSTRUCCION = (
    "Sos un analista. Respondé la pregunta usando solo los archivos de esta carpeta "
    "(no podés ejecutar código: leé los archivos y hacé las cuentas a mano, con cuidado). "
    "Explicá en pocas líneas cómo llegaste. La ÚLTIMA línea de tu respuesta tiene que ser "
    "exactamente `CIFRA: <número>` (sin unidades ni separador de miles), o "
    "`CIFRA: NO DETERMINABLE` si los datos no permiten responder."
)
CON_SKILL = ("Antes de responder, leé `skill/SKILL.md` y aplicá lo que corresponda "
             "(podés leer también sus `references/` y `templates/`). ")


INSTRUCCION_SCRIPT = (
    "Sos un analista de datos. {contexto} Respondé la pregunta usando solo los archivos de esta "
    "carpeta. Los exports son grandes: la cuenta se hace con un script. Podés mirar los archivos "
    "(Read, Glob, Grep) pero no ejecutar nada. Tu respuesta tiene que traer UN bloque ```python con "
    "el script completo: se va a correr una sola vez desde esta carpeta, con Python 3 y solo la "
    "librería estándar, y no vas a ver su salida. La ÚLTIMA línea que imprima el script tiene que "
    "ser exactamente `CIFRA: <número>` (sin unidades ni separador de miles), o "
    "`CIFRA: NO DETERMINABLE` si los datos no permiten responder. Antes del bloque, explicá en "
    "pocas líneas qué hace."
)
IMPORTS_OK = {"csv", "io", "re", "decimal", "collections", "pathlib", "math", "statistics",
              "datetime", "codecs", "itertools", "json", "sys", "glob", "os", "unicodedata",
              "functools", "operator", "fractions", "string", "typing", "dataclasses"}
# Por nombre, los builtins dinámicos; como atributo, los métodos que borran, mueven o lanzan
# procesos. Separados: `re.compile` no es `compile` (el ensayo de la v2 lo rechazaba).
BUILTINS_NO = {"exec", "eval", "compile", "__import__", "getattr", "setattr", "delattr", "globals",
               "vars", "breakpoint", "input"}
METODOS_NO = {"system", "popen", "remove", "unlink", "rmdir", "removedirs", "rmtree", "rename",
              "renames", "chmod", "chown", "kill", "symlink", "link", "truncate", "write_text",
              "write_bytes", "putenv", "mkdir", "makedirs", "startfile", "execv", "execve",
              "spawnv", "fork", "replace_file", "touch", "hardlink_to", "symlink_to"}
MODULOS_CON_OPEN = {"io", "codecs", "os"}   # su open lleva el modo en el 2.º argumento; Path, en el 1.º
BLOQUE = re.compile(r"```python[ \t]*\n(.*?)```", re.S)


def extraer_script(texto: str) -> str | None:
    bloques = BLOQUE.findall(texto)
    return bloques[-1] if bloques else None


def rechazo(script: str) -> str | None:
    """Motivo para no correr el script, o None. No es un sandbox: filtra lo obvio, y el
    script corre en una copia descartable de `datos/`."""
    try:
        arbol = ast.parse(script)
    except SyntaxError as exc:
        return f"no compila: {exc}"
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            nombres = [a.name for a in nodo.names] if isinstance(nodo, ast.Import) else [nodo.module or ""]
            for n in nombres:
                if n.split(".")[0] not in IMPORTS_OK:
                    return f"import no permitido: {n}"
        if isinstance(nodo, ast.Call):
            f = nodo.func
            es_metodo = isinstance(f, ast.Attribute)
            nombre = f.attr if es_metodo else f.id if isinstance(f, ast.Name) else ""
            if nombre in (METODOS_NO if es_metodo else BUILTINS_NO):
                return f"llamada no permitida: {nombre}"
            if nombre == "open":
                de_modulo = es_metodo and isinstance(f.value, ast.Name) and f.value.id in MODULOS_CON_OPEN
                posicion = 0 if es_metodo and not de_modulo else 1
                modos = list(nodo.args[posicion:posicion + 1]) + [k.value for k in nodo.keywords
                                                                  if k.arg in ("mode", "flags")]
                for m in modos:
                    if not (isinstance(m, ast.Constant) and isinstance(m.value, str)):
                        return "open con modo no literal"
                    if set(m.value) & set("wax+"):
                        return f"open para escribir: {m.value!r}"
    return None


def correr_script(script: str, cwd: Path) -> tuple[str, str]:
    """(stdout, stderr) del script corrido una vez en `cwd`."""
    motivo = rechazo(script)
    if motivo:
        return "", f"[RECHAZADO] {motivo}"
    (cwd / "_respuesta.py").write_text(script, encoding="utf-8")
    dec = lambda b: (b or b"").decode("utf-8", errors="replace")  # noqa: E731
    try:
        proc = subprocess.run([sys.executable, "-I", "_respuesta.py"], cwd=cwd,
                              capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "", "[TIMEOUT] 120 s"
    # La ruta del temporal trae el usuario de la máquina; la salida se publica.
    tapar = lambda t: t.replace(str(cwd.parent), "<tmp>")  # noqa: E731
    return tapar(dec(proc.stdout)), tapar(dec(proc.stderr))[-2000:]


def cargar_casos(suite: Path) -> tuple[list[dict], str, str]:
    """(casos, modo, contexto). La v1 es una lista; una suite con modo es un objeto."""
    data = json.loads((suite / "casos.json").read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data, "lectura", ""
    return data["casos"], data.get("modo", "lectura"), data.get("contexto", "")


def guardar_y_correr(texto: str, destino: Path, suite: Path) -> str:
    """Guarda respuesta, script y stderr junto a `destino`; devuelve la salida a puntuar."""
    def guardar(ext: str, t: str) -> None:
        destino.with_suffix(ext).write_text(t.rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    guardar(".respuesta.md", texto)
    script = extraer_script(texto)
    if script is None:
        guardar(".err", "[SIN SCRIPT] la respuesta no trae un bloque ```python")
        return ""
    guardar(".script.txt", script)
    with tempfile.TemporaryDirectory(prefix="erp-script-") as limpio:
        shutil.copytree(suite / "datos", Path(limpio) / "datos")
        salida, err = correr_script(script, Path(limpio))
    guardar(".err", err)
    return salida


def preparar(base: Path, con_skill: bool, suite: Path = HERE) -> Path:
    shutil.copytree(suite / "datos", base / "datos")
    if con_skill:
        shutil.copytree(SKILL, base / "skill", ignore=shutil.ignore_patterns("evals", "tests", "__pycache__"))
    return base


def llamar(cwd: Path, modelo: str, prompt: str, presupuesto: float) -> tuple[str, float]:
    cmd = ["claude", "-p", "--setting-sources", "", "--disable-slash-commands", "--model", modelo, "--tools", "Read,Glob,Grep",
           "--strict-mcp-config", "--no-session-persistence", "--output-format", "json",
           "--max-budget-usd", f"{presupuesto:.2f}"]
    exe = shutil.which(cmd[0])
    if exe is None:
        raise RuntimeError("no se encontró `claude` en el PATH")
    # El prompt va por stdin: en Windows `claude` es un .CMD y cmd.exe corta un argumento
    # en el primer salto de línea (y reinterpreta & | < > ^ %).
    proc = subprocess.run([exe, *cmd[1:]], cwd=cwd, input=prompt.encode("utf-8"),
                          capture_output=True, timeout=900)
    salida = proc.stdout.decode("utf-8", errors="replace")
    try:
        data = json.loads(salida)
    except json.JSONDecodeError:
        raise RuntimeError(f"salida no es JSON (exit {proc.returncode}): "
                           f"{proc.stderr.decode('utf-8', errors='replace')[:300]}") from None
    return str(data.get("result", "")), float(data.get("total_cost_usd", 0.0))


def main() -> int:
    ap = argparse.ArgumentParser(description="Corre el benchmark (gasta dinero).")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tope-usd", type=float, required=True)
    ap.add_argument("--modelos", default="haiku,sonnet,opus")
    ap.add_argument("--casos", default="")
    ap.add_argument("--suite", default="", help="subcarpeta de la suite (p. ej. v2); vacío = v1")
    args = ap.parse_args()
    suite = HERE / args.suite if args.suite else HERE
    if args.tope_usd <= 0:
        print("[ERROR] --tope-usd tiene que ser > 0", file=sys.stderr)
        return 2
    casos, modo, contexto = cargar_casos(suite)
    if args.casos:
        pedidos = set(args.casos.split(","))
        casos = [c for c in casos if c["id"] in pedidos]
    modelos = [m for m in args.modelos.split(",") if m]
    tareas = [(m, c, caso) for m in modelos for c in ("con-skill", "sin-skill") for caso in casos]
    gastado, costos, cortado = 0.0, [], False
    with tempfile.TemporaryDirectory(prefix="erp-trampas-") as tmp:
        dirs = {(m, c): preparar(Path(tmp) / m / c, c == "con-skill", suite) for m in modelos for c in ("con-skill", "sin-skill")}
        for i, (m, c, caso) in enumerate(tareas):
            restante = args.tope_usd - gastado
            presupuesto = restante / (len(tareas) - i)
            if presupuesto < 0.01:
                cortado = True
                print(f"[TOPE] {gastado:.2f} de {args.tope_usd:.2f} USD: quedan {len(tareas) - i} sin correr")
                break
            base = INSTRUCCION_SCRIPT.format(contexto=contexto) if modo == "script" else INSTRUCCION
            prompt = (CON_SKILL if c == "con-skill" else "") + base + "\n\nPregunta: " + caso["pregunta"]
            try:
                texto, costo = llamar(dirs[(m, c)], m, prompt, presupuesto)
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                print(f"[ERROR] {m}/{c}/{caso['id']}: {exc}", file=sys.stderr)
                cortado = True
                continue
            gastado += costo
            destino = args.out / m / c / f"{caso['id']}.txt"
            destino.parent.mkdir(parents=True, exist_ok=True)
            if modo == "script":
                texto = guardar_y_correr(texto, destino, suite)
            destino.write_text(texto.rstrip("\n") + "\n", encoding="utf-8", newline="\n")
            costos.append({"modelo": m, "condicion": c, "caso": caso["id"], "usd": round(costo, 4)})
            print(f"{m}/{c}/{caso['id']}: {costo:.3f} USD (acumulado {gastado:.2f})")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "costos.json").write_text(
        json.dumps({"tope_usd": args.tope_usd, "gastado_usd": round(gastado, 4), "llamadas": costos},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return 1 if cortado else 0


if __name__ == "__main__":
    raise SystemExit(main())
