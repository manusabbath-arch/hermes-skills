## Pedido 1

Lo guardaría en dos tablas Delta versionadas: una de ventas y una de facturas.

- **Tabla de ventas:** `write_deltalake(ruta_ventas, arrow_table, partition_by=["mes"])`, con tipos compactos (int64, double, date) y sin objetos.
- **PDFs de facturas:** hay dos opciones.
  1. Si el volumen es moderado (decenas de MB), guardarlos como columna `binary` en una tabla `facturas` con `factura_id`, `nombre`, `fecha`, `sha256`, `tamaño` y `contenido`. El dataset de entrenamiento queda como un único snapshot versionado.
  2. Si son muchos o pesados, subir los archivos a object storage (S3, GCS o Azure, con `storage_options`) y guardar en la tabla la ruta y el `sha256`. La tabla versiona el índice y el hash garantiza que el archivo no cambió.

Supuesto: volumen moderado, así que usaría la opción 1 y pasaría a la 2 si crece.

Para entrenar después, fijá la versión con `DeltaTable(ruta, version=N)` y guardá ese `N` junto con el modelo. Así podés reproducir exactamente el mismo dataset.

## Pedido 2

Lo más probable es que haya muchos archivos chicos y versiones viejas acumuladas, y que el upsert reescriba toda la tabla en cada corrida. Revisaría esto en orden:

1. Mirar `DeltaTable(ruta).history()` y la cantidad de archivos (`files()`). Si hay miles de partfiles chicos, el problema es de compactación.
2. Si el upsert lee toda la tabla y la reescribe con `mode="overwrite"`, cada día genera un commit enorme. Para tablas que crecen, conviene un merge incremental (`DeltaTable.merge`, verificando la API de tu versión de deltalake) que solo toque los archivos afectados.
3. Compactar con `DeltaTable(ruta).optimize.compact()`.
4. Particionar por la columna de corte (día o mes) si las lecturas filtran por fecha. No conviene particionar por columnas de alta cardinalidad.
5. Limpiar versiones viejas con `vacuum`, pero con retención explícita y nunca 0 (ver pedido 4).
6. Medir antes y después con el volumen real, durante horas, no con datos de prueba.

## Pedido 3

Sí, con algunas reglas:

- El agente debe leer **la misma tabla** que escribe el sistema, no una copia. Usá una conexión de solo lectura.
- Para DuckDB, cargá la tabla como Arrow y consultala desde ahí: `actual = pa.table(QueryBuilder().register("t", DeltaTable(ruta)).execute("SELECT * FROM t").read_all())` y luego `con.execute("SELECT ... FROM actual")`. Así no depende de la extensión `delta`.
- Exponé vistas con nombres de negocio y columnas documentadas, no las tablas crudas. Limitá el SQL a `SELECT` y a una lista cerrada de tablas.
- Declarar el contrato de cada tabla (columnas, tipos, nulos) y validarlo en cada ciclo, para que el agente no responda con datos vacíos o incompletos.
- Guardar con cada respuesta la versión consultada (`DeltaTable(ruta).version()`) para poder auditar qué estado vio.
- Una medición ausente debe ser NULL, no 0.

## Pedido 4

Probablemente no se pueda recuperar desde la propia tabla. `vacuum` con retención 0 borra los archivos de datos de todas las versiones que no son la actual. El log de Delta todavía menciona la versión de hace un mes, pero sus parquet ya no existen, así que el time-travel falla.

Qué haría ahora:

1. No correr más `vacuum` ni escrituras grandes sobre esa tabla hasta evaluar la situación.
2. Buscar copias fuera de la tabla: backups del filesystem o del object storage (si tiene versionado), exports de la fuente o snapshots del dataset que se hayan guardado.
3. Si la fuente original (SQLite, JSON, logs o API) todavía tiene los datos, regenerar el dataset con el mismo código de extracción y el mismo rango de fechas. Solo será idéntico si la extracción es determinística.
4. Verificar con `history()` qué versiones quedaron y si `DeltaTable(ruta, version=N)` falla.

Para que no vuelva a pasar: retención explícita de varios días, `vacuum(dry_run=True)` antes de borrar, y para entrenamientos, exportar el dataset usado como parquet con hash en otro lugar, además de la versión Delta.

## Pedido 5

La extensión `delta` de DuckDB se descarga la primera vez que se usa, así que en un servidor sin internet no se puede instalar sin preparación previa. Opciones:

- **La más simple (recomendada):** no usar la extensión. Leer la tabla con `deltalake` (`QueryBuilder`, que no necesita descargas) y pasar el resultado Arrow a DuckDB, como en el código de la skill. Solo hacen falta los paquetes `deltalake`, `duckdb` y `pyarrow` instalados en el servidor, desde wheels o un índice interno.
- **Si necesitás `delta_scan` sí o sí:** en una máquina con internet, con la misma versión de DuckDB y la misma plataforma, ejecutar `INSTALL delta FROM community;` y copiar los archivos de la extensión desde `~/.duckdb/extensions/<versión>/<plataforma>/`. En el servidor, cargarla con `LOAD '/ruta/delta.duckdb_extension';`. Verificar que la versión y la plataforma coincidan.

## Pedido 6

Con pandas:

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
```
