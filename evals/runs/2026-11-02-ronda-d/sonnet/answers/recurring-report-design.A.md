## Pedido 1

Puedo sumar la hoja, pero no lo haría como "todo lo que vimos esta semana". Eso acumula, y un parte que ya se siente largo se lee menos con cada hoja que se le agrega. Lo que propongo:

- **Primera hoja fija:** qué cambió y qué mirar hoy. No rota nunca, porque rotar las excepciones esconde lo accionable.
- **Segunda hoja con un tema por día de la semana,** que rota en vez de acumular. Así el parte tiene siempre las mismas hojas, y el resumen de la semana va a la vista semanal (una vez por semana), no al parte diario.
- **Cada ítem nuevo necesita un lector y una base.** Para cada cosa de la semana que quieras incluir, decime quién la lee y qué hace distinto por verla. Cada cifra va con su denominador, por ejemplo "12 de 156". Lo que no tenga lector se queda afuera.

Si igual querés una hoja más, hay que medir cuántas páginas imprime cada variante del parte (cada día de la semana), no solo la de hoy. Una hoja que entra el martes puede dejar el viernes en tres. Cuando un parte sale una página más de lo esperado, casi siempre el culpable es el pie de página que se pasa por pocos milímetros. Ahí se achica el aire entre bloques antes de tocar tipografías o gráficos.

Pasame qué temas de la semana querés incluir y te armo la hoja rotativa.

## Pedido 2

Imprimir los 278 ítems completos va a lograr lo contrario de lo que buscás. Una lista de 278 líneas no se ejecuta: se saltea entera, y arrastra con ella los ítems que sí importan. El atraso se ve mejor con números, y eso sí lo puedo poner en el parte:

- **Una dosis diaria con tope.** Por ejemplo, 3 por día × 5 días = 15 por semana, y la línea dice "los 278 ítems abiertos son 18-19 semanas".
- **Un ítem por escalón,** no los primeros N de un solo ranking:
  1. registros imposibles, como cantidades negativas;
  2. registros con el documento faltante demostrable;
  3. stock cero con ventas recientes;
  4. riesgo por valor y rotación para el resto.
  Si un escalón se vacía, su lugar pasa al siguiente.
- **Sin repetir lo que ya está pendiente,** ni en el registro de acciones ni en la hoja anterior.
- **Los que esperan hace mucho** pasan a una línea de aviso con los días de espera ("sigue esperando, 21 días"). Siguen visibles pero no ocupan lugar.
- **Orden fijo,** nunca al azar, para que dos corridas del mismo día impriman lo mismo.
- **La cola completa con su denominador** va en la vista semanal. Si querés ver el atraso completo, ahí está. Si querés una lista para recorrer de una vez, agrupala por estantería, marca o proveedor, como "33 ítems, todos de una marca", y que cada día imprima un grupo con el total restante.

Antes de agrupar, hay que medir con qué campo se agrupa. El catálogo y el texto del propio producto suelen no coincidir (4 filas en un caso, 104 categorías distintas en el otro). Y hay que escribir cuál de los dos se usa.

## Pedido 3

Mandalo igual. Si el reporte solo habla cuando hay algo para decir, una mañana tranquila y una corrida rota se ven igual: silencio. Que no llegue nada tiene que ser la alarma.

Por eso el primer ítem del día sale siempre, con sus números y diciendo que es el latido. Algo como: "N cargados, 0 excepciones, M candidatos. Este ítem confirma que la corrida funcionó". No molesta, ocupa una línea.

Dos cosas más:

- **Qué día mide.** El latido mide el último período cerrado que tenga datos, y lo dice. Si corre en el borde del día y mide un período recién empezado, "0 excepciones" se lee como "todo bien" sin serlo.
- **Código de salida.** Un día sin excepciones sale con código 0. Un código distinto de cero es solo para cuando no se pudo medir o entregar.

## Pedido 4

No pondría 17:55 en el encabezado. Una corrida atrasada tiene que decirlo, y nunca afirmar la hora en que debía salir. Si el encabezado dice 17:55, afirma algo falso sobre su propio corte: los datos se leyeron a las 19:56, y quien compare con la fuente va a ver que no coinciden.

Lo que haría:

- **Encabezado:** 19:56, la hora real de lectura.
- **La hora nominal queda aparte,** como dato de la programación.
- **Como el atraso es material,** va una línea visible: "corrida atrasada: la de las 17:55 salió a las 19:56, 121 minutos más tarde".

Así se conserva el 17:55 que querés, pero como aviso y no como hora del corte. Lo mismo vale para cada cifra viva del parte: lleva la hora en que se leyó, no la que marcaba la agenda.

## Pedido 5

La única medida que tengo es la de este tipo de parte impreso, y no es un estándar de A4: **10 mm por lado**. El papel A4 mide 210 × 297 mm, y con márgenes de página de 10 mm queda un área útil de 190 × 277 mm. Esos 277 mm de alto son la referencia para medir si un bloque entra en la hoja.

No hay un margen único que A4 "use" por norma. Es lo que se configura en el diseño de impresión (por ejemplo, `@page { margin: 10mm }`). Si tu impresora o tu plantilla usan otro valor, el alto útil cambia. Es siempre 297 menos el doble del margen.
