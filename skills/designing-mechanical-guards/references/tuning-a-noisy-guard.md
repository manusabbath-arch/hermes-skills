# Tuning a guard that runs but does not enforce

Rules for a guard, hook or detector that already exists, already logs, and is **not yet allowed to
block** (shadow mode) — from its first day through the decision to enforce it. Designing a new
guard is a different job; this file starts once the check is running and writing a log.

## 1. The decision to enforce comes from the guard's own log, counted

- Aggregate the log before deciding: how many events, how many produced an aviso, and the
  **distribution by code**. "N avisos" alone says nothing; the split says what to fix.
- Read the log **once** and note the cutoff row. A live guard appends while you read: two
  consecutive reads disagree, and the second one is not "the" measurement. The validation cites
  the cutoff, not "the log".
- If one code is the majority, the rate is measuring that code, not the guard. Fix the criterion
  before reading the rate as a false-positive estimate.

## 2. Split the avisos: how the turn ended vs the state of another tree

- An aviso about state the agent **cannot fix before answering** — uncommitted work in the
  integration tree, a dirty worktree, a stale export — must be **logged but not blocking**. Mark it
  explicitly (`bloqueante: False`) and filter on that mark in the decision function. Do not delete
  the check: the log has to keep showing the state.
- The rule it duplicates is usually already enforced elsewhere, at the moment it can be enforced
  (a commit-time guard that refuses to commit in the integration tree). When two guards cover one
  rule at different moments, the one that can act wins and the other only informs.
- Keep the informational mark out of the block reason. A block that names something the agent
  cannot resolve loops the turn.

## 3. A text detector must know code from prose

- A number inside a fenced block or between backticks is a literal, a format string, an example or
  a sample table — not a claim about data. Skip fenced regions (carrying the fence state across the
  lines you scan) and strip inline code spans before matching.
- Do not solve it by exempting a path (drafts, plans, notes): that also silences a real claim
  written in prose in the same file. Fix the criterion, not the route.
- Some prose still fools a regex (a number named in order to be denied: "published as unmeasurable,
  not as 0%"). Accept the residue and write it down; teaching a regex to read negation costs more
  than the aviso it silences.

## 4. A green that never ran the subject is not a green

- For a wrapper that shells out to a script, exit code 0 proves nothing: the wrapper can exit 0
  while its inner command failed (`error: File not found` on stderr) and the test then measures an
  empty run.
- Assert the inner effect — a line in the log the hook writes, the artifact it produces — or at
  minimum assert that stderr carries no `error`/`Traceback`.
- Prove the assertion by breaking the wrapper on purpose once: remove the fix, watch the test fail,
  restore. An assertion never seen red is a hypothesis.
- Corollary for path handling: a native binary does not resolve the shell's POSIX-style paths. Pass
  it the native form (`cygpath -m` on Windows) — the failure is quiet (`File not found` at exit 0)
  and lands exactly in the hole described above.

## 5. Verify enforcement behaviourally, never by reading config

- Config that names the hook does not prove it fires. Fire it the way the runtime does — a real
  turn, or the tool's own `test` subcommand with a synthetic payload — and read the output.
- For a guard that rewrites what the model reads (a tool-result transform), the only proof is a
  fresh session doing the write and the tool result carrying the message.
- Write down which steps are versioned in the repo and which are machine-local: a new clone
  repeats only the latter, and nobody remembers them.
