## Pedido 1

Todavía no. Que la estrategia gane en el rango 0.30-0.42 es un hallazgo exploratorio, no una validación. Supongo que ese rango lo encontraste mirando los mismos datos con los que lo evaluaste, así que hay riesgo alto de sobreajuste: si probaste muchos cortes, alguno iba a salir bien por azar.

Qué haría antes de activarla:

1. Revisar cuántos cortes/rangos se probaron (multiplicidad) y cuántas operaciones hay dentro del rango. Con pocas operaciones, el resultado es ruido.
2. Validar fuera de muestra: fijar el rango 0.30-0.42 de antemano y testearlo en un período o mercado que no se usó para encontrarlo (walk-forward o holdout).
3. Chequear robustez: ¿se sostiene si el rango se mueve un poco (0.28-0.44)? Un borde muy filoso es mala señal. ¿Hay una razón económica o de mecánica de mercado que explique por qué funciona ahí?
4. Incluir costos reales: comisiones, slippage, liquidez, y si el precio de entrada era realmente ejecutable.
5. Si pasa, activarla gradualmente: paper trading o tamaño mínimo, con límites de pérdida y criterios de corte definidos de antemano.

Respuesta corta: no la activo en producción con este análisis; la dejo como hipótesis, la valido fuera de muestra y, si aguanta, arranco chico con monitoreo.

## Pedido 2

Todavía no lo cerraría. "Deployado y sin errores" significa que no rompe, no que funciona. La ausencia de errores puede ser también ausencia de uso, o fallas silenciosas (logs que no capturan el caso, resultados incorrectos sin excepción).

Supongo que el feature tiene un objetivo definido. Antes de cerrar verificaría:

1. Que se esté usando: eventos o métricas que muestren tráfico real al feature, no solo ausencia de errores.
2. Que haga lo correcto: comparar el resultado contra los criterios de aceptación originales, con un caso real de punta a punta en producción.
3. Que las métricas de éxito acordadas se muevan (o al menos no empeoren las existentes): latencia, conversión, tasa de error de otros componentes.
4. Que haya alertas y monitoreo para este feature, y que esté documentado cómo revertirlo (flag o rollback).
5. Una ventana de observación razonable (por ejemplo una semana con tráfico normal), cubriendo casos borde y picos.

Si todo eso está bien, lo cierro y dejo anotado qué se verificó y cuándo. Si no hay métricas de uso, el cierre real es agregar esa instrumentación primero. Propongo moverlo a "en observación" y fijar una fecha de cierre.

## Pedido 3

Si un bug documentado dos veces en el README volvió, la documentación no lo está resolviendo: documentar es un parche, no una corrección. El patrón de recurrencia indica que la causa raíz sigue viva.

Lo que haría:

1. Reproducirlo ahora y escribir un test automatizado que falle por este bug (test de regresión), para que no vuelva a pasar sin que CI avise.
2. Revisar las dos entradas del README y el historial de git/issues: qué se hizo cada vez, por qué reapareció (fix superficial, regresión por otro cambio, entorno distinto, condición de carrera).
3. Buscar la causa raíz en lugar de aplicar otro workaround. Supongo que las veces anteriores se documentó un paso manual o una advertencia; hay que eliminar la condición que lo genera.
4. Aplicar el fix, con el test incluido en el mismo cambio, y verificar que cubra las variantes del caso (no solo la instancia exacta).
5. Dejar en el README una sola entrada consolidada: síntoma, causa, fix y enlace al test o commit, reemplazando las dos duplicadas. Si el fix es definitivo, la nota pasa a ser historial, no una instrucción de uso.

Si no se puede arreglar de raíz ahora, lo registro como issue abierto con dueño y fecha, en vez de sumar una tercera nota al README.
