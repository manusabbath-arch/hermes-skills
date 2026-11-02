---
name: documentation-drift-audit
description: "Use when auditing docs against the system they describe: stale facts, stale advice, broken wikilinks, orphans from the entry point, and a mechanical integrity check that must print its denominator before a clean result counts."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, audit, drift, knowledge-base, obsidian, markdown, links]
    category: productivity
    related_skills: [agent-ready-project, grounded-citations]
---

# Auditing documentation for drift


## Cuándo NO aplicarla

Si el pedido es corregir una frase o un typo, se responde **solo eso**. Esta skill aplica
cuando hay que **auditar un árbol de docs** contra el sistema que describe.

For the task "read the docs and bring them up to date" — a documentation tree, vault,
runbook set, or wiki that *claims* to describe a system: its structure, its counts, its
rules, its open items. Also for the narrower question "can I trust what this says?"

## The premise

**A document that describes a system is a set of claims, and every claim drifts.** Docs
are written when something is true and are not re-verified when it stops being true. So
the work is not "read carefully and improve the prose" — it is **verify each claim
against the thing it describes, mechanically where possible, and then correct with a
trail.** Reading carefully is how you miss the stale number; it looks exactly as
convincing as the correct one.

Three failure classes cover most of what you will find, and they need different fixes:

| Class | Example | Fix |
| --- | --- | --- |
| **Stale fact** | "8 checks pass" when the registry has 16 | Correct the number, or better, replace it with the command that produces it |
| **Stale advice** | A TODO telling the reader to do something now known to be harmful | Mark it explicitly as *do not do this*, with why — highest-value fix in the whole pass |
| **Broken structure** | A doc no index links to; a wikilink to a note that was renamed | Repair the link, or link the orphan |

## Procedure

1. **Inventory the tree before reading anything.** Every markdown file, excluding the
   tooling directories (`.git/`, `.obsidian/`, and any tool-owned cache like `.hermes/`).
   Build the set of note names; the link check below needs it. **Then inventory the other
   perimeter: the instruction files that load *before* the tree** — project skills in a
   tool's own skills directory, per-tool entry files elsewhere on the machine. They are
   not in the tree, so no tree guard covers them, and they are read first, so a stale
   claim there propagates further than one inside it. List them separately and audit them
   with the same pass (see `references/instruction-file-audit.md`).
2. **Run the mechanical integrity check first** — it is cheap and it finds things reading
   will not. Broken `[[wikilinks]]` and documents not reachable from the entry point:

   ```bash
   uv run --quiet python scripts/check_docs_integrity.py <vault-root>
   ```

   `scripts/check_docs_integrity.py` in this skill does both and exits non-zero when
there is anything to fix. Run it again at the end of the pass: **the pass is not
finished until it reports zero on both counts**, and that is a machine verdict, not
your impression.
3. **Identify the entry point and treat it as an index, not as a document.** One file
   (a README, a home/panel note) is where a reader lands. Every doc has to be linked
   from it, or it is invisible. Orphaned docs are the most common structural finding and
   they are invisible to a reader who never knows they were looking for one.
4. **Verify the numbers, in code.** For every count, total, threshold, or list length
   stated in prose, find the thing that produces it and run it. Never re-derive it by
   hand from what the doc says. Where a number is produced by a command, the durable
   fix is to write **the command** in the doc (`run X to list the checks`) rather than
   the number — see the pitfall below. When the check finds nothing, **verify it
   inspected something before reading the result as "clean":** print the denominator
   (documents scanned, links resolved) and treat a zero as a broken check, not a pass.
   A validator over an empty or unreadable tree reports no problems — the same output
   as a healthy one.
5. **Look specifically for advice that has been overtaken by the work.** The dangerous
   class is a TODO or recommendation whose premise has since been disproved. A reader
   follows those — they are written as instructions. Strike them and say why.
6. **Correct in place, and keep the trail.** Do not silently overwrite; the value of a
   validation log or a decision record is that a reader can audit *what changed and
   when*. Concretely:
   - Add a dated block at the top of a superseded document saying it is the picture of
     that date, listing what has since changed, and pointing at the live index for the
     current state. Leave the body alone.
   - For a corrected line, strike the old text and put the new claim beside it with the
     date and the reason. The old number is evidence, not garbage.
   - Fix a wrong bullet in place — edit the sentence that misled. Do not append
     `UPDATE:` underneath a wrong statement and leave the wrong statement standing; the
     next reader reads the first thing they see.
