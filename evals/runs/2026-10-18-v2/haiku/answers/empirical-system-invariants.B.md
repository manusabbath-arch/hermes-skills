## Pedido 1

Lo verificaría con queries contra producción, no leyendo el código ni con el "corre sin errores", que no prueba nada. Supuesto: el pipeline escribe en una tabla de Postgres y hay una fecha de deploy conocida.

1. Listar los campos que el pipeline debe poblar, sobre todo los que consume el paso siguiente o el guard.
2. Para cada campo, contar sobre las filas posteriores al último deploy, usando una conexión nueva:

   SELECT count(*) AS total, count(campo) AS no_nulos, count(*) FILTER (WHERE campo IS NULL) AS nulos FROM tabla WHERE created_at >= '<fecha_deploy>';

3. Si el campo tiene defaults (0, '' o similares), mirar también la distribución de valores: SELECT campo, count(*) FROM tabla GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
4. Confirmar en el código que existe una escritura para ese campo. Si el campo está en el esquema pero nada lo asigna, es un eslabón ROJO (transformación o enriquecimiento).
5. Convertir cada query en un check del guard, con valor esperado contra valor real, y agregar un test de frontera que verifique que el fixture realmente ejercita el caso.

## Pedido 2

No lo resolvería silenciando el check ni subiendo el umbral. Primero hay que decidir si 0 es un dato legítimo para ese campo. Eso se declara por campo: "NULL = defecto" y "0 = medición válida" son cosas distintas.

Si el 0 es legítimo:
1. Cambiar la condición: el campo falla solo si es NULL en filas posteriores al deploy, no si vale 0.
2. Verificar con una query que los ceros son mediciones reales y no un default del writer (por ejemplo COALESCE(x, 0)).
3. Agregar el test de frontera: un fixture con un 0 real que debe pasar y uno con NULL que debe fallar.

Supuesto: no tengo el código del guard ni el contrato del campo, así que el cambio exacto depende de eso.

## Pedido 3

No lo haría tal cual. Un try/except que traga el error convierte el guard en uno que nunca alerta, y eso es justo lo que hay que evitar en un check de invariantes.

Lo que haría:
- Capturar la excepción por check, no alrededor de todo el ciclo, y registrar el eslabón que falló, el error y el valor esperado contra el real.
- Marcar ese check como ROJO en el fichero de estado y notificar.
- Seguir con los demás checks, para que un fallo no corte el ciclo.
- Terminar con exit 1 si cualquier check quedó en ROJO.

Así el ciclo no se rompe a mitad de camino, pero el fallo queda visible. Si un check falla por un error de código o de infraestructura, lo correcto es arreglar ese error, no esconderlo.

## Pedido 4

Lo trataría como un defecto de carga hasta demostrar lo contrario. Que las 4.548 filas tengan exactamente 0 se parece más a un valor por defecto (COALESCE, inicialización) que a una medición real.

Verificaría:
1. Conteo por categoría: SELECT count(*) FILTER (WHERE margen IS NULL) AS nulos, count(*) FILTER (WHERE margen = 0) AS ceros, count(*) FILTER (WHERE margen <> 0) AS no_cero FROM tabla;
2. En el código de escritura, si el campo se asigna y con qué valor por defecto.
3. Desde qué fecha las filas tienen 0, para cruzarlo con los deploys.

Si hay NULLs donde debería haber valores, el dato no se está cargando. Si el writer asigna 0 a propósito y la fuente lo confirma, entonces 0 es un dato válido y el contrato debe declararlo así, aunque el 100% de ceros siga siendo sospechoso y convenga revisarlo con la fuente.

Supuesto: no tengo acceso a la base ni al código.

## Pedido 5

No está bien. Loguear solo cuando N > 0 hace que "cero procesados" y "el job no corrió" sean indistinguibles. La ausencia de log no informa nada, y eso es un silencio traicionero.

Cambios que haría:
- Loguear siempre, también con N = 0: "procesados 0".
- Guardar el resultado de cada ciclo (fecha, N, estado) en un fichero o tabla, no solo en logs que rotan.
- Agregar un check de que el job corrió: si el último registro tiene más de X horas, ROJO.

Antes de cambiar nada, verificaría si anoche corrió, con el estado del timer o cron y el log completo de esa ejecución. Si corrió y procesó 0, el problema es el diseño del log. Si no corrió, el problema es el scheduling.

## Pedido 6

Con ALTER TABLE:

ALTER TABLE nombre_tabla ADD COLUMN nombre_columna tipo;

Si necesita default: ALTER TABLE nombre_tabla ADD COLUMN nombre_columna tipo DEFAULT valor; desde Postgres 11, un default constante no reescribe la tabla.

Si necesita NOT NULL, falla cuando la tabla ya tiene filas sin default. La forma segura es agregar la columna nullable, hacer el backfill y luego ALTER COLUMN ... SET NOT NULL.

Para campos medidos, evitaría DEFAULT 0: esconde las escrituras que faltan, que es justo lo que se quiere detectar. Mejor dejarla en NULL y declarar en el contrato que NULL es defecto, con una query de producción que demuestre que la columna se pobló.
