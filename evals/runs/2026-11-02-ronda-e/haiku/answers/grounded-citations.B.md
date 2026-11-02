## Pedido 1

No tengo acceso a internet ni a herramientas de búsqueda en esta conversación, así que no puedo investigar el estado actual de Sentinel-2 NDCI ni citar fuentes recientes. Mi conocimiento llega hasta junio de 2026, y hoy es noviembre de 2026.

Lo que sí puedo darte es la base técnica, y dejar marcado qué habría que verificar:

- **Qué es:** el NDCI (*Normalized Difference Chlorophyll Index*) estima la clorofila-a en aguas continentales y costeras turbias a partir de las bandas *red-edge* de Sentinel-2 MSI. La fórmula es NDCI = (B5 − B4) / (B5 + B4), con B5 ≈ 705 nm y B4 ≈ 665 nm.
- **Referencia original:** Mishra & Mishra (2012), *Remote Sensing of Environment*, 117, 394–406. Verificá la cita en la fuente antes de usarla.
- **Lo que habría que actualizar:** versiones de los satélites (Sentinel-2A, 2B y 2C), validaciones regionales publicadas desde 2024, cambios en los productos L2A de Copernicus y calibraciones nuevas para aguas oligotróficas o cianobacterias.
- **Para el informe con fuentes:** buscaría en Copernicus Data Space Ecosystem (documentación de productos), artículos de 2024–2026 en *Remote Sensing of Environment*, *Remote Sensing* (MDPI) e *International Journal of Applied Earth Observation and Geoinformation*, y en la documentación de la ESA.

Si me pasás tu lista de fuentes o un texto base, puedo ayudarte a armar el informe con lo que tengas.

## Pedido 2

No recibí ningún texto con cifras que confirmar. Pegámelo aquí y lo reviso cifra por cifra, con la cita textual de la evidencia para cada una. Si alguna cifra no aparece en el material, la marco como no respaldada.

## Pedido 3

No tengo el draft ni la lista de Sources en esta conversación, así que no puedo corregir la numeración de los [n]. Pegame el texto del draft y la lista de fuentes, y te devuelvo el draft con las referencias alineadas y una tabla con los cambios hechos.

## Pedido 4

No puedo consultar Reddit, feeds RSS ni YouTube desde aquí, así que no tengo opiniones actuales sobre el tema. Si me decís de qué se trata, puedo:

- Decirte qué tipo de discusiones suelen aparecer en esos canales, con la salvedad de que no son datos actuales.
- Armarte consultas de búsqueda y una forma de muestrear comentarios para que lo hagas vos.

Si pegás los comentarios o los títulos que ya tengas, los resumo y separo por postura.

## Pedido 5

En Python 3.12, un f-string es un literal con prefijo `f` (o `F`) en el que las expresiones entre llaves `{}` se evalúan y se insertan en el texto:

```python
nombre = "Ana"
precio = 1234.5
print(f"Hola {nombre}, total: {precio:,.2f}")   # Hola Ana, total: 1,234.50
```

Sintaxis de cada campo de reemplazo:

```
{expresión!conversión:especificador_de_formato}
```

- `!r`, `!s` o `!a` aplican `repr()`, `str()` o `ascii()` antes de formatear.
- `{{` y `}}` producen llaves literales.
- Con `=` al final de la expresión (`{x=}`) se imprime la expresión y su valor.

Lo específico de 3.12 es PEP 701, que cambia la gramática de los f-strings:

- Podés reutilizar las mismas comillas dentro de la expresión: `f"{d["clave"]}"` ya no da error de sintaxis.
- Podés usar barras invertidas dentro de la parte de la expresión: `f"{'\n'.join(lineas)}"`.
- Podés poner comentarios `#` dentro de expresiones de varias líneas.
- Podés anidar f-strings con cualquier nivel de profundidad: `f"{f"{x}"}"`.

En versiones anteriores a 3.12, todo esto era un error de sintaxis o estaba prohibido.
