# Decisión de infraestructura — <SISTEMA> / <DECISIÓN>

> Registrar TODA decisión de arquitectura (servidor externo vs local, proveedor,
> MCP, despliegue) con números reales medidos, no estimaciones. Mismo espíritu
> que el pre-registro: criterios fijados antes de ver los datos de rendimiento.

## Fecha

YYYY-MM-DD

## Decisión que se está evaluando

Ej: "¿exponer el estado del bot vía MCP externo o dashboard local?" ·
"¿consumir la API X externa o correr un recolector propio?"

## Criterios de decisión (fijados ANTES de medir)

| Criterio | Umbral de aceptación | Medido |
|----------|----------------------|--------|
| Latencia (p50/p95) | Ej: p95 < 2s | |
| Disponibilidad | Ej: > 99.5%, sin silencio | |
| Costo | Ej: $/mes < budget | |
| Cuota / rate-limit | Ej: cubre <pico> con margen | |
| Falla en silencio | Peor que local lento pero honesto → descarta | |

## Medición (números reales, por ciclo/día/cantidad)

- Qué se midió, con qué herramienta, en qué ventana (fecha + SHA si aplica).
- Distinguir SIEMPRE: dato medido vs estimación.

## Costo in-cycle vs CLI (si aplica)

- ¿La función se llama in-cycle? ¿Comparte default caro con un uso manual?
- Señal de costo in-cycle: los ciclos más lentos caen en múltiplos exactos
  (200, 400, 600…) = un `_EVERY_N_CYCLES` caro.

## Veredicto

- **Decisión:** externo / local / híbrido / descartado.
- **Con qué números** (citar los de la tabla).
- **Riesgo aceptado / deuda** (si falla, ¿a qué escala mediste?).

## Re-evaluación

- ¿Cuándo se re-mide? (cambio de cuota, de carga, de costo).
- Un proveedor que cambia sus términos o falla en silencio invalida el veredicto.