7. **When two documents contradict each other, report the contradiction — do not pick a
   winner.** If the documents disagree and nothing you can run decides between them, that
   is a finding about the system, not an editing task. Write it up as an open question
   with each reading and what would settle it, and warn against relying on the disputed
   value until then.
8. **Re-run the integrity check and report what you changed.** End with the list of
   corrections, not a description of the process.

## Pitfalls

- **A stated quantity that a command can compute (a number of files, of checks, of
  sources, of rules) should be written as the command, or with the command beside it.**
  During a single pass the true
  value can change several times, and a doc that was correct when you started is wrong
  when you finish — so **re-measure immediately before writing, and prefer the command
  over the number** wherever a future reader would otherwise trust a stale figure.
- **Before building any doc-side mechanism to keep numbers honest, check whether the
  codebase already has one — and if it does, cite the command instead of building a
  parallel one.** A project that verifies its own figures (a check registry, a test
  that asserts stored totals, a smoke command) already re-measures them on every run,
  which is strictly better than anything you can keep in prose: it fails loudly instead
  of silently ageing. Adding a second, documentation-level register of the same numbers
  creates the divergence it was meant to prevent — two places to update, and the doc
  copy is the one nobody runs. Inventory the guards first; if the numbers are already
  gated, the durable edit is a pointer to the command that prints them. The distinction
  that keeps this rule from being over-applied: a **comparator is not a duplicate
  register.** A register is a second place the value is *stored* — two copies to update,
  and the doc copy is the one nobody runs. A comparator stores no value: it reads what
  the code produces and what the prose says and fails when they disagree, which is
  exactly what nothing does when a number is written by hand. So when the project
  already computes its figures but nothing checks them against the documents that cite
  them, adding that comparison is the missing guard, not the divergence. Related trap in
  the other direction: do **not** manufacture drift. Measure the most-cited figures
  before writing a word about staleness — if they verify exactly, that is the finding,
  and "no corrections needed here" is a legitimate result to report rather than a
  reason to look harder for something to fix.
- **An index/link check that enumerates *tracked* files reports a brand-new note as a broken
  link until it is staged.** A vault that is also a repository answers "does this link
  resolve?" against what version control knows, not against what is on disk, so a note you
  just wrote and have not added comes back as "link with no file" — a verdict shaped exactly
  like a renamed or misspelled target. Stage the new document before reading the check's
  result, and when a link failure names a file you can see in the tree, check its staging
  state before hunting for a typo in the anchor.
- **Verify the tree after editing, not while reading it.** Wikilinks break because a note
  was renamed, and orphans appear because a new note was never linked. Both are
  introduced *by the editing pass itself* as often as they are pre-existing. The final
  check is a gate, not a formality.
- **A pending item that nothing can reach is not pending work — measure the path before
  queueing it.** A TODO list is audited for items that are *done* or *contradicted*, and the
  third case is missed: an item that is still literally true but which no code path, reader or
  process can arrive at — a gap that only fires if something later consumes a source nobody
  consumes today. Check reachability mechanically (grep real call sites, resolve the cited
  path, count the readers) instead of reasoning from the wording, then move those items out of
  the list as **latent**, saying what would make them live. Leaving them in inflates the
  backlog, and an inflated backlog is what makes a reader stop reading it.
- **A document recommending a specific action deserves a harder look than one stating a
  fact.** A stale number misleads; stale *advice* gets followed, and following it is
  often worse than the original problem. Read every TODO and recommendation with the
  question "is the premise of this still true?" — and check whether the recommended
  action would now actively undo a fix.
- **When you correct in place by script, preserve the file's own line endings — detect them
  from the content, never from the extension.** There is no "the tree's line ending": it is
  per file and can change between commits when another writer rewrites one, so a multiline
  match on a file whose endings you assumed fails with "not found" while the text looks
  identical, and on a source file it inserts the wrong ending and breaks the linter. Read
  the raw text, assert the anchor occurs exactly once, replace, write, then re-count. Use
  `io.open(path, mode, encoding=..., newline="")` for both the read and the write: it works
  identically whether the code lives in a `.py` or is piped through stdin, whereas
  `Path.read_text(newline=...)` refuses the keyword when called from stdin — and stdin is
  how a one-off edit gets applied when the endings have to be preserved. A failure there is
  a fact about the call site, not a sign the rule is wrong.
