# Pitfalls catalogue for mechanical guards

Load this when a guard is going red for a surprising reason, when choosing severity, or before converting an advisory check. The procedure stays in SKILL.md.

## Contents

- Matcher and vocabulary collisions
- Vacuous greens, perimeters and ignore files
- Baselines, declared reds and worktree roots
- Remediation text that is not a command
- Guards over machine state and ageing thresholds

---

## Pitfalls

- **When a vocabulary-matching guard flags a literal in the file you just wrote, ask whether
  that literal is load-bearing before you touch the matcher.** A guard over a rule's
  distinctive nouns (a category name, a status word, a place name) will fire on a list you
  added for another purpose — a registry of identifiers, a set of expected values. The
  reflex is to widen the guard's exemption; the correct first question is whether the list
  earns its place. Measured: a declarative constant listing dozens of table names existed
  only as an intention nobody consumed, and one of its entries matched the rule guard — so
  the file was flagged for a rule it did not implement, and deleting the unused constant was
  both the smallest fix and the better code. Corollary in the other direction: a guard that
  is right about a literal you *need* means the exemption must be scoped to that occurrence,
  not to the pattern.
- **A regression that names subjects absent from the tree is comparing against a baseline you
  did not read.** When a baseline-mode gate prints `<check>: PASS -> FAIL` over files or items
  that do not exist in the working tree (a directory that was never created, paths belonging
  to an earlier naming scheme), the baseline in play is not the file the repo versions — a
  runner can read its baseline from a second location, or a concurrent editor can have changed
  which one is read while you worked. Order of operations before spending any escape: read the
  timestamp the failing output quotes and compare it against the timestamp inside the
  repository's baseline artifact. A mismatch is the finding, and the correct move is to fix
  *which baseline is read*, not to accommodate a phantom red. Two corollaries: the gate's
  refusal is about the **state of the tree**, so a red that cites only paths you did not touch
  and that do not exist cannot be a regression from your diff; and since the condition is
  transient on a shared tree, re-run the gate at the moment you commit rather than trusting the
  verdict you collected earlier — the same reasoning the shared-tree rules apply to any foreign
  block.

- **The vacuously-green early return.** A check returns success on its "nothing to do"
  branch: the file is absent, the directory does not exist, the list is empty. Enumerate
  every path that exits success and ask what it looked at. A missing subject is a failure,
  not a pass — otherwise a tree where the thing was renamed or never created reports
  healthy forever. Verify by pointing the check at an empty tree and confirming it goes red.
  **And an empty input is not always "nothing to do": the subject set a step reads can come back
  empty because it could not read it, not because there was nothing to check.** Measured: a hook's
  test step derived its subjects from the staged diff, the diff of a partial commit read empty on a
  commit that carried three modules, and the step printed its "no code changed, skipping" notice
  while the suite never ran — a notice indistinguishable from a clean one. Give that branch a
  second reading (the working tree, the directory listing) and make the disagreement the **loud**
  path — run the whole set and say why — and keep the cheap selector on an `elif`, so it cannot
  overwrite the decision the first branch already made.
  **An early return placed *mid-check* is the same defect twice: it also deletes every
  obligation that used to follow it.** A check is a sequence, so a `return fail` inserted
  for a new precondition silently removes the coverage of everything downstream — and the
  symptom arrives as *other* tests failing on *their own* subjects, never as a failure of
  the new branch, which sends the author looking for a stale test instead of at the
  insertion point. Insert new exits after the existing obligations, or make the
  precondition one the check can always satisfy; and when a patch fails several unrelated
  fixtures at once, suspect the early return before suspecting the fixtures.
- **Never return green when the audit could not run.** A check that catches its own error
  and returns pass with the error as the message reports "nothing wrong" when the truth is
  "nothing measured". Distinguish the three outcomes explicitly: pass, fail,
  could-not-run — and make the third non-green.
- **A check whose harness dies *before* its assertion is the could-not-run outcome wearing a
  fail's clothes, and it sends the next reader into the product.** The message names the code
  under test, so a crash on the way to the comparison reads as a real red and you go hunting a
  defect that is not there. Measured: a test read a subprocess's output with `text=True` while
  the child was a native binary writing in the **console code page** (not UTF-8); the decode
  error is raised in `subprocess`'s reader thread, so the process still exits normally while
  `stdout` is left **`None`**, and the next line dies concatenating `stdout + stderr` with
  `TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'` — the assertion that
  mattered ("the reason reaches the user") never ran, and a lost reason looked exactly like a
  healthy block. Three rules: **read a native child's output as bytes and decode it
  explicitly** (`(p.stdout + p.stderr).decode('utf-8', errors='replace')`, no `text=True`),
  keeping every assertion ASCII so one stray accented byte cannot abort the check; treat a
  `TypeError`/`AttributeError` on `None` inside a test as a harness failure until proven
  otherwise, never as the product's verdict; and prove the assertion can fail by feeding a
  variant with the right *shape* but the wrong content (correct exit code, missing message)
  and watching it go red — a check that crashed before comparing has the same defect as one
  that was never able to fail.
  **Same family, and easy to misread as the product's fault: a subprocess timeout under CPU
  contention.** A test that shells out — an import probe, a hook probe, a scanner — fails as a
  *timeout* when parallel workers saturate the machine, and the message names the file under
  test, so a branch that never touched that file reads as its author. Measured: a parallel run
  on a machine saturated by other sessions failed five times, every case in a file the branch
  did not touch, and all five passed serially and alone. When the failing subject is outside your
  diff, re-run that subject by itself before editing anything — a red that is arithmetic on
  wall-clock is not a defect, and "fixing" it writes a change to code you were not there to
  change.
  **But do not stop at "not mine": when the wall-clock red is a step of the gate everyone commits
  through, the guard itself is the defect, and the repair is to make its verdict independent of the
  machine.** A test whose subject is "the file already contains the end-marker when the deadline
  expires" measures how fast the machine can start a process — red on a loaded box, green on a quiet
  one — and as a pre-push or pre-commit step it blocks every session, not just its author, with a red
  that names a real assertion. Reproduce it under load before touching it (saturate the CPUs with a
  handful of spinner processes and run the subject alone, keeping the failure's own message), then
  **measure the latency the test was implicitly assuming** — spawn-to-marker, under that load — and
  let the number rule: a deadline sized below the measured maximum keeps flaking, and raising it only
  trades a fast flake for a slow one. Prefer removing the dependence: have the spawn step return once
  the child has produced the signal the test is about, so the deadline covers the logic and not the
  scheduler. Close it both ways — old form red under load, new form green under the same load, and
  the guard still red when the production fix it protects is reverted, which is what shows the repair
  did not quietly disarm it.
- **When you prove a guard can fail by reintroducing the defect in place, verify the edit
  actually applied — count the replacements, do not trust the script's success message.** A
  `replace` against a file whose line endings differ from the pattern (CRLF vs LF on a Windows
  checkout) matches nothing and reports fine, so the guard is then "proven" against an unmodified
  file and the proof is empty. Assert the occurrence count is the one you expect before
  re-running the test, and restore from a copy taken **before the first edit of the series** rather than by re-editing — one written halfway through reverts every later edit with it. Do that edit
  in code rather than by hand: read the bytes, normalize `\r\n` to `\n`, assert the anchor occurs exactly
  once, replace, and write back with the line endings the file already had. Re-typing a find-and-replace
 that missed once misses the same way again, and a half-applied edit is what makes the proof empty.
 **And when the replacement text itself contains escapes, do not write them as literals in the edit
 payload**: a `\r\n` typed into the new string can land as a real newline inside the Python literal
 and leave the file with a `SyntaxError` unrelated to the change — build the sequence from
 `chr(13)`/`chr(10)` so nothing is reinterpreted on the way in. **The same endings bite the test
 that slices the file's text**: splitting on `\n` in a CRLF checkout returns a neighbouring block,
 so the assertion passes or fails about the wrong region — normalise `\r\n` to `\n` once, up front.
- **A check whose subject is an artifact's existence is not a check.** It proves the file
  is there, never that it is current or correct, and it stays green through the entire
  regression. Check the *content*, or check the property that actually matters.
  **And when the property is "tool X is wired to the rule", the property that matters is
  that the wiring *runs* — so the check must execute it the way the consumer executes it:
  same interpreter, same shell, same working directory.** Asserting that the manifest
  exists and names the script asserts the existence of the guard, not the guard. Measured:
  a hook manifest was present, its wrapper present, delegating to the canonical script, and
  the wiring check reported green — while the declared command resolved nothing in **any**
  directory the tool could plausibly use as its cwd (exit 127, no output): the guard was
  off and every artifact said it was on. Reproduce the consumer's context in the test (the
  launch shell, the cwd the tool documents) rather than the developer's; and where the
  context cannot be measured live, make the command correct under **every** plausible
  context and pin that with a test, stating in the guard's own output which contexts were
  exercised. This is the same defect as a detector that only matches the payload shape your
  fixtures produce — see the next pitfall.
