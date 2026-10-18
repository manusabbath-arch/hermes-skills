## Pedido 1

Supuesto: las facturas son PDFs en disco y la tabla de ventas sale de un CSV o de una base. No conozco el volumen.

Lo guardaría en dos tablas Delta, no en carpetas sueltas:

- `facturas`: una fila por PDF, con `id`, `sha256`, `nombre_archivo`, `ingested_at` y el contenido. Si los PDFs son chicos, el contenido va como columna binaria (`large_binary`), así queda versionado junto con el resto. Si son muchos o pesados, los PDFs quedan en object storage y la tabla guarda la ruta más el hash.
- `ventas`: la tabla de ventas normalizada a Arrow, con tipos compactos (int64, double, timestamp). Los valores no medidos quedan como NULL, no como 0.

Ambas se escriben con `write_deltalake`. Antes de entrenar, registro la versión exacta con `DeltaTable(path).version()`. Así el dataset se reproduce después con `DeltaTable(path, version=N)`.

Si necesitás texto extraído de las facturas, va en una tabla aparte, derivada del PDF, que se puede regenerar.

## Pedido 2

Causa probable: el upsert de la skill reescribe la tabla completa en cada corrida (`mode="overwrite"`). Con una corrida diaria se acumulan muchas versiones, muchos archivos chicos y lecturas que tocan todo. No tengo tu tabla ni tu código, así que es un diagnóstico probable, no confirmado.

Qué haría:

1. Medir primero: cantidad y tamaño de archivos (`DeltaTable(path).files()` y `history()`), y el tiempo de una query real en producción durante varias horas.
2. Particionar por la columna de corte (por ejemplo, la fecha) con `partition_by`, así las lecturas tocan solo las partes necesarias. Esto obliga a reescribir la tabla una vez.
3. Cambiar la reescritura diaria por un merge incremental (`DeltaTable.merge(...)`).
4. Compactar con `dt.optimize.compact()` para unir los archivos chicos.
5. Limpiar versiones viejas con `vacuum`, con retención explícita y `dry_run=True` antes de borrar (ver pedido 4).

## Pedido 3

Lo haría con una sola conexión de lectura sobre las tablas que el sistema escribe, nunca sobre copias:

- Leo la tabla con `deltalake` (QueryBuilder) y la paso a Arrow. Después la registro en DuckDB, y el agente consulta con SQL.
- Para poder auditar qué vio el agente, guardo la versión de la tabla (`DeltaTable(path, version=N)`) junto con cada respuesta.

Límites que pondría:

- Acceso de solo lectura. El agente nunca escribe en las tablas.
- Un archivo de descripción por tabla, con columnas y significado, para que el agente no invente nombres. La skill lo liga a los contratos de datos de `empirical-system-invariants`.
- Tope de filas y timeout en cada query.
- Validar las respuestas contra una query conocida antes de confiar en el agente.

Supuesto: el agente recibe SQL como texto y lo ejecuta. La skill no cubre la capa de LLM, así que el diseño de prompts y herramientas queda fuera de esta respuesta.

## Pedido 4

Vacuum borra los archivos de datos que no pertenecen a la versión actual. Con retención 0, eso incluye las versiones de hace un mes. Por defecto delta-rs bloquea retenciones menores a 7 días; para usar 0 hay que desactivar `enforce_retention_duration`, así que el borrado fue posible por esa vía.

Lo que puedo afirmar: `history()` puede seguir mostrando la versión de hace un mes, pero si sus archivos fueron borrados, esa versión ya no se puede leer desde Delta.

Qué revisaría ahora:

- Si existe una copia: un snapshot o backup en disco, versionado de object storage (S3/GCS), o las fuentes originales (SQLite, JSON, logs). Con el mismo código y la misma fecha de corte, el dataset se puede regenerar.
- Si guardaste la versión usada en el entrenamiento, eso indica exactamente qué datos reconstruir.

Para el futuro:

- Retención explícita, por ejemplo 30 días o más, y `dry_run=True` antes de cada vacuum.
- Registrar la versión en cada entrenamiento y exportar un snapshot inmutable (parquet con fecha) cuando reproducir importa.

## Pedido 5

La extensión `delta` de DuckDB se descarga la primera vez que se usa `delta_scan`. Sin internet, falla. Opciones:

1. Evitar la extensión, que es lo que hace la skill: leer la tabla con `deltalake` (QueryBuilder), pasarla a Arrow con pyarrow y consultarla desde DuckDB. No necesita red. Recomiendo esta opción.
2. Si necesitás `delta_scan` sí o sí: en una máquina con internet, instalar la extensión (`INSTALL delta;`), copiar la carpeta de extensiones de DuckDB (por defecto `~/.duckdb/extensions`) al servidor y cargarla desde ahí. La versión tiene que coincidir con la de DuckDB del servidor.

Además, `deltalake`, `duckdb` y `pyarrow` tienen que estar instalados en el servidor. Si no hay internet, instalalos desde wheels descargados antes.

## Pedido 6

Con pandas:

```python
import pandas as pd
df = pd.read_csv("archivo.csv")
```

Si el separador no es coma, usá `sep=";"`. Si el archivo no tiene encabezado, usá `header=None`.

Para ingesta en el lakehouse, la skill prefiere pyarrow: `pyarrow.csv.read_csv("archivo.csv")` devuelve una tabla Arrow lista para `write_deltalake`. Usá pandas solo si el proyecto ya lo usa.

Supuesto: pandas ya está instalado.
