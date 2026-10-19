## Pedido 1

Supuestos: la pregunta de negocio la fijamos antes de construir, por ejemplo "¿cuánto cambian ingresos y margen por cliente/segmento si varía el descuento, el volumen o el mix?". Si es otra, solo cambia la capa Gold.

**Fuentes y elección:** las tres entran (API REST de ventas, Postgres de clientes, CSV diario por SFTP). Antes de construir, comparalas con números (freshness, latencia, cuota, disponibilidad, si la API devuelve datos cacheados en silencio) y dejá la decisión registrada.

**Arquitectura medallion (stack: deltalake + duckdb + pyarrow):**

- **Bronze (crudo, append-only):** una tabla Delta por fuente (`bronze/ventas_api`, `bronze/clientes_pg`, `bronze/ventas_csv`). Se guarda tal como llega, con duplicados y basura, más metadatos (fecha de ingesta, archivo/endpoint de origen). Nada se limpia ni se deduplica. Es tu auditoría y tu punto de reproceso.
- **Silver (limpia):** dedup por clave primaria (por ejemplo `id_venta`), tipos coercionados, unificación de las dos fuentes de ventas y join con clientes. Los valores que no parsean quedan en NULL, nunca en 0 (NULL = defecto, 0 = medido legítimo). Todo sentinel se documenta.
- **Gold (agregada, lista para el dashboard):** agregado por la dimensión de corte (día, cliente/segmento, producto) con las métricas base.

**Escenarios:** un escenario es la MISMA query Gold con otro parámetro (descuento 5% vs 10%, volumen +/-x%), no consultas sueltas. Se ejecutan con DuckDB sobre Gold (`delta_scan`) parametrizadas.

**Dashboard:** lee directamente de Gold, sin copias que se desincronicen. Mostrá el n real por escenario y marcá el punto de operación real, no una muestra de juguete.

**Verificación:** contrato de datos por capa (Bronze "recibí el evento", Silver "dedup + tipo", Gold "responde la pregunta"), y comprobar que al cambiar un parámetro la salida cambia como se espera.

## Pedido 2

No te lo recomiendo: Bronze no es opcional, y saltearla te cuesta más de lo que ahorra.

Bronze es la copia cruda y append-only de lo que llegó, sin limpiar ni deduplicar. Su valor es justamente ese: es la fuente de verdad y la capa de auditoría y reproceso. Si limpiás al ingestar y después descubrís que tu regla de dedup o de parseo estaba mal (por ejemplo, descartaba filas válidas o convertía un "n/d" en 0), el dato original ya no existe y no podés reconstruir Silver ni Gold. Además perdés trazabilidad: no podés demostrar qué mandó la fuente.

Lo que sí es cierto es que no necesitás que Bronze sea cara o compleja. Es una tabla Delta en modo append, sin transformaciones. El costo es almacenamiento barato y unas pocas líneas de código.

Cada capa hace solo lo suyo:
- Bronze: recibir y guardar tal cual.
- Silver: dedup por PK, tipos, manejo declarado de NULL.
- Gold: agregar para responder la pregunta de negocio.

Si lo que te preocupa es el volumen, atacalo con retención o compactación de Bronze, no eliminándola. Si te preocupa la latencia, Silver puede calcularse de forma incremental sobre lo nuevo de Bronze. Mezclar limpieza con ingesta te deja con un solo pipeline ad-hoc imposible de auditar.

## Pedido 3

Supuestos: el CSV tiene columnas `id_venta`, `cliente`, `monto`, `fecha`; el archivo se llama `ventas.csv`; instalás con `pip install deltalake duckdb pyarrow` (en un venv). Hay duplicados y montos que no parsean.

```python
import os, csv, duckdb, pyarrow as pa
from deltalake import write_deltalake, DeltaTable, QueryBuilder

LAKE = "./lake"
bronze, silver, gold = (os.path.join(LAKE, c) for c in ("bronze", "silver", "gold"))

def leer(path):
    return pa.table(QueryBuilder().register("t", DeltaTable(path)).execute("SELECT * FROM t").read_all())

# BRONZE: crudo, tal cual llegó (todo string), append-only. Sin limpiar ni deduplicar.
with open("ventas.csv", newline="", encoding="utf-8") as f:
    filas = list(csv.DictReader(f))
for i, r in enumerate(filas):
    r["_archivo"] = "ventas.csv"
    r["_fila"] = str(i)
write_deltalake(bronze, pa.Table.from_pylist(filas), mode="append")

# SILVER: dedup por PK + tipos. Lo que no parsea queda NULL, nunca 0.
def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

vistos = {}
for r in leer(bronze).to_pylist():
    vistos[r["id_venta"]] = {
        "id_venta": r["id_venta"],
        "cliente": r["cliente"],
        "monto": to_float(r["monto"]),
        "fecha": r["fecha"],
    }
schema = pa.schema([("id_venta", pa.string()), ("cliente", pa.string()),
                    ("monto", pa.float64()), ("fecha", pa.string())])
write_deltalake(silver, pa.Table.from_pylist(list(vistos.values()), schema=schema), mode="overwrite")

# GOLD: agregado por cliente (la pregunta de negocio)
con = duckdb.connect()
s = leer(silver)
g = con.execute("""
    SELECT cliente,
           SUM(monto)  AS ingresos,
           COUNT(monto) AS ventas_medidas,
           COUNT(*) - COUNT(monto) AS ventas_sin_monto
    FROM s GROUP BY cliente ORDER BY cliente
""").to_arrow_table()   # to_arrow_table(), no .arrow(): evita que el proceso quede colgado
write_deltalake(gold, g, mode="overwrite")

print(leer(gold).to_pylist())
```

Notas:
- Bronze se reejecuta en append: si corrés dos veces el mismo archivo habrá duplicados en Bronze (es lo esperado); Silver los resuelve por `id_venta`.
- Si la misma venta puede llegar con valores distintos, el dedup actual se queda con la última leída. Si necesitás otro criterio (por ejemplo la `fecha` más reciente), cambiá esa regla en Silver, no en Bronze.
- Los montos inválidos quedan NULL y Gold los cuenta aparte en `ventas_sin_monto`, así el defecto no se silencia.
- Para escenarios, parametrizá la query de Gold (por ejemplo un descuento) con DuckDB sobre la misma tabla Gold.
