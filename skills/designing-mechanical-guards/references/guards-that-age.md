# Guards that go red on their own

## The shape

A guard whose criterion moves with the work instead of with a defect: *no more than N commits since
artifact X*, *the snapshot is younger than N days*, *the export was refreshed this month*. Nothing is
broken the day it turns red — the counter simply arrived. The check then reports a cadence condition
with the voice of a defect, and the three reflex responses are all wrong: widen N, refresh the seal,
Declare it as a red.

Typical subject: a restore/rehearsal proof tied to a backup bundle, a freshness check on a
catalog, a *the schema model is not older than* check. In every case the guard is the only thing
that makes anyone redo the maintenance, and the maintenance is the whole point.

## Why the threshold is not the knob

- **Widening N to get today's commit through buys exactly one commit** and removes the only signal
  that the maintenance happened. The repo's own convention is usually written down next to the
  constant (*do not touch the cadence; redo the thing*) — read it before editing a number.
- **Declaring it is legitimate only for reds nobody can act on** (an upstream that did not
  publish, a business decision waiting on its owner). A self-aged cadence red has an action, it is
  in the guard's message, and the action is the guard's purpose.
- **The blast radius is the repository, not the session.** If the gate compares against a sealed
  baseline (*this was PASS before*), a cadence red reads as a **regression** and blocks every write
  of every writer — so in a repo several agents share, one aged counter freezes everybody. That is
  the argument for re-baselining promptly and for doing it once, not per session.

## Procedure when it fires

1. **Read the criterion from the check's own message**, not from memory: it states the artifact it
   read, its age and the cadence.
2. **Check it is not already done or in flight** — the artifact's own date, `git log -1 -- <file>`,
   and the check run on its own (seconds). Two sessions re-baselining at once fight over the same
   artifact and pay the same hours twice.
3. **Re-baseline for real**, from the state the guard reads (usually the integration branch), with
   the procedure the repo documents for it — not an ad-hoc equivalent.
4. **Produce the evidence the guard's document declares** (front matter fields, digest, size, counts)
   and put it in the same change that would otherwise be blocked, so the gate turns green *in* that
   commit and the next session inherits the reason.
5. **Re-run the check alone** and confirm it is green without the constant having moved.

## The trap: re-baselining is a long run

The maintenance is usually the most expensive thing in the repo — a full suite, a restore, a rebuild.
Treat it as a long run: its own log, its own closing marker, launched detached. If the launching tool
call hits its cap, the child may be alive and writing — read the log and the process list before
concluding anything, and **do not relaunch**; a second copy competes with the first and a partial log
reads like a failure. (See `long-running-commands` for the mechanics.)

## Making it survivable

- **The re-baseline lives in the repo** — a make target or CLI subcommand with the recipe beside it,
  not in a person's head and not only in the current session's transcript.
- **The message carries the numbers**: which artifact, how old, which cadence, and what re-baselines it.
  A guard that says only *stale* makes the next session reproduce the diagnosis from zero.
- **Prefer a criterion with a stated exit over one that drifts silently.** A cadence guard is only
  acceptable when the maintenance it demands is documented and cheap to run on demand; if the
  maintenance takes half a day, the guard belongs in a scheduled job, not in the pre-commit of every
  writer.
