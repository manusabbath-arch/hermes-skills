## Pedido 1

Que el pipeline corra sin errores no dice nada sobre si los datos salen completos. Hay que medir el contenido de la salida, no la ejecución.

Qué haría:
1. Perfilar cada tabla de salida, campo por campo: porcentaje de NULL, de strings vacíos, de ceros, de valores por defecto, cantidad de valores distintos y mín/máx. Un campo con un solo valor distinto en todas las filas es el sospechoso típico.
2. Mirar la serie temporal de ese perfil por día. Un campo que nunca se llenó se ve plano desde el primer día. Uno que se rompió después muestra un quiebre.
3. Rastrear cada campo sospechoso hasta su origen: si la fuente lo trae, si la transformación lo mapea (nombre de columna mal escrito, join que no matchea, `.get()` con default) y si la carga lo escribe.
4. Comparar con una fuente independiente, por ejemplo una muestra manual de 20 filas contra el sistema de origen.
5. Dejar el chequeo como parte permanente: una consulta o test que alerte cuando un campo que debería variar tenga un solo valor distinto o más de X% de nulos.

Supuesto: es un pipeline batch que escribe a una base SQL. Con eso, el perfil es una consulta de `COUNT(*)`, `COUNT(campo)`, `COUNT(DISTINCT campo)` y `SUM(CASE WHEN campo = 0 ...)` por columna. Cuando tengas los resultados puedo ayudarte a interpretarlos.

## Pedido 2

Un guard que da ROJO todos los días por algo legítimo es ruido, y el ruido enseña a ignorar las alarmas, así que conviene arreglarlo pronto. No lo silenciaría ni lo bajaría de severidad en general.

Supuesto: el guard dice algo como "campo X vale 0, debería ser distinto de 0".

Opciones, de mejor a peor:
1. Precisar la invariante. Lo que se quiere detectar casi nunca es "vale 0" sino "no se cargó". Si el 0 es un valor válido, distinguilo de la ausencia: usá NULL o un indicador explícito de "no informado", y que el guard falle por NULL, no por 0.
2. Condicionar la regla. Si el 0 es legítimo solo en ciertos casos (cierto tipo de registro, cierto estado), validá solo sobre el subconjunto donde no debería ser 0. Ejemplo: "ningún registro de tipo A tiene 0".
3. Cambiar el umbral. Si lo anormal es que todas las filas valgan 0, alertá por proporción (por ejemplo, más de 95% en 0) o por variación respecto de la semana anterior, no por la mera presencia.
4. Allowlist explícita y documentada, con motivo y fecha de revisión. Es lo último que haría, porque se pudre.

Después de cambiar la regla, probala con un caso donde el campo realmente no se cargó y verificá que sigue dando ROJO. Si no, arreglaste el ruido pero perdiste la detección.

## Pedido 3

Lo puedo hacer, pero hay una trampa. Un `try/except` que traga el error convierte "el check falló" en "el check pasó", y eso es peor que el ciclo caído: nadie se entera de que el guard dejó de proteger.

Haría esto:

```python
import logging
log = logging.getLogger(__name__)

def run_cycle():
    ...
    try:
        resultado = check_invariantes(datos)
    except Exception:
        log.exception("check_invariantes FALLÓ (no es lo mismo que pasar)")
        notificar_alerta("Guard de invariantes no pudo ejecutarse")
        resultado = ESTADO_NO_EVALUADO
    ...
```

Puntos clave:
- Capturar `Exception`, no un `except:` pelado, para no atrapar `KeyboardInterrupt` ni `SystemExit`.
- El fallo del check es un estado distinto de VERDE y de ROJO: "no evaluado". Que se vea en el reporte y dispare una alerta.
- Loguear el traceback completo con `log.exception`.
- Contar los fallos consecutivos. Si el check falla N ciclos seguidos, escalar o frenar el ciclo.
- Si el ciclo no puede continuar de forma segura sin la validación (por ejemplo, porque escribe datos que el check protege), mejor que falle.

Sin archivos a la vista, adapto los nombres (`check_invariantes`, `notificar_alerta`) a tu código real.

## Pedido 4

No se puede saber solo mirando el valor. Un 0 en las 4.548 filas es compatible con las dos cosas, pero que sea uniforme en toda la tabla es una señal fuerte de que falta cargarlo. Un margen real casi nunca es idéntico en miles de filas.

Para decidir:
1. Preguntar el significado de negocio: ¿puede el margen ser exactamente 0 para todos los productos o clientes? Casi seguro que no.
2. Ver si el campo es calculable. Si `margen = precio - costo` (o similar), recalculalo desde los campos de origen y compará. Si da valores distintos de 0, el 0 es un valor por defecto.
3. Revisar el origen: si la fuente trae el campo con valores y la tabla lo tiene en 0, el problema está en la transformación o la carga. Mirá si el esquema tiene `DEFAULT 0` o `NOT NULL DEFAULT 0` en la columna.
4. Buscar una época anterior o una tabla anterior donde el campo tuviera valores variables. Si la hubo, es una regresión.

Mi lectura: es muy probable que falte cargarlo, y que el 0 sea un default que oculta la ausencia. Si se confirma, conviene cambiar la columna a permitir NULL, así "no cargado" y "margen cero" dejan de confundirse, y agregar un chequeo de variabilidad para detectarlo la próxima vez.

## Pedido 5

No necesariamente. Que no haya log significa una de dos cosas, y con ese diseño no se pueden distinguir:
- El job corrió y N fue 0 (no había nada para procesar).
- El job no corrió, falló antes de llegar al log, o se colgó.

Como el log solo aparece cuando N > 0, el silencio es ambiguo. Es una trampa clásica: la ausencia de señal se lee como "todo bien".

Qué haría:
1. Verificar ahora si el job corrió: historial del scheduler (cron, systemd, Airflow), código de salida, duración y última ejecución. Eso responde si anoche pasó algo.
2. Cambiar el logueo para que loguee siempre, incluso con 0: `procesados 0`. Además, un "inicio" y un "fin" con duración.
3. Idealmente, agregar un heartbeat o latido: que el job registre en algún lado su última corrida exitosa, y una alerta si pasan más de X horas sin latido (dead man's switch).
4. Si 0 procesados es anormal para tu negocio un día normal, que 0 genere una advertencia.

Supuesto: es un job de cron o similar, sin alerta de ausencia. Si el scheduler confirma que corrió y terminó bien, probablemente estuvo bien. Pero confirmalo en lugar de inferirlo del log.

## Pedido 6

Con `ALTER TABLE ... ADD COLUMN`:

```sql
ALTER TABLE mi_tabla ADD COLUMN nueva_columna tipo;
```

Ejemplos:

```sql
-- columna simple, permite NULL
ALTER TABLE clientes ADD COLUMN telefono text;

-- con valor por defecto y NOT NULL
ALTER TABLE clientes ADD COLUMN activo boolean NOT NULL DEFAULT true;

-- solo si no existe
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS pais text;
```

Notas:
- Desde Postgres 11, agregar una columna con `DEFAULT` constante es rápido y no reescribe la tabla. En versiones anteriores sí la reescribe y puede bloquear por un buen rato en tablas grandes.
- Si agregás `NOT NULL` sin `DEFAULT` a una tabla con filas, falla. Primero agregá la columna como nullable, rellenala y después `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL`.
- El comando toma un lock exclusivo breve sobre la tabla; en producción con mucho tráfico conviene ejecutarlo en un momento tranquilo.
- Si usás migraciones (Alembic, Flyway, Rails, etc.), ponelo en una migración en vez de ejecutarlo a mano.
