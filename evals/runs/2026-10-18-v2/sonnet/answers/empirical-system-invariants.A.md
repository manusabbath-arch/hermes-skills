## Pedido 1

"Corre sin errores" no prueba que mida lo que dice. Lo verificaría con un contrato de datos por ciclo, empezando por los campos sospechosos.

1. Para cada etapa, listá etapa fuente, etapa consumidora y campo prometido.
2. Para cada campo, escribí la condición que prueba que se pobló. No alcanza con "hay filas": hacen falta valores plausibles en filas posteriores al último deploy.
3. Escribí primero la query de producción que lo demuestra. Por ejemplo, `SELECT count(*) total, count(campo) no_nulos FROM tabla WHERE created_at > '<fecha_deploy>'`.
4. Un campo con 0 no-NULL sobre N filas es un defecto. Casi seguro el código que lo escribe nunca existió o nunca se conectó.
5. Revisá el wiring. Buscá `getattr` con default que nadie asigna y comprobá con `hasattr` sobre la instancia real.
6. Declarale al contrato, por campo, si NULL es defecto o si 0 es un dato legítimo.
7. Corré un guard por ciclo, con cron o systemd. Que falle fuerte (exit 1) y nombre el eslabón con valor esperado vs real. Guardá el resultado en un archivo de estado y no dependas de logs que rotan.
8. Probá el guard con un caso que roce el límite, para que no pase por accidente.

Supuesto: tenés acceso de lectura a la DB. Leé con una conexión nueva, no la del pool.

## Pedido 2

Eso no se arregla silenciando la alerta. Se arregla declarando en el contrato que ese campo trata 0 como dato legítimo.

- Distinguí NULL de 0. NULL significa "nunca se escribió", que es un defecto. 0 significa "se midió y dio cero", que es un dato.
- Cambiá el check de ese campo de `valor != 0` o `valor > 0` a `valor IS NOT NULL` en filas posteriores al deploy.
- Si querés más rigor, agregá una condición de plausibilidad. Por ejemplo, que no sea 0 en todas las filas cuando el negocio dice que debería variar.
- Dejá el resto de los checks en rojo-si-falla. No uses `|| true` ni `except: pass`, y no apagues el guard.
- Agregá un test de frontera: un fixture con 0 legítimo debe dar verde, y uno con NULL debe dar rojo.

Si el campo realmente nunca varía, preguntate si es un dato o si falta cargarlo (ver Pedido 4). El rojo diario por un 0 legítimo es fatiga de alertas. Esa fatiga hace que después ignoren un rojo verdadero.

## Pedido 3

No lo haría como lo pedís. Un `try/except` que traga la falla del check de invariantes es justo el silencio traidor que el guard existe para evitar. Si el check falla y el ciclo sigue como si nada, parece verde sin serlo.

Lo que sí puedo hacer, para que no rompa el ciclo y a la vez no oculte nada:

```python
try:
    resultados = correr_invariantes()
except Exception as e:
    log.error("GUARD ROJO: el check de invariantes falló: %r", e)
    escribir_estado("ROJO", motivo=repr(e))
    notificar(...)
    guard_ok = False   # el ciclo se marca ROJO
```

El ciclo de producción sigue corriendo, pero el resultado queda ROJO, con la causa registrada y una notificación. Nunca `except: pass`, y el exit code final del guard debe ser distinto de 0.

Supuesto: querés aislar el ciclo de producción del guard. Esto lo logra sin perder la señal.

## Pedido 4

Con lo que tengo no se puede saber. Que sean 4.548 de 4.548 filas con 0 es una señal de alarma, pero no una prueba.

Un campo con 0 en todas las filas puede ser un dato real, o puede ser un campo diseñado que nunca se escribió y quedó con el valor por defecto. Hay que mirar esto:

1. **Código:** ¿existe alguna línea que escriba `margen`? Si no, es un defecto.
2. **Plausibilidad:** ¿el negocio esperaría margen distinto de 0 en alguna fila? Si sí, 0 en el 100% es sospechoso.
3. **Esquema:** ¿la columna tiene `DEFAULT 0 NOT NULL`? Eso esconde un "nunca cargado".
4. **Fuente:** ¿en la fuente de origen hay valores distintos de 0?
5. **Filas posteriores al deploy:** ¿hay alguna fila con valor?

Mi recomendación es tratarlo como defecto hasta que se pruebe lo contrario. Si faltaba cargarlo, el valor correcto debería ser NULL, no 0. Declará en el contrato si 0 es legítimo para `margen`.

## Pedido 5

No necesariamente. Con ese log no podés distinguir "no había nada que procesar" de "el job no corrió" o "falló antes de loguear".

Un job que sólo loguea cuando N > 0 hace que el silencio sea ambiguo. Los tres casos se ven igual:
- Corrió y N = 0, que puede ser normal.
- No corrió, por timer caído, cron roto o intérprete inexistente.
- Corrió y falló antes de llegar al log.

Qué haría:
- Loguear siempre, también cuando N = 0 (`procesados 0`), junto con la hora de inicio y de fin.
- Verificar que el job corrió: `journalctl` o el estado del timer, y el exit code.
- Revisar si la ingesta trajo datos frescos o si todo era stale, porque N = 0 puede ser un problema aguas arriba.
- Contrastar con la tabla: ¿hay filas nuevas desde ayer que debían procesarse?

Supuesto: es un job de cron o systemd. Si ayer hubo datos de entrada y N salió 0, está mal. Si no hubo datos, está bien, pero tenés que poder probarlo.

## Pedido 6

Con `ALTER TABLE ... ADD COLUMN`:

```sql
ALTER TABLE mi_tabla ADD COLUMN nueva_columna integer;
```

Con valor por defecto y restricción:

```sql
ALTER TABLE mi_tabla
  ADD COLUMN IF NOT EXISTS activo boolean NOT NULL DEFAULT true;
```

Detalles útiles:
- Sin `DEFAULT`, las filas existentes quedan en NULL.
- Desde Postgres 11, agregar una columna con `DEFAULT` constante es casi instantáneo, porque no reescribe la tabla.
- Si agregás `NOT NULL` sin `DEFAULT` en una tabla con filas, falla. Agregala nullable, rellenala y después hacé `ALTER COLUMN ... SET NOT NULL`.
- En producción conviene usar una migración versionada y probarla antes en staging.
