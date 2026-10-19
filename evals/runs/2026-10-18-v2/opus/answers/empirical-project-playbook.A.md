## Pedido 1

Todavía no. Un rango tan específico (0.30–0.42) encontrado mirando los datos es un candidato típico a sobreajuste: si probaste muchos rangos, alguno iba a "ganar" por azar.

Antes de activarla haría esto:

1. **Validación fuera de muestra**: fijá el rango con datos viejos y probalo en un período posterior que no usaste para encontrarlo (walk-forward).
2. **Tamaño de muestra y significancia**: ¿cuántos trades caen en ese rango? Con pocas decenas el resultado puede ser ruido. Calculá el intervalo de confianza del retorno medio, no solo el promedio.
3. **Corrección por búsqueda múltiple**: si probaste 20 rangos, el umbral de significancia tiene que ser más estricto (Bonferroni o similar).
4. **Robustez**: ¿sigue ganando con 0.28–0.44 o 0.32–0.40? Si se cae al mover un poco los bordes, es frágil.
5. **Costos reales**: incluí comisiones, spread y slippage.
6. **Hipótesis causal**: ¿hay una razón de por qué ese rango debería funcionar?

Si pasa todo eso, la activaría con capital chico (paper trading o una fracción del tamaño) y con criterios de corte definidos de antemano: cuánta pérdida o cuánta divergencia respecto al backtest te hace apagarla.

## Pedido 2

Que esté deployado y sin errores solo prueba que no rompe, no que funciona. Antes de cerrarlo verificaría:

- **Que se usa**: ¿hay tráfico o eventos del feature en producción? "Sin errores" puede significar que nadie lo ejecuta (por ejemplo, un feature flag apagado o una ruta a la que no se llega).
- **Que hace lo que tiene que hacer**: un smoke test end-to-end en producción y que el output sea correcto, no solo que no tire excepciones. Los errores silenciosos (datos mal calculados, fallbacks que se tragan excepciones) no aparecen en los logs.
- **Criterios de aceptación**: repasá los del ticket uno por uno.
- **Métrica de éxito**: si el feature tenía un objetivo (más conversión, menos latencia), dejá definido cuándo y cómo lo vas a medir.
- **Observabilidad**: que haya logs, métricas o alertas para enterarte si se rompe más adelante.

Si todo eso da bien, sí, cerralo. Si la métrica de impacto necesita tiempo, cerrá el ticket técnico y abrí un seguimiento con fecha para revisar el impacto.

## Pedido 3

Si ya está documentado dos veces y vuelve, el README no está funcionando como defensa: la gente no lo lee en el momento en que importa. La solución es pasar de documentación a algo que se haga cumplir solo.

Lo que haría:

1. **Arreglar la causa raíz**, no solo el síntoma. Revisar por qué los dos fixes anteriores no alcanzaron.
2. **Test de regresión** que reproduzca exactamente el bug y corra en CI. Si vuelve a aparecer, el build falla.
3. **Guardas en el código**: validaciones, asserts, tipos, o un linter/pre-commit hook que detecte el patrón que lo causa.
4. **Hacer imposible el error** si se puede: cambiar la API o la configuración para que el camino equivocado no exista.
5. **Alerta en producción** si el bug tiene un síntoma observable.
6. Dejar el README como contexto, pero enlazado desde el test, no como la única barrera.

También revisaría el historial (git blame) de las dos veces anteriores para ver qué cambio lo reintrodujo; eso suele señalar dónde poner el test.

## Pedido 4

No. Con 40 usuarios por brazo, un +12% casi seguro no es estadísticamente significativo.

Para darte una idea: si la conversión base es del 20%, son unos 8 conversiones contra 9. Una diferencia de 1 conversión es puro ruido. El intervalo de confianza de la diferencia va a ser enorme (fácilmente de −15 a +20 puntos porcentuales).

Lo que haría:

1. **Calcular el tamaño de muestra necesario** antes de seguir. Para detectar un efecto relativo del 12% con base 20%, 80% de potencia y α=0.05, necesitás del orden de varios miles de usuarios por brazo.
2. **Seguir corriendo el test** hasta llegar a ese tamaño, fijado de antemano. No frenarlo cuando "se ve bien" (peeking), porque eso infla los falsos positivos.
3. **Revisar la aleatorización**: que los brazos sean comparables y que no haya bugs de asignación.
4. **Mirar métricas de guarda** (ingresos, retención, errores) además de conversión.

Si necesitás decidir ya, una alternativa es un rollout gradual (10% → 50% → 100%) monitoreando las métricas, pero sabiendo que hoy no tenés evidencia de que el cambio mejore algo.

## Pedido 5

Un success rate tiene que estar entre 0% y 100%, así que −5046% es un bug de cálculo o de datos, no un resultado real. Causas probables:

- **Denominador equivocado o casi cero**: se divide por algo mucho más chico que el total (por ejemplo, solo los fallidos, o un conteo filtrado por otra ventana de tiempo).
- **Numerador negativo**: se calcula como `(total − fallos) / total` y los fallos se cuentan varias veces (por reintentos, joins que duplican filas), entonces fallos > total.
- **Doble multiplicación por 100**: el valor ya viene en porcentaje y el dashboard lo vuelve a multiplicar. −50.46 × 100 = −5046, lo que además sugiere que el número subyacente ya era negativo.
- **Ventanas desalineadas**: numerador y denominador de períodos o fuentes distintos.
- **Overflow o tipos**: enteros con signo que desbordan, o resta de contadores que se resetearon.
- **Nulls o valores centinela** (−1, −999) tratados como datos.

Cómo lo encararía: sacar la query del panel, ver el numerador y el denominador por separado para el mismo período, contar los registros a mano en una muestra chica y buscar duplicados en los joins. Después agregar una validación que alerte si la métrica sale de [0, 100].

## Pedido 6

El p-valor es la probabilidad de observar un resultado tan extremo como el que obtuviste, o más, **suponiendo que la hipótesis nula es cierta** (por ejemplo, que no hay diferencia entre A y B).

Si el p-valor es chico (típicamente < 0.05), los datos serían raros si no hubiera efecto, y por eso rechazás la hipótesis nula.

Lo que **no** es:
- No es la probabilidad de que la hipótesis nula sea verdadera.
- No mide el tamaño ni la importancia del efecto.
- p > 0.05 no prueba que no haya efecto, solo que no alcanzó la evidencia.
