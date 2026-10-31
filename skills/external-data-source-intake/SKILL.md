---
name: external-data-source-intake
description: "Use when a non-ERP data source lands for analysis - GPS, telemetry, fleet traces, CKAN or open-data catalogs, supplier portals, river levels, fuel prices, weather APIs - and its numbers will be crossed with project masters or published. Covers reader shrinkage, threshold sweeps, interval overlap, stacked series, SOAP encoded arrays, and declaring what the source does not carry."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [data-quality, telemetry, gps, fleet, geocoding, validation, open-data, ckan]
    category: productivity
    related_skills: [erp-business-analysis, empirical-system-invariants]
---

# External data source intake

A file arrives from a system that is **not** the project's primary system of record — a
GPS/telemetry platform, a supplier portal, a provider's export — and its numbers are about
to be crossed with the project's own masters (customers, routes, stock, vehicles) or
published in a report.

The defining hazard of this class: **the file reads fine.** It opens, it parses, the
columns make sense, and it yields plausible figures. Nothing throws an exception. Every
failure is a silent shrinkage or a definition artifact — rows discarded by a reader built
for another format, a column that looks summable and is not, a figure that measures a
parameter *you* chose. So the work is not "read the new file": it is **establish what the
project would do to this file, and what the file cannot answer, before quoting anything.**

Deliverables go in the user's own language and register; the gates below are what earn the
right to publish them.

## Cuándo NO aplicarla

Si el pedido es cómo abrir un CSV o qué librería usar, se responde **solo eso**. Esta skill
aplica cuando un archivo ajeno al sistema de registro del proyecto está a punto de cruzarse
o publicarse.

## Gates — all of them, before any number leaves the analysis

1. **Measure the project's own reader against the raw file first.** Run the source through
the pipeline that already exists (`leer()`, `_filas_crudas()`, the subtotal guard) and
compare its row count with the raw count. A reader built for the primary system's export
shape will quietly eat another system's rows: a guard keyed on "the primary id is numeric"
discarded **100%** of a telemetry file's rows (its id is an alphanumeric mobile code), and a
reader that opens only the first sheet returned **527 of 2,514** rows of a multi-sheet
report. Neither raised anything; both produce a smaller report. Count flagged rows *and read
three of them* — flagging everything is as suspicious as flagging nothing.
2. **Sweep every parameter you chose, and publish the sweep.** Any threshold, radius,
window or tolerance is a choice, and a figure that moves with it is measuring the choice.
Measured: the same universe of customers "never visited" gave **73,6% at 50 m, 26,5% at
150 m and 8,2% at 400 m**. A swing of several x is not a datum with uncertainty; it is an
artifact of definition. Publish only the part that does not depend on the parameter, or the
figure with the value used beside it.
3. **Sum an interval column per entity, never across entities.** Time- or distance-valued
columns that represent intervals overlap. Check overlap *within* an entity first (there it
is a defect), then sum per entity: across entities the overlap is usually legitimate and
large — the delivery vehicles park at the same depot every night, which made one
`Tiempo Detención` read **1.021,5 h summed against 275,2 h unioned**.
4. **Declare what the source does *not* carry.** The field someone asked about is often
   absent from this system entirely. Say so in the document, as an open question: a missing
   capability left unmentioned reads as covered. Do not "find" the field in a derived export
   that inherited no such column — go to the original file, and check its column types, before
   concluding either way.
5. **Before recommending a table as the input for the next stage, open it and read its
   columns — a sheet's name and row count are not evidence of its grain.** A second sheet that
   looks richer than the first (more rows, a name like *Parciales* / *Partial* / *Detail*) reads
   as the finer-grained version of the same data and gets recommended onward on that basis. The
   columns are what decide: a "trips" sheet with start time, end time and distance and **no
   destination, customer, coordinate or heading column** cannot say where anything went, and it
   is a decomposition of movement between engine stops, not a trip log. Measured cost: the
   richer-looking sheet was written up as the input for a routing cross-check, and the claim
   had to be retracted once the columns were read. **The column list is the deliverable of that
   check** — quote it, so the next reader does not have to re-open the file to know what it can
   answer. And when the source *does* carry the location you need, it is usually in a plain
   sibling table you already have: prefer the one with the location column over the one with
   more rows.
