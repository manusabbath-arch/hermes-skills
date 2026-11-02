## Pedido 1

No necesariamente se cortó el archivo. El mensaje `20 record(s) selected.` cuenta las **filas devueltas por la consulta**, mientras que tu conteo mide **líneas de texto**. Son cosas distintas, y hay varias causas posibles para la diferencia:

- **Salida de la CLP con encabezado y pie:** si copiaste la salida de pantalla, la línea de guiones, el encabezado de columna y el pie `20 record(s) selected.` también aparecen. Eso no explica que haya menos líneas, pero conviene excluirlos al contar.
- **Filas que no llegaron al archivo o a la pantalla:** si redirigiste la salida (`>`) o la copiaste desde una terminal con búfer limitado, el final puede haberse perdido. Revisá el último registro y comprobá si el archivo termina de forma completa.
- **Líneas en blanco o saltos de línea dentro de los datos:** si algún NOMBRE o TELEFONO tiene un salto de línea, una fila ocupa varias líneas. Eso aumentaría el conteo de líneas, no lo bajaría, pero confunde la comparación.

Para resolverlo sin adivinar:

1. Contá las filas directamente: `SELECT COUNT(*) FROM <tabla> WHERE <mismo filtro>;`. Si da 20, la consulta está bien y el problema está en la salida.
2. Exportá sin encabezados ni pie: `db2 -x -r salida.txt "<tu consulta>"` (el `-x` suprime encabezado y pie, y `-r` escribe a archivo). Luego contá las líneas de ese archivo. Si hay 20, el problema estaba en la copia manual.

## Pedido 2

No, que ningún producto tenga proveedor no prueba que el maestro esté vacío. Lo más común es que la **clave de unión no coincida**, y el LEFT JOIN muestra NULL en todas las filas sin error. Revisá:

- **Tipos y formato de la clave:** un `CHAR(10)` contra un `VARCHAR`, ceros a la izquierda (`00123` vs `123`), mayúsculas/minúsculas o espacios sobrantes hacen que no coincida nada. Mirá los tipos en `SYSCAT.COLUMNS`.
- **Que sean campos distintos:** el código del export puede ser un SKU, un EAN o un código interno, no el PRODUCTOID. Comparar ejemplos de ambos lados a mano suele aclararlo.
- **Que el proveedor esté en otra tabla:** en muchos ERP el proveedor vive en una tabla de relación (producto–proveedor) y no en el maestro de productos. Un LEFT JOIN directo a productos no lo va a encontrar.

Diagnóstico rápido:

```sql
SELECT COUNT(*) FROM <maestro_productos>;               -- ¿está vacío?
SELECT DISTINCT PRODUCTOID FROM <lineas_venta> FETCH FIRST 10 ROWS ONLY;
SELECT DISTINCT <codigo_export> FROM <export> FETCH FIRST 10 ROWS ONLY;
```

Si el maestro tiene filas pero los valores tienen aspecto distinto, probá `TRIM` y `UPPER` en ambos lados, o un cast explícito.

## Pedido 3

La sintaxis es:

```sql
SELECT a.columna1, b.columna2
FROM tabla_a a
LEFT JOIN tabla_b b
  ON a.clave = b.clave;
```

- `LEFT JOIN` y `LEFT OUTER JOIN` son equivalentes.
- Se devuelven **todas** las filas de `tabla_a` (la de la izquierda). Si no hay coincidencia en `tabla_b`, sus columnas salen como NULL.
- Si querés filtrar por `tabla_b`, ponés ese filtro en el `ON`, no en el `WHERE`. Un `WHERE b.columna = ...` convierte el LEFT JOIN en un INNER JOIN de hecho.
