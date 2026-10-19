# Libro de errores — {{PROYECTO}}

**Corte:** {{FECHA}}. Este libro cataloga los errores **del propio análisis**
(supuestos, lecturas, métodos, atribuciones que hubo que retractar), clasificados
por forma, para que la próxima retracción se detecte en horas y no en semanas.

**Qué no es:** no es el catálogo de problemas de los *datos del ERP* (eso va en un
`known-issues.md`). Tampoco reemplaza a las validaciones: cada entrada apunta a su
validación fechada, que tiene la medición. Esto es el índice **por forma de error**.
Si este libro contradice a su validación, manda la validación.

## Contents

- Checklist antes de publicar una cifra
- Tipos 1–8: forma, cómo se frena, entradas
- Formato de una entrada
- Límites

---

## Checklist antes de publicar una cifra

- [ ] **(1)** ¿Alguna identidad aritmética verifica el número (suma por grupo =
      total, rotación × cobertura = período)? ¿El archivo cierra consigo mismo?
- [ ] **(2)** ¿Crucé por posición de columna? Imprimir el encabezado de cada lado.
      ¿Las filas devueltas coinciden con las líneas del archivo?
- [ ] **(3)** ¿Leí el período del preámbulo del export, o del nombre del archivo?
- [ ] **(4)** ¿Declaré entidad, período, grano y —contra la base viva— la hora?
- [ ] **(5)** ¿El chequeo que aprueba esto miró algo? ¿Cuál es su denominador?
- [ ] **(6)** ¿La regla de negocio que apliqué está implementada en un solo lugar?
- [ ] **(7)** ¿La cifra deriva de un dato o de un supuesto mío? ¿Antes de culpar al
      ERP comparé el archivo contra sí mismo? ¿Un cociente redondo es una moneda?
- [ ] **(8)** ¿La premisa de negocio sigue vigente? ¿Es declarada por el dueño o
      medida?

---

## Tipo 1 — El número plausible que no rompe nada

**Forma:** error de método o parseo cuyo resultado es una tabla bien formateada con
números creíbles. Sin excepción ni aviso. Síntoma típico: dos cifras del mismo
documento que no pueden ser ciertas a la vez (25× de rotación y 625 días de
cobertura), o una firma visible (todos los montos enteros, el mismo documento dos
veces en un top 20).

**Cómo se frena:** identidades aritméticas como chequeo, plausibilidad, canario
contra fuente independiente, el archivo contra sí mismo, `DECIMAL` sin `DOUBLE()`,
parseo numérico en una sola función con test.

## Tipo 2 — La columna N no significa lo mismo en todos los informes

**Forma:** cruzar o filtrar por índice de columna. El reexport cambia de forma y el
índice heredado lee otra cosa; el lector descarta justo el dato buscado.

**Cómo se frena:** cruzar por nombre de columna; "no levantó excepción" no es
"se leyó": contrastar filas devueltas vs líneas del archivo.

## Tipo 3 — Creerle al rótulo, no al contenido

**Forma:** el nombre del archivo, el `(COMPLETO)` o el `YTD` tomados como dato.

**Cómo se frena:** el período se lee del preámbulo; la truncación se detecta por
formato (techo de filas), no por confianza.

## Tipo 4 — El universo equivocado (empresa, período, grano)

**Forma:** el cálculo es correcto y mide otra entidad, otro período, otro grano u
otra hora. Una fuente que pierde el grano (de producto a marca) sigue siendo leída
como si lo tuviera.

**Cómo se frena:** entidad/período/grano declarados por cifra; antes de tocar una
fuente compartida, medir los tres números que cambian (filas, días, entidad) en
**cada** consumidor.

## Tipo 5 — El verde vacío

**Forma:** chequeo que aprueba sobre cero elementos, archivo ilegible que sale del
universo y del denominador a la vez, perímetro recortado (`*.csv` y no `*.json`),
sentencia SQL que nunca corrió dentro de un archivo que "devolvió filas".

**Cómo se frena:** todo verde lleva su denominador; un chequeo que no pudo medir
sale rojo; se audita vaciando el universo, no leyendo el código.

## Tipo 6 — La regla escrita cinco veces, y la prosa que no frena

**Forma:** la misma regla de negocio en varios lugares, cada uno distinto; números
escritos a mano en docs que describen un sistema que se mueve; backlogs que dicen
abierto lo ya cerrado.

**Cómo se frena:** un módulo dueño de la regla + test que busca copias; los
conteos en docs se reemplazan por el comando que los produce; un backlog se
verifica contra el código (`git log -S`) antes de trabajarlo.

## Tipo 7 — Fabricación y atribución falsa

**Forma:** cifras que no derivan de un dato, o un defecto de nuestro código
atribuido a la fuente ("el ERP viene desactualizado").

**Cómo se frena:** sello de procedencia, canario, archivo contra sí mismo antes de
culpar a la fuente, bloquear en vez de borrar con la retractación visible y
propagada (`grep` del árbol).

## Tipo 8 — La premisa de negocio errada

**Forma:** el análisis era correcto dado un supuesto que la medición siguiente o el
dueño invierte.

**Cómo se frena:** lo declarado por el dueño manda; lo medido se revisa; las
premisas van fechadas y una decisión con premisa vieja se relee contra la base.

---

## Formato de una entrada

```markdown
- **DD/MM — <Título corto que nombre el error, no el tema>.** Qué se publicó (cifra
  y dónde), qué era en realidad (cifra correcta), por qué no saltó (la firma que
  estaba a la vista y nadie miró). **Cómo se frena:** <chequeo/test/regla nuevo>.
  [[<validación-fechada>]]
```

Reglas de la entrada: con cifra publicada y cifra real, con la guarda que nació
(o el motivo escrito de por qué no es mecanizable), y con enlace a su validación.

## Límites

- Última pasada completa: {{FECHA}}. Las entradas nuevas se agregan leyendo las
  validaciones; el libro no se auto-actualiza.
- Cobertura: solo errores con validación escrita o retractación declarada.