- **A repo whose commit gate runs the project's full check suite will exceed the tool's
  foreground timeout, and the timeout message does not mean the commit failed.** Land the
  commit as a tracked background process with its output redirected to a file
  (`background=true, notify=true`), then read that log — it holds the gate's full verdict
  (counts, pass/fail per stage, whether the suite was skipped) and doubles as the evidence
  for your report, so the gate never has to be run twice. Then **verify with
  `git log --oneline -1` and `git diff-tree --no-commit-id --name-only -r <sha>`**; the
  second also proves the explicit-path commit did not carry another writer's files along.
  Never treat `echo launched` or the tool's timeout as the commit's outcome: a commit
  killed before it runs leaves no log, no lock and no error. The same holds for a **push**:
  a pre-push hook (backup, gate) takes it past the timeout and the call reports the timeout
  while the push completes, so verify the effect against the remote — `git ls-remote origin
  refs/heads/<branch>` compared with `git rev-parse <branch>`, plus a `git status -sb` line
  with no ahead/behind — and never against the call's exit message.
- **Do not "clean up" history to make it consistent.** Correcting a log or a decision
  record by editing its past entries destroys the only thing it was for. Supersede with a
  new dated block; never rewrite.
- **A dated report citing a source version that has since been replaced is a version pin,
  not drift — recompute the figure against the version it names before correcting anything.**
  A freshness check keyed on file hashes flags exactly this on every re-export, and it reads as
  "this report is wrong", so the reflex is to re-derive it against today's file. But the report
  claims what was true of the export it names, and the project's own archive usually still holds
  those bytes: hash-match the cited version, recompute from that, and if the figure holds the
  document is correct *as history*. Two consequences: correct forward — the old report stays as
  written and the new documents cite the new version — and keep "the source this report names is
  no longer the current one" separate from "the number in it is wrong". Collapsing the two sends
  a pass rewriting dated documents that were never wrong, which is the history-rewrite below by
  another door.
- **Docs that cite a file, path, or command that no longer exists.** Grep the cited
  paths and check they resolve. A doc pointing at a deleted script is a reader sent on a
  dead end, and it is invisible unless you resolve the references.
- **Arithmetic inside the prose is a free pre-check: counts that disagree with each other
  are wrong before you measure anything.** A sentence that says "6 of the 41 sources" and
  then reasons about "those 22 sources" contradicts itself — 41 minus 6 is not 22 — and the
  contradiction is visible without opening the code. Scan every paragraph that carries two
  or more counts for the internal relation between them (total minus subset, sum of parts,
  "the other N"); a break means at least one figure is stale, and it usually means both are,
  since neither tracks the source. Then verify against the producer. This is the cheapest
  drift signal in the pass and the easiest to read past, because each number looks fine in
  isolation and the prose around them is fluent.
- **Another writer on the same tree.** If anyone else edits it (another agent, the user,
  a sync process), re-read a file immediately before patching it and stage your own files
  by explicit path. A doc you read early in the pass may have changed underneath you, and
  a sweeping add commits their work in progress. When the audit's findings are reported
  **by line number**, freeze the subject first and prove it did not move: record the file's
  `sha256sum` plus `git log -1 --format=%h` and the clock time before starting, state that
  photo in the report, and re-hash before delivering. A citation whose line no longer holds
  what you quoted is worse than no citation, and a file edited mid-pass invalidates every
  reference in the document — so the hash check is part of the deliverable, not politeness.
  This is also what lets you audit a file another writer is actively working in: you are
  reporting on the version you can name.
- **A document's own self-description drifts too, and it is the class most likely to be
  missed.** A file that describes a corpus is the corpus's most authoritative-looking member
  and nothing measures it: the entry-point panel keeps a count of documents "today", the
  README keeps a test count, a tools note keeps a list of commands, and all of them were true
  once. Audit them against the system exactly like any other claim — and when the count is a
  live list (documents present, validation notes registered), the durable fix is to have the
  *guard* enforce membership and count both directions, not to update the number. The check
  that only walks one directory passes while the sibling directory fills with orphans: the
  orphan set has to be computed per directory and reported per directory, or the blind spot
  survives the fix that was written to close it. Two subtleties when wiring that check: an
  output the index cites by filename in ordinary text (not as a link) also counts as indexed,
  so match the raw text and not only the link syntax; and only link documents whose content
  is *comparable* — linking an index entry to a document with no verdict block changes what
  the other checks compare against it, so scope the new links deliberately.
- **When two artifacts answer the same question from the same source with opposite results,
  the missing declaration is usually a parameter someone typed.** Two reports over one input
  can disagree without either being wrong: the divisor, the period, the filter or the
  granularity was supplied by hand and only one of them recorded it. The tell is a result
  ratio that matches the parameter ratio (two runs with periods differing ~10x reporting
  counts differing ~10x). Treat such a parameter as a declared assumption that has to appear
  next to the figure it drives, and treat the *name of the output* as part of the problem:
  if a parameter or an input *type* selects which file gets written, then changing the
  parameter leaves two different files published, both plausible, with nothing saying which
  one is current. Name outputs stably so a re-run **replaces** its predecessor; dates and
  provenance belong inside the document, not in a name that varies with the inputs.
