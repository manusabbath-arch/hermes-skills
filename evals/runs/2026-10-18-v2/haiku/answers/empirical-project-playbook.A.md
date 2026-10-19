## Pedido 1

No, todavía no. Supuesto: el hallazgo salió de mirar los datos y el rango 0.30 a 0.42 se eligió después de verlos.

Eso es minería post-hoc: un sweet spot encontrado así es una hipótesis, no un hallazgo. Para avanzar haría lo siguiente:

1. Pre-registrar antes de mirar más datos: el rango, la métrica de veredicto (por ejemplo EV), el tamaño de muestra mínimo y los criterios de kill y success. Por ejemplo, "kill si EV < 0 con n ≥ 80; success si EV ≥ 0.05 con n ≥ 80". Los números son ilustrativos; el n correcto sale de un cálculo de potencia.
2. Re-medir el rango en una muestra fresca que no participó en descubrirlo, con corte de frescura estricto.
3. Si pasa, entrar en shadow: el flag calcula y loguea "habría operado X" sin ejecutar. Sin ejecución real hasta tener observación suficiente.
4. Recién después, activación gradual con kill switch y rollback conocido.

Respuesta corta: no se activa en producción con lo que hay.

## Pedido 2

No lo cerraría. Que no tire errores es presencia, no utilidad.

Antes de cerrar necesito:

- La query de producción escrita antes del build que responde la pregunta que motivó el feature.
- Valores plausibles en filas post-deploy, medidos durante horas (un reconnect o un arranque limpio puede hacer que todo se vea sano por 1 o 2 minutos).
- Confirmación de que el flag de kill switch existe y que el rollback es revertir un SHA conocido.

Si la query da valores razonables, se cierra. Si solo hay filas o no hay errores, queda abierto.

## Pedido 3

Que un bug documentado dos veces en el README vuelva a aparecer indica que la prosa no lo frena. Lo que frena un bug recurrente es un check mecanizado que falle el build.

Haría esto:

1. Registrar el incidente con la plantilla `templates/incident-pattern.md` y decidir si es mecanizable.
2. Escribir el test de regresión y verificar que falla contra el código previo (revertir el archivo con `git show HEAD:<f>`, correr la suite, restaurar). Un test que pasa antes y después no prueba nada.
3. Agregarlo al CI como check que bloquea el merge.
4. Si no es mecanizable hoy, agregar una fila a `docs/DEBT.md` con fecha, evidencia y el motivo.

No agregaría una tercera línea al README. Supuesto: no tengo el detalle del bug ni el README a mano; por eso no lo leí.

## Pedido 4

No lo escalaría. Con 40 usuarios por brazo, un +12% casi seguro es ruido. Supuesto: no hay criterios pre-registrados para este A/B.

Qué haría:

1. Calcular el intervalo de confianza y el p-valor del efecto, y el tamaño de muestra necesario para detectar una diferencia del tamaño que importa (cálculo de potencia).
2. Pre-registrar la métrica de veredicto y los criterios de kill y success antes de seguir corriendo.
3. Replicar en una muestra nueva con el n pre-registrado.
4. Si el efecto se sostiene, escalar por etapas con kill switch, no a todos de una vez.

Hoy el resultado es una hipótesis para replicar.

## Pedido 5

Una tasa de éxito no puede ser -5046%. Ese valor indica un error en el cálculo, no un resultado real. Hay dos causas probables:

- El denominador cuenta solo los éxitos (o un subconjunto chico), mientras el numerador incluye fallos. Con pocos éxitos, la razón se dispara. Es el patrón de "métrica que cuenta solo éxitos usada como denominador".
- Una fórmula de tipo (x - y) / y donde y es casi cero, o un NULL tratado como 0 en alguna parte del cálculo.

Qué haría: revisar la query que alimenta el dashboard y comparar el numerador y el denominador contra el conteo bruto en la base. Después, agregar un check que falle si una tasa sale del rango [0, 100] o si el denominador es menor que un mínimo. El dashboard tendría que tratar "no medido" (NULL) distinto de "medido y cero".

## Pedido 6

El p-valor es la probabilidad de observar un resultado tan extremo o más que el que obtuviste, suponiendo que la hipótesis nula es verdadera (es decir, que no hay efecto).

No es la probabilidad de que la hipótesis sea verdadera, ni el tamaño del efecto, ni la probabilidad de que el resultado se repita. Un p-valor bajo dice que el dato es incómodo para la hipótesis nula, no que el efecto sea grande o importante.

El umbral de 0.05 es una convención. Lo correcto es fijarlo antes de ver los datos, junto con el resto de los criterios de decisión.
