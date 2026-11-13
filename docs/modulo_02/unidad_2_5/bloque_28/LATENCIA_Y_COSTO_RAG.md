# Bloque 28 — Latencia del flujo RAG y costo de generación

## Objetivo y alcance

Instrumentar una consulta RAG para medir por separado el embedding de la pregunta, la búsqueda vectorial y la generación. Conservar los tiempos, el consumo informado por el modelo, el contexto y la respuesta para analizarlos posteriormente.

Los tiempos y tokens registrados corresponden a consultas reales. Los importes monetarios son estimaciones de generación con tarifas de referencia de pago; no representan necesariamente cargos en la cuenta.

## Archivos

- [Instrumentación, preparación y guardado](../../../../src/registro_rag.py).
- [Lectura y cálculo del costo de referencia](../../../../src/resumir_registro_rag.py).
- [Preparación compartida del prompt](../../../../src/recuperacion.py).
- [Pruebas de instrumentación y guardado](../../../../tests/test_registro_rag.py).
- [Pruebas del cálculo y del lector](../../../../tests/test_resumir_registro_rag.py).
- [Prácticas del bloque](../../../../laboratorio/practicas/modulo_02/unidad_2_5/bloque_28/).
- [Cuatro registros reales en JSONL](registros_latencia_costo.jsonl).

## Preparación y decisiones

Se comprobó localmente que el corpus produce fragmentos no vacíos, sin textos duplicados y con metadatos de fuente. Git confirma que la base vectorial está ignorada.

También se verificaron los doce casos de evaluación y el índice persistente: seis fragmentos con vectores de 3072 dimensiones.

Se compararon dos tamaños de fragmentación, manteniendo un solapamiento configurado de 35 caracteres:

| Tamaño máximo | Fragmentos | Suma de caracteres |
| --- | ---: | ---: |
| 160 | 11 | 1282 |
| 240 | 6 | 1137 |

Los documentos originales suman 1139 caracteres. El solapamiento puede repetir contenido; la separación también puede retirar espacios o saltos de línea de los extremos.

Con 240, los párrafos de reintentos y los otros cuatro documentos quedan completos en sus respectivos fragmentos. Se mantiene esa configuración por este criterio estructural y por los resultados de recuperación del bloque 27.

La comparación con 160 se realizó en memoria. No se indexó esa alternativa ni se evaluó su calidad de recuperación.

## Configuración de las mediciones reales

| Parámetro | Valor |
| --- | --- |
| Modelo de generación | `gemini-3.5-flash-lite` |
| Modelo de embeddings | `models/gemini-embedding-001` |
| Dimensiones | 3072 |
| Colección | `proyecto-09ca32e294f70044` |
| Fragmentación | 240 caracteres, solapamiento 35 |
| Valores de k | 3 y 6 |
| Timeout de generación | 30 segundos |
| Intentos de generación configurados | 1 |

El vector de la pregunta se calcula una vez mediante `embed_query`. La búsqueda recibe ese vector mediante `similarity_search_by_vector`.

El prompt se prepara con la función compartida `preparar_prompt`, conservando las instrucciones de citas y de información insuficiente.

El tiempo total medido comienza antes del embedding y termina después de la generación. Incluye el armado del prompt. La suma de etapas comprende únicamente las tres operaciones cronometradas.

La construcción de clientes, apertura y comprobación del índice, presentación en consola y escritura del registro quedan fuera de ese tiempo total.

## Mediciones observadas

Las cuatro consultas completadas se realizaron el 12 de noviembre de 2026. Cada registro conserva su timestamp en UTC.

Los tiempos de esta tabla están expresados en segundos y redondeados a tres decimales:

| Caso | k | Embedding | Búsqueda | Generación | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| R01 | 3 | 17.658 | 0.011 | 5.640 | 23.309 |
| R06 | 3 | 7.596 | 0.013 | 4.480 | 12.089 |
| R08 | 3 | 1.894 | 0.006 | 2.645 | 4.545 |
| R01 | 6 | 4.307 | 0.019 | 11.964 | 16.291 |

La búsqueda local fue la etapa más rápida en las cuatro mediciones. La etapa dominante varió: el embedding fue la más lenta en R01 con k=3 y R06; la generación, en R08 y R01 con k=6.

Estos tiempos incluyen lo ocurrido durante cada llamada al SDK. No se separaron los tiempos de red y procesamiento del servicio.

### Revisión de las respuestas

