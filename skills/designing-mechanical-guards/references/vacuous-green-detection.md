# Auditing a check set for vacuous green
## Contents

- See headings below. Load this file when SKILL.md points here.


For the question "do these checks actually check anything?" — reviewing an existing gate,
inherited suite, or check registry before trusting its green.

A check has one job: fail when the thing it guards is wrong. Everything below finds checks
that cannot do that, while reporting success.

## The three probes, cheapest first

### 1. Enumerate the success paths and ask what each inspected

```bash
grep -n 'ok=True\|return True\|return 0\|exit(0)\|sys.exit(0)' <check-module>
```

For each hit, read the branch it is on and answer: *what did this line look at?* The
suspects are the early returns — "file not found", "nothing to compare", "empty list".

Then read the success *messages*. A green message containing `0 `, "no hay", "nothing",
"empty" or "none" is the signature:

```bash
grep -n 'ok=True' -A 3 <check-module> | grep -iE 'no hay|ningun|no existe|0 |vac'
```

### 2. Point it at an empty subject and confirm it goes red

The decisive probe, and the one to reach for whenever a check can be given a path. Build an
empty directory (or one containing only the entry file) and call the check on it directly:

```bash
uv run --quiet --with-requirements requirements.txt python -c "
from pathlib import Path
import tempfile
from <module> import <check_fn>
d = Path(tempfile.mkdtemp())
print('subject absent ->', <check_fn>(d))
"
```

Three outcomes, and each means something different:

| Result | Reading |
|---|---|
| green with a "nothing to check" message | **vacuous pass** — the defect. There is no subject, so no check happened |
| green reporting "0 X, 0 Y" | **vacuous pass** — it walked a tree with nothing in it and called the empty set clean |
| red | correct — a missing subject is a failure |

A check written with an injectable root makes this probe a one-liner. If the check only
takes global state, that is itself the finding: it cannot be probed, so nobody ever has.

### 3. Count the denominator

Ask of every audit: how many things did it look at, and is that in the output? A check
that reports only findings cannot distinguish "clean" from "blind". The fix is to put the
count in the message — files scanned, links resolved, rows compared — so the green path
proves coverage.

The inverse failure is a check that finds a real defect but reports it as a count without
a location: `3 problems found` and nothing else. Add file:line to each finding; an
unlocatable finding costs a search every time.

## The error-into-pass path

A distinct defect from the empty subject: the check *tries* to run, fails to, and returns
success with the failure text as its message.

```bash
grep -n 'except .*:' -A 4 <check-module> | grep -B 2 -A 2 'ok=True\|return True'
```

and specifically look for an error value read out of a result dict then returned as green:

```python
if result.get("error"):
    return CheckResult(ok=True, message=result["error"])   # <- reports clean, measured nothing
```

This is worse than the empty-subject case because it looks like diligence: the message
contains a real error string, so a reader concludes the check noticed and handled it.

**Rule for the fix:** the outcomes are pass / fail / could-not-run. The third is *not*
pass. Return it non-green with a message that says the audit did not run and why.

## Why a green is not evidence, even when non-vacuous

Two more shapes worth checking while you are in the module:

- **Existence-only subject.** The check asserts a file or artifact is present. It stays
green through every content regression. Verify by looking only at *what* is asserted — if
the assertion is `exists()` / `is_file()` / a path string, the content is unguarded.
- **The denominator nobody recorded.** A check that ran over 3 items yesterday and 3000
today reported the same green both times. If the check's threshold was tuned against the
small population, the green now means something different. Prefer a threshold relative to
the check's own history (a baseline, a ratio against the previous run) over an absolute
count fixed once.

## Reporting the findings

Fix the vacuous paths in the same pass as finding them — a check reported broken and left
broken gets deleted by the next person. For each one, the useful write-up is:

- the check name and the exact line of the vacuous return;
- the command that reproduces it (probe 2 above);
- the observed output versus the correct one;
- what it should assert instead.

A check that has been proven to go red on a synthetic defect is the only kind worth
keeping in the gate.
