# Guard perimeter: measuring what a check actually walks
## Contents

1. Enumerate the should-be perimeter, then the actual one, and diff them
2. Turn the perimeter into an assertion that cannot re-narrow
3. The perimeter has a second dimension: the extensions it admits
4. When a guard takes its subject list from a tuple, the tuple is the guard
5. Exclusions must be scoped to what they mean, not to convenience
6. The perimeter has a third dimension: what the ignore file removes
7. A scanner that walks the filesystem never reads the ignore file
8. The perimeter has a fourth dimension: which checkout it resolves to


The most common structural defect in a check set is not a bug in a check — it is a check
whose **file list** is narrower than the tree it is believed to cover. Two guards that glob
the same root, plus a directory neither of them names, read as complete coverage from
inside either one. This is the recipe for measuring it instead of eyeballing it.

## 1. Enumerate the should-be perimeter, then the actual one, and diff them

Do not read the globs and reason about them. Build both sets in code and print the
difference. Run this from the repo root with whatever interpreter the project uses.

```python
from pathlib import Path

RAIZ = Path(".")
EXCLUIDOS = {".git", ".venv", "__pycache__", "node_modules", "engram"}


def todo_el_python(raiz=RAIZ):
    return sorted(
        p for p in raiz.rglob("*.py")
        if not any(parte in EXCLUIDOS for parte in p.parts)
    )


# El perimetro REAL: lo que las guardas del proyecto recorren. Copiarlo de la fuente,
# no reescribirlo de memoria — si cambia alla, esta medicion tiene que cambiar sola.
def perimetro_de_las_guardas(raiz=RAIZ):
    recorridos = set()
    # Un glob por guarda que camina el arbol.
    for patron in ("src/*.py",):
        recorridos |= {p.resolve() for p in raiz.glob(patron)}
    # Un root por guarda que recibe un directorio.
    # recorridos |= {p.resolve() for p in (raiz / "otro/root").rglob("*.py")}
    return recorridos


todo = {p.resolve() for p in todo_el_python()}
fuera = sorted(p.relative_to(RAIZ.resolve()) for p in todo - perimetro_de_las_guardas())
print(f"{len(todo)} archivos .py en el arbol, {len(fuera)} fuera del perimetro")
for p in fuera:
    print("  FUERA:", p)
```

Expected output names every unvisited file. Each one is then classified:

| Finding | Verdict |
|---|---|
| Generated output, vendored code, fixtures, caches | Legitimate exclusion — declare it in the guard with the reason |
| A sibling source directory, a second scripts folder, a reports folder holding runnable code | **Real blind spot** — widen the glob, or move the files under the watched root |
| A file that does work on import, or reads a source by hand | **A live defect the guard was supposed to catch** — fix the file and widen the guard in one commit |

## 2. Turn the perimeter into an assertion that cannot re-narrow

The measurement above is a one-off. The durable form is a test that states the permitted
exceptions by name, so a new directory is a red in the suite rather than a silent gap:

```python
PERMITIDOS = (
    # Cada excepcion con su motivo. Un path suelto sin motivo es como se llega a la
    # lista de exclusiones que nadie se anima a tocar.
    "reports/scripts/one_off_generator.py",   # una corrida, ya produjo sus salidas
)


def test_no_hay_codigo_fuera_de_los_roots_vigilados():
    sueltos = sorted(
        str(p.relative_to(RAIZ))
        for p in RAIZ.rglob("*.py")
        if not any(parte in EXCLUIDOS for parte in p.parts)
        and not str(p.relative_to(RAIZ)).startswith(("src/", "tests/"))
        and p.name != "cli.py"
        and str(p.relative_to(RAIZ)) not in PERMITIDOS
    )
    assert not sueltos, (
        "Hay .py fuera de los roots vigilados: " + ", ".join(sueltos) + ". "
        "Moverlos al root con su guard `__main__`, o declararlos arriba con el motivo."
    )
```

And the non-vacuity guard beside it — every perimeter test needs one, or an empty tree
passes:

```python
def test_el_perimetro_encontro_archivos():
    assert len(list(RAIZ.rglob("*.py"))) > 50, "El rglob dejo de encontrar archivos"
```

