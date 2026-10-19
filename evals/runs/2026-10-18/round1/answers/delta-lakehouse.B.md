## Pedido 1

Supuesto: las facturas son PDFs sueltos y la tabla de ventas está en CSV/DB; el modelo se entrenará más adelante, así que lo importante es poder reproducir el dataset exacto.

Qué haría:

1. **Ventas como tabla Delta.** Extraigo la tabla de ventas (CSV/DB) a `pyarrow` con tipos compactos (int64, double, bool). Uso `None` para lo "no medido", porque NULL no es 0. Escribo con `write_deltalake(ruta, tabla)`, que crea la versión 0. Si el volumen diario es grande, particiono por día con `partition_by=["day"]`.
2. **PDFs de facturas.** Los PDFs son binarios, así que no los fuerzo a columnas planas. Los dejo en object storage o en una carpeta del lake (S3/GCS/local). Creo una tabla Delta de metadatos con `factura_id`, ruta/URI del PDF, hash, fecha, cliente y, si extraigo texto o campos de la factura, columnas list/struct con eso. La tabla de ventas se une con la de facturas por `factura_id`.
3. **Historial y time-travel.** Cada escritura crea una versión nueva y `DeltaTable(ruta).history()` deja el rastro de cambios. Al entrenar, anoto el número de versión usado. Después `DeltaTable(ruta, version=N)` reproduce exactamente ese dataset.
4. **Lectura.** DuckDB o `deltalake` leen la misma tabla, sin copias que se desactualicen.

Stack: `deltalake`, `duckdb` y `pyarrow` en un venv. Las pruebas del ingesta las haría sobre un directorio temporal, nunca sobre archivos reales. Como el modelo se entrena después, defino una retención explícita antes de usar `vacuum`, para no borrar versiones que necesitaré reproducir.

## Pedido 2

Causa probable: meses de upserts diarios generan muchas versiones y muchos archivos pequeños. Cada lectura tiene que recorrer todos esos archivos y el log de transacciones, y eso la vuelve lenta. Supuesto: la tabla es chica o mediana y la corre `deltalake`/DuckDB, no un cluster Spark.

Qué haría, en orden:

1. **Diagnosticar primero.** Miro `DeltaTable(ruta).history()` y las `operationMetrics` (filas, `num_files`) para ver cuántas versiones y archivos se acumularon. Mido el tiempo de lectura real, no solo en un test chico.
2. **Compactar.** Corro la compactación (`optimize.compact()`) para juntar los archivos chicos en pocos grandes.
3. **Vacuum con retención explícita.** Uso `DeltaTable.vacuum()` para borrar los archivos viejos que ya no usa ninguna versión. Primero lo corro en modo simulación (dry run). Fijo la retención a propósito: si un modelo o un agente necesita reproducir versiones viejas con time-travel, esas versiones dejan de existir después del vacuum.
4. **Particionar por la columna de corte** (por ejemplo `day`), para que las lecturas toquen solo los archivos relevantes. Esto implica reescribir la tabla una vez.
5. **Revisar los upserts.** Si cada día reescribo toda la tabla con `mode="overwrite"`, es mejor un merge o una escritura por partición, para que cambien menos archivos por corrida.

Después de cada paso vuelvo a medir la lectura con la query de producción.

## Pedido 3

Supuesto: las tablas ya son Delta, o se pueden pasar a Delta, y el agente solo lee.

Diseño:

1. **Una sola fuente.** El agente consulta la misma tabla Delta que escribe el sistema, nunca una copia exportada que se desactualice. Le doy una conexión de solo lectura: DuckDB en memoria, que es barata y no necesita servidor.
2. **Acceso.** Cargo la tabla con `deltalake` y la consulto por SQL con DuckDB. `delta_scan` también sirve, pero descarga una extensión la primera vez y falla sin red. Si no hay red, paso la tabla a Arrow y consulto sobre eso.
3. **Contrato de datos.** Documento qué tabla promete qué columnas, con descripción y unidades de cada una. Verifico en cada ciclo que esas columnas estén pobladas. Así el agente sabe qué puede preguntar y detecto cuando una tabla quedó vacía.
4. **Valores nulos.** Marco bien NULL (no medido) frente a 0, para que el agente no interprete un dato faltante como cero.
5. **Auditoría.** Registro la versión de la tabla que vio el agente en cada respuesta. Con `history()` y time-travel puedo reconstruir luego exactamente qué datos usó.
6. **Aceptación.** No alcanza con que la tabla exista. Pruebo con 5 o 10 preguntas reales de negocio y confirmo que las respuestas salgan con valores plausibles.
