# Límites de la métrica de evaluación

## Qué mide

Coincidencia de palabras entre una respuesta y una referencia,
después de limpiar y tokenizar ambos textos, contando repeticiones
para calcular precisión, cobertura y F1.

La normalización elimina diferencias de mayúsculas y puntuación.
El cálculo no interpreta el significado ni verifica los hechos.

## Modos de falla conocidos

### Hallazgos de la evaluación real

- Paráfrasis válidas pueden obtener puntuaciones bajas.
  En C10, «El coche avanza muy rápido» conserva la idea de
  «El auto es veloz», pero obtiene F1 de 0.222.

- Reconocer correctamente información ausente no garantiza
  una puntuación alta. C05 responde que la hora no está indicada
  y obtiene F1 de 0.300 por diferencias de redacción.

- Un F1 parecido puede acompañar distintos niveles de completitud.
  C02 obtiene 0.343 y satisface sus aspectos esperados; C03 obtiene
  0.345 y omite el aprovechamiento de la luz requerido por su rúbrica.

- Las restricciones de formato requieren comprobaciones propias.
  C14 utiliza exactamente 25 palabras, pero F1 no comprueba ese
  límite. En C01, el cumplimiento de minúsculas y ausencia de
  puntuación debe revisarse sobre la respuesta original.

### Límites demostrados mediante ejemplos controlados

En las prácticas del Bloque 16, añadir una negación obtuvo
F1 aproximado de 0.91 y cambiar quién persigue a quién mantuvo
F1 de 1.00, pese a modificar el significado.

Estos ejemplos controlados demuestran límites del cálculo;
no son errores producidos por el modelo en el lote del Bloque 17.

[Ver ejemplos y evidencia del Bloque 16](Bloque%2016/EVALUACION_METRICAS.md).

## Muestra revisada

Evaluación iniciada el 28-10-2026 con veinte respuestas nuevas
de `gemini-3.5-flash-lite`.

Se revisaron los veinte casos completos, incluidos F1 bajos,
intermedios y altos. Cada caso recibió valoración de corrección
factual, completitud y contradicción, con justificación.

Se encontraron 19 respuestas completas y una parcialmente
completa según los aspectos esperados. No se detectaron
contradicciones ni se identificaron afirmaciones factuales
incorrectas en la revisión aprobada.

Son veinte casos dirigidos y heterogéneos: esta revisión no
demuestra confiabilidad general para cualquier consulta.

[Revisión manual y respuestas completas](Bloque%2017/REVISION_MANUAL.md).

[Registro original de resultados](Bloque%2017/resultados_metricas.json).

## Recomendación de uso

Usar las métricas para describir coincidencia léxica y orientar
la revisión, manteniendo los mismos casos, referencias y
procesamiento cuando se comparen ejecuciones.

Revisar también casos con F1 alto y comprobar expresamente
fechas, cifras, participantes, negaciones y restricciones de formato.

Una puntuación baja no basta para rechazar una respuesta,
y una alta no basta para aceptarla como correcta.