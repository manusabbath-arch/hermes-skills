## Pedido 1

No puedo hacer una investigación con fuentes en esta conversación: no tengo acceso a búsqueda web ni a páginas en vivo, y no puedo ejecutar comandos. Lo que sigue sale de mi conocimiento de entrenamiento, así que no lo tomes como estado actual ni como informe citado.

- **Qué es:** NDCI (Normalized Difference Chlorophyll Index) es un índice de clorofila-a para aguas continentales y costeras turbias. Se calcula con las bandas 5 (red edge, ~705 nm) y 4 (roja, ~665 nm) de Sentinel-2 MSI: NDCI = (B5 − B4) / (B5 + B4). Lo propusieron Mishra y Mishra (2012).
- **Estado actual:** no lo sé con certeza para 2026. Habría que revisar publicaciones recientes y los procesadores de Copernicus o de los proveedores de datos que usen NDCI.
- **Para armar el informe con fuentes:** buscaría el paper original de Mishra & Mishra (2012), revisiones posteriores sobre validación de NDCI en distintos cuerpos de agua, y documentación oficial de Copernicus Sentinel-2 sobre las bandas y su calibración. Si me pasás los links o textos, puedo armar el informe citando solo lo que aparezca en ellos.

## Pedido 2

No veo el texto ni las cifras que querés confirmar. Pegámelo con sus fuentes (o los links con el texto extraído de cada página) y reviso cada cifra. Para cada una te devuelvo el fragmento literal de la fuente que la respalda, o marco que no encontré evidencia. Si una cifra no aparece tal cual en la fuente, la voy a señalar como no verificada en lugar de darla por buena.

## Pedido 3

No tengo el draft ni la lista de fuentes, así que no puedo corregir el bloque Sources. Pegame:

1. El draft completo, con los `[n]` del texto.
2. La lista de URLs con su número (el id → URL que se usó al citar).

Con eso reescribo el bloque Sources a mano para que coincida con los `[n]` del texto: cada número citado aparece una vez, con su URL correspondiente, y no quedan números huérfanos ni URLs sin citar. Mi recomendación es que, si tenés acceso al script de la carpeta de trabajo, regeneres el bloque con él y no a mano, para evitar errores de transcripción.

## Pedido 4

No especificaste el tema y no tengo acceso a Reddit, feeds RSS ni YouTube desde acá. Decime qué es "esto" (producto, noticia, evento, etc.) y, si podés, pegá los posts, comentarios, entradas RSS o transcripciones que quieras analizar. Con eso puedo resumir qué dice cada plataforma, separando lo que la gente reporta como experiencia de lo que está verificado, y marcando dónde falta cobertura. Sin ese material no puedo decir qué opina la gente.

## Pedido 5

En Python 3.12 un f-string tiene esta forma:

```python
f"texto {expresión!conversión:especificador_de_formato}"
```

- **Expresión:** cualquier expresión válida dentro de `{}`.
- **Conversión (opcional):** `!r`, `!s` o `!a`, que aplican `repr()`, `str()` o `ascii()`.
- **Especificador de formato (opcional):** después de `:`, con la mini-sintaxis de `format()`, por ejemplo `{x:>10}` o `{x:.2f}`. Puede anidar otros campos: `{x:{ancho}.{prec}f}`.
- **Signo `=` (desde 3.8):** `f"{x=}"` imprime el nombre, el `=` y el valor.

Lo que cambió en 3.12 (PEP 701) es que las f-strings tienen gramática formal, así que ahora podés:

- Reutilizar las mismas comillas dentro de las llaves: `f"{d["clave"]}"`.
- Anidar f-strings: `f"{f"{x}"}"`.
- Usar barras invertidas dentro de la expresión: `f"{'\n'.join(lineas)}"`.
- Poner comentarios con `#` dentro de llaves en f-strings multilínea.
