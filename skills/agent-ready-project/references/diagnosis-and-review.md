# Diagnóstico antes del arreglo, y cómo recibir una revisión — referencia

Dos disciplinas que el proyecto NG adaptó de `systematic-debugging` y
`receiving-code-review` de [obra/superpowers](https://github.com/obra/superpowers)
(MIT), llevadas a un repo donde se rompen **cifras** tanto como código.

## Contents

1. Diagnóstico: la ley y las cuatro fases
2. Señales de que te salteaste la fase 1
3. Recibir una revisión: verificar antes de aplicar
4. Cuándo se rebate y cómo se responde

## 1. Diagnóstico: la ley y las cuatro fases

**Sin causa raíz no hay arreglo.** Subir una tolerancia, filtrar la fila rara,
re-sellar la línea base o mover un umbral hasta que dé verde son arreglos de
síntoma; en un repo de análisis, un síntoma tapado es una cifra equivocada que ya
salió a alguien.

**Fase 1 — Mirar lo que hay, no lo que uno supone.**
1. Leer el error entero: la traza, el encabezado del informe, el mensaje del check
   **con su denominador**.
2. Reproducirlo con un comando a demanda. Si no se reproduce, se juntan datos; no
   se adivina.
3. Qué cambió: `git log` del archivo y de su check; para una cifra, la hora del
   export contra la base viva.
4. En un sistema de capas (export → lector → script → check → panel), medir qué
   entra y qué sale en cada borde y ubicar **la capa** antes de abrir ninguna.
5. Seguir el valor malo hacia atrás hasta donde nace; se arregla ahí.

**Fase 2 — Descartar las causas ya conocidas.** Antes de una hipótesis nueva,
recorrer el catálogo propio (libro de errores, patrones de incidente). Y buscar algo
parecido que **sí funciona** en el repo y compararlo línea por línea: toda diferencia
cuenta hasta probar que no importa.

**Fase 3 — Una hipótesis, una prueba.** Escribirla ("creo que X porque Y"); si no
se puede escribir, no es una hipótesis. Probarla con el cambio más chico, **de a una
variable**. Si no se confirma, hipótesis nueva; no se apila un arreglo sobre otro.
"No sé" es una respuesta válida; inventar una causa plausible es fabricación.

**Fase 4 — Arreglar en la causa.** Primero el test o check que reproduce el fallo,
visto en rojo. Un solo arreglo. Verde, y correr lo que podría haber roto. Si era una
cifra publicada, se retracta con su bloque de corrección; no se reescribe en
silencio.

**Tres arreglos fallidos seguidos: se para.** No es mala suerte: el diseño o el
diagnóstico están mal. Volver a la fase 1 y plantearlo a una persona antes del
cuarto intento.

## 2. Señales de que te salteaste la fase 1

- "Arreglo rápido ahora y después lo miro."
- "Probablemente es…" sin haberlo reproducido.
- Subir la tolerancia, filtrar la fila o re-sellar "para destrabar".
- Cambiar varias cosas a la vez y correr la suite a ver qué pasa.
- Culpar a la fuente externa sin haber comparado el archivo contra sí mismo.
- Proponer el arreglo antes de saber en qué capa está la falla.

Y lo que nunca se hace para diagnosticar: escribir en producción "para probar",
re-sellar para silenciar un rojo que no se entiende, saltar una guarda sin el motivo
escrito en el commit.

## 3. Recibir una revisión: verificar antes de aplicar

Lo que importa es si la observación es correcta, no quedar bien. Un comentario de
otro agente o de un revisor automático es una afirmación más.

1. **Leer todo** antes de tocar nada: los puntos suelen estar relacionados.
2. **Reformular** cada punto como requisito técnico; si no se puede, no está claro.
3. **Si algo no está claro, preguntar todo junto** antes de cambiar nada.
4. **Verificar contra el repo:** ¿es cierto? ¿rompe algo? ¿por qué estaba hecho así?
   (`git log`, la validación que lo justificó, el test que lo fija).
5. **Responder:** aplicarlo o rebatirlo con argumento técnico.
6. **Aplicar de a uno**, cada uno con su test en verde.

Si la revisión objeta una cifra publicada, no se corrige al pasar: se verifica contra
la fuente (canario) y, si estaba mal, se retracta; si estaba bien, se responde con la
validación que la sostiene.

## 4. Cuándo se rebate y cómo se responde

Se rebate cuando la sugerencia rompe algo que hoy funciona (o un test que existe por un
caso real), contradice una regla medida del repo (un revisor genérico sugiere
`IS NULL` donde se midió que el detector es `= 0`), agrega algo que nadie pidió, o el
revisor no tenía el contexto (no vio la validación ni el incidente).

Cómo responder:
- Sin frases de compromiso antes de verificar ("¡tenés razón!", "ya lo implemento").
- Un punto correcto se reconoce con el cambio: "Corregido: <qué>, en `<archivo>`".
- Uno incorrecto, con el porqué y la evidencia (archivo, test, validación fechada).
- Uno dudoso, con la pregunta concreta.
- Si después resulta que el revisor tenía razón, se dice y se corrige.

Una revisión **no autoriza** acciones irreversibles: escribir en producción, push
forzado, saltar guardas, re-sellar la línea base. Esa confirmación es de una persona.
