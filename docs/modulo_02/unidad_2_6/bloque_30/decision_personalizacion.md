# Decisión de personalización: clasificador de mensajes

Fecha de revisión: 14 de noviembre de 2026.

## 1. El problema

El laboratorio necesita clasificar mensajes de clientes como queja, sugerencia, pregunta o desconocida. Se evalúa si existe una necesidad demostrada de añadir recuperación documental o entrenamiento al clasificador actual.

En una muestra preparada de 20 mensajes, el modelo produjo 20 categorías correctas y ningún incumplimiento del formato solicitado. Este resultado describe esa muestra; no demuestra fiabilidad general.

Evidencia: [evaluación del clasificador](evaluacion_clasificacion.json).

## 2. Resultado del método de decisión

| Criterio | Respuesta | Fundamento |
|---|---|---|
| Información cambiante | False | Clasificar la intención no requiere consultar información externa actualizada. |
| Problema de formato o tono | False | Se observaron 0 incumplimientos de formato en 20 respuestas; el umbral orientativo es 3. No se evaluó el tono de respuestas de atención. |
| Dataset grande y de calidad | False | Hay 16 ejemplos preparados, menos de los 200 orientativos del curso. |
| Presupuesto limitado o iteración rápida | True | Se adopta como requisito del laboratorio comprobar cambios durante una sesión de estudio, en menos de un día. No se afirma un presupuesto de entrenamiento. |
| Múltiples variantes | False | Existe un clasificador con cuatro categorías; no hay un requisito de modelos personalizados distintos. |

Resultado: RAG obtiene 2 puntos, PEFT obtiene 1 y fine-tuning completo obtiene 0. RAG es la única candidata con puntaje máximo.

El cálculo se reproduce con la [práctica de decisión del laboratorio](../../../../laboratorio/practicas/modulo_02/unidad_2_6/bloque_30/practica_decision_laboratorio.py).

## 3. Técnica elegida y por qué

Se mantiene el modelo mediante prompting y la normalización existente, y se pospone el entrenamiento.

El puntaje favorece RAG únicamente por la necesidad de iterar rápido. Sin embargo, esta clasificación no necesita recuperar documentos. Ese criterio, por sí solo, no justifica incorporar recuperación documental.

Tampoco se observó un problema de formato que justifique entrenar con PEFT o fine-tuning completo. La decisión complementa el método con análisis cualitativo, como contempla la guía cuando sus preguntas no encajan suficientemente con el caso.

Como análisis de sensibilidad, cambiar únicamente el criterio de formato a True produce RAG: 2, PEFT: 3 y fine-tuning completo: 1. Es un escenario hipotético que permitiría reconsiderar PEFT; no representa un fallo observado ni demuestra que PEFT sea necesario.

## 4. Qué necesitaríamos para ejecutarla

La solución elegida ya está implementada y fue comprobada con 20 consultas reales. Para mantenerla no se requieren nuevos documentos de RAG ni un trabajo de entrenamiento.

Se conservan los 16 ejemplos del bloque 29 separados de los 20 casos de evaluación. Para alcanzar la referencia orientativa de 200 ejemplos faltarían 184 ejemplos de entrenamiento; esa cifra no constituye una exigencia actual ni un mínimo oficial del servicio.

Antes de reconsiderar entrenamiento se necesita una evaluación más amplia, con mensajes variados e independientes y criterios definidos previamente. Cualquier problema detectado deberá compararse primero con alternativas de instrucciones y validación, y evaluarse con datos separados.