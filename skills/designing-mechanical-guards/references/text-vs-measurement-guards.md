# Guards that compare hand-written prose against a measured value

The class: a check that crosses text a person wrote — a panel/index entry, a document's summary
line, a skill or agent file — against a number the code itself computes. It is the cheapest guard
that covers documentation drift (seconds, against a commit gate that takes minutes), and it has a
signature failure of its own.

## The guard reads the text that describes it

A pattern looking for `<number> <noun>` cannot tell a claim about the data from a sentence about
the guard. So:

- **Keep the measured number out of the prose that talks about it.** Name the figure, do not
  quote its value, and when an example is needed, write the value in a form the pattern does not
  reach (`NN`, `cuatro cifras`) rather than the literal number. Measured: the file documenting
  this trap tripped it on its first run, and the whole gate was paid to learn that.
- **The noun is the pattern, not the number.** A guard watching `pares`/`chequeos`/`claves`/
  `validaciones` turns every sentence using that word into a claim about the repo's own count.
  When the guard's vocabulary collides with the domain's — the pairs a *database* has, against the
  (file, key) pairs the repo *declares* — the red belongs to the wording, not to the data.
- **The number may be correct and still be a lie: `0` is not empty.** A guard (and a reader) that
  treats a zero-filled field as a missing one publishes the opposite conclusion. "Nobody fills
  this" and "it is filled with the literal `0`" are different findings with different fixes.

## Design the message for the person who will fix it

- **Name the file, the line, the value written and the value measured.** Without the measured
  value the reader cannot separate "stale" from "mis-worded"; with it, the repair is a one-line
decision. The message is what an agent reads first, and it is the difference between a guard that
gets fixed and a guard that gets declared away.
- **Check both directions of the same pair.** Entry against document *and* document against entry
  (the entry repeats the figures of the summary, the summary repeats those of the entry): a
  one-directional check lets through the copy that was updated while the other was not.
- **Declaring the red is for the red that cannot be fixed**, with its reason, kept visible — never
  the shortcut for the one that can. A guard whose reds are routinely declared stops being a guard,
  and the declaration file becomes the place where the drift hides.

## Scope it wider than the code

- **Run the prose guard over everything that gets published, including the skills and the agent
  files that state the rules.** Those are the last place an old figure survives: no code check
  reads them, no test compiles them, and every session loads them.
- **Run it before queueing the long gate**, not after: it takes seconds and it is precisely the
  check the long gate runs last.