6. **A figure from a source that updates continuously travels with its window, its coverage and its
   fetch time — and the payload behind it gets archived.** River levels, fuel prices, weather and any
   live API move between two runs of the same day: the current period enters **incomplete** and
   changes on its own, so a number quoted with no window is not reproducible two hours later. Quote
   the field **the tool already computed**, with its declared coverage, rather than your own
   arithmetic; if you do compute by hand, put the result **beside** it as a control with a written
   tolerance; and archive the payload as a fixture with its `sha256` in the project, because a
   hand-derived figure over a payload nobody kept cannot be defended the next day — that is exactly
   how a figure gets published and retracted the same day. Read the payload's own note field before
   completing anything it leaves open: it often declares the trap for you (a unit it does not state,
   a `-999` that means "no data"), and what it says is unknown is not inferred. Two further rules
   when the source is a series: the **maximum window the tool accepts is part of the figure** (a rise
   measured over a 92-day cap is "in 92 days", never "from the year's minimum"), and a
   reconciliation between two paths to the same source **does not have to close exactly** — when one
   mean weights by reading and the other does not, the residual is the mechanism: declare the cause
   and the tolerance instead of forcing equality or hiding the gap.

7. **A source that gives you the quantity rarely gives you the threshold that turns it into a decision —
   go find that outside, and prefer the structured table over the prose.** A level, a rate, a price is not
   a finding until it is read against the rule that defines "high" / "over" / "late", and that rule lives
   in a regulation, an emergency protocol or a spec — not in the API. Measured: a river level that read as
   "the highest in ten years" only became an answer when set against the official three-rung ladder
   (warning / safety / sensitive-affectation): the window's mean sat **0,02 below** the safety rung while
   the same window's daily peak crossed it by **0,52**, so *which rung* you compare against decides the
   sentence. Two traps: the official page **contradicts itself** (its prose quoted one safety figure and its
   table another — use the table, declare the difference), and the number circulating in the press is
   usually that day's **forecast**, not the threshold. Cross-check the ladder against a second body
   publishing the same rungs under other names: two independent bodies reproducing the same pair is what
   confirms you read the ladder right, and a recorded extreme you only have from the press is cited *as the
   press*, never as official.
   - **A second, independent source of the same quantity is the control — and its disagreement is the
     evidence.** Where the quantity is well defined the two must agree; where they diverge, the divergence
     itself tells you what you measured: two public elevation models agreed to ≤2 m on dry ground and
     diverged by tens of metres over the water, and that divergence is what proves the point was river. A
     single source with no contrast says nothing about *what* it is measuring.
   - **A difference between two points of ONE source is valid; a conversion between two datums is not.**
     DEM metres are not port cotas — the offset is a constant the source does not publish, so state it as an
     explicit limit (and what would close it) instead of estimating it. The limit written down is worth more
     than a number that will not survive review.
   - **Name the comparison target in the test, not in the prose.** "Tens of metres above the water" and
     "above the riverbank" are two different claims; a check that compares against the *maximum* of a window
     it meant as the *low* reference passes or fails for the wrong reason. One constant per claim.

## Procedure

1. **Raw inventory before interpreting anything:** files, rows per file *and per sheet*,
   and the real header (`repr()` of the first cells). Never interpret before knowing what
   exists — and count rows per sheet, because a multi-sheet report read through a
   single-sheet reader loses whole sheets without a word.
2. **Fingerprint the inputs** (`sha256sum`) and record the periods each file declares.
3. **Measure what the project's own reader discards** (gate 1), and what the subtotal /
   total guards do to this file in particular.
4. **Resolve the entity keys** — which vehicle/person/site each code is — against a source
   that actually names them (an on-screen admin list, a master with descriptions). If no
   file and no screen names them, the mapping is **not inferable**: report it as a question
   to the source.
5. **Cross against the project's masters** by key or by geography — never by capacity or by
   narrative convenience ("this one must be the truck for the north route").
6. **Sweep the parameters** (gate 2), then write: source hashes, the periods, a **trap
   section** listing each reading trap with the row count it affects, and an explicit
   section for what the source does not carry.

### Locating a fixed site from its own stops (and the name trap that fakes a point)

A fixed place of the operation — a depot, a branch, a regular stop — usually has **no
coordinate column**. The fleet is the evidence: it repeated there. Prefer deriving the
coordinate from those repeated stops over geocoding the address, which depends on the address
being typed correctly. This is the constructive mirror of *"a single location shared by many
entities is a base"*: the same cluster that you must not read as activity is what lets you
place the base.

