# Corrida v2, 2026-10-31 — Haiku y Sonnet: tampoco discrimina

**Resultado contra el pre-registro:** fracaso en el primer criterio, que manda sobre los
demás. Caídas en la trampa (`I`) sin skill: **0 de 8 en los dos modelos** (el éxito pedía
≥ 2). Con skill, también 0. Correctas con skill / sin skill: Haiku 5 / 8, Sonnet 5 / 5.
Negativos: 2 de 2 en las cuatro condiciones. Palabras en negativos con / sin skill: Haiku
1,05×, Sonnet 1,44× (dentro de lo fijado). Gasto: 1,17 USD de un tope de 2,5 USD, 40
llamadas, más 0,03 USD del ensayo declarado en la enmienda del pre-registro. La tabla, que
el CI regenera desde las salidas crudas, está en `results.md`.

Como no discrimina, la diferencia de correctas no se lee como efecto de la skill.

## Qué dice

Ninguno de los 80 sujetos de las dos versiones dio la cifra ingenua. Eso incluye la v2, con
archivos que no se leen enteros, preguntas que no nombran la trampa y la cuenta hecha por
un script. **Haiku y Sonnet ya ven solos estas ocho trampas** cuando cada archivo trae una
y la pregunta es concreta: miran el pie del archivo, leen las columnas por nombre, filtran
la empresa y convierten la moneda.

Las respuestas que no fueron `C` no son caídas. Leyendo cada una:

1. **Haiku con skill, 3 `-`: scripts más defensivos que se rompieron.**
   - `t6` y `t7`: el script buscaba el archivo con una ruta propia y no lo encontró. En
     `t7`, por ejemplo, abría `ventas_agosto.csv` sin la carpeta.
   - `t3`: decodificó como cp1252 un archivo que era UTF-8, por precaución. `Período` quedó
     con dos caracteres raros, la expresión regular no lo encontró y el script salió con
     error.

   Sin skill, los mismos casos salieron `C`. Con n = 8 es una sola observación, no un
   efecto medido, pero apunta en una dirección concreta: **la skill empuja a validar el
   encoding y el período, y un script que valida sin poder probarse falla más.**
2. **Sonnet, 4 `O` por NO DETERMINABLE.** Son `t1`, `t4` y `t5` sin skill, y `t5` con
   skill. El defecto está en el caso, no en el modelo. El contexto fijo de `casos.json` dice
   que el flete se factura como el producto ENVÍO. En los archivos sin columna de producto,
   Sonnet razonó que no podía excluir el flete y no dio la cifra. En las cuatro, el total que
   su script imprimió antes de esa línea era el correcto: 468550, 243590 y 827920.
   Ese contexto, que se escribió para `t7`, contaminó a los demás casos.
3. **Sonnet con skill, `t2` en `O`:** imprimió `CIFRA: 5.1705E+5`, que es la cifra correcta
   (517050) en notación científica. `puntuar.py`, fijado en el pre-registro, no lee
   exponentes. Se puntúa como quedó y no se toca el puntuador después de ver la corrida.
4. **Sonnet con skill, `t3` en `-`:** el script no compilaba (error de sintaxis).

## Qué se concluye

Dos versiones y 80 llamadas no muestran ni una caída. Hacer una v3 que siga ajustando las
trampas hasta que algún modelo caiga sería minería: el benchmark se termina diseñando para
que la skill gane. Lo que sí se sabe:

- **Lo que estos modelos no necesitan que les enseñe la skill:** una trampa aislada por
  archivo, de las ocho que costaron una cifra publicada en el proyecto de origen. En el
  origen, la trampa mordía con varias juntas, en un análisis de varios pasos y en una
  sesión larga, donde nadie volvía a mirar el pie del archivo. Este benchmark no reproduce
  esas condiciones.
- **Un costo posible de la skill en Haiku:** más validación dentro del script y más fallos
  de ejecución. Si se mide de nuevo, este es el efecto que conviene pre-registrar.
- **Dos defectos del instrumento, para quien lo reuse:**
  - el contexto compartido entre casos tiene que aplicar a todos; si no, introduce la
    ambigüedad que el caso quería sacar;
  - el puntuador tiene que leer notación científica.

**Recomendación:** cerrar la fase 5 con este resultado negativo documentado, en lugar de
abrir una v3. Si se vuelve a medir, que sea con otra pregunta: una tarea de varios pasos
sobre exports con varias trampas juntas, con shell y con su propio pre-registro.

**Nota sobre las salidas crudas:** en 3 archivos (`.txt`/`.err` de Haiku), la ruta del
temporal de la máquina que corrió la prueba se reemplazó por `<tmp>` antes de publicar,
porque traía el nombre de usuario. Ninguna línea `CIFRA:` cambió, y el CI regenera la misma
tabla. Desde esta corrida, `correr.py` tapa esa ruta solo.
