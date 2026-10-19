## Pedido 1

Que no haya errores solo significa que el código no explotó. No prueba que los datos estén bien. Para verificarlo, mediría la tabla de salida directamente:

1. **Perfil por columna**: para cada campo, contá nulos, vacíos, ceros y valores distintos.
   ```sql
   SELECT COUNT(*) total,
          COUNT(campo) no_nulos,
          COUNT(*) FILTER (WHERE campo = 0 OR campo = '') ceros_o_vacios,
          COUNT(DISTINCT campo) distintos
   FROM tabla;
   ```
   Un campo con 100% de nulos o ceros, o con un único valor distinto, es sospechoso.
2. **Ver la evolución en el tiempo**: hacé el mismo perfil por fecha de carga. Si un campo dejó de llenarse en una fecha puntual, buscá qué cambió ese día (un deploy, la fuente, el esquema).
3. **Rastrear el origen**: para cada campo sospechoso, fijate si la fuente lo trae y si el mapeo lo copia. Muchas veces el campo viene con otro nombre o el código lo descarta en silencio, por ejemplo con un `.get()` que tiene default.
4. **Dejarlo fijo**: agregá chequeos automáticos al final del pipeline, del tipo "el campo X tiene que estar lleno en al menos el N% de las filas", que fallen o alerten de forma visible. Así el problema no vuelve a pasar sin que nadie se entere.

## Pedido 2

Que el guard falle todos los días hace que la gente aprenda a ignorarlo, y entonces deja de servir. Pero no lo apagaría entero. Lo corregiría para ese caso:

1. **Confirmar que el 0 es legítimo**: revisá la fuente o preguntale al dueño del dato. Que el campo "suela" valer 0 no alcanza; tiene que ser un valor real y no un default.
2. **Ajustar la regla de ese campo** en vez de desactivar el guard:
   - Si el 0 es válido pero "nunca debería ser 0 en todas las filas", cambiá el check a "no todo 0" o a "porcentaje de ceros por debajo de X".
   - Si el 0 es válido siempre, sacá el chequeo de "no cero" para ese campo y dejá los otros (no nulo, tipo, rango).
   - Si hace falta, separá "0 cargado" de "no cargado" usando NULL para lo que falta. Así el guard puede verificar nulos en vez de ceros.
3. **Documentar la excepción** junto a la regla: por qué el 0 es válido, quién lo confirmó y la fecha.

Supongo que el guard es configurable por campo. Si no lo es, ese es el cambio que conviene hacer.

## Pedido 3

Lo haría, pero sin tragarme el error. Un `except: pass` vuelve el guard inútil, porque si se rompe nadie se entera. Propuesta:

```python
try:
    resultado = check_invariantes(datos)
except Exception:
    logger.exception("check de invariantes falló al ejecutarse")
    alertar("invariantes: ERROR de ejecución")  # canal visible
    resultado = EstadoCheck.ERROR  # distinto de OK
```

Puntos clave:
- **Distinguir los tres estados**: "el check pasó", "el check detectó violaciones" (ROJO) y "el check no pudo correr" (ERROR). Este último nunca tiene que contar como verde.
- **Atrapar solo la excepción del check**, no el ciclo entero, y loguear con el traceback completo.
- **Alertar** por el mismo canal que el ROJO, o por uno parecido, para que alguien lo vea.
- Si el resto del ciclo depende de que los datos sean válidos, por ejemplo si publica o hace cargas downstream, decidí explícitamente si sigue o no cuando el estado es ERROR. Mi recomendación es no publicar.

Así el ciclo no se corta y el fallo sigue siendo visible.

## Pedido 4

Con solo esa información no se puede saber. Que el 100% de las filas tenga 0 es, de hecho, la señal típica de que el dato falta y no de que es real. Un margen real casi nunca es exactamente 0 en 4.548 filas. Lo verificaría así:

1. **Fuente**: mirá si el sistema de origen tiene margen para esas filas. Si allá hay valores distintos de 0, falta cargarlo.
2. **Código de carga**: buscá cómo se llena `margen`. Fijate si existe un `DEFAULT 0` en la columna, un `COALESCE(..., 0)`, un `fillna(0)` o un `.get('margen', 0)`. Cualquiera de esos convierte "no vino" en 0.
3. **Historia**: si hay datos de fechas anteriores, revisá si alguna vez tuvo valores distintos de 0 y desde cuándo está todo en 0.
4. **Coherencia**: si existen precio y costo, calculá el margen y comparalo.

Mientras no se confirme, trataría el campo como **no cargado**. No lo usaría en reportes y anotaría la sospecha. A futuro conviene que lo faltante quede como NULL y no como 0, y agregar un chequeo que alerte si un campo numérico tiene 100% de ceros.

## Pedido 5

No se puede saber, y ese es justamente el problema del diseño. Si no hay log, puede ser por cualquiera de estas causas:
- corrió y procesó 0 (lo normal),
- no corrió (falló el cron, el host estaba caído o hubo un problema de permisos),
- arrancó y murió antes de loguear,
- se colgó.

Para saber qué pasó anoche: revisá el log del scheduler (cron, systemd o el orquestador), el código de salida y la hora de inicio y fin. También podés buscar efectos en la base, como timestamps de la última ejecución.

Para que no vuelva a pasar:
- **Loguear siempre**, incluso `procesados 0`, junto con un inicio y un fin explícitos y la duración.
- Registrar un **heartbeat** (última ejecución exitosa) en una tabla o archivo.
- Poner una **alerta por ausencia**: si no hubo una ejecución exitosa en las últimas ~25 h, que avise.

Un silencio tiene que significar algo distinto de "todo bien". Si no, no se puede distinguir de "no corrió".

## Pedido 6

```sql
ALTER TABLE nombre_tabla ADD COLUMN nombre_columna tipo;
```

Ejemplos:
```sql
ALTER TABLE clientes ADD COLUMN email text;
ALTER TABLE ventas ADD COLUMN margen numeric(12,2) DEFAULT 0 NOT NULL;
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS activo boolean DEFAULT true;
```

Notas:
- Desde Postgres 11, agregar una columna con un `DEFAULT` constante es instantáneo y no reescribe la tabla.
- Si después vas a usar el valor para distinguir "no cargado", no le pongas `DEFAULT 0`. Dejala nullable.
