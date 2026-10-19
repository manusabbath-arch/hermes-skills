## Pedido 1

Supuestos: la pregunta de negocio la fijás vos antes de construir (ej. "¿qué productos/clientes sostienen margen > x si el costo sube 10%?"); usamos Delta + DuckDB + PyArrow.

**Arquitectura: Fuente → Bronze → Silver → Gold → Dashboard**

**Ingesta a Bronze (cada fuente distinta):**
- **API REST (ventas):** incremental por cursor o `updated_since`, paginada, reintentos con backoff. Guardás el payload JSON crudo y la hora de extracción. Cuidado con paginación que cambia mientras leés, rate limit y respuestas cacheadas que parecen frescas.
- **Postgres (maestro de clientes):** snapshot completo si es chico (lo más probable para un maestro), desde réplica y fuera de hora pico. Si crece, incremental por `updated_at` o CDC. Ojo: un incremental no ve borrados.
- **CSV por SFTP:** copiás el archivo tal cual, con nombre, hora y checksum. Ingesta idempotente por checksum. Declarás encoding y separador.

**Bronze:** append-only, crudo, sin limpiar ni deduplicar. Es tu auditoría y tu punto de reproceso (time-travel de Delta).

**Silver:** dedup por PK, tipos coercionados, lo que no parsea queda NULL (nunca 0), con conteo de NULL por campo. Acá se une ventas con clientes. Las tres fuentes convergen en un modelo común.

**Gold:** agregado a la dimensión de corte (producto/día/cliente) que responde la pregunta. Se valida antes de usarla: rangos y signos plausibles, todas las particiones con filas y un total que cierre contra una fuente independiente (ej. total de ventas del sistema fuente).

**Escenarios y dashboard:** un escenario es la misma query Gold con otro parámetro (aumento de costo, horizonte, descuento), no queries sueltas. El dashboard ejecuta esa query parametrizada con DuckDB (`delta_scan` sobre Gold), nunca sobre una copia que derive. Mostrá n real por escenario, no un sample.

Dejá registrada la decisión de fuentes en un documento de decisión de infraestructura, con criterios (freshness, cuota, costo) definidos antes de ver los datos.

## Pedido 2

No te lo recomiendo: Bronze es justamente lo que no te conviene ahorrar.

Bronze guarda el dato tal como llegó, append-only, sin limpiar ni deduplicar. Si limpiás al ingestar y la lógica de limpieza tiene un bug (y alguna vez lo va a tener), el dato original ya no existe y no hay de dónde reprocesar. Con Bronze, corregís la regla y recalculás Silver y Gold. Además te da auditoría: con el time-travel de Delta podés reproducir qué crudo había cuando se calculó un número.

El costo de Bronze es almacenamiento barato; el costo de no tenerla es perder datos de forma irrecuperable.

Lo que sí podés hacer es mantener la ingesta lo más simple posible: escribir el crudo a Delta con `mode="append"` y dejar toda la limpieza (dedup por PK, coerción de tipos, NULL en lo que no parsea) en Silver. Cada capa hace solo lo suyo.

## Pedido 3

Supuesto: columnas `sku`, `precio`, `ts` (PK = sku + ts). Instalá con `pip install deltalake duckdb pyarrow`.

