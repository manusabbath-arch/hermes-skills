# The corruption harness

For the class "this reader keeps returning plausible-but-false output". No unit test written from
the reader's own assumptions catches it: those tests encode what the code does, and the defect is
that what the code does is wrong on an input nobody tried.

## Corrupt the data, not the code

Mutation testing the code (mutmut, cosmic-ray) is the reflex and usually the wrong instrument: it
needs a spawn budget and a full test→mutant→test loop, it mutates branches the reader does not own
(stdlib, third-party parsing), and the mutations it generates are syntactic, not semantic. The
corruptions that matter are already known — every strict reader carries a docstring listing the
traps it was measured against — so the harness just turns that list into cases. The default suite
stays offline, fast and deterministic because every fixture is built in a `tmp_path`.

## Shape

Two frozen dataclasses and two parametrized tests. `Trampa` is one documented corruption; `Valido`
is the same source, uncorrupted.

```python
@dataclass(frozen=True)
class Trampa:
    nombre: str
    escribir: Callable[[Path], Path]      # builds the corrupted file AND asserts what the reader does
    afirmar: Callable[[Path], None]

@dataclass(frozen=True)
class Valido:
    nombre: str
    escribir: Callable[[Path], Path]
    leer: Callable[[Path], object]

@pytest.mark.parametrize("caso", TRAMPAS, ids=[c.nombre for c in TRAMPAS])
def test_la_trampa_declarada(caso, tmp_path):
    caso.afirmar(caso.escribir(tmp_path))

@pytest.mark.parametrize("caso", VALIDOS, ids=[c.nombre for c in VALIDOS])
def test_el_archivo_valido_pasa(caso, tmp_path):
    resultado = caso.leer(caso.escribir(tmp_path))
    assert resultado, f"{caso.nombre}: leyó cero filas"
```

## Rules that make it work

1. **The assertion lives inside the builder**, and the test only calls `caso.afirmar(caso.escribir(...))`.
   The builder then reads as one sentence — "the error response must not be read as a month with no
   quote" — with the setup, the call and the expectation in one place. `afirmar` stays
   `lambda p: None` for every case, so adding a case is one function, not three edits.
2. **The inverse half is not optional.** A reader that rejects everything passes every rejection
   case. `VALIDOS` is the half that catches the reader which is strict in the wrong place, and it
   is the half people skip. Assert the result is non-empty, not merely that it did not raise.
3. **Name each case as the sentence a person would say**, in the user's language, and let it be the
   pytest id: the failing report then says what broke instead of `test_param_7`.
4. **The fixture must reproduce the artifact's real shape, not a paraphrase of the defect.** A
   near-miss trips a *different* branch and the test goes green proving nothing: the row meant to
   pin "a row with no date is skipped" was built without its empty leading field, so it hit the
   "wrong column count" rejection instead. After the first green, read the error message (or the
   returned count) and confirm it came from the rule the case names.
5. **One corruption per builder; no fixture shared between cases** that a later case could silently
   mutate. Build from a helper that writes a whole valid file, then pass the corrupt rows to it.
6. **Keep the harness offline.** The one case that needs the network goes in the red/marked suite as
   a single canary, never as the loop.

## Picking the corruptions

- One per trap in the docstring / README table — that table is the contract, and until each row is a
  case the contract is prose.
- The ones measured on the real artifact, with the measurement date in the docstring so a reader
  knows which figures to distrust.
- Specifically the *harmless-looking* ones: a doubled byte-order mark, trailing spaces in an id, a
  `0` that is a measured zero next to a missing value, a column whose two halves are swapped while
  the header still reads plausibly. That class never raises, and it is the one that costs a
  published figure.
- Not the ones the reader cannot control (a truncated download, a 500). Those belong to the network
  layer and its retries.

## Cost

Nine cases run in about half a second, need no new dependency, and join the default suite — so the
cheap gate is on every commit rather than on a special run. A new reader adds one row to each table;
when someone adds a row to one table only, that is visible in the count.
