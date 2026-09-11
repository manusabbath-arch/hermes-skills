# Pre-registro — <TEMA>

> **Regla:** este memo se escribe ANTES de ver los datos de la muestra. Si ya
> viste los datos, no es un pre-registro: es una hipótesis post-hoc y no
> autoriza gates ni capital.

- **Fecha:** YYYY-MM-DD
- **Autor / sesión:**
- **Estado en registry:** PROPOSED (→ TESTING cuando se instrumenta)

## Claim

Una frase falsable. Ej: "filtrar señales por `capturable=1` en el write path
hace que el veredicto de edge mida edge accionable en vez de edge de pantalla".

## Evidencia que lo motiva (si existe)

- Qué se midió, con qué n, en qué ventana.
- Distinguir SIEMPRE: dato medido vs. hipótesis. Un sweet spot minado post-hoc
  es una hipótesis, no un hallazgo.

## No-goals (explícito)

Qué NO se va a hacer aunque el claim se confirme. Ej: "no tocar
`INITIAL_CAPITAL` ni `FLAT_SIZE_PCT`".

## Métrica post-deploy

La query/log de PRODUCCIÓN que va a demostrar que el feature sirve, con valores
plausibles esperados. Si no se puede escribir esta verificación, el feature no
está terminado.

## Kill criteria (fijados ANTES de ver datos)

- **Kill:** <condición> a n≥<umbral>. Ej: "EV<0 a n≥80".
- **Success:** <condición> a n≥<umbral>. Ej: "EV≥0.05 a n≥80".
- **Robustez:** <si aplica> en ≥3/5 segmentos (ligas, mercados, cohortes).

## Réplica en muestra fresca

- Corte de frescura estricto: solo filas creadas DESPUÉS del deploy del flag.
- La muestra de descubrimiento NO participa en la réplica.

## Flags / gates

- Flag opt-in (default OFF) que activa el comportamiento.
- Shadow → observación → enforce. Nunca enforce desde paper.
