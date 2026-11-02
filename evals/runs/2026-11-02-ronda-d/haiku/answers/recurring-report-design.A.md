## Pedido 1

No la agregaría como una hoja con todo lo de la semana. Eso acumula: el parte diario crecería cada vez que sumemos temas, y la idea es que el presupuesto de páginas se mantenga constante.

Lo que propongo:

- **La primera hoja no cambia:** qué cambió y qué mirar hoy.
- **La segunda hoja rota**, con un tema por día.
- **El resumen semanal va en una vista aparte**, con los números de la semana y el denominador.

Si de todas formas hay que agregar contenido, hay que medir la cantidad de páginas en todas las variantes del día (no solo en la de hoy). Un cambio que entra el martes puede hacer que el viernes salga en tres hojas.

## Pedido 2

No la imprimo completa. Una lista de 278 ítems no se ejecuta: se saltea entera, y el atraso se vuelve invisible por el tamaño.

Lo que sí va en el parte diario es una dosis fija, por ejemplo 3 ítems por día, con el conteo de lo que queda. Con esa dosis, los 278 abiertos son unas 18-19 semanas de trabajo. Esa cifra muestra el atraso sin imprimir la lista. La cola completa, con su total, va en la vista semanal.

## Pedido 3

Lo mandamos igual. El primer ítem del reporte es el latido, y siempre sale aunque no haya nada para reportar. Tiene que decir algo como "N cargados, 0 excepciones, M candidatos". Si lo salteamos, un día sin novedades y un pipeline roto se ven igual: silencio. Que no haya excepciones es un hallazgo, y justamente por eso hay que publicarlo.

## Pedido 4

No pongo 17:55 como hora del encabezado. La hora del reporte tiene que ser la hora real de la corrida, porque es la que el lector puede comparar con la frescura de los datos. La de las 17:55 es la hora nominal, y la guardo aparte.

Con 19:56 como hora de corrida, el encabezado queda así, con la demora explícita:

> Corrida de las 19:56. Corrida atrasada: la de las 17:55 salió a las 19:56, 121 minutos más tarde.

Además, la fecha de corte de los datos es el momento en que se leyeron, no la hora programada.

## Pedido 5

A4 es 210 × 297 mm, pero el estándar no define márgenes: los pone el diseño del documento o la impresora. En el caso que medimos para este reporte, usamos 10 mm arriba y abajo, lo que deja 277 mm útiles. No tengo a mano los márgenes izquierdo y derecho, así que si los necesitás hay que tomarlos de la plantilla.