- **A percentage that a formatter rounds, or that renders with a thousands separator where a
  decimal belongs, is a data error wearing cosmetic clothes.** Locale-formatting helpers put
  `.` between thousands and `,` for the fraction, so asking for three decimals of `3.1998`
  prints `3.200%` — a difference of three percent that reads as three thousand, and a reader
  discards it at a glance. Compute the arithmetic separately from the rendering and check the
  rendering on a number whose rounded form is obviously wrong (a small percentage, not a
  large one — a big value's thousands group masks the defect). It is worth a guard because it
  never raises: only the reader is wrong, and the document looks fine to grep.
- **The deliverable language is not your choice.** Match the language and register of the
  tree you are editing, and follow the local conventions of the index note (heading
  structure, how links and dates are formatted) rather than importing a style you prefer.
  This covers the audit's own output too: when the tree is written in another language,
  write the corrections, the new index entries and the validation note in that language,
  and put the audit's reasoning there rather than in your working language.
- **A claim of the form "N of M" carries two figures and both drift; resolve the universe
  from the producer before measuring either.** Counting the files on disk is not measuring
  M. The code usually keeps its own registry (a declared-keys table, a contract mapping, a
  config list) and that registry — not the directory listing — defines the population the
  sentence is about. Measured: a document asserted a rule was unenforced "in 22 of the 26
  sources" while the producer's registry held 28 entries, 24 of them without the
  declaration; the subset had grown *and* the denominator had, so the cited ratio was wrong
  in both directions and reading it as "slightly stale" hid the size of the gap. Find the
  function or table the code enumerates with, call it, and compare against that output.
  Deriving a denominator by listing files is the same defect as deriving the numerator by
  hand.
- **A drift detector built from a keyword list is itself a coverage claim, and nothing
  checks it.** When the pass leans on a regex or a fixed vocabulary to find hand-written
  figures, the misses are silent by construction: the pattern matches the terms whoever
  wrote it happened to think of, and the term that drifted is exactly the one it had no
  reason to include. Measured: a detector covering `pares|chequeos|claves|validaciones`
  could not see the stale figures it existed to catch, because both were stated about
  `scripts` and `fuentes`. So when the finding is **"the detector did not flag this"**, the
  durable output is a widened pattern — add the vocabulary the pass proved is citable — not
  a hand-fix of the single number you happened to notice. And state the searched vocabulary
  as a caveat when reporting: "no drift found" over an unlisted term is a pass for work
  that never happened, the same shape as a validator over an empty tree.
- **Check whether the stale claims are already being repaired by someone else before
  reporting them as open.** Re-read the flagged lines at the end of the pass, not only at
  the start: another writer may have replaced a hand-written figure with the command that
  produces it while you were auditing, which is the correct fix and not a finding. Report
  the ones still standing, say plainly which were already resolved, and never "re-fix" a
  line that was just fixed correctly — a second edit to a shared file races the writer who
  made the first one.

- **Before recommending a pending item to the reader, grep for it already closed.** The
  stale advice you must fix is not only what stays in the tree — it is what you *repeat
  outward*. A document's findings section can list an action as open while a
  closure/update block further down the same file records it as done, and the entry-point
  panel already reflects it; recommending from the top of the file sends the user to redo
  finished work. Check in this order: does the document have a later closure or update
  section, does a repo-wide search for the item's identifiers (`grep -rl "<id>"
  --include='*.md' .`) find a newer record, and what does the newest index entry say. Then
  look for the **second half, which is more silent**: an *impact claim* attached to that
  item that was never measured and is likely false. Measured: a doc asserted that while
  certain records stayed unconfirmed "every figure of this kind keeps understating by a
  growing amount", while the validated formula filtered exactly those records out and the
  total did not move when they were closed. Correct both — the open item *and* what was
  attributed to it — and check each cited document, because an unmeasured impact claim
  gets copied from one document to the next until someone measures it.
- **A tracker or board row is a claim like any other, and it is the one that gets read.**
  A status table (open items with owner, trigger and last update) is a *derived* layer over the
  records it summarises, and it drifts the same way prose does — worse, because a row that names
  work as pending is exactly what someone acts on. Measured: a board row still said "the
  comparison against the master has not been run" while the note the row itself linked to
  recorded that comparison resolved **the same day** — and the board's own header declared the
  derivation order ("if anything differs from the note, the note wins"). Two rules. **When the
  document set declares a precedence between a summary and its source, the stale text is in the
  derived layer, and both get corrected** — fix the row, do not delete it, since the tracker is
  what the reader actually opens; and leave the row in place with the resolved value and the link
  rather than removing it from the list. **Read the last section of each linked record before
  trusting any row's status** — a note accumulates dated updates under its original verdict, so
  the status word at the top of the target can be current while the row summarising it is a week
  stale. This is the same check as the findings-section one above, applied to the layer that
  reads as authoritative because it is a table.
- **Do not answer "what is still pending?" by reading — run the entry points.** The pending
  documents (roadmap, tracker, backlog, the list of floating work) tell you what *was* pending,
  and the whole point of re-auditing is that the system moved since. Execute the project's own
  analysis commands and its gate before reporting the backlog, because a regression that no
  document records is exactly what the pass is for: measured, the main analysis entry point was
  returning **zero** results where the published report carries hundreds, and no roadmap,
  tracker or log mentioned it — the defect was seven days old and only visible by running the
  thing. Treat a zero, an empty output file and the phrase "the artefact is unchanged" as the
  strongest signals available: all three mean a pipeline is producing nothing, and the first
  suspicion is that an input changed shape. Then report the backlog **with what running it
  proved**, not as a list transcribed from the documents.
- **An instruction file that loads before the tree is in the perimeter even when it lives
  outside the tree, and the tree's own guard cannot see it.** Verify such a file claim by
  claim like any other doc: extract every figure a command can compute (test totals,
  command lists, line counts, tool install state) and measure it — the prose around a
  stale number reads exactly as convincing as around a correct one. Two shapes recur, and
  the second is the dangerous one: a hand-written **count**, and **content copied out of
  the source of truth**, where the copy keeps the wording the source already corrected and
  the two versions contradict each other with nothing telling the reader which is current.
  The durable rule is the one the repo applies to its own entry files: point at the file,
  never restate it. State the blind spot in the report — a guard scoped to the repo root
  resolves the paths it was handed, and this file is not one of them.
- **Before pruning or merging a copy, prove every item in it has another home; the items
  that do not are the ones you cannot delete.** Such a copy is usually a mixture: mostly
  derivative, with a minority that is the only place a lesson was ever written. Classify
  mechanically, not by reading — for each self-contained lesson grep a distinctive phrase
  from it across the source of truth (rules, catalogue, logs) and count hits. Zero hits
  means deleting the copy loses the lesson outright, so **rescue those first**, into the
  place the project reads from and with their own commit, and replace the copy with a
  pointer only afterwards. This holds when the intent is consolidation rather than
  deletion: the same measurement says which part of a long file is worth keeping, and a
  merge that skips it drops precisely the knowledge that had no other copy. Measured on
  one such file: of thirteen lessons checked, nine already lived in the project's own
  catalogue and four existed nowhere else — a file that is 70% duplication is also the
  sole record of the rest.
- **If the file you must correct is user-owned, you may be refused the write — report the
  drift and put the correction where you *can* write.** Instruction files a user authored
  (rather than an agent, or a tool's own generator) can be off-limits to an automated
  pass. Do not retry, and do not leave the finding unrecorded: state the specific stale
  claims with their measured values, say which guard does not cover the file, and
  recommend the ownership step that makes it editable (`hermes curator adopt <name>` for a
  Hermes skill). Land the durable half of the fix in the source of truth in the meantime —
  the lessons that exist only in the copy are still at risk while it stays unowned.

## Support files

- `scripts/check_docs_integrity.py` — resolves every wikilink against the set of note
  names and reports documents unreachable from the entry point. Exits non-zero when
  either check finds something, so it can gate the end of a pass.
- `references/instruction-file-audit.md` — auditing the instruction files that load before
  the tree: why they are the highest-risk docs, how to classify a copy into derivative vs
  sole home, how to choose which skills in a library earn their place, and what the report
  has to say about the guard's blind spot.
- `references/auditing-an-external-proposal.md` — the neighbouring task: a plan, vendor
  proposal or outside recommendation about *this* system, written by someone who could not
  see it. How to triage it front by front against measured state, what sections the
  deliverable needs, and why the output is a project document rather than a correction of
  theirs — plus the variant where the outside document is still live, in which case its
  numbers are fixed in the file and the audit is logged in the project instead.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/documentation-drift-audit`). Editar acá, nunca la copia instalada.
