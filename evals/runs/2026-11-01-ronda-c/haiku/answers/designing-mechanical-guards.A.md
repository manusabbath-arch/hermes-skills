## Pedido 1

I can't run anything or see the repo here, so this is the plan, not a verified change. A rule written as prose will break again. It only stops breaking when a command exits non-zero.

1. **Write the failing test first.** Build a tiny fake report with no source hash, and assert the guard rejects it. Run it and confirm it fails because the guard is missing, not because of a typo.
2. **Make the guard testable with injected inputs.** It takes a reports directory and the expected hash source as parameters, so the test doesn't touch the real repo.
3. **Check the declared field against the real source.** A report without the field is a failure. A report whose hash doesn't match the source is a failure too. Don't accept an empty or missing field as a pass.
4. **Make it report what it inspected.** For example: `12 reports inspected, 0 missing source hash`. An empty reports directory must go red, not green.
5. **Register it in the existing gate** and confirm the pre-commit hook actually runs it. A check nobody invokes does nothing.
6. **Prove it on the real tree, then flip the defect.** Remove one hash by hand, confirm the gate exits non-zero and names the file, then restore it.
7. **Commit the guard, its test, and its registration together.** If the new check needs a baseline entry, add it in the same commit so the commit doesn't block itself.

Tell me where the reports are generated and I can make this concrete.

## Pedido 2

Don't ship it yet. A green on the live repo only shows the check passes today. It doesn't show the check can catch anything. Before it ships, I need to see:

- The test failed first, for the right reason.
- An empty or subject-less tree turns the check red.
- The output shows a non-zero count of what it inspected on the real repo.
- The gate's exit code goes non-zero when the check fails, not just the summary line.
- The check is registered and the hook runs it.
- If it's a new check, its baseline entry is in the same commit.

I can't run any of these from here, so I haven't verified any of them. Run them, paste the output, and I'll tell you whether it's ready.

## Pedido 3

Don't fix the three old reds in this commit, and don't bypass the hook with `--no-verify`. First prove they aren't yours:

1. Run each of the three failing checks by itself, on the untouched files, and confirm they fail the same way.
2. Confirm none of the failing files is in your diff.
3. Compare the gate's FAIL list with the baseline. If the three are already recorded as known reds, your change adds no new red.

If they're foreign, use the escape the hook documents for that step, such as an environment variable scoped to that step, and never a global bypass. Put this in the commit message: which checks failed, what they're about, and the command you ran showing they were already red before your change. That leaves a trail. If the one-line fix touches any of those three checks, it isn't a clean "not mine" case, and you should say so in the message.

## Pedido 4

I wouldn't add `|| true`. It runs the check, throws away the result, and nothing will ever block on it. A rule that breaks will break again with no sign in the gate, and the next person will assume it's enforced.

Better options, in order:

1. **Fix the noise.** If it's noisy, the matcher is probably too broad or it's counting things it shouldn't. Tighten it and keep it blocking.
2. **If it's really non-blocking, use the gate's own non-critical severity or a declared known red**, with a written reason and date. The line should still print in the output so people see it.
3. **Announce the change** in the commit message, since a check that is now advisory changes what every committer sees.

If you tell me what the check looks at and what the false positives are, I can suggest the tighter matcher.

## Pedido 5

Use your editor's rename, which updates every reference in the project:

- **VS Code:** place the cursor on the name and press `F2`.
- **PyCharm:** `Shift+F6`.

If you need to do it by hand, search the whole project, not only the call sites. Check:

- imports and `from x import old_name`
- strings that refer to the name, such as `getattr` calls and mock patch targets like `"module.old_name"`
- `__all__` lists
- tests and docs

If other code outside the project imports the old name, keep a temporary alias:

```python
def new_name(x):
    ...

old_name = new_name  # temporary alias, remove after callers update
```
