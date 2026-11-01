# Elevación del terreno y anclaje a un umbral oficial

Profundidad de la compuerta 7. Dos preguntas de la misma familia, y las dos se arruinan igual: **citar un
número sin su escala** («el río está en 11,38» / «el galpón está a 53 m»). Acá está la receta que sí las
cierra, y el orden importa: primero el contexto de la fuente, después el umbral, y recién ahí el número.

## 1. Topes y trampas de una serie de nivel (caso concreto de la compuerta 6)

- **La ventana máxima que acepta la herramienta es parte de la cifra.** Una suba medida sobre un tope de
  **92 días** es «en 92 días», nunca «desde el mínimo del año». La serie fina va cada 15 min (96 lecturas
  por día): la `cobertura` declarada (esperadas vs recibidas) se mira **antes** de citar una media.
- **La comparación multi-anual se hace por los mismos días de calendario**, no por un promedio de años: la
  herramienta de comparado devuelve la media de esos días en cada año desde el inicio de la serie, con el
  **puesto** (1 de N) y la lista de años excluidos por falta de lecturas. Leer esa lista: vacía significa
  que ninguno quedó afuera.
- **Un año fuera de escala se declara outlier, no se promedia.** Un valor que se despega del resto (medido:
  un año a dos órdenes de magnitud del resto) mueve el puesto y la conclusión: señalarlo.
- **La media ponderada no cierra exacto contra la media simple, y no debe.** Una pondera por lectura; el
  residuo es el mecanismo, no el error. Fijar el **orden** (0,01) con tolerancia escrita (0,02) y decir la
  causa (un día que entró con menos lecturas). `variacion_en_el_periodo` sí es identidad: último día menos
  primero, exacto.
- **Una ventana de clima posterior al último dato devuelve lista vacía, y eso no es «no llovió».** Las
  fuentes de lluvia suelen llegar con semanas de atraso: comparar el último dato contra la ventana pedida y
  decirlo, en vez de leer el vacío como ausencia.
- **`-999` es «sin dato»**, no un caudal negativo. Un campo nulo porque la estación no mide eso se declara
  como no medido.

## 2. Los umbrales que la fuente no trae

El servicio da el nivel y no da la cota. La escalera existe, es oficial y tiene **tres escalones**
—aviso / seguridad / afectación sensible—, y hay un segundo organismo que republica los mismos escalones
con otros nombres (alerta / evacuación) para los puertos de aguas abajo: **dos cuerpos independientes con
la misma dupla confirman la lectura de la escalera**.

- Comparar contra **los tres**, no contra uno: la media puede quedar abajo del de seguridad mientras el
  pico diario de la misma ventana lo pasa. La frase cambia según el escalón elegido: decir cuál.
- **La página oficial puede contradecirse**: la prosa y la tabla del mismo informe con dos números
  distintos para el mismo escalón. Usar la tabla y declarar la discrepancia.
- **El número de prensa suele ser el pronóstico del día** para ese puerto, no el umbral. Y un récord
  histórico citado solo por prensa se cita **como prensa**.
- **El anclaje de escala se hace sin inventar unidades:** si el pronóstico del propio organismo para el
  punto medido cae en el mismo rango que lo medido por la herramienta, la unidad del campo y las cotas
  oficiales **son la misma escala**. Eso autoriza la frase «quedó 0,02 abajo de la cota de seguridad» en
  lugar de «la unidad no está declarada». El límite que queda sin cerrar se dice aparte (ver §4).

## 3. ¿El agua llega a este predio? — la receta del DEM

1. **Dos DEM públicos e independientes** (modelos digitales de elevación, sin clave): uno de 30 m y otro de
   90 m de resolución, de dos proveedores distintos. Sirven para cualquier punto del planeta y son
   **estables** (no son una fuente viva): re-consultar la misma URL y coordenada tiene que dar el mismo
   número, así que el fixture es re-verificable para siempre.
2. **La misma lista de puntos en las dos llamadas**, y se guarda el payload crudo de las dos.
3. **Grilla 3×3 de ~0,002°** (≈220 m) por ancla en vez del píxel del punto: el terreno alrededor es lo que
   separa una barranca de un predio llano, y el punto solo puede caer en el borde de un cambio.
4. **El canario es el desacuerdo**: donde hay terreno los dos coinciden (≤2 m); sobre el agua divergen
   (decenas de metros). Si coinciden sobre el agua, ese punto no es agua o uno de los dos está mal.
5. **Dos referencias separadas, cada una con su umbral nombrado**: contra el **agua** (celdas mínimas de la
   grilla ribereña, ≥30 m) y contra **lo más alto de la ribera** (celdas máximas, ≥15 m). Un solo umbral
   para las dos esconde cuál se está afirmando.
6. **Trampa de resolución:** un galpón de 45×15 m cabe entero en un píxel de 30 m, así que un techo puede
   falsear la lectura. Si los dos modelos coinciden **exactamente** en el predio, ninguno tomó el techo
   (dos errores iguales son improbables).
7. **Una respuesta multipunto puede no devolver las coordenadas** (solo los valores, en el orden pedido).
   El proveedor que repite `location.lat/lng` es el que **ancla la identidad** de los puntos; el otro se
   alinea por el orden de la lista. Un test que compara las coordenadas devueltas contra los puntos pedidos
   es lo que fija ese contrato.
8. Guardar fixture + `sha256` y los tests que lo fijan: coinciden en el predio, **divergen en el agua**,
   desnivel mínimo por referencia, y las grillas de 9 puntos.

## 4. Cómo se cierra (y cómo no) una pregunta territorial

- Con un desnivel de decenas de metros, **el eje «más cerca del río» no es un eje de riesgo** y sale de la
  decisión. Decirlo explícitamente: una validación previa pudo haberlo dejado como dato a favor o en
  contra, y corregirlo es parte del trabajo, no un detalle.
- Un récord de nivel es una **altura de agua sobre un cero local**, no la altura a la que llega el agua en
  el predio. La distancia en línea recta a una **estación** (un punto del río) sirve para comparar dos
  predios entre sí, no para decir a cuántos metros de la orilla está uno.
- Lo que la elevación **no** contesta, y hay que nombrar: anegamiento por lluvia, estado de los caminos, la
  cota del piso de la construcción (mide el terreno alrededor) y la distancia real a la orilla.
- El riesgo que queda suele ser **otro**: una voladura de techo es viento, no agua. Cerrar la pregunta que
  se hizo no es cerrar la que importaba.

## 5. La cifra que no se reproduce

- Antes de citar la media de un día en curso, **fijar ventana y hora**: cambia entre dos corridas del mismo
  día, y la que queda escrita es un dato viejo disfrazado de medición.
- Cuando igual pasa: **retractar** (qué cifra y por qué, en el campo que el proyecto use para eso), corregir
  el número en **todos** los lugares donde salió (documento, panel, otro repo) y dejar el porqué en un
  bloque de corrección. Reemplazarlo en silencio es la versión barata del mismo error.
- **El fixture con `sha256` es lo que permite distinguir un error de redondeo de un dato viejo.** Sin
  payload archivado, la cifra publicada no se puede defender ni refutar.
