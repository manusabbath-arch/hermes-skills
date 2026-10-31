# Mechanizing a step a person keeps skipping

A *check* catches a defect after the fact. Its sibling is turning a manual step into a
**command** — the difference between "we wrote down that someone should tidy the worktrees
when done" and a subcommand that does it. Reach for this when the rule that keeps breaking is
a procedure (clean up when done, rotate this, close that, re-derive the other), not a state.

The failure direction inverts, and that is what makes it a different craft:

| | A check | A mechanized step |
|---|---|---|
| Fails because | someone forgot | the robot acted on the wrong subject |
| Safe by | reporting what it did not measure | **refusing** what it cannot prove is its own |
| Verified by | a fixture that must go red | both branches of every refusal, and the action |

## Design rules

1. **Refuse by default; act only on what it can prove is its own.** A command that changes
   state inherits every ambiguity the prose never had to resolve. Enumerate the states the
   rule collapsed into one phrase — for "clean up what is already integrated": the trunk
   itself, the tree the command is *running in*, and a subject carrying uncommitted or
   unmerged work — and refuse all of them, acting only where ownership can be demonstrated.
2. **Give the rest an explicit opt-in flag, never a cleverer heuristic.** A flag that says
   "include the others, and I have verified nothing is using them right now" is honest about
   the judgement the tool cannot make. A heuristic that tries to guess whether a subject is
   live (age, recent writes) is a guess with the same blast radius.
3. **Print every refusal with its reason**, in the same run that acts. The declined list is
   what makes the command trustworthy the first time a reader sees it not doing something.
4. **Make the irreversible half follow the reversible one**, and use the form that re-checks
   what you just checked. Delete the artifact first, the reference to it second; prefer the
   plain form of the destructive verb over its `--force`/`-D` variant precisely because the
   plain one re-verifies the precondition the audit reported. Ordering is not style here: a
   reference deleted before its artifact is an orphan, and its inverse is a data-loss window.
5. **State the cases the tool *cannot* decide, in the tool's own output.** A limit left
   implicit reads as coverage. The canonical one: a subject whose work was integrated moments
   ago is indistinguishable from one created moments ago while the trunk still sits at its
   tip — so it is never a default candidate, and the tool must say so rather than guess.
6. **A report-only first version is legitimate and often correct.** Making the population
   visible (what is a candidate, what is not, and why) is a complete deliverable; flipping it
   to delete is a second change with its own risk.

## Proving it safe

- **Test every refusal branch as its own fixture** — the trunk, the tree the command runs in,
  the dirty subject, the subject belonging to someone else — and assert both that it declined
  *and* that the reason names why. The refusal paths are the product; the action path is the
  part a user notices.
- **One fixture must be the subject it *does* act on**, with the action asserted (the artifact
  gone, the reference gone, the survivor untouched). A tool that refuses everything passes
  every safety test and does nothing.
- **Run it on the real tree before believing it**, and record what it declined: that run is the
  evidence, and the declined list is what tells you the refusals are calibrated rather than
  accidental.
- **Make the discovery order the same order the tool applies**: if the tool identifies
  candidates by a query over version control, remember that registrations and on-disk remnants
  diverge — a directory the tool has already forgotten is invisible to it and cannot be its
  subject. Say which population it walks.
- **A dry-run/listing mode that shares the code path with the acting mode is worth more than a
  separate "what would happen" implementation**, because a second implementation drifts from
  the first and the one people read is the one that drifts.
