## Pedido 1

Propongo una arquitectura medallón (Bronze, Silver, Gold) sobre un lakehouse. Supuestos: volumen moderado (millones de filas, no miles de millones), nube genérica, y el dashboard de escenarios necesita recalcular agregados con parámetros (precio, descuento, volumen).

**Ingesta (Bronze, crudo e inmutable)**
- API REST de ventas: extracción incremental por fecha de modificación o cursor, guardando la respuesta JSON tal cual, con metadatos (`_ingested_at`, `_source`, `_batch_id`, `_request_params`).
- Postgres (maestro de clientes): CDC (por ejemplo Debezium) o snapshot incremental por `updated_at`. Se guarda cada captura sin tocar.
- CSV por SFTP: se copia el archivo original a una zona de aterrizaje y se registra su nombre, hash y fecha. Se carga a Bronze sin transformar (todo como string si hace falta).

**Silver (limpio y conforme)**
- Tipado, normalización de fechas y monedas, tratamiento de nulos explícito (no inventar valores), deduplicación por clave de negocio y MERGE idempotente.
- Unificación de ventas de API y CSV en un esquema común; clientes como dimensión con historia (SCD2) si importa el cambio en el tiempo.
- Reglas de calidad con cuarentena para filas inválidas, en lugar de descartarlas.

**Gold (consumo)**
- Modelo dimensional: `fact_ventas`, `dim_cliente`, `dim_producto`, `dim_fecha`.
- Tablas agregadas por grano del dashboard y una tabla de parámetros de escenarios (supuestos base/optimista/pesimista), de modo que los escenarios se calculan sobre Gold sin mutar los datos.

**Transversal**: formato Parquet con Delta o Iceberg, orquestación con Airflow o Dagster, transformaciones con dbt o Spark, catálogo y linaje, y alertas de frescura y volumen.

## Pedido 2

Técnicamente podés, pero no te lo recomiendo. Bronze es barata (almacenamiento) y te da cosas que no recuperás después:

- **Reproceso**: si descubrís un bug en la limpieza o cambian las reglas, reconstruís Silver desde Bronze. Sin Bronze, tendrías que volver a pedirle los datos al origen, y la API o el SFTP quizá ya no los tengan.
- **Auditoría y depuración**: podés demostrar qué llegó exactamente y cuándo.
- **Desacople**: la ingesta no falla porque una regla de limpieza cambió.
- **Deduplicar al ingestar es destructivo**: si tu criterio de duplicado era incorrecto, perdiste información sin posibilidad de volver atrás.

Si lo que te preocupa es el costo o la complejidad, hay opciones intermedias: Bronze con retención corta (30 a 90 días), compresión en Parquet, o una Bronze mínima que sea solo el archivo crudo en almacenamiento de objetos más una tabla de metadatos. Esa versión mínima sigue cumpliendo la función y casi no cuesta.

## Pedido 3

Supuesto: stack PySpark con Delta Lake (Parquet por debajo), ejecutable localmente o en Databricks. Columnas del CSV: `sale_id, customer_id, product_id, sale_date, quantity, price`.

```python
from pyspark.sql import SparkSession, functions as F
from delta.tables import DeltaTable

spark = SparkSession.builder.getOrCreate()
SRC = "/data/landing/ventas.csv"
BRONZE, SILVER, GOLD = "/lake/bronze/ventas", "/lake/silver/ventas", "/lake/gold/ventas_diarias"

# BRONZE: crudo, todo string, con metadatos
raw = (spark.read.option("header", True).option("inferSchema", False).csv(SRC)
       .withColumn("_source_file", F.input_file_name())
       .withColumn("_ingested_at", F.current_timestamp())
       .withColumn("_row_hash", F.sha2(F.concat_ws("||", *[F.col(c) for c in
                   ["sale_id","customer_id","product_id","sale_date","quantity","price"]]), 256)))
raw.write.format("delta").mode("append").save(BRONZE)

# SILVER: tipado, calidad, dedup, MERGE idempotente
b = spark.read.format("delta").load(BRONZE)
typed = (b.select(
    F.col("sale_id"), F.col("customer_id"), F.col("product_id"),
    F.to_date("sale_date").alias("sale_date"),
    F.col("quantity").cast("int").alias("quantity"),
    F.when(F.lower(F.trim("price")).isin("n/d", "", "null"), None)
     .otherwise(F.col("price").cast("decimal(18,2)")).alias("price"),
    "_ingested_at"))
valid = typed.filter("sale_id is not null and sale_date is not null and quantity > 0")
rejected = typed.subtract(valid)
rejected.write.format("delta").mode("append").save("/lake/silver/_cuarentena")

from pyspark.sql.window import Window
w = Window.partitionBy("sale_id").orderBy(F.col("_ingested_at").desc())
dedup = valid.withColumn("rn", F.row_number().over(w)).filter("rn=1").drop("rn")

if DeltaTable.isDeltaTable(spark, SILVER):
    (DeltaTable.forPath(spark, SILVER).alias("t")
     .merge(dedup.alias("s"), "t.sale_id = s.sale_id")
     .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())
else:
    dedup.write.format("delta").save(SILVER)

# GOLD: agregado de negocio
s = spark.read.format("delta").load(SILVER)
gold = (s.groupBy("sale_date", "product_id")
          .agg(F.sum("quantity").alias("unidades"),
               F.sum(F.col("quantity") * F.col("price")).alias("ingresos"),
               F.avg("price").alias("precio_medio")))
gold.write.format("delta").mode("overwrite").save(GOLD)
```

