# Diseño de guardas — referencia

Detalle de "El verde vacío", "Guards" y "Baseline con trinquete" de `agent-ready-project`:
cómo se diseña una guarda para que siga mirando lo que dice mirar seis semanas después.
**Origen:** la distribuidora del proyecto de origen, con ~180 chequeos registrados, una
línea base sellada, siete agentes sobre el mismo repo y una regla de trabajo: *cuando un
agente falla, falla un chequeo* (test primero, o el motivo escrito de por qué no se puede).

**Relación con `designing-mechanical-guards`:** esa skill es el procedimiento general para
convertir una regla en guarda (test en rojo, cableado, no-regresión sobre una compuerta
madura); esta referencia es el catálogo de un proyecto concreto: qué forma tomó cada guarda y
qué la rompió. Cada sección termina con un **Procedimiento:** que apunta a la referencia de
esa skill que lo desarrolla. Las dos salen del mismo origen y no se contradicen (revisado
el 01/11/26); lo que solo estaba acá se llevó allá en su versión 1.1.0.

## Contents

1. Un catálogo de chequeos, no scripts sueltos
2. La línea base con rojos declarados
3. El denominador, siempre
4. Perímetros y listas con un solo dueño
5. Una regla, una implementación
6. La guarda que pagaba el costo de lo que rechaza
7. Los permisos del agente son código
8. La compuerta en capas, y medir antes de optimizar
9. Documentos que el código obliga a mantener
10. Guardas nuevas: primero en sombra

## 1. Un catálogo de chequeos, no scripts sueltos

- **Un total nuevo, una regla nueva o un error de agente entran como entrada del catálogo**
  (un registro de funciones con nombre, una compuerta que las corre todas), nunca como un
  script que alguien tiene que acordarse de correr.
- Cada chequeo devuelve un veredicto (`PASS | WARN | FAIL | ERROR`) y un mensaje que
  **lleva su denominador**. "No pudo medir" (archivo ausente, excepción) es `ERROR`, no
  `PASS` con el error en el texto.
- **Un nombre de chequeo mal escrito sale rojo a propósito**: un verde que no corrió nada no
  es un verde.
- **Importar un módulo no tiene efectos.** Un script con todo su cuerpo a nivel de módulo
  consultaba el servidor del proveedor del ERP 7 veces cada vez que algo lo importaba (un
  test, un generador de docs, el editor). Lo que toca un sistema va detrás de
  `if __name__ == "__main__"`, y un test importa cada script en un subproceso y falla si
  alguno imprime.

## 2. La línea base con rojos declarados

`scripts/check_baseline.py` implementa este contrato (stdlib, con tests):

- **Tres clases de rojo, tres respuestas:** *regresión* (estaba mejor, ahora peor) bloquea y
  no se sella; *rojo sin declarar* (ya estaba en la base, nadie lo explicó) avisa;
  *rojo declarado* (motivo + **condición de salida**) no bloquea y se imprime cada vez.
- **Un rojo declarado sin condición de salida es un rojo silenciado:** se rechaza. Al
  redeclarar, la condición vieja se conserva y la fecha de revisión pasa a hoy.
- **Un chequeo que la base no conoce cuenta como si viniera de PASS**: el que nace rojo
  bloquea el commit que lo agrega. Se declara **en ese mismo commit**; sellar la base para
  taparlo absorbe también los rojos ajenos.
- **Un chequeo de la base que dejó de correr bloquea:** desaparecer es la forma más
  silenciosa de apagarse.
- **Sellar mezcla, no reemplaza.** Un sellado con una corrida filtrada dejó 1 entrada de 23.
  Una corrida sin sus dependencias (falta una librería y la mitad sale `ERROR`) no se
  declara ni se sella: se espera a poder correrla completa.
- **El motivo declarado es una foto.** Al imprimir los declarados, mostrar el veredicto y el
  mensaje **de hoy** encima del motivo fechado: una validación copió el número sellado (viejo)
  porque era la línea que estaba más abajo. Avisar cuando el mensaje cambió respecto del de
  la declaración, comparando sin los dígitos de contadores que suben solos.
