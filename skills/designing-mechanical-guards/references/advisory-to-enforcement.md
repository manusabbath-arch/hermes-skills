# Turning an advisory into an enforcement

For the common case where the repo **already has the detector** and only the consequence is
missing. It shows up when a rule breaks anyway: someone wrote the check, with its tests, and
the call site prints it and moves on (`|| true`, a `print` with no `exit`). The commit lands,
the rule breaks, and the register says a guard was there.

## Look for the half-built guard before writing a new one

- The detector is usually there, because warning is cheap and gets written first. Search by
the rule's **subject** and by the verb of the warning, not by the name you would invent:

  ```bash
  grep -rn "warn\|advisory\|does not block\|not enforced" scripts/ | head -20
  ls tests/ | grep -i guard
  ```

- A function that returns the warning text (or `None`) is already two things paid for: the
detection and its tests. A parallel implementation leaves two sources of one rule that
diverge on the first change, and the new one usually loses the edge cases the old one had
already solved.

## The shape of the conversion

- **Find the call site and read the exit code.** `grep -n "<command>" *.sh .githooks/*` and
  read the whole line: the `|| true` sits at the end and is the only thing to change. A
  `|| true` in a hook is a guard switched off, not a soft guard.
- **Convert at the caller, not in the detector.** The detector changes only its exit
  contract (`return` → `sys.exit(1)`), so its existing tests keep passing. Changing how it
  returns the warning forces every detector test to be rewritten along with logic that
  already worked.
- **Keep the escape the detector already documents.** If its docstring names an env var for
  the session allowed to do the action, that is the one; inventing a second (`ALLOW_X`)
  leaves two doors and the next reader cannot tell which is official. The escape belongs in
  the error message, not only in the code.
- **Rewrite the text that said the opposite.** A docstring saying "this is a warning, not a
  block" and a message ending in "nothing is blocked" is the licence for the next agent to
  put the `|| true` back. Replace it with the behaviour and the reason, dated.
- **Prove the legitimate path does not go through the guard.** If the rule says integration
  happens with `merge --ff-only`, verify it: a fast-forward creates no commit, does not run
  `pre-commit`, and the guard never sees it. That check is what separates a useful guard
  from one that breaks the flow its own rule mandates.

## Tests that prove the consequence, not the detection

Detection is already tested. What is not — and what breaks — is the wiring:

- **The hook does not swallow the verdict.** Read the hook file and assert the good line is
  present and the bad one is not (`|| true` absent, `|| exit 1` present). It is a test over
  text, and that is correct: rewriting that line is exactly the failure mode.
- **The command now fails when it should.** Monkeypatch the detector to return the warning,
  build `sys.argv` by hand, assert `SystemExit` with `code == 1`; plus the negative case
  (detector returns `None` → no `SystemExit`). Without the negative, an unconditional
  `sys.exit(1)` passes the first test and breaks every commit.
- **One cheap end-to-end case in a scratch repo** when the condition depends on git state
  and cannot be simulated with monkeypatch: `git init -q -b main`, one file, one commit,
  then run the script on the good branch, on `main`, and with the escape. Three expected
  outputs; paste them in the commit message or the validation note.

## When the hook is a versioned text file

- **LF endings, always.** Rewriting the hook with Python's `Path.write_text` on Windows
  converts it to CRLF and kills the shebang. A repo with a real gate has a test for it
  (`\r\n` in the hook's bytes) and the commit dies with a message that talks about something
  else. Write with `newline="\n"`, or edit by patch, which preserves the file's endings.
- **Step numbering is contract.** A hook that says `1/4` needs all four labels and the header
  comment renumbered when a step is added; leaving `0/5` next to `1/4` means the next reader
  cannot tell how many steps ran.
- **The message says what to do, not only what is forbidden.** Whoever reads it is mid-commit:
  the branch, the escape command, one line of why.

## The side effect to announce

Turning a warning into a block stops **every** writer in that tree, including the ones who
were working there out of habit and never read the rule. Announce it in the commit message,
in the docstring and in the closing report; and if the repo keeps a per-consumer list of
guards, add it there so the denominator cannot drop unnoticed.
