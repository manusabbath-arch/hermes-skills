## Pedido 1

Propongo una arquitectura medallion (Bronze → Silver → Gold → dashboard) sobre tablas Delta, con DuckDB para consultar. Cada capa cumple un solo rol.

**Ingesta a Bronze (cruda, solo se agrega, nunca se modifica). Cada fuente se ingesta a su manera:**
- **API de ventas:** lectura incremental por cursor o `updated_since`, paginada y con reintentos con backoff. Guardo el JSON crudo y la hora de extracción. Hay que vigilar el rate limit y las respuestas cacheadas que parecen frescas.
- **Postgres (maestro de clientes):** si la tabla es chica, snapshot completo; si es grande, incremental por `updated_at` o CDC. Siempre desde una réplica o fuera de hora pico. Ojo con los borrados, porque un incremental no los ve.
- **CSV por SFTP:** copio el archivo tal cual, con su nombre, la hora y un checksum. La ingesta es idempotente por checksum. Antes de leerlo valido que el archivo esté completo, el encoding y el separador.

**Silver:** deduplico por PK (`id_venta`, `id_cliente`), convierto los tipos y dejo en NULL lo que no parsea, nunca 0. Cuento los NULL por campo.

**Gold:** antes de construir fijo la pregunta de negocio. Supuesto: "¿qué margen tiene cada producto o segmento de clientes si el costo sube X% o el descuento cambia Y%?". La agregación es ventas × clientes por producto, día y segmento.

**Escenarios y dashboard:** cada escenario es la misma consulta sobre Gold con otro parámetro (por ejemplo conservador +5% de costo, pesimista +15%), no una consulta suelta distinta. El dashboard lee Gold directo con `delta_scan` de DuckDB, sin copias que se desincronicen. Muestra n por escenario sobre el volumen real de datos.

**Verificación:** antes de dar Gold por buena compruebo que los valores sean plausibles, que cada partición tenga filas y que el total cierre contra una fuente independiente (por ejemplo el total que reporta la API). Que la tabla tenga filas no alcanza. También dejaría por escrito los criterios con los que se eligió cada fuente.

## Pedido 2

No. Bronze es justamente la capa que te salva cuando la limpieza falla. Si limpiás y deduplicás al ingestar y la lógica tiene un bug (una clave de dedup mal elegida, un parseo que descarta filas válidas), el dato original ya no existe y no hay desde dónde reprocesar.

Con Bronze guardás el dato tal como llegó, sin modificarlo, y solo agregás filas. Si Silver o Gold se rompen, los regenerás desde ahí. Con el historial de Delta (time-travel) podés además ver exactamente qué datos crudos había cuando se calculó un número, lo que sirve para auditar.

El costo es poco: algo de almacenamiento y un paso más. La limpieza y el dedup van en Silver, que es para lo que existe esa capa.

## Pedido 3

Supuesto: el CSV tiene las columnas `id_venta, fecha, sku, cantidad, precio`. Stack: `pip install deltalake duckdb pyarrow` (en un venv).

