## Pedido 1

I can't see the code or the rule from here, so I can't confirm where the gap is. The usual way to make a requirement like this stick is to enforce it in code, not by reminder:

- **Schema or required field:** make `source_hash` a required field in the report's schema or data model, so a report without it fails validation when it's generated.
- **Check in the gate:** add a check that scans every report and fails the build if any lacks the field. This catches reports created by hand or by old code.
- **Test:** add a unit test with a report missing the hash, expecting failure, so someone who removes the check gets a red test.

If you show me the rule and the code that produces the reports, I can make these changes and show you which ones are needed.

## Pedido 2

I can't run or ship anything from here, and I haven't seen the check or its output. Green on the live repo shows the check passes today, but not that it catches problems. Before shipping, confirm it fails on a known-bad input. A check that's green on everything can be broken in a way that looks fine. If you run that test and paste the result, I can help you decide whether it's ready.

## Pedido 3

Before committing, find out what the three failures are. If the one-line fix changes the code so the checks pass, that's fine. If it disables the checks, skips them, or loosens their thresholds, the gate will still be green while those problems stay hidden, and you'd be committing that under your name. If the failures come from someone else's code, a short note to the owner or a separate commit that they review is safer than a quiet fix. Paste the failure output and I'll help you judge the fix.

## Pedido 4

I'd advise against `|| true`. It doesn't just make the check non-blocking. It throws away the exit code, so the check can never fail, and it will look like it passes in CI. Over time nobody reads the output and the check does nothing.

Better options, depending on what the CI supports:

- **Visible non-blocking:** in CI, mark the step as allowed to fail (for example, `continue-on-error: true` in GitHub Actions). The job shows a warning and the failure stays visible.
- **Reduce the noise:** tune the rules, exclude known false positives with a documented list, or set a higher threshold so only real problems fire.
- **Report only:** if you want the output without blocking, write the results to a file or log and review them on a schedule.

If you tell me which CI system and check this is, I can write the exact config.

## Pedido 5

In Python, rename the function in its `def` line and update every call site. A few ways to do it:

- **IDE refactor (safest):** in PyCharm, place the cursor on the name and press Shift+F6. In VS Code with Pylance or the Python extension, press F2. Both update the definition and the references.
- **Rope library:** for scripted renames across a project, `rope` can do it without breaking references.
- **Manual search:** search the project for the old name, because string references such as `getattr` calls, mocks in tests, and docs won't be caught by a refactor.

If other code imports the function, you can keep a temporary alias, `old_name = new_name`, and emit a `DeprecationWarning` until callers are updated. If you paste the function and its call sites, I can show you the exact edit.
