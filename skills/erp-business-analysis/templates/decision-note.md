---
tema: {{TEMA}}
fecha_creacion: {{AAAA-MM-DD}}
estado: abierta              # abierta | decidida | rechazada | superada
dueño: {{DUEÑO}}             # una persona, no "el equipo"
fecha_limite: ""             # solo si hay una fecha REAL; nunca inventada
disparador_revision: {{DISPARADOR}}   # el evento que obliga a volver a mirarla
fuente: {{DOCUMENTO_ORIGEN}} # el análisis vive allá, no acá
superseded_by: ""
# Ciclo de resultado (optativo). Quien escribe hipotesis Y metrica_esperada se
# compromete a medir: al cerrar, completar resultado_observado y estado_evaluacion.
hipotesis: ""
metrica_esperada: ""         # con su línea base, tomada antes de actuar
resultado_observado: ""
estado_evaluacion: ""        # confirmada | refutada
---

# {{TITULO}}

## La decisión que pide

[Una o dos frases: qué hay que decidir. No el análisis completo.]

## Por qué importa

[Plata, riesgo o qué desbloquea. Si hay una cifra, con su procedencia; si hay dos
métodos de valuación, el rango, nunca un solo número elegido.]

## Premisas

- [Premisa] — **declarada por** [dueño, fecha] | **medida** en [validación, fecha]

Lo declarado por el dueño manda; lo medido se revisa. Si la nota se relee semanas
después, re-medir las premisas medidas contra la base antes de usarla.

## Alternativas consideradas

- [Opción A]
- [Opción B]

## Qué hace falta saber, y de quién

[Mientras esté `abierta`, el agente prepara esto y pregunta; no implementa
suponiendo la respuesta.]

## Decisión tomada

[Vacío hasta que `estado` cambie. Al cerrar: qué, quién, cuándo — y el `estado`
del frontmatter cambia en el mismo commit, nunca uno sin el otro.]

## Resultado observado

[Vacío hasta la revisión. Una hipótesis escrita después del resultado no es una
hipótesis: si no era medible, vaciar `hipotesis` y `metrica_esperada`.]
