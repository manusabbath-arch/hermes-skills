---
name: recurring-report-design
description: "Use when designing a recurring daily or weekly report people actually read: every item names its consumer and denominator, rotation instead of accumulation, work-assignment blocks with a capped dose, and the heartbeat whose absence is the alarm."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [reporting, operations, curation, action-lists, rotation]
    category: productivity
    related_skills: [unattended-run-verification, grounded-citations]
---

# Recurring reports: designing and curating what people read on a schedule


## Cuándo NO aplicarla

Si el pedido es un informe de una sola vez, se responde **solo eso**. Esta skill aplica
cuando el artefacto **sale en una cadencia** y alguien lo lee todos los días o todas las semanas.

For a report that goes out on a cadence: a morning sheet printed and left on a desk, a weekly
message to a team, a dashboard someone opens every Monday. Its cost is not compute. It is the
attention it spends every day, and that cost is paid whether or not the content earns it. Scope:
which items belong, how the content rotates, and how an item is retired.

## Rules that apply to every item

1. **Every item names its consumer.** If you cannot say who reads it and what they do
   differently because of it, it does not go in. A report nobody has mentioned in weeks is a
   candidate for retiring, not for extending.
2. **Nothing enters without its denominator or its baseline — and a derived column's denominator
   is the one printed beside it, not the one the code used.** A total with nothing to compare
   it against cannot be read as good or bad; a count with no universe beside it says nothing. A
   row whose percentage is computed over a universe the page never shows is worse than one with no
   denominator: it invites the reader to divide the two figures it does show and reach a different
   number (measured: a rejection percentage taken over gross sales while the row printed net
   beside it — 5,62% on paper against 6,19% actual, in every row of the table). Put the base in its
   own column, or compute the percentage over what is printed, and name the base in the footnote.
3. **A number the system computes is produced by that system's own query.** Do not carry a
   figure into the report from an export snapshot of the same tables: the definition lives in
   the query and the file carries only rows from one moment.
4. **It is a decision surface, not a data dump.** One idea per page, and the reader should be
   able to act on a line without opening anything else.
