# Why the printed report has more sheets than sections

Everything here is measured on the rendered artifact, never estimated from the markup: a layout that
looks right in a browser screenshot still breaks at the page boundary, and the boundary is what the
reader holds.

## 1. Count the sheets, and locate the overflow

Render the report the way the sender does (same browser, same print flags) and count the pages with a
PDF reader. `pypdf` is usually not a declared dependency — run it ad hoc:

```bash
uv run --with pypdf python -c "import sys;from pypdf import PdfReader;print(len(PdfReader(sys.argv[1]).pages))" <salida.pdf>
```

Then measure each top-level block of the page. Copy the rendered HTML, append **one** script that
writes every block's height into a `<pre>`, and read it back from the browser's DOM dump (the same
browser binary the generator uses; on Windows it lives under `Program Files`):

```html
<script>
  const out = [...document.querySelectorAll('.sheet, .hoja, section')]
    .map((e, i) => `${i}: ${(e.getBoundingClientRect().height * 25.4 / 96).toFixed(2)} mm`);
  document.body.insertAdjacentHTML('beforeend', `<pre id="m">${out.join('\n')}</pre>`);
</script>
```

```bash
chrome --headless=new --disable-gpu --virtual-time-budget=3000 --dump-dom <copia-con-sonda.html>
```

Usable height of the paper = `paper height − 2 × page margin` (A4 with `@page { margin: 10mm }`:
277 mm). The block that passes it is the one that spills.

**A block that carries a `min-height` reports the floor, not its content.** When the sheet is styled
as a fixed-height block (a flex column with `min-height`/`height` and `margin-top: auto` pushing a
footer to the bottom), the block's own height reads as the declared value while what overflows is
the content inside — so also measure the block's **children**, and re-measure with the `min-height`
zeroed on the probe copy. The overflowing child is usually the last one: in that layout everything
past the boundary is the footer, which is why the extra sheet comes out nearly empty and the footer
looks unrelated to the problem.

## 2. Render the CLEAN copy, and vary one value per run

- **The copy you measured is not the copy you print.** The injected probe adds content and pushes
everything down: rendering the probed copy counts an extra page and confirms a defect that is not
there. Measure with the probe, print the copy without it.
- Change **one** value per run (`--print-to-pdf`, count pages) and tabulate: block height in mm plus
  sheet count for each value of the knob (inter-block gap, row height, font size). The value that
  ships is the first one that holds on **every** variant measured — including the longest day in
  `deliverables/`, not just today — and the table goes into the code comment so the next person does
  not re-derive it.
- Count the pages of the historical outputs too. It separates "this broke today" from "this has been
  happening since the change landed" and tells you which variants need re-checking.

## 3. Re-render a day's output without overwriting what was delivered

The rendered files under the delivery directory are the record of what was printed and mailed, so they
are not the test fixture. Point the whole data root at a scratch directory and re-feed the saved source
output instead of querying again:

```bash
NEW_ROOT=<scratch> uv run --with-requirements requirements.txt python <entry point> \
  --desde-archivo <salida guardada de la consulta>
```

- With the data root redirected, nothing the command writes touches the delivered copy — and the
  delivered copy is verified afterwards (timestamps and page count unchanged), because "I ran it in a
  scratch dir" is a claim you can check.
- **The command still writes state inside the repository** (a ledger, an action queue): check the
  working tree and revert those files before committing, or the commit carries a test run's state.
- Some columns are derived from **previous days' outputs**: in a scratch root that history is missing
  and they degrade silently (an age column reads "new" instead of "on the list since Monday"). The
  page count does not depend on them; if the re-rendered copy is quoted anywhere, declare the
  degradation instead of presenting it as a change in the data.

## 4. Say what the fix does not cover

- The slack is single-digit millimetres: a longer day overflows again. A count-the-pages check inside
  the generator is the guard that catches it, and if it is not built, say so.
- A tighter layout is a cosmetic cost paid by the reader: state it and offer the real alternative
  (drop content from the crowded sheet) rather than tightening the air indefinitely.
