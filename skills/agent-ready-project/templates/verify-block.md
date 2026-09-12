# Bloque `<!-- verify -->` — especificación

Un doc puede afirmar números. El número tiene que ser **generado y chequeado**,
no tipeado y confiado. Este bloque es el contrato entre la prosa y el código.

## Formato

```markdown
El módulo principal tiene 1317 líneas tras la extracción.

<!-- verify
id: main-py-loc
kind: loc
target: src/main.py
expect: 1317
tolerance: 2%
-->
```

El bloque va **inmediatamente después** de la frase que afirma el número, para
que quien edite la prosa vea el contrato.

## Campos

| Campo | Obligatorio | Qué es |
|-------|-------------|--------|
| `id` | sí | Identificador único en todo el proyecto. Un duplicado es error, no warning. |
| `kind` | sí | `loc`, `files`, `matches` o `command`. |
| `expect` | sí | El número que la prosa afirma. |
| `target` | según kind | Path o glob relativo a la raíz. No puede escapar de la raíz. |
| `pattern` | `matches` | Regex a contar dentro de los archivos del target. |
| `command` | `command` | Comando cuya última línea de stdout es el número. Requiere `--allow-command`. |
| `tolerance` | no | Absoluta (`5`) o porcentual (`2%`). Sin ella, igualdad exacta. |

## Kinds

- **`loc`** — líneas del target (archivo o glob). El caso más común: el tamaño de
  un módulo que la doc usa para justificar un refactor.
- **`files`** — cantidad de archivos que matchean un glob. Sirve para "hay 14
  estrategias registradas".
- **`matches`** — ocurrencias de un regex. Sirve para "12 endpoints", "3 usos de
  la API vieja", "0 `TODO` sin ticket".
- **`command`** — cualquier número que un comando sepa producir (cobertura,
  tamaño de imagen, cantidad de filas). **Opt-in** porque ejecuta un proceso: un
  verificador que corre comandos arbitrarios sobre un repo no confiable es un
  vector, no un check.

## Elegir la tolerancia

- **Sin tolerancia** para números que solo cambian a propósito: cantidad de
  servicios, de estrategias registradas, de migraciones.
- **Porcentual (2–5%)** para números que se mueven con cada commit: líneas de un
  módulo, cobertura. Demasiado ajustada convierte el check en ruido y el equipo
  aprende a ignorarlo; demasiado floja deja pasar el drift que importa.
- La tolerancia NO es una excusa para dejar el número viejo: cuando se va de
  rango, se corre `--update` y se revisa que el número nuevo tenga sentido.

## Reglas de operación

- **Un target que no existe NUNCA da verde.** Es el drift más grave: el mapa
  perdió el territorio. Sale como error (exit 2), no como OK.
- **El bloque malformado es error, no se saltea en silencio.** Un verificador que
  ignora lo que no entiende es un gate que no puede fallar.
- **`--update` reescribe los `expect`**, para el commit que efectivamente cambió
  el número. Nunca correrlo "para poner todo en verde" sin leer el diff: ahí se
  pierde exactamente la señal que el check existe para dar.
- Correrlo en **pre-commit** (barato) y en **CI** (no eludible).

## Qué instrumentar primero

Los 3 números que la doc afirma y que envejecen más rápido. Típicamente:

1. El tamaño del módulo que la doc usa para argumentar arquitectura.
2. La cantidad de elementos de una lista que la doc enumera a mano.
3. Un número de cobertura o de performance que alguien citó una vez.
