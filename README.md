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
| `empirical-project-playbook` | Método para proyectos empíricos construidos con agentes: anti-minería, checks que fallan el build, pre-registro, capa de análisis empresarial, capa de invariantes y veredictos (self-attesting), capa de data-engineering y lakehouse (ETL→Delta→ML/agentes), y aprendizajes transversales (CI/test, estructura, recolección de datos, know-how). Plantillas: pre-registro, checklist de checks, patrón de incidente, memo de infraestructura. |
| `empirical-system-invariants` | Batería operativa que convierte "¿funciona?" en respuesta mecánica: 5 contratos de datos por ciclo, regla de semáforo ROJO con eslabón exacto, NULL≠0, falla alto. Incluye `scripts/invariant_guard.py` (agnóstico, stdlib, exit code) + plantilla `templates/data-contracts.md`. Capa operativa de `empirical-project-playbook`. |
| `delta-lakehouse` | ETL/data pipelines: extrae datos estructurados y no estructurados de orígenes heterogéneos, los almacena en un lakehouse Delta (historial de operaciones, time-travel, optimización de almacenado/lectura) y los conecta a entrenamiento de modelos IA / agentes. Stack validado: deltalake + duckdb + pyarrow. Plantilla: `templates/ingesta-plantilla.md`. |
| `data-medallion-architecture` | Diseño punta a punta de arquitectura de datos: elegir la FUENTE (API/DB/SFTP), armar la capa medallion Bronze→Silver→Gold (ingesta, transformación, almacenamiento en Delta lakehouse/DW), y llegar a CONSUMO (AI/ML/MCP/análisis) y dashboards de escenarios hipotéticos. Patrones de diseño y decisión de fuente. Plantilla: `templates/scenario-dashboard.md`. |
| `hermes-skills-tap-workflow` | Cómo publicar/propagar skills vía tap (este repo como fuente canónica). |

## Cómo editar y propagar un cambio de skill

Editar la skill en este repo (`skills/<nombre>/`), commit + push a `main`. El CI
(`.github/workflows/validate.yml`) valida manifests, rutas citadas y tests antes
de mergear.

### Propagación: symlink, no copia (recomendado)

Una copia instalada drifta respecto al tap y hay que re-instalarla a mano en cada
perfil. Un symlink no: el cambio en el repo es el cambio en el perfil, sin paso
intermedio.

```bash
for s in /ruta/al/tap/skills/*/; do
  n=$(basename "$s")
  ln -sfn "$s" ~/.claude/skills/$n     # Claude Code
  ln -sfn "$s" ~/.hermes/skills/$n     # Hermes (perfil default)
done
```

Ambos loaders resuelven symlinks (Hermes ya tiene 28 skills enganchadas así).

### Instalación por copia (`hermes skills install`)

Sigue funcionando y es lo correcto para consumidores externos del tap. Pero la
copia **no se propaga sola**: un cambio al repo solo llega al perfil si se
re-instala.

```
hermes skills install <repo>/<ruta>                   # perfil default
hermes --profile <nombre> skills install <repo>/<ruta>
```

## Checks del repo

El playbook que este tap publica dice: *"si es mecanizable, es check que falla el
build, no párrafo"*. El repo se aplica su propia regla.

```bash
python3 scripts/validate_skills.py   # manifests, descriptions, rutas citadas
python3 -m pytest skills -q          # tests de los scripts publicados
```

`validate_skills.py` falla el build si una skill pierde el frontmatter, si el
`name` no coincide con el directorio, si la `description` es un stub que no
dispara con nada, si el SKILL.md pasa las 500 líneas, o si el cuerpo cita una
plantilla/referencia que no existe.
