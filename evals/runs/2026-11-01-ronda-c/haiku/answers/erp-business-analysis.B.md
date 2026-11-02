## Pedido 1

No se cortó el archivo. Lo más probable es que DB2 descartó las filas en la consulta, no en la exportación.

En DB2, si una columna es NULL dentro de `||`, toda la concatenación da NULL. Si la fila entera se arma como una cadena, esa fila desaparece de la salida sin error. El "20 record(s) selected" cuenta lo que la consulta devolvió antes de que el cliente imprimiera, así que las 4 filas que faltan tienen algún NULL en NOMBRE, RUC o TELEFONO.

Para confirmarlo, contá las filas con NULL en alguna de esas columnas (debería dar 4):

```sql
SELECT COUNT(*) FROM tu_tabla
WHERE NOMBRE IS NULL OR RUC IS NULL OR TELEFONO IS NULL;
```

Para corregirlo, envolvé cada columna que admite NULL con `COALESCE`. No cambia ningún valor que no sea NULL:

```sql
SELECT COALESCE(NOMBRE, '') || ';' || COALESCE(RUC, '') || ';' || COALESCE(TELEFONO, '') AS LINEA
FROM tu_tabla;
```

Después de correrla, las líneas impresas deberían coincidir con los 20 registros. Si no coinciden, revisá también si algún campo tiene saltos de línea, porque eso también cambia el conteo de líneas del archivo.

## Pedido 2

Un LEFT JOIN sin ninguna coincidencia casi siempre indica que la clave está mal, no que la tabla esté vacía. Antes de concluir que el maestro no tiene proveedores, verificá tres cosas:

1. **¿La tabla de productos tiene filas?**
   ```sql
   SELECT COUNT(*) FROM productos;
   ```
   Si da 0, el maestro está vacío. Si da más de 0, el problema está en el join.

2. **¿Las claves coinciden?** En DB2, un `CHAR(n)` se rellena con espacios. Si `PRODUCTOID` es `CHAR(20)`, `'ABC'` no coincide con `'ABC               '` y el join no da error, solo no encuentra nada. Comparalas recortadas:
   ```sql
   SELECT COUNT(*)
   FROM lineas_venta v
   JOIN productos p ON TRIM(v.PRODUCTOID) = TRIM(p.CODIGO);
   ```
   Si este `COUNT` es mayor que 0, el LEFT JOIN estaba bien y solo faltaba el `TRIM`.

3. **¿El proveedor está en esa tabla?** Puede estar en otra tabla, enlazada por un código de proveedor. Revisá el catálogo de columnas (por ejemplo, buscando columnas con "PROV" en el nombre) antes de asumir que la columna no existe.

Si el `COUNT` con `TRIM` da 0 y la tabla de productos tiene filas, mirá algunos valores de cada lado lado a lado. Las diferencias suelen ser ceros a la izquierda, mayúsculas o prefijos.

## Pedido 3

Un LEFT JOIN conserva todas las filas de la tabla de la izquierda y completa con NULL las columnas de la derecha cuando no hay coincidencia:

```sql
SELECT a.id, a.nombre, b.dato
FROM tabla_a AS a
LEFT JOIN tabla_b AS b
  ON b.a_id = a.id;
```

Si querés solo las filas de A que no tienen coincidencia en B, filtrá por NULL:

```sql
SELECT a.id, a.nombre
FROM tabla_a AS a
LEFT JOIN tabla_b AS b
  ON b.a_id = a.id
WHERE b.a_id IS NULL;
```
