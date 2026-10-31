# Pre-registro — benchmark de trampas de ERP (escrito antes de correrlo)

**Qué se mide:** en 8 exports con una trampa conocida cada uno, cuántas veces el agente da
la cifra correcta y cuántas la ingenua, con y sin `erp-business-analysis`. Más 2 negativos.

**Fijado antes de la primera corrida (31/10/26):** los datos (`SEMILLA = 20261031`), las
preguntas (`casos.json`), la instrucción y las herramientas de `correr.py`, y la puntuación
(`puntuar.py`, tolerancia 0,5%). Cambiar cualquiera después de ver resultados es minería:
si hay que cambiarlo, se dice acá con fecha y se vuelve a correr todo.

**Criterios:**

| Métrica (por modelo) | Éxito si | Fracaso si |
|---|---|---|
| Correctas con skill − correctas sin skill (de 8) | ≥ +2 | ≤ 0 |
| Caídas en la trampa (`I`) con skill | ≤ 1 | ≥ 3 |
| Negativos con skill | 2 de 2 correctos | alguno incorrecto |
| Palabras en negativos, con skill / sin skill | ≤ 1,5× | > 2× |

**Una trampa que no discrimina** (sin skill, todos los modelos la aciertan) se reporta como
tal en el resultado, por caso: no se saca del conteo ni se reemplaza por otra.

**Lectura honesta:** con 8 casos por modelo, una diferencia de ±1 es ruido. El resultado se
publica tal como salga, incluido el fracaso.
