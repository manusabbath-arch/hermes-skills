## Pedido 1

Supuesto: usás Databricks o Spark con Delta Lake sobre almacenamiento de objetos (S3/ADLS/GCS).

Los dos tipos de datos van en lugares distintos del mismo lakehouse:

- **Tabla de ventas**: tabla Delta (formato columnar, transacciones ACID, time travel). Particioná por fecha solo si la tabla es grande (cientos de GB); si no, no particiones y usá liquid clustering o Z-order por las columnas de filtro habituales (fecha, cliente).
- **PDFs de facturas**: son datos no estructurados, no van dentro de una tabla Delta. Guardalos como archivos en un volumen o carpeta de objetos (por ejemplo `/Volumes/.../facturas/AAAA/MM/`) y creá una tabla Delta de metadatos con: `factura_id`, `ruta_pdf`, `hash_sha256`, `fecha`, `cliente_id`, tamaño y estado. Así podés unir las facturas con la tabla de ventas por `factura_id`.
- **Para entrenar después**: agregá una capa que extraiga el texto o los campos (OCR o parser de PDF) a una tabla `facturas_extraidas`, con versión del extractor. Eso te da features reproducibles.

Buenas prácticas: capas bronze (crudo), silver (limpio) y gold (listo para modelar). Registrá la versión de la tabla Delta usada en cada entrenamiento para poder reproducirlo. Controlá permisos con un catálogo (Unity Catalog o equivalente), porque las facturas tienen datos personales.

## Pedido 2

Causa más probable: muchos archivos chicos. Cada upsert (`MERGE`) reescribe archivos y genera otros nuevos, y tras meses la tabla queda fragmentada, con un log de transacciones largo.

Qué haría, en orden:

1. Diagnosticar con `DESCRIBE DETAIL tabla` (cantidad de archivos y tamaño promedio) y `DESCRIBE HISTORY`.
2. Compactar: `OPTIMIZE tabla` (objetivo de archivos de ~128 MB a 1 GB). Si filtrás siempre por las mismas columnas, `OPTIMIZE tabla ZORDER BY (col)` o activá liquid clustering.
3. Limpiar archivos viejos: `VACUUM tabla` con retención por defecto (7 días), no menos.
4. Prevención: activá `delta.autoOptimize.optimizeWrite = true` y `delta.autoOptimize.autoCompact = true`. Si usás Delta 3.x o Databricks, considerá deletion vectors para que los merges reescriban menos.
5. Hacé que el `MERGE` sea selectivo: agregá a la condición de join un filtro por partición o por fecha, para no escanear toda la tabla.
6. Programá `OPTIMIZE` diario o semanal después de la carga.

Si después de esto sigue lenta, revisá el plan de ejecución y las estadísticas de columnas (`delta.dataSkippingNumIndexedCols`).

## Pedido 3

Supuesto: querés un agente LLM que genere SQL y devuelva respuestas de negocio.

Diseño recomendado:

- **Acceso de solo lectura**: un usuario o rol con permisos `SELECT` únicamente, sobre un esquema curado (capa gold), nunca sobre las tablas crudas.
- **Capa semántica**: una vista o tabla documentada por métrica de negocio (ventas netas, margen, cliente activo), con comentarios en tablas y columnas. El agente rinde mucho mejor con esa documentación que con nombres crípticos.
- **Herramientas del agente**: listar tablas, describir esquema, ejecutar SQL (con límite de filas, timeout y bloqueo de DDL/DML), y ver ejemplos de consultas validadas.
- **Motor de consulta**: un SQL warehouse, Trino, o DuckDB/Spark con conector Delta. Exponelo vía MCP o una función de herramienta.
- **Controles**: registrá cada consulta, mostrá el SQL junto a la respuesta, y pedí que el agente cite las tablas usadas.
- **Evaluación**: armá 30 a 50 preguntas con respuesta conocida y medí exactitud antes de darlo a usuarios.

Riesgos: números incorrectos con aspecto convincente y exposición de datos sensibles. Mitigalos con la capa semántica y con permisos por fila o columna.

## Pedido 4

Mala noticia: `VACUUM RETAIN 0 HOURS` borra físicamente los archivos que ya no forman parte de la versión actual. El time travel depende de esos archivos, así que las versiones de hace un mes probablemente no se pueden leer más. Para ejecutarlo tuviste que desactivar la verificación `retentionDurationCheck`.

Qué hacer:

1. Verificá qué quedó: `DESCRIBE HISTORY tabla` y probá `SELECT * FROM tabla VERSION AS OF n`. Si falla con archivo no encontrado, esa versión se perdió.
2. Buscá recuperación fuera de Delta: versionado del bucket (S3 versioning, soft delete en ADLS/GCS), snapshots o backups, o una réplica. Si el bucket tiene versionado, podés restaurar los archivos borrados y recuperar la versión.
3. Si no hay copia, reconstruí el dataset aproximado: reaplicá la lógica de generación sobre los datos actuales y filtrá por fecha. No va a ser idéntico si hubo updates o deletes.
4. Prevención: no uses retención 0. Mantené 7 días como mínimo, o más (30 a 90) si necesitás reproducibilidad. Configurá `delta.deletedFileRetentionDuration` y `delta.logRetentionDuration` acordes. Para entrenamientos, guardá un snapshot inmutable: `CLONE` de la versión usada o una copia a Parquet, además de registrar la versión de la tabla. Para ahorrar espacio, es mejor compactar y borrar datos viejos que no necesitás.

## Pedido 5

Supuesto: el servidor tiene la misma versión de DuckDB y la misma plataforma que una máquina con internet.

Las extensiones se descargan de `extensions.duckdb.org` en el primer `INSTALL`. Sin internet, hay que instalarlas manualmente:

1. En una máquina con internet y **la misma versión de DuckDB y la misma plataforma** (por ejemplo `linux_amd64`), descargá el archivo:
   `http://extensions.duckdb.org/v<VERSION>/<PLATAFORMA>/delta.duckdb_extension.gz`
2. Descomprimilo (`gunzip`) y copialo al servidor.
3. Cargalo directo por ruta:
   ```sql
   LOAD '/ruta/delta.duckdb_extension';
   ```
   Si DuckDB rechaza extensiones sin firmar, iniciá con `allow_unsigned_extensions` (solo si confiás en el archivo, que debe venir del repositorio oficial).
4. Alternativa: poné el archivo en `~/.duckdb/extensions/<VERSION>/<PLATAFORMA>/delta.duckdb_extension` y ejecutá `LOAD delta;`.
5. Otra opción: configurá `custom_extension_repository` apuntando a un espejo interno.

Ojo: la versión de la extensión debe coincidir exactamente con la de DuckDB. La extensión delta tampoco existe para todas las plataformas, así que verificá que haya build para la tuya. Si no, exportá la tabla a Parquet con otra herramienta y leela con DuckDB.

## Pedido 6

Con `pandas.read_csv`:

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
print(df.head())
```

Parámetros útiles:

- `sep=";"` si el separador no es coma.
- `encoding="latin-1"` si hay errores de caracteres.
- `usecols=["a", "b"]` para leer solo algunas columnas.
- `dtype={"id": str}` para forzar tipos.
- `parse_dates=["fecha"]` para convertir fechas.
- `nrows=1000` o `chunksize=100000` para archivos grandes.
