# Guards over state that lives outside the repo
## Contents

1. Measure a versioned witness, not the live foreign system
2. Compare identity, not position
3. Severity: one implementation, two surfaces
4. When the subject is absent, say so
5. Read it from the checkout the producer writes to
6. Test the guard itself, first
7. Wiring it into an existing gate


A guard whose subject is not in the repo — another tool's config file, a credential or
memory store another process owns, a live database, a per-machine directory — fails in ways
a repo-only check never does. The rules below keep it from becoming either a permanently
red check or a green that measures nothing.

## Measure a versioned witness, not the live foreign system

- The gate must not shell out to a binary that lives outside the repo, parse its ids, or
depend on its schema. Ids change when a store is recreated and its CLI changes between
versions, so the check goes red for reasons that are not the repo's — and the first person
to hit it declares the red and stops looking.
- Commit a **seal**: the hashes needed to detect drift (per item, not just per file), the
date, and a free-text reference to where the authoritative copy lives. The seal certifies
"someone reviewed this and published it", which is the invariant you actually own. It does
not certify the foreign system's contents, and it should say so in its own docstring.
- Take the seal **after** the action that makes it true, never before. Sealing first leaves
the guard green over a copy that does not exist. Give the command a `--seal` that refuses
to write when the source is missing, so the empty case cannot pass.

## Compare identity, not position

- Hash each item and compare as multisets. Index-based comparison reports every entry as
  changed when one is inserted at the top, and a check that cries wolf gets declared.
- Normalize line endings and edge whitespace before hashing in any repo with
  `core.autocrlf` on: the file gets rewritten without its content changing, and the guard
  must not read that as drift.
- Store hashes, never the text. The failure message names positions ("entry 4 changed"),
  not content: the point is to send someone to copy the delta, not to version the data.

## Severity: one implementation, two surfaces

- The same function feeds the operator view (a per-item PASS/WARN list) and the gate (one
  line per run). Two copies of the logic diverge, and the copy in the gate is the one
  nobody reads.
- Make it non-mandatory in the operator view and non-critical in the gate whenever the
  subject cannot invalidate a business number. It stays visible every run without
  closing the gate for everyone; reserve mandatory for invariants whose violation
  corrupts results.
- **Import the tolerance from the operator view; do not re-derive it for the gate.** A check the
  baseline does not know is treated as a regression, so a brand-new guard that can be red on a
  healthy machine blocks every commit/push from its first run. A gate-only threshold that is
  stricter than the dashboard's (say 24 h while the dashboard already allows 26 h for the same
  daily task) does exactly that the first night the machine legitimately did not run. Call the
  operator-view function, or at minimum import its constant, so both surfaces flip on the same
  hour — one truth, and the new guard gets to be green on day one.

## When the subject is absent, say so

- A machine without the foreign system (fresh clone, CI box, another workstation) must not
  report PASS as if it had measured. If the harness only has ok/not-ok, keep it
  non-failing but put the words in the message: which store was expected, and that the
  seal was not compared here. A bare green over zero files is the exact failure mode the
  guard exists to end.
- A missing *seal* is ERROR ("cannot measure"), not PASS and not FAIL: it is a red you fix
  by sealing, and it must not be sellable as a tolerated red.

## Read it from the checkout the producer writes to

- When the foreign state is a task's log/registry inside the project's own tree, it is usually
  gitignored and therefore **per-checkout**: the scheduler runs in the integration tree, and a
  per-session `git worktree` has an empty `logs/`. A guard that resolves the path from the module
  location reports "never ran" on every healthy task whenever it is invoked from a worktree — the
  exact false red that gets a guard declared away.
- Resolve the path to the integration tree explicitly, through the same helper the scheduled tasks
  use (or a declared fixed path, registered where the project keeps its list of legitimate fixed
  paths), and make the first run print the absolute path it read. That print is the proof: same
  check, same machine, different answer means it read two different files.
- The same asymmetry bites the verification run: re-running the task from a worktree writes its log
  there, so the fix has no evidence in the tree that matters. Verify from the integration tree.

## Test the guard itself, first

- Registration tests come before the implementation: the check is in the registry, it is
  non-critical, the operator view lists it. A guard that is not registered cannot fire.
- Write them before the module and run them red — the import error is the honest first red.
  A guard test that passes on the first run proved nothing.
- **When the guard is invoked through a wrapper that must not block, the wrapper is part of the
  subject.** A hook that fails open exits 0 on every path, including the path where its subject
  never ran, so a test that asserts only `returncode == 0` and empty stdout stays green over a
  guard that did nothing at all. Assert what the run must PRODUCE — a clean stderr, the guard's
  log line, its state file — and prove the assertion load-bearing by reintroducing the defect
  once (point the path at nothing, drop the conversion) and watching it go red. Run the wrapper
  by hand with a synthetic payload and read the artefact: that line is the evidence, and it is
  also what tells you the guard is looking at the files you think it is.
- **A path the wrapper hands to a native binary has to be in the native form.** A wrapper
  assembled in a POSIX-emulation shell passes `/c/...`-style paths that native tools reject, the
  subject never starts, and the fail-open exit hides it — this is the concrete mechanism behind
  most "the guard is wired and silent" reports.
- Cover four paths: no seal (ERROR), subject absent (explained, non-failing), clean (PASS),
  and each drift kind separately (added / edited / removed).

## Wiring it into an existing gate

- A new check is a regression on the sealed baseline until the baseline knows it: add the
  entry, run the full gate, and re-seal from the complete registry (never from a filtered
  run — a filtered seal drops every check it did not run and turns them into regressions).
- If the project keeps a declared perimeter of entry points or totals, register the new
  check there too, or the guard exists but nothing counts it.
