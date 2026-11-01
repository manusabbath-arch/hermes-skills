## Pedido 1

Se puede, y hay dos caminos principales:

**1. Claude Code en modo headless + un scheduler**
- Corrés `claude -p "<instrucción>"` (modo no interactivo) desde un script que lance tus evals y resuma los resultados. Podés pedir salida en JSON con `--output-format json` para procesarla.
- Lo programás con lo que ya tengas:
  - **GitHub Actions** con `on: schedule: - cron: "0 3 * * *"` (la opción más simple si el código está en GitHub).
  - **cron** en Linux/macOS o **Task Scheduler** en Windows.
- La API key va como secreto (`ANTHROPIC_API_KEY`), nunca en el repo.

**2. Agent SDK / API directamente**
- Si las evals ya son un script (Python/TypeScript), lo ejecutás de noche con el scheduler y usás el SDK para llamar a los modelos y puntuar.

**Para que "llegue el resultado":**
- Que el script termine escribiendo un resumen (pasaron/fallaron, comparación con la corrida anterior) y lo envíe a Slack (webhook entrante), email o lo comente en un issue.
- Hacé que falle con código de salida distinto de cero si hay regresiones, así el scheduler marca la corrida en rojo.

**Recomendaciones:**
- Guardá los resultados históricos (artefactos o una tabla) para detectar tendencias, no solo el estado de esa noche.
- Fijá la versión del modelo y usá temperatura baja para reducir ruido entre corridas.
- Poné un límite de costo/tiempo por corrida.
- Avisá también si la corrida **no se ejecutó**. Un scheduler que falla en silencio es peor que uno que falla ruidosamente (conecta con tu segundo pedido).

Si me decís dónde corre el código (GitHub, servidor propio, Windows) y cómo están hechas las evals, te armo el workflow o el script concreto.

## Pedido 2

No, no está bien: es un falso verde. "Sin errores" y "todo sano" no son lo mismo. La ausencia de log de respaldo es justamente la señal de que el respaldo probablemente no corrió, y tu tablero la interpreta como éxito porque solo busca errores.

**Cómo corregirlo:**
- **Chequeá la presencia positiva de éxito**, no la ausencia de fallos: "existe un log de respaldo de ayer *y* indica que terminó bien".
- **Tres estados, no dos**: verde (evidencia de éxito), rojo (error explícito) y **gris/amarillo "sin datos"** (no hay log o está desactualizado). Faltar datos nunca debe verse verde.
- **Verificá frescura**: fecha del último respaldo exitoso, con umbral (por ejemplo, rojo si pasaron más de 26 h).
- **Verificá el resultado real**: tamaño no nulo, o mejor, una prueba periódica de restauración.
- **Alertá por ausencia** (patrón "dead man's switch"): que el respaldo avise al terminar y que se dispare una alerta si no llega el aviso a tiempo.

Es la misma lógica que aplica a tus evals nocturnas: si no corren, el tablero tiene que ponerse en rojo, no quedarse en verde.

## Pedido 3

El 15% de 2.400 es **360**.

(2.400 × 0,15 = 360)
