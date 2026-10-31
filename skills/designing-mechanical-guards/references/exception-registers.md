# Exception registers: checks that are allowed to stay red

A gate that can carry an accepted exception (a declared red, a waiver, a known-failure, an
`--ignore` list) turns its register into a second source of truth. It rots in one specific way: the
text explaining the exception is written once, at acceptance, and every later run prints it as
though it described today.

## Two fields, not one

- Store the human reason (`motivo`, `waiver_reason`) **and** the machine snapshot of what the check
  measured when it was accepted (`mensaje_al_declarar`, `observed_at_accept`). The reason answers
  *why we live with it*; the snapshot answers *what it said then*, and it is the only thing that can
  detect the reason going stale.
- Take the snapshot from the verdict the check just produced, never from a hand-typed summary. A
  number typed into a reason decays silently; a number copied from the run can be compared.

## Print live first, sealed second

- Per exception: name and **live** verdict/message, then the sealed reason labelled with its date. A
  register that prints only the sealed text is read as current state even when the live verdict sits
  one screen above — readers stop at the block that has the word "declared" in it.
- Say whose text is whose: `declarado el <date>: <reason>`. Without the label the two messages read
  as a contradiction instead of as history.

## Warn on staleness without crying wolf

- Compare snapshot to live message with digits normalised (`re.sub(r"\d+", "#", s)`) before
  flagging. Counters that move by themselves — days late, rows pending, files not yet arrived —
  fire the warning every day, and a warning that is always on gets filtered out by the reader.
- Declare the blind spot where the code lives: a change of *counts only*, same subjects, does not
  fire; a changed subject list does. A blind spot that is written down is a design; an undeclared one
  is a trap.
- Keep the staleness line **advisory**. Making it fatal turns a reading warning into a work stoppage
  on something the reader cannot fix from the tool.

## Exit conditions, expiry, ownership

- Every exception carries an exit condition ("closes when X writes Y") and a review date. Fail the
  gate when the review is older than the stated window: an exception waiting on an event that may
  never happen is permanent without that clock.
- **Check that the named action can turn the verdict green before writing the condition.** Read the
  branch that produces the red. If its trigger is a *difference between two measurements* (one basis
  vs another, gross vs net, one reader vs another), then deciding which side is official changes
  nothing: the difference outlives the decision and the exit condition is unreachable. Do the
  arithmetic of the imagined post-decision run. An exception whose exit condition names an action
  that cannot flip the check is an unowned red wearing a reason — nobody picks it up because it
  cannot be finished, and a register of unfinishable reds teaches readers to skim the reds.
- When the verdict is unreachable by the named action, the entry is conflating two things: the
  **decision** (which number gets published, whose call it is) and the **check** (what invariant it
  claims to enforce). Send the decision to the decision log and repair the check to measure the
  invariant its own docstring states — typically "every published figure names its basis" rather
  than "the two bases agree". The repair needs no answering from the decision's owner.
- Do not invent an owner. Point at the decision, ticket, or plan that produced the exception; when the
  owner is unknown say unknown and name who must decide. Fabricated ownership is worse than an
  unassigned one — the next reader routes a question to someone who never had it.
- Report exceptions that are no longer failing instead of deleting them. The tool's job is to make
  retirement easy; the owner's job is to retire.

## Refreshing the accepted-state baseline is not a fix

- Re-sealing (`--seal`, `--update-baseline`, `--accept-current`) rewrites the reference verdicts; it
  does **not** rewrite reasons. An exception whose reason is wrong stays wrong after a seal — the
  two artefacts are different files or different fields, and only a declaration path touches the
  reason.
- Seal only when the **instrument** changed (new reader, new toolchain version, new upstream format),
  and only after the tool reports that it would absorb no undeclared red.
- If the comparison is verdict-level (`PASS < WARN < FAIL` ordering) and not numeric, say so out loud
  before treating "the baseline is old" as a defect: sealing then moves a date and nothing else.
- A new red is *declared*, not absorbed. "We'll seal it" when a check turns red is the failure this
  section exists to prevent.

## Tests that keep the register honest

1. The live message appears **inside** the exception block: assert on the slice after the block
   header, not on the whole command output. An earlier line already contains the live text and will
   let the test pass while the block still lies.
2. A changed subject list produces the staleness warning.
3. A changed counter alone does not.
4. An entry without a snapshot asserts nothing and does not crash the block.
5. Declaring through the CLI persists reason + snapshot, and re-declaring the same check replaces the
   snapshot instead of appending a second one.