## 3. The perimeter has a second dimension: the extensions it admits

The diff above measures *where* a guard walks. A guard can also be narrow in *what kind of
file* it reads there, and the two defects look different in the output: a directory gap
usually shows as nothing being reported at all, while a format gap shows as a **correct-looking
denominator** over the wrong set.

Start from the histogram, not from the guard's code:

```bash
for f in $(git ls-files); do echo "${f##*.}"; done | sort | uniq -c | sort -rn
```

Then rule on each extension, once, in writing:

| Kind | Verdict |
|---|---|
| Table-like formats holding the same records (`.csv`, `.tsv`, `.json`, `.ndjson`, `.sqlite`) | **One perimeter.** A record hidden in the sibling format is the same defect |
| Container / markup / prose formats (`.md`, `.rst`, `.html`) | Out of scope, **stated as such** — a document discussing a case is not a leak |
| Tool and config files `.txt`, files with no extension (`.githooks/*`, `Makefile`) | Out of scope, stated — and name the residual risk explicitly ("a `.txt` carrying a roster is not covered") so the guard is not read as total coverage |

Write the ruling as a single constant the guard reads (`EXTENSIONES_DATOS = (...)`) and give
it one owner, so a new format is added in one edit instead of being remembered in each
caller. The check that reports this perimeter keeps a **non-zero denominator requirement**
over all of it — with several formats in play, "nothing inspected" becomes likelier, not
less.

### Calibrating a widened perimeter before it ships

The detector was tuned against the narrow set, so run the widened guard against the real
tree **first** and read every finding as a candidate false positive:

- **A structural file sharing the data's vocabulary.** A schema catalogue, a config tree, an
  API model all contain keys named after business entities. Measured: widening a `.csv` guard
to `.json` made a schema catalogue match, because it declares one key per entity
  (`"CUSTOMER": ...`, `"PRODUCT": ...`). The file is not a leak; the *test* was too loose.
- **The fix is a shape test, not an exclusion.** In a nested format the signal for a record
  is an object that is **an element of a list** (a row), not a bare key anywhere in the
  document — declarative schema is written as nested objects, a dataset as a list of them.
  Scope the matcher to that shape, and add a fixture asserting the structural file does **not**
  match, so the next widening cannot re-break it.
- **Widening must not create a new red.** Measure before/after: if the tree goes from clean
  to red, either the finding is real (handle it) or the matcher is wrong (tighten it). A
  guard shipped red on day one is the false-alarm trap. "N files before, N+k after, still
  zero findings" is the sentence that proves the door was closed without declaring a new
  failure.
- **Report the format in the finding.** Carrying the extension into the finding's output
  makes a mixed-format report readable and makes the next format's absence visible.

## 4. When a guard takes its subject list from a tuple, the tuple is the guard

A guard that audits *documents* rather than source has a hardcoded list of filenames — the
entry points, the index, the configs. That list is its perimeter, and it was chosen when
the list was shorter. Rank the whole tree by how often it changes and check that the
top of that ranking is in the list:

```bash
for f in $(git ls-files '*.md'); do
  echo "$(git log --oneline -- "$f" | wc -l) $f"
done | sort -rn | head -10
git rev-list --count HEAD
```

A file that changes in half of all commits and is not audited is the finding. The file's
high churn is *why* it drifted: nothing kept it honest, and prose corrections do not
survive the next edit.

## 5. Exclusions must be scoped to what they mean, not to convenience
Every exemption in a guard earns one of two verdicts:

- **Scoped to the token or window it applies to.** Correct — a historical mention is
  exempt for the figure it recounts, and the rest of the same line is still checked.
- **Scoped to a whole line, file, or directory "to reduce noise".** A blind spot exactly
  where the problem was. Replace it with a declaration in the input (a named tuple, an
  explicit parameter, a comment marker) so the exception leaves a trail.

Test both directions of every exemption you keep: one fixture where the thing is exempt,
one where a current violation sharing the same line is still caught. An exemption with only
the first test is an exemption that can quietly widen.

## 6. The perimeter has a third dimension: what the ignore file removes

