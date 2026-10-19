## Pedido 1

Que el pipeline corra sin errores no dice nada sobre si los campos se llenan. Un job puede terminar bien y escribir NULL o un valor por defecto. Lo verificaría en la base, con datos reales:

1. Medir la tasa de nulos y de valores por defecto de cada columna sobre la tabla completa y sobre la última semana. Supongo Postgres:

```sql
SELECT
  count(*)                                   AS total,
  count(*) FILTER (WHERE campo IS NULL)      AS nulos,
  count(*) FILTER (WHERE campo = 0)          AS ceros,
  count(DISTINCT campo)                      AS distintos
FROM mi_tabla
WHERE created_at >= now() - interval '7 days';
```

2. Repetir para todas las columnas (o generarlo desde `information_schema.columns`). Las que dan 100% nulos o un único valor son sospechosas.
3. Revisar en el código del loader si esa columna se asigna en algún lugar. Una columna que nunca aparece en un `INSERT`/`UPDATE` nunca se llena.
4. Comparar contra la fuente: ¿el origen trae ese dato?

Con eso separo tres casos: el dato no existe en la fuente, el mapeo está roto, o el campo es opcional y nadie lo usa. Después agregaría un check de "tasa de nulos por campo" que falle si supera un umbral.

## Pedido 2

Que un campo en 0 dispare ROJO casi siempre significa que la regla trata el 0 como "faltante". Por ejemplo, `campo > 0` o `campo IS NULL OR campo = 0`. La corrección correcta es cambiar la regla, no silenciarla:

- Si 0 es un valor válido, la regla debe ser `campo IS NOT NULL` y, si hay un rango, `campo >= 0` (o el mínimo que corresponda).
- Si 0 también puede significar "no cargado", hay que distinguirlo en origen. Un 0 que es a veces dato y a veces ausencia no se puede validar con una sola regla.

Antes de cambiar nada confirmaría con qué valores aparece ese campo y en qué casos es 0. Supuesto: el guard es una regla por campo y no una regla agregada.

## Pedido 3

No agregaría un try/except que silencie el check. El guard existe para detectar datos malos, y si falla en silencio el ciclo sigue con datos sin validar y nadie se entera.

Lo que haría es capturar la excepción de forma explícita, registrar el error con traceback, marcar el ciclo como degradado o fallido y disparar una alerta. Si el objetivo es que el ciclo no se corte, decidiría explícitamente si continúa o no, y lo dejaría escrito en el log. Así el ciclo no se rompe sin control y el problema queda visible.

Supuesto: un fallo del propio check (por ejemplo, un error de conexión o de código) es distinto de un resultado ROJO legítimo. Los trataría por separado.

## Pedido 4

Muy probablemente no es un dato. Que `margen` sea 0 en las 4.548 filas indica que el campo nunca se carga. Un margen real nunca vale exactamente 0 en todos los casos.

Verificaría en este orden:

1. Ver si la columna tiene `DEFAULT 0` en el esquema, lo que la llenaría sola.
2. Buscar en el loader la asignación de `margen`, o si se calcula a partir de otros campos que pueden ser nulos.
3. Comparar con la fuente: ¿el origen trae margen?
4. Revisar si hubo un cambio de mapeo en alguna fecha.

Hasta resolverlo, lo trataría como falta de carga y no como un valor válido. Supuesto: no tengo acceso a la tabla, así que esto se basa solo en el patrón descripto.

## Pedido 5

No necesariamente está bien, pero el log actual no permite saberlo. Un log que aparece solo cuando N > 0 hace indistinguibles tres situaciones: el job procesó cero registros, el job no corrió, o el job falló antes de llegar al log.

Lo que haría:

- Loguear siempre el resultado, incluso `procesados 0`, y también un marcador de inicio y otro de fin.
- Revisar el exit code y el registro del scheduler de anoche, para saber si el job corrió y terminó bien.
- Si el job debería procesar algo cada noche, agregar una alerta cuando no hay log de fin dentro de una ventana esperada.

Supuesto: no sé si anoche había datos nuevos. Si no los había, el cero es correcto, pero el log tendría que decirlo.

## Pedido 6

En Postgres se usa `ALTER TABLE`:

```sql
ALTER TABLE mi_tabla
  ADD COLUMN IF NOT EXISTS nuevo_campo integer;
```

Si necesita un valor por defecto y NOT NULL:

```sql
ALTER TABLE mi_tabla
  ADD COLUMN nuevo_campo integer NOT NULL DEFAULT 0;
```

Desde Postgres 11, agregar una columna con un default constante es rápido en tablas grandes. Si la tabla es muy grande y el default no es constante, conviene hacerlo en pasos: agregar la columna nullable, cargar los datos y luego agregar la restricción.

Si el proyecto usa migraciones, la columna debería ir ahí y no como un cambio manual en la base.
