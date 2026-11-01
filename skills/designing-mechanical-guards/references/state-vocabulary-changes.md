# Changing the vocabulary of a tracked state

Trigger: a tracker gains a state (`convertida`, `draft`, `void`, `converted`, `superseded`),
or you are tempted to reuse an existing state to mean something new. Every guard and count
that classified rows by *negation* or *subtraction* silently becomes wrong at that moment,
and it stays wrong without throwing: the damage lands in a reported number, not in an
exception.

## Audit every `not <state>` and every `total - n`

`closed` inferred as `not open`, or `decided` inferred as `total - open`, is a two-bucket
model. A third state that is neither enters every "closed" bucket. Before adding the value:

- grep the domain module AND the checks for the state literal, for `not `, and for
  `len(...) -`, `total -`.
- replace each hit with an explicit membership test against a named tuple
  (`ESTADOS_CERRADOS`, `OPEN_STATES`), defined once in the domain module.
- delete local copies of that tuple in check modules and import the canonical one; a copy is
  the exact place the new value gets forgotten.

Symptom that tells you the defect is present: the denominator of a rate moves when nothing
was decided, or a history scan dates closures that never happened (a scan for "when did the
state leave the open set" matches *any* non-open value, so a conversion gets dated as a
closure).

## Declared-count checks: parse with formatting stripped, compare per bucket

A reading layer declares its own totals (`**12 abiertas · 24 decididas · 7 convertidas**`) and
a guard compares them against the source rows.

- Run the regex over `texto.replace("**", "")`. Otherwise bold placement (one run vs three)
decides whether the guard fires, and a valid line reads as "does not declare its counts" —
which turns the check off instead of red. An accidentally-disabled guard is the worst outcome
of a vocabulary change.
- Keep the new bucket optional in the pattern and default it to 0, so an older declaration
still parses; let the *comparison* go red when reality has rows the declaration omits.
- Never infer the new bucket by subtraction. Declare it and compare it.

## Converting rows without lying

When the honest answer is "this row was never of this type":

- Change the state and write the reason in the body **in the same edit**. A row whose state
  moved with no explanation reads as closed-without-result — worse than leaving it open.
- Keep the fields that record what was believed (the hypothesis, the expected metric). A
  conversion is about the queue, not about erasing the record.
- Conversion is not closure: it must not enter the closure denominator and must not date a
  closure.
- Do not push such rows into an auto-generated ledger whose types are a closed list: each new
  type demands a generator to justify it, and a handful of one-off items do not. The source
  note already carries owner, trigger and closing condition.
- Make the classification auditable one row at a time: each conversion cites the row's own
  words saying it was not a decision. A revert is then a one-line edit, not an argument.

## Pin the distinction with the hard fixture

Write the test with a converted row that STILL carries a hypothesis and an expected metric.
With a bare converted row, `not open` and `in CERRADOS` agree, the test passes green over the
live defect, and you ship it. Assert both the closure count and the "still pending" count.