A scanner that respects the repository's ignore rules — a secret scan, a confidentiality
check, an extension histogram built from `git ls-files` — shrinks whenever a line is added to
`.gitignore`. Nothing in the guard's own code changes, so a green that was honest last week
covers less this week and no output records the difference.

- **Read an ignore line as a perimeter edit, especially when a tool wrote it.** Agent CLIs and
  generators append their own scratch or output directories, and the tool's convenience is
  your scanner's blind spot. Measured: a worktree helper appends its private worktree root to
  `.gitignore` with no opt-out, which would drop that entire tree — a full checkout of the
  repo — out of the secret scan while it still lives inside the repo. `git check-ignore -v
  <path>` names the rule that matched; when the exclusion is deliberate, leave a one-line
  comment naming the guard that now skips it, because an inherited exclusion and a chosen one
  look identical in the file.
- **Measure the exclusion before accepting it.** Run the guard with the rule and without it
  (or compare a `git ls-files` walk against a filesystem walk) and read both counts. A
  difference that is intentional gets declared next to the rule; one that is not is the
  finding, and the fix belongs in the ignore file, not in the guard's code.
- **An ignore rule is half a mechanism: it stops the file from entering, and does nothing about
  the copies already in history.** The tracked-file guard goes green the instant the path is
  ignored, which is correct for *new* artifacts and misleading for one already committed — the
  data still travels inside every old commit, and integrating the branch with a fast-forward
  carries it along while the guard reports clean. So a green here answers "does the tree declare
  this", never "is it absent from what I am about to publish". The two halves:
  - **If the file never reached the shared remote, remove it from the branch's whole history**
    (`git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch <paths>'
    --prune-empty <base>..HEAD`), or the exclusion is cosmetic. Test reachability first with
    `git branch -r --contains <commit>` — a commit reachable from no remote ref is safe to
    rewrite, and one that is already published is not: rewriting it breaks every reference and
    every artifact hash that cites it, so a published leak is *declared*, never silently
    scrubbed.
  - **A history rewrite resets the working tree.** Regenerable outputs the rewrite removed come
    back as deleted files, so re-run the producers afterwards and confirm the guard's subject
    count is non-zero before believing the green — a clean guard over a tree whose files all
    vanished is the vacuous green wearing an ignore rule.
- **When the subject is a *class* of artifact rather than a named file, the guard is as wide as
  its list of names, and the list is the thing to audit.** The same ignore file names artifacts
  one line at a time, so a new artifact of an already-ruled-on kind is uncovered by default; the
  durable form states the kind (a filename pattern, an extension plus a column-name test) and
  measures the denominator, so the next artifact of that kind is caught without anyone
  remembering this conversation.

## 7. A scanner that walks the filesystem never reads the ignore file

§6 is the scan that respects the repository's ignore rules. The opposite arrangement is just
as common and fails in the opposite way: a scanner that walks the **working tree** (`rglob`,
`os.walk`) with its own hand-written exclusion set. Its perimeter is that set, not the ignore
file, so a line added to `.gitignore` changes nothing about what it reads — and nothing about
the scan looks wrong in either file.

- **The blow-up is invisible until a directory kind that was never there appears.** Measured:
  a session installed a Node dependency tree inside the repo — 3,437 files — and the secret
  scan went from 627 files to 4,064, with **every one of its 70 findings** in third-party
  code (`password:` in a compiled schema, a credentialed URL in an HTTP helper). The
  repository's own files were clean throughout. Read findings grouped by their source root
  before believing a red: when they all sit in a subtree that is a dependency or a cache, the
  perimeter is the defect, not the tree.
- **Exclude by directory NAME, not by path.** These sets are matched against every part of a
  path, so the bare directory name covers it at any depth, under any tool's directory. A path
  scoped to the single tool that exists today re-narrows the moment the next tool installs the
  same way — which is the whole failure being fixed.
- **The step with no escape is the one to fix, not the one to route around.** When the
  scanner is one step of a commit hook and offers no skip variable, a red it produces is not
  yours to waive: measured, a single finding in a dependency blocked the commit of every
  session in every worktree. Widen the perimeter and land it there, rather than hunting for a
  bypass.