- **Convert the timestamp before filtering.** These files carry datetimes as **Excel serials,
  not text** (`46279.305868055555`); a filter written against text silently empties the window.
- **Match the full, exact street name.** A bare surname (or an avenue's bare name) matched
  three streets of the same surname plus the whole avenue, and the median fell **between** the
  clusters — a point that is not any declared address, with the shape of a clean result. One
  street can also have **two separated stretches** (the site vs. a delivery area kilometres
  away). Use a whitespace-tolerant full-name pattern, and a test that asserts it does *not*
  admit the homonym.
- **Anchor per how the address is declared, and differently per address.** An address given as
  a corner is a **point** (the intersection); one given as "N metres from the landmark" is a
  **radius** to that landmark. Averaging the two modes, or averaging across the two stretches,
  yields a coordinate nobody stated.
- **Take a weighted centroid, not a flat mean of lat/lon** (Weiszfeld) — lat/lon is not a plane.
- **Before quoting it, print two checks:** the distance from the inferred point to its declared
  anchor, and the **spread** of the contributing stops. A large spread, or a point far from the
  anchor, means the match captured other streets. A point with no such check is the same
  failure as a cross with no denominator.
- **A straight-line distance is not a driving distance.** With no routing service available,
  use haversine and **state it** in the document; and when comparing two candidate sites, the
  aggregate median hides the decision — measure per locality and against a random baseline
  (gate 2), because "closer on average" can be an artifact of the geography.
- **Distinguish a real base from a GPS default by whether the entity RETURNS there.** The
  first point of the day is where a vehicle slept — but a device that reports before it
  fixes satellites also emits one repeated coordinate as its first point, and that looks
  identical. The control that separates them: require the entity to **also end the day at
  the same point**, and that the point be a non-trivial share of its trace. Measured: three
  trucks opened and closed 20/20, 17/17 and 18/20 days at the same spot, and that spot was
  13–22% of every truck's points — a base. A default appears *only* as a first point.
- **The raw position trace gives real km with no router.** Telemetry sampled every ~30 s
  carries both an absolute odometer and lat/lon; `max−min` of the odometer is ground truth,
  and the haversine between consecutive points is what a router would return — **skipping
  jumps larger than a few km**, which are signal gaps and not travel (measured: summing one
  such gap invented 226 km on a day the odometer read 46,8). Cross the two: agreement within
  a few percent validates the method and gives the km that the aggregate analysis declared
  missing. It validates a router; it does not replace one for a *counterfactual* route.

## Pitfalls

- **Una fuente pública de obligados contiene a los que NO reportan, y eso suele ser el dato más
  accionable.** Un padrón regulatorio (registro de precios, de establecimientos, de habilitación)
  publica la lista de sujetos obligados *y* sus datos: cruzar los dos lados mide el cumplimiento
  del otro, no el tuyo. Medido: de 19 comercios que el Estado declara obligados a informar precios
  diarios en una ciudad, **6 no tenían una sola fila de precio en el año** — dos de ellos de la
  misma razón social. La lista de quién está afuera del régimen es más accionable que el promedio
  de los que están adentro, y no la da ninguna suscripción paga. Contar los dos universos por
  separado (declarados vs. reportantes) antes de calcular cualquier estadística sobre el segundo.
  Y el padrón de sanciones del mismo organismo es la otra mitad: mide a qué ritmo y por qué motivo
  el Estado llega a los que no informan (medido: la sanción más frecuente de todas era «precio no
  informado»).
- **El mismo producto, el mismo día, en la misma ciudad, varía más de lo que uno supone.** Antes de
  tratar un precio de fuente externa como "el" precio de un SKU, medir su dispersión entre puntos:
  medido, un artículo del mismo relevamiento público variaba hasta **2,59× la mediana** (y 1,45× en
  los productos que el operador también vende). Un promedio sobre eso no es un precio.
- **Una cifra horneada en la prosa de la consulta es la más probable de estar mal.** De nueve
  afirmaciones de contexto, dos se cayeron al probarlas (un conteo de establecimientos que el padrón
  desmiente, y un orden de magnitud de clientes: 800 dichos contra 2.249 medidos) y una traía la
  sustancia bien con los endpoints de API equivocados (todos 404). Probar afirmación por afirmación
  contra la fuente, y anotar en la tabla cuál se confirmó, cuál se corrigió y cuál quedó sin
  verificar.
- **Un documento que afirma que el proyecto YA tiene un insumo es una afirmación como cualquier
  otra, y es la que decide si el cálculo cierra.** Cuando una ronda previa —externa o propia— deja
  escrito que el proyecto ya cuenta con el dato que falta («el repo ya tiene los litros por
  camión»), verificarlo contra el proyecto antes de construir nada encima: es la *precondición* de
  toda la tarea y, si es falsa, el cálculo no cierra por más que la fuente nueva entre perfecta.
  Medido: la afirmación de que los litros ya estaban resultó falsa en tres documentos del proyecto
  y buscar el archivo daba cero — la fuente externa (precio por litro) se podía incorporar, el
  costo por km no. **La fuente externa y el insumo interno son dos cosas distintas: incorporar una
  no crea la otra.** Al planificar, separar siempre «esto entra hoy» de «esto queda bloqueado
  hasta que exista X», y dejar el bloqueante escrito con su pregunta y su dueño.
- **El nombre de un campo no dice su contenido — y una fuente puede traer las columnas invertidas.**
  Medido en una serie pública de precios de combustible: el encabezado declaraba `Unidad` y `Valor`,
  pero **`Unidad` traía el número y `Valor` la unidad de medida** (`'68,6'` y `'$/kg'`). Quien sume
  la columna que se llama "Valor" suma unidades de medida. Antes de usar una serie, imprimir una
  fila y comprobar que el número esté donde el nombre dice. Mismo cuidado con un recurso que dice
  `CSV` y es un ZIP (magic bytes `PK`), o con un archivo que dice "nacional" y tiene una columna
  `CCZ` (Centro Comunal Zonal: **es de una sola ciudad**). El campo que decide el alcance es el que
  hay que mirar primero, no el título del dataset. Y el encabezado puede traer el BOM **dos veces**
  (`\xef\xbb\xbf\xef\xbb\xbf`): `utf-8-sig` quita uno solo, así que el primer nombre de columna no
  compara contra el literal (`'Año'`) y parece que las columnas cambiaron. Limpiar el `\ufeff`
  residual del primer campo antes de comparar el encabezado, o el lector rechaza un archivo sano.
- **Un archivo puede traer la MISMA serie apilada muchas veces, y el total se multiplica en silencio.**
  Una fuente que publica periódicamente puede emitir, en cada publicación, la serie **entera hasta ese
  momento** y acumular las publicaciones en un solo archivo — en vez de una fila por período, el archivo
  guarda una por *publicación × período*. Medido en una serie pública de precios de combustible: **25.364
  filas de publicación para 1.232 combinaciones (producto × año × mes) distintas**, o sea **20,6× la misma
  serie**; el precio de un mes aparecía **29 veces**. Sumar o promediar las filas mide la cantidad de
  publicaciones, no el precio. Síntoma barato: calcular `filas / (productos × períodos)` y ver que da
  mucho más que 1. Es el defecto de la lámina «Todos» que es la suma de sus hermanas, un nivel más arriba
  (una dimensión de tiempo apilada en vez de hojas hermanas). Deduplicar por la clave real (entidad,
  período) antes de citar cualquier mes o total, y declarar el criterio de desempate cuando un período
  tenga dos valores (medido: 2 de 56 pasaron de precio a «sin cotización»; un valor que existió no se
  pierde porque una publicación posterior diga que no).
- **Contar líneas no es contar filas: un archivo con líneas en blanco tiene más líneas que datos.**
  Medido: un archivo traía **25.366 líneas bajo el encabezado** pero **25.364 filas de datos** (2 en blanco);
  una "corrección" que contó líneas con `splitlines()` pasó a publicar 25.366 y **rompió el número bueno que
  el documento original ya afirmaba**. Contar filas con un parser de CSV (`csv.reader`, saltando la fila
  vacía), nunca con `splitlines()` ni `wc -l`. **Y antes de "corregir" una cifra que un documento previo ya
  afirmaba, mirar qué explica una diferencia chica:** un delta de 2 sobre 25.000 casi nunca es un error
  de quien contó antes — es una fila que no lo es (línea en blanco, subtotal, encabezado repetido). El número
  viejo suele ser el que usó el parser bueno. Cuando la diferencia no se explica, se dice en el documento;
  no se reescribe la cifra a la del conteo propio.
- **Un archivo de hoy suele ser un año de una serie, no la serie.** Antes de dar por agotada una
  fuente, buscar sus hermanos en el mismo catálogo: medido, el padrón que se había tratado como
  "2026" tenía datasets por año hasta veinte años atrás, cada uno con su propia tabla de entidades.
  Un dato con veinte años atrás es una serie; con uno, es una foto.
- **Dos datasets hermanos con casi el mismo título miden cosas distintas: se elige por definición,
  no por parecido del nombre, y se confirma que el archivo usado es el de ese dataset.** Medido en
  un catálogo público: «Precios de Combustibles - Poder Ejecutivo» es el precio máximo al público
  con IVA incluido (por decreto), y «Precios de Combustibles - ExPlanta» es el mismo producto *neto
  de flete, tasas y margen* — dos datasets, dos números, títulos que difieren en dos palabras. Un
  documento que cita «los precios de combustibles del organismo» sin decir cuál no dice qué mide. Regla:
  nombrar el dataset por su título exacto en la cita, y comprobar por `sha256` que el archivo que
  se usó es byte por byte el recurso de ese dataset, en vez de asumirlo por la descripción.
- **La búsqueda de un catálogo puede estar rota sin decirlo, y también puede devolver cero sobre
  una fuente que sí está.** Medido: el endpoint de búsqueda por relevancia de un catálogo de datos
  del Estado devolvía `count: 0` para *todos* los términos, con los datasets presentes y visibles
  en el listado completo — o sea, quien buscaba no encontraba nada que sí estaba. Y la cara
  inversa, medida en el mismo catálogo: una búsqueda **filtrada por un valor que no existe**
  devuelve cero igual de limpio (filtrar por la etiqueta `clima` da **0**) mientras el filtro por
  organismo sobre el mismo tema da **7**. Un cero de una consulta es el resultado más peligroso de
  leer como «no hay»: re-consultar por otra vía antes de concluir nada. La técnica que lo evita
  —texto libre vs. filtro por campo, facets, y el total del catálogo que cambia según cómo se
  pregunte— está en `references/ckan-open-data-catalog.md`.
- **Una respuesta SOAP *encoded* nombra los elementos del arreglo `item`, no por su tipo, y buscarlos por
  tipo da una lista vacía sin error.** Medido en un webservice público: el WSDL declara el retorno como
  `soap-enc:Array` y el XML trae `<return SOAP-ENC:arrayType="ns1:Estacion[75]"><item>…</item></return>`;
  un lector que hace `findall('Estacion')` devuelve **0 estaciones**, y «0» parece un servicio caído cuando
  es un lector roto. Imprimir una respuesta cruda y mirar los tags reales antes de elegir cómo parsear, y
  **rechazar el arreglo vacío como error** en vez de devolverlo como resultado: «0 filas» y «no hay nada» no
  son lo mismo. Aplica a cualquier fuente cuyo arreglo se lea por nombre de tipo, no solo a SOAP.
- **A summary sheet that is the exact sum of its siblings is one level up from the total-row
  trap: aggregating the report double-counts it, silently.** Some sources emit both a combined
  sheet (`Todos` / `All` / `Total`) and one sheet per entity, and the combined one is usually
  present when the per-entity ones are. Measured: the combined sheet's 787 rows were exactly
  the sum of the five per-entity sheets (260+139+309+33+46), so iterating every sheet returned
  **100% more** than the truth with no exception and a plausible-looking total. Assert the
  identity (`sum(per_entity) == combined`) once, and drive aggregation off an explicit
  exclude-aggregate-sheets accessor. **Do not detect it by an empty entity column** — in the
  same corpus another report's two sheets both carried a blank entity column and were *not*
  duplicates, they were two grains of one job; the sheet *name* was the only reliable marker.
  This is the same failure as a subtotal row, one level up, so treat any "combined" sheet as a
  subtotal until the identity is checked.
- **A detail sheet can be a second representation of the same job, not additional work.** When
  two sheets of one report close on the same total (measured: one day-grain sheet and one
  movement-grain sheet carrying identical kilometre sums), they are two views of one thing and
  must never be added together. State, for every pair of sheets you consume, whether they
  compose or overlap.
- **The roster is not activity.** An entity listed in the master with an odometer or hour
  meter loaded and **zero rows in every table** is an entity given access that does not
  report — not one that does not operate. Count entities with zero rows in *each* table,
  not in one, because the first table you checked may be empty for an unrelated reason.
  And when the fleet is smaller than the roster, resist assigning the surplus code to
  "the one that must be missing": a false story built on true numbers is the most
  expensive output of this class.
- **Two files are two universes only if their hashes differ.** Exports that *should* be
  different ("stops inside zones" vs "stops outside zones") can be byte-for-byte
  identical when the feature behind them was never configured. `sha256sum` the pair before
  contrasting them: otherwise the comparison reports a clean zero over one file twice.
- **Third-party geocoding contaminates any coverage figure built on it.** When a large
  share of the universe has no coordinate, the measured "coverage" is coverage of the
  geocoding as much as of the operation, and remote-region coverage is usually the worst of
  all. State how many of the universe dropped out for lack of a coordinate, and treat a low
  coverage as a possible visibility gap (a third party may be serving that area) rather than
  a service gap — as a hypothesis, never as a result.
- **A single location shared by many entities is a base, not many visits.** Hundreds of
  records at one coordinate and one repeated reference string is a depot. Group and look at
  the mode before reading it as activity.
- **Heavy spatial joins need a grid.** Bucket by cell and compare within neighbouring
  buckets; the naive all-against-all version does not finish inside a tool timeout, and a
  job that gets killed mid-way leaves a half-written result rather than an error you notice.
- **A column's unit and meaning are not given by its name.** "Stopped time", "idle time" and
  "engine on" can be separate reports over the same interval, and a vehicle reporting a full
  24 h of engine time on non-working days including weekends is a finding about the source
  (real engine, a signal that never switched off, or stationary working) — list the readings
  and say which cannot be closed from the file, instead of picking one.
- **A file derived from the source may be worse than the source.** The original `.xls`
  carried the street/reference columns that the derived `.csv` had dropped. When a value is
  missing in the derived export, go back to the original before reporting it absent.
- **A location column that reads as a partition may be a coverage gap.** A zone/city field can
  be populated for the operator's home base and be effectively empty for exactly the remote
  areas you wanted to segment by — not because the field is broken, but because those areas are
  served and recorded elsewhere. Measured: a `Ciudad` column read 96% one city and none of the
  two northern localities, so a "cost per zone" partition was not computable from it at all.
  Count the distinct values before designing any cut on a location field, and when the values
  you need are absent, say the cut is impossible from this source instead of bucketing the
  remainder into an "other".
- **A measured example baked into prose is the number most likely to be wrong next time.**
  The figures in this skill (the row counts a reader ate, the threshold sweep) were taken from
  one project's file at one moment and are kept for the *shape* of the failure, not as
  current values. When you cite any of them, re-derive it from the file in hand, or mark it
  as the historical reading it is — a reader cannot tell a measured example from a live figure
  and will re-quote it as the latter.
- **Non-ERP input takes no provenance seal.** If the project's pipeline stamps provenance
  from the primary system, a document about an outside source derives from no such export:
  state that in the document so the missing seal is not read as an oversight.

## Support files

- `references/ckan-open-data-catalog.md` — la técnica para trabajar un catálogo de datos abiertos
  (CKAN: Uruguay, Argentina y casi todo Latinoamérica): la acción genérica, texto libre vs. filtro
  por campo, los facets para elegir una fuente con el número, y `datastore_search` para consultar
  filas sin bajar el archivo.
- `references/interval-and-threshold-measurement.md` — the measurement depth behind gates 2
  and 3: interval overlap detection, sum-vs-union worked numbers, the threshold sweep table,
  the geocoding confound, and the grid-based spatial join.
- `references/elevation-and-threshold-anchoring.md` — la profundidad detrás de la compuerta 7: dos DEM
  públicos independientes, la grilla 3×3, el canario del desacuerdo, las cotas oficiales con sus tres
  escalones, y cómo se cierra una pregunta territorial («¿el agua llega a este predio?»).
- Complements a dedicated file-reader skill (magic bytes, guards) — load that one for the
  parsing mechanics, this one for what to establish before a new source's numbers are published.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/external-data-source-intake`). Editar
acá, nunca la copia instalada.
