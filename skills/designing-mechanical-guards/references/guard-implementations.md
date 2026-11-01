# Guard reference implementations
## Contents

1. Shape 1 — static probe over source
2. Shape 2 — comparator: prose against a measured value
3. Registering into the project's gate


Two shapes cover most guards worth writing. Both are written to be *called* rather than
retyped — the parameters exist so tests can inject a subject and an expected value.

## Shape 1 — static probe over source

For rules about how code is written: an attribute read that nothing assigns, a route with
no handler, a config key nothing consumes, a banned import. Parse, do not grep: grep cannot
tell a read from a write, an import from a comment, or a call in a string literal.

```python
import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    archivo: str
    linea: int
    nombre: str


def candidates(tree: ast.AST) -> list[tuple[str, int]]:
    """Reads-with-a-default over a literal name. Narrow by construction."""
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) == 3):          # the default is what hides it
            continue
        name = node.args[1]
        if isinstance(name, ast.Constant) and isinstance(name.value, str):
            out.append((name.value, node.lineno))
    return out


def assigned_names(tree: ast.AST) -> set[str]:
    """Every name the file could be assigning: attr store, name store, def."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            names.add(node.attr)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def audit(paths: list[Path], base: Path) -> tuple[list[Finding], int, int]:
    """Returns (findings, files_inspected, names_seen). The counters are the point."""
    trees, universe = {}, set()
    for p in paths:
        try:
            trees[p] = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue                              # count these, do not hide them
    for t in trees.values():
        universe |= assigned_names(t)
    findings = [
        Finding(str(p.relative_to(base)), line, name)
        for p, t in trees.items()
        for name, line in candidates(t)
        if name not in universe                          # repo-wide, not per-file
    ]
    return sorted(findings, key=lambda f: (f.archivo, f.linea)), len(trees), len(universe)
```

**Design notes that matter:**

- The set of assigned names is built across **all** files, not per file. Where the wiring
  lives in a different module is exactly the case that matters; a per-file check reports
  every legitimate cross-module read as a defect.
- Scope the walk to the project's source roots. Vendored code, migrations and generated
  files are noise and noise is what gets a guard disabled.
- `SyntaxError` is skipped, not fatal: on a multi-writer tree a file is routinely mid-edit.
  But count the skipped files and expose the count, or a tree of unparseable files reads
  as clean.
- The finding is only a *candidate*. Say so in the message so the reader judges rather than
  obeys.

## Shape 2 — comparator: prose against a measured value

For rules about what documents claim. The measured side is injected so the guard never
hard-codes a number.

```python
import re
from pathlib import Path

# Enumerate the vocabulary. Do NOT write a regex for "any number".
COUNTS = re.compile(r"(?<![\w.])(\d{1,4})\s+(pares|chequeos|claves)\b", re.IGNORECASE)

# History markers. Everything here means "this figure is being recounted, not cited".
HISTORY = re.compile(r"dec[íi]a|eran|cuando|medido el|20\d\d-\d\d-\d\d", re.IGNORECASE)

# Where the number's own clause starts: the last boundary before it.
BOUNDARY = re.compile(r"(?:[.;:|()]|\by\b|\bpero\b|\bmientras\b|\bo\b)", re.IGNORECASE)
WINDOW = 50


def _exempt(line: str, start: int) -> bool:
    """Is the window immediately BEFORE the figure marked as history?

    Scoping to the preceding window (not the whole line) is what keeps an exempt
    historical figure from also exempting a current, wrong one beside it.
    """
    before = line[:start]
    cuts = list(BOUNDARY.finditer(before))
    since = cuts[-1].end() if cuts else 0
    return bool(HISTORY.search(before[max(since, len(before) - WINDOW):]))


def audit(roots: Path, measured: dict[str, int], files: tuple[str, ...]):
    out = []
    for name in files:
        path = roots / name
        if not path.exists():
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in COUNTS.finditer(line):
                noun = m.group(2).lower()
                if noun not in measured or int(m.group(1)) == measured[noun]:
                    continue
                if _exempt(line, m.start()):
                    continue
                out.append((name, lineno, int(m.group(1)), noun, measured[noun]))
    return out
```

**The exemption is the part that goes wrong.** Two failures to design against:

| Exemption scope | Fails because |
|---|---|
| Whole line | a current, wrong figure sharing a line with a historical one is excused |
| Whole sentence, cut only on `.;:` | `"decía 18 … y hoy corre 19"` is one sentence — the current figure is excused |

Cut the window on the boundaries that separate *independent claims* (`y`, `pero`, `o`,
`mientras`, plus punctuation) and mark the history with an explicit vocabulary.

**Do not exempt the marker that means "current".** A phrase like "as of today" or "hoy"
next to a figure reads as freshness, not as history — exempting it silently accepts exactly
the stale number the guard exists to catch.

### Read the expected value from ONE designated section of the document

A comparator that reads a whole document for a figure cannot tell a citation from a
retraction. The same number sits in the body as history, in a table as a measurement, and in
the summary as the claim, and every occurrence is compared against the same expected value.
Then the document's own prose style decides the guard's precision, and prose changes weekly.

Give each document a single machine-readable verdict section (`**Resultado**`, a findings
block, a front-matter field) and read **only** that as the expected value. Print which
section was read in the guard's message, so a wrong-section read is visible on the green
path. Measured failure of not doing it: a figure quoted correctly from a document's body was
reported as a retracted figure and blocked the gate, because the expected value came from
that document's result block — the guard was right about the mismatch and wrong about which
of the two was the claim.

The companion rule goes on the writing side, not the guard: **whoever cites the figure cites
what the verdict section says, and leaves the detail in the document.** A guard that reads one
section plus a rule that says so is stable; a guard that reads everything is a style linter
nobody asked for.

**The tests this shape needs** (all four, or the exemption is untested):

1. a stale figure is caught, with the written and measured values both asserted;
2. an aligned figure passes;
3. a historical recount of an old figure is exempt;
4. **the mixed line** — historical figure exempt, current figure on the same line still
   caught. This is the one that fails if the scope is wrong.

## Registering into the project's gate

Add an entry to the existing registry rather than a new runner, and keep the guard's own
signature narrow: `fn()` called by the gate, `fn(root, measured)` for the tests. If the
registry supports severity, mark a check that does not invalidate a result as non-critical —
a blocking check that is wrong once will be bypassed forever.

Give the message the counter the guard already computed:

```python
def summary(findings, inspected: int, universe: int) -> str:
    lines = [f"  {inspected} file(s) inspected, {universe} name(s) seen"]
    if not findings:
        lines.append("  No reads over a name that nothing assigns.")
        return "\n".join(lines)
    lines.append(f"  {len(findings)} finding(s):")
    lines += [f"    {f.archivo}:{f.linea}  {f.nombre!r}" for f in findings]
    return "\n".join(lines)
```

Note what the green branch says: no count that would need maintaining. Counters computed at
run time are fine; a number typed into the source is the defect.

