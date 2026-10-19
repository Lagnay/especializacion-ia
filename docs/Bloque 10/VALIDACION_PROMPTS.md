# Validación del banco de prompts

Fecha: 19-10-2026  
Modelo: gemini-3.5-flash-lite.

## Procedimiento

Construí tres prompts: clasificación de consultas,
extracción de pedidos y resumen de mensajes.

Cada prueba realizó tres intentos por prompt seleccionado.
El script conservó instrucciones, entradas, esquemas,
respuestas y motivos de rechazo.

La validación comprueba JSON interpretable como objeto,
campos obligatorios, tipos, valores permitidos, límites
numéricos y el máximo de palabras cuando corresponde.

## Ajustes del resumen

Utilicé una entrada de 56 palabras y mantuve un límite
de salida de 23 palabras durante todas las pruebas.

- Instrucción inicial: 1/3 válido.
- Primer ajuste, solicitando un margen de longitud: 0/3 válidos.
- Segundo ajuste, incorporando un ejemplo compacto: 2/3 válidos.
- Tercer ajuste, utilizando estilo de nota breve, un objetivo
  de 12–18 palabras y una descripción del campo: 3/3 válidos.

Conservé los resultados anteriores, incluidos los fallos.

## Validación completa final

Después de los ajustes ejecuté nuevamente los tres prompts
con la configuración final:

- Clasificación de consultas: 3/3 válidos.
- Extracción de pedidos: 3/3 válidos.
- Resumen de mensajes: 3/3 válidos.

Resultado total: 9/9 bajo las comprobaciones programadas.

Los resúmenes finales tuvieron 16, 17 y 17 palabras.

## Registros

- [Prueba inicial](../../prompts/registro_resultados_inicial.json).
- [Primer ajuste](../../prompts/registro_resultados_ajuste_1.json).
- [Segundo ajuste, solo resumen](../../prompts/registro_resultados_ajuste_2.json).
- [Tercer ajuste, solo resumen](../../prompts/registro_resultados_parcial.json).
- [Validación completa con la configuración final](../../prompts/registro_resultados.json).

## Conclusión y límites

La configuración final superó todas las comprobaciones
en esta ejecución completa. Esta muestra no garantiza
cumplimiento permanente ni generalización a otras entradas.

La validez estructural y la longitud no garantizan fidelidad
del contenido. En la ejecución final aparecieron expresiones
como «indemnización» y «exige compensación», que hacen
más específica o intensa la consulta original. El validador
actual no detecta esos matices.

La confianza declarada por el modelo no representa una
probabilidad de acierto calibrada.

Para un uso con requisitos estrictos, quedaría por implementar
y evaluar una estrategia de recuperación ante respuestas
rechazadas y una evaluación adicional del contenido.