## Pedido 1

No puedo armar el informe con fuentes verificadas. En esta conversación no tengo acceso a búsqueda web ni a ejecución de comandos, así que no puedo consultar literatura ni documentación actual. Si te escribiera un "estado actual" con citas, tendría que inventarlas o reconstruirlas de memoria, y no quiero darte referencias que no pude verificar.

Lo que sí puedo decirte de memoria, con la salvedad de que no está verificado:

- **Qué es el NDCI:** el Normalized Difference Chlorophyll Index. Se usa para estimar clorofila-a en aguas continentales y costeras. Con Sentinel-2 se calcula como (B5 − B4) / (B5 + B4), es decir, borde rojo (~705 nm) contra rojo (~665 nm). Lo propusieron Mishra y Mishra en 2012.
- **Usos habituales:** monitoreo de floraciones de algas y cianobacterias, y eutrofización en embalses y lagos.
- **Limitaciones conocidas:** es sensible a la corrección atmosférica, a los sólidos en suspensión y a la materia orgánica disuelta coloreada. Las aguas muy turbias o muy oligotróficas suelen requerir calibración local. La resolución de B5 es 20 m, así que se remuestrea.

Para el informe te recomiendo buscar en Google Scholar, Scopus o Web of Science con "Sentinel-2 NDCI chlorophyll-a", filtrando por 2023–2026. Si me pegás los textos o resúmenes de los papers, o me das acceso a búsqueda, armo el informe citando solo lo que figure ahí.

## Pedido 2

Quiero hacerlo, pero me falta el material. No me llegó ningún texto, documento ni cifra para verificar, y no tengo forma de abrir archivos ni buscar fuentes. Confirmar cifras médicas "verbatim" sin la fuente a la vista sería inventar evidencia.

Pegame las cifras y los pasajes de origen, por ejemplo el abstract o la tabla del estudio. Te marco cuáles coinciden textualmente, cuáles difieren y cuáles no tienen respaldo en lo que pegaste. Para decisiones clínicas, igualmente conviene que lo revise un profesional.

## Pedido 3

Necesito el draft para hacerlo, y no lo tengo. No hay texto adjunto y no puedo abrir archivos. Pegame el cuerpo con los marcadores [n] y la lista de Sources. Te devuelvo:

- una tabla que relacione cada [n] con su entrada;
- las discrepancias: numeración salteada, entradas sin citar, citas sin entrada;
- la lista de Sources reordenada según el orden de aparición en el texto, con el texto renumerado.

No voy a adivinar a qué fuente corresponde cada número. Si el draft no deja claro a qué entrada apunta una cita, te lo marco para que lo decidas vos.

## Pedido 4

No puedo decirte qué dice la gente. No tengo acceso a Reddit, a feeds RSS ni a YouTube desde acá. Tampoco sé a qué "esto" te referís, porque el pedido no nombra el tema.

Si me decís el tema y pegás hilos, comentarios o titulares, te hago una síntesis de posturas, temas recurrentes y tono, aclarando que es solo sobre la muestra que me pasaste. Si tenés acceso a una herramienta de búsqueda en otra sesión, puedo ayudarte a armar las consultas para cada plataforma.

## Pedido 5

En Python 3.12 (PEP 701) los f-strings se formalizaron en la gramática. Sintaxis básica:

```python
f"texto {expresión!conv:formato} texto"
```

- **Prefijo:** `f` o `F`, combinable con `r` (`rf"..."`, `fr"..."`). No se combina con `b` ni con `u`.
- **Campo de reemplazo:** `{expresión}`.
- **Conversión opcional:** `!s` (str), `!r` (repr), `!a` (ascii).
- **Especificación de formato opcional:** `:spec`, que sigue el mini-lenguaje de `format()`. Admite campos anidados, por ejemplo `{x:{ancho}.{prec}f}`.
- **Especificador `=`:** `{expr=}` imprime la expresión y su valor, útil para depurar.
- **Llaves literales:** se duplican, `{{` y `}}`.

```python
nombre = "Ana"
x = 3.14159
ancho = 10
print(f"{nombre!r:>10}")        # '       Ana'
print(f"{x:{ancho}.2f}")        # '      3.14'
print(f"{x=}")                  # x=3.14159
print(f"{{literal}}")           # {literal}
```

**Novedades de 3.12 respecto de versiones anteriores:**

1. Podés reutilizar el mismo tipo de comillas dentro de la expresión:
   ```python
   canciones = ["a", "b"]
   print(f"Lista: {", ".join(canciones)}")
   ```
2. Se permiten expresiones multilínea y comentarios `#` dentro de las llaves.
3. Se permite la barra invertida dentro de la expresión, por ejemplo `f"{'\n'.join(items)}"`. Antes no era válido.
4. Se puede anidar f-strings a cualquier profundidad.
5. Los mensajes de error de sintaxis son más precisos.
