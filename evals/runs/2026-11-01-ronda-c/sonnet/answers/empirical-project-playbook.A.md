## Pedido 1

Te recomiendo no programarlas así. Hay una regla que va justo en contra: un agente que gasta en modelos no corre programado. Programar gasto es una decisión de una persona, y tiene que estar escrita antes.

Si igual querés que corran de noche, hacelo con estas condiciones:

- **Tope por llamada y tope obligatorio por corrida.** Cuando se alcanza el tope de la corrida, los casos que faltan puntúan como fallo. No se saltean, porque si no el resultado parece mejor de lo que es.
- **Lista de lanzadores.** Un test tiene que fallar si un script lanza un modelo y no está en esa lista con su tope. También tiene que fallar si una tarea programada invoca un modelo sin estar autorizada en esa lista.
- **Decisión escrita antes de programar.** Anotá quién autoriza el gasto nocturno, cuál es el tope diario y qué pasa si se supera. Ese registro es la autorización, y un cron suelto no lo es.
- **Aviso sin silencios.** Si la corrida no arranca, se corta o se queda sin dato, el mensaje que les llegue tiene que decir "NO CORRIÓ". No puede ser lo mismo que "sin fallos".

Mientras eso no esté escrito y verificado, lo más sano es que las evals las lance una persona a mano, con tope. Después, cuando esté el registro y el test, se pasa a lo nocturno.

## Pedido 2

No, no está bien. Que no haya log de respaldo de ayer es un dato que falta, y un dato que falta no es un dato sano. El tablero tiene que mostrar **STALE** (sin dato), nunca verde.

Verde por falta de errores es un "silencio traidor". El tablero no distingue "falló" de "no corrió". Si el respaldo dejó de ejecutarse, tampoco va a haber errores, y el tablero va a seguir verde justo cuando hay un problema.

Qué cambiaría:

- Medí la **antigüedad del último respaldo bueno**. Si pasa de tu umbral (por ejemplo 26 h para un respaldo diario), el estado es STALE o rojo.
- Mostrá en la misma vista disco libre y trabajo sin commitear de más de N horas. Así hay una sola vista de salud.
- Un respaldo que nunca se restauró en un entorno limpio tampoco prueba que funcione. Conviene probar la restauración cada tanto.

## Pedido 3

El 15 % de 2.400 es **360**.

(2.400 × 0,15 = 360)
