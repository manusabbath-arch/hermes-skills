---
name: designing-mechanical-guards
description: "Use when a rule keeps breaking and should become a check the machine runs - mechanical guards, pre-commit gates, vacuous greens, guard perimeters, ratchet baselines, declared reds, advisory-to-enforcement, and make-sure-this-never-happens-again. Covers writing the failing test first, wiring into the existing gate, proving no regression on a mature gate that already carries known reds, and the measured failure shapes of checks that look green while covering nothing."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [guards, checks, gates, regression, pre-commit, invariants, enforcement, quality]
    category: software-development
    related_skills: [agent-ready-project, empirical-system-invariants]
---

# Designing mechanical guards

For the task of turning a rule, a lesson, or a freshly-fixed defect into a check the
machine runs — adding an invariant to a project's existing gate, or building one when the
project has a gate but nothing covering this class of failure.

Guards whose subject lives outside the repo (a tool's config, another process's store) or IS
the repo (a source scan, an index) have their own failure shapes:
`references/guards-over-machine-state.md`, `references/self-scanning-detectors.md`.

Guards that carry **accepted exceptions** — checks allowed to stay red — rot in their own way: the
written reason is a photo of the day it was accepted, and it keeps being printed as if it were
today's state. Two fields per exception, live-first printing, a digits-normalised staleness warning,
and why re-sealing the baseline is not a fix: `references/exception-registers.md`.

Guards whose criterion is a **moving quantity** — N commits since the last rehearsal, a snapshot
older than N days — go red with nothing broken, and in a shared repository they block every writer
at once. The threshold is not the knob; the answer is the documented re-baseline:
`references/guards-that-age.md`.

When the *vocabulary* a guard counts changes (a tracker gains a state), every guard that
classified rows by `not <state>` or `total - n` becomes wrong without throwing, and
declared-count checks can quietly stop firing: `references/state-vocabulary-changes.md`.

A guard that already exists as an **advisory** — the detector is written and tested, but the
caller swallows the verdict with a `|| true` — is not rewritten: it is converted at the call
site, keeping the escape the detector already documents. Recipe, plus the tests that prove
the wiring rather than the detection: `references/advisory-to-enforcement.md`.

Guards whose subject is an export someone re-downloads (an ERP/GPS/carrier dump, «the newest
file in the download folder») have a third one: an assertion pinned to a vintage —
`700 < total < 800`, `len(sheets) == 5`, `abs(a - b) < 1 km` — passes the day it is written
and reds on a different period with a message naming the wrong defect. Assert the structure
(no aggregate row counted twice, one sheet per entity, totals one per entity) and skip with
the reason when the input's shape cannot support the measurement; the procedure, the
classification of a red as real finding vs stale premise, and the pitfalls are in the skill
`tests-over-changing-data-exports`.

Load this when the user says "make sure this never happens again", "can we check for
that", "add it to the checks", "this keeps drifting", "the rule says X but nobody
follows it", or after you have just found and fixed something that a written rule was
already supposed to prevent.

Also load it when a parser, reader or loader keeps producing **plausible-but-false output**: the
highest-yield guard for that class is a corruption harness — corrupt the input data, not the code,
and pin what the reader must do with each already-documented corruption. Recipe and rules in
`references/corruption-harness.md`.

## The premise

**A rule stated in prose is not a mechanism.** The failure this skill exists to prevent
repeats for a specific reason: the rule was already written down, everyone agreed with
it, and it still happened — because prose cannot fail. So the goal is never "make the
rule clearer" or "add a stronger warning". The goal is a command that exits non-zero.

Two consequences that shape everything below:

**A guard has a subject and a denominator, and both must be visible.** A check that found
nothing is indistinguishable from a check that looked at nothing. Every guard reports what
it inspected alongside what it found.

**And the subject is a perimeter, not a directory.** Almost every guard here is fed a file
list someone typed — a glob, a tuple of entry points, a root path. That list was chosen when
it was shorter, and two guards sharing a glob read as complete coverage from inside either
one. Measure the perimeter (what the guard walks) against the tree (what exists) before
trusting a green. See `references/guard-perimeter.md`.
- **The guard goes where the project already runs things.** A new standalone script that
  nobody invokes is not a guard; it is documentation with a shebang.

There are three outcomes of a check, not two: **pass**, **fail**, and **could not run**.
Collapsing the third into pass is the most common way a guard silently dies.

## "Does this need to compile?" / "can it run like a program?"

An analysis layer whose outputs are files does not compile, and does not need to; its build
step is the gate command. When asked to judge whether such a layer is a real program, **run
the project's own commands and quote their output** — the command list for the inventory, the
test collector for the count, the gate for the verdict — rather than describing the
repository from memory. The judge is the command that exits non-zero, plus whatever physical
guards the reader imposes (a legacy format's row ceiling, an undeclared entity, a missing
header) and the hook that enforces the read-only rule. And note the half that is usually
missing: a project that guards its **inputs** and not its **outputs** has no contract at all
for whoever consumes it, which is the failure the next section's reference closes.