Notas: Gold se recalcula desde Silver, así que es idempotente. Para volúmenes grandes conviene reemplazar solo las particiones afectadas.

## Pedido 4

La causa es que la carga no es idempotente: el mismo archivo entró dos veces y se sumó dos veces. Se arregla en tres niveles:

1. **Detectar archivos repetidos en Bronze**: calculá el hash del archivo (SHA-256) y registralo en una tabla de control (`nombre, hash, filas, fecha_carga`). Si el hash ya existe, se omite la carga (o se registra como duplicado). El nombre solo no alcanza, porque el proveedor puede renombrarlo.
2. **Deduplicar en Silver por clave de negocio** (`sale_id` o la combinación que identifique una venta) y escribir con `MERGE`/upsert en lugar de `append`. Así, aunque Bronze tenga las filas dos veces, Silver queda con una.
3. **Gold recalculado desde Silver** (o con overwrite por partición), nunca acumulando incrementos sobre Gold.

**Para corregir lo ya duplicado**: Bronze conserva ambas cargas, así que no hay que pedirle nada al proveedor. Marcás la carga duplicada (por `_batch_id`), reconstruís Silver con el dedup y recalculás Gold. Si usás Delta, también podés hacer `RESTORE` a una versión anterior.

Agregá además un control de calidad: conteo de filas y suma de importes por archivo contra Silver y Gold, con alerta si divergen. Si no hay una clave de negocio confiable, usá un hash de la fila completa.

## Pedido 5

No, no lo pongas en 0. Un 0 es un valor real y falso: baja los promedios, distorsiona los mínimos y los márgenes, y es indistinguible de un precio genuinamente cero (promociones, muestras).

Lo correcto en Silver:
- Convertir `'n/d'` a **NULL** (tipo numérico), porque significa "dato no disponible".
- Agregar una columna de calidad, por ejemplo `price_is_missing` (booleana) o `dq_flag`, para poder auditar cuántos casos hay.
- Mantener el valor original en Bronze, que ya lo tiene.

Los promedios no se rompen: `AVG` y `SUM` en SQL y Spark ignoran los NULL, así que el promedio se calcula sobre los registros con precio. Lo que sí tenés que cuidar son los cálculos como `quantity * price`, que dan NULL; eso es correcto, porque el ingreso de esa fila es desconocido.

Si el negocio necesita un valor para esas filas, imputalo en **Gold** (o en una columna aparte en Silver), con una regla explícita y documentada: precio de lista del producto, última mediana conocida, etc. Así queda visible y reversible. Si el porcentaje de `n/d` es alto, conviene alertar y hablarlo con el proveedor.

## Pedido 6

**CSV**: archivo de texto plano, orientado a filas. Sin tipos ni esquema (todo es texto), sin compresión nativa, legible y editable a mano, y universal. Para leer una columna hay que recorrer el archivo entero. Los problemas típicos son delimitadores, comillas, saltos de línea y codificación.

**Parquet**: formato binario, columnar y comprimido. Guarda el esquema y los tipos, y comprime mucho mejor (suele ocupar entre 5 y 10 veces menos). Permite leer solo las columnas necesarias y saltear bloques con estadísticas (predicate pushdown), por lo que las consultas analíticas son mucho más rápidas. No se puede abrir con un editor de texto y es menos cómodo para escrituras fila a fila.

Regla práctica: CSV para intercambio con terceros y archivos chicos; Parquet para almacenar y analizar datos (por ejemplo, en Silver y Gold).
