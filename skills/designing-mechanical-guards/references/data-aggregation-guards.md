# Guards whose subject is a dataset, not a file
## Contents

1. Its perimeter is the list of sources the project already calls its own
2. What may be aggregated: an enumerated vocabulary of *meaningful* magnitudes
3. Cost: persist the measurement keyed by content hash
4. Proving it measures the right quantity: reproduce an independently measured figure
5. A test's own pattern is part of the guard


A third shape beside the static probe over source and the comparator over prose: a guard
that **aggregates** — sums magnitudes, counts rows, compares a total against the previous
run. Its subject is the contents of large data files, which changes three things: what may
be aggregated, what the guard costs, and how you prove it measures the right quantity.

## 1. Its perimeter is the list of sources the project already calls its own

An aggregation guard over data has a subject list someone typed, and the list that comes
first is usually *every declared input* — which includes sources that cannot be read at all:
hand-maintained spreadsheets beside machine exports, files in a format the project's own
reader rejects by design.

Measured: of 65 declared inputs, 11 failed with "no recognizable header row in the first 10
rows". They were not corrupt data — they were hand-maintained workbooks that the project's
`read()` refuses on format, and the project already had a precedent for the split: a sibling
check declaring *"out of scope: N manual workbooks, which do not follow the export format"*.
Leaving them in produced a guard that is **red forever for a condition nobody can fix from
here**, which is how it gets switched off.

The rules:

- **Use the perimeter the project already drew**, not a new one you invent. If a sibling
  check already separates "machine exports" from "human workbooks", read that same split.
- **Declare the exclusion with its count, in the guard's own output** — `perimeter: 49 export(s);
  out of scope 16 workbook(s)`. An exclusion that only exists in the code is read as total
  coverage by every later reader; one printed on every run is an assertion someone can
  dispute.
- **Exclude a readable manual too.** A workbook that *does* parse is still not a subject: its
  shape changes by hand between versions, so its total moves from a human edit rather than
  from data going wrong — which is the thing being watched for. The distinction is the
  **source of truth**, not whether the parser happens to succeed.
- Pin the perimeter with a test that asserts the count equals `all declared - excluded`, so
  the split cannot drift from the project's own lists.

## 2. What may be aggregated: an enumerated vocabulary of *meaningful* magnitudes

"Sum every numeric column" is the naive form and it is wrong. Numeric-looking columns that
are not magnitudes — identifiers (record ids, document numbers, tax ids, personal ids),
coordinates, phone numbers — produce a large meaningless total that **moves whenever rows are
reordered**, which is a false-positive surface, and repeated false positives are what gets a
check disabled.

- **Declare the vocabulary explicitly and extend it deliberately**: the tokens for money
  (`total`, `amount`, `balance`, `discount`, `tax`, `gross`) and for physical quantity
  (`quantity`, `units`, `weight`) are the subject; everything else is not.
- **Match on tokens, not substrings.** Split the header on non-alphanumeric characters and
  compare candidates for equality against the vocabulary; a substring matcher flags a column
  whose name merely contains a watched word. Normalize accents but **keep separator
  boundaries**: stripping the dots of `C.I.` must yield the token `ci`, not `ci`-smeared-into
  a neighbour, and a naive `\w+` extraction drops the abbreviation entirely.
- **Reject a column whose header is empty.** A delimited export with a trailing separator
  leaves a **phantom unnamed column** that sometimes carries a stray value. Measured: a
  client file reported `col37 = 1641.0` from the empty header — a parse artefact being summed
  as if it were a figure.
- Test all three: a watched column is kept, an identifier column is dropped, an unnamed
  column is dropped.

## 3. Cost: persist the measurement keyed by content hash

An aggregation guard must read everything, so its cost is proportional to the dataset —
minutes, not milliseconds. The reflex (shrink the perimeter, run it less often) is what
reopens the hole. **Persist one record per subject keyed by the input's content hash and
reuse it when the hash is unchanged**: identical bytes cannot produce a different total, so
there is nothing to re-read.

Measured: a full pass over 49 files cost ~56 s of parsing; the next pass, with every hash
matching, cost ~2 s — which is what made running it on every gate defensible instead of a
"nine-minute check that turns itself off".

The design points:

- **The artifact is a first-class, versioned output** (beside the baseline/registry), not a
  cache. Without it in the repository the comparison does not travel between sessions and the
  guard certifies nothing.
- **Reuse only on a matching hash, and fall through to a real read on any mismatch or any
  inability to hash.** The short-circuit is a performance path, never a correctness path.
- **Never seal a subject that failed to measure.** If the record for a failed read were
  written, the next run would compare a correct figure against a declared hole and pass.
- **Prove the short-circuit by asserting the reader was NOT called**, with the reader replaced
  by one that raises. A timing assertion is flaky and proves nothing about the mechanism.
- Because every subject's hash is hashed on every run, a stale artifact is self-correcting:
  you only pay the parse where something actually changed.

## 4. Proving it measures the right quantity: reproduce an independently measured figure

The guard's own test suite proves internal consistency only. The evidence that it measures
what it claims is that it **reproduces a figure the project already computes from the same
source by a different path** — no shared plumbing, no value passed in. Measured: a new column
control summed a purchases file to the exact figure a pre-existing check had already measured
with its own code, and a client file to the exact total a third check reported. Two
independent agreements is the strongest cheap evidence available for an aggregation guard.

Corollary for the write-up: **read every measured number out of the run log, never from
impression.** A duration quoted from memory ("about seven minutes") was off by 8x against the
log's recorded 56 s, and a count quoted from the same memory was off 2x; the log had both.
The validation note and the index cite the artifact, not the recollection.

## 5. A test's own pattern is part of the guard

When the guard's test extracts subject names from a document — a docstring that must name
every command, an index that must list every report — the **extraction pattern** is as much
the guard as the comparison is. If it under-matches the legal spellings of the subject, one
name fails the whole test set **in two opposite directions at once**: absent from the "must
be named" set, and its own prefix present in the "names something nonexistent" set. Two
unrelated-looking failures, one cause.

Measured: a regex `tool\.py (\w+)` did not accept a hyphen, so a `control-total` command was
both missing from the named set and contributed `control` to the unexpected set. Add a
fixture asserting the pattern matches a legal spelling that stresses it (here: one with a
separator), not merely that the document passes.