**A gate with permanent, declared reds in it is not ready to feed a consumer, and building
the consumer first is the wrong order.** The reason is arithmetic, not taste: a gate that is
always red has no signal left, so nobody reads it, so the number the consumer displays came
from a check no one looked at. Measured: three checks red for reasons unrelated to any recent
diff, printed in exactly the same format as a fresh red — which cost the author real time
twice in one session just distinguishing "did I break this" from "this is always red".
So the order is: separate **new red** from **declared/known red** in the gate's own output —
this is usually the smallest change and it is what makes every other verdict actionable —
then close or declare the known reds, then point the consumer at the output.
The corollary cuts the other way too: state plainly that the consumer is waiting on
something real (a data-source defect the contract already measures, a resource ceiling, a
credential that must be rotated before anything is automated) rather than implying that the
missing piece is the dashboard. A consumer over data the gate is already reporting as
incomplete shows a wrong number convincingly.

## Procedure

1. **Write the test that reproduces the real defect first, and watch it fail.** Before the
   guard exists. It must fail for the right reason (the module is missing, or the assertion
   on the defect is wrong) — not from a typo. This is the same RED step as any TDD cycle,
   and it is what proves the guard can detect the thing at all.
2. **Make the test's subject synthetic and its expected value injected.** The guard reads
   a tree and compares against a value someone else computes. Give it two parameters — a
   root path and the measured value — so the test builds a tiny fake tree with the defect
   and passes the value in directly. A guard whose only test runs against the live repo
   goes red whenever an unrelated number moves, and gets disabled. **If the guard walks the
   filesystem, its root is a parameter too, and the test must never reach the real
   machine**: resolve the root to `None` (or a sentinel) when the process is not the real
   repository, so a fixture running under `tmp_path` cannot scan the user's home or
   Desktop. Measured: a guard that walked an enclosing directory re-read gigabytes of
   unrelated archives on the developer's machine on every test run — slow,
   non-deterministic, and reading third-party data for no reason.
   **When the guard's perimeter comes from a query rather than a path — a version-control
   listing, a registry, a remote index — the test injects the query's *result* and never
   runs the query.** Mutating shared repository state to make a subject appear (`git add -N`
   then `git reset` around the assertion) races the very commit that is assembling the suite
   when the guard's test runs inside a commit hook: measured, a test green alone and green on
   the shard it was written for, red **only** in the pre-commit, where parallel workers and
   the running `git commit` contend for the index. Stub the enumerator to return a list
   containing the phantom subject and assert on the finding; a test that fails only under the
   hook is testing the hook's concurrency, not the guard.
3. **Register it in the project's existing gate.** Find the registry (the check list, the
   test target, the lint config, the hook) and add an entry. Reuse whatever the project
   already has for baselines, severity, and reporting; do not build a parallel runner.
4. **Classify severity honestly.** A check that does not invalidate a result is
   non-critical / warning. Making everything blocking is how a gate earns its reputation
   for false alarms and then gets bypassed. See the pitfall on false alarms.
5. **Make the message carry the denominator and the location.** `N inspected, M found`
   plus the file/line of each finding. The message is read most often on the green path,
   so it must also prove something was inspected. When the subject is a *service* rather than a
   file, add the **repair** as well: the command that brings it back and the artifact that says why
   it left — a red with no instruction is a complaint, and it gets routed to whoever reads it next.
6. **Prove it against the real tree**, and record the measurement (what it found, how many
   things it inspected). Then **flip the defect back** — or better, confirm the fixture
   test covers it — and watch it go red. A guard nobody has seen fail is unverified.
7. **Confirm it is wired to the loop that actually runs.** If the project has a
   pre-commit hook, that hook is the enforcement; a check registered but not invoked is
   inert. Verify by running the gate command and seeing your check in the output.
8. **Only now write the rule in the repo's rule file**, pointing at the check. Rule first
   is the trap: the rule already existed and did not work.
9. **Commit the guard, its test, and the registration as one unit.** Adding a check can
   change the gate's recorded baseline — expect to re-seal it deliberately and say so,
   since re-sealing to silence an unexplained red is a different act from recording a new
   known state.

### The baseline the guard is compared against has to cover the guard's own registry

