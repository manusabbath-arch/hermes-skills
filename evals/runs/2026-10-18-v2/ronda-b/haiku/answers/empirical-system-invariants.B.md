## Pedido 1

Lo verificaría con una query de producción sobre filas posteriores al último deploy, no con el "corre sin errores". Un pipeline puede terminar bien y dejar campos vacíos.

Pasos:

1. Listar, para cada etapa, la etapa fuente, la etapa consumidora y el campo prometido.
2. Para cada campo consumido, contar filas no NULL y valores plausibles en filas nuevas, por ejemplo `SELECT COUNT(*) AS total, COUNT(campo) AS no_nulos FROM tabla WHERE creado_at >= '<fecha_deploy>'`.
3. Marcar ROJO cualquier campo que esté NULL en todas las filas posteriores al deploy, o que tenga 0 filas no NULL de N.
4. Repetir la chequeo durante varias horas o ciclos, no solo una vez, porque una reconexión puede hacer que todo se vea sano por 1 o 2 minutos.

Si un campo no tiene ningún código que lo escriba, es defecto y no dato legítimo. Eso se registra en el contrato de la etapa correspondiente.

## Pedido 2

Esto es un problema de semántica NULL frente a 0. El guard trata 0 como fallo, pero el contrato del campo no declara que 0 es un valor medido legítimo.

Lo que haría:

1. Revisar el contrato de ese campo y declarar explícitamente si "campo ausente" es defecto (NULL a corregir) o si 0 es un dato medido válido.
2. Para un campo donde 0 es legítimo, cambiar la condición para que solo marque ROJO el NULL, y que el 0 pase como verde.
3. Mantener un gemelo de frontera: un test con un fixture que tenga 0 y otro con NULL, para confirmar que el check distingue los dos casos.

No cambiaría el umbral a ciegas ni lo deshabilitaría. Si se apaga el check, se pierde la detección del caso real de campo nunca escrito.

## Pedido 3

No agregaría un try/except que silencie el check. Un guard de invariantes no debe tragarse excepciones: eso convierte un fallo en verde falso.

Lo que haría en su lugar:

1. Capturar la excepción, loguear el eslabón que falló con el valor esperado y el real, y dejar el ciclo en ROJO.
2. Persistir el estado en un fichero y notificar, de modo que el fallo quede visible en el ciclo.
3. Dejar que el script termine con exit 1 para que el timer o cron lo reporte.

Si el objetivo es que el ciclo de datos no se corte por un error del guard, eso se resuelve separando los pasos: el pipeline sigue, y el guard reporta ROJO con detalle. No se usa `except: pass` ni `|| true`.

No hay código adjunto en este pedido, así que describo el cambio sin editar archivos.

## Pedido 4

Con 0 en las 4.548 filas, es sospechoso y no lo tomaría como dato legítimo sin verificar. Un valor de margen idéntico en todas las filas indica casi siempre que el campo nunca se cargó.

Supuesto: la tabla no tiene un contrato que declare si margen puede valer 0.

Lo que verificaría:

1. Confirmar que el código que escribe margen existe y se ejecuta, con una query del tipo `SELECT COUNT(*) FILTER (WHERE margen IS NOT NULL AND margen <> 0) FROM tabla`.
2. Revisar si margen depende de una fuente externa o de una transformación que no está conectada.
3. Si el campo fue diseñado y nunca conectado, es defecto de enriquecimiento y debe quedar ROJO hasta que se pueble.

Si después se confirma que el margen real es 0 en todas las operaciones, se declara en el contrato como valor medido y el check pasa.

## Pedido 5

No está bien. Un job que loguea solo cuando N > 0 hace que "no logueó nada" sea indistinguible de "no corrió" o "falló antes de procesar".

Lo que haría:

1. Loguear siempre, incluso con N = 0, por ejemplo "procesados 0", para que la ausencia de log sea una señal.
2. Verificar si el job corrió anoche revisando el log de ejecución del timer o cron, y el fichero de estado si existe.
3. Si el job no corrió, el problema es de ingesta o de scheduling, no de datos. Si corrió y procesó 0 registros, hay que revisar si la fuente trajo datos frescos o solo datos stale.

Supuesto: no tengo acceso al log de anoche, así que lo dejo como pregunta a verificar.

## Pedido 6

Sintaxis básica en Postgres:

```sql
ALTER TABLE nombre_tabla ADD COLUMN nombre_columna tipo;
```

Si la columna debe tener valor por defecto o no admitir NULL, se agrega así:

```sql
ALTER TABLE nombre_tabla ADD COLUMN nombre_columna tipo DEFAULT valor NOT NULL;
```

Ojo: si la tabla ya tiene filas y pones NOT NULL sin DEFAULT, el comando falla. Si la columna va a ser consumida por el pipeline, conviene que el contrato del campo declare si NULL es defecto o dato legítimo.
