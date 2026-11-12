# Bloque 27 — Evaluación de la recuperación

## Objetivo y alcance

Evaluar si la recuperación semántica encuentra los fragmentos pertinentes del corpus del proyecto, mediante precisión, recall y F1.

La evaluación compara identificadores de fragmentos. No genera respuestas finales ni mide su corrección factual.

## Archivos

- [Casos de evaluación](../../../../src/casos_recuperacion.py).
- [Métricas de recuperación](../../../../src/metricas_recuperacion.py).
- [Evaluador y guardado de informes](../../../../src/evaluar_recuperacion.py).
- [Práctica inicial](../../../../laboratorio/practicas/modulo_02/unidad_2_5/bloque_27/practica_metricas_recuperacion.py).
- [Pruebas de las métricas](../../../../tests/test_metricas_recuperacion.py).
- [Pruebas del evaluador](../../../../tests/test_evaluar_recuperacion.py).

## Conjunto y configuración

Se definieron doce preguntas y sus fragmentos relevantes antes de ejecutar estas mediciones, leyendo el corpus:

- R01 a R10: un fragmento relevante por pregunta.
- R11: dos fragmentos relevantes.
- R12: ningún fragmento relevante; el corpus no contiene el teléfono solicitado.

Se utilizó un corpus de cinco documentos, dividido en seis fragmentos.

| Parámetro | Valor |
| --- | --- |
| Colección | `proyecto-09ca32e294f70044` |
| Modelo de embeddings | `models/gemini-embedding-001` |
| Dimensiones | 3072 |
| `chunk_size` | 240 caracteres |
| `chunk_overlap` | 35 caracteres |
| Valores de `k` comparados | 3 y 5 |

Los valores de fragmentación del informe están declarados explícitamente en el evaluador. Si cambia la fragmentación, deben actualizarse esos valores, revisarse las etiquetas e indexarse el corpus correspondiente.

## Métricas y promedios

- Precisión: fragmentos relevantes recuperados divididos por fragmentos recuperados.
- Recall: fragmentos relevantes recuperados divididos por fragmentos relevantes etiquetados.
- F1: media armónica de precisión y recall.

Si no se recuperan fragmentos, la precisión es cero. Si una pregunta no tiene relevantes etiquetados, su recall y F1 se consideran no definidos: `null` en JSON y `N/D` en TXT.

La precisión promedio incluye los doce casos. Los promedios de recall y F1 incluyen los once casos donde esas métricas están definidas.

El F1 promedio se obtiene promediando los F1 individuales. No se calcula a partir de los otros dos promedios.

## Resultados observados

Las tres corridas se realizaron el 11 de noviembre de 2026, manteniendo el corpus y las etiquetas.

| Corrida | k | Precisión promedio | Recall promedio | F1 promedio |
| --- | ---: | ---: | ---: | ---: |
| Primera | 3 | 0.333 | 1.000 | 0.527 |
| Segunda | 3 | 0.333 | 1.000 | 0.527 |
| Tercera | 5 | 0.200 | 1.000 | 0.355 |

Las cifras de la tabla están redondeadas a tres decimales; los JSON conservan mayor precisión.

Las dos corridas con `k=3` coincidieron en los identificadores recuperados, su orden y las métricas. En la corrida con `k=5`, los primeros tres identificadores de cada caso coincidieron con los obtenidos con `k=3`.

### Registros conservados

| Corrida | JSON | TXT |
| --- | --- | --- |
| Primera, k=3 | [Registro](evaluacion_20261111_200915_275858_k3.json) | [Informe](evaluacion_20261111_200915_275858_k3.txt) |
| Segunda, k=3 | [Registro](evaluacion_20261111_201116_257553_k3.json) | [Informe](evaluacion_20261111_201116_257553_k3.txt) |
| Tercera, k=5 | [Registro](evaluacion_20261111_201159_657182_k5.json) | [Informe](evaluacion_20261111_201159_657182_k5.txt) |

## Interpretación y decisión

Con `k=3` se recuperaron todos los fragmentos etiquetados como relevantes para las once preguntas con respuesta en el corpus.

Al aumentar a `k=5`, el recall se mantuvo en 1.000. Los fragmentos adicionales redujeron la precisión y el F1, porque no aportaron nuevos relevantes según las etiquetas.

Se mantiene `k=3` como valor predeterminado. La comparación respalda esta decisión frente a `k=5` para el conjunto evaluado; no demuestra que sea el mejor valor posible.

R12 recibió fragmentos irrelevantes en ambas configuraciones. Su resultado muestra que solicitar los más cercanos no garantiza que el corpus contenga una respuesta. Esta actividad no comprobó la abstención del modelo generador.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo y las dependencias instaladas:

```powershell
python -m src.casos_recuperacion
python -m src.evaluar_recuperacion
python -m pytest tests/test_metricas_recuperacion.py tests/test_evaluar_recuperacion.py -v
```

Estos comandos no realizan consultas a Gemini.

Para reproducir las mediciones reales se necesita `GEMINI_API_KEY` configurada y el índice del corpus creado:

```powershell
python -m src.evaluar_recuperacion --ejecutar --k 3
python -m src.evaluar_recuperacion --ejecutar --k 3
python -m src.evaluar_recuperacion --ejecutar --k 5
```

Cada corrida consulta el modelo de embeddings para las preguntas y utiliza el índice existente. No vuelve a indexar el corpus ni genera respuestas finales.

Al completar el lote, se crean un JSON y un TXT nuevos en esta carpeta, con fecha, configuración, resultados y promedios. El JSON también conserva los identificadores relevantes y recuperados. Los registros anteriores se conservan.

El guardado se realiza al finalizar el lote; esta implementación no incorpora reanudación de corridas interrumpidas.

## Validación y límites

Las diez pruebas específicas verifican las métricas, los casos vacíos, los identificadores repetidos, la coordinación del evaluador, los promedios y el rechazo de valores de k no positivos.

La comprobación completa del proyecto terminó con 95 pruebas pasadas y dos advertencias de deprecación de dependencias: `google-genai` y Chroma.

El conjunto es pequeño y sus etiquetas fueron definidas manualmente sobre un corpus didáctico. Los resultados describen este conjunto y esta configuración.

La coincidencia entre dos corridas demuestra repetibilidad observada en este ensayo. No garantiza que cualquier servicio, índice o configuración produzca siempre resultados idénticos.

No se midieron latencias ni costos de embeddings. Tampoco se evaluó la calidad de respuestas generadas.