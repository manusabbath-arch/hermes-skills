# Working a CKAN open-data catalog
## Contents

- See headings below. Load this file when SKILL.md points here.


Uruguay (`catalogodatos.gub.uy`), Argentina (`datos.gob.ar`) and most Latin American open-data
portals run **CKAN 2.x**: the same Action API behind all of them. This is the shape of that API,
with the readings taken on Uruguay's portal as a worked example — the counts are what they read
at one moment, so re-derive them before quoting, and never carry them into a report as current.

## The action API

`https://<portal>/api/3/action/<accion>?param=valor` → `{"success": bool, "result": …}`.

Wrap it as a single generic `accion(nombre, **parametros)` that validates `success` and returns
`result`. That is what `ckanapi` — the CKAN organisation's own reference client — exposes
(`action.package_search(...)`, `action.datastore_info(...)`) instead of one function per
endpoint. A `success: false` must raise with the portal's `error`: returning an empty table for
it turns a broken call into "there is no data".

Actions that matter: `package_list` (names only), `package_show?id=` (one dataset with its
resources), `package_search` (query + facets), `datastore_search?resource_id=` (rows of one
resource).

## `q` is free text; `fq` is the field filter

- `q=<texto>` searches free text. A tag name does **not** go here.
- `fq=organization:<org>` filters by field, and is what actually answers "which agencies publish
  about this?": measured — `mides` 1.875 · `intendencia-montevideo` 159 · `ancap` 60 · `correo`
  43 · `ose` 28 · `agesic` 27 · `miem` 25 · `udelar` 23 · `ursec` 23 ·
  `banco-central-del-uruguay` 21 · `opp` 19 · `ine` 15 (50 organisations in total).
- `fq=res_format:<F>` filters by format: CSV 2.554 · JSON 2.271 · XML 2.222 · **XLSX 2.162** ·
  TXT 103 · **XLS 60** · SHP 58 · PDF 53. A reader that only handles CSV ignores two thousand
  resources that are the same corpus as a spreadsheet.
- **A filter on a value that does not exist returns 0, and 0 reads as "there is no data"**:
  filtering by the tag `clima` returns **0**, against **7** for the agency that publishes the
  weather datasets. Re-query by another field before concluding anything from a zero.
- `rows`, `start` and `sort` paginate. `rows=0` returns only `count` and the facets.

## Facets: the counts of the whole query, for free

`facet.field='["organization", "res_format"]'` (a JSON list as the parameter value) returns in
`result.facets` the counts over the **entire query**, not over the returned page: the cheap way to
answer "which agencies publish this?" without downloading a single dataset. `result.count` is the
query total and the only quotable number; `result.results` is the page. `search_facets` carries
the same facets with their human-readable values.

## "How many datasets does the catalog have" has two answers

`package_list` gave **2.779**; the `count` of `package_search` with an empty query gave **2.718**
(61 unlisted datasets, most likely). State which query produced the number: an unqualified total
is not reproducible.

## `datastore_search`: rows without downloading the file

`datastore_search?resource_id=<id>&limit=1` works on the resources the portal ingested, and is how
to avoid pulling 12 MB for one row. It returns `total`, `fields` and `records`.

- **Every field comes back typed `text`**, numerics included: the caller converts, and decides
  what to do with what does not convert.
- **`total` does not mean the same thing in every family — count the rows yourself.** Measured: it
  came one above the data rows in one family's CSVs (332.071 against 332.070 data rows plus 8
  non-data lines) and **exactly equal** to the data rows in another (2, 56, 108, 1.235 — five
  indicators, five times exact). Read it as a prompt to re-measure, never as the row count.
- **`fields` carries an `_id` column that the CSV does not have.** It is CKAN's own row counter, so
  the file's header is `fields` **minus `_id`**. Compared as-is, the two differ by exactly one
  column and read as "the file changed".
- Only the resources the portal ingested are queryable, not all of them.
- `datastore_search_sql` (server-side aggregation) is a separate action, often disabled: probe it
  with one line before designing on it.

## Resources, and the URLs that move

`package_show?id=<dataset>` → `result.resources[]` with `name`, `url`, `format`, `size`,
`created`, `last_modified`, sometimes `datastore_active`. **The download URL changes whenever the
agency re-uploads the file**: never hard-code it, ask the portal.

One dataset can carry the same content in several formats. When the data is published **also** as
a plain sheet — a survey released as `PDF, RAR, XLS` per year — take the `.xls` resource directly:
there is no need to unpack the `.rar`.

## Sizing a source before committing to it

`fq=organization:<org>&rows=<n>` lists one agency's datasets with their titles and formats; that
plus a `package_show` per dataset is the whole pre-flight. It is how the next reader gets chosen
with a number instead of a taste. And it is how you find out that a family of names — for example
`mides-indicador-<n>`, 1.875 datasets always in the same four formats — is either **one reader or
1.875 tables**, which is exactly what has to be measured before writing it: sample a handful,
compare their column sets, and only then decide. The two halves of that measurement, in order:

1. **Sample wide and cheap through `fields`.** `datastore_search` on one resource per dataset returns
   the column names **without downloading anything**, so fifty datasets cost a minute instead of
   fifty files. It is the only affordable way to find out whether a family shares one shape.
2. **Then validate the proxy on a handful of real downloads.** The datastore holds what CKAN
   understood of the header, not the header. Download ~10 spread across the size range and require
   `fields` minus `_id` to equal the file's first row — otherwise the wide sample measured CKAN's
   reading of the source, not the source.

And a family whose dimension columns are **free-form** (a different set per dataset) is still **one
reader**, provided the *last* columns are fixed and in order: the reader declares that tail once and
nothing else. A column list per dataset is N contracts nobody wrote — write it and the next file
breaks it. Derive the size of the family before trusting its name, too: the agency counts above are
of *datasets*, and that count can include things that are not of the family at all (measured: six
surveys and panels sitting among 1.869 same-shaped indicators), so filter by the name prefix.

**Decode before comparing, or the comparison lies.** These CSVs can come in **cp1252** and be read
as UTF-8 **without raising**: `año` silently becomes `aÃ±o`, and the column-set comparison then
reports a shape change that does not exist. The cheap detector is the check the reader needs anyway
— require the expected **last** column names and reject the file when they do not match, which
catches a real shape change and a wrong encoding in the same test. An encoding read wrong is the
defining hazard of this class in miniature: nothing throws, and every number after it is plausible.
