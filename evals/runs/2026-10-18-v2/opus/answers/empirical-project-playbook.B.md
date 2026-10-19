## Pedido 1

Todavía no. Un rango como 0.30–0.42 encontrado mirando los datos es una hipótesis, no un hallazgo: si probaste varios cortes hasta dar con el que gana, el resultado está minado a posteriori y lo más probable es que no se repita.

Lo que haría:

1. **Pre-registro antes de volver a mirar.** Escribir un memo con el claim (la estrategia tiene EV positivo con precio entre 0.30 y 0.42), los criterios de kill y de éxito con n mínimo (por ejemplo, kill si EV < 0 con n ≥ 80; éxito si EV ≥ 0.05 con n ≥ 80) y la métrica única que decide.
2. **Réplica en muestra fresca.** Volver a medirlo sobre datos que no se usaron para descubrir el rango, con un corte de fecha estricto. Deduplicar por entidad usando la herramienta canónica y no una query ad-hoc, porque el n inflado engaña.
3. **Shadow mode.** Activarla en producción con un flag que solo loguee "habría operado X", sin ejecutar nada. Juntar resultados resueltos hasta llegar al n pre-registrado.
4. **Enforce con kill switch.** Recién si cumple el criterio de éxito, pasarla a live con flag OFF por defecto, un tamaño chico (el veredicto vale para la escala en que se midió) y un rollback conocido.

Supuesto: no hay pre-registro previo de ese rango. Si lo hubiera y además replicara, se puede saltear el paso 1.

## Pedido 2

No. Que esté deployado y no tire errores dice que el feature está presente, no que sirva. Muchos bugs reales no rompen nada: un writer que nunca commitea, un getter que devuelve vacío ante una excepción, un atributo que nadie asigna y que el código lee con un default "seguro".

Para cerrarlo:

- **Query de aceptación.** Correr la consulta que demuestra que el feature responde la pregunta que lo motivó (idealmente escrita antes de construirlo) contra la base de producción, con una conexión nueva.
- **Filas post-deploy con valores plausibles.** Que haya filas no alcanza. Revisar que los campos nuevos no estén en NULL y que los valores tengan sentido, separando "no medido" (NULL) de "medido y dio cero".
- **Verificar el SHA.** Confirmar que lo que corre en producción es el commit que creés que deployaste.
- **Observar horas, no minutos.** Si mide frescura o throughput, un reconnect hace que todo se vea sano durante uno o dos minutos.
- **CI en verde** sobre ese push.

Si todo eso da bien, se cierra. Si no, sigue abierto, con el hueco anotado.

## Pedido 3

Si ya lo documentaron dos veces y volvió, la prosa no está alcanzando. La solución es un check mecanizado que haga fallar el build.

Lo que haría:

1. **Reproducirlo** y escribir un test que lo capture. Ese test tiene que fallar contra el código actual. Si pasa antes y después del fix, no prueba nada.
2. **Registrar el patrón** de incidente: síntoma, causa raíz, por qué se repitió y cuál es la firma detectable (un grep, un lint, una condición en runtime).
3. **Convertir esa firma en un guard** que corra en CI y bloquee el merge: un test de regresión, un script que busque el patrón o una invariante que falle con exit 1. Confirmar que el step no tiene `|| true` ni `continue-on-error`, porque un gate que no puede fallar no sirve.
4. **Arreglar el bug** y verificar que el guard pasa de rojo a verde.
5. **Limpiar el README.** Dejar una línea que apunte al check en lugar del párrafo; una regla en prosa que no se cumple es peor que no tenerla.

Si de verdad no se puede mecanizar, anotarlo como deuda explícita en `docs/DEBT.md`, con la fecha, la evidencia y el motivo, y revisarlo en cada sesión.

## Pedido 4

No. Con 40 usuarios por brazo, +12% es casi seguro ruido.

Una cuenta rápida: si la conversión base ronda el 20%, son unas 8 conversiones contra 9. El error estándar de cada proporción es de unos 6 puntos, así que el intervalo de la diferencia va de mucho peor a mucho mejor. Detectar con potencia razonable un efecto relativo del 12% suele pedir miles de usuarios por brazo, no decenas.

Lo que haría:

1. **Pre-registrar** la métrica única de decisión, el efecto mínimo que te importa, el n calculado con un análisis de potencia y los criterios de éxito y de kill. Todo eso antes de seguir mirando.
2. **No espiar ni cortar a mitad de camino** cuando el número se ve lindo. Correr hasta el n fijado.
3. **Revisar la instrumentación**: asignación aleatoria real, sin contaminación entre brazos, conversiones deduplicadas por usuario.
4. **Si al llegar al n cumple el criterio**, escalar de forma gradual (canary, por ejemplo al 10% y después al 50%) detrás de un flag con kill switch, y monitorear contra la propia línea base.

Supuesto: el +12% es relativo y no hubo pre-registro.

## Pedido 5

Un success rate negativo es imposible, así que el problema está en el cálculo y no en el sistema. Es un patrón conocido: una métrica que solo cuenta éxitos, o que se calcula de manera inconsistente, termina usada como denominador o en una resta.

Las causas más probables:

- **Denominador equivocado.** Se divide por un contador que solo cuenta éxitos, o uno que se resetea o rota (por ejemplo, vive en un log), en lugar de dividir por el total de intentos.
- **Fórmula del tipo `(éxitos − fallos) / algo`**, o `1 − fallos/éxitos`, con muchos más fallos que éxitos. Algo como 1 − 51.46 da −5046%.
- **Contadores de fuentes distintas.** El numerador y el denominador vienen de ventanas de tiempo o tablas diferentes, o los fallos se cuentan duplicados porque no se deduplican por entidad.
- **NULL tratado como 0**, o filas no medidas contadas como fallos.

Lo que haría:

1. Leer la fórmula exacta del dashboard y de dónde sale cada término.
2. Recalcular a mano con una query COUNT sobre producción: intentos totales, éxitos y fallos en la misma ventana.
3. Corregirla a éxitos / intentos (con NULL excluido o marcado aparte).
4. Agregar un check que haga fallar el build si cualquier tasa queda fuera de [0, 1].

## Pedido 6

Un p-valor es la probabilidad de ver un resultado al menos tan extremo como el que observaste, suponiendo que no hay ningún efecto real (la hipótesis nula).

Si te da p = 0.03, quiere decir que, si en verdad no hubiera diferencia, un resultado así o más extremo aparecería por azar alrededor del 3% de las veces.

Lo que no es:

- No es la probabilidad de que la hipótesis sea cierta o falsa.
- No mide el tamaño ni la importancia del efecto.
- Pierde sentido si probaste muchas variantes o cortes y te quedaste con la que dio p < 0.05, porque alguna va a dar "significativa" por azar.

Por eso conviene fijar de antemano el umbral, la métrica y el tamaño de muestra.