- R01, con ambas configuraciones: indicó hasta tres intentos por consulta.
- R06: explicó el cálculo mediante tokens y tarifas configuradas, con acumulación durante la sesión.
- R08: indicó que la memoria del agente se pierde al terminar el proceso.

Las respuestas citaron el fragmento [1], cuyo contenido respaldaba esas afirmaciones. El JSONL conserva los textos completos, los prompts y las fuentes.

### Incidencia de conexión

Un intento previo falló durante el embedding con `getaddrinfo failed`, un error de resolución de nombres. No llegó a ejecutar la búsqueda ni la generación y no añadió un registro completado.

La resolución del servidor funcionó en las comprobaciones posteriores. La consulta se repitió correctamente sin cambiar el código.

## Consumo y costo de referencia

Se utilizaron las tarifas Standard del nivel de pago de Gemini 3.5 Flash-Lite, consultadas el 12 de noviembre de 2026:

| Concepto | USD por millón de tokens |
| --- | ---: |
| Entrada normal | 0.30 |
| Salida, incluido razonamiento | 2.50 |
| Lectura de caché | 0.03 |

Fuente: [tarifas oficiales de Gemini 3.5 Flash-Lite](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite).

El lector separa la entrada normal de la entrada en caché. Los tokens de razonamiento ya incluidos en `output_tokens` no se suman nuevamente. Las cuatro consultas registraron cero tokens leídos de caché.

| Caso | k | Entrada | Salida | Generación estimada, USD |
| --- | ---: | ---: | ---: | ---: |
| R01 | 3 | 179 | 12 | 0.000083700 |
| R06 | 3 | 199 | 33 | 0.000142200 |
| R08 | 3 | 190 | 13 | 0.000089500 |
| R01 | 6 | 314 | 12 | 0.000124200 |
| **Total** | | **882** | **70** | **0.000439600** |

La estimación comprende únicamente los tokens de generación. Los registros no incluyen el consumo de tokens de los embeddings, por lo que su costo no se calculó.

Si faltan los datos de consumo, el lector muestra `N/D`. No los interpreta como costo cero.

## Comparación de k y decisión

Para R01, pasar de k=3 a k=6 aumentó la entrada de 179 a 314 tokens: 135 tokens adicionales, un 75.4 %.

Ambas ejecuciones produjeron la misma respuesta y doce tokens de salida. El costo de referencia de generación aumentó aproximadamente un 48.4 %.

El tiempo total fue menor con k=6 porque el embedding tardó menos en esa corrida. Estas dos observaciones no permiten concluir que aumentar k acelere el flujo.

Se mantiene k=3 como valor predeterminado, considerando también la evaluación del bloque 27. Esta decisión describe el corpus y los casos evaluados; no establece un valor óptimo universal.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo y las dependencias instaladas, para comprobar la preparación, leer los registros conservados y ejecutar las pruebas:

```powershell
python -m src.registro_rag --caso R01 --k 3
python -m src.resumir_registro_rag
python -m pytest tests/test_registro_rag.py tests/test_resumir_registro_rag.py -v
```

Estos comandos no realizan consultas a Gemini.

Para reproducir las mediciones se requiere el índice creado y `GEMINI_API_KEY` configurada:

```powershell
python -m src.registro_rag --ejecutar --caso R01 --k 3
python -m src.registro_rag --ejecutar --caso R06 --k 3
python -m src.registro_rag --ejecutar --caso R08 --k 3
python -m src.registro_rag --ejecutar --caso R01 --k 6
```

Cada comando realiza una nueva consulta RAG y consume cuota. Cada ejecución completada añade una línea a `registros_latencia_costo.jsonl`, conservando los registros anteriores.

El lector admite una ruta alternativa como argumento y analiza los datos sin modificar el archivo.

## Validación y límites

Las 25 pruebas específicas comprueban coordinación, tiempos con reloj simulado, entradas inválidas, interrupción de etapas posteriores, ausencia de datos de consumo, guardado acumulativo, conservación del archivo, modo de preparación, lectura de JSONL y cálculo de costos.

La comprobación completa terminó con 120 pruebas pasadas y dos advertencias conocidas de deprecación de dependencias: `google-genai` y Chroma. `pip check` no detectó conflictos.

Las pruebas de escritura utilizan carpetas temporales. Los registros de evidencia contienen únicamente las cuatro consultas reales completadas.

La muestra es pequeña y no representa el rendimiento típico de todo el sistema. Los tiempos dependen de las condiciones de ejecución. El costo estimado de generación tampoco equivale al costo completo del RAG ni a una factura del proveedor.