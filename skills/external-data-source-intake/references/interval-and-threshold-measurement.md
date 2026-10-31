# Interval and threshold measurement

Depth behind gates 2 and 3 of `external-data-source-intake`. Load when a new source's
figures are time-, distance- or location-valued.

## Interval columns: the sum and the union are different numbers

A column of durations (stopped time, idle time, engine-on time, a distance per segment)
represents **intervals**, and intervals can overlap. Summing the column counts the overlap
more than once.

Worked measurement, one fleet over twelve days:

| Quantity | Sum of the column | Union of the intervals |
|---|---|---|
| `Tiempo Detención` | 1.021,5 h | 275,2 h |

That is a factor of ~3,7 with no error anywhere. The procedure that separates the two:

1. **Check overlap within an entity.** Parse each row's start/end into real datetimes and
   test whether intervals of the *same* entity intersect. Within one entity overlap is a
   defect in the source — report it. (Parsing trap: the same book can carry dates as strings
   and as Excel serials; a parser that only handles strings raises or silently drops rows, so
   accept `datetime`, `int`/`float` serials (`1899-12-30 + timedelta`) and strings.)
2. **If no entity overlaps internally, the column is summable per entity** — that is the
   union within an entity, and it is the honest number for "how long was this vehicle
   stopped".
3. **Never sum across entities.** Their overlap is usually legitimate and large: three
   delivery vehicles parked at the same depot every night produce hundreds of overlapping
   night-time intervals. Summing the column then reports the fleet's night once per vehicle.
4. **Say which of the two you are quoting**, in the figure's own line. "1.021,5 h" and
   "275,2 h" describe the same corpus under two operations.

The same reasoning applies to a cumulative odometer: it is a per-entity accumulator, not a
fleet counter. An odometer that barely moves while engine-on time reports full days is a
finding to declare, not to average.

## Threshold sweeps: the figure may be measuring the threshold

Any figure defined through a distance or a window ("visited" = a stop within R metres,
"active" = a movement within N days) moves with that parameter.

Sweep it and print the table before publishing:

| Radius | Universe "never visited" |
|---|---|
| 50 m | 73,6% |
| 150 m | 26,5% |
| 400 m | 8,2% |

Three consequences:

- A swing of several x is a **definition artifact**, not an uncertainty interval. Retract it
  in the document that published it — same file, all three figures and the range — and
  publish only what does not move with the parameter.
- Report the parameter with the figure whenever you keep it; a threshold published alone is
  a claim about the world that was never tested.
- The sweep is cheap. Do it before writing, not after being asked.

## The geocoding confound

Whenever "visited / not visited" is computed against coordinates, the result is a measure of
**geocoding coverage plus operational coverage**, and the two are separable only by counting:

- Count how many of the universe have no coordinate at all, and report that number beside
  the coverage figure. Remote regions are where geocoding is worst.
- A low measured coverage in a region where most customers lack a coordinate is not
  evidence of a service gap. State it as an open question, including the possibility that an
  outside carrier serves that area.
- Cross the same question twice when both keys exist: against the **declared route** and
  against the **geographic zone**. They are different questions, and mixing or summing their
  subtotals produces a third, meaningless one.

## Spatial joins at scale

The naive form compares every stop against every client, which does not finish inside a
tool timeout on a few thousand rows and a few hundred stops. Bucket both sides into a grid
(cell size tied to the radius), then compare a stop only against clients in its own and the
eight neighbouring cells, and dedupe by client id. This turns the job into a linear pass; the
version that timed out finishes in seconds.

## Trap table to carry into the document

Publishing a short table of reading traps, each with the row count it affects, is what lets
the next consumer use the file without repeating the diagnosis:

| Trap | Rows affected |
|---|---|
| Rows discarded by the project's subtotal guard | all / N |
| Rows lost by reading only the first sheet | N of M |
| Two "different" exports identical by hash | N |
| Column that looks summable but overlaps between entities | N |
| Records lacking a coordinate (geocoding) | N of M |
