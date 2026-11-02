## Pedido 1

No, el archivo no se cortó. Lo más probable es que **4 filas se perdieron en la consulta**, no en el archivo.

En DB2, si alguna columna de una concatenación con `||` vale NULL, el resultado completo de la concatenación es NULL. Una fila cuyo `SELECT` es solo esa cadena sale NULL y no aparece en lo que imprime el cliente. El contador sí la cuenta. Por eso ves `20 record(s) selected.` y solo 16 líneas, sin ningún error. Lo más probable es que 4 registros tengan `NOMBRE`, `RUC` o `TELEFONO` en NULL. El teléfono es el candidato más común.

**Arreglo:** envolvé cada operando que admita NULL con `COALESCE`:

```sql
SELECT COALESCE(NOMBRE,'') || ';' || COALESCE(RUC,'') || ';' || COALESCE(TELEFONO,'')
FROM ...
```

Esto no cambia ningún valor que no sea NULL. Con eso deberías ver las 20 líneas, y las 4 que faltaban tendrán el campo vacío.

**Para confirmarlo:** corré `SELECT COUNT(*) FROM ... WHERE NOMBRE IS NULL OR RUC IS NULL OR TELEFONO IS NULL`. Si da 4, es esto.

Si en lugar de `COALESCE` usás `x / NULLIF(y,0)` dentro de la cadena, pasa lo mismo cuando `y = 0`.

Conviene comparar siempre las filas declaradas con las impresas. Si el archivo se usa para algo, sin esas 4 filas está incompleto.

## Pedido 2

Casi seguro que no está vacío. Que el LEFT JOIN no devuelva ni una coincidencia suele indicar que **la clave del cruce no es la correcta**, no que falten datos.

Causas probables, en orden de sospecha:

1. **`CHAR(n)` con relleno.** Si `PRODUCTOID` es `CHAR(20)`, tiene espacios al final. Compararlo con el código del export da 0 coincidencias y no tira error. Cruzá contra la columna de código con `TRIM`.
2. **`PRODUCTOID` no es el código del export.** Puede ser un id interno distinto del código que ves en el informe. Revisá el encabezado de cada lado y cruzá por nombre de columna, no por posición.
3. **Ceros a la izquierda o formato.** Un código leído como número o en notación científica pierde ceros o dígitos. Cargalo como texto.

**Antes de mirar el resultado:**

- Contá las coincidencias del join: `COUNT(*)` de las filas donde la tabla de productos no es NULL.
- Contá las filas del maestro de productos. Si tiene filas, no está vacío.
- Mirá unos cuantos valores de cada lado, con su largo, para ver la diferencia.

Hay otra posibilidad: que el producto sí cruce pero el campo de proveedor esté vacío o en `0` para todos. En ese caso hay que ver si es NULL o un cero guardado, porque cambia el detector (`IS NULL` frente a `= 0`). Es un campo que probablemente nadie carga. Si la tabla tiene muchos cruces y el proveedor sigue vacío, es un campo muerto, no un maestro vacío.

Y si el ERP maneja varias razones sociales, confirmá que no estás filtrando una empresa que no tiene esos datos.

## Pedido 3

Un `LEFT JOIN` devuelve todas las filas de la tabla izquierda y, de la derecha, solo las que coinciden. Donde no hay coincidencia, las columnas de la derecha salen NULL.

```sql
SELECT a.id, a.nombre, b.valor
FROM tabla_a a
LEFT JOIN tabla_b b
  ON b.a_id = a.id;
```

Ejemplo con clientes y pedidos:

```sql
SELECT c.id, c.nombre, p.id AS pedido_id
FROM clientes c
LEFT JOIN pedidos p
  ON p.cliente_id = c.id;
```

Todos los clientes aparecen, tengan pedidos o no.

Para encontrar los que no tienen coincidencia, agregá `WHERE p.id IS NULL`.

Si ponés una condición sobre la tabla derecha en el `WHERE`, el `LEFT JOIN` se comporta como un `INNER JOIN`. Para filtrar la derecha sin perder filas de la izquierda, ponela en el `ON`:

```sql
LEFT JOIN pedidos p
  ON p.cliente_id = c.id AND p.estado = 'ACTIVO'
```
