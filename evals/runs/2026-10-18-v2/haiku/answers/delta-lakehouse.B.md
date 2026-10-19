## Pedido 1

Supuesto: el lakehouse corre sobre almacenamiento de objetos (S3, GCS o ADLS) con un catálogo encima, y el modelo se entrena después.

Yo lo separaría en dos partes:

- **PDFs de facturas:** son datos no estructurados. Los guardaría como archivos inmutables en el almacenamiento de objetos, en una ruta tipo `raw/facturas/<hash-sha256>.pdf`. Así el nombre es único y no se pisan archivos al reprocesar.
- **Tabla de metadatos:** una tabla Delta con una fila por PDF: ruta, hash, fecha de carga, id de factura y campos extraídos (si los hay). Esa tabla es la que se consulta y se versiona.
- **Tabla de ventas:** tabla Delta normal, con esquema explícito y particionada por fecha si el volumen lo justifica.

Para entrenar después, no apuntes al "estado actual". Guardá la versión exacta usada: número de versión de Delta (o snapshot en Iceberg) más la lista de hashes. Así el dataset es reproducible aunque cambien los datos. No corras VACUUM con retención baja sobre estas tablas.

## Pedido 2

Causas probables de la lentitud tras meses de upserts diarios:

1. **Muchos archivos chicos.** Cada MERGE genera archivos nuevos y pequeños. Revisá con `DESCRIBE DETAIL <tabla>` (campo `numFiles` y `sizeInBytes`).
2. **Historial de log largo.** Muchas versiones hacen más lento el arranque de cada lectura.
3. **Sin clustering.** Si las consultas filtran por ciertas columnas y no hay Z-ORDER o liquid clustering, se leen demasiados archivos.

Qué haría:

- Ejecutar `OPTIMIZE <tabla>` para compactar archivos, y agregar `ZORDER BY` (o clustering líquido) por las columnas de filtro más usadas.
- Limpiar con `VACUUM` usando la retención por defecto (7 días o más), nunca 0.
- Revisar la condición del MERGE: si incluye la partición o una clave acotada, Delta reescribe menos archivos.
- Activar auto-optimize o programar OPTIMIZE semanal o diario según el volumen.
- Revisar particiones: si hay demasiadas particiones pequeñas, conviene quitarlas.

Medir antes y después con las mismas consultas.

## Pedido 3

Lo haría con una capa semántica y permisos de solo lectura:

- **Tablas curadas (gold):** el agente consulta tablas de negocio con nombres claros y comentarios, no las tablas crudas.
- **Diccionario de métricas:** definiciones explícitas (por ejemplo, qué es "venta neta"). Sin esto el agente inventa definiciones.
- **Usuario de solo lectura:** un service principal con permiso SELECT sobre las tablas permitidas. Nada de escritura.
- **Guardrails:** límite de filas, timeout por consulta, lista de tablas permitidas y validación del SQL antes de ejecutarlo.
- **Trazabilidad:** que el agente muestre el SQL usado junto con la respuesta, y registre cada consulta.
- **Evaluación:** un set de preguntas con respuestas esperadas, para medir precisión antes de usarlo.

## Pedido 4

Con VACUUM retención 0 se borraron los archivos de datos que Delta necesita para time travel. Delta no los conserva, así que esa versión no se puede reconstruir desde el log. Lo que haría, en orden:

1. Buscar copias: el dataset de entrenamiento en otro lugar (artefactos de MLflow, exports, snapshots del pipeline), o la fuente original (las facturas y ventas de origen) para regenerarlo.
2. Revisar si el bucket tiene versionado de objetos. Si lo tiene, las versiones anteriores pueden seguir ahí aunque Delta las haya marcado como borradas.
3. Revisar si hay un clone (shallow o deep) de la tabla en algún lado.
4. Si nada de eso existe, regenerar el dataset desde la fuente con la misma lógica, y documentar la diferencia.

A futuro: retención mínima de 7 días, no desactivar la validación de retención, y guardar cada dataset de entrenamiento con su versión de Delta y sus hashes.

## Pedido 5

El problema es que DuckDB intenta descargar la extensión y no tiene internet. Supuesto: tenés una máquina con internet igual a la del servidor (mismo sistema y misma versión de DuckDB).

1. En la máquina con internet: `INSTALL delta FROM community;` y ubicar el archivo `delta.duckdb_extension` (dentro de `~/.duckdb/extensions/<versión>/<plataforma>/`).
2. Copiar ese archivo al servidor.
3. En el servidor: `LOAD '/ruta/delta.duckdb_extension';`

Si DuckDB rechaza el archivo, la versión de DuckDB o la plataforma no coinciden. Otra opción es usar la librería `deltalake` (delta-rs) de Python, instalada desde un wheel descargado previamente, y pasar los datos a DuckDB como DataFrame o Parquet.

## Pedido 6

Con pandas:

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
```

Si hace falta, podés ajustar el separador (`sep=";"`), la codificación (`encoding="latin-1"`), las fechas (`parse_dates=["fecha"]`) o leer solo algunas filas (`nrows=1000`).
