## Pedido 1

Probablemente no se cortó el archivo. Hay varias causas posibles de que veas 16 líneas y no 20:

- **Filas con NULL.** En DB2, `NOMBRE || ';' || RUC || ';' || TELEFONO` da NULL si cualquiera de las tres columnas es NULL. La fila cuenta en "20 record(s) selected", pero la línea sale vacía. Según cómo cuentes, puede que no la veas. Esta es la causa más probable.
- **Líneas en blanco.** Si contaste solo las líneas con contenido, las filas NULL o vacías no las habrás contado.
- **Saltos de línea dentro de los datos.** Esto suele dar más líneas, no menos. Igual conviene revisarlo.
- **Archivo realmente truncado.** Es poco probable. El CLP escribe todo lo que devuelve la consulta. Pasaría solo si la redirección falló o si se interrumpió el proceso.

Para comprobarlo:

1. Contá también las líneas vacías. Abrí el archivo en un editor que muestre los números de línea, o mirá si hay huecos.
2. Ejecutá esta consulta: `SELECT COUNT(*) FROM tabla WHERE NOMBRE IS NULL OR RUC IS NULL OR TELEFONO IS NULL`. Si da 4, ya tenés la explicación.
3. Si hay NULLs, usá `COALESCE(NOMBRE,'') || ';' || COALESCE(RUC,'') || ';' || COALESCE(TELEFONO,'')`. Así cada fila sale completa, con campos vacíos donde falten datos.

## Pedido 2

No necesariamente. Que ningún producto tenga proveedor con ese LEFT JOIN suele indicar que el cruce no está haciendo match. No indica que la tabla esté vacía.

Causas probables:

- **Tipos o formatos distintos.** `PRODUCTOID` puede ser numérico y el código del export un texto, o viceversa. También pueden diferir los ceros a la izquierda (`00123` y `123`), los espacios al final (típico en CHAR) o las mayúsculas y minúsculas.
- **Campos que no corresponden.** Puede que el código del export sea un código de barras o SKU y no el ID interno del producto.
- **Proveedor en otra tabla.** Puede que la tabla de productos no tenga el proveedor y este viva en otra, como productos-proveedor o compras.
- **Filtro en el WHERE.** Una condición sobre la tabla derecha en el `WHERE` convierte el LEFT JOIN en un INNER JOIN. Debe ir en el `ON`.
- **Columna de proveedor vacía.** El producto puede aparecer en el join, pero con el campo proveedor en NULL.

Para diagnosticar:

1. `SELECT COUNT(*) FROM productos` te dice si el maestro tiene filas.
2. Mirá unos pocos valores de `PRODUCTOID` y unos pocos códigos del export, lado a lado. Fijate en el tipo, el largo y los ceros.
3. Contá cuántas filas del LEFT JOIN tienen la parte derecha no nula, por ejemplo `COUNT(p.PRODUCTOID)`. Si es 0, el problema es el cruce. Si es mayor que 0 pero el proveedor sale NULL, el problema es la columna de proveedor.
4. Probá normalizando: `ON TRIM(CAST(p.PRODUCTOID AS VARCHAR(50))) = TRIM(v.CODIGO)`.

## Pedido 3

La sintaxis básica es:

```sql
SELECT a.*, b.*
FROM tabla_a a
LEFT JOIN tabla_b b
  ON a.id = b.a_id;
```

- Devuelve todas las filas de `tabla_a`, la tabla izquierda.
- Si no hay coincidencia en `tabla_b`, las columnas de `b` salen como NULL.
- `LEFT OUTER JOIN` es equivalente a `LEFT JOIN`.

Para quedarte solo con las filas de A sin coincidencia en B:

```sql
SELECT a.*
FROM tabla_a a
LEFT JOIN tabla_b b ON a.id = b.a_id
WHERE b.a_id IS NULL;
```

Si querés filtrar por una columna de B sin perder filas de A, poné la condición en el `ON`, no en el `WHERE`:

```sql
LEFT JOIN tabla_b b ON a.id = b.a_id AND b.activo = 1
```
