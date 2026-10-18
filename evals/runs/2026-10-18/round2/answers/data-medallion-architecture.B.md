## Pedido 1

Supuestos: las ventas tienen un identificador de transacción, el maestro de clientes cambia poco, y no hay requisito de tiempo real (batch diario o intradiario alcanza).

**Pregunta de negocio primero.** Antes de construir, fijá la pregunta que responde Gold. Ejemplo: "¿Qué ventas y margen tendríamos por cliente/producto si el precio o el volumen cambian X%?". Los escenarios son esa misma pregunta con parámetros distintos, no queries sueltas.

**Arquitectura medallion (Delta + DuckDB + PyArrow):**

- **Ingesta a Bronze, distinta por fuente:**
  - API REST: incremental por cursor o `updated_since`, paginada, con reintentos con backoff. Guardás el JSON crudo y la hora de extracción. Cuidado con paginación que cambia mientras leés y con respuestas cacheadas que parecen frescas.
  - Postgres: snapshot completo del maestro (es chico), leído desde réplica. Si crece, incremental por `updated_at`. Ojo con los borrados, que un incremental no ve.
  - CSV por SFTP: copiás el archivo tal cual, con nombre, fecha y checksum. Es idempotente por checksum, así que un reenvío no duplica. Declarás encoding y separador, y descartás archivos a medio subir.
- **Bronze:** append-only, crudo, sin limpiar ni deduplicar. Una fila por evento recibido. Con el time-travel de Delta podés reproducir qué había cuando se calculó un número.
- **Silver:** dedup por clave, tipos coercionados, join de ventas con clientes. Lo que no parsea queda NULL, nunca 0. Contás los NULL por campo y los reportás.
- **Gold:** agregado por día, cliente y producto, que responde la pregunta. Se valida antes de darlo por bueno: rangos y signos plausibles, todas las particiones con filas, y un total que cierre contra una fuente independiente.
- **Consumo:** el dashboard consulta con DuckDB la misma tabla Gold que escribe el pipeline. Nada de copias que se desfasen.

**Escenarios:** cada uno es la query Gold parametrizada (por ejemplo variación de precio, descuento o horizonte). Un selector en el dashboard cambia el parámetro. Mostrás siempre el n real por escenario, no una muestra, y marcás el punto de operación real.

**Verificación:** cambiar un parámetro tiene que mover la salida como se espera. Revisá también que ningún escenario sea inalcanzable por cota. Dejá registrada la decisión de fuentes con criterios (freshness, costo, disponibilidad).

## Pedido 2

Mi recomendación es que no te saltees Bronze. Sí podés (y debés) limpiar y deduplicar, pero en Silver, no al ingestar.

La razón es práctica. Si limpiás al entrar y la lógica tiene un bug (un dedup que descarta filas válidas, un parseo que convierte mal un formato, una regla que cambia después), el dato original ya no existe. No tenés de dónde reprocesar y no podés auditar qué llegó realmente. Con Bronze append-only, si Silver o Gold se rompen, corregís la transformación y recalculás desde el crudo. Además, con el historial de Delta podés reproducir exactamente qué datos había cuando se calculó un número.

Lo que te ahorrás de verdad es poco: Bronze es solo escribir lo recibido, sin lógica, así que casi no cuesta cómputo. El costo es almacenamiento, que en un lake con archivos Parquet/Delta es barato.

Si el espacio te preocupa, hay alternativas sin perder la auditoría:

- Retención: conservá Bronze X meses y archivá o comprimí lo viejo.
- Particioná por fecha de ingesta y compactá archivos chicos.
- Para el CSV de SFTP, Bronze puede ser el archivo original más un registro con checksum.

Resumen: una sola pasada de ingesta está bien, pero con dos escrituras: primero lo crudo a Bronze, después la limpieza a Silver. Ahí está tu seguro contra errores de limpieza.

## Pedido 3

Supuestos: el CSV tiene columnas `id_venta, sku, cliente_id, monto, fecha`; el separador es coma; el path es `ventas.csv`. Stack: `deltalake` + `duckdb` + `pyarrow` (`pip install deltalake duckdb pyarrow`).

