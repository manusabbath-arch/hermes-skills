# A chat write loop: a person records a fact the source cannot

## Contents

1. The shape
2. State, and why it lives in the book
3. The id is what makes it idempotent
4. Failure paths answer, they never raise
5. The join
6. Guards, tests, what not to do

Use when a field the data source does not carry can only be known by the person who was there —
whether the tank was filled, whether the truck came back whole, what a checker actually counted —
and the ask is to get that fact back into the versioned book without anyone typing a number.

This is the write half of a reply bot. It is worth building only when the missing field has a
**measurable consequence** that is currently degenerate (a ratio that returns null, a difference
that cannot be computed, a guard that cannot fire). Say the measured gap before designing the flow;
without it the loop is a form nobody asked for.

## The shape

1. **The artifact opens the record.** A photo of the paper (a ticket, a receipt, a delivery sheet)
or a bare command. Receiving it creates a row in the book in an **open** state and stores the
artifact; it does not interpret anything yet.
2. **Question one is a choice between few options, so it is buttons** — one inline button per
subject (the vehicles of the fleet, the open cases). More than about eight options is the signal
the subject should have been in the artifact's key instead of in a keyboard.
3. **Question two is a yes/no** — the field that was missing. It is the whole reason the loop exists.
4. **The receipt is the same message, edited** (`editMessageText` with the new `reply_markup`), not a
new message per step. A three-message chat for a two-tap task is what teaches people the bot is
noise.

Never ask for a number the source already has. Asking for litres because «the ticket says litres»
reopens the hand-keyed-data problem the loop exists to close: the source is the authority for what
it measures, the person is the authority for what only they saw.

## State, and why it lives in the book

The record is a line in an append-only `.jsonl` in the versioned store, one per record, rewritten
in place as the flow advances (`estado: abierta` → `declarada`). The listener holds nothing.

Why not memory: the process is restarted by the OS on crash, on a logon, on a deploy, and the
operator may answer the second question after lunch. Why not a session file: a second machine or a
restart loses it silently, and the operator gets a keyboard that answers «no existe».

Typical row:

```json
{"id": "car-f910c72048", "estado": "declarada", "movil": "ABC1234", "lleno": true,
 "foto": "<path>\\2026-10-23-car-f910c72048.jpg", "chat": "<id>", "mensaje_id": "91",
 "cuando": "2026-10-23T17:08:11-03:00"}
```

- `cuando` **carries the offset**. A naive local timestamp in a book that will be joined against a
  source on a ±window is a bug that only shows up in the join, months later.
- The artifact's path, never the bytes: a ticket carries a driver's name and a tax id, so the file
  lives outside the repo and the book keeps only its path.

## The id is what makes it idempotent

Derive the id from `chat:message_id` through the repo's existing id helper. Two properties fall out:

- **Redelivery is free.** The updater hands the same update again if the process dies before the
offset is committed; the deterministic id turns that into the same record, not a second one.
- **A stale keyboard cannot write.** The book is read first; a record already `declarada` answers
«ya estaba declarada» and is not modified. Otherwise a keyboard from last week marks today's load.

Write the idempotency tests explicitly — same artifact twice gives one row, a second tap on a closed
row changes nothing — because they are the two ways this loop corrupts data and neither shows up in
a happy-path demo.

## `callback_data` is 64 bytes and must carry the record

`<verb>:<record-id>:<choice>` — e.g. `ll:car-8f3a2b1c90:si`. The id in the payload is what lets a
button pressed later find its row without any server-side session. A payload made only of the choice
(`lleno:si`) forces you to guess which record was meant, and the guess is wrong exactly when two
loads are open at once.

Answer every callback (`answerCallbackQuery`) even when you are about to edit the message:
unanswered callbacks leave a spinner on the operator's screen and, in some clients, a «loading» that
never resolves.

## Failure paths answer, they never raise

The handler is called from the same loop that serves the rest of the channel. A photo that fails to
download, a callback with an invented subject, a book with no such id — each returns a short message
(`No anoté nada: la matrícula XX9999 no es de los móviles…`) and the loop continues. One malformed
tap must not take down the channel that also delivers the daily report.

Validate choices against the declared universe in code, not by trusting the keyboard: an old
keyboard, a forwarded message or a hand-crafted callback all carry whatever they like.

## The join, which is where the value appears

Keep the join a **pure function** over (source rows, declared records, window) and pass the window as
a parameter. Rules that keep it honest:

- A declaration matches a source row only inside a window (an hour is the usual scale, because the
  source records the pump's time and the person records their own).
- What falls outside the window is a **rejection with a reason**, listed, not dropped.
- A source row with no declaration keeps the missing value explicit (`NO`/`null`), never blank and
  never imputed.
- Two near-but-not-equal numbers (a ticket rounding at the fourth decimal, a pump cutting at two) are
  **reported side by side**, never averaged.

## Guards that make it not decay

- **Age of the last declaration.** A guard that measures days since the last record and goes red past
  a threshold, because a loop nobody uses rots into a column of nulls with no warning.
- **Coverage.** Share of source rows carrying the declared field — it starts at zero and that zero is
the baseline, so the guard has to accept zero as «measured, empty» instead of «broken».
- The declaration book must be committed by whatever job commits the other ledger; otherwise the loop
  writes to a file that never reaches the versioned store and every downstream reader sees nothing.

## Tests, without network or chat

Pure functions for parsing the payload, building keyboards, opening and applying steps, formatting
the receipt, and the join. Inject the three impure edges: the artifact downloader, the clock, and the
book's path (`tmp_path`). Then drive the whole flow from synthetic updates in one test and assert the
sequence of replies — text, keyboard, and `editar` (the message id being edited) — because that is
the only place the two-tap promise is actually checked.

## What not to do

- **Do not read the paper before the confirmation exists.** OCR of a ticket is a second source of
  numbers with no witness; ship the two taps first, accumulate real photos, and only then measure how
  often a reader would have been right.
- **Do not write to the ERP from the loop.** The book is the repo; a person loads the ERP afterwards.
- **Do not trust an ambiguous field on the paper.** A form field labelled `Km` may be the pump's
  counter, not the odometer. Cross it against the subject's previous known reading and reject an
  impossible value instead of storing it — an odometer stored two orders of magnitude off gives a
  consumption figure that is wrong and arithmetic-consistent, which is worse than missing.
