## Pedido 1

Propongo una arquitectura medallion (Bronze → Silver → Gold) sobre archivos Parquet, orquestada con un scheduler simple (cron, Airflow o Dagster).

**Ingesta (Bronze, crudo e inmutable)**
- **API REST de ventas:** extracción incremental por `updated_at` o cursor, con paginación y reintentos. Se guarda el JSON tal cual en `bronze/ventas_api/fecha_carga=YYYY-MM-DD/`.
- **Postgres (maestro de clientes):** snapshot diario completo o CDC si la tabla es grande. Va a `bronze/clientes/`.
- **CSV por SFTP:** se copia el archivo original sin tocarlo y se registran el nombre, el hash SHA-256 y la fecha de carga.
- Todas las fuentes llevan columnas de auditoría: `_source`, `_ingested_at`, `_file_name`, `_batch_id`.

**Silver (limpio y conformado)**
- Tipado, normalización de fechas, monedas y códigos.
- Deduplicación por clave de negocio, por ejemplo `id_venta`.
- El maestro de clientes es una dimensión SCD tipo 2 si interesa la historia de los cambios.
- Validaciones de calidad: nulos, rangos e integridad referencial. Los registros inválidos van a una tabla de cuarentena.

**Gold (modelo para el negocio)**
- Esquema estrella: `fact_ventas` más las dimensiones `dim_cliente`, `dim_producto` y `dim_fecha`.
- Una tabla de supuestos de escenarios (por ejemplo variación de precio, volumen o tipo de cambio) cargada por el negocio y versionada.
- Vistas o agregados `escenario_x_periodo` que combinan los datos reales con esos supuestos.

**Consumo:** el dashboard (Power BI, Superset o Streamlit) lee solo Gold. Los parámetros de escenario se manejan en el dashboard o en la tabla de supuestos.

**Supuestos:** volumen moderado (menos de cientos de millones de filas), así que DuckDB con Parquet alcanza. Si el volumen crece, se pasa el mismo diseño a Delta/Iceberg sobre Spark o a un warehouse.

## Pedido 2

No te lo recomiendo. Bronze es tu red de seguridad:

- **Reprocesar:** si mañana descubrís un bug en la regla de deduplicación o de limpieza, sin el dato crudo no podés reconstruir nada. Habría que volver a pedirle los datos a la fuente, y muchas veces eso ya no es posible (una API sin historia, un SFTP que borra los archivos).
- **Auditoría y trazabilidad:** vas a poder demostrar qué llegó exactamente y cuándo.
- **Debugging:** vas a poder comparar el dato crudo con el limpio cuando un número no cierra.
- **Reglas que cambian:** lo que hoy es un "duplicado" mañana puede no serlo.

Bronze cuesta poco: Parquet comprimido o el archivo original en almacenamiento barato. Si te preocupa el espacio, definí una retención, por ejemplo 90 días o 2 años según la regulación. Eso es mejor que no tenerla.

Lo que sí podés hacer al ingestar es lo mínimo y sin pérdida: agregar metadatos de carga, calcular el hash del archivo y rechazar archivos repetidos idénticos. La limpieza y la deduplicación de registros van en Silver.

## Pedido 3

Supongo un stack en Python con DuckDB y Parquet, que es liviano, corre local y no necesita cluster. Columnas asumidas: `id_venta, fecha, id_cliente, producto, cantidad, precio`.

```python
import duckdb, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("lake")
con = duckdb.connect("lake/meta.duckdb")
con.execute("CREATE TABLE IF NOT EXISTS archivos_cargados(hash TEXT PRIMARY KEY, nombre TEXT, cargado_en TIMESTAMP)")

def bronze(csv_path: str):
    h = hashlib.sha256(Path(csv_path).read_bytes()).hexdigest()
    if con.execute("SELECT 1 FROM archivos_cargados WHERE hash=?", [h]).fetchone():
        print("Archivo ya cargado, se omite"); return
    dest = BASE / "bronze/ventas" / f"{h}.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"""
        COPY (SELECT *, '{Path(csv_path).name}' AS _file, '{h}' AS _hash,
                     now() AS _ingested_at
              FROM read_csv('{csv_path}', all_varchar=true))
        TO '{dest}' (FORMAT parquet)""")
    con.execute("INSERT INTO archivos_cargados VALUES (?,?,?)",
                [h, Path(csv_path).name, datetime.now(timezone.utc)])

def silver():
    (BASE / "silver").mkdir(exist_ok=True)
    con.execute(f"""
        COPY (
          SELECT * EXCLUDE rn FROM (
            SELECT TRY_CAST(id_venta AS BIGINT) id_venta,
                   TRY_CAST(fecha AS DATE) fecha,
                   TRIM(id_cliente) id_cliente,
                   TRIM(producto) producto,
                   TRY_CAST(cantidad AS INT) cantidad,
                   TRY_CAST(NULLIF(TRIM(precio),'n/d') AS DECIMAL(12,2)) precio,
                   _ingested_at,
                   ROW_NUMBER() OVER (PARTITION BY id_venta ORDER BY _ingested_at DESC) rn
            FROM read_parquet('{BASE}/bronze/ventas/*.parquet')
            WHERE TRY_CAST(id_venta AS BIGINT) IS NOT NULL)
          WHERE rn = 1)
        TO '{BASE}/silver/ventas.parquet' (FORMAT parquet)""")

def gold():
    (BASE / "gold").mkdir(exist_ok=True)
    con.execute(f"""
        COPY (SELECT date_trunc('month', fecha) mes, producto,
                     SUM(cantidad) unidades,
                     SUM(cantidad*precio) importe,
                     COUNT(*) FILTER (WHERE precio IS NULL) ventas_sin_precio
              FROM read_parquet('{BASE}/silver/ventas.parquet')
              GROUP BY ALL)
        TO '{BASE}/gold/ventas_mensual.parquet' (FORMAT parquet)""")

if __name__ == "__main__":
    bronze("ventas_2026-10-18.csv"); silver(); gold()
```

