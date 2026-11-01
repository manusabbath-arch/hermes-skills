# Auditing instruction files that live outside the tree

The class: files that load into an agent's context *before* it reads the project's own
entry points — a project skill in `~/.claude/skills/` or `AppData/Local/hermes/skills/`, a
per-tool pointer file, a notepad the user keeps beside the repo. They are not in the
documentation tree, so a documentation guard scoped to that tree cannot see them, and
they are read first, so their errors travel furthest.

They fail differently depending on provenance, and the sort comes first.

| Provenance | Regenerated? | Who can edit | Failure mode |
| --- | --- | --- | --- |
| A `synced/`-style cache pulled from a service | Yes, on next refresh | Nobody local | A local fix survives until the next sync, then vanishes with the correction |
| A tool's own shipped skill | On upgrade | Nobody you should touch | Do not edit; treat as upstream |
| Authored on this machine by an agent | No | Whoever owns it; may be refused to an automated pass | **Nothing corrects it and nothing checks it** — this is the class to audit |
| Authored by the user by hand | No | Only the user | Same drift; your write will be refused |

The third row is the target. Nothing regenerates it, no guard covers it, and every session
loads it before reading the repo.

## Measure it claim by claim

Same discipline as auditing a document, but the claims are of four kinds:

1. **A count a command produces.** Test totals, number of subcommands, line counts of the
   files it tells you to read. Measure each against the producer and compare. These are
the claims that go stale fastest, because the code they describe grows.
2. **A hand-copied command list.** A CLI's subcommand list grows mid-project; the doc
   enumerates the commands that existed when it was written. The fix is a pointer to the
   command that prints the list, never the refreshed list.
3. **A tool or install state.** "Not on the PATH", "installed as X", "no remote yet".
   These flip in both directions and the file keeps asserting the old one.
4. **Content copied from the source of truth.** The dangerous class. Compare section by
   section against the file the repo owns: the copy typically preserves prose the source
   has since corrected, so the two now disagree, and the copy is the one that loads first.

Report the stale claims with their measured values, not as "may be outdated".

## Classify a copy: derivative vs sole home

Before pruning, merging, or consolidating such a file, measure how much of it has another
home. Do it mechanically, one item at a time:

1. Split the file into its atomic lessons (one pitfall, one procedure, one warning each).
2. For each, pick a distinctive phrase — a function name, a flag, an uncommon noun — and
   grep it across the source of truth: the rules file, the catalogue of known issues, the
   logs, the validations, the tests.
3. A hit means the lesson already lives somewhere the project reads. Zero hits means the
   copy is its only home.

Then: **rescue the zero-hit items first**, into the source of truth they belong to, with
their own commit — a lesson that exists in exactly one place is one you delete by tidying.
Only after that does the copy become a pointer.

Expect the mixture to be lopsided in the direction that makes this step feel unnecessary:
a file that is overwhelmingly duplication is precisely the one whose residue is
irreplaceable, because nothing forced the residue to be written down anywhere else.

A practical shortcut for the grep pass: the phrases worth searching are the ones that look
like they could only have come from this file — a specific command, a specific flag, a
specific failure string. A phrase that appears in the source of truth verbatim is
derivative by construction; the interesting items are the ones you have to think about.

## Which skills earn their place

When the job is to decide what belongs in a skill library, the useful ordering is by
*evidence*, and the evidence is mostly in the failures the project already wrote down.

- **Rank by measured origin, not by topic appeal.** A skill whose examples come from the
  project's own incident record — a row in its catalogue of known issues, a correction in
  its validation log — is carrying a lesson someone paid for. A skill on an adjacent topic
  with no such trace is a guess about usefulness.
- **A narrow skill that duplicates an existing process has negative value**: it is another
  copy to keep in sync, and the copy is the one nobody runs. Prefer extending the process
  in the place the project already reads.
- **Name the specific external things worth reading, and say what not to take from them.**
  A recommendation to look at a large public collection is not actionable unless it names
  the two or three entries and the reason; otherwise the next session re-derives the
  shortlist.
- **Do not adopt an external tool because it maps onto a process the project already has.**
  A third-party skill that covers onboard / profile / reconcile / validate is evidence the
  project's design is sound, not a reason to install it. Say that explicitly, or the
  reading becomes a migration proposal.

## The report

State, for every instruction file audited:

- the specific stale claims, each with the value the command measured;
- whether a guard covers it, and if not, that the guard's path list is the reason;
- which lessons are sole-home and where they were rescued to;
- which files are off-limits and why, with the ownership step that would change that.

The point of the last two is that the audit's real output is *durable knowledge moved into
the place that is guarded*, not a list of complaints about files nobody can edit.
