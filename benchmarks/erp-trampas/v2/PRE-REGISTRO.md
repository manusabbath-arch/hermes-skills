# Pre-registro — benchmark de trampas de ERP, v2 (escrito antes de correrlo)

**Por qué hay una v2.** La v1 (31/10/26) no discriminó: 0 caídas en la trampa con y sin
skill, en Haiku y Sonnet. Su lectura (`../runs/2026-10-31/LECTURA.md`) dio tres causas:
archivos chicos que se leen enteros, preguntas que nombran la trampa y un caso ambiguo
(`t5`). La v2 cambia exactamente eso y nada más:

| | v1 | v2 |
|---|---|---|
| Tamaño | ~20 filas por export | más de 1.000 filas por archivo (2.200 en casi todos) |
| Cómo se responde | leyendo, cuentas a mano | el sujeto mira los archivos y entrega un script; el runner lo corre una vez y se puntúa lo que imprime |
| Preguntas | nombran la dimensión ("de la empresa A", "en pesos") | de negocio ("¿cuánto vendimos en julio?"); el contexto fijo dice quiénes somos, la moneda, el tipo de cambio y qué es el flete |
| `t5` | "en pesos" admitía dos lecturas | el tipo de cambio está en el contexto: la correcta es pesos + dólares convertidos |
| `t8` | un archivo con los dos exports pegados y un preámbulo que lo decía | dos archivos que se solapan del 8 al 10, y números repetidos entre series |
| Semilla | 20261031 | 20261101 |

**Fijado antes de la primera corrida (31/10/26):** los datos y la semilla (`generar.py`),
las preguntas y el contexto (`casos.json`), la instrucción y el filtro de scripts de
`../correr.py` (modo script), la puntuación (`../puntuar.py --suite v2`, tolerancia 0,5%).
Modelos: Haiku y Sonnet. **Tope: 2,5 USD** para toda la corrida (la v1 gastó 0,67 de un
tope de 5 USD aprobado para el benchmark; las dos juntas quedan dentro de ese tope).

**Criterios** (por modelo; iguales a los de la v1, más uno de discriminación):

| Métrica | Éxito si | Fracaso si |
|---|---|---|
| El benchmark discrimina: caídas (`I`) sin skill | ≥ 2 de 8 | ≤ 1 |
| Correctas con skill − correctas sin skill (de 8) | ≥ +2 | ≤ 0 |
| Caídas en la trampa (`I`) con skill | ≤ 1 | ≥ 3 |
| Negativos con skill | 2 de 2 correctos | alguno incorrecto |
| Palabras en negativos, con skill / sin skill | ≤ 1,5× | > 2× |

Si **no discrimina** (≤ 1 caída sin skill), las otras métricas no se leen como efecto de la
skill: se reporta que el benchmark sigue sin medir y por qué.

**Cómo se cuenta un script que no sirve:** rechazado por el filtro, que falla, que tarda
más de 120 s o que no imprime `CIFRA:` es `-` (fallo), y se reporta aparte cuántos hubo
por condición. No se corrige ni se vuelve a correr un script después de ver su error.

**Lo que esta versión todavía no mide:** el sujeto no ve la salida de su script (una sola
corrida, sin iterar), así que un error de ejecución que un agente con shell arreglaría
acá es un fallo. Es una condición más dura que la real; se declara, no se compensa.

**Lectura honesta:** con 8 casos por modelo, ±1 es ruido. Se publica tal como salga.
