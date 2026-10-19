# Pedido de export — {{TEMA}}

Un pedido "a secas" ("mandame la deuda de 2025") vuelve con otro período, otra
entidad, sin código de producto o truncado. Cada pedido declara las cuatro cosas de
abajo, aunque sea un pedido de una línea en medio de una conversación.

## 1. Qué informe

- **Nombre en el menú del ERP:** [tal como aparece; si no se conoce la ruta exacta,
  decirlo: "buscar 'X' en el menú Y"]
- **Entidad / razón social con la que se entra:** [obligatorio si el ERP tiene más
  de una; los saldos y metas pueden cambiar según el login]

## 2. Qué parámetros

- **Período:** desde [dd/mm/aaaa] hasta [dd/mm/aaaa] (inclusive)
- **Depósito / sucursal / vendedor:** [todos | cuál]
- **Tipo de informe / nivel de detalle:** [resumido | por documento | por línea]
- **Columnas:** si el informe deja elegir, incluir **siempre el código** (de
  producto, de cliente) además del nombre; nunca solo el nombre.
- **Incluir anulados / devoluciones:** [sí | no], separados del resto si se puede.

## 3. En qué formato

- `.csv` o `.xlsx`. **Nunca `.xls`**: trunca en 65.536 filas sin avisar.
- No convertir el archivo ni abrirlo y guardarlo de nuevo en una planilla (cambia
  encoding, formatos numéricos y fechas).
- Nombre sugerido: `{{informe}}_{{entidad}}_{{desde}}_{{hasta}}.csv` — el nombre
  ayuda a encontrarlo, pero el período **se verifica en el preámbulo**.

## 4. Cómo se verifica que llegó bien

- **Cifra de control:** [el total que muestra el ERP en pantalla para estos mismos
  filtros, o el total de otro informe que debería coincidir]
- **Columna que tiene que estar:** [p. ej. código de producto]
- **Cantidad aproximada de filas esperada:** [orden de magnitud]
- Al recibirlo: correr el sello (`provenance_seal.py --expect-period ...`) y
  comparar contra la cifra de control antes de usarlo.