```python
import os, csv, tempfile, pyarrow as pa, duckdb
from deltalake import write_deltalake, DeltaTable, QueryBuilder

lake = tempfile.mkdtemp()   # en prod: la ruta real del lake
bronze, silver, gold = (os.path.join(lake, c) for c in ("bronze", "silver", "gold"))

def leer(path):
    return pa.table(QueryBuilder().register("t", DeltaTable(path)).execute("SELECT * FROM t").read_all())

# BRONZE: crudo tal cual, todo como string, append-only (con duplicados y basura)
with open("ventas.csv", newline="", encoding="utf-8") as f:
    raw = list(csv.DictReader(f))
write_deltalake(bronze, pa.Table.from_pylist(raw), mode="append")

# SILVER: dedup por PK + tipos; lo que no parsea queda NULL, nunca 0
def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

seen = {}
for r in leer(bronze).to_pylist():
    seen[(r["sku"], r["ts"])] = {"sku": r["sku"], "precio": to_float(r["precio"]), "ts": int(r["ts"])}
schema = pa.schema([("sku", pa.string()), ("precio", pa.float64()), ("ts", pa.int64())])
write_deltalake(silver, pa.Table.from_pylist(list(seen.values()), schema=schema), mode="overwrite")

# GOLD: agregado de consumo
con = duckdb.connect()
s = leer(silver)
g = con.execute("SELECT sku, MAX(precio) AS ultimo_precio, COUNT(precio) AS medidos "
                "FROM s GROUP BY sku ORDER BY sku").to_arrow_table()
# to_arrow_table(), no .arrow(): en duckdb 1.5 .arrow() devuelve un stream y cuelga el proceso
write_deltalake(gold, g, mode="overwrite")

# Verificación de Gold: plausible y con los NULL contados, no solo "hay filas"
final = leer(gold).to_pylist()
assert all(r["ultimo_precio"] is None or r["ultimo_precio"] > 0 for r in final)
print(final)
```

Notas: Bronze nunca limpia; Silver cuenta los NULL por campo y los reporta; y en Gold conviene además cuadrar el total contra una fuente independiente. Para el CSV real, declará encoding y separador.

## Pedido 4

Causa: Bronze, al ser append-only, registró el archivo dos veces, y la deduplicación no se aplicó donde correspondía, así que Gold sumó doble.

**Arreglo en tres puntos:**

1. **Ingesta idempotente por checksum.** Al copiar el CSV desde SFTP a Bronze, guardá nombre, hora y checksum (ej. SHA-256). Si el checksum ya está registrado, no lo volvés a ingestar. Así el mismo archivo reenviado no duplica.
2. **Dedup por PK en Silver.** Aunque entre algo repetido, Silver deduplica por la clave de negocio (ej. sku + ts, o id de venta). Eso protege también contra reenvíos con otro nombre o contra solapamientos parciales entre archivos.
3. **Reprocesar.** No toques Bronze para borrar: reconstruí Silver desde Bronze (con la dedup activa) y regenerá Gold. Esa es justamente la utilidad de tener Bronze crudo.

**Verificación:** el total de Gold tiene que cerrar contra una fuente independiente (ej. el total que declara el proveedor o el sistema origen). Agregá además un chequeo que alerte si un mismo checksum aparece dos veces en Bronze o si hay PK repetidas en Silver.

Supuesto: existe una clave de negocio confiable; si no, definila con el proveedor antes de ingestar.

## Pedido 5

No. Ponerlo en 0 es peor que el problema que querés evitar.

Un 0 inventado se suma como dato real: baja tus promedios y los hace engañosos, y después nadie distingue un precio "no disponible" de un precio legítimamente cero. La regla es NULL ≠ 0: NULL significa "no medido" (un defecto a corregir), 0 significa "medido y es cero".

**Qué hacer en Silver:**
- Convertí 'n/d' a **NULL** (coerción de tipo con `try/except` que devuelve `None`).
- Contá los NULL por campo y reportalos (ej. "12 de 1.000 precios n/d").

**Sobre los promedios:** no se rompen. `AVG` y `COUNT(precio)` en SQL ignoran los NULL, así que el promedio se calcula sobre los precios efectivamente medidos. Conviene mostrar también cuántos se midieron (`COUNT(precio)`) junto al promedio, para que se vea sobre qué base se calculó.

Bronze conserva el 'n/d' original, por lo que siempre podés auditarlo o cambiar la regla más adelante.

## Pedido 6

**CSV:** archivo de texto plano, por filas. Legible a simple vista y universal, pero sin tipos (todo es texto, hay que inferirlos o coercionarlos), sin esquema declarado, con problemas típicos de encoding y separador, y más pesado y lento de leer.

**Parquet:** formato binario, columnar y comprimido. Guarda el esquema y los tipos, comprime bien y permite leer solo las columnas que necesitás, lo que lo hace mucho más rápido y chico para análisis. No se lee a ojo: necesitás una herramienta.

**En la práctica:** el CSV es típico como formato de entrada de un proveedor (por eso en Bronze lo guardás tal cual), y Parquet es mejor para almacenar y consultar. Delta Lake, de hecho, usa Parquet por debajo.
