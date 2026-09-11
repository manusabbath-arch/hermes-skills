# hermes-skills

Skills reutilizables de Hermes Agent como GitHub tap. Agregar con:

```
hermes skills tap add manusabbath-arch/hermes-skills
```

Layout: cada skill vive en `skills/<nombre>/` con su `SKILL.md` y sus
plantillas (`templates/`), exactamente como los instala Hermes.

## Skills

| Skill | Propósito |
|-------|-----------|
| `empirical-project-playbook` | Método para proyectos empíricos construidos con agentes: anti-minería, checks que fallan el build, pre-registro, capa de análisis empresarial, capa de invariantes y veredictos (self-attesting), y aprendizajes transversales (CI/test, estructura, recolección de datos, know-how). Plantillas: pre-registro, checklist de checks, patrón de incidente, memo de infraestructura. |
| `empirical-system-invariants` | Batería operativa que convierte "¿funciona?" en respuesta mecánica: 5 contratos de datos por ciclo, regla de semáforo ROJO con eslabón exacto, NULL≠0, falla alto. Incluye `scripts/invariant_guard.py` (agnóstico, stdlib, exit code) + plantilla `templates/data-contracts.md`. Capa operativa de `empirical-project-playbook`. |
| `hermes-skills-tap-workflow` | Cómo publicar/propagar skills vía tap (este repo como fuente canónica). |

## Cómo editar y propagar un cambio de skill

1. Editar la skill en este repo (`skills/<nombre>/`).
2. Commit + push a `main`.
3. Re-instalar la skill desde el tap en cada perfil local que la usa:
   ```
   hermes skills install <repo>/<ruta>          # perfil default
   hermes --profile <nombre> skills install <repo>/<ruta>
   ```
   (o propagar los archivos manualmente al `skills/` del perfil,
   preservando `templates/`.)

El tap es la FUENTE canónica (para instalación y search); la copia instalada en
cada perfil es la que se carga. Un cambio al repo solo llega a los perfiles si
se re-instala la skill — no se propaga solo.
