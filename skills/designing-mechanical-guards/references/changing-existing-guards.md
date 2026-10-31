# Changing a guard that already exists
## Contents

- See headings below. Load this file when SKILL.md points here.


Adding a guard is the easy half. Most damage happens when an existing check is *edited* —
narrowed because its subject got noisy, re-scoped because the tree moved, split, or retired.
Every one of those is a change to a contract that something else already depends on.

## Pre-flight: before touching a guard, find what depends on it

Run all four; they are cheap and each has caught a real regression.

1. **Grep the test tree for the property, not the function.** Search for the *behaviour* the
   branch enforces (the noun it requires, the phrase in its failure message), not for the
   test's own name. A test whose name does not mention your branch may still assert it
   through a fixture.
2. **Run the guard's own test class against the proposed change**, before committing, with
   the change applied in the working tree. `pytest <file> -k <TheClass>` is usually enough.
   The expected outcome of a *good* refactor here is that every test still passes; anything
   red is either a test that must be rewritten deliberately or protection you are deleting.
3. **Ask what case the existing branch was added for.** A guard branch that looks like noise
   ("why is this demanding a file be listed somewhere?") usually has a real case behind it.
   The docstring or the test that exercises it is the record. If neither exists, that absence
   is itself the finding.
4. **Check the denominator, not just the outcome.** A narrower subject makes the check
   greener and quieter; print what it inspected before and after. A guard whose green now
   covers half the tree is worse than the noisy version, because it still reports safety.

## Classify the change before writing it

| Intent | What it means | What it costs |
|---|---|---|
| **Widen** | the subject grows to cover a tree the guard should already have covered | re-measure the perimeter; widen the *measurement* together with the matcher, or aligned values start reading as findings |
| **Narrow** | remove a subset of the subject because it is noisy | this is **deleting protection**; it needs a replacement obligation or an explicit declaration, plus the pre-flight above |
| **Split** | one check enforces two unrelated properties | each half needs its own denominator and its own vacuous-green probe; the split is worth it exactly when the two have different failure severities |
| **Retire** | the subject no longer exists | the check must still fail loudly if the subject reappears, or state in its message that it measured nothing |

## Narrowing: separate membership from presence

The specific narrowing that comes up most: a guard requires every *emitted artifact* to be
listed in an index, and the artifact count grows until the requirement is unbearable.

The fix is almost never "stop checking". It is to split the obligation:

- **Membership** is for things a human asserts — a document someone wrote, which should be
  linked in the commit that adds it. This can stay blocking.
- **Presence / citation** is for things a process emits — a report, an export, a table. The
  durable obligation is that an artifact *cited by a document exists*, plus that the output
  area is non-empty (so the check is not vacuously green).

When you narrow a guard this way, keep the branch that verifies cited artifacts exist — that
is the part with a real failure mode — and delete only the inventory requirement.

## Retrofitting a declared/known state onto a gate that is already red

The most common edit of this class: the gate has permanent reds and nobody can tell a new
one from an old one, so the first change is to teach it the difference. It is an **additive**
edit — no existing check changes verdict — and it still goes wrong in four predictable ways.

**1. Partition every finding, not the blocking subset.** A gate normally has a second
predicate deciding whether a red *stops the run* (criticality, severity, a threshold). Do not
reuse it to decide what is *new*. Measure it: in the repo where this was done, all three
permanent reds were non-blocking, so a partition filtered by the blocking flag classified
none of them and the feature was invisible in the output while present in the code.

**2. A declared state needs a writer, and the writer is a second call site.** The classifier
reads a record; something must produce it. Adding only the reader leaves the operator with no
legitimate way to declare anything, and the pressure then lands on the exclusion list instead.
Ship both in the same unit, and give the writer one command per subject
(`<gate> <check> --declare "<motive>"`) — never a hand-edited file, which loses the audit trail
that is the whole point.