```python
import hashlib, os, datetime as dt
import pyarrow as pa, pyarrow.csv as pcsv, duckdb
from deltalake import write_deltalake, DeltaTable, QueryBuilder

LAKE = "/data/lake"
BRONZE, SILVER, GOLD = (os.path.join(LAKE, n) for n in ("bronze_ventas", "silver_ventas", "gold_ventas_dia"))

def existe(p): return os.path.isdir(os.path.join(p, "_delta_log"))
def leer(p):
    return pa.table(QueryBuilder().register("t", DeltaTable(p)).execute("SELECT * FROM t").read_all())

# BRONZE: tal cual llegó (todo string), append-only, idempotente por checksum
def ingestar(csv_path):
    sha = hashlib.sha256(open(csv_path, "rb").read()).hexdigest()
    if existe(BRONZE) and sha in set(leer(BRONZE).column("_checksum").to_pylist()):
        return print("archivo ya ingestado:", csv_path)
    cols = pcsv.read_csv(csv_path).column_names
    t = pcsv.read_csv(csv_path, convert_options=pcsv.ConvertOptions(
        column_types={c: pa.string() for c in cols}))
    n = t.num_rows
    t = (t.append_column("_archivo", pa.array([os.path.basename(csv_path)] * n))
          .append_column("_checksum", pa.array([sha] * n))
          .append_column("_ingestado_en", pa.array([dt.datetime.now(dt.timezone.utc)] * n)))
    write_deltalake(BRONZE, t, mode="append")

con = duckdb.connect()

# SILVER: dedup por PK (última ingesta gana), tipos; lo que no parsea queda NULL
def silver():
    b = leer(BRONZE)
    s = con.execute("""
        SELECT id_venta, TRY_CAST(fecha AS DATE) AS fecha, sku,
               TRY_CAST(cantidad AS BIGINT) AS cantidad, TRY_CAST(precio AS DOUBLE) AS precio
        FROM b
        QUALIFY ROW_NUMBER() OVER (PARTITION BY id_venta ORDER BY _ingestado_en DESC) = 1
    """).to_arrow_table()          # to_arrow_table(), no .arrow() (en duckdb 1.5 devuelve un stream)
    print(con.execute("SELECT COUNT(*) - COUNT(precio) FROM s").fetchone()[0], "precios NULL")
    write_deltalake(SILVER, s, mode="overwrite")

# GOLD: ventas por día y SKU, con el NULL contado
def gold():
    s = leer(SILVER)
    g = con.execute("""
        SELECT fecha, sku, SUM(cantidad * precio) AS venta, COUNT(*) AS filas, COUNT(precio) AS medidos
        FROM s GROUP BY fecha, sku ORDER BY fecha, sku
    """).to_arrow_table()
    rows = g.to_pylist()
    assert rows and all(r["venta"] is None or r["venta"] >= 0 for r in rows)
    write_deltalake(GOLD, g, mode="overwrite")

ingestar("ventas_2026-10-18.csv"); silver(); gold()
```

Faltaría cerrar el total de Gold contra una fuente independiente, por ejemplo el total de control del proveedor. Los tests irían herméticos, con `tmp_path`, nunca contra archivos reales.

## Pedido 4

Hay que atacarlo en dos capas:

1. **Bronze idempotente por checksum.** Al recibir un archivo por SFTP calculás su sha256 y lo registrás junto al nombre y la hora (columna `_checksum`). Si el checksum ya existe, no lo agregás. Así el reenvío del mismo archivo no duplica nada.
2. **Silver deduplica por PK de negocio** (por ejemplo `id_venta`, quedándote con la última ingesta). Esto también cubre el caso de un archivo con otro nombre o checksum que repite ventas, cosa que el checksum solo no detecta.

**Para arreglar lo que ya pasó:** no borres nada de Bronze, que solo se agrega y sirve de auditoría. Con las columnas `_archivo` y `_checksum` (o con el historial de Delta) identificás la ingesta duplicada, regenerás Silver con el dedup y después Gold.

**Para que no vuelva a pasar sin que nadie lo note:** a Gold le agregás una verificación de que el total cierre contra una fuente independiente (el total de control del proveedor o el de la API). Si eso hubiera estado, la duplicación se habría detectado antes de llegar al dashboard.

## Pedido 5

No. Un 0 inventado se suma y se promedia como si fuera un precio real, así que te baja los promedios en silencio y además esconde que el dato falta.

En Silver, `'n/d'` tiene que quedar como **NULL**: NULL significa "no medido" y 0 significa "medido, y vale cero". Las funciones de agregación (`AVG`, `SUM`, `COUNT(precio)`) ya ignoran los NULL, así que no te rompen los promedios. Lo que sí tenés que hacer:

- Contar los NULL por campo y reportarlos (por ejemplo, en Gold, `COUNT(precio) AS medidos` al lado de `COUNT(*)`).
- Tratar esos NULL como un defecto a corregir en la fuente, no como un valor válido.

En Bronze el `'n/d'` queda tal como llegó, así que si después conseguís el precio real podés reprocesar.

## Pedido 6

- **CSV:** texto plano, se lee fila por fila y no tiene tipos (todo es string hasta que lo parseás). No declara encoding ni separador y pesa más. Su ventaja es que cualquier herramienta lo abre.
- **Parquet:** binario y columnar, con el esquema y los tipos guardados en el archivo y compresión por columna. Es mucho más chico y rápido para análisis, porque lee solo las columnas que necesitás. No se abre a mano.

En la práctica, CSV sirve para intercambiar datos (por ejemplo lo que llega por SFTP) y Parquet para guardar y analizar. Las tablas Delta, de hecho, guardan Parquet por debajo.
