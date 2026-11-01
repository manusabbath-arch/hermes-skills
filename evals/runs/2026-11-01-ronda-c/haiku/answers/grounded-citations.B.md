## Pedido 1

No puedo hacer una investigación actual: no tengo acceso a la web en esta conversación, y mi conocimiento llega hasta junio de 2026, así que no sé el estado a noviembre de 2026. Lo que sí puedo darte es lo que sé de memoria, marcado como no verificado, y sin URLs inventadas.

- **Qué es:** NDCI (Normalized Difference Chlorophyll Index) es un índice para estimar clorofila-a en cuerpos de agua continentales y costeros. Se calcula como (B5 − B4) / (B5 + B4) en Sentinel-2 MSI, usando la banda del borde rojo (705 nm) y la roja (665 nm). [unverified]
- **Referencia original:** Mishra, S. & Mishra, D. R. (2012), *Remote Sensing of Environment*, 117, 394–406, sobre el índice. Lo recuerdo de memoria y no pude abrirlo para confirmarlo. [unverified]
- **Misión:** Sentinel-2 es de ESA dentro de Copernicus. Sentinel-2C se lanzó en 2024. [unverified]
- **Limitaciones conocidas:** el índice depende de la corrección atmosférica y pierde fiabilidad en aguas muy turbias o con mucha materia orgánica disuelta. [unverified]

Para un informe con fuentes verificables, necesito que tengas acceso a búsqueda web y que me digas qué región o aplicación te interesa.

## Pedido 2

No veo ninguna cifra para confirmar: el pedido llegó sin el texto ni archivos adjuntos. Pegame el texto médico (o el fragmento con las cifras) y te devuelvo cada cifra con la frase exacta de la fuente que la respalda. Si alguna cifra no aparece en la fuente, la marco como no respaldada en lugar de corregirla de memoria.

## Pedido 3

No recibí el draft, así que no puedo ver el bloque Sources ni los [n] del texto. Pegame el draft completo y, si tenés la lista de URLs que se registraron para cada número, pegala también. Sin esa lista no puedo saber qué URL corresponde a cada [n], así que no voy a adivinar el mapeo. Con ambas cosas reescribo el bloque Sources para que cada [n] apunte a su URL y te aviso de cualquier número que quede sin fuente.

## Pedido 4

No tengo acceso a Reddit, feeds RSS ni YouTube desde esta conversación, así que no puedo decir qué opina la gente. No quiero inventar comentarios ni citas. Si tu pregunta es sobre el NDCI del Pedido 1, puedo ayudarte a armar las búsquedas (subreddits de teledetección, feeds de blogs de agua o canales de YouTube de tutoriales de Sentinel-2) para que las revises vos. Conviene separar lo que la gente reporta de lo que está comprobado, porque un hilo de Reddit muestra opinión, no un hecho.

## Pedido 5

En Python 3.12 (PEP 701) las f-strings se pueden anidar sin límite y con las mismas comillas dentro de la expresión:

```python
nombre = "Ana"
f"Hola {nombre.upper()}"                  # Hola ANA
f"{'\n'.join(['a', 'b'])}"                 # las barras invertidas ya son válidas dentro de la expresión
f"{f"{nombre!r:>8}"}"                      # anidación; las mismas comillas están permitidas
f"{nombre=}"                               # "nombre='Ana'" (desde 3.8)
f"{3.14159:.2f}"                           # especificador de formato: "3.14"
```

Las partes principales son:
- `{expr}` evalúa la expresión e inserta el resultado.
- `!r`, `!s` o `!a` aplican una conversión antes del formato.
- `:spec` es el especificador de formato, como en `format()`.
- `{expr=}` imprime el texto de la expresión seguido de su valor.
- Las expresiones pueden ocupar varias líneas dentro de `"""..."""`, y también pueden llevar comentarios `#` en esas líneas.