- **A fixture that never varies the *shape* of its input cannot prove an extractor works.**
  When a guard or hook parses a structured input — JSON, a delimited row, a keyed payload —
  the test must exercise the same field in different **positions** and with sibling fields
  present, not only with different values. A greedy extraction (`"field"[[:space:]]*:[[:space:]]*"\(.*\)"`
  and friends) anchors on the **last** quote in the payload and swallows everything after
  the field it wanted; a fixture that always puts the parsed field last returns the bare
  value and passes, so the extractor is green for the test and broken for the real payload.
  Measured: a rule-enforcement hook parsed its command out of the payload the runtime
  actually sends, where the parsed field sits **before** session/cwd/extra keys; the
  extracted value came back contaminated (`cp a.dat <dest>` stopped matching) and a real
  write slipped through — for every consumer that shares the extractor, while the suite was
  green because every fixture ended on the field. Cut such extractions at the first
  **unescaped** terminator, not the last; handle the empty field as empty; and add a fixture
  whose parsed field is followed by at least one more key, plus one whose value contains an
  escaped quote — the two cases the greedy form gets wrong.
- **Separating a gate's known reds from its new ones is a partition of everything the gate
  reports, never of the blocking subset — filtering it by severity hides the classification
  exactly where the noise lives.** The instinct is to keep only the checks that can fail the
  run, because those are the ones that matter; the effect is that a gate whose known reds are
  all non-blocking prints them, unchanged, beside a fresh red — which is the very defect the
  partition was added to fix. Keep the two questions apart: severity answers whether a finding
  *blocks* and is already answered by the gate's own blocking predicate, while the partition
  answers whether a finding is *new* and must cover every finding. Measured: three permanent
  reds, none of them blocking, survived a partition that filtered on the blocking flag, so the
  feature shipped present in the code and invisible in the output. Retrofitting it, add a test that the classification is **displayed** for a non-blocking red, not merely computed.
  - **And a partition built from *this* run's results must only count the subjects that RAN — an
    absent check did not "stop being red", it was not measured.** Measured: a gate that lets a
    caller run a **subset** by name reported every declared red it had not run as "declared reds
    that are no longer red, clean the register", on each partial run: three false notices every
    time, which turns the one message whose purpose is to prompt a cleanup into noise nobody reads.
    Intersect the declared set with the set that produced a result before diffing them, and say in
    the message which population the count is over.
- **Silencing a finding is not handling it.** When a check needs an escape hatch, make it
  a declaration in the input — a comment, an explicit parameter, a named list — never a
  muted line or a widened exclusion. Then a false alarm costs one declaration and leaves a
  trail, instead of costing trust in the check. **And the declaration must carry its reason,
  with the mechanism refusing one that does not**: an escape hatch whose motive is optional,
  or is free text taken as a flag argument that the parser can silently consume as a
  positional subject name, is the muted line one indirection away. Require the subject and
  the motive together, and strip the motive from the positional list before that list is
  interpreted. Measured: the declaration landed with its motive read as a check name, so the
  call failed and the red stayed undeclared while looking handled.
- **A blanket exemption creates a blind spot exactly where the problem was.** If the guard
  excuses a whole line for containing a historical mention, a current, wrong value sharing
  that line is excused too. Scope the exemption to the token or window it actually applies
  to (the text before the match, up to a clause boundary) so the rest of the line is still
  checked. Test the exemption explicitly: one fixture where the history is exempted, one
  where the current value on that same line is still caught.
- **A baseline that can only suppress rots into a blanket mute.** If the project records
  known/accepted findings, the check must also report baseline entries that no longer
  correspond to anything, or the file grows into a permanent amnesty. Treat a stale entry
  as good news to surface, never as a failure of the check — and a **declared motive is itself a
  stale entry**: it quotes the figure that was red when written, so print it after the live message,
  with its date, and warn when they diverge (store the check's own message at declaration; normalize
  digit runs or the warning is daily noise). the changing-existing-guards.md note (load from SKILL.md).
- **A test that skips when the artifact is empty hibernates an out-of-date expectation.** A guard
  over a register, a baseline or a declaration legitimately skips when that artifact was never
  used — and that skip is what hides a fixture list that stopped matching the thing it
  enumerates. Measured: a test asserting three named reds were declared stayed green because the
  register was empty and the test skipped; restoring the register woke it onto a list one of
  whose members had graduated to passing, so the test that exists to catch a deleted register
  failed on a *correct* register. Skip on the condition the test cannot observe (no artifact at
  all), never on a state a correct repair will change; and treat restoring such an artifact as a
  change to the test's subject, not only to the code's — re-read every list keyed to its contents
  as its own step.
- **A false alarm trains people to ignore alarms.** A check that is permanently red for an
  unrelated or unfixable reason gets bypassed, and the bypass takes the real signal with
  it. Measure the check against the current tree before making it blocking; if it is red,
  fix the state in the same commit or ship it non-blocking with the reason written down.
