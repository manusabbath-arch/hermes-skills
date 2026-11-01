# Remediation that is also a command

A guard has two jobs: say what is wrong, and say what to do about it. The second one is the one
they get wrong, and the failure is silent because the message looks helpful.

## The rule

**Every remediation line a red prints must be executable as printed, with the tool's own
arguments.** Before writing `clean the registry`, `re-declare it`, `update the baseline`, `remove
the entry`, check that the command exists and that the tool accepts that spelling. If it does not,
the operator is left with one path: hand-editing a versioned file — the exact manual step the guard
existed to prevent, with no test, no audit trail and no validation of the edit.

The tell is a message with an imperative verb and no tool name. `limpiar el registro` is not an
instruction; `the project's gate command ``<check-name> --clear-red``` is.

## How it happens

The guard is written when the *detection* is fresh and the *fix* is still a person's job. Later the
fix gets automated, or the automation never gets written because the red is rare, and the message
keeps the imperative from the first version. Nobody re-reads the remediation text — it is a string,
not a code path, so no test fails when it drifts.

## What to do

1. **Prefer adding the command.** The check that reports work is not done until the way to finish it
   is also a command. It is usually small: read the registry, remove or update one key, write it
   back merging the rest.
2. **Test the two shapes that make a registry edit safe.**
   - Removing/updating one entry leaves the rest of the file byte-identical (seal, counts, other
     entries) — the merge-not-rewrite property.
   - A no-op target (a name that was not there) leaves the file untouched, bytes equal. A
     rewrite-that-changes-nothing dirties the diff and lands in someone else's commit.
3. **Name the command in the message, with its arguments.** If the message is longer than the
   command, the command is probably missing.
4. **Only then** hand the red to a person, and say why no command exists — a red that is genuinely
   a business judgement is legitimate; a red that is manual by omission is a bug in the gate.

## Related lifecycle

A registry of accepted exceptions has three operations, and a gate that offers only two of them
pushes the third into a text editor: **declare** (with motive, date and exit condition),
**re-declare** (when the motive went stale), and **remove** (when the check went green and the entry
is now a lie). Grep the tool for all three before trusting a message that mentions one.