5. **The period's total and the reader's working set are different sets: publish the residue by
   state, with its consequence.** A report counts records; the reader then prints, picks or calls
   from another system whose list filters by a **status** the report never mentions — so a residue
   sitting in the state that step skips is invisible on paper while the total reads complete.
   Measured here: a run reported 156 records for the closed period while four of them were still in
   the pending state, and those four were exactly the ones missing from the work list the reader had
   printed that morning ("they didn't show up on the list"); when the state moved, they entered the
   next list. Count the period **by state**, and when something is left sitting in the state the next
   step skips, print it as a named line with its consequence ("4 came in after the close and are still
   pending: they will not appear in the list until they are confirmed") — that line is the only part
   of the sheet that tells the reader what they are *not* going to see. The state is a live field, not
   a property of the period: it clears mid-morning (three of those four flipped between two runs 25
   minutes apart), so the line carries the hour it was read, like every live figure here.
6. **A comparison against the reader's own average counts only the periods that carry data, and a
   period with none prints that it has none.** "Below your average" over a week whose source loaded
   no activity is a verdict about a person built from missing data: it reads on paper as a bad week and
   there is nothing behind it. Take the denominator from the periods where the activity was actually
   registered — the days the route went out *and* the visits were loaded — print it beside the figure
   ("in 5 route days"), and when it is zero print "no visits loaded" with no comparison at all. It is
   the same discipline the report already owes a rate with nothing closed yet, applied to a ratio the
   reader will act on emotionally rather than arithmetically.

## Rotation: keep the budget constant

The design that holds up is **one fixed first page plus one rotating thematic page**. The first
page is "what changed and what to look at today", every day, never rotated, because rotating
the exceptions hides the actionable half. The second carries one theme per weekday, and it
**rotates rather than accumulates**, which is what stops the page count from growing every time
themes are added.

- **Measure the page count after every content change, on every rotating variant**, not only
  today's. A change that fits on Tuesday's sheet can push Friday's to three pages, and a page
  budget that only holds on the days you checked is not a budget.
- **When the PDF is one page more than the sections, the overflow is the footer, and the fix is the air.**
  A sheet whose content overshoots the paper by a few millimetres prints as one extra, nearly empty
  page: nothing in the markup looks wrong and the reader gets a sheet ending in a stray line (measured:
  the first page's content was 284,69 mm against 277 mm of usable A4 — 297 minus two 10 mm page
  margins — and the 7,69 mm that fell over were the 5,82 mm footer alone, so the second sheet carried
  two lines and the real second section landed on a third page). Measure each block's height in
  millimetres against the usable height and shrink the **air** between blocks before touching a font or
  a chart — the air is where the millimetres are. Two obligations ride on that fix: the slack it buys is
  single-digit millimetres, so a slightly longer day breaks again (state the slack in the code comment
  and the report's history, and prefer the smallest value that fixes every variant measured, not a round
  number), and a day whose section count is legitimately higher still prints more pages — that is
  content, not a defect, so count the sections before declaring one. Recipe, with the headless-browser
  height probe and the page counter: `references/print-layout-measurement.md`.
- **A theme whose data condition the business has not confirmed does not get built.** Leave the
  slot, name the gate, and wait for it. Filling the slot with the nearest available data prints a
  claim nobody agreed to, and an empty slot is a decision rather than a gap.
- **Keep every rendering on one formatter function** (paper, message, markdown). Two renderings
  written separately diverge, and the printed one is the one nobody diffs. Strip the
  markdown-only syntax (wiki links, escapes) on the way to paper.

## Blocks that assign work (a list someone has to go execute)

Some blocks are read; some are carried out — a count, a sweep, a round of calls. A block that
assigns work fails differently from one that only reports: if it cannot be executed it is not
partially useful, it is skipped whole.

- **Verify the grouping field is populated before grouping by it, and say which reading
  governs.** Grouping a work list by "section" only helps if the section is real and known to
  whoever has to walk it. The lookup catalog and the entity's own text disagree more often than
  not: measured, a category lookup table held **4 rows** while the product master carried **104
distinct categories** written on the entities themselves. Neither reading is wrong — they answer
different questions — so measure both (rows in the catalog, distinct populated values on the
entity, and the share with the field empty) and state which one the list is grouped by, because
grouping by a catalog nobody filled prints a heading nobody can walk to.
- **Size the list so one unit of work finishes it, and make the grouping that unit.** The
difference between a list that gets executed and one that gets looked at is size and order:
every line of a 278-item list is skipped, while "33 items, all of them one brand" is a shelf and
one shift. Group by what the work is physically organised by — shelf, aisle, supplier, route —
and print which group today covers **and how many remain in total**, so the reader can see the
list closing over days instead of restating it every morning.
- **When the backlog is hundreds of items, the block prints a capped dose, not the queue.** A sweep
that would take months at the cap leaves exactly one design question — which few go today — so the
cap and the sweep length are printed numbers ("3 a day × 5 = 15 a week; the 278 open items are 18-19
weeks"), and the dose takes **one item from each rung of the ladder** instead of the top N of one
ranking: a dose fed from a single class stops producing anything the day that class empties, while
the other classes keep losing money unattended. Never re-propose what is already pending somewhere
else (an action ledger, a ticket, last issue's sheet) — the repeat crowds out the new items — and
move what has waited past a threshold into a notice line **with the days it has waited**, so a stuck
item stays visible without occupying a slot. The order is fixed (priority, then a stable tie-break on
the key), never shuffled, so two runs of the same day print the same items and the rotation is
testable. And keep the two views apart: the daily dose is the action; the full queue with its
denominator belongs on the weekly view.
- **The report records the dose it printed, or the rotation resets every morning.** Reading the
ledger is half the rule; the other half is that the sheet itself writes the day's items into it, at
the end of the run, under the key the reader sees on paper — otherwise tomorrow proposes the same
few, because nothing changed about what is pending. That write is **state**, so it carries three
obligations: it is idempotent for the day (a second run of the same sheet must not duplicate the
items), a failure to write it never takes down the sheet (the report is the deliverable; the ledger
is bookkeeping), and the report's own tests never touch the real ledger — test suites commonly drive
the report's entry point directly, so guard the write in the code rather than remembering not to run
the tests.

  **Idempotent for the day is a property of the SELECTOR, and "exclude what is pending" does not give it
  to you.** The exclusion is what stops the sheet repeating yesterday's items; applied to today's it makes
  a second run of the same day **propose a fresh dose** — the retry, the manual re-run, the scheduled task
  firing twice — so the store grows to 2N while the sheet tells the reader N. The correct selector reads the
  ledger FIRST: today's own pending items *are* the dose and are re-printed as they are (it is the same
  sheet the person is holding), only `N - len(today)` new items are proposed, and the whole day is capped at
  N. What a day past the cap leaves over stays pending and is declared by the notice line rather than
dropped. A ledger whose records carry the reason code and the display name is also what lets that re-print
  happen from the ledger alone, without re-reading a source that may be unreachable — and a record written
  before those fields existed must fall back to its own stored text instead of printing `None`.
- **Each line carries the value the worker has to compare against: what the system currently says is there.**
Without it the sheet produces an observation instead of a correction. Print the comparison value,
and a reason code per line, so the expected difference already means something. **That value belongs
on the line only when the task is to CORRECT the record; when the task is to MEASURE it, printing it
turns the measurement into a copy.** Decide by what the block is for, because the two live on the same
sheet: a correction line (the worker is there to fix the record) prints what the system holds plus its
reason code, while a **count** line prints only what identifies the item — code, description, location,
and the id that closes the record — never the quantity being counted. A counter who reads `the system
says 240` beside the box counts toward 240, so the accuracy the block publishes afterwards measures how
well the number on the page was copied rather than what is on the shelf. The reference value still
travels, on the receiver's copy, keyed by the same id; and when one content is emitted twice (a copy
to read beside the copy to print), assert the required lines against **each** rendering, since a block
that exists for another purpose can swallow the line on one of them while the test covering the other
stays green. And **render that
value the way a person reads it** — normalize what the engine hands back before it reaches the page.
A decimal under 1 arrives from some SQL drivers without its leading zero (`.00`, `-.42`), so the printed line reads
as a typo in exactly the line the reader has to trust and act on; that is one string away from costing
the whole block its credibility. **The clock is the same defect in different punctuation**: a timestamp from the driver prints as `2026-10-14-16.30.17.000000`, so slicing out the hour yields `16.30.17` —
normalize the separators (and keep the seconds) before an hour reaches a sheet the reader trusts.
- **A block whose denominator is in dispute does not print.** When two cuts of the same class
disagree (two sources, two universes), hold the block until they reconcile and print the pending
work instead of picking one: a total with a doubtful denominator is worse than a missing block,
because the reader will average it with the other reading.

- **The block is half a mechanism until what came back is recorded and the report publishes the
  accuracy of what came back.** A list that assigns work and records that it printed the work is
  measurable in effort only: with no outcome there is no way to tell a program that works from one
  being ignored, and the daily dose becomes a ritual. So the closure carries a **value**, and the report
  publishes the rate — correct records over records inspected — taken from the established practice,
  cited, never invented: measured, the standard definition asked for three components (item + quantity +
  **location**) while the data held two, so the line states which shape it is measuring instead of
  implying the full one. It is **absolute**: a shortage and an overage are two wrong records, never one
  cancelling the other. Three edges, the same discipline the totals already get here: the rate **carries
  its denominator in the same sentence** ("of N inspected, A matched"), a closure that came back
  **without the value is declared and kept out of the denominator** instead of counted as a match, and
  with nothing closed yet the line says **it cannot be measured** — never `0%`, which the reader takes
  as "nothing is wrong". Until the first closure arrives, that sentence is the honest content of the
  line, and making the closure reachable by whoever holds the paper (a value's entry where the sheet's
  reader already is, not behind a tool only the report's author knows) is what turns it into a number —
  and the paper has to carry the record's **own id**, produced by the single function that writes the
  record: an entry box with no id is an answer nobody can attach to a record, and the day the id is
  computed twice (once to store, once to print) they diverge and the break shows up on paper.

See `references/work-assignment-blocks.md` for the ladder that picks the items and the periodic
dose that caps them.

## Withdrawing an item is the hard part, so do it on evidence

An instruction nobody can carry out does not fail loudly: it gets skipped, and a list the reader
has learned to skip takes the items that do matter with it. Decide on evidence, not taste:

- **The metric moved the wrong way while the item was printed.** An ask whose number got *worse*
  across days of printing it was never actionable. Measured here, a request that loaders fill a
  field rose from 84% to 94,4% unfilled over four days of printing it, after a reworded version
  had already been tried. Withdraw the ask.
- **The application writes the field, not a person.** If the value only appears when the system
  itself performs an action (a cancellation, a reversal), there is no human action to request.
- **The consumer says stop.** An explicit "stop asking for this" outranks the metric.

Then **remove the ask and keep the measurement**: the figure moves to an indicator with its
baseline, somewhere the reader already goes, so the situation stays visible without a daily
instruction nobody can follow. Write down why it left, in the report's own history *and* in the
document that proposed it, or the next session re-adds it.

## Editing a report safely

- **Test the withdrawal like any other change: assert the absence.** A test that the withdrawn
  line no longer appears is what stops it coming back in a refactor, and it doubles as proof that
  every rendering of it is gone.
- **Sweep the whole text for the phrase, not just the function.** One instruction usually lives
  in three strings: the markdown row, the HTML row, and the alert computed above them.
- **Audit the rendered artifact against itself, not the code that built it.** For each table,
  recompute the derived column from the numbers that row prints, and cross the list below against
  the summary that cites it (row count and sum). The gate tests the code and nothing tests the
  page, so a report can be green and not reproducible on paper. Keep the auditor as a small script
  that takes the artifact path and exits non-zero on findings — it can live in the versioned repo
  even when the artifact cannot (it reads a path; it carries no names) — and keep the *gate's* copy
  of the invariant as a row-by-row test (`assert printed == approx(numerator / denominator * 100)`),
  never a snapshot of the rendered text: a snapshot breaks on a legitimate column change and says
  nothing about a wrong number. Sweep the whole artifact once by hand before shipping the auditor,
  because the auditor only checks the shapes someone thought of.
- **A record that stores `num`/`den` and a render that drops them is the same defect from the other
  side.** When the register already carries the pair, print it (`8,01% — 75 of 936`) instead of the
  bare rate; and a record written before the pair existed is printed as it is, never completed with
  an invented denominator.
- **Renaming a label that no longer matches its base is a fix, not a retraction, when the baseline
  is keyed by id.** If the register stores its readings under a stable key and the display name is
  rendered from code, the name can be corrected to say the base it really uses with the history
  intact; read the register's format before assuming a rename invalidates the baseline.
- **Prove a fix to the subject/period on both sides: over the artifact the wrong run produced, and over
  the live source.** Replay the old rule against the saved output of the run that was wrong and print
  what it reported — reproducing the false zeros is what shows the fix is aimed at the numbers the
  reader actually received; then run the new rule over that same artifact *and* over fresh data, and
  read the artifact the reader will hold. A fix demonstrated only on new data leaves unproven that the
  figures it replaces were the ones in the reader's hands.
- **When you reorder or truncate a list, name in the footer what fell below the cut.** Sorting by
  recency to match the day's action is right; silently dropping the tail is not.
- **Never attribute a team metric to a person the data grain cannot support.** If the record is
  tied to a route, a delivery or a document rather than to a seller, print it by that grain. A
  report that names the wrong owner gets argued with instead of used.
- **Keep the exceptions line out of the rotation:** what to look at today is every day's page.
- **Never paste a Windows path with single backslashes into a text-substitution edit — the escape
  sequences are interpreted and the line splits silently.** Replacement text carrying `...\base\report.csv`
  lands a carriage return inside the file at `\r` and a backspace at `\b`, so the document keeps two
  half-lines while the edit preview reads as a harmless wrap. Write paths with forward slashes or
  doubled backslashes, and **verify the file itself** (`print(repr(line))`, or count the control
  characters) instead of trusting the editor's preview — same discipline as proving a fix over the
  artifact the reader actually received.

## Where the output lives

- Anything carrying names, observations or free text is **rendered outside the versioned repo**
  and never committed; the query or template that produces it is committed. When a name has to
  appear on the report but must not be versioned, print the key.
- Print where the reader actually looks, on a schedule that survives a restart (a scheduled task
  running as the logged-in user, not a daemon nobody owns), and make a *requested* print that
  fails fail loudly: distinguish it from a printer that was simply off.
- Never mix two entities or companies in one figure without saying which one it is. An undeclared
  mix is worse than a missing figure, because the reader cannot detect it.

## The cadence itself: the heartbeat, the exit code, the late run

A recurring report is only as good as the run that produces it, and the run fails in ways no
content rule can see.

- **One item goes out every single time, and its absence is the alarm.** If the report speaks only
  when it has something to say, a broken pipeline and a quiet day are the same morning: silence. So
  the day's first item always publishes, carrying its numbers even when there is nothing to report
  ("N loaded, 0 exceptions, M candidates"), and says in its own text that it is the heartbeat. It is
  the only item whose absence is itself the finding, which is why it belongs to the cadence and not
  to the content.
- **A finding is content; not being able to measure is the error.** The run's exit status is read by
  a scheduler, an operator or the next check, so it cannot be carrying "the business had a bad day":
  exit 0 whenever the measurement happened — exceptions included — and non-zero only when it could
  not measure or could not deliver. Otherwise the day with real news is exactly the day the task
  shows up failed, and everyone learns to ignore that red. Print the reason in the run's own log, not
  only in the code.
- **A run that arrives late must say so, and must never claim the hour it was due.** Any job that
  catches up — the machine was off at its hour, "start when available" is set, the queue was backed
  up — runs at a real hour that is not its nominal one, and a report printing the nominal hour states
  something false about its own cut. Record the **clock** time as the report's time (it is the one a
  reader can check against the source's freshness), keep the nominal apart, and when the gap is
  material print it: "corrida atrasada: la de las 17:55 salio a las 19:56, 121 minutos mas tarde".
  The same rule dates every figure the report quotes — the cut instant is when the data was read,
  never the hour the schedule named.
- **The first run of the day looks at the last period that CLOSED, and says which one it looked at.**
  A run that fires at the rim of a period measures a period that has barely begun: a morning run
  reported `1 recorded, 0 gaps, 0 candidates` while the closed day held 156 records, 139 candidates
  and one missing id. The monitor was healthy and its message certified the least useful day. So the
  heartbeat's subject is the **last closed period that has data** — searched backwards, so on a Monday
  it is the previous Friday and never the empty weekend — not "yesterday" literally; the runs that fire
  while the period is still running keep reporting the period in course. And the period examined is
  printed, in the artifact and in the register (a column naming the censused period, separate from the
  run's own date), because a reader who cannot tell a censused period from the one in course reads the
  zeros as "all good".
- **The source's window serves several periods, so the period travels on every row.** A query whose
  blocks carry the period in their own text — filters pinned to "current date", aggregates grouped over
  the whole window — can only answer for the period in course; ask it for the closed period and the
  blocks come back **empty or mixed, with no error**, which reads as a quiet day rather than as a query
  that cannot answer. Widen the window far enough to cover the gap the calendar makes (days, not one:
  a Monday's run has to still reach Friday) and have every row **and every aggregate emit its own
  date**, so picking the period is the consumer's job and one query serves every run of the cadence.
- **An event with no date of its own belongs to its neighbours' periods, under one rule both consumers
  share.** A gap in a sequence has no timestamp: it is only visible between two rows that do, and when
  those two fall on different days the attribution is a decision, not a datum. Put it in one function
  and state it once — the earlier neighbour's day, so the lookback reads the gap as part of that
  period's close, and the later neighbour's day, so the runs of the following day still see something
  somebody can act on. A rule written twice is how the same gap gets reported as two different findings
  or, worse, as none.
- **Verify the cadence by firing it once and reading its own log, before trusting the schedule.**
  What a run from your session proves is the script; what changes in the scheduled context is the
  user, the session, the working directory, the hidden-window launcher and a machine that has just
  woken. Trigger the task once, then read the artifact the reader will actually hold and the run's
  own log — not the unit tests. Recipe and the settings that matter:
 `references/scheduled-task-delivery.md`.
 - **A fix that has to be in tomorrow's run must live in the tree and the branch the schedule
 actually runs.** The task fires a launcher, and the launcher's working directory decides which
 checkout — and often which branch — the report is built from, so a change sitting on a feature
 branch does not reach the reader while your local tests are green. Read the task's own action
 (which script, which directory) and the branch of that directory (`git -C <dir> rev-parse
 --abbrev-ref HEAD`) *before* reporting a fix as done, and when the fix has to take effect on the
 next run, integrate it the same day instead of leaving it "ready" on a branch.

- **A renderer that reads a saved source refuses a period that is not the one that just closed.**
  When the render step accepts an export instead of running its own query, nothing stops a ten-day-old
  source from being rendered as this week's sheet: the figure is real, the period is not, and the page
  says nothing — measured here, the last good export was ten days old and the sheet printed it without a
  single warning. The default is the guard (compute the period that just closed, compare it with the
  source's own period header, refuse and say both dates), and reproducing a sheet that was already
  delivered is an explicit flag that names the intent, never the path of least resistance.

- **A timeout that gives up on the PDF or the browser is not a timeout unless it kills the child.**
  The conversion step runs a headless browser; when the wait expires the code prints "did not return in
  N s", skips the print and exits non-zero — and the browser keeps going, writes the PDF minutes later,
  and leaves an orphan artifact that the next run may collect as its own. Measured: the run declared the
  failure, the morning part did not go out, and the PDF appeared six minutes afterwards. Kill the process
  tree when the ceiling expires (or wait longer when the machine is loaded, which is the usual cause), and
  make the run's exit status follow the **artifact**, not the wait — a delivery that half happened is not a
  failure to report as one, it is a delivery nobody printed.

## Support files

- `references/scheduled-task-delivery.md` — putting a recurring report on a schedule (Windows Task
  Scheduler): one task per run, the hidden launcher that avoids the hang, the settings that make a
  missed hour recover, reading the scheduler from a POSIX shell, and the one-shot verification.
- `references/work-assignment-blocks.md` — designing a block that assigns a physical task
  (which items enter, in what order, grouped by what, and the canary that holds it back).
- `references/print-layout-measurement.md` — measuring why a rendered report prints in more sheets
  than it has sections: the height probe, the clean render, the page counter, and how to re-render a
  day's output without overwriting the copy that was already delivered.

## Related

- `erp-business-analysis`: the measurement side of any item whose source is a query or an export.
- `grounded-citations`: for items that quote an outside source.
- `unattended-run-verification`: the heartbeat and the scheduled run that produce the sheet.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/recurring-report-design`). Editar acá, nunca la copia instalada.
