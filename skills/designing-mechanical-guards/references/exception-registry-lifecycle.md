# Accepted-exception registries

When a gate must tolerate known-bad states, the tolerance lives in a versioned registry: one
entry per check, with the reason someone wrote, the seal date, a review date, and the condition
that would end the exception. The registry is the difference between "this was always red" and
"this broke now", so its own lifecycle has to be complete.

## Three operations, not two

Declare and refresh are the obvious ones. **Retire** is the one that gets forgotten: the check is
fixed, the entry stays, and the gate ends up printing "declared but no longer red" on every run
with no way to act on it. A registry that can only grow stops describing reality within weeks.

## Every instruction the gate prints must be executable

If a check tells the reader to do something — clean the registry, seal the baseline, re-declare
with a reason — the command that does it has to exist, and the message has to name it. The
anti-pattern: the gate says "clean the registry" and the only way is editing the registry file by
hand. That is a trap dressed as an instruction: it pushes the human out of the tool, and the next
person to write a script or re-seal the baseline drops entries the tool would have preserved.

Test the message, not only the behaviour: one assertion that the hint names the command keeps a
later refactor from quietly deleting the affordance.

## Retiring an entry

- Remove **only** that entry. Seal date, known-state map and registry notes stay byte-identical —
  merge, never rewrite the whole document.
- A name that was not declared must not rewrite the file at all: an unchanged rewrite shows up as
  diff noise and gets swept into an unrelated commit.
- After retiring, a future failure of the same check blocks like a brand-new one. The exception is
  gone, not dormant, and the message after the operation should say so.
- Retire from the command, never by editing the file: the command is the documented path and it is
  what a reviewer can repeat.

## The exit condition has to be reachable

Before accepting an entry, name the action its exit condition demands and ask: **does that action
change the number the check computes?** If it does not, the entry can never be retired, and "it needs
an owner" becomes a permanent assignment — a debt with no due date, which is the shape that teaches
readers to ignore reds.

The recurring trap is a condition phrased as a decision — *closed when someone decides which X is
official* — over a check that compares two values **that both survive the decision**. Deciding makes
one of them official; it does not make the other one stop existing, so the comparison keeps failing
and the person who answered correctly is credited with nothing. Two symptoms worth acting on: the
entry is red for weeks with several different people named as its owner, or the number the check
prints does not move no matter what anyone does to it.

**Repair in the check, not in the registry.** Make the check read the decision record instead of
comparing the two values: red when the record is absent, still open, or declares a different option;
green when it is closed and names the option the check verifies. The method then changes by editing
the record, and the guard carries no constant that goes stale. Two details make it honest:

- **"Closed" alone is not evidence.** Assert the record's own text names the chosen option (a
  distinctive substring of the option's name), or a note closed for an unrelated reason passes as if
  it had answered the question.
- **Keep the compared values in the message.** They are the information the reader needs; only the
  verdict changes hands from "the values differ" to "nobody has decided which one governs".

A test that hardcodes the names of declared checks is part of this registry: retiring an entry reds
it. Update the list **and** strengthen it in the other direction — the retired name must *not* be
declared again — otherwise the next session re-adds the exception to silence a red that has already
been resolved, which is the failure the retire step exists to prevent.

## Refresh is not re-seal

- **Refresh** one entry: keep its exit condition, move its review date, keep or update the reason.
- **Re-seal the whole baseline** is a different and riskier operation: it makes today's state the
  reference and can absorb undeclared failures. Print what it would absorb *before* writing, and
  never re-seal to make a red go away — re-sealing is for when the instrument that produced the
  reference changed, or when an accepted state legitimately stops being a failure.

## Verification shape

1. Retire one of two entries: the other survives.
2. The rest of the document is untouched (seal, known state, notes).
3. Retiring an absent name leaves the bytes identical.
4. The CLI path produces no "declared but no longer red" line on the next run.
5. The hint text names the retire command.