A regression baseline stores one entry per check, and its comparison rule is almost always
"a check the baseline does not know starts from the best verdict". That default is correct
for detecting a *new* red — and it is exactly why **the commit that adds a check cannot
pass its own gate**: the check has no baseline entry, so it is compared against pass, and a
new non-critical red blocks the author who introduced it. The rule: when a check is added,
its baseline entry is added in the same unit, and the sealing routine **warns when the
baseline is missing an entry for any registered check** rather than sealing silently. **Whether declaring a red is enough for a check the baseline has never seen is a property of the
comparator, not of the artifacts — read it before choosing.** The registry of declared reds and the
baseline of verdicts are two artifacts, and the regression comparison reads the second, so the default
is that a red declared with its motive still exits non-zero, reported as `(not present) -> FAIL` under
"regressions", because the check has no verdict entry to compare against. Many comparators carry the
explicit carve-out for exactly this case — a name in the declared register overrides the missing
baseline entry with the worst verdict it tolerates — and there **declaring is both sufficient and
preferable to sealing**, because the seal absorbs every other unreviewed red in the same run while the
declaration costs one visible line carrying its motive. Read the comparison function, then confirm by
the gate's **exit code** and its own "no regressions" line rather than by the summary, since a
non-critical red on its own does not set the exit code. Write
that warning into the baseline file itself (a `faltan: [...]` field), so it is visible to
whoever reads the artifact next and not only in the terminal that sealed it. Two adjacent
rules that keep a baseline honest: sealing must **merge** rather than rewrite (a seal run
with a filter leaves every unfiltered check unknown, which converts declared reds into
fresh ones), and a stale entry that no longer maps to a registered check is **inert, not a
failure** — surface it, never let it fail the gate.
**Merge every section of the artifact, not only the one the routine was written for.** A
baseline commonly stores two things — the per-check verdicts and a register of declared reds
with their motives — and a seal that merges the first while rebuilding the file from scratch
drops the second in silence. The damage is exactly what the register existed to prevent: the
declared reds come back looking like fresh ones. The tell is a commit whose message asserts the
state its own code just destroyed ("N reds remain declared", written by a routine that dropped
them, with the suite still green because the register's own assertions are keyed to entries
that no longer exist). Read the seal routine before trusting a seal, and after any reseal
confirm the register still carries its entries: a section the writer does not mention is a
section it is rewriting.

**And the baseline's path must be the tree you are actually working in, or the seal and the
comparison disagree by construction.** A gate that resolves its baseline through a
project-wide "root" setting shared by every worktree (a config constant pointing at the
integration checkout) reads and **writes** the wrong tree the moment you work from a linked
checkout: the seal lands in the other tree, and the very next comparison there re-reads the
old file and reports `(not present) -> FAIL` for a check you just sealed. Measured, and it
cost two rounds of confused debugging. Resolve repository artifacts from the **module's own
location** (`Path(__file__).resolve().parents[N]`) and reserve the configured root for the three roles it genuinely has: things that
describe shared machine state (the backup directory, whether an installed hook exists), data that
by design lives only there, and **the identity question — which tree am I in**. A guard that must
decide whether it can measure compares its own location against the configured integration root,
and that comparison *is* the question being asked — it is correct where it stands, not a missed
extraction, and it should say so in a comment so the next reader does not "fix" it into a guard
that measures the wrong tree. The tell: the configured root appears on one side of a comparison
whose *result* is a verdict about the guard itself (measure / skip), never on one side of a path
being opened for writing. It is worse than a read-only guard with the same bug because the artifact is
versioned: a session in a worktree can seal — or appear to seal — the state of a tree that is
not the one it is about to commit. When you audit a gate for this, remember the writer: the
seal step is a second call site and easy to miss when you only grep the comparison.


## Cuándo NO aplicarla

Si el pedido es una pregunta puntual de código (renombrar, qué hace una función, una sintaxis), se responde **solo eso**, sin agregar una guarda, un test ni un chequeo de perímetro que nadie pidió: esta skill aplica cuando una regla ya escrita sigue rompiéndose, o cuando hay que convertir un defecto recién arreglado en un check que falle el build.

## Pitfalls

El catálogo medido de formas de fallo vive en `references/pitfalls.md`. Cargalo cuando una guarda sale roja por un motivo sorprendente, al elegir severidad, o antes de convertir un chequeo advisory. El cuerpo de esta skill se queda con el procedimiento.

## Verification

A guard is done when all five hold:

1. Its test failed first, for the right reason, before the guard existed.
2. The fixture test builds a synthetic subject and injects the value, so it does not
   depend on the live tree.
3. Pointed at an empty or subject-less tree, the guard is **red** — the vacuous path is
   closed.
4. Run against the real project, it reports a denominator and is green only because the
   denominator is non-zero.
5. The project's own gate command lists it, and the gate exits non-zero when the guard
   fails.

## Reading a mature gate as a contributor: prove *no regression*, never *all green*

