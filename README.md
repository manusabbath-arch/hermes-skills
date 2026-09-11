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
| `empirical-project-playbook` | Método para proyectos empíricos construidos con agentes: anti-minería, checks que fallan el build, pre-registro, capa de análisis empresarial. Destila las lecciones del polymarket-trading-bot en una capa portable. Plantillas: pre-registro, checklist de checks, patrón de incidente, memo de infraestructura. |

## Cómo editar

1. Editar en este repo (`skills/<nombre>/`).
2. Commit + push.
3. Propagar a los perfiles locales que lo usan (la skill del tap se puede
   instalar/sincronizar desde el repo).
