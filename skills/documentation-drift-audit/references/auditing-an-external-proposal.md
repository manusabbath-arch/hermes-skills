# Auditing an outside proposal against the system it proposes to change

## Contents

1. Procedure
2. Variant: the outside document is live
3. Pitfalls

For the task "someone outside sent us a plan / proposal / recommendation — what do we do
with it?". The document may be a strategy memo, an architecture proposal from a vendor, a
consultant's roadmap, or a long answer an LLM wrote about *this* project. It is well
written, plausible, and its author **could not see the system**, so parts of it describe
as future work things that are already done, and parts prescribe things the system cannot
accept.

The work is the same shape as auditing docs for drift — verify each claim against the
thing it describes — with one difference that changes the deliverable: **the outside doc is usually not a
candidate for correction.** Nobody rereads it, so the output is a document *of this
project's own*, in this project's own terms, that separates what already exists from what
is genuinely new. The exception is a document that is still live — the plan that will be
sent, negotiated from or quoted in a meeting: there the numbers get fixed **in the file**,
and the audit is logged in the project (see the Variant section below).

## Procedure

1. **Measure the system before writing a word about it.** The proposal rests on
   assumptions — that a pipeline must be built, that the hard part is a purchase, that a
   practice is not yet in place. Assume nothing and price each one with a command. Cover
   at minimum: what the system already produces and how it is verified, what is currently
   broken (gates, backups, credentials, retention), what the cost of the status quo is,
   and the current constraints (disk, throughput, the human steps in the loop).
2. **Build the front-by-front table.** For each point of the proposal: **what already
   exists**, **its real measured state**, **what is actually missing**. Three buckets
   matter and they need different treatment: already covered (the author could not have
   known), read wrong (a claim the system contradicts), and genuinely new (the one bucket
   that becomes work).
3. **Say plainly that the proposal is outdated rather than wrong, and lead with the part
   it got right.** Proposals of this kind usually order their phases by generic maturity
   models, which is why they place already-solved problems in the future and in-flight
   work in a late phase. Naming that — with the measurement — is more useful than a
   point-by-point rebuttal, and the part it does get right (almost always continuity and
   recovery) should be said first.
4. **Write the sections the author could not have written.** This is the actual
   contribution. The shapes that recur: the thing that is broken today and is nobody's
   assigned task; the item that is not engineering but **one phone call to a vendor or one
   process decision**; the capability that already exists in the operation and is being
   scheduled as future build; and the single point of failure that is a procedure or a
   person rather than a machine.
5. **Re-express the plan in this project's own decision format.** Every item carries
   **what / why (with the measurement) / who / the gate** — the condition that must hold
   before the next stage starts. Stages are **dependencies, not calendar dates**: a date
   nobody agreed to is a fabricated fact. An item whose owner is unknown says so; do not
   manufacture one to fill the column.
6. **Close with what NOT to do**, each item with its measurement. This section is what
   stops the standard failure of buying tooling that duplicates a capability already
   present, and it is usually the section the reader acts on first.
7. **File it as a document of the project and link it from the index**, then run the
   project's own doc gate before committing. State in the document's own header that the
   outside material is **analysis, not this project's evidence** — the measurements are,
   and each one is cited to a command or an internal document.

## Variant: the outside document is live — fix it, and log the audit

Two tasks wear the same request. **Assess a proposal** (the case above: the deliverable is a
project document and the outside file is left alone), or **fix a document the user still
uses**. The tell is the request itself ("work on this file") and whether the file is dated
*now* with figures about to be defended. Choosing the first when it is the second hands back
a critique nobody asked for while the wrong number stays in the file that goes out.

1. **Close the internal arithmetic before measuring anything.** Stages, parts and subtotals
   must sum to the total the document declares, and each conversion must match the rate it
   states (currency, per-period extrapolation factor). It is one script, and it either closes
   exactly or produces a finding nothing else can top. **"Everything closes" is the result** —
   report it as such instead of hunting for something else to fix.
2. **Every count needs a definition that reproduces it.** A count that does not match the
   obvious denominator gets *tested*, not nudged: try the plausible alternative definitions
   (date cutoffs, subsets, exclusions), and if none reproduces it, replace it with the measured
   value **and say that no definition reproduced the original**. Adjusting it by eye to the
   nearest plausible figure destroys the only information the audit had.
3. **Never lend the document a verification you did not run.** "N tests passing" can only be
   corrected with the *collected* count when you did not run them: write the measured
   population, delete the adjective, and list the unverified claim under a heading for what the
   audit does **not** measure. A number upgraded to a stronger-sounding one is worse than the
   stale number it replaced.
4. **Correct in the file, and put the audit in the project's own record.** The outside file is
   unversioned, so an in-place fix leaves no trail: land a validation note plus an index entry
   that cites it, and state in the note where the corrected file lives and that moving it into
   the repository is a separate decision the audit did not settle.
5. **Price the part of the document that prices nothing.** Proposals cost their strengths; the
   weaknesses they name themselves (slow decisions, no dashboard, dependence on one machine)
   often carry no budget line and are actionable without purchase. Say so as an observation
   about the document, not as a new figure.

## Pitfalls

- **Do not answer only in chat.** An assessment that lives in the conversation is lost;
  its value is being versioned, indexed and carrying owners and gates inside it.
- **Do not improve the outside document's prose or restate its structure.** The reader
  already has it. Restating it is the failure mode that looks like work.
- **Do not take a single figure from the proposal or from memory.** Every number in the
  deliverable comes from a command run in that session, cited next to it.
- **Keep the outside material's status declared.** Mixing an external recommendation into
  a document that otherwise carries measured figures contaminates it — a reader cannot
  tell which claim was verified and which was received.
- **Do not invent a deadline to make the plan look finished.** If no date was agreed,
  the stage boundary is the gate, and that is a complete answer.
- **A user-owned instruction file you must correct may refuse your write.** Report the
  specific stale claims with their measured values and recommend the ownership step that
  makes the file editable, rather than retrying or silently dropping the finding.
- **The audit's own output is subject to the same guards as anybody else's.** An index entry
  that cites a figure must carry that figure in the audited document's **verdict block**, not
  only in a table further down: the index check compares against the verdict, so a figure the
  body states reads as "a figure the document discarded". Put the headline numbers where the
  verdict looks, and stage a brand-new note before reading any link check over it.
