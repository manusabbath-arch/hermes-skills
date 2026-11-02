## Pedido 1

No puedo armar este informe con fuentes verificables ahora. No tengo acceso a búsqueda web ni a ejecución de comandos en esta conversación, y un informe sobre el "estado actual" de Sentinel-2 NDCI (índice de clorofila de diferencia normalizada) necesita páginas recuperadas. Si lo escribo de memoria, las citas y las URLs serían inventadas.

Lo que sí puedo decirte sin citar, como conocimiento general:
- El NDCI se calcula con bandas del borde rojo de Sentinel-2, normalmente (B5 − B4) / (B5 + B4). Se usa para estimar clorofila-a y floraciones de algas en aguas continentales y costeras.[unverified]
- No tengo cifras actuales de validación, productos operativos ni novedades recientes. Eso es lo que habría que buscar.

Para hacerlo bien necesito una de estas dos cosas:
1. Que me pases textos o enlaces ya recuperados, y armo el informe citando solo esos.
2. Que lo corras en un entorno con búsqueda web. Ahí registraría cada fuente en el ledger al recuperarla, citaría con `[n]` y verificaría el borrador antes de entregarlo.

## Pedido 2

No puedo confirmar cifras con evidencia textual porque no me pasaste ninguna cifra, borrador ni fuente. Para un tema médico no voy a "confirmar" nada de memoria.

Para hacerlo necesito:
- las cifras o afirmaciones concretas, y
- el texto de cada fuente (o acceso para recuperarlo).

Con eso, cada cifra llevaría una cita textual copiada de la página recuperada. Si la cita no aparece literalmente en el texto, se rechaza. Lo que no pueda respaldarse quedaría marcado como `[unverified]`, y las cifras en disputa se contrastarían con una segunda fuente independiente.

## Pedido 3

No veo el draft en esta conversación, así que no puedo corregirlo. Tampoco conviene arreglarlo a mano: renumerar a mano o retipear URLs es justo lo que genera el desajuste.

Lo correcto es regenerar el bloque desde el ledger:
```
python sources.py verify draft.md
python sources.py render --replace-in draft.md
python sources.py verify draft.md --strict
```
El primer comando muestra qué ids no coinciden. El segundo reescribe `## Sources` con los ids y URLs del ledger. El tercero confirma que quedó consistente.

Si me pegás el draft y la lista de fuentes con sus ids, te digo qué `[n]` están rotos y cuál debería ser cada uno. Si el ledger no existe, hay que reconstruirlo desde las URLs originales y no desde el texto del draft.

## Pedido 4

No puedo decirte qué opina la gente. No tengo acceso a Reddit, a feeds RSS ni a YouTube desde acá, y tampoco me dijiste cuál es "esto". Cualquier resumen que te diera sería inventado.

Con acceso a esas fuentes, el barrido sería así:
- Reddit: búsqueda y lectura de hilos.
- RSS: posts fechados y changelogs.
- YouTube: demos y charlas.
- Para cada plataforma, un informe aparte de qué cubrió y qué no devolvió resultados.

Los hilos de Reddit se presentarían como lo que los usuarios *reportan*, no como hechos. Decime el tema y si podés habilitar esas herramientas.

## Pedido 5

En Python 3.12 (PEP 701) los f-strings se pueden escribir así:

```python
nombre = "Ana"
f"Hola {nombre}"             # básico
f"{3.14159:.2f}"             # especificación de formato -> 3.14
f"{nombre!r}"                # conversión: !r, !s, !a
f"{x=}"                      # autodocumentado: muestra "x=valor"
f"{'a' + 'b'}"               # expresiones arbitrarias
f"{{llaves literales}}"      # llaves duplicadas para escaparlas
```

Novedades de 3.12:
- Se pueden reutilizar las mismas comillas dentro de la expresión: `f"{d["clave"]}"`.
- Las expresiones pueden ocupar varias líneas y llevar comentarios `#`.
- Se admiten barras invertidas dentro de la expresión, por ejemplo `f"{'\n'.join(lista)}"`.
- Los f-strings se pueden anidar a cualquier profundidad.

Antes de 3.12 nada de esto estaba permitido, y había que alternar tipos de comillas.
