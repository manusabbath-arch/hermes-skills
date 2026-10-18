## Pedido 1

Supuesto: las facturas son PDFs y las ventas son una tabla estructurada, y el modelo se entrena después sobre ambos.

Armaría un lakehouse Delta con `deltalake` + `pyarrow` + `duckdb`:

1. **Ventas**: normalizar a `pa.Table` con tipos compactos (int64, double, bool; `None` para "no medido", porque NULL no es 0) y escribirla con `write_deltalake(ruta, tabla)`. Eso crea la versión 0. Si consultás por fecha, particiono con `partition_by=["day"]`.
2. **Facturas PDF**: los binarios no se fuerzan a columnas planas. Guardo los PDFs en object storage o en una carpeta del lake, y en una segunda tabla Delta dejo una fila por factura: id, ruta/URI, hash, fecha, metadatos y el texto extraído si lo necesitás para entrenar. Si querés el binario dentro de la tabla, va como columna binary, pero con muchos PDFs prefiero la referencia.
3. **Reproducibilidad**: cada escritura nueva crea otra versión. `DeltaTable(ruta).history()` te da el rastro de operaciones y `DeltaTable(ruta, version=N)` te devuelve exactamente el dataset con el que entrenaste. Anotá la versión usada en cada entrenamiento.
4. **Consumo**: DuckDB lee la misma tabla, sin copias que se desfasen.

Instalación: `python3 -m venv .lhenv && .lhenv/bin/pip install deltalake duckdb pyarrow`.

Para validar, no alcanza con que la tabla exista: corré una consulta real y mirá que los valores sean plausibles.

## Pedido 2

Supuesto: la tabla se reescribe con upserts diarios y nadie hizo mantenimiento.

Lo más probable es que acumulaste muchas versiones y muchos archivos chicos, y eso enlentece las lecturas. Haría esto:

1. **Diagnosticar**: `DeltaTable(ruta).history()` para ver cuántas versiones y operaciones hay, y contar los archivos (`num_files` en `operationMetrics`).
2. **Compactar** los archivos chicos en menos y más grandes.
3. **Vacuum** con una retención explícita, nunca 0. Antes decidí qué versiones históricas necesitás reproducir (por ejemplo, las usadas para entrenar), porque vacuum borra los archivos viejos y elimina esa posibilidad de time travel.
4. **Particionar** por la columna de corte (por ejemplo `day`) con `partition_by=["day"]`, así las lecturas tocan solo los archivos relevantes. Esto implica reescribir la tabla una vez.
5. **Medir** el tiempo de lectura antes y después con consultas reales de producción, durante horas y no en una prueba chica.

Si leés con `to_pyarrow_table()` y notás cuelgues, probá la lectura nativa con `QueryBuilder().register("t", dt).execute("SELECT * FROM t")`.

## Pedido 3

Supuesto: el agente solo necesita leer, no escribir.

La idea es que el agente consuma la misma tabla que escribe el sistema, nunca una copia que se desfase.

1. **Conexión única de lectura**: DuckDB en memoria, sin servidor. Conviene que sea de solo lectura.
2. **Acceso**: pasarle a DuckDB un Arrow table leído con `deltalake` (`QueryBuilder` o `DeltaTable`), o `delta_scan('<ruta>')`. Ojo: `delta_scan` necesita descargar la extensión `delta` la primera vez, así que requiere red o instalarla de antemano.
3. **Contrato de datos**: documentá qué tabla promete qué columnas y verificalo en cada ciclo, para que el agente sepa que los datos están poblados.
4. **Reproducibilidad**: registrá en qué versión de la tabla consultó el agente. Con time travel (`DeltaTable(ruta, version=N)`) podés reconstruir exactamente qué estado vio.
5. **Aceptación**: probá con preguntas reales de negocio y comprobá que las respuestas tengan valores plausibles.

Para el agente, exponé una herramienta de SQL de solo lectura con las tablas y columnas documentadas, y limitá los resultados.

## Pedido 4

Con retención 0, vacuum borró los archivos que ya no formaban parte de la versión actual. Esos archivos eran los que permitían el time travel, así que las versiones de hace un mes probablemente no se pueden leer más.

Qué haría:

1. **Verificar el daño**: intentar `DeltaTable(ruta, version=N)` y leerla. El historial (`history()`) sigue mostrando las operaciones, pero los datos pueden faltar.
2. **Recuperar si hay respaldo**: snapshots del storage, versionado del bucket o backups. Si existen, restaurá desde ahí.
3. **Si no hay respaldo**: reconstruir el dataset desde las fuentes originales, o aproximarlo con la versión actual y los criterios de filtrado de aquella fecha. Va a ser una aproximación, no una copia exacta, y hay que declararlo.
4. **Prevenir**: usar siempre una retención explícita acorde a cuánto tiempo necesitás reproducir entrenamientos. Además, congelá cada dataset de entrenamiento: anotá la versión o exportá una copia a parquet.

Supuesto: nadie hizo copia previa. No volvería a correr vacuum sin definir antes qué se tiene que poder reproducir.

## Pedido 5

DuckDB intenta descargar la extensión `delta` la primera vez que usás `delta_scan`, y sin internet falla.

Opciones, de la más simple a la más trabajosa:

1. **Evitar la extensión (recomendado)**: leer con `deltalake` y pasarle el resultado a DuckDB como Arrow:

```python
import pyarrow as pa, duckdb
from deltalake import DeltaTable, QueryBuilder
dt = DeltaTable(ruta)
actual = pa.table(QueryBuilder().register("t", dt).execute("SELECT * FROM t").read_all())
con = duckdb.connect()
con.execute("SELECT * FROM actual").fetchall()
```

DuckDB reconoce la variable `actual` por nombre. No necesita red.

2. **Instalar la extensión sin conexión**: bajarla en una máquina con internet para la misma versión y plataforma de DuckDB, copiarla al servidor y cargarla con `LOAD` desde el archivo. Es más frágil porque tiene que coincidir con la versión.

Supuesto: `deltalake` y `pyarrow` ya están instalados en el servidor.

## Pedido 6

Con pandas:

```python
import pandas as pd
df = pd.read_csv("archivo.csv")
print(df.head())
```

Opciones útiles: `sep=";"` si el separador no es coma, `encoding="latin-1"` si hay problemas con acentos, `usecols=["a","b"]` para leer solo algunas columnas y `dtype={"id": str}` para forzar tipos.
