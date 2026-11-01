# Registry guards, data guards, and guard canaries

Three guard shapes that come up once a codebase has a registry, a public surface, or personal
/ secret data. Each is a relation the machine can check, not a list a human keeps up to date.

## 1. Guard the registry, not each member

When the code has a registry — a CLI's module list, a plugin map, an exception hierarchy, a
manifest of data sources — assert the **relation**, and discover the members by introspection.
A hand-written list of members is the thing that goes stale.

- Discover: `pkgutil.iter_modules(pkg.__path__)` + `inspect.getmembers`, filtered by a naming
  convention (`*Invalido`, `*Error`) and by `member.__module__ == module.__name__` so imported
  classes from elsewhere do not count.
- Assert the partition: `set(adapters) | set(pending) == set(registry)` and
  `not set(adapters) & set(pending)`. A new entry with no home fails; so does one in both.
- Assert the base type: every discovered exception inherits the common base, so a consumer needs
  one `except`. Subclass the type the package already raised (`ValueError`) and existing callers
  keep working.
- Assert a **floor** (`len(members) >= 19`) so a broken discovery cannot return nothing and stay
  green forever.

Why introspection rather than a list: the failure mode is "someone added a module and forgot the
list", which a list-based test reproduces exactly. The convention-based scan catches the addition
on the day it lands, in the same commit that caused it.

## 2. Measure a data guard against the tree before shipping it

A guard over values (secrets, personal identifiers, machine paths) has two failure directions:
false negatives that make it theatre, and false positives that make people disable it.

- Run the scanner over every **tracked** file first and classify every hit as synthetic or real,
  before the guard exists. The classification is the work; the regex is the easy part.
- `git ls-files` is the universe, not the disk. An untracked file is not audited, and a guard run
  before `git add` reports green on the file you just wrote. Run it after staging.
- Budget the false positives explicitly. A 12-digit numeric token has roughly a 1-in-11 chance of
  passing a check-digit test, so in a repo full of docs and lockfiles an allowlist is inevitable;
  every allowlisted value gets a comment naming where the fake came from.
- If the scan finds a real value, **that is the finding**: replace it (with a synthetic value that
  still passes the check, so the test data keeps testing the parser), then ship the guard. Shipping
  the guard first makes it fail on code that predates it, and invites weakening it.
- Restrict the scanned corpus to what can carry the data (`docs/`, `tests/`, `README.md`) and skip
  lockfiles; a lockfile's hashes are not a place anybody typed an identifier.

## 3. The guard must not publish what it protects

- The failure message names file, line and class of finding — **never the matched value**. CI logs
  of a public repo are published text; echoing the secret to prove it exists is the same leak the
  guard prevents.
- For the same reason, an allowlist of private names lives in a gitignored local file
  (`pattern<TAB>what it is`), not in the versioned test: listing the names in the guard publishes
  them.
- Add a guard over the guard: a test that fails if that local file is ever committed.

## 4. Every guard needs a canary

- One test plants a known hit in a literal string and asserts the scanner returns it. Otherwise
  "0 findings" is indistinguishable from "scanner looks at nothing" — wrong glob, wrong encoding,
  empty file list, `errors="ignore"` swallowing everything.
- Extract the scanner as a pure function (`def _rut_validos(texto) -> list[str]`) so the canary is
  two lines with no filesystem and no fixtures.
- Same rule for value-level guards: assert one row that must be rejected *and* one that must pass.
  A guard tested only on rejections is satisfied by `raise` at the top of the function.
