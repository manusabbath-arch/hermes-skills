## Pedido 1

"Corre sin errores" solo prueba que el código no explotó, no que los campos se llenen. Hay que medirlo directamente sobre los datos de salida, no sobre el estado del job.

Supuestos: el pipeline escribe a una tabla o archivos con un esquema conocido, y tenemos al menos unas semanas de historial.

Qué haría:
1. **Perfilar cada campo** sobre las últimas N corridas (por ejemplo 30 días): porcentaje de nulos, de vacíos, de valores por defecto o centinela ("", "N/A", 0, -1, fecha epoch) y cantidad de valores distintos. Un campo con 100% nulo, o con un único valor distinto en todas las corridas, es sospechoso de no llenarse nunca.
2. **Distinguir "nunca se llena" de "se llena a veces"**: graficar el porcentaje de llenado por día. Un salto a 0% tras un deploy sugiere una regresión, y 0% constante desde siempre sugiere un campo muerto.
3. **Rastrear hacia atrás**: para cada campo sospechoso, buscar en el código dónde se asigna. Si ninguna rama lo escribe, o la fuente upstream no lo trae, ya tenemos la causa. Confirmar con una muestra de registros crudos de origen.
4. **Dejar un chequeo permanente**: una aserción de completitud por campo, con umbral esperado (por ejemplo ">= 95% no nulo"), que falle o alerte. Así dejamos de depender de la sospecha.

Si no tengo acceso a los datos, empiezo escribiendo la consulta de perfilado y te la paso para correrla.

## Pedido 2

Un guard que da ROJO todos los días por un valor legítimo es un falso positivo, y eso es peor que no tener guard: entrena a todos a ignorar el rojo, y cuando salte uno real nadie lo mira.

Supuesto: el invariante hoy es algo como `campo > 0` o `campo` truthy, y por eso el 0 lo viola.

Qué haría:
1. **Corregir la regla, no silenciar el guard.** Si 0 es válido, el invariante real es "el campo está presente y es numérico (y >= 0)", no "es truthy". Cambiar `if not campo` por `campo is None` o `campo < 0`. Este es el error clásico de confundir 0 con "faltante".
2. **Separar "ausente" de "cero"**: el guard debe distinguir null/no informado de un cero informado. Si hace falta, agregar un flag explícito de "informado".
3. **Documentar por qué 0 es legítimo** en un comentario o en la definición del invariante, para que nadie lo "arregle" de vuelta.
4. **Validar el cambio en ambos sentidos**: que el caso actual pase a VERDE, y que un caso realmente malo (null, negativo) siga dando ROJO. Si no probamos que todavía puede fallar, solo lo apagamos.

No lo excluiría del guard entero ni subiría el umbral a ciegas, porque perderíamos cobertura sobre ese campo.

## Pedido 3

Lo hago, pero con una condición: el except no puede tragarse el fallo en silencio, porque entonces un check roto se ve igual que un check que pasó. Es el mismo problema del Pedido 1 (verde que no significa nada).

Supuestos: Python, y una función `check_invariants()` llamada desde el ciclo principal.

```python
import logging
log = logging.getLogger(__name__)

try:
    result = check_invariants(data)
except Exception:
    log.exception("check_invariants falló (error del check, no violación)")
    result = InvariantResult(status="ERROR")  # estado propio, ni VERDE ni ROJO
    alert("Invariant guard no pudo ejecutarse")
```

Puntos clave:
- Captura `Exception`, nunca `BaseException` ni un `except:` pelado, para no atrapar Ctrl+C ni SystemExit.
- Un estado **ERROR/UNKNOWN distinto de VERDE**: si falla, el reporte debe decir "no verificado", no "todo bien".
- Se loguea el traceback completo y se avisa por el canal de alertas.
- El ciclo continúa, que es lo que pediste, pero queda visible que ese día no hubo verificación.
- Si el check falla varios días seguidos, escalar la alerta.

Si preferís un comportamiento distinto (por ejemplo, que ERROR cuente como ROJO), es un cambio de una línea.
