# Tiered gates: making a gate affordable without narrowing what it guards

**Load this when** the project's gate is expensive enough that people work around it: the full suite,
scan or aggregation runs on every commit and the measured cost is minutes. The failure mode is not
"someone forgot" — it is that an expensive gate gets switched off (`--no-verify`, a skip variable, a
habit of committing with the step disabled) and the bypass takes the gate's real signal with it.

**The repair is levels, never a narrower subject.** Shrinking what the slow step *reads* reopens the
hole the guard exists to close (see SKILL.md: make a whole-dataset guard affordable by reusing a
measurement keyed on the input's content hash, not by reading less). A level is different: the slow
step still runs, later, at a boundary where the work becomes irreversible.

## The shape

- **Level 1 — at the cheap, frequent boundary (a commit).** The subjects *this change* can affect,
  plus a short always-on list of the checks that guard the gate itself and the artifact that leaves
  the building.
- **Level N — at the irreversible boundary (a push, a publish, a merge).** Everything, once, and it is
  the default there: no opt-out flag a hurried session can reach for.
- **The selector is computed from the change, never a hand-written table.** Parse the import graph —
  for each changed source module, the test files that import it. A hand-kept map drifts and nobody
  notices; the imports are current because they are what executes. Measure the mapping once and write
  the number down: how many test files resolve to a module, and how many resolve to none (measured on a
  repo of ~170 test files: all of them resolved to at least one module, so the "declared, not inferred"
  list started empty — and the drift guard below is what keeps it empty or makes the gap visible).
- **The always-on list is short and justified one line each** — the gate's own checks, the register of
  declared exceptions, the code paths that produce the delivered artifact. A long list runs everything
  and saves nothing.

## The loud fallback: the three outcomes again, one level up

A selector has the same third outcome a check has: **pass, fail, could not select.** Collapsing it into
"select something" is how a level silently stops covering the tree. Fall back to the full set, and say
so in the gate's own output, when:

- the change touches the gate's own infrastructure — the hook, the suite's `conftest`, the runner, the
  dependency manifest, the lint config. A gate does not get to judge itself cheaply;
- the change touches a module **no test imports**: there is nothing to select from;
- the selection came out empty.

Print the reason beside the level actually run. A label that says "level 1" while the full set ran is a
small lie in the gate's own output, and that output is the only thing the next reader sees.

## The drift guard: a test that proves the selector covers the tree

The selector is a guard, so it gets a guard, with the same discipline as any other check:

- every subject of the slow step (every test file) is either reachable through the selector's map or
  listed as explicitly declared — a new file in neither fails the guard, so its author either declares
  it or makes it import what it tests;
- every declared path still exists;
- each fallback case above really falls back;
- **a change to code does NOT take the full set** — the property the level exists for, asserted, or a
  future edit "simplifying" the selector back to everything passes unnoticed;
- the selection is never empty.

## Report, measure, record

- The gate prints which level ran and how many subjects it selected, over the denominator of the whole
  tree.
- **Measure both levels before declaring a budget.** A proposed ceiling ("level 1 under 90 s") is a
  wish until a run produces the number; then write the measured figure into the gate's own comment,
  because that comment is what stops the next reader from simplifying the levels away. Calibration from
  one real split: level 1 = 340 tests in ~60 s, level N = ~3,000 tests in 300–470 s — the level-1 budget
  held with margin, and the level's value is exactly that ratio.
- The commit that installs the levels proves the fallback end to end: it touches the gate's own
  infrastructure, so it must take the full set. If it does not, the fallback is broken.

## Inside one step: the cheap rejection goes before the expensive work

The same ordering applies inside a single check. If there is a cheap way to decide that a subject is
going to be rejected, it runs **before** the costly pass over that subject, never after it. Measured in
the origin project: an export reader parsed each file completely and only then asked whether it was
truncated; one rejected file cost 42% of the gate's parse time, while the cheap test (count rows
against the format's ceiling, about a thousand times faster) already existed. Swapping the order took
the gate from 71 s to about 38 s. Pin the order with a test that fails if the expensive call happens
on a subject the cheap test rejects, or the next refactor puts it back. The same shape gives a hook its
fast path: keyword scan first, full analysis only when a keyword appears.

## Do not adopt a third-party selection tool when the import graph gives the same cut

Record the measurement, not the tool's reputation: how long since its last release, whether its
selection model conflicts with the parallelism the project already uses (a per-test dependency tracker
against file-level sharding), and whether the cut it offers beats the fraction the import graph already
gives. Prefer the mechanism with no dependency to keep alive, and write down what you rejected and why,
so the next session does not re-propose it.
