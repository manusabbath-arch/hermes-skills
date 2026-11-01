## Pedido 1

No puedo buscar en la web desde esta sesión, así que no puedo informarte el estado actual de Sentinel-2 NDCI con fuentes verificadas. Lo que sí puedo darte es el marco general, que suele ser estable:

- **Definición:** NDCI = (B5 − B4) / (B5 + B4), usando la banda roja-borde de 705 nm (B5) y la roja de 665 nm (B4) de Sentinel-2. Fue propuesta por Mishra & Mishra (2012), *Remote Sensing of Environment* 117: 394–406, como índice de clorofila-a para aguas turbias y productivas.
- **Uso típico:** estimar clorofila-a y detectar floraciones de algas en lagos, embalses y aguas costeras. Suele combinarse con correcciones atmosféricas (por ejemplo, Sen2Cor o ACOLITE) y con validación contra mediciones *in situ*.
- **Limitaciones conocidas:** sensibilidad a la corrección atmosférica, a la materia orgánica disuelta y a los sedimentos en suspensión, y necesidad de calibración local.
- **Misiones:** Sentinel-2A (2015), Sentinel-2B (2017) y Sentinel-2C (lanzado en septiembre de 2024) de la ESA.

Para el estado actual (versiones de algoritmos, calibraciones nuevas, estudios de 2025–2026), te recomiendo buscar en Google Scholar y Web of Science con "NDCI Sentinel-2", y revisar el catálogo de la ESA (Copernicus Data Space). Si me pegás artículos o resúmenes, los analizo y te armo el informe con las citas exactas.

## Pedido 2

No veo ningún texto ni documento en esta conversación, así que no tengo cifras que confirmar. Pegame el texto médico y, para cada cifra, te devuelvo la cita literal de la fuente que la respalda. Si una cifra no aparece en la fuente, te lo marco como "sin evidencia" en vez de darla por válida.

## Pedido 3

No tengo acceso al draft ni a su sección de Sources, así que no puedo corregirlo a mano. Pegame el texto con los marcadores [n] y la lista de Sources, y te devuelvo:

- la lista de Sources reordenada y numerada para que coincida con el orden de aparición en el texto;
- los [n] del texto ajustados;
- una lista de cualquier referencia citada que no tenga entrada, o de entradas que nunca se citan.

## Pedido 4

No puedo acceder a Reddit, feeds RSS ni YouTube desde aquí, así que no sé qué se dice ahora mismo. Para hacerlo, podés:

- copiar y pegar los comentarios o títulos relevantes, y te los resumo y clasifico por postura;
- usar la búsqueda de Reddit o YouTube con el término del tema y revisar las fechas;
- exportar los RSS con los títulos y fechas, y pasármelos.

## Pedido 5

En Python 3.12 un f-string es un literal con prefijo `f` en el que las expresiones entre llaves `{}` se evalúan y se formatean:

```python
nombre = "Ana"
edad = 30
print(f"{nombre} tiene {edad} años")       # Ana tiene 30 años
print(f"{edad + 1=}")                      # edad + 1=31  (forma de depuración)
print(f"{nombre!r:>10}")                   # conversión !r y especificador de formato :>10
print(f"{3.14159:.2f}")                    # 3.14
print(f"{'sí' if edad >= 18 else 'no'}")   # expresiones condicionales
```

Lo nuevo en 3.12 (PEP 701) es que la gramática de f-strings se volvió igual a la del resto del lenguaje:

- Podés reutilizar las mismas comillas dentro de las llaves: `f"{d["clave"]}"`.
- Podés usar barras invertidas dentro de las expresiones: `f"{'\n'.join(lineas)}"`.
- Podés anidar f-strings a cualquier profundidad: `f"{f"{x}"}"`.
- Podés poner comentarios `#` dentro de expresiones multilínea.

Las conversiones válidas son `!s`, `!r` y `!a`. Dentro del especificador de formato (después de `:`) podés anidar campos, por ejemplo `f"{valor:>{ancho}}"`.
