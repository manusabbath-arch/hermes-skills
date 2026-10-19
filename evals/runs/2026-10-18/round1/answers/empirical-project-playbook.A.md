## Pedido 1

No la activaría en producción todavía. Un rango (0.30 a 0.42) que aparece al mirar los datos después de haberlos visto es un sweet spot minado post-hoc: sirve como hipótesis, no como hallazgo. Con suficientes cortes posibles, algún rango siempre "gana".

Supuesto: el rango salió de explorar los mismos datos sobre los que medís la ganancia, sin criterios fijados de antemano.

Lo que haría, en orden:

1. **Pre-registro antes de volver a mirar.** Escribo un memo con el claim ("la estrategia tiene EV positivo entre 0.30 y 0.42"), los no-goals y la métrica. También fijo kill y success con números, por ejemplo "kill si EV < 0 a n ≥ 80; success si EV ≥ 0.05 a n ≥ 80". Fijo cuál es la única métrica que decide.
2. **Réplica en muestra fresca.** Re-mido el rango sobre datos que no participaron en el descubrimiento, con un corte de frescura estricto. Uso la herramienta canónica de veredicto y no queries ad-hoc, porque estas no deduplican y pueden inflar `n` varias veces si hay fuentes gemelas.
3. **Tamaño real.** El veredicto vale al tamaño al que se midió, no a uno mayor.
4. **Shadow, observación y recién después enforce.** Un flag que calcula y loguea "habría operado" sin ejecutar. Nunca pasar a live ni a hard gate desde datos de paper. Con el flag en OFF como kill switch y rollback conocido.
5. Si la réplica cumple el criterio, el hallazgo pasa de PROPOSED a TESTING y a SUPPORTED en el registry. Si no, queda como INSUFFICIENT o RETRACTED.

Resumen: hoy es una hipótesis. Con la réplica y el shadow se decide si se activa.

## Pedido 2

Todavía no lo cerraría. "Deployado y sin errores" es presencia, no utilidad. Un feature está terminado cuando una query o log de producción responde la pregunta que lo motivó, con valores plausibles en filas posteriores al deploy.

Supuesto: no tenemos escrita todavía la query de aceptación del feature.

Qué haría:

1. **Escribir la query de aceptación** (idealmente debió existir antes de construir) y correrla en producción sobre filas post-deploy. Verifico que los valores sean plausibles y no solo que haya filas.
2. **Distinguir tres estados:** no medido (NULL, defecto), medido con valor (dato) y medido en cero (dato legítimo). Un campo NULL en todas las filas indica que no funciona, aunque no haya errores.
3. **Buscar los silencios traidores**, que son justamente bugs que no tiran error:
   - wiring fantasma (un atributo que nadie asigna, con un default "seguro");
   - un writer que escribe y nunca hace commit;
   - un getter que traga la excepción y devuelve vacío.
   Para leer, uso una conexión nueva, no la del pool.
4. **Medir durante horas, no minutos.** Un reconnect hace que todo parezca sano 1 o 2 minutos.
5. **Verificar el SHA realmente deployado**, no la intención, y mirar el CI tras el push a main.
6. Confirmar que existe flag/kill switch y rollback conocido.

Cuando la query de producción devuelva valores plausibles post-deploy, lo cerramos. Si no, queda abierto con el motivo anotado.

## Pedido 3

Que un bug documentado dos veces vuelva a aparecer indica que la prosa no lo frena. Un párrafo en el README no previene la recurrencia: lo que sí lo hace es un check que falle el build.

Supuesto: no sabemos todavía si el bug es mecanizable, así que cubro las dos ramas.

Qué haría:

1. **Reproducir y registrar el patrón** con el formato de incidente: síntoma, causa, firma detectable y si es mecanizable.
2. **Si es mecanizable** (casi siempre lo es): escribo un check o guard que falle el build ante esa firma. Lo conecto a CI sin `|| true` ni `continue-on-error`, porque un gate que no puede fallar no protege. Verifico que el gate distinga "falló" de "no corrió".
3. **Test de regresión que falle contra el código previo.** Un fix no está verificado hasta que su test está en rojo con el código viejo. Reviertro el archivo, corro la suite, restauro. Agrego un gemelo de frontera para confirmar que el fixture realmente toca el límite.
4. **Revisar la familia a la que pertenece.** Compruebo si es un silencio traidor (wiring fantasma, writer sin commit, default que oculta el error) y busco el mismo patrón en otros lugares del proyecto.
5. **Si hoy no es mecanizable**, lo anoto como deuda explícita en `docs/DEBT.md`, con fecha, evidencia y por qué todavía no es check. Se revisa en cada sesión y se promueve a check si cambia el contexto.
6. **No corregir solo el síntoma.** Si corrijo y no dejo rastro mecánico ni deuda, la próxima sesión repite el error.

Además, el README que lo documentó dos veces pasa a apuntar al check, en lugar de repetir la explicación.
