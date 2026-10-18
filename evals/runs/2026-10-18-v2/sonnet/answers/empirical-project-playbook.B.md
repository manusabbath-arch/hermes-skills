## Pedido 1

No, todavía no. Un rango de precio (0.30 a 0.42) encontrado mirando los datos después de la sesión es una hipótesis, no un hallazgo: si probaste muchos cortes y quedaste con el que ganaba, el "sweet spot" puede ser puro ruido.

Qué haría, en orden:
1. Escribir un pre-registro (claim, evidencia, no-goals, métrica) con criterios fijados antes de mirar datos nuevos. Ejemplo: "kill si EV < 0 con n ≥ 80; éxito si EV ≥ 0.05 con n ≥ 80".
2. Replicar el rango en una muestra fresca, con datos que no participaron en el descubrimiento y un corte de fecha estricto. Hay que deduplicar por entidad, porque un n inflado engaña.
3. Pasarla a shadow: que calcule y loguee "habría operado X" sin ejecutar nada. Desde datos de paper nunca se pasa directo a producción.
4. Escribir de antemano la query de aceptación: qué tiene que mostrar producción, con valores plausibles en filas posteriores al deploy, para decir que sirve.
5. Dejar el flag en OFF como kill switch, con rollback conocido (revertir un SHA).

Supuesto: no sé cuántas variantes de rango probaste ni el tamaño de muestra. Si fueron muchas o n es chico, la evidencia es aún más débil.

Veredicto: seguir en shadow y replicar. Activar en producción solo si pasa los criterios pre-registrados.

## Pedido 2

Todavía no. Que esté deployado y no tire errores demuestra que corre, no que sirve. "Presence ≠ utility": un feature está terminado cuando una query o log de producción responde la pregunta que motivó el feature, con valores plausibles en filas posteriores al deploy.

Antes de cerrar:
1. Verificar el SHA realmente deployado. Un deploy puede reportarse completo mientras el código corre atrasado respecto a main.
2. Correr la query de aceptación en producción y mirar que las filas nuevas tengan valores plausibles, no NULL ni todo cero. Distinguir "no medido" (NULL, defecto) de "medido y dio cero" (dato legítimo).
3. Observar durante horas, no minutos. Un reconnect hace que todo se vea sano 1-2 minutos.
4. Revisar silencios traidores: getters que devuelven vacío ante un error, escrituras sin commit, wiring que nadie asigna. Todos son sistemas "sin errores" que no hacen nada.
5. Confirmar que el CI de main esté verde.

Supuesto: no tenemos todavía una query de aceptación escrita. Si no existe, escribila ahora.

Cerramos cuando esa query responda con datos reales de producción. Si hoy solo tenemos "no hay errores", dejalo abierto en observación.

## Pedido 3

Un bug que se documentó dos veces en el README y volvió a aparecer indica que la prosa no lo frena. Si se puede mecanizar, tiene que ser un check que falle el build, no un párrafo.

Qué haría:
1. Reproducir el bug y escribir un test que falle contra el código actual. Un fix no está verificado hasta que su test falla contra el código previo.
2. Arreglar la causa raíz, no el síntoma, y confirmar que el test pasa a verde. Agregar un gemelo de frontera si el test afirma una cota.
3. Convertir la regla del README en un check que falle el build: lint, guard o test en CI, con gate que distinga "falló" de "no corrió".
4. Revisar si es una familia conocida (silencio traidor) y buscar otras instancias del mismo patrón en el código.
5. Si realmente no se puede mecanizar hoy, dejarlo como deuda explícita en `docs/DEBT.md`: fecha, evidencia y por qué todavía no es check. Así la próxima sesión sabe que el patrón existe.
6. Podar el README: dejar un puntero al check, no la tercera explicación.

Supuesto: no sé cuál es el bug. Si me lo pasás, puedo proponer el check concreto.

## Pedido 4

No lo escalaría todavía. Con 40 usuarios por brazo, +12% relativo es casi seguro indistinguible del ruido. Por ejemplo, con una conversión base del 10% son 4 conversiones contra 4,5: una diferencia de media conversión. El intervalo de confianza va a cruzar el cero con holgura.

Qué haría:
1. Pre-registrar antes de seguir: métrica única de veredicto, tamaño de muestra objetivo (calculado por poder estadístico para el efecto mínimo que importa) y criterios de kill y éxito.
2. Seguir corriendo el test hasta ese n, sin mirar y parar cuando "da bien" (eso es minería de los propios datos).
3. Reportar el intervalo de confianza, no solo el +12%, y medir al tamaño en que se midió: un veredicto a 40 por brazo no vale para todo el tráfico.
4. Si el resultado se sostiene, hacer rollout gradual (canary) con flag y rollback listo, no pasar de 40 usuarios a todos.

Supuesto: la asignación fue aleatoria y la métrica estaba definida de antemano. Si no, aún menos confiable.

Veredicto: es una pista, no un hallazgo. Se sigue el test hasta el n pre-registrado.

## Pedido 5

"-5046%" es casi seguro un bug de cálculo, no un resultado real: una tasa de éxito no puede ser negativa. Es la firma de un silencio traidor clásico: una métrica que cuenta solo éxitos y se usa como denominador, o un denominador mal armado.

Hipótesis, de más a menos probable:
1. Denominador incorrecto: por ejemplo `(éxitos - total) / éxitos`, o un total que cuenta solo una parte de los eventos, o resta en vez de dividir.
2. Mezcla de NULL y 0: un "no medido" tratado como valor, o un contador que se resetea y queda negativo.
3. Contador que vive solo en un log que rota, o dos fuentes con la misma etiqueta que se pisan.
4. Un delta calculado contra una línea base casi cero, que explota el porcentaje.

Cómo lo investigo:
1. Tomar los números crudos (éxitos, fallos, total) con una query directa a producción, con conexión nueva.
2. Recalcular la fórmula a mano y compararla con la del dashboard.
3. Buscar de dónde viene cada término y si algún getter traga excepciones y devuelve vacío.
4. Agregar un check que falle si la tasa sale de [0, 100%].

Supuesto: no veo la fórmula ni la query del dashboard. Con eso podría señalar el término exacto.

## Pedido 6

Un p-valor es la probabilidad de observar un resultado tan extremo como el que obtuviste (o más), suponiendo que la hipótesis nula es cierta, es decir, que no hay ningún efecto real.

Ejemplo: comparás dos versiones de una página y la diferencia de conversión da p = 0.03. Eso significa que, si en realidad no hubiera diferencia, verías una diferencia así o mayor por azar solo el 3% de las veces.

Lo que NO es:
- No es la probabilidad de que la hipótesis nula sea cierta.
- No es la probabilidad de que tu resultado sea "casualidad".
- No mide el tamaño ni la importancia del efecto. Un efecto minúsculo puede tener p chico con muestras enormes.

Se suele usar un umbral (0.05), pero conviene fijarlo antes de ver los datos. Si probás muchas hipótesis o cortes hasta que alguno da p < 0.05, ese resultado es engañoso por comparaciones múltiples. Por eso se acompaña con el intervalo de confianza, el tamaño de muestra y, de ser posible, una réplica con datos nuevos.
