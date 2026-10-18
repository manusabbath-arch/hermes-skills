## Pedido 1

"Corre sin errores" no prueba que mida lo que dice. Lo verificaría con contratos de datos por campo:

1. **Mapear el linaje:** para cada etapa, anotar etapa fuente → etapa consumidora → campo prometido. Así sabés qué campos *deberían* llenarse y quién los usa.
2. **Medir la población real** en filas posteriores al último deploy, no en toda la historia:
   ```sql
   SELECT count(*) AS total,
          count(campo_x) AS no_null,
          count(*) FILTER (WHERE campo_x = 0) AS ceros
   FROM tabla WHERE created_at > '<fecha_deploy>';
   ```
   `no_null = 0` sobre N filas = campo diseñado y nunca escrito: es un defecto, no un dato.
3. **Buscar el escritor:** para cada campo vacío, confirmar que existe código que lo asigna. Ojo con wiring fantasma (`getattr(obj, "x", None)` donde nadie setea `x`) y getters que tragan excepciones y devuelven `[]`.
4. **Leer con conexión nueva**, no la del pool, para no ver transacciones propias sin commit.
5. **Convertirlo en guard por ciclo:** cada campo con su condición (ej. "≥95% no-NULL en filas post-deploy"), corrido por cron/systemd. Si algún contrato falla, ciclo ROJO con eslabón + esperado vs real, persistido a un archivo de estado y con notificación (no solo en logs que rotan).
6. **Declarar NULL ≠ 0 por campo:** decidir si "ausente" es defecto o si 0 es un valor medido legítimo.

Supuesto: los datos están en una base SQL consultable. Si no, lo mismo con los logs de producción.

## Pedido 2

El problema es el contrato, no el dato: está tratando 0 como fallo. Eso genera fatiga de alertas y termina con todos ignorando el ROJO, incluido el día que sea real.

Arreglo:

1. **Declarar NULL ≠ 0 para ese campo** en el contrato: `NULL` = defecto (no se escribió), `0` = valor medido legítimo.
2. **Cambiar la condición** de "valor > 0" (o "truthy") a "valor IS NOT NULL". Revisá el código del check: un `if not valor:` en Python trata 0 y None igual; tiene que ser `if valor is None:`.
3. **Si querés seguir vigilando los ceros**, que no sea un ROJO por fila: por ejemplo, alertar solo si el 100% de las filas post-deploy es 0 (señal de que se escribe un default en vez de una medición).
4. **Agregar un test de frontera:** un fixture con 0 legítimo debe dar VERDE y uno con NULL debe dar ROJO. Si no, el check pasa o falla por accidente.

No lo silenciaría ni le bajaría la severidad al guard entero; se corrige la semántica de ese campo y nada más.

## Pedido 3

No lo haría así: un guard de invariantes que traga sus propias fallas deja de servir. `try/except: pass` (o loguear y seguir) convierte un ROJO en silencio, que es justamente lo que el guard tiene que evitar.

Lo que sí haría, según qué te preocupe:

- **Si el problema es que el guard frena el ciclo de producción:** separarlo. El guard corre como proceso propio (cron/systemd) después del ciclo, persiste el resultado en un archivo de estado y notifica en ROJO. El ciclo de negocio no depende de él, pero la falla queda visible.
- **Si el check en sí revienta (excepción, no ROJO):** eso también es ROJO. Capturar solo para *reportar* el eslabón y el error, y salir con código distinto de 0:
  ```python
  try:
      resultado = check(contrato)
  except Exception as e:
      log.error("ROJO eslabón=%s error=%r", contrato.nombre, e)
      sys.exit(1)
  ```
- **Si recién lo estás introduciendo:** un kill switch (flag OFF) para que corra en modo monitor sin bloquear deploys mientras se estabiliza, en vez de esconder el error.

Nada de `|| true`, `continue-on-error` ni `except: pass` en ese camino.

## Pedido 4

Con 4.548 de 4.548 en 0, lo más probable es que **falte cargarlo**: un margen real casi nunca da exactamente 0 en todas las filas. Ese patrón suele significar un default de columna (`DEFAULT 0`) o un `coalesce(x, 0)` escribiendo algo donde nunca hubo medición.

Cómo confirmarlo:

1. **Buscar el escritor:** ¿hay código que calcule y asigne `margen`? Si no existe o lee un atributo que nadie setea (`getattr(..., 0)`), es un campo fantasma.
2. **Ver el esquema:** si la columna tiene `DEFAULT 0` o `NOT NULL DEFAULT 0`, el 0 no distingue "medido" de "ausente".
3. **Recalcular a mano unas filas** con los insumos (precio, costo). Si da distinto de 0, es un defecto.
4. **Revisar filas antes y después de deploys** por si en algún momento se llenó.

Recomendación: declarar que para `margen` el ausente es `NULL` (no 0), cambiar el default, conectar el cálculo y agregar un check por ciclo: ROJO si el 100% de las filas post-deploy es NULL o 0. Mientras tanto, no usaría ese campo para decidir nada.

## Pedido 5

No se puede saber, y ese es el problema. Con ese log, "no hubo nada que procesar" y "el job no corrió / murió antes / falló en silencio" se ven idénticos.

Para saber de anoche:

- Revisar si el job arrancó: `systemctl status` / `journalctl -u <unidad>` o el log del cron, el exit code y la hora.
- Mirar la fuente: ¿había registros pendientes para procesar? Si había y N = 0, hay un problema.

Para que no vuelva a pasar:

1. **Loguear siempre**, incluido `procesados 0`, con timestamp de inicio y de fin.
2. **Persistir un heartbeat** (archivo de estado o fila en DB con última corrida, N y estado) en vez de depender de logs que rotan.
3. **Agregar un check externo:** ROJO si no hay heartbeat en las últimas ~25 h, o si N = 0 cuando la fuente tenía pendientes.
4. Verificar que errores internos no queden tragados (getters que devuelven `[]` ante una excepción dan N = 0 "legítimo").

## Pedido 6

```sql
ALTER TABLE nombre_tabla ADD COLUMN nombre_columna tipo;
```

Ejemplos:

```sql
ALTER TABLE clientes ADD COLUMN telefono text;
ALTER TABLE pedidos ADD COLUMN descuento numeric(10,2) DEFAULT 0 NOT NULL;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS notas text;
```

Notas:
- Desde Postgres 11, agregar una columna con `DEFAULT` constante no reescribe la tabla: es rápido incluso en tablas grandes.
- Si la columna puede quedar sin valor, conviene dejarla nullable (sin `DEFAULT 0`) para distinguir "no cargado" de "cero".
