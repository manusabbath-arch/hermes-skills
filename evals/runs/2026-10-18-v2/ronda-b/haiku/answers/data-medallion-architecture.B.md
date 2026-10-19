## Pedido 1

Supuesto: la pregunta de negocio es algo como "qué productos y clientes mantienen margen si cambian el costo o el precio", y el dashboard muestra varios escenarios de esa misma pregunta. Fijo esa pregunta antes de construir Gold.

**Fuentes y cómo ingesto cada una**

- **API REST de ventas:** ingesta incremental por cursor (`updated_since`), paginada, con reintentos y backoff. Guardo el JSON crudo y la hora de extracción. Cuidado con la paginación que cambia mientras se lee y con respuestas cacheadas que parecen frescas.
- **Postgres (maestro de clientes):** como el maestro es chico, snapshot completo diario desde una réplica, fuera de hora pico. Un incremental no ve los borrados, así que un snapshot evita ese problema.
- **CSV diario por SFTP:** copio el archivo tal cual, con nombre, hora y checksum. Es idempotente por checksum. Valido encoding, separador y que la subida esté completa.

**Capas**

- **Bronze:** crudo, append-only, tal como llegó. Es la fuente de verdad y permite reprocesar.
- **Silver:** dedup por PK, tipos coercionados y NULL para lo que no parsea (con el conteo de NULL por campo). Acá se unen ventas con clientes.
- **Gold:** tabla de ventas por día, producto y cliente, con el margen calculado. Es la que responde la pregunta.
- **Consumo:** DuckDB con `delta_scan` sobre Gold. Cada escenario es la misma query con un parámetro distinto (costo +10%, horizonte, descuento). El dashboard lee Gold, nunca una copia.

**Aceptación:** los totales de Gold cierran contra las fuentes, cada capa tiene su contrato verificado, y la decisión de arquitectura queda registrada en `empirical-project-playbook/templates/infra-decision.md`.

## Pedido 2

No conviene. Bronze es el registro de lo que llegó. Si la limpieza al ingestar tiene un bug, el dato original ya no existe y no hay de dónde reprocesar. Además, la deduplicación en Silver es barata. Lo que ahorrás es poco espacio, y lo que perdés es auditoría y la posibilidad de volver atrás. Si el problema es el costo de almacenamiento, lo resuelvo con retención o compresión de particiones viejas, no eliminando Bronze.

## Pedido 3

Código de referencia con el mismo stack (deltalake, duckdb, pyarrow). Bronze guarda el CSV tal cual, Silver deduplica y tipa, y Gold agrega. Supuse que la PK es `(sku, ts)`; ajustala a la PK real.

```python
import os, tempfile, pyarrow as pa, pyarrow.csv as pacsv, duckdb
from deltalake import write_deltalake, DeltaTable, QueryBuilder

lake = tempfile.mkdtemp()  # en prod: la ruta del lake
bronze, silver, gold = (os.path.join(lake, c) for c in ("bronze", "silver", "gold"))
csv_path = os.path.join(lake, "ventas.csv")
with open(csv_path, "w") as f:  # archivo de ejemplo
    f.write("sku,precio,ts\nA0,55.0,10\nA0,55.0,10\nA1,n/d,11\n")

def leer(path):
    return pa.table(QueryBuilder().register("t", DeltaTable(path)).execute("SELECT * FROM t").read_all())

# BRONZE: CSV tal cual, columnas como string, append-only
cols = {c: pa.string() for c in ("sku", "precio", "ts")}
raw = pacsv.read_csv(csv_path, convert_options=pacsv.ConvertOptions(column_types=cols))
raw = raw.append_column("_archivo", pa.array([os.path.basename(csv_path)] * raw.num_rows))
write_deltalake(bronze, raw, mode="append")

# SILVER: dedup por PK + tipos; lo que no parsea queda NULL, nunca 0
def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
seen = {}
for r in leer(bronze).to_pylist():
    k = (r["sku"], int(r["ts"]))
    seen[k] = {"sku": r["sku"], "precio": to_float(r["precio"]), "ts": int(r["ts"])}
schema = pa.schema([("sku", pa.string()), ("precio", pa.float64()), ("ts", pa.int64())])
write_deltalake(silver, pa.Table.from_pylist(list(seen.values()), schema=schema), mode="overwrite")

# GOLD: agregado de consumo, con NULL contado
con = duckdb.connect()
s = leer(silver)
g = con.execute("SELECT sku, MAX(precio) AS ultimo_precio, COUNT(precio) AS medidos, "
                "COUNT(*) - COUNT(precio) AS nulos FROM s GROUP BY sku ORDER BY sku").to_arrow_table()
write_deltalake(gold, g, mode="overwrite")

final = leer(gold).to_pylist()
assert all(r["ultimo_precio"] is None or r["ultimo_precio"] > 0 for r in final)
assert sum(r["nulos"] for r in final) == 1
print(final)
```

## Pedido 4

Hay dos problemas separados. Bronze es append-only, así que la segunda copia del archivo quedó registrada, y eso es correcto. El error está en que Gold sumó filas duplicadas.

Cómo lo arreglo:

1. **Ingesta idempotente:** calculo el SHA-256 del archivo y lo guardo en una tabla de control. Si el checksum ya existe, no vuelvo a cargar el archivo a Bronze.
2. **Dedup en Silver por la PK real:** así, aunque entre un duplicado, Silver no lo cuenta dos veces. Gold se reconstruye solo desde Silver.
3. **Regla de conflicto:** si el proveedor reenvía una versión corregida con la misma PK, tengo que definir cuál gana (por ejemplo, la de llegada más reciente).
4. **Chequeo de cierre:** el total de Gold tiene que coincidir con la suma calculada sobre el archivo original, no solo "tiene filas".

Después de corregir, recalculo Gold y comparo el total contra el archivo.

## Pedido 5

No. Un 0 se suma como si fuera un precio real y distorsiona los promedios. En Silver el valor "n/d" queda como NULL. Lo que hago es contar los NULL por campo y reportarlos. Las agregaciones de SQL ignoran NULL, así que el promedio se calcula sobre los precios medidos. Además, "n/d" es un defecto que hay que corregir en origen: conviene avisar al proveedor o al responsable de la fuente, con un alerta si el porcentaje de NULL sube.

## Pedido 6

- **CSV:** texto plano, orientado a filas, sin tipos ni esquema (todo llega como string), sin compresión y pesado. Lo lee cualquier herramienta. Sirve para intercambio o para la capa Bronze, tal como llega.
- **Parquet:** binario, columnar, con esquema tipado y comprimido. Ocupa menos espacio y las agregaciones son más rápidas porque lee solo las columnas necesarias. No se puede leer como texto.

Para el intercambio con el proveedor uso CSV. Para las capas del lake uso Parquet, a través de Delta.
