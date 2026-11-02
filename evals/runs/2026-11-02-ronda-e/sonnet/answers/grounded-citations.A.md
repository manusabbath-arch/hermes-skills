## Pedido 1

No puedo hacer el informe con fuentes verificables. En esta conversación no tengo acceso a búsqueda web ni a navegación, así que no puedo consultar literatura ni documentación actual. Si te escribiera citas y enlaces de memoria, correría el riesgo de inventarlos.

Lo que sí puedo darte, sin citar fuentes:

- **Qué es el NDCI:** el Normalized Difference Chlorophyll Index estima la clorofila-a en aguas continentales y costeras. Usa las bandas del borde rojo de Sentinel-2, B5 (~705 nm) y B4 (~665 nm).
- **Fórmula:** NDCI = (B5 − B4) / (B5 + B4).
- **Uso típico:** monitoreo de floraciones algales y cianobacterias en lagos y embalses.
- **Limitaciones habituales:** hace falta corrección atmosférica y enmascarar nubes, sombras y brillo solar. B5 tiene 20 m de resolución, así que es menos útil en cuerpos de agua pequeños. Las aguas muy turbias o con mucho CDOM requieren calibración local.

Para el estado actual, buscá en Google Scholar o Scopus con "Sentinel-2 NDCI chlorophyll". Mirá también la documentación de ESA/Copernicus sobre Sentinel-2 y Sen2Cor/C2RCC. Si me pasás los textos o PDFs, armo el informe citando solo lo que figure ahí.

## Pedido 2

No puedo confirmar cifras con evidencia verbatim porque no recibí ningún texto ni cifra y no tengo acceso a fuentes. En un tema médico, una cifra sin cita textual verificable no debería darse por confirmada. Pegá acá las cifras y los pasajes de origen, o el documento. Voy a contrastar cada cifra con el texto exacto y te marco cuáles no figuran o difieren.

## Pedido 3

No tengo el draft, así que no puedo arreglar la numeración. Pegá el texto con los [n] y la lista de Sources. Con eso:

1. Listo los [n] en orden de aparición.
2. Los emparejo con las entradas de Sources.
3. Reordeno o renumero para que coincidan.
4. Te marco las referencias huérfanas, es decir, citadas pero ausentes de la lista o al revés.

## Pedido 4

No puedo ver lo que dice la gente en Reddit, RSS o YouTube. No tengo acceso a internet en esta conversación, y cualquier resumen que hiciera sería inventado. Tampoco me dijiste cuál es el tema de "esto". Decime el tema y pegame hilos, comentarios o transcripciones. Con eso te armo un resumen de posturas, temas recurrentes y tono. Si lo hacés vos mismo, buscá en Reddit por subreddit y ordená por "top" del último año. En YouTube leé los comentarios de los videos más vistos, y en RSS filtrá por palabras clave.

## Pedido 5

En Python 3.12 un f-string es un literal de cadena con prefijo `f` o `F`. Las expresiones van entre llaves:

```python
nombre = "Ana"
f"Hola, {nombre}"
```

**Sintaxis dentro de las llaves:** `{expresión !conversión :formato}`

- **Expresión:** cualquier expresión de Python.
- **Conversión (opcional):** `!r` (repr), `!s` (str) o `!a` (ascii).
- **Formato (opcional):** va después de `:` y sigue el mini-lenguaje de formato.

```python
x = 3.14159
f"{x:.2f}"        # '3.14'
f"{nombre!r}"     # "'Ana'"
f"{1000000:,}"    # '1,000,000'
f"{x=}"           # 'x=3.14159' (autodocumentado)
f"{'a'}{{}}"      # llaves literales: se duplican {{ }}
```

**Novedades de 3.12 (PEP 701):**

- Podés reutilizar las mismas comillas dentro de la expresión: `f"{", ".join(lista)}"`.
- Se permiten expresiones multilínea y comentarios `#` dentro de las llaves.
- Se permite la barra invertida dentro de la expresión: `f"{'\n'.join(lista)}"`.
- Se pueden anidar f-strings a cualquier profundidad.
- Los mensajes de error son más precisos.

Los f-strings también admiten campos de formato anidados, por ejemplo `f"{x:{ancho}.{prec}f}"`. Se pueden combinar con `r` en `rf"..."`, pero no con `u` ni `b`.
