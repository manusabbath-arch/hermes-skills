## Pedido 1

Supuesto: lakehouse sobre almacenamiento de objetos (S3/ADLS/GCS) con Delta Lake.

- **Tabla de ventas**: guardala como tabla Delta, particionada solo si es grande y por una columna de baja cardinalidad (p. ej., `anio_mes`). Así tenés transacciones ACID, esquema forzado y time travel.
- **PDFs**: no los metas como blobs dentro de la tabla principal. Dejá los archivos crudos en una zona "raw/bronze" del bucket (`s3://lake/raw/facturas/2026/10/...pdf`) y creá una tabla Delta de metadatos/índice: `invoice_id`, `path`, `sha256`, `tamano`, `fecha_ingesta`, `cliente_id`. Si son pocos y chicos, Spark puede leerlos con el formato `binaryFile` y guardarlos en Delta, pero suele convenir la referencia por path.
- **Capa silver**: extraé texto/campos de los PDFs (OCR o parser) a otra tabla Delta (`invoice_id`, `texto`, `monto`, `fecha`, `cliente`), unible con ventas.
- **Para entrenar después**: registrá la versión de cada tabla usada (`VERSION AS OF n` o timestamp) junto al modelo (p. ej., en MLflow) para reproducibilidad, y configurá retención de historial acorde (`delta.logRetentionDuration`, `delta.deletedFileRetentionDuration`) para que `VACUUM` no borre esas versiones.
- Gobernanza: si hay datos personales en facturas, controlá accesos (Unity Catalog o IAM) y considerá enmascarar.

## Pedido 2

Causa típica: miles de archivos chicos y muchos archivos "tombstoned"/deletion vectors acumulados por los `MERGE` diarios, más un `_delta_log` largo.

Qué haría:
1. **Diagnóstico**: `DESCRIBE DETAIL tabla` (numFiles, sizeInBytes) y `DESCRIBE HISTORY` para ver la frecuencia de MERGE.
2. **Compactar**: `OPTIMIZE tabla` (y `ZORDER BY (clave_merge, columna_filtro)`), o liquid clustering (`CLUSTER BY`) si tu versión lo soporta.
3. **Limpiar**: `VACUUM tabla` con la retención por defecto (7 días) — no la bajes a 0.
4. **Prevenir**: activar `delta.autoOptimize.optimizeWrite` y `autoCompact` (Databricks), o programar `OPTIMIZE` semanal. Si usás deletion vectors, `REORG TABLE ... APPLY (PURGE)` periódicamente.
5. **Mejorar el MERGE**: agregar predicados de partición/clustering en la condición `ON` para que no reescriba toda la tabla; evitar sobre-particionar.
6. Checkpoints del log: verificá que se generen (cada 10 commits por defecto).

## Pedido 3

Supuesto: tablas Delta registradas en un catálogo, consultables por SQL.

Diseño recomendado:
- **Herramienta de SQL de solo lectura**: el agente genera SQL y lo ejecuta vía un motor (Databricks SQL, Spark, DuckDB, Trino) con un usuario/rol con permisos `SELECT` únicamente y sobre un esquema curado (gold), no sobre raw.
- **Contexto semántico**: dale al agente descripciones de tablas y columnas, métricas definidas (qué es "venta neta"), joins válidos y ejemplos de preguntas→SQL. Una capa semántica o vistas bien nombradas reduce errores.
- **Guardarraíles**: `LIMIT` automático, timeout, costo máximo, bloqueo de DDL/DML, y validación del SQL antes de ejecutarlo.
- **Flujo**: pregunta → listar/inspeccionar esquema → generar SQL → ejecutar → resumir resultado mostrando la consulta usada, para que el usuario pueda verificar.
- **Seguridad**: row/column-level security para datos sensibles; logueá cada consulta.
- **Evaluación**: armá un set de preguntas con respuestas conocidas y medí precisión antes de exponerlo.

## Pedido 4

Mala noticia: `VACUUM ... RETAIN 0 HOURS` borró físicamente los archivos que ya no pertenecían a la versión actual. El time travel a hace un mes ya no funciona porque esos Parquet no existen, aunque el `_delta_log` aún los referencie.

Opciones de recuperación:
1. **Versionado/soft delete del storage**: si el bucket tiene versioning (S3), soft delete (ADLS/GCS) o snapshots, restaurá los archivos borrados; con ellos vuelve a funcionar `VERSION AS OF`.
2. **Backups o clones**: un `DEEP CLONE`, copia o export previo.
3. **Reconstruir desde la fuente**: si las fuentes upstream son reproducibles (CDC, archivos raw), re-ejecutá el pipeline con corte a esa fecha.
4. Si nada de eso existe, el dataset exacto no es recuperable; documentalo.

Para que no se repita:
- Volvé a activar `spark.databricks.delta.retentionDurationCheck.enabled = true`.
- Retención ≥ al horizonte de reproducibilidad (p. ej., `delta.deletedFileRetentionDuration = 'interval 90 days'` y `logRetentionDuration` acorde).
- Para entrenamiento, materializá snapshots: `CREATE TABLE train_2026_09 DEEP CLONE ventas VERSION AS OF n`, y registrá la versión en el tracking del modelo.

## Pedido 5

DuckDB intenta bajar la extensión `delta` desde su repositorio y sin internet falla. Solución: instalarla offline.

1. En una máquina con internet y **la misma versión de DuckDB y plataforma** (p. ej., v1.x, `linux_amd64`), ejecutá `INSTALL delta;` y buscá el archivo en `~/.duckdb/extensions/<version>/<plataforma>/delta.duckdb_extension` (o descargalo de `http://extensions.duckdb.org/<version>/<plataforma>/delta.duckdb_extension.gz` y descomprimilo).
2. Copialo al servidor.
3. Instalalo desde archivo:
   ```sql
   INSTALL '/ruta/delta.duckdb_extension';
   LOAD delta;
   ```
   o copiá el archivo en la misma ruta `~/.duckdb/extensions/<version>/<plataforma>/` y hacé solo `LOAD delta;`.
4. Evitá el autoload que intenta descargar: `SET autoinstall_known_extensions = false;` y, si querés, `SET extension_directory = '/ruta/compartida';`.

Ojo: la versión de la extensión debe coincidir exactamente con la de DuckDB; si actualizás DuckDB, repetí el proceso. Alternativa: usar un mirror interno con `SET custom_extension_repository = 'http://mirror-interno/...'`.

## Pedido 6

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
print(df.head())
```

Opciones útiles: `sep=";"` para otro separador, `encoding="latin-1"` si hay problemas de acentos, `usecols=[...]` para leer solo algunas columnas y `parse_dates=["fecha"]` para fechas.
