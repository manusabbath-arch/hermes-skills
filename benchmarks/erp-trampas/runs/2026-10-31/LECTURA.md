# Corrida 2026-10-31 — Haiku y Sonnet: el benchmark no discrimina

**Resultado contra el pre-registro:** fracaso. Correctas con skill − sin skill: Haiku −1,
Sonnet +1 (el éxito pedía ≥ +2). Caídas en la trampa: **0 en las cuatro condiciones**, con y
sin skill. Negativos: 2 de 2 en todas. Palabras en negativos con skill / sin skill: Haiku
1,35×, Sonnet 1,1× (dentro de lo fijado). Gasto: 0,67 USD de un tope de 5 USD, 40 llamadas.
La tabla, regenerada por el CI desde las respuestas crudas, está en `results.md`.

## Qué dice

**Ninguna trampa trampeó a un modelo sin skill.** El benchmark mide algo que los dos modelos
ya hacen bien en estas condiciones, y la skill no tiene margen para sumar. No prueba que la
skill no sirva: prueba que **estas ocho trampas, así presentadas, no la miden**.

Por qué, leyendo las respuestas:

1. **Archivos chicos y sin código:** el sujeto lee cada fila. Un `TOTAL GENERAL`, un
   encabezado repetido o una fila en `U$S` se ven a simple vista en 20 filas. En el origen,
   la trampa mordía porque el agente **escribía código** sobre miles de filas y nunca miraba
   la fila mala.
2. **Las preguntas nombran la dimensión de la trampa:** "de la empresa A", "en pesos", "sin
   contar el flete (ENVÍO)", "la empresa A" con un preámbulo que dice "(todas)". Una pregunta
   así es la mitad del freno. En el origen, la pregunta era "¿cuánto vendimos?".
3. **Los dos `O` son el mismo defecto del caso, no del modelo:** en `t5_monedas`, "¿cuánto se
   vendió en pesos?" admite dos lecturas (las ventas en pesos, o el total convertido a pesos).
   Haiku con skill y Sonnet sin skill tomaron la segunda, no encontraron tipo de cambio y
   contestaron `NO DETERMINABLE`, explicando las dos cifras. Es una respuesta defendible; por
   el pre-registro se puntúa como quedó y el caso se corrige en la próxima versión.

## Qué cambia para la próxima versión (v2 del benchmark, con su propio pre-registro)

- Exports de miles de filas, con la ejecución de código permitida (en un directorio aislado):
  es la condición en la que la trampa aparece de verdad.
- Preguntas de negocio que no nombran la trampa ("¿cuánto vendimos en junio?",
  "¿cuánto cobramos en la quincena?").
- `t5_monedas` sin ambigüedad: o se da el tipo de cambio en el preámbulo, o se pregunta por
  las ventas "en moneda nacional".
- Cambiar la semilla: estos datos y sus respuestas ya son públicos.