**3. Refuse a declaration without its motive.** A declaration whose reason is optional is a
mute. Make both arguments required, and strip the motive from the positional list *before* that
list is interpreted as subject names, or the motive's words get read as check names and the
call fails while looking handled. Keep the motive in the record, with its date, and print it in
the gate's output — a declared red whose reason only lives in JSON is indistinguishable from a
silenced one to everyone who reads the terminal.

**4. A declaration step is a second seal, so it inherits every rule the seal obeys — and gets
its own assertion.** The merge-not-rewrite and inert-not-failure rules for baselines (SKILL.md,
"the baseline the guard is compared against") apply here unchanged, because declaring a red
rewrites the same record. What is specific to this edit is the proof: after declaring, assert
that the record's timestamp, its registered-check count and its declaration set are all still
intact. Measured: the check that mattered was the one nobody thought to re-run.

**And when the gate's record is written through a project-wide root, this edit is where that
bug becomes a versioned write.** A seal resolves the record's path; if that path points at the
integration checkout, declaring a red writes the *other* tree's artifact and the next comparison
there disagrees with what you just did. Resolve through the module's own location. Measured in
the same edit: the declaration landed in the integration tree, not the branch under work; revert
it before anything else, then fix the resolver.

**5. The recorded motive is a snapshot, and printing it alone states yesterday's measurement as
today's state.** The motive is prose a person wrote at declaration time, and it normally quotes the
number that was red then. As the tree moves the check's live message and the motive's figure
diverge, and the gate prints two lines that disagree — the live one in the check list, the frozen
one under `declared`, which is the one readers trust because it carries a reason. Measured: a
declared red's motive named five subjects and four of them had closed *before* the motive was
written, while the check measured one; a validation written the same day copied the motive's
figure and passed it on. So the block prints **the live message first, then the recorded motive
with its date**, and says when they diverge. Three pieces make that possible, and they ship
together:

- the writer stores **the message the check produced at declaration time**, because a
  human-typed motive has no diff basis and can never be checked for staleness;
- the comparison **normalizes the volatile parts** — digit runs, and any counter that moves on its
  own (days elapsed, population size) — or the divergence warning fires every run and is ignored,
  which is the false-alarm pitfall one level up; say in the guard which parts are normalized,
  since that is exactly its blind spot;
- refreshing a stale motive is **not re-sealing the baseline**: it rewrites one line and keeps
  that red visible, while a seal absorbs every other unreviewed red in the same run.

Two edges. A test for the block must slice the output **from the block's own header** before
asserting — a console-output test that searches the whole transcript goes green on the check
list's line without ever touching the declared block (measured: the assertion meant to prove the
fix passed against the unfixed code). And when the motive's number moves because the *population*
moved, the prose around it is stale too — the register's own motive, every document that quoted
it, the sentence in a skill describing what the red means — so sweep them in the same change: a
frozen figure outlives the reason it was frozen.

## Re-deriving a red whose reported cause is disputed

A red that is no longer reproducible, with a cause asserted in prose, is a hypothesis. Before
acting on the fix the prose implies, reconstruct the revision that produced it and run the
check against that tree:

```bash
R=$(git rev-parse <rev>)
T=$(mktemp -d)
for f in $(git ls-tree -r --name-only $R | grep -E '\.(md|csv)$'); do
  mkdir -p "$T/$(dirname $f)" && git show "$R:$f" > "$T/$f"
}
done
```

Then point the checker at `T`. Two outcomes worth distinguishing:

- It goes red for the asserted cause — the hypothesis holds; fix that.
- It goes red for a **different** reason, or goes green — the asserted cause was fitted to the
  symptom. The most common real finding is that the check was *correct*: it flagged a
  legitimate in-flight state (another writer had added an artifact and not yet linked it),
  and the "defect" was just timing. That converts the action from "weaken the guard" to
  "nothing to do here".

The same reconstruction is the cheapest way to answer "was this ever red for the reason
someone says it was", so reach for it whenever a plan, a commit message or a rule file
attributes a failure to a mechanism you cannot currently observe.