- **Una declaración que sobra** (el chequeo volvió a verde) se avisa con el comando exacto
  para quitarla, no con "limpiar el registro".

**Procedimiento:** skill `designing-mechanical-guards`: *exception-registers*, *exception-registry-lifecycle* y *changing-existing-guards* (agregarle a una guarda que ya existe el estado declarado).

## 3. El denominador, siempre

- **"0 hallazgos" sobre 0 elementos no es "0 hallazgos".** El test de cada chequeo incluye
  el caso del universo vacío y exige que no salga verde (en el origen, más de 60 casos así en
  una sola clase de tests: cero fuentes, inventario vacío, manifiesto ausente, manifiesto con
  sello vacío, cero documentos, un repo sin archivos, una raíz que no es repo…).
- **Un archivo ilegible no sale del universo y del denominador a la vez:** el parser que se
  traga la excepción da `(0, 0)`, lo mismo que un directorio limpio.
- **Antes de publicar un conteo, correr el chequeo sobre aciertos conocidos** y exigir 0
  falsos positivos; un chequeo de consistencia compara contra el **componente** donde vive el
  valor (la ciudad en la cola de una dirección compuesta), no contra la subcadena.
- **Un test que muere antes de su aserción** (en Windows: `text=True` y un binario que
  escribe en la página de códigos) se ve igual que una falla del producto. El harness también
  necesita su denominador: que la aserción haya corrido.

**Procedimiento:** skill `designing-mechanical-guards`: *vacuous-green-detection* (las tres sondas: caminos de éxito, sujeto vacío, denominador) y *corruption-harness*.

## 4. Perímetros y listas con un solo dueño

- **El perímetro de una guarda vive en una constante, en un módulo**, y todo lo demás la
  importa. La guarda de datos personales que miraba `*.csv` dejó pasar un `.json`; desde
  entonces la lista de extensiones tiene un dueño y un test que la recorre.
- **La cobertura de un hook se cuenta sobre una lista declarada de consumidores** (cada
  agente que puede ejecutar la acción), y el chequeo pone rojo al que no tiene guarda.
  Esa lista y la de prefijos de rama de agente son **el mismo conjunto**, fijado por test.
- **Correr el comando, no leer el wrapper.** La cobertura se prueba mandando a cada hook el
  payload real de su agente (con los campos extra que trae) y exigiendo que bloquee.
- **Lo declarado no protege si el consumidor no lee la declaración:** el escaneo de secretos
  recorría el disco, no `git ls-files`, y el `.gitignore` no lo frenaba.

**Procedimiento:** skill `designing-mechanical-guards`: *guard-perimeter* (perímetro que debería ser contra el real, extensiones, ignore file, checkout) y *agent-cli-hook-semantics* (verificar un hook corriéndolo).

## 5. Una regla, una implementación

- Una regla de negocio ("este registro no es un cliente real", "qué semana es") vive en un
  módulo. Un test busca copias: prohíbe la llamada cruda (`.isocalendar()`, el patrón de
  exclusión) fuera de ese módulo.
- Un chequeo **importa** la regla que verifica; si tiene su propia copia, verifica su copia.
- Los archivos de entrada (doc raíz, skills del proyecto, panel) **no llevan cifras a mano**
  que el código mide: un chequeo marca el número pegado a un sustantivo medido (`chequeos`,
  `tests`, `validaciones`) que no coincide con el de hoy, salvo que esté fechado como
  historia ("el 07/10 eran…"). Lo que se mueve con cada unidad de trabajo se cita como
  propiedad.
- `getattr(obj, "x", default)` sobre un atributo que nadie escribe es **cableado fantasma**:
  el default se lleva toda la carga en silencio (ver `scripts/phantom_wiring.py`).

**Procedimiento:** skill `designing-mechanical-guards`: *text-vs-measurement-guards* (prosa contra el valor medido) y *guards-over-machine-state*.

