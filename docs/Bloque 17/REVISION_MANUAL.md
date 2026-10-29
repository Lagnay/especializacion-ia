# Bloque 17 — Revisión cualitativa de veinte respuestas

## Ejecución y alcance

- Inicio de la evaluación: 28-10-2026, 22:49:14, zona -03:00.
- Modelo configurado: `gemini-3.5-flash-lite`.
- Respuestas generadas: 20.
- Errores registrados: 0.
- Casos revisados: 20 de 20.
- Revisión validada por Slaven Matkovic Baricic.

Se generaron veinte respuestas nuevas con las preguntas, referencias
y aspectos esperados definidos antes de ejecutar el lote.

Revisé el conjunto completo: incluye los casos con F1 bajo,
intermedio y alto, sin duplicar casos por selección de extremos.

El registro conserva el catálogo utilizado, los mensajes enviados,
las referencias, las respuestas completas, las fechas y las métricas:

[Registro completo de la evaluación](resultados_metricas.json).

## Rúbrica aplicada

- Corrección factual: sí, no o parcialmente, según las afirmaciones
  de la respuesta y la información de control.
- Completitud: sí, no o parcialmente, según la cobertura de los
  aspectos establecidos para cada caso.
- Contradicción: sí o no, según exista una afirmación incompatible
  con la información de control.
- Nota: justificación concreta de cada valoración.

Completitud y corrección se evalúan por separado: cubrir un aspecto
no garantiza haberlo respondido correctamente.

Las diferencias de redacción no se consideran errores factuales.
Las instrucciones de formato se comprueban sobre la respuesta
original, no sobre sus tokens normalizados.

## Revisión por caso

El F1 se presenta redondeado a tres decimales.

| Caso | F1 | Corrección factual | Completitud | Contradicción | Justificación |
| --- | ---: | --- | --- | --- | --- |
| C01 | 1.000 | Sí | Sí | No | Reproduce la frase en minúsculas, sin puntuación ni añadidos. |
| C02 | 0.343 | Sí | Sí | No | Identifica Python y describe usos pertinentes. No era obligatorio repetir «interpretado». |
| C03 | 0.345 | Sí | Parcialmente | No | Explica la producción de alimento, pero omite la relación con la luz establecida en los aspectos esperados. |
| C04 | 1.000 | Sí | Sí | No | Conserva los cuatro paquetes de arroz y el retiro del viernes. |
| C05 | 0.300 | Sí | Sí | No | Reconoce que no se indica la hora y no inventa una. |
| C06 | 0.632 | Sí | Sí | No | Mantiene la ausencia de pan y la disponibilidad de leche y arroz. |
| C07 | 1.000 | Sí | Sí | No | Identifica el 15 de mayo como fecha de retiro. |
| C08 | 0.667 | Sí | Sí | No | Aplica correctamente el mínimo de 30000 pesos a una compra de 28000. |
| C09 | 0.750 | Sí | Sí | No | Calcula un total de 3600 pesos y un vuelto de 1400. |
| C10 | 0.222 | Sí | Sí | No | Reformula la idea con «coche» y «rápido», conservando el significado. |
| C11 | 1.000 | Sí | Sí | No | Mantiene a Laura como quien entrega y a Marcos como quien recibe. |
| C12 | 0.667 | Sí | Sí | No | Aplica la excepción para alimentos pese a que solo han pasado diez días. |
| C13 | 0.750 | Sí | Sí | No | Reconoce que el teléfono no está proporcionado. |
| C14 | 0.773 | Sí | Sí | No | Conserva retraso, producto intacto y solicitud de factura; utiliza exactamente 25 palabras. |
| C15 | 0.500 | Sí | Sí | No | Mantiene pan y arroz y explica la cancelación de la leche. |
| C16 | 0.833 | Sí | Sí | No | Calcula doce botellas y conserva la unidad correcta. |
| C17 | 0.880 | Sí | Sí | No | Identifica el plan B y la diferencia de dos visitas mensuales. |
| C18 | 0.880 | Sí | Sí | No | Sitúa la revisión de la conexión antes del reinicio. |
| C19 | 0.368 | Sí | Sí | No | Expone las fechas incompatibles y evita confirmar arbitrariamente una. |
| C20 | 0.750 | Sí | Sí | No | Interpreta Luna como marca de arroz utilizando el contexto. |

En C19, «Falta el dato necesario» podría formularse con mayor
precisión: las fichas discrepan y debe aclararse cuál es válida.
La respuesta identifica el problema y no selecciona una fecha,
por lo que esta observación de redacción no cambia la valoración.

## Respuestas observadas

Las consultas, contextos, referencias y criterios correspondientes
a cada identificador están disponibles en el registro JSON enlazado.

**C01**

> el cielo es azul

**C02**

> Python es un lenguaje de programación de alto nivel, versátil y fácil de aprender que se utiliza en diversas áreas como el desarrollo web y la inteligencia artificial.

**C03**

> La fotosíntesis sirve para que las plantas produzcan su propio alimento y liberen oxígeno vital para el planeta.

**C04**

> El pedido incluye cuatro paquetes de arroz y se retira el viernes.

**C05**

> El contexto no indica a qué hora se retira el pedido.

**C06**

> No hay pan disponible y se puede comprar leche y arroz.

**C07**

> El pedido se retira el 15 de mayo.

**C08**

> No cumple la condición porque el envío gratuito requiere al menos 30000 pesos y esta compra suma 28000 pesos.

**C09**

> El total es de 3600 pesos y corresponde un vuelto de 1400 pesos.

**C10**

> El coche avanza muy rápido.

**C11**

> Laura entregó la caja y Marcos la recibió.

**C12**

> No se puede devolver el arroz porque es un alimento, a pesar de haber sido comprado hace 10 días.

**C13**

> El contexto no proporciona el teléfono del local.

**C14**

> El pedido llegó con dos días de retraso pero el producto estaba intacto, y la clienta solicitó que le enviaran la factura por correo electrónico.

**C15**

> En la lista quedan pan y arroz porque la leche fue cancelada.

**C16**

> El pedido contiene doce botellas en total.

**C17**

> El plan B incluye más visitas, concretamente dos más que el plan A.

**C18**

> Según el procedimiento, antes de reiniciar el equipo debe revisarse la conexión del cable.

**C19**

> Falta el dato necesario porque la ficha A indica que se retira el lunes y la ficha B indica que se retira el martes.

**C20**

> Luna es una marca de arroz según el catálogo ficticio.

## Hallazgos

- C10 conserva el significado pese a obtener F1 de 0.222.
- C05 reconoce correctamente información ausente con F1 de 0.300.
- C02 y C03 obtienen F1 muy similares, pero su completitud difiere
  según los criterios definidos para cada pregunta.
- C14 cumple el límite de 25 palabras, algo que F1 no comprueba.
- No se detectaron contradicciones en este conjunto.

Resultado de la revisión: 20 respuestas factualmente aceptables,
19 completas y una parcialmente completa según la rúbrica.

Promedios por caso:
precisión 0.618, cobertura 0.805 y F1 0.683.
Estos valores no equivalen a porcentajes de respuestas correctas.

## Comprobaciones técnicas

Las 39 pruebas automatizadas del proyecto fueron aprobadas.
Comprueban comportamiento del código; la revisión cualitativa
de esta actividad se registra en este documento.

Para analizar el registro sin nuevas consultas:

    python -m src.resumir_evaluacion "docs/Bloque 17/resultados_metricas.json"

[Consultar los límites de la métrica](../limites_metrica.md).