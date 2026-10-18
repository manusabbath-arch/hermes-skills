## Pedido 1

"Corre sin errores" no prueba nada: un campo que nunca se escribe no tira excepción, queda NULL. Hay que pasar de "funciona" a una verificación mecánica por ciclo. Supuesto: es un pipeline con base de datos y varias etapas (ingesta, transformación, enriquecimiento, decisión, registro).

Qué haría:

1. **Inventario de contratos.** Para cada etapa listo etapa fuente, etapa consumidora y campo prometido. Los campos sospechosos van primero.
2. **Condición de "poblado" por campo.** No alcanza con "hay filas". Pido valores plausibles en filas posteriores al último deploy, por ejemplo "al menos X% no-NULL y dentro de rango".
3. **Query de producción antes de tocar código.** Por ejemplo, el conteo de no-NULL por campo en las últimas 24 h, leído con una conexión nueva y no la del pool. Un getter que traga excepciones devuelve `[]` en silencio y oculta el problema.
4. **Declarar NULL vs 0 por campo.** "Ausente" es defecto, y "0 medido" es dato legítimo.
5. **Buscar wiring fantasma.** Reviso `getattr` con default que nadie asigna, flags declarados que la config real no tiene, y campos de fuentes externas con 0 de N filas pobladas.
6. **Guard por ciclo.** Un script que lee el contrato (JSON), corre los checks y sale con exit 1 si alguno falla, indicando el eslabón y valor esperado vs real. Lo corro con cron o systemd timer y guardo el resultado en un fichero de estado, sin depender de logs que rotan.

Primero lo corro solo como monitor, durante horas, y recién después lo convierto en gate de deploy. Los campos que den 0 de N no-NULL son los que hay que arreglar. Si el código que los escribe nunca existió, es un defecto.

## Pedido 2

Un guard que da ROJO todos los días por un campo que vale 0 legítimamente está confundiendo "0 medido" con "campo ausente". Eso genera fatiga de alertas: el equipo termina ignorando el rojo, y se pierde la utilidad del guard.

Arreglo, sin silenciar nada ni bajar el check:

1. **Declarar la semántica en el contrato.** Para ese campo, escribir explícitamente que 0 es dato legítimo y que el defecto es solo NULL (`IS NULL`), no `= 0` ni un chequeo de "falsy".
2. **Corregir la condición.** Cambiar `if not value` por `value is None`. Es un bug clásico de Python/SQL que trata 0 como vacío.
3. **Exigir otra evidencia de que se pobló.** Por ejemplo, que la fila exista post-deploy, que el campo sea no-NULL y que la distribución no sea 100% constante. Si siempre fuera 0 en todas las filas, eso sí podría indicar un campo que nunca se escribe. Ahí lo distingo con una query de aceptación sobre una ventana larga.
4. **Gemelo de frontera.** Un test con un fixture 0 (debe dar verde) y otro con NULL (debe dar rojo), para probar que el check no pasa por accidente.

No agregaría `|| true`, `continue-on-error`, ni un allowlist ciego que ignore el campo. El campo sigue vigilado, pero con la regla correcta. Supuesto: el 0 es realmente esperado por negocio. Si hubiera días con 0 y días con valores, verificaría la ventana antes de dar el cambio por bueno.

## Pedido 3

Puedo hacerlo, pero no con un try/except que se trague el error: eso convertiría un guard roto en un guard "verde", que es justo el silencio traidor que el guard debe evitar. Un `except: pass` en un check de invariantes está prohibido.

Lo que sí hago para que el ciclo no se rompa:

```python
import logging, sys, traceback
log = logging.getLogger("invariants")

def run_guard_safely(run_checks, write_state, notify):
    try:
        results = run_checks()          # lista de (eslabon, esperado, real, ok)
    except Exception:
        # El guard mismo fallo: esto es ROJO, no verde.
        log.error("INVARIANT GUARD CRASHED\n%s", traceback.format_exc())
        write_state({"status": "RED", "link": "guard_execution",
                     "detail": traceback.format_exc()})
        notify("Invariant guard no pudo ejecutarse")
        return 1                        # exit code distinto de 0
    reds = [r for r in results if not r[3]]
    write_state({"status": "RED" if reds else "GREEN", "failures": reds})
    return 1 if reds else 0
```

Puntos clave:

- El ciclo de producción sigue (el llamador captura el exit code y no aborta el resto), pero el estado queda marcado ROJO.
- Se loguea el traceback completo y se persiste en el fichero de estado, más una notificación.
- Una excepción del guard nunca se reporta como "todo verde".
- Un kill switch (flag OFF) permite desactivar el check nuevo mientras se estabiliza, sin romper deploys.

Supuesto: el guard corre separado del trabajo principal del ciclo. Si me pasás el código real, lo adapto.