## 6. La guarda que pagaba el costo de lo que rechaza

Si hay una forma barata de decidir que algo se descarta, va **antes** del trabajo caro.
Medido: el lector de exports parseaba el archivo entero y **recién ahí** preguntaba si
estaba truncado; un solo archivo rechazado costaba el 42% del parseo de la compuerta, y la
verificación barata (contar filas contra el techo del formato, mil veces más rápida) ya
existía. Invertir el orden bajó la compuerta de 71 s a ~38 s, y un test falla si alguien lo
vuelve a dar vuelta. El mismo
principio ordena la compuerta (§8) y el hook del ERP: un camino rápido por palabras clave,
y el análisis completo solo si alguna aparece.

**Procedimiento:** skill `designing-mechanical-guards`: *tiered-gates*, sección del rechazo barato.

## 7. Los permisos del agente son código

- Un permiso versionado con comodín que **no nombra el script** (`python *`) es ejecución
  arbitraria para todos los agentes que leen ese archivo: `python -c "…rmtree…"` pasa sin que
  nadie apruebe. El test que buscaba seis palabras peligrosas no lo veía: un test que busca
  palabras prueba que esas palabras no están, no el criterio.
- El criterio mecanizable: **el patrón nombra lo que corre** (`python -m pytest *`, `python
  tool.py sql *`). Un detector chico, un corpus de patrones que tiene que rechazar y otro que
  tiene que aceptar, y una aserción sobre el archivo real.
- Lo de la máquina (el intérprete suelto) va al archivo local ignorado, no al versionado.

**Procedimiento:** skill `designing-mechanical-guards`: *agent-cli-hook-semantics*, sección de permisos versionados.

## 8. La compuerta en capas, y medir antes de optimizar

- Orden por costo: secretos (sin escape) → lint → chequeos acotados por lo que el commit
  toca → tests en paralelo por archivo, solo si el commit toca código. La suite entera va
  en pre-push. Ante cualquier duda sobre qué toca el commit, se corre todo.
- **Una tabla de tests lentos** con su disparador (el archivo que ejercen) y un test que
  falla si una entrada deja de resolver: si no, un test lento queda salteado para siempre.
- **Medir antes de optimizar:** una bitácora por comando (veces, mediana, p90, máximo,
  fallas). La hipótesis "el escaneo tarda por recorrer el árbol" era falsa. Con varios
  agentes en la máquina, comparar CPU y alternar el orden: el tiempo de pared es ruido.

**Procedimiento:** skill `designing-mechanical-guards`: *tiered-gates* (nivel elegido desde el grafo de imports, fallback ruidoso, guarda de deriva).

## 9. Documentos que el código obliga a mantener

- **Diagramas con compuerta:** cada diagrama declara qué archivos describe; un commit que
  toca uno queda frenado hasta que se edite la especificación del diagrama o se suba su
  fecha de `revisado` (que es una afirmación de honor, y se dice así).
- **Planes:** la sección "cómo puede fallar → control" pedida en prosa la tenían 1 de 29
  planes; las decisiones, que tenían chequeo, 42 de 42. Una regla nueva sobre un corpus viejo
  se exige **por fecha de corte**: exigirla pareja nace roja sobre todo lo anterior.
- **El panel no cita conteos que se mueven:** cita propiedades (ver §5).

**Procedimiento:** skill `designing-mechanical-guards`: *promoting-advisory-checks*, sección de la fecha de corte.

## 10. Guardas nuevas: primero en sombra

Un hook de cierre de sesión ("código sin test, cifra sin validación, trabajo suelto") arrancó
**en modo sombra**: escribe lo que habría bloqueado sin bloquear, y se prende cuando su tasa de
falsos positivos medida es aceptable. Una guarda que bloquea mal el primer día se desactiva el
segundo, y con ella la confianza en las demás.

**Procedimiento:** skill `designing-mechanical-guards`: *promoting-advisory-checks*, *tuning-a-noisy-guard* y *advisory-to-enforcement*.
