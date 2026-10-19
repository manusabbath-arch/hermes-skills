#!/usr/bin/env python3
"""
validate_skills.py — build-failing validator for this skills tap.

The playbook this repo publishes says: "if it can be mechanized, it is a check
that fails the build, not a paragraph." This is that check, applied to the repo
itself.

Verifies, for every skills/<name>/:
  - SKILL.md exists and its YAML frontmatter parses
  - required keys are present (name, description, version)
  - `name` matches the directory name (the loader keys on the directory)
  - `description` is a real trigger, not a stub - it is the ONLY text an agent
    reads to decide whether to load the skill
  - every templates/ references/ scripts/ path cited in the body exists
  - related_skills that live in this repo actually resolve
  - no `|| true` / `continue-on-error` inside shipped scripts (a gate that
    cannot fail is not a gate)
  - shipped Python compiles
  - rules from Anthropic's skill authoring guide: `name` is lowercase/digits/
    hyphens, <=64 chars, without the reserved words "anthropic"/"claude";
    `description` carries no XML tags; a references/ or templates/ .md longer
    than 100 lines opens with a table of contents (an agent previews long files
    with `head`); references/ files do not cite other references/ files (keep
    them one level deep from SKILL.md, or the agent reads them partially)
  - evals/evals.json exists with >= 5 scenarios in the guide's format
    ({skills, query, files, expected_behavior}), at least one of them
    `"negativo": true` (a request the skill should NOT change): "build
    evaluations first" - a skill without them was never shown to change, or to
    leave alone, what an agent does
  - trust policy (skills are executable supply chain): shipped scripts import
    only the stdlib, never a network module, and use subprocess only when
    listed in SUBPROCESS_ALLOWED; skill text carries no prompt-injection
    phrasing, pipe-to-shell installs, or invisible/bidi Unicode characters
  - business data from the source project (the repo is public): no amount with
    3+ significant digits ($381.927, 58,31M - ficticio) in any text file unless its line
    says "ficticio" - round illustrative amounts (290.000, 25M) pass; and, when
    `.private-terms` exists (gitignored, one term per line), none of its terms.
    Without that file the run says so: "not checked" is not "clean"
  - a skill whose files changed since the last v* tag carries a new `version`
    (shallow history is RED: it cannot see the tag)

Exit codes: 0 all green, 1 at least one RED. Paths anchored to __file__.
"""
from __future__ import annotations

import ast
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

REQUIRED_KEYS = ("name", "description", "version")
MIN_DESCRIPTION_CHARS = 80
MAX_DESCRIPTION_CHARS = 1024
MAX_SKILL_LINES = 500

# A description made only of these words triggers on nothing a user would type.
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_CHARS = 64
RESERVED_NAME_WORDS = ("anthropic", "claude")
XML_TAG = re.compile(r"</?[A-Za-z][\w-]*[^>]*>")
TOC_THRESHOLD_LINES = 100
TOC_HEADING = re.compile(r"^#{2,3} (Contents|Contenido|Índice)\s*$", re.M | re.I)
TOC_WINDOW_LINES = 30
MIN_EVALS = 5
MIN_NEGATIVE_EVALS = 1
MIN_EXPECTED_BEHAVIORS = 2

STUB_PATTERN = re.compile(
    r"^use when [\w/\- ]{0,40}(projects?|skills?|agents?|repos?)\.?$", re.I
)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal flat YAML frontmatter reader (no dependency on PyYAML)."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def cited_paths(body: str) -> set[tuple[str | None, str]]:
    """Paths the prose promises, as (skill_prefix, path).

    A citation may be local (`templates/foo.md`) or qualified with another
    skill (`empirical-system-invariants/scripts/guard.py`). An unqualified path
    is resolved against the citing skill - which is exactly how an agent reads
    it, and why a cross-skill path written bare is a broken reference.
    """
    found: set[tuple[str | None, str]] = set()
    pattern = r"`((?:([a-z0-9][a-z0-9-]*)/)?(?:templates|references|scripts)/[\w./-]+)`"
    for m in re.finditer(pattern, body):
        full, prefix = m.group(1).rstrip(".,;:)"), m.group(2)
        if full.endswith("/"):
            continue
        rel = full[len(prefix) + 1:] if prefix else full
        found.add((prefix, rel))
    return found