Silver y Gold se reconstruyen completos en cada corrida, así que son idempotentes. Con mucho volumen convendría pasar a un esquema incremental particionado por fecha.

## Pedido 4

El problema es que el pipeline no es idempotente. Hay que arreglarlo en dos niveles.

**1. Control a nivel archivo (Bronze).** Calculá el hash SHA-256 de cada archivo y guardalo en una tabla de control (`archivos_cargados`). Si el hash ya existe, el archivo se omite y se loguea. Así se cubre el caso de un reenvío idéntico aunque cambie el nombre del archivo.

**2. Deduplicación por clave de negocio (Silver), que es la defensa principal.** Aunque el archivo venga con otro hash (por ejemplo, regenerado con otro timestamp), Silver tiene que quedarse con un solo registro por `id_venta`:

```sql
SELECT * FROM bronze
QUALIFY ROW_NUMBER() OVER (PARTITION BY id_venta ORDER BY _ingested_at DESC) = 1
```

Si no hay un ID natural, armá una clave con el hash de las columnas que identifican la venta (fecha, cliente, producto, comprobante).

**3. Escritura idempotente.** Usá `MERGE`/upsert o la sobrescritura de la partición de fecha en lugar de un `INSERT` append. Así, volver a correr el mismo día da el mismo resultado.

**4. Corregir lo que ya pasó.** No borres el duplicado de Bronze, porque sirve como evidencia. Aplicá la deduplicación en Silver y reconstruí Gold para las fechas afectadas.

**5. Prevención.** Agregá un test de calidad que haga fallar el pipeline si aparecen claves duplicadas en Silver, y una alerta si el total diario se desvía mucho del histórico.

## Pedido 5

No. Ponerlo en 0 justamente rompe los promedios: los tira para abajo e inventa ventas gratis que no existieron. Un 0 es un valor real ("sin costo") y "n/d" significa "desconocido". No son lo mismo.

Lo correcto en Silver:

- Convertí `'n/d'` (y variantes como `''`, `'N/A'` o `'-'`) a **NULL**: `TRY_CAST(NULLIF(TRIM(precio), 'n/d') AS DECIMAL)`.
- Agregá un flag `precio_faltante = TRUE` o un motivo de calidad, para que sea trazable.
- Medí el porcentaje de NULLs y alertá si supera un umbral.

Con NULL, `AVG(precio)` ignora esos registros y el promedio queda correcto sobre los datos conocidos. Para sumas como `SUM(cantidad*precio)`, mostrá en Gold cuántas ventas quedaron sin precio, así el dashboard no presenta un total incompleto como si fuera completo.

Si el negocio necesita un valor, la imputación (último precio conocido, precio de lista del producto) se hace en Gold o en una columna aparte (`precio_imputado`), documentada y sin pisar el dato original. Bronze conserva el `'n/d'` tal cual llegó.

## Pedido 6

- **CSV:** texto plano, orientado a filas, sin tipos (todo es texto hasta que lo interpretás), sin compresión nativa y con problemas típicos de separadores, comillas y encoding. Es universal y legible por humanos, ideal para intercambio.
- **Parquet:** binario, columnar, con esquema y tipos incluidos, comprimido (suele ocupar entre 5 y 10 veces menos) y con estadísticas por bloque. Permite leer solo las columnas necesarias y saltear bloques al filtrar, así que las consultas analíticas son mucho más rápidas. No se abre con un editor de texto.

En la práctica: CSV para recibir o entregar datos, Parquet para almacenar y analizar dentro del lake.
