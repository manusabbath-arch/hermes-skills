# Guards over your own declarations
## Contents

- See headings below. Load this file when SKILL.md points here.


A fourth shape beside the static probe over source, the comparator over prose, and the
aggregation over a dataset: a guard whose expected value comes from a **declaration you
wrote about the artifacts you publish** (a table's columns, its format, its identity), and
whose job is to prove the declaration and the artifacts still agree. It answers a different
question from the other three. They ask "is the code/rule/data still right"; this one asks
"is what I promised my consumers still what I ship".

It exists because the alternative is a consumer reading your output by position: the day a
column moves or a file's shape differs from its sibling, that consumer breaks **in silence**,
and no input guard notices, because nothing was wrong with the input.

## 1. Declare per artifact, and let the artifact be the judge

One entry per published artifact: a **stable name**, the column list with each column's type
and meaning, the **format** (separator, decimal mark, encoding/BOM, line ending, header
present or a fixed fields-per-row), and the identity that makes the number traceable
(which legal entity, which cut-off date, the source's content hash). The name must be stable
precisely because the consumer hard-codes it: a table whose file name carries the run date is
a snapshot, not a table.

Two ordering rules inside the check, both learned by getting them wrong:

- **Emit the shape findings before the value findings.** A missing column, an unexpected
  column, or a changed order is one finding each, reported as such; if you let a wrong column
  list fall through to the per-value checks, each of those checks reads the wrong field and
  reports plausible nonsense under a neighbour's name.
- **Resolve every column against the header the artifact actually has**, never against the
  order the declaration lists. This is the same rule the SKILL.md pitfall states in the
general case; here it is load-bearing, because the declaration is the one thing you are
allowed to be wrong about, and the check exists to find out.

## 2. An artifact nobody declared is itself a finding

The completeness property is what keeps the declaration from rotting into a subset nobody
notices is a subset. Enumerate the artifacts that actually exist (the version-controlled
listing of the output directory is the honest denominator, not a glob you can quietly widen)
and subtract `declared` and `explicitly exempt`. Anything left over is a finding, not a
silent pass. Report the inspected count every run.

The exemption list is a declaration too: **one reason per entry**, and the count of exempted
artifacts printed in the guard's output, or it becomes a permanent amnesty. If the project
already has "which declared inputs are missing" for its sources, this is the mirror of that
same guard — reuse the shape rather than inventing a second idiom.

Two mechanics of that completeness check, both of which belong in its message. It counts the
**version-controlled** listing, so a brand-new artifact is red between creation and commit —
by design; the consequence is that the artifact and its registration land in the **same
commit**, with the project's own registration command as the fix path rather than a hand-edit
to the listing. And because that listing is what makes it fire, the red names a path the
committer never touched, which reads as a foreign block until you recognise it as the artifact
you just created — so put the artifact's own name first in the message, before the diagnosis.

## 3. Measure the whole corpus before writing the declaration

A corpus of exports is not uniform, and the files that share a name are the ones that differ.
Every one of these was found by measuring, none by reading one representative file:

- **Siblings that share a slug but not a shape** — a variant with an extra leading or
trailing column, or a file the declaration gave the sibling's full column list when it really
  has four columns and is a different artifact entirely.
- **A decimal mark that differs in an isolated pair** of otherwise identical files. Reading
  `7.677` with the wrong decimal mark gives 7677, no error.
  - **Values that are numbers but not in the shape your numeric test expects**: scientific
    notation, and percentages carried as formatted strings (`'15.9%'`). These are not
    "non-numeric"; the type vocabulary needs a member for a formatted magnitude, or the
    declaration is wrong, not the data.
- **Headerless series** (a field-per-line format). Declare fields-per-row, not columns, and
  keep that count in the contract for the same reason columns are.
- **BOM present on some files and not others, and line endings that differ from what the
  repository stores.** Version control may normalize line endings on checkout, so the working
  tree and `HEAD` can disagree — and when the normalization is a property of the checkout
  itself (an `autocrlf`-style setting), the disagreement is not a defect in any artifact:
  measured, every published file reported `i/lf w/crlf`, so a disk-vs-declaration line-ending
  check is red on all of them by configuration. Rule: **check only the format properties the
  producer controls; a property owned by the checkout is not a data property.** Drop it from
  the guard and record the exclusion where the field would have been, or assert it against
  the *stored* blob rather than the working tree. A check red for every file in the tree is
  not strictness; it is the check everyone learns to skip.

Rule: derive the declaration from a measurement pass over **every** artifact, and when the
declaration and the artifact disagree about *which* columns exist, the artifact is the
evidence and the declaration is what changes.

## 4. The consumer side is half the contract

A contract that only guards inputs is half a contract. The rule for whoever consumes the
output — a BI tool, a dashboard, a colleague's spreadsheet — is that they read the **gated
output**, never the raw export, because the project's reader exists precisely to refuse what a
consumer swallows without complaint: a legacy workbook that truncates at a row ceiling and
opens fine, subtotal rows that double a total when grouped. Point the consumer at the raw
source and every guard between them becomes decorative.

Say plainly which parts of the path are not built yet (the refresh that still needs a human,
the credential that has to be rotated before anything is automated), so the contract is not
mistaken for the finished pipeline.

## 5. Verification

- Flip one defect by hand and watch the guard go red **naming the artifact and the column**,
  not just the file.
- Point it at a tree with no artifacts, and at a declaration that declares everything: the
  first must be red (a missing subject is a failure), the second is the vacuous green this
  shape is most prone to.
- Fixtures for each finding type, including the variant whose column list differs from its
  sibling.