def check_evals(skill_dir: Path) -> list[str]:
    name = skill_dir.name
    path = skill_dir / "evals" / "evals.json"
    if not path.is_file():
        return [f"{name}: falta evals/evals.json (>= {MIN_EVALS} escenarios: query + expected_behavior)"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{name}: evals/evals.json no es JSON válido ({exc})"]
    negatives = sum(1 for ev in data if isinstance(ev, dict) and ev.get("negativo") is True) \
        if isinstance(data, list) else 0
    if isinstance(data, list) and len(data) >= MIN_EVALS and negatives < MIN_NEGATIVE_EVALS:
        return [f"{name}: evals/evals.json sin escenario negativo (`\"negativo\": true`): "
                "falta probar que la skill no empuja donde no corresponde"]
    if not isinstance(data, list) or len(data) < MIN_EVALS:
        n = len(data) if isinstance(data, list) else 0
        return [f"{name}: evals/evals.json tiene {n} escenario(s), mínimo {MIN_EVALS}"]
    errors = []
    for i, ev in enumerate(data):
        where = f"{name}: evals[{i}]"
        if not isinstance(ev, dict):
            errors.append(f"{where} no es un objeto")
            continue
        if name not in (ev.get("skills") or []):
            errors.append(f"{where}.skills no incluye '{name}'")
        if not str(ev.get("query", "")).strip():
            errors.append(f"{where}.query vacío")
        eb = ev.get("expected_behavior")
        if not isinstance(eb, list) or len([b for b in eb if str(b).strip()]) < MIN_EXPECTED_BEHAVIORS:
            errors.append(f"{where}.expected_behavior con menos de {MIN_EXPECTED_BEHAVIORS} criterios")
    return errors


# --- Trust policy ---------------------------------------------------------

NETWORK_MODULES = {
    "socket", "ssl", "urllib", "http", "ftplib", "smtplib", "poplib", "imaplib",
    "telnetlib", "xmlrpc", "socketserver", "asyncio", "webbrowser",
}
# Scripts that run a subprocess on purpose, with the reason. Adding one is a
# reviewed decision, visible in the diff.
SUBPROCESS_ALLOWED = {
    "skills/agent-ready-project/scripts/doc_verify.py": "kind=command, opt-in con --allow-command",
    "skills/agent-ready-project/scripts/worktree_guard.py": "corre git worktree/rev-list",
    "scripts/validate_skills.py": "corre git describe/diff/show contra el último tag (versión)",
}
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+|the\s+)?(previous|prior|above)\s+instructions", re.I),
    re.compile(r"ignor[aáe]\w*\s+(todas\s+)?las\s+instrucciones\s+(anteriores|previas)", re.I),
    re.compile(r"disregard\s+(the\s+|your\s+)?(system|previous)\s+(prompt|instructions)", re.I),
    re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b", re.I),
    re.compile(r"base64\s+(-d|--decode)[^\n|]*\|\s*(ba)?sh\b", re.I),
]
# Zero-width and bidirectional controls: invisible to a reviewer, readable to a model.
HIDDEN_CHARS = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")


def imported_modules(source: str) -> set[str]:
    mods: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.add(node.module.split(".")[0])
    return mods


def check_script_policy(script: Path, rel: str) -> list[str]:
    try:
        mods = imported_modules(script.read_text(encoding="utf-8"))
    except SyntaxError:
        return []  # py_compile ya lo reporta
    errors = []
    local = {p.stem for p in script.parent.glob("*.py")}
    for m in sorted(mods - set(sys.stdlib_module_names) - local - {"__future__"}):
        errors.append(f"{rel}: importa '{m}', que no es stdlib (los scripts publicados no traen dependencias)")
    for m in sorted(mods & NETWORK_MODULES):
        errors.append(f"{rel}: importa '{m}' (red): un script publicado no sale a la red")
    if "subprocess" in mods and rel not in SUBPROCESS_ALLOWED:
        errors.append(f"{rel}: usa subprocess y no está en SUBPROCESS_ALLOWED (agregarlo con su motivo)")
    return errors


def check_text_policy(path: Path, rel: str) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors = []
    for pat in INJECTION_PATTERNS:
        m = pat.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            errors.append(f"{rel}:{line}: texto con forma de instrucción inyectada o instalación a ciegas: '{m.group(0)}'")
    m = HIDDEN_CHARS.search(text)
    if m:
        line = text.count("\n", 0, m.start()) + 1
        errors.append(f"{rel}:{line}: carácter Unicode invisible U+{ord(m.group(0)):04X}")
    return errors


# --- Datos del negocio de origen --------------------------------------------
# El repo es público y las lecciones vienen de un negocio real. Un monto preciso
# (3+ cifras significativas) tiene forma de dato real; uno redondo, de ejemplo.
# Los nombres propios no se pueden listar acá sin publicarlos: van en un archivo
# ignorado por git que solo existe en la máquina de quien conoce el origen.

NUMBER = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?"
AMOUNT = re.compile(
    rf"(?:US\$|U\$S|USD|UYU|\$)\s?(?P<a>{NUMBER})(?:\s?(?:M|k|mil|millones)\b)?"
    rf"|\b(?P<b>\d+,\d+)\s?M\b"
)
MIN_PRECISE_DIGITS = 3
FICTICIO = re.compile(r"ficticio", re.I)
PRIVATE_TERMS_FILE = REPO / ".private-terms"
BUSINESS_SCAN_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".csv"}
BUSINESS_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}


