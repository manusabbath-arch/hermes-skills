## Pedido 1

A written rule can't fail, so this needs a check that exits non-zero. Here is the order I'd work in:

1. **Write the failing test first.** Build a tiny fake tree with one report that has no source-hash declaration. Pass the root path in as a parameter, so the test never touches the real repo. Run it and confirm it fails because the check doesn't exist yet.
2. **Write the check.** It should walk the reports and fail on any report without the declaration.
3. **Make the output show what it inspected.** For example: `N reports inspected, M without a hash`, with the file and line of each one.
4. **Make an empty tree red.** If the check finds zero reports, that means it looked at nothing, not that everything is fine.
5. **Check what it walks against what exists.** List the report folders and formats that actually exist, and compare them with the check's glob. A report in a format or folder the check doesn't visit would slip through.
6. **Register it in the gate you already run.** Run the gate and confirm your check appears in the output and that a failure changes the exit code. A script nobody calls isn't a guard.
7. **Add its baseline entry in the same commit.** Otherwise the commit that adds the check can fail its own gate.
8. **Write the rule in the rule file last,** pointing at the check.

If you tell me where your gate is registered and what a "declared hash" looks like, I can write the check and its test.

## Pedido 2

Green on the live repo isn't enough. It only shows the check passes today, not that it can fail. Before shipping:

- **Prove it can fail.** Run it on a synthetic fixture with the defect, and on an empty tree. Both should be red. If you've only seen it green, it's unverified.
- **Check the denominator.** The green output should say what it inspected (`N inspected, 0 found`), and N should be above zero.
- **Confirm it's wired in.** Run the project's gate and check that it lists your check and that a failure gives a non-zero exit code.
- **Add its baseline entry in the same commit.** A check the baseline doesn't know about is compared against "pass". A red on it can then block you, or a regression can show up as `(not present) -> FAIL`.
- **Commit the check, its test and the registration as one unit.**

I can't commit or run anything from here. If you paste the test and the gate output, I'll tell you which of these is missing.

## Pedido 3

You need to show there's no new red, not that everything is green. A red you didn't cause still blocks you, but you handle it in this order:

1. **Prove the reds are foreign.** Run each of the three failing checks alone, with your change not applied, and confirm the same failure. Confirm the failing files aren't in your diff.
2. **Compare the set of failing check names with the baseline's failing set.** If they match, you've introduced no regression. Don't edit the code behind those three checks. You weren't there to change it.
3. **If the hook still blocks you, use the escape the hook documents for that one step.** That usually means an environment variable. Don't use `--no-verify` or any other global bypass.
4. **Record it in the commit message.** Name the three checks, say they were red before your change, and give the command that showed it. Then the skip leaves a trail instead of looking like a clean run.
5. **Re-run the gate at the moment you commit.** The state of a shared tree can change while you work.

Also check that the gate was run the project's own way, with its wrapper or environment. A wrong interpreter produces import errors that look like a wall of fresh reds.

## Pedido 4

I'd advise against `|| true`. It switches the check off and doesn't make it soft. The command still runs, but the exit code is discarded, so nobody sees the output and the check is dead in practice. A check that is always ignored also teaches people to ignore the next one.

These are better options:

- **Find out why it's noisy.** Run it over the current tree and read the findings. Usually the matcher is too broad, and tightening it fixes the noise.
- **Mark the check non-critical in the gate's registry.** It still runs and shows in the output but doesn't block, and you write the reason next to it.
- **Declare the known reds, each with a reason.** New reds then stand out from the old ones.
- **Scope any exemption to the exact token or line.** A broad exemption creates a blind spot where the problem was.

If you do end up with `|| true`, put the reason and an expiry date in a comment next to it. Tell me what the check flags and I'll help choose between these.

## Pedido 5

Renaming a function in Python takes three steps:

1. **Rename it.** Change the name in `def old_name(...)` to the new one.
2. **Update every use.** That means call sites, `import` and `from x import old_name` lines, and any references in other modules, tests and docs.
3. **Search for leftovers.** Run `grep -rn "old_name" .` to find the ones you missed, including strings, `getattr(...)` calls and config files that refer to it by name.

For safety, use your editor's rename refactor instead of search and replace:

- **VS Code:** put the cursor on the name and press `F2`.
- **PyCharm:** press `Shift+F6`.

If other code depends on the old name (a public API), keep a temporary alias: `old_name = new_name`.