```python
import os, hashlib, datetime as dt
import pyarrow as pa, pyarrow.csv as pacsv, duckdb
from deltalake import write_deltalake, DeltaTable, QueryBuilder

LAKE = "./lake"
BRONZE, SILVER, GOLD = (os.path.join(LAKE, c) for c in ("bronze", "silver", "gold"))
CSV = "ventas.csv"

def leer(path):
    return pa.table(QueryBuilder().register("t", DeltaTable(path)).execute("SELECT * FROM t").read_all())

# ---------- BRONZE: crudo, todo string, append-only, idempotente por checksum ----------
with open(CSV, "rb") as f:
    checksum = hashlib.sha256(f.read()).hexdigest()

ya_cargado = False
if os.path.exists(BRONZE):
    ya_cargado = checksum in leer(BRONZE).column("_checksum").to_pylist()

if not ya_cargado:
    # todas las columnas como string: no se interpreta nada en Bronze
    tbl = pacsv.read_csv(CSV, convert_options=pacsv.ConvertOptions(
        column_types={c: pa.string() for c in
                      ("id_venta", "sku", "cliente_id", "monto", "fecha")}))
    n = tbl.num_rows
    tbl = (tbl.append_column("_checksum", pa.array([checksum] * n))
              .append_column("_archivo", pa.array([os.path.basename(CSV)] * n))
              .append_column("_ingesta_ts", pa.array([dt.datetime.utcnow().isoformat()] * n)))
    write_deltalake(BRONZE, tbl, mode="append")

# ---------- SILVER: dedup por PK, tipos; lo que no parsea queda NULL (nunca 0) ----------
def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def to_date(v):
    try:
        return dt.date.fromisoformat(v)
    except (TypeError, ValueError):
        return None

vistos = {}
for r in leer(BRONZE).to_pylist():            # el último ingestado gana
    vistos[r["id_venta"]] = {
        "id_venta": r["id_venta"], "sku": r["sku"], "cliente_id": r["cliente_id"],
        "monto": to_float(r["monto"]), "fecha": to_date(r["fecha"]),
    }
schema = pa.schema([("id_venta", pa.string()), ("sku", pa.string()),
                    ("cliente_id", pa.string()), ("monto", pa.float64()),
                    ("fecha", pa.date32())])
write_deltalake(SILVER, pa.Table.from_pylist(list(vistos.values()), schema=schema),
                mode="overwrite")

# reporte de NULL por campo
s = leer(SILVER)
for c in s.column_names:
    print(f"NULL en {c}: {s.column(c).null_count}")

# ---------- GOLD: ventas por día y SKU ----------
con = duckdb.connect()
g = con.execute("""
    SELECT fecha, sku,
           SUM(monto)   AS ventas,
           COUNT(monto) AS ventas_medidas,
           COUNT(*) - COUNT(monto) AS monto_nulo
    FROM s
    WHERE fecha IS NOT NULL
    GROUP BY fecha, sku
    ORDER BY fecha, sku
""").to_arrow_table()   # to_arrow_table(), no .arrow()
write_deltalake(GOLD, g, mode="overwrite")

# ---------- Verificación de Gold (presence != utility) ----------
final = leer(GOLD).to_pylist()
assert final, "Gold vacía"
assert all(r["ventas"] is None or r["ventas"] >= 0 for r in final), "montos negativos"
total_gold = sum(r["ventas"] or 0 for r in final)
total_silver = sum(v["monto"] or 0 for v in vistos.values() if v["fecha"])
assert abs(total_gold - total_silver) < 1e-6, "Gold no cierra contra Silver"
print(final[:5])
```

Notas:

- Bronze guarda todo como texto con checksum, archivo y timestamp. Cargar el mismo CSV dos veces no duplica.
- Silver deduplica por `id_venta` y deja NULL lo que no parsea. El reporte de NULL te dice cuánto dato falta.
- Gold agrega por día y SKU. Los asserts validan signos y que el total cierre contra Silver. Para una verificación más fuerte, cerralo también contra el total del CSV original, que es la fuente independiente.
- Para el dashboard, consultá esa tabla Gold con DuckDB y parametrizá los escenarios sobre la misma query.
