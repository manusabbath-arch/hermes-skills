## Pedido 1

No lo programaría todavía. Un agente que gasta en modelos tiene que tener un tope declarado y escrito antes de correr solo. Programar las evals todas las noches significa gastar cada día sin que nadie lo haya decidido, así que esa decisión la tiene que tomar una persona y dejarla por escrito.

Antes de programarlas, definiría:

- **Tope por llamada** y **tope obligatorio por corrida**. Si una corrida llega al tope, los casos que quedan cuentan como fallo, no se saltean.
- **Quién autoriza el gasto** y cuánto por noche y por mes.
- **Qué resultado les llega y cómo**: veredicto, n, y si la corrida se completó o se cortó por tope.

Cuando eso esté escrito, lo armo: el programador, los topes en el código y un test que falle si una tarea programada invoca un modelo que no tiene tope declarado. Si querés, empezamos por una corrida manual con tope bajo para medir cuánto cuesta una noche real.

## Pedido 2

No está bien. Un tablero que muestra verde cuando no hay log de respaldo de ayer da una señal falsa: la falta de datos se lee como "todo sano".

La regla correcta es que **sin dato = STALE, nunca verde**. Para el respaldo, el tablero tiene que mostrar:

- **Rojo o amarillo** si no hay log de hoy o de ayer, con la antigüedad del último respaldo bueno.
- **Verde** solo si el log existe, es de la fecha esperada y el respaldo se verificó.

Lo mismo aplica a los demás indicadores (espacio libre en disco, trabajo sin commitear hace horas): si no se pudo medir, se muestra como desconocido o stale, no como sano. Si un chequeo está mal configurado y no corre, también tiene que aparecer como fallo y no como ausencia de errores.

## Pedido 3

El 15% de 2.400 es **360**.
