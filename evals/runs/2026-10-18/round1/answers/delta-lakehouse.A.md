## Pedido 1

Supuestos: uso un lakehouse tipo Databricks/Fabric con Delta Lake; las facturas son PDFs escaneados o generados, y la tabla de ventas es tabular (CSV/Excel/base transaccional).

Los dos datos son de naturaleza distinta, así que van en lugares distintos del mismo lakehouse:

- **Tabla de ventas**: tabla Delta gestionada (Unity Catalog / sección Tables), con arquitectura medallion. Bronze: carga cruda; Silver: tipos limpios, deduplicada, con clave (id_venta) y fecha; Gold: agregados o features para el modelo. Particionaría por fecha solo si la tabla es grande (cientos de GB); si no, mejor sin particionar.
- **PDFs de facturas**: archivos, no tablas. Los guardaría tal cual en un Volume (Unity Catalog) o en la zona Files, en rutas como `/facturas/anio=2026/mes=10/`. Luego crearía una tabla Delta de metadatos (nombre de archivo, ruta, fecha, cliente, id_factura, hash) que se une con ventas por id_factura. Si el modelo necesita el contenido, extraería texto/campos con OCR o un parser de documentos y guardaría el resultado en otra tabla Delta, conservando la ruta del PDF original como trazabilidad.

Para entrenar después: definir un split reproducible (por fecha, para evitar fuga de datos), usar Delta time travel o una versión fija de la tabla para versionar el dataset de entrenamiento, y aplicar permisos (las facturas tienen datos personales/fiscales: enmascarar o restringir acceso).

Haría: crear catálogo/esquema, volume, ingesta con Auto Loader para los PDFs, carga de ventas a bronze, y la tabla de metadatos que une ambos.

## Pedido 2

Supuesto: tabla Delta con `MERGE` diario; la lentitud viene de acumulación de archivos pequeños y de metadata/versiones viejas, que es lo típico tras meses de upserts.

Diagnóstico primero:
- `DESCRIBE DETAIL tabla` para ver numFiles y sizeInBytes: muchos archivos de pocos MB confirma el problema.
- `DESCRIBE HISTORY tabla` para ver cuántas operaciones MERGE y cuántos archivos reescribe cada una.

Acciones, en orden:
1. **`OPTIMIZE tabla`** para compactar archivos pequeños en archivos de ~1 GB (o ~128 MB–1 GB según el motor). Si se filtra siempre por ciertas columnas, `OPTIMIZE tabla ZORDER BY (col)`, o mejor, liquid clustering (`CLUSTER BY`) si está disponible.
2. **`VACUUM tabla`** para eliminar archivos obsoletos fuera del período de retención (7 días por defecto; no lo bajes sin entender el impacto sobre time travel y lectores concurrentes).
3. Reducir la reescritura del MERGE: agregar a la condición del merge un filtro sobre la partición/fecha (`ON t.id = s.id AND t.fecha >= ...`) para que no escanee toda la tabla. Activar deletion vectors si el motor lo soporta, así los updates no reescriben archivos completos.
4. Activar optimized writes y auto compaction (`delta.autoOptimize.optimizeWrite`, `delta.autoOptimize.autoCompact`) para que no vuelva a pasar.
5. Programar OPTIMIZE semanal (y VACUUM) como job.

Verificaría con la misma consulta antes y después, comparando tiempo y archivos leídos.

## Pedido 3

Supuestos: lakehouse con tablas Delta en catálogo (Unity Catalog u otro); el agente es un LLM con herramientas; las preguntas son de negocio (ventas por región, márgenes, etc.).

Diseño recomendado:
- **Capa de acceso**: el agente no toca el almacenamiento; consulta vía un SQL endpoint/warehouse con un servicio de solo lectura. Credenciales con el mínimo privilegio: un rol que solo ve las tablas gold/silver aprobadas, con columnas sensibles enmascaradas.
- **Contexto semántico**: tablas gold bien modeladas, con comentarios en tablas y columnas, definiciones de métricas (qué es "venta neta", "cliente activo") y relaciones. Una capa semántica o vistas de métricas reduce errores mucho más que un prompt largo.
- **Herramientas del agente**: (1) listar/describir tablas, (2) ejecutar SQL de solo lectura con límite de filas y timeout, (3) opcional: buscar métricas definidas. Flujo: entender la pregunta, inspeccionar esquema, generar SQL, ejecutar, validar el resultado (¿filas vacías? ¿magnitud razonable?), responder mostrando la consulta usada.
- **Seguridad**: solo `SELECT`, bloquear DDL/DML, permisos a nivel de catálogo, auditoría de cada consulta, límite de costo.
- **Calidad**: armar un set de 20–30 preguntas con respuestas conocidas y medir la exactitud del agente antes de dárselo a usuarios; que cite siempre tabla y filtros.

Si usás Databricks, Genie o un MCP de SQL cubren buena parte de esto; si no, un MCP propio con las herramientas anteriores.
