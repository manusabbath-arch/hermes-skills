# Detectors whose subject is the repo they live in

For guards that scan the source tree they are part of — "no script opens a source file by
hand", "every printable sheet is declared", "every note is linked from the index",
"no file mixes line endings". The subject includes the checker, so the ordinary failure
shapes are not the ones to watch. These are.

## The detector counts itself

- **Match code structure, not a substring.** A text scan for a marker finds the marker in
the checker's own message, docstring, or test, and reports an extra subject whose only
defect is quoting the rule. Parse the file (AST) and look for the shape a real subject has
—a call, an import, a module-level assignment— and skip docstrings.
- **When a substring is unavoidable, pair it with a second marker that only a subject can
have** (a document literal carries both the doctype and the `<html>`; a quotation carries
one). Then write the blind spot into the docstring: what shape it would miss.
- **The regression test is "a mention that is not a subject"**: a file whose message or
comment quotes the marker and must stay out of the count. Write that test with the
detector, not after the first false red — it is the test that fails first when the
criterion is loosened later.

## A mention is not a use; an import to scan is not an import to use

- **When the criterion is "this module uses X", match the symbol, not the module.** The
scanner imports the module to introspect it; a module-level criterion then lists the
scanner among the subjects that "use" it. Subject = the import of the function, or the
call to it.
- Same for "reads through the shared reader": the subject is the call site. A reference in
a comment or a docstring is not a violation and must not be reported as one.

## The perimeter is what git tracks

- **A gate that enumerates files with `git ls-files` cannot see a file you just wrote.**
Link/completeness/index checks, line-ending checks and "every doc is indexed" scans all
read the tracked list: a new note reads as *link without file* and as *document the index
does not link*. Stage the new files by path, then run the gate. A red that names a file
you just created, which `ls` shows on disk, is the staging — not the content.
- **Name-based resolvers collapse two documents with the same basename in different
folders**, and the index link then resolves to nothing. Give a new note, plan or record a
unique stem even when it lives in another directory.
- **Count what the scan found, never the size of the declared registry.** A denominator
that is `len(registry)` grows with the registry and hides a tree that shrank; a
`len(registry)` numerator hides subjects that were never declared. Report both, and take
the denominator from the walk.

## When the subject changes shape

- **An extractor that reads one representation of the source stops seeing the subject when
  that representation changes — silently.** The classic case: a guard parses `CSS = "…"` to
  measure a sheet's styles, the consolidation turns it into `CSS = BASE + "…"` (or an
  f-string), `getattr(nodo.value, "value")` returns `None`, and the sheet drops out of the
  count. The metric *improves* precisely while the repo got harder to read, and nothing goes
  red: absence and unreadable render the same. Teach the extractor the new shape
  (evaluate the composition, not only constants) and cover three cases in the test — literal,
  composed, and an expression it cannot evaluate.
- **An unreadable subject is red, not absent.** Keep the subjects the scan could not parse in
  their own list and fail when it is not empty, next to the "zero subjects is not green" rule:
  otherwise every broken parser reads as a smaller tree, and a smaller tree always looks like
  progress.

## Put the number in the message, not in the notes

- **Measure in code and let the check print the measurement**, so the write-up cites the
command's output instead of a hand-typed figure. The measuring function is reusable: the
note, the message and the plan then quote one source.
- **A test that asserts the measured tuple** — characters, shared selectors, derived
counts — makes the number age loudly: whoever changes the subject must update the
statement instead of letting it rot silently.
- **Never let an index or entry document restate a count the code produces** ("N checks",
"N sources", "N fields"). The guard that compares those numbers goes red the moment the
registry grows, and the correct fix is to phrase by reference ("the checks of that run"),
not to bump the digit — bumping it falsifies the historical statement.
- **A check you add changes numbers other guards measure.** Before declaring the gate
clean, run the guards that compare index text against live counts; an added item is
exactly what drifts them.