- **When the red exists to prompt a human decision, the trigger must be the presence of
  *decidable* work, never a magnitude that stands in for it.** A threshold over the whole
  population ("N items, over the declared limit of M") fires whether or not there is anything
  to act on, and when the actionable subset is empty the red cannot be cleared by doing what it
  asks: the only exits are destroying things that are not redundant, or editing the threshold.
  Measured: 96 subjects against a declared limit of 70 with **0** actionable candidates — each
  one was the newest of its kind — so the check was red by construction while its message
  ("the deletion is a person's call") invited a decision that did not exist. Key the verdict on
  the actionable set (red exactly when the candidate list is non-empty) and keep the population
  count in the message as information, naming which decision is the real one ("the limit is
  below the number of subjects: raise it and re-seal, do not delete"). The tell is one question:
  what is a reader supposed to *do* about this red, and can doing it ever turn the check green?
- **When the finding is a gap in the *rule* rather than a defect in the tree, the repair is
  the rule — never the matcher.** A guard enforces a policy someone else decided; when your
  measurement shows the policy does not *name* the case you found, widening the matcher makes
  the check demand something nobody agreed to, over artifacts that have **already shipped and
  cannot be withdrawn** (a published history is not rewritten, a delivered export is not
  recalled). The red is then permanent, which is the single most reliable way to kill a gate:
  an unfixable red gets bypassed, and the bypass takes the guard's genuine signal with it. Make
  the gap a **decision** — with owner and trigger — and let the matcher change be its
  consequence if, and only if, the decision goes that way. The test to run first: is this case
  forbidden *today, by a rule someone wrote*, or am I the one deciding it should be? If it is
  the second, write the decision before writing the check. Corollary for the finding's
  severity: a subject already published is not a candidate for a *new* blocking check at all —
  the honest output is a declaration plus an open question, and a guard that blocks on a
  question nobody has answered teaches everyone the escape hatch.
- **And once that decision goes the way of yes, the matcher change is a *split*, not a
  widening — a token with both a legitimate and an illegitimate use is recognised as its own
  category and never fires on its own.** A column name, a vocabulary word, a category value
  can be correct in one context and a leak in another, and the same tree holds both: a
  legitimate aggregate *over* the token beside an illegitimate crossing of it *with* a
  protected subject. Teach the guard to recognise the token **separately** (its own pattern,
  and a field on the finding to carry it) and to **name it only when the illegitimate
  companion is present** — `vendedor;monto` passes, `vendedor;cliente` fails and the message
  says the pair. Firing on the token alone is what makes the change unusable: the legitimate
  artifacts have already shipped and cannot be withdrawn, so those reds are permanent, and a
  guard that can no longer go green is bypassed, taking its genuine signal with it. Prove both
  ends with a fixture **pair** — token alone passes; token plus companion fails *and the
  message names the pair* — because a split that fires on the companion alone is just the
  widening it replaced, one level over.
- **Sample a field's *values* before writing any rule, guard, filter or finding about it — the
  column's name tells you nothing about its subject.** A header is chosen by whoever generated
  the file, and the same word names different things on different sides of the tree. Measured: a
  column called `nombre` held **product** names across a dozen catalogues, while a column called
  `vendedor` — which reads as neutral metadata — held **people's** names; a detector keyed on the
  header would have flagged the catalogues and passed the names. This bites a guard's matcher
  (it must match the value's shape, not the column's label), a classifier (its categories are
  about the value), and any write-up: print three to five raw values of the field before you
  conclude what it contains.
- **Never gate on a value that moves.** The check recomputes the number; it must not be
  fed a constant that was true once. If the guard's message or fixtures contain a count
  that changes, that count is a second thing to maintain — and the first one to go stale.
  **The toolchain that produces the value moves the same way, and it is declared in the same
  place the guard's other subjects are: a dependency list written with floors (`>=`) is not a
  declaration but a query — what runs tomorrow is whatever resolves then, so the same green can
  mean two different things on two days with no file changed, and a suite that goes red is
  unattributable.** Pin the declared list to the versions that resolved when you measured it,
  and add the structural guard that keeps it pinned: every line carries `==`, and the message
  names the floors it found. That guard reads the **declaration**, never the installed
  environment — a check comparing resolved versions reds for everyone whose environment differs
  (the hook, the scheduled task, another interpreter) and, being permanently red, gets switched
  off. Declare the part you did not pin, the transitive set the resolver still chooses, because
  that is the next reader's whole question.
- **When the guard decides "pending" from a recency threshold, measure the age of the
  *subject*, not of the container that keeps moving.** A check that asks "has this been
  sitting unanswered too long" must date the thing that is unanswered — the correction, the
  finding, the request — because the container it arrived in (a branch, a queue, a pull
  request, a claim) goes on accepting work. Measured: a threshold on a branch's tip commit
  reported nothing for the exact incident the guard was written to catch, because the branch
  received commits for hours *after* the correction that mattered; re-pointing the
  measurement at the **oldest un-integrated commit** made it fire. The tell is a threshold
  that someone else's innocent activity can reset: if continuing to work on the subject
  lowers its apparent age, the guard measures the wrong object and is green precisely while
  the problem is at its worst. This is the inverse of the pitfall above — there the moving
  value must not be pinned, here a moving container must not be the clock — and the two share
  one question: *which* timestamp is this number supposed to be.
  A threshold is also the one guard parameter whose test cannot wait for wall-clock time:
  inject the dates (author/committer dates on a fixture commit) so the boundary is exercised
  on both sides in a second, and assert the pair — just under the threshold is silent, just
  over it fires — rather than testing only the case that happens to be true today.
- **When a property legitimately takes several values across the tree, the invariant is
  that no single artifact changes value *within itself* — forbid the mixture, never pick a
  winner.** A guard demanding one uniform value makes an arbitrary choice and comes back
  red on most of the tree; a guard demanding the *absence of the mixture* is satisfiable
  today and stays satisfiable through any legitimate rewrite, so it can be made blocking on
  the first run. Write the threshold down from the measurement you just took, before the
  check exists — a number chosen by feel is a wish, not a baseline — and when such a check
  flags a real case on its very first run, suspect yourself before the tree: the same edit
  that installed the guard is the likeliest thing to violate it. Corollary for a guard whose
  subject is prose: a test for it must name a token the guard's vocabulary **demonstrably
  watches** — verify the noun is in the matcher before asserting on it, or the test goes
  green while measuring nothing, which is the vacuous green one level up (the guard is fine
  and the proof is empty).
- **A check that duplicates the producer's rule instead of calling it will disagree with
  it.** Import the predicate from the code that owns it (extract it if it is not exposed)
  rather than paraphrasing the criterion. Two copies of one rule, each confident, is the
  state the check was meant to eliminate. Corollary: this is about *rules*, not *values* —
  a comparator that reads what the code produces and what the prose claims is not a second
  register, because it stores nothing. See the vacuous-green-detection.md note (load from SKILL.md).
  **The same holds one level over for a WRITE path: a consumer that opens the artifact and writes
  it itself has copied the producer's guarded writer with the guard removed, and no test of the
  guard will see it.** The tell is a second place that knows how to write the artifact. Make the
  consumer call the guarded writer, and when a fix lands in one consumer, sweep the other call
  sites of the same source before declaring the class closed — the defect arrives in siblings, and
  the one you did not grep is the one that clobbers the evidence next.
- **The guard's own output must not restate a volatile count.** A green message that says
  "N things checked" where N is hand-written reproduces the exact defect the guard exists
  to catch. Compute it or leave it out. **And carry the denominator as *distinct subjects*,
  not as occurrences of them.** A total built by summing per-citation lists counts one
  subject once per mention, so it comes out *larger* than the population it describes — the
  direction that reads as thorough rather than wrong. Measured: a resolvability guard
  reported "18 of 118" over what were 12 distinct unresolved hashes appearing 18 times.
  Deduplicate before counting, and when the difference is real say which you counted
  (`12 distinct (18 mentions)`).
- **A detector over a program's stdout must count by the producer's own record convention, and
  declare when that convention is absent instead of approximating.** Counting the non-blank lines
  of a tabular tool's output also counts its connection banner, the statement the tool echoes back
  (wrapped across several lines), the column header and its status notices. Measured: a first
  version of such a detector flagged **191 of 191** saved outputs as suspect — the false-alarm
  pitfall above, arriving before the guard shipped — and the cheap way to find it is to run the
  candidate detector over everything already on disk and read the count, before wiring it into
  anything. Count what the producer's own rows carry (a short leading mark per record), so a record
  either prints with its mark or does not print at all; when the output has no such mark, report
  **could-not-verify for that subject** — never a green from an empty count, and never a red from a
  convention the output never had. Two edges: the declared total may arrive once per statement, so
  the denominator is the sum across blocks and the guard must say how many blocks it summed; and
  the count belongs in the module that produces the output, reusing the declared-total helper the
  existing checks already call, not in a second regex beside it.
- **A verification added to a data-producing command must not ride the failure path of the job that
  consumes it.** When the command's output feeds a scheduled deliverable, failing the command on the
  new finding stops the deliverable, and the defect changes class: from "a wrong number nobody saw"
  to "no number at all". Give the new finding its own exit status, keep writing the artifact (the
  command *did* run, and that file is the consumer's evidence), leave the caller's existing success
  predicate untouched, and put the loud part where a person reads it. Measured: the finding shipped
  as a distinct code beside the tool's ordinary failure codes, so the scheduled producer was
  unaffected while the interactive door reported it and the run ledger recorded it — where reusing
  the ordinary failure code would have withheld the day's file over a defect that only shrinks a
  denominator.
- **A guard's verdict can be right while its finding is wrong, and the finding is what the
  next session acts on.** A check that resolves an identifier against a *declared* subset
  answers "cannot derive this" for everything outside the declaration — a different
  population from "this is gone", with a different repair — and the guard collapses them
  into one sentence. Measured: a resolvability check was correctly red over 12 unresolvable
  hashes and told the reader all of them had lost their source; 5 existed on disk, merely
  undeclared, so the message sent those to re-derive a report that only needed a
  declaration. Keep the verdict as it is — the subject really is unresolved — and split the
  finding into the two actions, naming the repair for each (`N undeclared (declare them),
  M lost (re-derive)`). The tell is a message phrased as a single remedy for a set that is
  not homogeneous: ask what the reader is supposed to *do*, and if two members need
  different things, the sentence is lying about one of them.

- **A guard whose subject is "the source is missing" has three repairs, not one, and the one that
  is usually right is "the copy already exists somewhere the guard does not look".** Before editing
  a declaration or re-deriving an artifact a red check reports absent, check the project's own
  archive — retention store, backup directory, snapshot. Measured: a *critical* check stood red over
  three declared hand-maintained sources that the project's retention store held complete, with
  matching hashes; the red reported a problem already solved, and the cheapest correct repair was to
  return the bytes. Enumerate all three repairs (re-derive, declare, restore) before touching any of
  them, and say in the guard's message which one applies — an existing verified copy is a different
  finding from a lost one (the sibling of the finding-splitting rule above).
  **The deeper rule is about the mechanism, not the message: a store that can prove a byte but cannot
  put it back is half a mechanism, and the missing half is the one that ends an incident.** Capture
  plus verify with no restore turns a recoverable loss into a permanent red — worse than no retention,
  because everyone believes the data is safe. Build the return path when you build capture, and prove
  it the way you prove capture: hash the restored file against the archived one, per subject, never by
  size or timestamp. Three edges: make restore **find-or-refuse, never overwrite** — a live working
  copy beats an old capture, and an archive that clobbers the file it was protecting is worse than
  none; restore to the path the **declaration already names**, so the check goes green without the
  declaration being edited to fit the accident; and **re-verify the whole store afterwards**, since a
  restore that consumes or corrupts the capture converts a recoverable red into an unrecoverable one.
  Corollary on consent: when the repair writes **outside the repository** — the user's Desktop, a shared
  drive, another machine — the repair is a proposal, not a step. Ask which of the three applies and
  where, even when the restore is obviously correct, because those are the user's files and their
  absence may itself be the intended state.
  **A fourth case sits beside the three and needs the opposite action: the source was MOVED by the
  person who owns the machine, and the declaration is what is stale.** Distinguish it by where the file
  actually is — a folder created after the baseline was sealed, holding the file under the same name —
  which is a reorganization, not a loss. There the repair is to **update the declaration to the path that
  exists**, using the pattern the config already applies to its other relocated entries; declaring the red
  would version a falsehood. So before choosing among re-derive/declare/restore/relocate, locate the
  subject in the tree and in the project's own archive: *which* repair applies is a directory listing away.
- **When the guard's subject is "this code does X with the wrong object", read the syntax tree and
  follow one level of assignment — the defect hides behind a local name.** A detector that only
  matches the flagged expression where it appears literally finds a fraction of the sites: measured
  on a repo-wide root-path audit, text matching saw 10 uses and the AST saw 23, the difference being
  every `p = os.path.join(BAD_ROOT, ...)` followed by `open(p, "w")` one line later. Follow names
  assigned from the flagged expression. Two edges that keep it precise: **do not follow names that
  are function parameters** (a parameter is the injectable form the tests need — `root=None` is what
  lets a fixture pass a `tmp_path`, and following it flags every auditor that legitimately reads the
  production tree), and **do not compare the flagged expression as a substring** — the guard's own
  source contains that string inside an `in` test, so it flags itself. Match the node
  (`Attribute`/`Name`), not the text, and add a fixture for each edge: the derived-name case, the
  parameter case, and the guard-flagging-itself case.
- **A matcher that needs nesting depth must measure it relative to the statement, and count over a
  copy with comments and literals blanked.** Counting brackets, quotes or parens over a whole file to
  find balanced groups — a call's arguments, a concatenation chain, a `SELECT` list — is wrong the
  moment a comment or a string literal carries an unbalanced one: the depth of every token *after* it
  is off by one, the spans come out shifted, and the finding names the wrong place, which is worse
  than no finding. Blank the comments and literals into a same-length copy (offsets stay valid, so
  the spans you report still index the original) and do all the counting there. **And resolve an alias
  inside its own statement**: one letter is a different table in the next block, so a file-wide alias
  map accuses a column that belongs to a sibling's table (measured: the same alias bound to a
  purchases table in one block and a clients table in the next, and the global map produced a
  confident, wrong list). When the guard is a *diagnosis* rather than a verdict — a candidate list a
  human then checks — say in its own message that it can over-report, and protect the guarantee that
  matters: the real culprit is always in the list. Excluding what cannot be the culprit keeps it short
  — a field used only inside a comparison (`x LIKE`, `x <`, `x =`) cannot be the one that drops the
  row. **If the guard's repair is applied through computed spans, apply them from the END backwards,
  skip spans that overlap ones already applied, and read the resulting diff line by line:** a forward
  pass using offsets computed before the first insertion writes broken text while reporting success,
  and the file it mangles is exactly the one the guard exists to protect. Keep each operand's
  surrounding whitespace outside the inserted wrapper so the diff stays one line per edit —
  normalizing the file's layout to make the edit easier turns a small change into a rewrite nobody can
  review.
- **When a guard's subject is "this resolves an artifact from the wrong root", the correct fix
  depends on whether the site WRITES or READS — and a reader of un-versioned data must keep the
  shared root.** The guard is right that an artifact rooted in the integration checkout lands in
  another session's tree; but that is a defect only for writes. Measured: a newly added module
  READ a report that a confidentiality rule keeps **out of the repository**, so the file exists
  only in the integration checkout — copying the fix applied to the other 25 flagged sites would
  have made the reader return an **empty list silently**, which is the very defect the guard
  exists to prevent, served by the guard itself. Classify each flagged site read-vs-write before
  editing; a read of data that by design lives only in the shared tree is correct where it is,
  and the honest repair is a declared exemption carrying that reason. The tell for a reader:
  resolving it elsewhere raises nothing — it just returns zero rows.
- **A comparator that reads a value out of a row must resolve the column by the subject's own
  header, never by the order the declaration lists it in.** When the expected column list and the
  file's header disagree — a variant with an extra leading column, a sibling file that shares a name
  but not a shape — an index taken from the declaration points one field over, so *every*
  per-column finding downstream is misattributed: real values are reported as non-numeric under the
  name of their neighbour, and the reader repairs the column that was never wrong. Resolve against
  the header the file actually has (`{name: i for i, name in enumerate(real)}`), and report the
  disagreement as its own finding (`missing column`, `unknown column`, `order differs`) instead of
  letting it corrupt the checks that follow. A comparison keyed on position is only as sound as the
  declaration it trusts, and the declaration is the one thing the guard exists to doubt.
- **Widening a guard's perimeter silently invalidates every piece of prose that describes the old
  one — and that prose is what the next agent acts on.** A rule file, a skill, a README that says
  "folder X is not covered" or "the index does not track Y" is true only while the guard's file list
  stays put; the day the list is widened the guard reddens documents in X while the prose keeps
  telling readers there is nothing to do there. Nothing guards the prose, so the disagreement
  surfaces as a blocked commit on work that followed the instructions — measured: a note stating that
  a certain directory was not indexed was still in place after the guard had been widened to cover
  it, so a document written exactly as instructed was refused by the index-completeness check.
  Two habits: **when you change a coverage list, grep the tree for prose naming the old perimeter and
  fix it in the same change** — keeping the authoritative statement in the guard's own comments makes
  it the first thing whoever edits the list will read; and when you are the reader, **read the
  perimeter out of the check's code before trusting any claim about it**, because a stale sentence and
  a current one look identical and only one of them can be executed.
- **Prove an exclusion is innocent by widening it once.** A guard that walks a subset of
  the tree — source roots only, tests excluded, vendored and generated code skipped — is
  only as sound as its boundary, and the boundary is normally chosen for noise rather than
  after measuring what it hides. Run the guard once with the excluded tree re-included and
  read the count: zero new findings means the exclusion is harmless and you can say so;
  anything else means the blind spot was real. Record which of the two you observed, since
  "0 findings" over an unexamined subtree is the denominator problem wearing a different
  hat.
- **When a guard pins measured counts, name each constant for the quantity it measures —
  near-identical names let a test assert a sibling's value and still be green.** A file
  guarding one computation often pins several counts that differ by one word (a total, the
  subset that is flagged, the subset that is inferred, the subset that falls in a queue).
  Measured: a constant was pinned to the *total* while its name promised the *flagged*
  subset, and the resulting assertion passed because nothing compared the constant against
  the key it claimed to be — the number was simply the wrong one to expect there. Two
  habits: read each value out of the measurement structure by its **key** rather than
  restating the digits, so a wrong expectation cannot be typed at all; and when one count
  changes, re-derive **every** count in the same file instead of only the one the failure
  named — the others were computed against the same population and are now stale together.
  Corollary: an assertion copied from a neighbouring case carries the neighbour's
  premise. A claim of "no activity" asserted as two zeroed fields went green for a group
  that had one of the two non-zero, because the second field had nothing to do with the
  claim. Assert the field the claim is about, and only that field. Finally, **prove the
  constant-pinning assertion can fail by perturbing the constant by hand** (the correct
  figure down to the old, wrong one) and watching it go red before trusting it. A test that
  pins a measured count has the same failure mode as any other guard — it may never have
  been able to fail — and it is the one guard whose whole subject is a number you typed.
- **A guard's coverage is the file list it walks, and that list is a hand-picked subset of
  the tree in every case that matters.** Two guards can look thorough and still leave a
  whole directory unvisited — a "no module-level side effects" check globbing `src/**` while
  a second scripts directory and a reports directory go unwatched, and a second guard
  globbing the same root, so the gap is invisible from either one. Compute the perimeter
  instead of trusting it: enumerate the tree the way the guard *should* (`rglob('*.py')`
  minus the excluded dirs), enumerate what it *does* (its glob or tuple), and print the
  difference as an assertion so the exclusion can never widen silently. Then ask of each
  exclusion whether it was chosen for noise or for role — generated output, vendored code
  and fixtures are legitimate; "the other scripts folder" never is.
  **And when the out-of-perimeter item is an artifact you just created, the first remedy is to
  move the artifact, not to widen the guard.** A new file of the guarded kind — a query, a note,
  an export — is often simply in the wrong directory, and a guard's glob widened to reach it
  covers more of every future run for a reason chosen in one afternoon. Relocate it into the
  directory the guard already walks, and prove the move with the guard's own subject count: a
  collector run over the guard filtered to your file selecting **0** is the measurement that it
  was outside, and the same run selecting it is the measurement that the move worked. Widening
  the perimeter is the correct second resort, and it is a change to what the guard means.
- **The perimeter can also be a file type, and a guard whose subject is one format passes
  green on the same defect in another.** A guard that reads "every `.csv` in the tree" states
  its perimeter in the *format*, and the format was chosen the day the first file of it
  appeared — so a second format carrying the identical records sits outside the guard and
  inside everyone's belief about it. Measured: a confidentiality guard over delimited data
  reported a healthy denominator ("N inspected, none found") while a JSON export of the same
  rows — dozens of names, addresses and phone numbers — sat versioned beside them. That is
  not the vacuous green (the denominator was fine); it is a green with the subject trimmed,
  which is harder to notice precisely because the count looks right. Read the extension
  histogram of the tree once and rule on each entry: table-like formats belong in the
  perimeter together, container/markup formats do not; write the ruling as one constant the
  guard reads, so widening it is a single edit in a single place. When you do widen it,
  **calibrate the new members before shipping** — the detector was tuned against the narrow
  set, and a structural file in the new format (a schema catalogue, a config tree) can share
  a data file's vocabulary and turn a clean tree red; that is a false positive in the guard,
  so tighten the *shape* test (in a nested format, the signal is a record — an object that is
  an element of a list — not a bare key) rather than dropping the format back out. **And when a perimeter is published as a count, the
  filter travels with the number.** A figure measured over a directory of outputs ("N of M carry
  the defect") is a function of the extension set, any size cutoff, and the moment — and that
  directory usually grows on its own, because a scheduled job writes into it. Measured: the same
  count read 49 in the note that published it and 84 when the reader re-ran the documented
  command, the note having been measured over two extensions and the command over three; the
  detector was identical the whole time, so the number was the defect, not the code — and it had
  already reached a panel entry and a skill. Publish the glob (or the extension tuple), the
  cutoff, the hour and the command that reproduces it, and re-run that exact command before
  publishing; where the count moves with the filter, publish the members that are stable across
  every measurement and let those carry the claim. See
  the guard-perimeter.md note (load from SKILL.md).
- **A scanner that walks the filesystem has the ignore file outside its perimeter, so its own
  exclusion set *is* the perimeter — and when it is a step of a commit hook it may have no
  escape to spend.** The scan that respects ignore rules is one arrangement; the scan that
  does not (`rglob`/`os.walk` plus a hand-written exclusion set) ignores `.gitignore`
  entirely, so no rule added there protects it. Measured: one installed dependency tree took a
  secret scan from 627 files to 4,064, with **70 of 70 findings** inside third-party code,
  while the repository's own files stayed clean — and because that step offered no skip
  variable it blocked the commit of every session on every worktree until the perimeter was
  fixed. Exclude by directory **name**, not by path (these sets match against every part of a
  path, so the name covers it at any depth under any tool's directory); read the findings
  grouped by source root before believing a red; and give the exclusion set the same
  non-vacuity guard the walk has, since a set widened "to reduce noise" scans nothing and
  still reports zero.
- **A check that asserts one narrow property of an artifact quietly certifies the whole
  artifact.** A test that a file *exists*, that a module *imports*, that a path *resolves*,
  or that a table *has a header* goes green and is then read as "this thing is correct",
  including the parts nothing looked at. It is the existence-vs-content pitfall one level
  out: the guard's subject is a subset of what its result implies. State the implication in
  the message ("exists, contents unverified"), or narrow the claim — and when you are the
  reader of such a green, treat it as the narrow assertion it is rather than as coverage.
  **The same narrowness applies to *which producer* you pointed at: one logical output with two
  renderers — a markdown body for the reader beside an HTML page for the printer, two templates,
  two serializers — needs one test per renderer, and a line guarded by a condition that exists for
  another purpose disappears from exactly one of them.** Measured: a required metric line sat inside
  a block that only runs when there is new work to show, so the printer's renderer emitted it always
  and the reader's never; the test covering the printer was green while the other path had silently
  dropped the line. When a line is required to be present, ask which condition it genuinely depends
  on, put it outside every other purpose's block, and assert it on each renderer separately.
- **Precision beats coverage for anything that matches text.** A guard over prose that
  tries to catch *every* number produces hundreds of false positives on dates, versions
  and illustrative examples, and gets turned off. Match a measured, enumerated vocabulary
  (the specific nouns that actually get counted here) and extend it deliberately when a new
  class appears. A narrow guard that survives is worth more than a broad one that is
  disabled. Two corollaries earned by widening one of these by hand: **widen the vocabulary
  and the denominator together** — adding a noun to the matcher without adding the
  measurement it compares against turns aligned figures into findings, and the first
  instinct is to delete the noun again rather than measure it. And **a matched noun with no
  single cheap measurement must be declared unmatchable, in the guard, not dropped from the
  matcher**: a list whose length depends on which subdirectory you mean makes the guard
  disagree with a correct document, and silence about it is how the next person "fixes" the
  document. An explicit `SIN_MEDICION`/`UNMEASURED` tuple is the honest form.
- **A guard over prose needs a designated section, or the document's own body becomes the
  false positive.** A comparator that scans a whole document for a figure cannot distinguish a
  citation from a retraction, so the expected value and the document's history collide and the
  guard's precision ends up decided by prose style. Read the expected value from one
  machine-readable verdict section, name that section in the guard's output, and make the
  citing side cite only that block. See the guard-implementations.md note (load from SKILL.md).
- **A guard whose subject is a file that another process creates will fire on someone
  else's work.** Checks that require the repository to be *complete* — every document
  linked from the index, every artifact paired with its manifest, no missing siblings —
  turn every in-flight addition by any writer into a red that lands on whoever commits
  next, not on whoever caused it. Separate the two obligations: membership for things a
  human asserts (a note that must be indexed), presence only for things a process emits (a
  report, an export, a table). An emitted artifact is referenced and validated from the
  document that cites it, never required to appear in an inventory. The observable symptom
  of getting this wrong is a gate that is red immediately after a fresh, valid output appears,
  with no code change.
- **A guard that resolves its perimeter through version control sees only what is tracked, so
  a document you just wrote reads as *missing* until it is staged — and the red lands on the
  author who is about to add it.** Building a link/perimeter check on the repository's
  *committed* listing (`git ls-files`, a `solo_versionados` filter) is the right design: it
  measures what a clean checkout will contain, which is the defect it exists to catch. The
  price is that a note you create and reference in the same breath reports a broken link in
  your own tree, before `git add` — a red on the exact work in progress, which reads as the
  panel being wrong. **Do not widen the guard to the working tree to silence it**: that swaps
  a clone-accurate verdict for a disk-accurate one and reopens the "green in the tree, broken
  in the clone" gap the versioned read was chosen to close. Stage the file and re-read; the
  red was ordering, not the check. The tell is the asymmetry — red with the file on disk and
  green the instant it is tracked — and it is the mirror of the pitfall above: there a foreign
  in-flight addition reddens someone else's commit, here your own reddens yours.
- **A derived boolean named after a criterion is not that criterion, and a guard citing it
  measures the wrong population.** A lax flag ("at least two records share this attribute") and
  the strict one the name implies ("all of them do") give different denominators over the same
  concept — measured, 22 vs 17 groups — and the name gives no hint which is which. The number
  reached a published report *and* the guard's own assertion before anyone noticed, because both
  read the flag and neither read its definition. Two habits: when a guard asserts a figure the
  report also prints, make it call the **same function** the report calls and assert the count it
  produces is the one the summary carries, so the two cannot drift apart in silence; and when a
  concept has a lax and a strict form, **publish which one you are counting** in the document — a
  reader cannot recover it from the number. Name the helper for the criterion it computes and say
  which one in one clause of its docstring, so the next author choosing between the two is
  choosing deliberately rather than by the name they remembered.

- **A matcher's fixture lives inside the tree the matcher walks, and a shell-quoted probe is not a test.** The test you write for a text-matching guard is itself a file the guard scans, so a fixture carrying a realistic instance of what it looks for makes the guard red on **your own test file** — the guard is right, the fixture is what changes (use the project's allow-marker, or a value that is unmistakably a placeholder) — and when the
  matcher's step is one the project's hook runs with no escape, that red is not yours alone:
  it blocks every committer on the tree until the fixture is fixed, so write the fixture
  innocuous from the start and re-run the scan over the real tree before committing it. Two consequences for proving the fix. Run the probe as a **file**, never inline through a shell string: measured, the same cases run via an inline `-c` reported two failures that did not exist, because the shell consumed the backslashes before the interpreter ever saw them — precisely the hazard when the matcher's subject *is* escapes. And cover **both spellings** of whatever you normalize: an escape sequence is `\r\n` in a literal and `\\r\n` in a raw string or a regex, so a normalizer built for one silently misses the other, and the case it misses is the guard flagging itself. When the normalization is a `strip`, strip punctuation only — stripping the escape *letters* mutilates the value at its edges (`test` becomes `tes`, a real key ending in `t` becomes a placeholder), converting a true positive into a false negative, which is the failure mode nobody looks for after loosening a matcher.

- **A guard whose subject is "this public tree must not cite the private one" cannot keep its list of
  private nouns in the file it publishes — the matcher *is* the finding.** A leak guard is written
  inside the tree it protects, so a versioned pattern list naming the protected things (internal
  folders, private document names, a system by name, a person's or a company's name) publishes
  exactly what it exists to hide, in the one file every cloner reads. Split it by who may see the
  entries: **generic forms stay versioned** (a machine-absolute path such as `C:\Users\` or
  `/c/Users/`, the name of a credentials file), and **the specific nouns live in an ignored file the
  guard loads only if present** — one line per entry, `pattern<TAB>what it is`, so the file explains
  itself and a clone without it still runs the generic half. Three obligations come with the split:
  **guard the guard**, with a test that the local file is both ignored and untracked
  (`git check-ignore -q <file>` exits 0 and the name is absent from `git ls-files`), because one edit
  to the ignore file otherwise republishes everything the guard was built to protect; **never print
  the offending line in the failure message** — a public CI log is a publication channel, so name the
  file, the line number and the class of internal, and leave the matched text out; and **state the
  limit**, since a guard over nouns cannot tell a paraphrase from a legitimate sentence, so a rule
  re-worded is not caught and human review of the prose does not become redundant. Corollary for the
  documents themselves: write why a reader exists without citing where it came from — "a previous,
  private investigation" is enough.

 - **A guard that aggregates "every declared input" includes sources the project's own reader
 rejects, and a guard that is red for an unfixable reason gets switched off.** A subject list
 taken as given rather than as the perimeter the project already draws pulls in hand-maintained
 documents beside machine output; the guard then reports a defect on files nobody can make
 conform from here, forever. Measured: 11 of 65 declared inputs failed on format — workbooks,
 not broken exports — against a sibling check that already declared that split. Use the split
 the project already made, and **print the exclusion and its count in the guard's own output**
 (`perimeter: 49 export(s); out of scope 16 workbook(s)`): an exclusion living only in the code
 is read as total coverage, and it hides from whoever could dispute it. A readable manual goes
 out too — its shape changes by hand, so its total moves for a human reason, not because data
 went wrong. See the data-aggregation-guards.md note (load from SKILL.md).
 - **A guard whose subject is a whole dataset must be made affordable by reusing a measurement
 keyed on the input's content hash — never by narrowing what it reads.** The reflex on a
 minutes-long check is to shrink its perimeter or run it rarely, and both reopen the hole the
 guard was built to close. Persist one record per subject under the input's hash and reuse it
 when the hash is unchanged: identical bytes cannot produce a different total, so there is
 nothing to re-read. Measured: ~56 s of parsing collapsed to ~2 s on an unchanged tree, which
 is what made running it on every gate defensible. Two hard edges: the reuse path is
 performance only, so never seal a subject that **failed** to measure (the next run would
 compare a correct figure against a declared hole and pass); and the persisted record is a
 versioned artifact beside the baseline, not a cache — without it the comparison does not
 travel between sessions. Prove it by asserting the real reader was **not called** (swap in one
 that raises), never by timing.
 - **Prove an aggregation guard by reproducing a figure the project already measures from the
 same source by a different path.** Internal tests prove consistency, not that the guard
 measures the quantity it claims; agreement with a pre-existing, independently-plumbed
 measurement of the same file is the cheap strong evidence. Measured: a new column control
 summed a purchases file to the exact figure an existing check computed with its own separate
 code, and a client file to the exact total a third check published. Corollary on the write-up:
 **read every count and duration out of the run log, not from impression** — a duration and a
 count quoted from memory were off by 8x and 2x against what the log had recorded, and the
 validation note and the index cite the artifact rather than the recollection.
 - **When the guard's test extracts subject names from a document with a pattern, the pattern
 is part of the guard — and a pattern narrower than the legal spellings fails in two opposite
 directions at once.** A test that asserts an index names every subject (every command, every
 report) is a guard over the *pattern* as much as over the document. Measured: a regex that did
 not accept a hyphen made one hyphenated command simultaneously absent from the "must be
 named" set and its own prefix present in the "names something nonexistent" set — two
 unrelated-looking failures from one cause, which sends the reader hunting for a stale
 document. Add a fixture asserting the pattern matches a legal spelling that stresses it, not
 merely that the current document passes. This is the general rule that a guard and the test
 that proves the guard are the same subject at two levels.
- **A guard's test that asserts a property of *where it ran* is green in one checkout and red in
  the other — and red there blocks every session that commits there.** Measured: a test asserted
  that a configuration constant (the shared integration root) differs from the module-derived code
  root. True from a linked worktree, false from the integration checkout itself, where the two
  coincide by construction — so the suite passed in every worktree and failed on the trunk
  everybody commits to, stopping every session on a test that proved nothing about the code. The
  property that mattered was a property of the **source**: that the module resolves no artifact
  from the fixed root. Assert *that*, by parsing the module and checking the flagged expression is
  absent, so the verdict is identical in any checkout. The tell is an assertion comparing two
  absolute paths: one derives from `__file__`, the other from configuration, so the test silently
  encodes which tree you happen to be in. General form: a check whose result depends on the
  observer's position measures the observer. Make the tree a parameter the fixture injects, or
 read the artifact — never the environment.
- **A guard that shells out to the project's suite inherits *where* that suite ran: in a linked
  checkout it can report zero findings because its subjects SKIPPED, not because they passed.**
  A check whose subject is "which tests fail without this input" runs the suite with the input
  removed and counts failures — but a test whose fixture resolves a source that is deliberately
  **not versioned** skips in a worktree for an unrelated reason, so exactly the tests that would
  have failed are absent from the count and the guard goes green with a denominator that looks
  healthy. Measured: the guard passed with four failures pending, visible only from the
  integration tree. Give the guard a way to know where it can measure — a
  `motivo_para_no_medir(root, integration_root)` that returns the reason and makes the check skip
  outside the integration tree, with both roots injected by the test — so the false green becomes
  a skip that reads. Three companions. A skip introduced to silence a red is honest only if the
  tests it hides still run where they can, so **count the file's passes before and after adding
  the marker**: identical counts is the evidence that the marker removed nothing but the red,
  and it is also what separates a false positive from a genuine defect that a skip would bury.
  When the project's own hook deliberately excludes the guard (a slow filter, a per-file skip
  list), name inside the guard which loop does run it, because if that loop is a person
  remembering a manual command, the red ages in silence — and say that in the guard's text, not
  only in a commit message. And prefer a declared skip to an invented green: a skip is visible to
  the next reader, a green is not.
 - **When a project guards one register and not its twin, the correct new guard is the sibling's shape
 copied — same severity, same vacuous-green carve-out, same injected-parameter test — not a fresh
 contract.** Registers of the same kind (open decisions and emitted actions, requests and approvals,
 findings and fixes) fail in the same way and deserve the same check; a second, independently designed
 opinion about the same obligation drifts, and the weaker of the two is the one nobody notices. Measured:
 a project required an owner on every open *decision* while the ledger of *actions* it emitted — one JSON
 object per line, one file per date — had no check at all, so entries had accumulated with no owner and
 the gate was green. The mirror took a parameterized root, the same non-critical severity, and the same
 *an empty artifact is red, not green* branch.
 - **An empty work-queue is the most seductive green there is, because it reads as "nothing to do".** A
 check over a register of pending items must treat zero entries as a failure: a queue that never fills is
 indistinguishable from a producer that stopped emitting, and the reader sees a healthy, quiet system.
 Say in the message which of the two it is. Its mirror is a filtering rule — an entry that is *closed*
 (done, discarded) is exempt from the obligation the check enforces, so count only the pending state
 rather than demanding the field on every entry, or the register can never go green once anything
 finishes.
 - **When you add a producer that writes into an existing register, the guards that read that register
 change population — sweep them in the same change.** The new entries are of a new *kind*, and a guard
 whose obligation is keyed to the register as a whole silently includes them: measured, a check
 demanding an owner on every pending entry began counting three machine-emitted entries a day, so its
 count grew without bound and the motive it had declared — which named a fixed number of *other*
 entries — was wrong the first time it ran afterwards. Two wrong repairs and one right one: inventing an
 owner for the new kind breaks the project's rule against inventing owners; suppressing the check loses
 the entries that genuinely need one; the repair is to **classify by kind** (exempt the machine-emitted
 type, keep the obligation on the human-decision type) and **print the exempted count in the message**,
 because an exclusion visible only in the code reads as total coverage. The new kind is not thereby
 unguarded: it carries its own expiry — an entry that ages past a stated window surfaces on its own
 report — and that rule belongs to the feature that emits it, not to the register's shared check.
   **And "sweep the guards" means every consumer of the register, the display ones included — a fix
   applied only to the check leaves the numbers lying in the artifacts people read.** A register's
   population is counted in more places than a check: a summary function, a report's footer line, a
   command's listing. Measured: the exemption was applied to the gate's check and not to the summary the
   report reads, so two counters kept inflating with the machine-emitted kind (19 where the truth was 16,
   17 where it was 14) — numbers that grow every day on their own, which is exactly what makes the reader
   stop believing the line rather than investigate it. Fix the count **at the source the displays read**
   (one summary function, not each call site), and have each display **say the exemption** ("N in the
   machine-emitted queue, which asks for no owner"): a population that silently shrinks in the display
   reads as a defect in the display. The tell to ask about is the **cap**: a list that prints a fixed
   number of rows loses the thing it exists for when a kind of entry that grows on its own enters it —
   measured, six printed rows against three new entries a day, so by the end of the week the work the
   sheet was built to show had been pushed off the page while the total still looked plausible.
 - **A guard over a register the project itself emits is incomplete if it never checks that the producer
 wrote a value where one is claimed.** A field populated with a sentinel for "not measured" — a hardcoded
 zero, an empty string, a placeholder date — makes every aggregate over the register lie, and it is
 invisible to checks about ownership, completeness or count, because the entry is present and
 well-formed. The tell is a field that is uniformly the same value: sample its distribution before
 trusting any sum over it, and make the producer store absence as absence (a null) rather than as a value
 with a meaning of its own. Measured: a ledger's monetary-impact field was hardcoded to `0.0` at emission,
 so summing the register reported "worth nothing" where the truth was "never calculated"; the repair was
 in the producer, not in the check — and the check then had to distinguish the field being *absent* from
 its being *zero*, because a genuine zero there meant something else entirely.
- **Mechanizing a *step* is a different act from adding a check, and it fails in the opposite
  direction: not "someone forgot" but "the robot did it to the wrong thing".** A command that
  changes state must refuse by default and report what it declined. The written rule it replaces
  says *clean up what is already integrated*; the tool reads three states the prose never
  separated — the main tree, the tree it is running in, and a subject carrying uncommitted or
  unmerged work — and refuses all three, acting only where it can prove the subject is its own.
  Give the rest an explicit opt-in flag rather than a cleverer heuristic, print the refused ones
  with the reason, and make the irreversible half follow the reversible one (delete the reference
  only after the artifact is gone; never reach for the `--force`/`-D` form where the plain one
  re-checks what the audit just checked). State the cases it *cannot* decide in its own output — a
  subject that just merged is indistinguishable from one just created while the trunk still sits at
  its tip — because a limit left implicit reads as coverage.
- **A subject that never finishes produces no completion record, so the only evidence it is alive
  is the last line of its own log — and the thing that restarts it must not be a child of a
  window.** Every check above assumes the subject *ends*: it ran, it exited, it wrote a file. A
  service, a long-poll listener, a daemon has no such record, and it is silent exactly when it is
  healthy, so a freshness test on its log cannot tell "working" from "died three hours ago" — the
  file stops moving in both cases. Read the **last line** only as the *explanation*, never as the verdict: a session marker does not
  mean alive — a process killed from outside leaves its own marker as the last line, with no exit
  record after it (measured: three hours of a dead listener whose log still ended in `listening as
  ...`), and **the verdict comes from the process table**, the one source that does not depend on the
  subject's cooperation: enumerate the running processes and match the command line. Two edges make
  such a query trustworthy: **the pattern must be specific enough not to match the querying process
  itself** — a one-token pattern matched the very interpreter running the check, whose own command
  line contains the word, so require the distinctive pair — and **the query must be proven to run at
  all**, by asserting it finds a process that certainly exists (the interpreter running the suite),
  because a query with a wrong property name does not fail: it returns empty, which is
  indistinguishable from the outage it was written to detect. No line for today at all is red, never
  green — that is this class's vacuous-green path — and keep the marker stable and greppable, so the
  explanation stays readable.
  Two mechanisms outside the check are what actually keep the subject up. **The supervisor must not
  live inside a console window**: a starter script in a login folder that loops while the child
  lives dies *with* the child, so closing one window turns a self-restarting job into a permanent,
  silent outage — its presence in that folder is not coverage. A real restart path is a scheduled
  task, a service, or a detached process, and you verify it **separately from the child** (is the
  supervisor itself in the process list?) before believing "it comes back on its own".
  **And the unattended start must not need the network**: a launcher that resolves its dependencies
  against a remote index on every start turns a DNS blip into an outage of the whole job while
  every wheel is already cached locally — resolve once, start offline, and keep the networked path
  as the single explicit fallback for a cold cache or a new dependency. The same rule points
  inward: the process absorbs the transient condition itself, with bounded backoff, instead of
  exiting, or a socket timeout becomes an outage reported as a crash. Measured: a supervised
  listener restarted 76 times in four days and exited 71, 51 of them on one socket timeout, with
  the offline path one flag away the whole time.
  Corollary on the write-up: **fixing why it dies does not fix who brings it back.** A note ending
  "the fix applies at the next restart" states an inference as a fact, and it is false the moment
  the supervisor is down; measure it (did anything restart today? is anything listening now?) or
  write it as a condition with both halves: what starts it, and what would notice if that does not
  happen.

 - **A guard over a cadence that is not installed yet must not be born red, and it must not watch the
  days the cadence physically cannot run.** The rule above — a missing subject is a failure, not a
  pass — is right for a subject that should already exist and wrong for one that is being installed:
  a check demanding today's run of a schedule nobody has registered is red on the very commit that
  installs it, and stays red until the first run, which is the unfixable red that gets bypassed.
  Give it an **activation marker**: a small file outside the versioned tree carrying the date from
  which the obligation starts, written by whoever installs the schedule, with a message that names
  the marker's absence instead of delivering a verdict ("not declared as installed: nothing to watch
  yet"). The off-calendar days are the same defect on another axis — the machine is switched off, the
  task cannot run — so the check reads the calendar and says so rather than reddening a day on which
  nothing was due, **and the hour of the run is that same axis a third time** — a check asking for *today's* run fires from midnight until the scheduled hour, because today's row cannot exist yet, which is a nightly false red on an otherwise healthy tree (gate such a check on the window it describes; and when you meet that red as a contributor, isolate it by calling the check for yesterday and for today with its own date parameter before writing it up as a defect in the data) — and it looks only at the run that is the heartbeat (the one that fires every day
  regardless of findings), because that run's absence is meaningful while a quiet run is not. Two
  obligations keep the carve-out honest: the **date in the marker** is what starts the red, never a
  bare existence check with an unbounded past; and the marker is written the day the first real run
  was measured, not before — until then the guard's own message is the true statement about the
  system.

  **The window needs the hour as an injected parameter, not only the date — a check that reads the
  machine clock is untestable, and every test already written against it silently asserts the hour the
  suite happened to run at** (the same file green at 00:30 and red at 08:00 of one day, so the suite
  carries a flake nobody can reproduce). Give the check an `ahora=None` parameter defaulted to the real
  clock *inside* the function, then re-read the tests that already existed for it and pass the hour
  explicitly in each: they were comparing against whatever time it was. Expect the RED of that change to
  be a signature error on **all** of them (`unexpected keyword argument`) — which proves the parameter was
  missing, not that the new window is right — so also exercise it once with the real clock, outside the
  suite, at a moment inside and outside the window. The reason the check prints is the deliverable:
  "not due yet until its hour" is what replaces the nightly false red.

  - **Mirror of the cadence guard, and its remedy belongs in the message: a check anchored to a
  renewable proof with a shelf life (a backup or restore run, a rehearsal, a fresh measurement of a
  costly thing) expires on its own.** The window is a schedule *you* chose and the tree walks past it
  with nothing changed — so on a gated push it reds every session at once, and the reflex repairs
  (bypass it, declare it, raise the threshold) all disarm it. Print the renewal command beside the two
  numbers that say *why* it expired (the artifact's age and its distance from the tip), size the window
  from the measured commit rate rather than from taste, and have the green line cite the fresh artifact
  so a renewed proof is distinguishable from a stale one. A check whose expiry has no discoverable
  renewal is the unfixable red above with a delay fuse. Renewal procedure: `multi-agent-shared-workspace`,
  the branch-integration-gate.md note (load from SKILL.md).