def significant_digits(number: str) -> int:
    return len(re.sub(r"\D", "", number).strip("0"))


def load_private_terms(path: Path) -> list[str] | None:
    if not path.is_file():
        return None
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line.lower())
    return terms


def check_business_data(path: Path, rel: str, private_terms: list[str] | None = None) -> list[str]:
    errors = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for n, line in enumerate(lines, 1):
        if not FICTICIO.search(line):
            for m in AMOUNT.finditer(line):
                number = m.group("a") or m.group("b")
                if significant_digits(number) >= MIN_PRECISE_DIGITS:
                    errors.append(
                        f"{rel}:{n}: monto preciso '{m.group(0).strip()}' (forma de dato real): "
                        "redondearlo o marcar la línea 'ficticio'"
                    )
        low = line.lower()
        for term in private_terms or []:
            if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", low):
                errors.append(f"{rel}:{n}: término privado del proyecto de origen")
    return errors


def business_scan_files() -> list[Path]:
    files = []
    for p in sorted(REPO.rglob("*")):
        if p.is_file() and p.suffix in BUSINESS_SCAN_SUFFIXES and not (
            BUSINESS_SKIP_DIRS & set(p.relative_to(REPO).parts)
        ):
            files.append(p)
    return files


# --- La versión sube con el contenido -----------------------------------------
# Entre septiembre y el primer release las 7 skills cambiaron y ninguna subió de
# versión: quien instala no tiene cómo saber que lo suyo quedó viejo.

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def check_versions(repo: Path) -> tuple[list[str], str]:
    """Each skill whose files differ from the last v* tag must carry a new version."""
    tag = _git(repo, "describe", "--tags", "--abbrev=0", "--match", "v*")
    if tag.returncode != 0:
        if _git(repo, "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
            return (["historia shallow: no se ve el último tag (checkout con fetch-depth: 0)"], "")
        return ([], "NO chequeado: el repo no tiene tags v*")
    tag_name = tag.stdout.strip()
    errors = []
    for skill_md in sorted((repo / "skills").glob("*/SKILL.md")):
        name = skill_md.parent.name
        rel = f"skills/{name}"
        if _git(repo, "diff", "--quiet", tag_name, "--", rel).returncode == 0:
            continue
        old = _git(repo, "show", f"{tag_name}:{rel}/SKILL.md")
        if old.returncode != 0:
            continue  # skill nueva desde el tag
        old_v = (parse_frontmatter(old.stdout) or {}).get("version")
        new_v = (parse_frontmatter(skill_md.read_text(encoding="utf-8")) or {}).get("version")
        if old_v == new_v:
            errors.append(f"{name}: cambió desde {tag_name} y sigue en version {new_v} (subirla)")
    return errors, f"contra {tag_name}"


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        return [f"{name}: falta SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        return [f"{name}: frontmatter YAML ausente o sin cierre `---`"]

    for key in REQUIRED_KEYS:
        if not fm.get(key):
            errors.append(f"{name}: frontmatter sin `{key}`")

    if fm.get("name") and fm["name"] != name:
        errors.append(
            f"{name}: frontmatter name='{fm['name']}' != directorio '{name}' "
            "(el loader indexa por directorio)"
        )

    fm_name = fm.get("name", "")
    if fm_name:
        if len(fm_name) > MAX_NAME_CHARS or not NAME_PATTERN.match(fm_name):
            errors.append(
                f"{name}: name='{fm_name}' debe ser minúsculas/dígitos/guiones, "
                f"<= {MAX_NAME_CHARS} chars"
            )
        for word in RESERVED_NAME_WORDS:
            if word in fm_name:
                errors.append(f"{name}: name contiene la palabra reservada '{word}'")

    desc = fm.get("description", "")
    if desc and XML_TAG.search(desc):
        errors.append(f"{name}: description con tag XML '{XML_TAG.search(desc).group(0)}'")
    if desc:
        if len(desc) < MIN_DESCRIPTION_CHARS:
            errors.append(
                f"{name}: description de {len(desc)} chars (<{MIN_DESCRIPTION_CHARS}). "
                "Es el UNICO texto que decide si la skill se carga: nombrá los "
                "términos que un usuario realmente teclea."
            )
        if len(desc) > MAX_DESCRIPTION_CHARS:
            errors.append(f"{name}: description de {len(desc)} chars (>{MAX_DESCRIPTION_CHARS})")
        if STUB_PATTERN.match(desc.strip()):
            errors.append(f"{name}: description genérica, no dispara con nada: '{desc}'")

    n_lines = text.count("\n") + 1
    if n_lines > MAX_SKILL_LINES:
        errors.append(
            f"{name}: SKILL.md de {n_lines} líneas (>{MAX_SKILL_LINES}). "
            "Mové el detalle a references/ (progressive disclosure)."
        )

    body = text[text.find("\n---\n", 3) + 5:]
    local_skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
    for prefix, rel in sorted(cited_paths(body), key=lambda x: (x[0] or "", x[1])):
        if prefix is None:
            if not (skill_dir / rel).exists():
                errors.append(
                    f"{name}: el cuerpo cita `{rel}` como local y no existe "
                    "(si es de otra skill, calificala con su nombre)"
                )
        elif prefix in local_skills:
            if not (SKILLS_DIR / prefix / rel).exists():
                errors.append(f"{name}: el cuerpo cita `{prefix}/{rel}` y no existe en este tap")
        # prefijo desconocido = skill externa al tap, no verificable acá.

    errors.extend(check_evals(skill_dir))

    for sub in ("references", "templates"):
        for doc in sorted((skill_dir / sub).glob("*.md")):
            doc_text = doc.read_text(encoding="utf-8")
            n_doc = doc_text.count("\n") + 1
            head = "\n".join(doc_text.splitlines()[:TOC_WINDOW_LINES])
            if n_doc > TOC_THRESHOLD_LINES and not TOC_HEADING.search(head):
                errors.append(
                    f"{name}: {sub}/{doc.name} tiene {n_doc} líneas y no abre con "
                    f"'## Contents' en sus primeras {TOC_WINDOW_LINES} (>{TOC_THRESHOLD_LINES} "
                    "líneas: el agente lo previsualiza con head y no ve el resto)"
                )
            if sub == "references":
                for _prefix, rel in cited_paths(doc_text):
                    if rel.startswith("references/"):
                        errors.append(
                            f"{name}: references/{doc.name} cita `{rel}`: las referencias "
                            "van a un solo nivel de SKILL.md"
                        )

    for doc in sorted(skill_dir.rglob("*")):
        if doc.suffix in {".md", ".json"} and doc.is_file():
            errors.extend(check_text_policy(doc, doc.relative_to(REPO).as_posix()))

    for script in skill_dir.rglob("*.py"):
        if "tests" in script.parts:
            continue
        errors.extend(check_script_policy(script, script.relative_to(REPO).as_posix()))
        source = script.read_text(encoding="utf-8")
        for banned in ("|| true", "continue-on-error"):
            # Ignorar la mención en prosa/docstring que EXPLICA por qué está prohibido.
            for line in source.splitlines():
                if banned in line and "NUNCA" not in line.upper() and not line.strip().startswith("#"):
                    errors.append(f"{name}: {script.name} contiene `{banned}` (gate que no puede fallar)")
        # Un directorio y no NamedTemporaryFile: en Windows el archivo abierto no
        # se puede reemplazar y py_compile escribe con os.replace.
        with tempfile.TemporaryDirectory() as tmp:
            try:
                py_compile.compile(str(script), cfile=str(Path(tmp) / "check.pyc"), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"{name}: {script.name} no compila -> {exc.msg.strip()}")

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"VALIDATE-SKILLS: no existe {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print("VALIDATE-SKILLS: el tap no publica ninguna skill", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for d in skill_dirs:
        errs = check_skill(d)
        all_errors.extend(errs)
        print(f"[{'ROJO' if errs else 'OK'}] {d.name}")
        for e in errs:
            print(f"    - {e}")

    repo_errors = []
    for script in sorted((REPO / "scripts").glob("*.py")):
        repo_errors.extend(check_script_policy(script, script.relative_to(REPO).as_posix()))
    print(f"[{'ROJO' if repo_errors else 'OK'}] scripts/ del repo")
    for e in repo_errors:
        print(f"    - {e}")
    all_errors.extend(repo_errors)

    terms = load_private_terms(PRIVATE_TERMS_FILE)
    data_errors = []
    for f in business_scan_files():
        data_errors.extend(check_business_data(f, f.relative_to(REPO).as_posix(), terms))
    scope = (f"montos + {len(terms)} término(s) privado(s)" if terms is not None
             else "solo montos; términos privados NO chequeados (falta .private-terms)")
    print(f"[{'ROJO' if data_errors else 'OK'}] datos del negocio de origen ({scope})")
    for e in data_errors:
        print(f"    - {e}")
    all_errors.extend(data_errors)

    version_errors, version_note = check_versions(REPO)
    print(f"[{'ROJO' if version_errors else 'OK'}] versión sube con el contenido ({version_note})")
    for e in version_errors:
        print(f"    - {e}")
    all_errors.extend(version_errors)

    print(
        f"\nVALIDATE-SKILLS: {len(skill_dirs)} skills, "
        f"{len(all_errors)} problema(s)"
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