- **Give the exclusion set its own non-vacuity guard.** The set is exactly the kind of list
  that gets widened "to reduce noise", and a set widened far enough scans nothing while still
  reporting zero findings. Assert three things, not one: the walk is non-empty; a known file
  of the repository's own source is still in it; and a synthetic tree holding the excluded
  directory beside a real source file keeps the source and drops the directory. The third is
  what proves the exclusion rather than merely the declaration.
- **A filesystem-walking scanner picks its own root, and a root chosen for convenience is a
  perimeter set by accident.** Measured: a check searching for a file's hash walked the whole
  Desktop — 1.3 GB, about half of it under a directory of backups — and took ~50 s, while
  every file it was actually looking for lived in the subtree the project declares as its
  working data (222 MB, ~4 s). The expensive root and the correct root were different
  directories, and the slowness was the only symptom. Point such a scan at the subtree the
  project already declares (a config path, the tracked working directory) rather than at an
  enclosing folder, and state the residual risk in the same breath: an artifact living
  outside the declared subtree is reported as absent — the conservative direction, because a
  guard may say "not found" over something it did not search but must never say "exists"
  over something it did not verify.

## 8. The perimeter has a fourth dimension: which checkout it resolves to

Every measurement above assumes the guard's root is *the tree you are working in*. When that
root comes from a **config constant that names one particular checkout** — typically the
integration tree — a guard run from a worktree audits the other one. Nothing in the output
says so: the denominator is non-zero, the findings are clean, and the artifacts you just
created do not exist as far as the check is concerned.

Measured: a declaration-contract check read its root from the project's fixed config path
while the process ran from a branch worktree. A new artifact staged **only on the branch**
was invisible, so the completeness guard — the one whose entire job is "an undeclared
artifact is a finding" — went green on precisely the case it was built to catch.

The two roots are a real distinction, not a defect in the config. Classify each call site:

| Kind of path | Root | Why |
|---|---|---|
| Artifacts the session produces or audits (generated reports, the declaration itself, the index) | The **code location** (`Path(__file__).resolve().parents[N]`) | They are versioned artifacts of *this* tree; a worktree must judge its own |
| State that exists once for the whole repository (claims, cross-session concurrency, backups, the scheduled-run log) | The **config path** | Being shared across worktrees is the point |

- **The tell is a verdict that does not move when you edit the tree it claims to measure.**
  Green in a worktree and red in the integration tree, or the reverse, or red only inside the
  commit hook.
- **Its own test will not catch this**, because a well-written test injects the root as a
  parameter — the defect lives only on the *default* path, which is whatever the CLI entry
  point passes. Cover the default explicitly: assert the module's root constant equals the
  directory the entry point lives in, so the two cannot drift apart.
- **Make that assertion discriminating.** If it ever runs from the integration tree the two
  roots coincide and it proves nothing, so fail loudly in that case instead of passing.
- **Do not fix it by editing the shared config.** Some callers point at the shared tree on
  purpose; the repair is per module, one call site at a time, each with its own test.
- **When the project's own plan enumerates the remaining call sites, re-measure before you
  quote it.** Measured: the plan said 47 uses across 27 modules and the tree had 52 across
  30, with the writer of the very artifacts the guard protects among them. A count in a plan
  is a measurement from the day it was written, and this is exactly the kind of refactor that
  grows while it waits.
- **And the branch runs the copy of the guard it carries — which may be older than the one
  that was fixed.** When the shared tree fixed the root resolution *after* your branch forked,
  the worktree keeps executing the stale guard and returns the stale verdict: green, over the
  tree it should not be reading, for a defect the fixed guard would catch. Nothing in the
  output is wrong-looking — the denominator is non-zero and the findings are clean. The tell is
  a disagreement that tracks *where the guard was read* rather than what it measured: red when
  the branch is tested from a separate checkout, green when the same guard runs in the worktree.
  **Do not re-apply the fix on your branch** — that duplicates it and the two copies drift;
  rebase onto the shared tree so the branch picks up the corrected guard. Then re-read the
  evidence, not the exit code: the run must still be green *and* its reported subject must be
  the tree you are working in — a stale green and a fresh green print the same word.


