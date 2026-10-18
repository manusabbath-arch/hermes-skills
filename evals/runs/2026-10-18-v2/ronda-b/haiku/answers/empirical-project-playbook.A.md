## Pedido 1

No la activaría en producción todavía. Supuesto: el rango 0.30-0.42 salió de explorar los datos, no de una hipótesis fijada antes de verlos. Un sweet spot encontrado así es una hipótesis, no un hallazgo, porque con suficientes cortes siempre aparece algún rango ganador.

Lo que haría:

1. Fijar por escrito, antes de tocar más datos, el criterio de éxito y el de muerte. Por ejemplo: "kill si EV < 0 con n >= 80; success si EV >= 0.05 con n >= 80".
2. Volver a medir la estrategia sobre datos frescos que no participaron en descubrir el rango, con corte de frescura estricto.
3. Si la réplica aguanta, pasarla a shadow: un flag que calcula y loguea "habría operado X" sin ejecutar. Solo después de observar ese log en un período razonable, considerar enforce.

Activar en producción directamente desde datos de paper o de exploración es saltarse los dos últimos pasos.

## Pedido 2

No lo cerraría. Que el feature esté deployado y no tire errores solo prueba presencia, no utilidad.

Para cerrarlo tiene que cumplirse que una query o log de producción responda la pregunta que motivó el feature, con valores plausibles en las filas posteriores al deploy. Si todavía no existe esa query de aceptación, hay que escribirla ahora y correrla. Además, si el feature tiene flag, conviene confirmar que el kill switch y el rollback (revertir el SHA) siguen funcionando.

Si el feature mide algo que se ve en horas (frescura, throughput), hay que mirar producción durante varias horas, no solo unos minutos: un reconnect puede hacer que todo se vea sano al principio.

## Pedido 3

Un bug que ya quedó documentado dos veces en el README no se resuelve con más prosa. Reaparecer después de documentarlo dos veces demuestra que el README no frena nada.

Lo que haría:

1. Verificar si el patrón es mecanizable. Si lo es, escribir un check que falle el build (script en CI que detecte la condición), y confirmar que el test falla contra el código anterior antes de aplicar el fix.
2. Si no es mecanizable hoy, registrarlo como deuda explícita en `docs/DEBT.md`, con fecha, evidencia y la razón por la que todavía no es check.
3. Registrar el incidente con el formato de incidente (`templates/incident-pattern.md`) para que el próximo agente lo encuentre.
4. Borrar o corregir la sección del README solo cuando el check o la deuda ya existan, para que la doc no diverja del comportamiento real.

## Pedido 4

No lo escalaría. Con 40 usuarios por brazo, un +12% de conversión no tiene peso estadístico.

Supuesto para ilustrar: una conversión base de 10%. Con 40 usuarios por brazo, el error estándar de la diferencia ronda los 7 puntos porcentuales, y el efecto observado es de unos 1.2 puntos. El resultado es perfectamente compatible con cero diferencia, y además es el tipo de número que sale de mirar muchas métricas hasta encontrar una que suba.

Lo que haría:

1. Definir antes de correr un nuevo test el tamaño de muestra necesario para detectar el efecto que importa, junto con los criterios de éxito y de muerte.
2. Medir el efecto en una muestra nueva, no en la que se usó para elegir la hipótesis.
3. Escalar solo si el resultado se replica al tamaño en que se va a operar, y no antes.

## Pedido 5

Lo más probable es que el denominador esté contando solo los éxitos, o que la fórmula tenga la forma incorrecta. Un success rate real está entre 0% y 100%; un valor negativo indica que la fórmula está mal, no que el sistema esté fallando de forma extrema.

Un ejemplo de cómo puede aparecer ese número: si la fórmula es 1 - fallos/éxitos y hay muy pocos éxitos frente a muchos fallos, el cociente da 51.46 y el resultado es 1 - 51.46 = -50.46, es decir, -5046%.

Lo que haría:

1. Revisar la query o función que calcula el dashboard y confirmar cuál es el denominador. Debe ser el total de intentos, no un subconjunto.
2. Correr la query a mano sobre un caso conocido para verificar el resultado.
3. Agregar un check que falle si el success rate sale de [0, 1], para que este tipo de error no vuelva a pasar en silencio.

## Pedido 6

El p-valor es la probabilidad de observar un resultado tan extremo como el obtenido, o más, asumiendo que la hipótesis nula es verdadera. No es la probabilidad de que la hipótesis nula sea verdadera, ni la probabilidad de que el resultado sea producto del azar.
