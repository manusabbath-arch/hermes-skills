# Patrón de incidente — <NOMBRE>

> Ritual: cuando un agente o el sistema comete un error, NO basta con
> corregirlo. Se mecaniza en la misma sesión o se registra como deuda explícita.
> Orden de prelación: (1) si es mecanizable → check que falla el build;
> (2) si no → fila acá con fecha y evidencia, y nota de por qué no es check.

## Fecha

YYYY-MM-DD

## Síntoma (lo que se vio)

## Causa raíz (lo que realmente pasó)

## Firma detectable (el patrón que lo delata)

¿Qué se puede buscar en el código para encontrarlo de nuevo? Ej: "un
`getattr(obj, 'x', {})` que nadie asigna", "un `pytest | grep passed || fail`".

## ¿Es mecanizable?

- [ ] SÍ → crear el check/script/test y agregarlo a CI + pre-commit. Referenciar
      el archivo y el test acá.
- [ ] NO → explicar por qué (ej. necesita la DB de producción, requiere juicio
      humano). Registrar como deuda explícita.

## Evidencia

- Logs, queries, números reales. Un timestamp sin SHA es indistinguible de
  "cambié el .env y asumí que el código nuevo corría".

## Lección (una frase)

## ¿Recurrió antes?

Si sí, es un patrón sistémico: el check es obligatorio, no opcional.
