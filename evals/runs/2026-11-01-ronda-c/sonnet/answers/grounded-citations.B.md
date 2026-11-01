## Pedido 1

No pude armar el informe. En esta conversación no tengo búsqueda web ni forma de bajar páginas, y tampoco puedo correr comandos. Todo lo que escribiera sobre el estado actual de Sentinel-2 NDCI saldría de memoria, sin fuentes verificables, así que prefiero no inventar un informe con citas.

Con acceso a retrieval haría esto:
- Buscar y extraer fuentes primarias: documentación de ESA/Copernicus, papers sobre NDCI (índice de clorofila de diferencia normalizada) y productos operativos.
- Registrar cada URL en un registro numerado antes de escribir.
- Redactar con citas `[n]` por oración y generar el bloque `Sources:` a partir de ese registro.

Si me pasás textos o URLs ya recuperados, armo el informe con ellos.

## Pedido 2

Todavía no hay cifras que confirmar. No me llegó ningún borrador, afirmación ni fuente.

Para un tema médico, cada cifra necesita una cita textual copiada de la página extraída, no retipeada. Si no se puede sustentar así, se marca `[unverified]`. Pasame el texto con las cifras y el texto fuente de cada una. Con eso te digo cuáles aparecen literalmente en la fuente y cuáles no.

## Pedido 3

No recibí el draft, así que no puedo ver qué números no coinciden.

Tampoco conviene arreglarlo a mano. Renumerar o retipear el bloque Sources es justo lo que genera desajustes. El procedimiento correcto es regenerar el bloque desde el registro url→[n] con `render --replace-in` y después correr `verify`. Eso necesita ejecutar comandos, que acá no puedo.

Si pegás el draft y las URLs reales de cada `[n]`, te propongo la corrección. Si no está claro qué fuente corresponde a cada número, te lo marco en vez de adivinar.

## Pedido 4

No puedo decirte qué opina la gente. No tengo acceso a Reddit, RSS ni YouTube desde acá, y cualquier resumen sería inventado.

Además, no dijiste de qué tema hablás con "esto". Decime el tema y, si podés, pegá los hilos, posts o transcripciones. Los resumo atribuyendo cada afirmación a su plataforma. Separo lo que los usuarios *reportan* de lo que está comprobado, y te aviso qué plataformas quedaron sin cubrir.

## Pedido 5

Desde Python 3.12 (PEP 701), los f-strings se parsean con la gramática normal. Esto cambia lo que podés escribir dentro de las llaves.

Sintaxis base:
```python
f"texto {expresión!conv:formato} texto"
```
- `expresión` es cualquier expresión de Python.
- `!r`, `!s` y `!a` son las conversiones opcionales.
- `:formato` es una especificación opcional, por ejemplo `:.2f`, `:>10` o `:%Y-%m-%d`.
- `{{` y `}}` producen llaves literales.
- `{x=}` imprime la expresión y su valor, por ejemplo `x=5`.

Novedades en 3.12:
```python
nombres = ["Ana", "Luis"]
f"Hola {", ".join(nombres)}"        # reutilizar las mismas comillas
f"{'\n'.join(nombres)}"             # barras invertidas dentro de la expresión
f"""{
    len(nombres)  # comentarios permitidos
}"""                                # expresiones en varias líneas
f"{f"{f"{1+1}"}"}"                  # anidamiento a cualquier profundidad
```

Antes de 3.12, no podías reutilizar el mismo tipo de comilla ni usar `\` o comentarios dentro de las llaves.
