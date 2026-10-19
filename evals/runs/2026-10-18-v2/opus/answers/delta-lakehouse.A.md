## Pedido 1

Propongo un lakehouse Delta con `deltalake` + `pyarrow` (+ `duckdb` para consultar). Supuesto: corrés en Python y el lake vive en disco local o en object storage (S3/GCS/Azure, con credenciales vía `storage_options`).

1. **Tabla `ventas`**: extraés de la fuente (CSV/DB) a un `pa.Table` con tipos compactos (int64, double, bool, timestamp) y escribís con `write_deltalake(ruta, tabla, partition_by=["dia"])`. Los nulos quedan como NULL, no como 0.
2. **PDFs de facturas**: los archivos binarios no van en la tabla. Los dejás en el storage (`facturas/raw/<id>.pdf`) y armás una tabla Delta `facturas` con metadatos: `factura_id`, `ruta_pdf`, `hash`, `fecha`, `texto_extraido` y los campos que extraigas (total, cliente). Los campos semiestructurados van como columna struct/list de Arrow, sin aplanarlos a la fuerza.
3. **Versionado para ML**: cada escritura crea una versión nueva. Cuando entrenes, anotá la versión de cada tabla (`DeltaTable(ruta).version()`) junto al modelo. Así podés reproducir el dataset exacto con `DeltaTable(ruta, version=N)`.
4. **Retención**: no corras `vacuum` agresivo sobre versiones que usaste para entrenar. Fijá una retención explícita.

Para validarlo, alcanza con que una query real (por ejemplo, ventas JOIN facturas por `factura_id`) devuelva valores plausibles. Que la tabla exista no prueba que esté bien.

## Pedido 2

Lo más probable es que cada upsert diario haya dejado archivos chicos y versiones viejas, y que cada lectura tenga que recorrer cientos de partfiles. Haría esto:

1. **Diagnóstico**: con `DeltaTable(ruta).history()` mirá `operationMetrics` (num_files, filas) y contá los archivos activos con `len(dt.files())`. Medí el tiempo de lectura antes y después de cada cambio.
2. **Compaction**: `dt.optimize.compact()` junta los archivos chicos. Si filtrás siempre por las mismas columnas, `dt.optimize.z_order(["col"])` agrupa los datos por esas columnas.
3. **Vacuum con retención explícita**: `dt.vacuum(retention_hours=168, dry_run=False)` borra los archivos que ya no se referencian. Elegí una retención que cubra las versiones que necesitás reproducir para modelos o agentes.
4. **Particionado**: si consultás por fecha, reescribí con `partition_by=["dia"]` para que cada lectura toque solo las particiones relevantes.
5. **Upsert más barato**: si hoy el upsert reescribe toda la tabla con overwrite, pasá a `dt.merge(...)` por clave primaria, que solo reescribe los archivos afectados.

Programá compact + vacuum como mantenimiento periódico, por ejemplo semanal, y validá con lecturas de producción reales.

## Pedido 3

Supuesto: el agente es un LLM con una herramienta para ejecutar SQL.

- **Engine**: DuckDB en memoria, sin servidor, leyendo las mismas tablas Delta que escribe el sistema, nunca copias que se desactualicen. Podés usar `delta_scan('<ruta>')` o leer con `deltalake` a Arrow y registrar esa tabla en DuckDB. La segunda opción evita depender de la extensión `delta`.
- **Una única herramienta de lectura** (`consultar_sql(query)`): conexión de solo lectura, con límite de filas y timeout, y solo sentencias SELECT.
- **Contexto para el agente**: dale el esquema de cada tabla, una descripción en lenguaje de negocio de cada columna, las unidades y el significado de NULL. Así no inventa columnas.
- **Auditabilidad**: registrá con cada respuesta la versión Delta que consultó (`DeltaTable(ruta).version()`). Con time-travel podés reproducir después exactamente qué datos vio.
- **Contratos de datos**: definí qué columnas promete cada tabla y verificá en cada ciclo que se cargaron.

Lo aceptaría cuando el agente responda bien un set de preguntas de negocio reales contra datos de producción. Que la herramienta funcione no alcanza.

## Pedido 4

Malas noticias: un `vacuum` con retención 0 borra físicamente todos los archivos que la versión actual ya no referencia. El log de transacciones conserva el historial, pero `DeltaTable(ruta, version=N)` de hace un mes va a fallar o va a apuntar a archivos que ya no existen. Delta no tiene forma de recuperarlo.

Opciones, de la más rápida a la más lenta:

1. **Versionado o backup del storage**: si el bucket tiene versioning (S3/GCS) o hay snapshots del disco, restaurá los partfiles borrados. Los paths aparecen en las entradas `add` del `_delta_log` de esa versión.
2. **Artefactos del entrenamiento**: revisá si el pipeline de entrenamiento guardó una copia o un cache del dataset (parquet, features).
3. **Reconstrucción**: si las fuentes originales siguen disponibles, re-ejecutá el ETL filtrando hasta la fecha de esa versión (el timestamp está en `history()`). Va a ser aproximado si las fuentes cambiaron.

Para que no vuelva a pasar:
- Nunca uses retención 0 en tablas que alimentan modelos. Usá una retención explícita mayor que tu ventana de reproducibilidad (por ejemplo, 30 a 90 días) y dejá activado el chequeo de retención mínima.
- Anotá la versión Delta junto a cada modelo entrenado. Para los datasets críticos, guardá un snapshot inmutable aparte, por ejemplo con un write a una tabla `training_snapshots`.
- Para ahorrar espacio, primero corré compaction. El vacuum va después y con retención razonable.

## Pedido 5

DuckDB intenta descargar la extensión `delta` la primera vez que usás `delta_scan`, y sin red esa descarga falla. Tenés dos caminos:

**A) Instalar la extensión offline**
1. En una máquina con internet, usá **la misma versión de duckdb y la misma plataforma** (por ejemplo, linux_amd64) y corré `INSTALL delta;`.
2. Copiá el archivo `~/.duckdb/extensions/<version>/<plataforma>/delta.duckdb_extension` a la misma ruta en el servidor.
3. En el servidor corré `LOAD delta;`. También podés hacer `INSTALL '/ruta/delta.duckdb_extension'; LOAD delta;`.

Si la versión de duckdb no coincide exactamente, la extensión no carga.

**B) No usar la extensión** (es lo que haría yo en un servidor aislado)
Leé la tabla con `deltalake`, que no necesita red, y consultá el resultado como Arrow desde DuckDB:

```python
import pyarrow as pa, duckdb
from deltalake import DeltaTable, QueryBuilder
dt = DeltaTable("ruta/tabla")
actual = pa.table(QueryBuilder().register("t", dt).execute("SELECT * FROM t").read_all())
duckdb.connect().execute("SELECT count(*) FROM actual").fetchall()
```

Además, preinstalá las dependencias (`deltalake`, `duckdb`, `pyarrow`) en un venv desde wheels descargados antes.

## Pedido 6

```python
import pandas as pd
df = pd.read_csv("archivo.csv")
```

Parámetros útiles: `sep=";"` si el separador no es coma, `encoding="latin-1"` si hay problemas con acentos, `usecols=[...]` para leer solo algunas columnas, `parse_dates=["fecha"]` para convertir fechas y `dtype={"col": "Int64"}` para fijar tipos.
