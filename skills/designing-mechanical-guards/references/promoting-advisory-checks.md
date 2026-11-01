# Promoting an advisory check to blocking

The phase after a guard exists: it starts in shadow (records, does not block) and the day comes
to decide whether it may stop work — plus what to do when its own log says it is measuring the
wrong thing.

## Decide from the log, by family

1. **Snapshot with a cutoff, not a live read.** A live check's log is being appended by every
   running session: two reads minutes apart give different totals (measured: 13 of one family,
   then 15 two minutes later). Take one read, write down the row count, the last timestamp and
   the count per `code`, and cite that snapshot in the write-up.
2. **Count per family and per closure.** A total like "16 avisos" says nothing; what matters is
   how many closures carried an aviso and how much each family contributed. One family owning
   most of the volume is the norm, not an accident.
3. **Ask of each family: does it describe how the unit of work closed, or the state of something
   else?** A family that fires on a *normal* end state can never be a block criterion. The
   canonical case: "uncommitted changes in the integration tree" fires on every turn that answers
   without committing, which is legitimate work — and the rule it cites is already enforced,
   harder, by the commit guard at the moment it matters.

## Reclassify, don't delete

- **Keep recording what may not block.** Mark the aviso non-blocking and filter it in the decision
  function; leave the recorder alone. Deleting the check loses the only evidence that the state
  existed.
- **Separate the two paths explicitly:** `evaluate()` returns everything, `decide()` filters
  through a helper that defaults to blocking when the flag is absent. Build the test fixtures from
  `evaluate()` — a dict hand-written in the test that forgets the flag asserts the fixture, not
  the code.
- **The block message must name only blocking families.** If the reason string lists everything,
  the agent is asked to fix something the gate will not enforce on the next attempt.

## When the hits are not what the family claims

- **Open the flagged lines before writing the fix.** The count says a family is noisy; only the
  lines say why. Measured: 6 of 7 "figures without validation" hits were a test literal
  (`assert "... 1 (50%)"`), a format spec (`f"{rate:.1%}"`), an API example and a sample table in
  backticks — code, not data.
- **Fix the criterion, not the path.** A detector that matches code should learn to skip fenced
  blocks and inline code; exempting a directory hides the real cases inside that directory. The
  hit left after narrowing was prose naming a `0%` in order to negate it — the correct residue:
  telling a negation from a claim needs reading.
- **Grep the tests for the aviso's identifier before reclassifying it.** A test may be using that
  aviso as a convenient vehicle for an unrelated property — an "output is pure ASCII" test that
  triggered it because its detail happened to carry accents. It breaks when the aviso stops
  blocking; re-point it at another blocking family whose message carries the property, and say in
  the test why.

## Don't promote while the rate includes noise

A rate computed with a family that cannot block inside it is not a rate. After the fix, recompute
what remains per closure and report *that*. If what remains is small and young (tens of closures
over a couple of days), say so and keep collecting: turning a gate on is cheap, turning off one
that blocks honest work is not.

## A new rule over an old corpus: enforce from a cutoff date

A rule that is promoted to blocking over a corpus that predates it (plans, decisions, validation
notes) is born red over everything already written, and the usual response is to weaken it until it
passes. Measured in the origin project: a "how this can fail → control" section that the prose had
asked for was present in 1 of 29 plans, while decisions, which had a check, carried theirs in 42 of
42. Enforce the rule on documents dated on or after the cutoff, keep the older ones as a reported
count (not a block), and write the cutoff into the check's docstring with the measured figure, so the
date is not moved forward later to make a new red disappear.

## Write the boundary next to the code

The module docstring should say, per family, what it detects, whether it may block, and the
measurement that settled it (snapshot time, counts, reference to the validation). That sentence is
what stops the next session from re-litigating a decision that was already paid for.
