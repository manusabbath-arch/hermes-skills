# Work-assignment blocks: what enters the list, and in what order

## Contents

1. The ladder
2. Choosing the grouping
3. The periodic dose
4. What each line carries
5. The canary that holds the block back

The depth behind the SKILL.md rules for a block that tells someone to go do something physical —
count these articles, sweep these shelves, call these customers. The unit of design is not "what
is interesting" but "what is worth a person's hour, and in what order is that hour spent well".

## The ladder: order by how cheap the item is to decide

Risk is `P(the record is wrong) × what being wrong costs`. Rank by the first factor, because it is
what decides whether an hour of counting changes anything.

1. **Records that cannot be true.** A negative physical quantity, a balance below zero, a date
   before the entity existed. Nothing to interpret: the record is wrong and the count settles it.
   These enter first, and they are the items that justify the block existing at all.
2. **Records whose missing companion is provable.** A balance that exactly equals the period's
   sales means the purchase was never loaded (or vice versa) — the arithmetic names the missing
   document. Counting closes the case in one pass.
3. **Nothing on hand while it is selling.** Zero stock with activity in the last N days: either
   the shelf holds goods the system does not know about, or sales are being lost. Both are fixed
   by counting.
4. **Cost of being wrong, for the residual.** High value × high rotation (an ABC cut): a 5% error
   on a fast mover costs more than the whole of a slow one. This is the class that fills the list
   to a fixed size once 1–3 are done.

Two consequences of the order. Classes 1 and 2 need no business judgement, so they cannot be
argued away — that is what makes the block credible to the person executing it. And a class that
is *large* is not thereby first: a class with 300 items and no way to tell which one is wrong is
worth less than 30 items whose wrongness is already established.

## Choosing the grouping

- **Measure the candidate fields before grouping.** For each one: how many entities carry it, how
  many distinct values, and how many are empty. A catalog table that is nearly empty beside a
  fully populated text field on the entity is the common case in an ERP whose module was never
  loaded — both readings are real, and which one the list groups by is a decision that has to be
  written down, not inferred.
- **The grouping is the unit of work, so prefer the one that matches the walk**: shelf, brand,
  supplier, route, aisle. Group by the classification when it is the same thing as the physical
  layout, and fall back to the next grouping for the groups that come out too small.
- **One group per print, with the total in sight.** "Today: brand X, 33 items · 278 remaining in
  46 groups" tells the reader the list is finite and that today's slice is finishable. Without the
  remainder, the same list reads as infinite and stops being picked up.
- **Never group a work list by an attribute the worker cannot map to a physical place.** A code, an
  internal id or a category only one system knows is not a place.

## The periodic dose: a few items per print, rotating

The alternative to a group-per-print when the reader wants something *daily* rather than one long
sweep day. The reader's own words are usually the spec: *"not all the products, maybe two or three
a day at most, so we can order the stock more dynamically"*. What that buys is a rate, and what it
costs is that the whole design moves into the selection.

- **Print the arithmetic that forces the choice.** Cap × issues per week versus the backlog size
  is the number that tells the reader whether the population is reachable at all ("3 a day are 15 a
  week: the 278 open items take 18-19 weeks"). At that rate the list's value is entirely in *which*
few, and the sweep length is what makes that argument for you.
- **Take one item per rung of the ladder, not the top N of one ranking.** A dose drawn from a
  single class is exhausted the moment that class is cleared, and it silently stops covering the
  other reasons — a negative-quantity item and a zero-with-sales item are fixed by the same walk
  and should not queue behind each other. Draw one from each rung in order and let a *short* rung
  pass its slot to the next; the dose is a fixed size, and only its composition varies.
- **Do not re-propose what is already open.** Keep the proposed items in the same ledger the other
  action types use (a stable key per entity, `estado: pendiente`), and select today's dose from the
  items that are *not* in it. A daily list that repeats yesterday's items is read as decoration and
  takes the new ones down with it.
- **Age the stragglers into a notice line, with the count of days.** An item open past a threshold
  (three issues is a reasonable start) leaves the list and appears as "still waiting, N days" — it
  stays visible, it stops consuming a slot, and it is the only signal that the executor is not
  clearing the dose.
- **Fixed order, never a shuffle.** Priority, then the ladder's rung, then a stable tie-break on
  the key: two runs over the same state must produce the same items. A rotation that cannot be
  reproduced cannot be tested, and the printed report has to be identical for the same day's data.
- **The dose closes its own loop.** Each item enters the ledger with entity key (not a name), the
  value to compare against, and the reason it is on the list; when the count comes back, it is
  closed with a result. That is what lets the weekly view read the ledger and report progress
  instead of re-deriving it.
- **Keep the map out of the dose.** The daily block is the action; the whole queue with its
  denominator, grouped by the physical walk, belongs on a weekly view. Printing both every day is
  how the daily block grows back into the list it replaced.
- **Size the mechanism so it can be tested without the source.** Select from a candidate list that
  is passed in, so the rotation (dedupe against the ledger, rung mix, slot passing, aging) is
  testable on fixtures while the data source is unreachable; the source only changes who fills the
  list.

## What each line carries

- The key the worker reads off the label (code) and the shortest name that identifies it.
- **What the system currently says is there.** The comparison value is the whole point: a list
  that names items without their recorded quantity cannot correct anything.
- **Why it is on the list**, as a short reason code — the worker decides what to do with the
  difference by that reason (a negative is a recording error, a zero-with-sales is likely
  unrecorded merchandise).
- **No names of people or free text** unless the block's whole purpose is that. Free text is what
  forces the rendered output out of the versioned repository.

## The canary that holds the block back

- The classes must **sum to the universe**: entities with a row in the balance/movement table for
  that entity. Print the universe beside the class counts, always.
- **Reconcile the two cuts before the total prints.** A class counted from an export and the same
  class counted live will differ, and the difference is usually the universe (all codes vs active
  codes) or the source (a report's column vs the table). Declare both readings, do not average
  them, and hold the block's total until one is explained — the block can print its *design* and
  the pending reconciliation, never a total nobody can source.
- **A class with no control group is an anecdote.** "The record is wrong" needs the number that
  says how often it happens over the same period, not one example.
