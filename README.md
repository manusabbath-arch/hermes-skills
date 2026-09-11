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
