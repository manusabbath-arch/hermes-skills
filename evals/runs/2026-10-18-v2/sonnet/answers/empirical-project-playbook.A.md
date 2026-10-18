## Pedido 1

No la activaría todavía. Un rango de precio (0.30 a 0.42) encontrado mirando los datos es una hipótesis, no un resultado confirmado. Probablemente es un umbral ajustado después de ver los resultados, y eso infla mucho la chance de que sea ruido o sobreajuste.

Supuestos: no sé cuántos trades caen en ese rango, ni si el rango se definió antes o después de mirar los datos.

Qué haría antes de producción:
1. Contar la muestra: cuántas operaciones hay en el rango y cuántas pruebas/rangos se probaron hasta dar con este (comparaciones múltiples).
2. Validar fuera de muestra: definir el rango congelado y probarlo en datos que no se usaron para encontrarlo (walk-forward o un período posterior).
3. Incluir costos reales: comisiones, slippage, liquidez y tamaño de posición.
4. Chequear robustez: ¿sigue ganando con rangos levemente distintos (0.28-0.44)? Si el resultado se cae con pequeños cambios, es frágil.
5. Si pasa, activarla en paper trading o con capital chico y límites de pérdida, con criterios de salida definidos de antemano.

Resumen: prometedora, pero no validada. Primero fuera de muestra, después producción gradual.

## Pedido 2

Todavía no lo cerraría. "Deployado y sin errores" solo dice que no explota; no dice que funcione ni que cumpla su objetivo. La ausencia de errores puede significar también que nadie lo usa, o que los errores no se están registrando.

Supuesto: el feature tenía un objetivo y criterios de aceptación definidos.

Antes de cerrar verificaría:
1. Que se ejecuta en producción de verdad: hay tráfico, el flag está encendido para los usuarios correctos, aparecen eventos/logs del camino feliz.
2. Que produce el resultado esperado: probarlo end to end en producción con un caso real y comparar contra los criterios de aceptación.
3. Que el monitoreo existe: alertas y métricas (uso, latencia, tasa de éxito), para no depender de "no hay errores".
4. Casos borde y rollback: qué pasa con entradas raras y que sabemos cómo revertirlo.
5. Una ventana de observación razonable (unos días) con las métricas de negocio que debía mover.

Si todo eso está, cerramos con una nota de qué se verificó. Si no, lo dejamos abierto en estado "en observación".

## Pedido 3

Que un bug documentado dos veces en el README vuelva a aparecer indica que documentarlo no lo está resolviendo: el README es un parche, no una solución. Hay que atacar la causa.

Supuesto: no tengo acceso al código, así que describo lo que haría.

1. Reproducirlo y escribir un test de regresión que falle hoy. Eso es lo que impide que vuelva, mucho más que una nota.
2. Encontrar la causa raíz, no el síntoma. Revisaría por qué reapareció: ¿se arregló solo el síntoma?, ¿un merge o refactor lo reintrodujo?, ¿hay otro camino de código con el mismo defecto?
3. Corregirlo en el origen y, si es posible, hacer que el error sea imposible por diseño (validación, tipos, una única fuente de verdad en vez de código duplicado).
4. Agregar el test a CI para que bloquee cualquier reintroducción.
5. Dejar en el README una línea breve con el enlace al test y al fix, no solo la descripción del problema.

Si ya hay tests para las dos veces anteriores y aun así volvió, el problema es de cobertura o de cómo se despliega; ahí miraría el pipeline.

## Pedido 4

No lo escalaría todavía. Con 40 usuarios por brazo la muestra es muy chica: el +12% relativo puede ser puro ruido.

Orden de magnitud: si la conversión base fuera, por ejemplo, 10%, 40 usuarios son unas 4 conversiones por brazo; pasar a 4,5 es una diferencia de media conversión. Un intervalo de confianza para ese +12% seguramente incluye cero e incluso valores negativos grandes. Un test estadístico daría un p-valor muy alto.

Supuestos: aleatorización correcta y una sola métrica primaria definida de antemano.

Qué haría:
1. Calcular el intervalo de confianza de la diferencia (no solo el porcentaje relativo).
2. Hacer un cálculo de potencia: para detectar un efecto de ~12% relativo con la conversión base real hacen falta típicamente miles de usuarios por brazo.
3. Definir el tamaño de muestra y la duración antes de seguir, y no frenar el test apenas se ve un número lindo (peeking).
4. Seguir corriendo el experimento hasta alcanzar ese tamaño.
5. Escalar gradualmente solo si el efecto se sostiene con intervalo que excluya cero y sin dañar métricas secundarias.

## Pedido 5

Un "success rate" de -5046% es imposible como proporción (debería estar entre 0% y 100%), así que es un bug de cálculo o de datos, no un resultado real.

Supuesto: success rate = éxitos / total, o algo similar.

Causas probables:
1. Una resta mal planteada, por ejemplo (éxitos - fallos) / total, o 1 - (fallos / éxitos) con fallos mucho mayores que éxitos. Con cifras como éxitos = 1 y fallos = 51.46 daría algo como -5046%.
2. Contadores inconsistentes: el denominador es mucho menor que el numerador o las dos métricas vienen de fuentes o ventanas de tiempo distintas, o el contador se reinició.
3. Overflow o desbordamiento de enteros sin signo, o un contador que decrementa.
4. División por un denominador casi cero (muy pequeño).
5. Un error de formato: un valor ya expresado en porcentaje multiplicado de nuevo por 100.

Cómo lo investigaría: tomar los números crudos (numerador y denominador) del período que muestra el valor, recalcular a mano, revisar la fórmula en la consulta o el panel, y comparar con otra fuente. Después agregar una validación para que el panel marque cualquier tasa fuera de 0-100%.

## Pedido 6

Un p-valor es la probabilidad de observar un resultado tan extremo como el que obtuviste (o más), asumiendo que la hipótesis nula es verdadera, es decir, que no hay efecto real.

Ejemplo: si comparás dos versiones de una página y obtenés p = 0.03, significa que, si en realidad no hubiera diferencia, solo verías una diferencia así de grande o mayor un 3% de las veces por azar.

Lo que no es:
- No es la probabilidad de que la hipótesis nula sea cierta.
- No es la probabilidad de que el resultado sea producto del azar.
- No mide el tamaño ni la importancia del efecto.

Se suele comparar con un umbral (0.05) para decir que es "estadísticamente significativo", pero ese corte es una convención. Un p-valor chico con muestra enorme puede corresponder a un efecto trivial, y un p-valor grande con muestra chica no prueba que no haya efecto. Conviene reportarlo junto con el tamaño del efecto y un intervalo de confianza.
