## Pedido 1

No la activaría en producción todavía. Que la estrategia gane en el rango 0.30 a 0.42 es un hallazgo sacado de los mismos datos con los que se eligió el rango, así que hay riesgo serio de sobreajuste: con suficientes cortes posibles, siempre aparece algún subgrupo que "funciona" por azar.

Antes de activarla, haría esto:
- Validar el rango en datos que no se usaron para encontrarlo (periodo posterior o holdout).
- Revisar cuántos rangos y subgrupos probamos, y ajustar por comparaciones múltiples.
- Medir el tamaño del efecto neto de costos, slippage y comisiones.
- Hacer un despliegue acotado (canary o shadow mode) con un grupo de control, y definir de antemano la métrica de éxito y el criterio para apagarla.

Supuesto: no hay una validación previa fuera de muestra. Si la hay, el análisis cambia.

## Pedido 2

No lo cerraría todavía. "Deployado y sin errores" solo confirma que no se rompe; no confirma que haga lo que se quería.

Antes de cerrarlo, verificaría:
- Los criterios de aceptación definidos al empezar, cumplidos con datos reales.
- Que la métrica de negocio o de uso objetivo se mueva como se esperaba.
- Que haya monitoreo y alertas activos, y un plan de rollback probado.
- Que los usuarios efectivamente usen la funcionalidad (adopción), no solo que esté disponible.

Supuesto: existe una definición de "terminado" escrita. Si no existe, lo primero es escribirla y después cerrar el ticket con evidencia.

## Pedido 3

Esto indica que documentar el bug no lo previene. Agregar una tercera nota al README sería repetir lo que no funcionó.

Haría lo siguiente:
- Revisar el historial de git para ver si el fix original se revirtió, se pisó en un merge o nunca llegó a producción.
- Encontrar la causa raíz, no solo el síntoma.
- Escribir un test de regresión que falle con el bug y pase con el fix, y correrlo en CI para que bloquee cambios que lo reintroduzcan.
- Dejar el README apuntando al test o al issue, no como única protección.

Supuesto: el bug es reproducible y el código está en un repositorio con CI.

## Pedido 4

No lo escalaría. Con 40 usuarios por brazo el resultado casi seguro no es confiable: el intervalo de confianza del +12% probablemente incluye valores cercanos a cero o negativos, y los efectos grandes obtenidos con muestras chicas tienden a sobreestimarse (la "maldición del ganador").

Antes de decidir, revisaría:
- Un cálculo de poder estadístico para saber cuántos usuarios hacen falta para detectar un efecto del tamaño que nos interesa.
- El p-valor y el intervalo de confianza, no solo el porcentaje.
- Que la prueba haya corrido suficientes días para cubrir ciclos semanales y evitar efectos de novedad.
- Métricas de guardrail (retención, ingresos, errores) que no hayan empeorado.

Plan: seguir el test hasta alcanzar el tamaño muestral planeado y escalar solo si el efecto se sostiene con significancia y en un intervalo que justifique el cambio.

## Pedido 5

Un "success rate" de -5046% no puede ser una tasa real, porque una tasa válida está entre 0% y 100%. Lo más probable es un error de cálculo o de datos.

Causas posibles, en orden de probabilidad:
- La fórmula: -5046% equivale a un valor de -50.46 multiplicado por 100. Puede ser una resta o una diferencia de conteos en el numerador, por ejemplo (éxitos - fallos) / total, en lugar de éxitos / total.
- Un denominador casi cero o distinto del esperado, por un filtro o join que no coincide entre tablas.
- Un join que duplica o descarta filas, o un conteo que mezcla eventos de distintos periodos.
- Un error de unidades o de formato, como dividir por 100 dos veces o mostrar un ratio como porcentaje sin cambiar el formato.

Qué haría: revisar la fórmula del widget, comparar los conteos crudos de éxitos e intentos contra la query, y verificar el denominador. Mientras tanto, ocultaría o marcaría la métrica como no confiable para que nadie tome decisiones con ese número.

## Pedido 6

El p-valor es la probabilidad de observar un resultado tan extremo como el que obtuvimos, o más, asumiendo que la hipótesis nula es verdadera (y que se cumplen los supuestos del modelo).

Ejemplo: si una moneda sale 60 caras en 100 tiradas, el p-valor responde cuán probable es ver 60 o más caras si la moneda es justa.

Lo que no significa:
- No es la probabilidad de que la hipótesis nula sea verdadera.
- No es el tamaño del efecto ni su importancia práctica.
- No es la probabilidad de que el resultado se repita.

Un p-valor bajo indica que los datos son poco compatibles con la hipótesis nula, pero no dice nada sobre la calidad del diseño del experimento. El umbral de 0.05 es una convención, no una regla natural.
