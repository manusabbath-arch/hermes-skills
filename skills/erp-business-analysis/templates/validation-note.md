---
fecha: {{AAAA-MM-DD}}
tema: {{TEMA}}
estado: pendiente          # pendiente | pass | warn | fail
entidad: {{EMPRESA}}       # bajo qué razón social corrió; nunca "todas" implícito
tolerancia: "0.15%"
# Propagación de retracciones. Dejar "" lo que no aplique.
retractado: ""             # motivo, si esta validación se retracta
superseded_by: ""          # ruta de la nota que la reemplaza
depends_on: ""             # notas/informes de los que deriva
---

# Validación — {{TEMA}} ({{AAAA-MM-DD}})

**Resultado:** [PASS / WARN / FAIL en una frase, con la cifra]

## Fuente

<!-- Pegar el sello de provenance_seal.py; no re-tipear los datos del archivo. -->
> **Procedencia** — `archivo.csv` · entidad **X** · período dd/mm/aa – dd/mm/aa ·
> export AAAA-MM-DDTHH:MM:SS+00:00 · sha256 `xxxxxxxxxxxx` · N filas leídas, M descartadas

## Método

- **Qué se mide:** [la pregunta de negocio, en una frase]
- **Grano:** [documento / línea / producto / cliente / día]
- **Canario:** [fuente independiente contra la que se cruza el total]
- **Período de cada fuente cruzada:** [declarado en el preámbulo; si difieren, cómo
  se recortó o se declaró el desfasaje]
- **Hora del corte** (si se cruza contra la base viva): [hora del export]

## Resultado

| Métrica | Valor |
|---|---|
| Esperado (canario) | |
| Obtenido | |
| Delta | ( %) |
| Tolerancia | 0,15% |
| Veredicto | |

## Trampas encontradas

1. [Encoding, subtotales, columnas desplazadas, moneda, campos en cero guardado...]

## Reproducción

```bash
# El comando exacto que produce las cifras de arriba.
```

## Si esta validación corrige otra

- Qué cifra se retracta, dónde estaba publicada, y el `grep` que confirmó que no
  quedó viva en otro documento.
- Entrada agregada al libro de errores: [tipo N].