Once a gate carries permanent, declared reds, "everything passed" is not the pass condition — a
contributor proves **no new red**, and the two are different questions. The check is a set
comparison, not a verdict: collect the gate's `FAIL` names from this run and compare them against
the sealed baseline's `FAIL` set. Identical sets means nothing you touched regressed; a name you
did not touch and that the baseline already carries is not yours to fix, and treating it as a
blocker sends you editing code you were not there to change. Two details that make the comparison
honest: **a check added in this run has no baseline entry** — it reads as new, so its green is
evidence that it ran and passed, not that it was already known good; and a gate that can be run
as a **subset by name** must be read that way, or the subset's own absence of the other checks
looks like a change in their state. Where the full gate outruns the caller's time limit, the
verdict still has to come from the real run — background it and read the summary line from its
captured output, rather than substituting a green from the checks you could be bothered to run.

**A red that is not yours still blocks you, and the procedure is evidence first, escape second.**
When the gate's slow step is keyed to what the commit touches (a test step that only runs when the
change includes code), a trunk that is red for someone else's file blocks **every** code commit on
the tree while a documentation-only commit sails through — so the first thing to read is whether the
step ran at all. Prove the red is foreign before spending anything: run the failing subject by itself
with the file untouched and confirm the same failure, and confirm the failing file is not in your
diff. Then use the escape the hook itself documents for that one step (an environment variable the
hook reads to skip it, never a global hook bypass) and **write the blockade into the commit
message** — the subject, what it uses that does not exist, and the command that established it was
not yours — so the skip leaves a trail instead of reading like a clean run. A per-step escape whose
reason is mandatory is the design that makes this possible; a hook with no escape turns one foreign
red into an outage for every committer, which is why an unfixable-permanent red is the thing to
remove rather than live with.

**Confirm the run used the project's own invocation before reading its reds as regressions.** A gate
invoked through an interpreter that lacks the project's declared dependencies reports every check that
reads data as red — all of them failing at *import*, in checks that share nothing else — which reads as
a wall of fresh reds on a tree nobody measured, and the reflex is to hunt a defect that is not there.
The tell is that the failures are import errors rather than findings; the repair is the project's
documented way in (its wrapper, its `make` target, its declared environment), never an edit to the
baseline.

## Support files

- `references/pitfalls.md` — catálogo de formas de fallo medidas. Cargar cuando una guarda sale roja por un motivo sorprendente.
- `references/vacuous-green-detection.md` — auditing an existing check set for passes that
  prove nothing: the empty-subject probe, the error-into-pass path, and the denominator
  question, with the commands to reproduce each.
- `references/guard-implementations.md` — working reference implementations for the two
  recurring shapes: a static probe over source (AST) and a comparator over prose against a
  measured value, including the exemption-window technique and its tests.
- `references/changing-existing-guards.md` — changing a guard that already exists and
  already has tests: the pre-flight that stops a "cleanup" from deleting protection, the
  classification of widen/narrow/split/retire, the recipe for retrofitting a declared/known
  state onto it, and how to re-derive a red whose reported cause is disputed.
- `references/guard-perimeter.md` — measuring what a check actually walks: the
  should-be-vs-actual diff over the tree, the assertion that keeps an exclusion from
  re-narrowing, ranking a tree by churn to find the file a guard forgot to audit, how to
  scope exemptions so they do not blind the check where the problem was, and the ignore
    file as a third perimeter input — an exclusion written by a tool silently shrinks every
    scanner that respects it.
- `references/declaration-contract-guards.md` — guards whose expected value is a **declaration
  you wrote about your own published artifacts**: the output contract that keeps a downstream
  consumer (BI, dashboard, spreadsheet) from reading your tables by position; shape findings
  before value findings; "an artifact nobody declared" as a finding; measuring the whole corpus
  before writing the declaration (variants that share a name, comma decimals, scientific
  notation, formatted percentages, headerless series, BOM/EOL).
- `references/data-aggregation-guards.md` — guards whose subject is the contents of a dataset:
  the perimeter as the project's own export/workbook split, the enumerated vocabulary of
  *meaningful* magnitudes (and why identifiers and unnamed phantom columns must be excluded),
  the content-hash short-circuit that makes a minutes-long pass affordable, and reproducing an
  independently measured figure as proof it measures the right quantity.
- `references/mechanizing-a-step.md` — the sibling of a check: turning a manual step a person
  keeps skipping into a command. Refuse-by-default design, the three states the prose collapsed
  into one phrase, opt-in flags over heuristics, irreversible-after-reversible ordering, the
  blind spot the tool must declare, and how to prove a destructive command safe by testing every
  refusal branch plus the one action.
- `references/tiered-gates.md` — a gate whose slowest step is paid on every commit: splitting it into
  a level selected from the change (computed off the import graph, never a hand-kept table) plus a
  mandatory full level at the irreversible boundary, the loud fallback when the selector cannot decide,
  the drift guard that proves the selector still covers the tree, and the measured figure that keeps
  the levels from being simplified away.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/designing-mechanical-guards`). Editar acá, nunca la copia instalada.
