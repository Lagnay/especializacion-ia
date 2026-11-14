# Bloque 30 — Costos, evaluación y decisión de personalización

## Alcance

Este bloque estudia cómo fundamentar una decisión de personalización a partir de costos, requisitos y resultados observados.

El caso corresponde al laboratorio académico. Sus decisiones no se trasladan automáticamente al proyecto principal.

La conclusión está en [decision_personalizacion.md](decision_personalizacion.md).

## Costos de preparar datos

La práctica de etiquetado utiliza supuestos ilustrativos, no tiempos registrados ni gastos realizados:

| Escenario | Tiempo | Costo supuesto |
|---|---:|---:|
| 16 ejemplos, 5 minutos por ejemplo, 25 USD/h | 1,33 h | 33,33 USD |
| 200 ejemplos, mismas condiciones | 16,67 h | 416,67 USD |
| 500 ejemplos, 4 minutos por ejemplo, 20 USD/h | 33,33 h | 666,67 USD |
| Segunda revisión de 100 ejemplos, 2 minutos cada uno, 20 USD/h | 3,33 h | 66,67 USD |
| Total de etiquetado y segunda revisión | 36,67 h | 733,33 USD |

La revisión agrega trabajo al etiquetado inicial. Estos importes no incluyen infraestructura ni entrenamiento.

Nuestro Chroma utiliza persistencia local: hay que conservar sus archivos o poder reconstruir el índice, pero esta implementación no exige un servidor separado permanentemente encendido.

## Lectura de estadísticas de entrenamiento

Se inspeccionaron los campos de `SupervisedTuningDataStats` del SDK instalado y se construyó un objeto simulado.

La práctica usa 8 ejemplos, 1 descartado, 1540 tokens facturables y 35 pasos. Son valores ficticios; no corresponden a un entrenamiento del proyecto.

Aunque el campo se llama `total_truncated_example_count`, su descripción indica ejemplos descartados por motivos como exceso de tokens o imágenes inválidas. Los índices empiezan en 1 y pueden representar una muestra parcial.

Un conteo de tokens no determina por sí solo un importe: requiere la tarifa aplicable al entrenamiento. No corresponde aplicar automáticamente precios de generación.

No se consultó ningún trabajo de tuning ni se entrenó un modelo.

## Método de puntuación

Se aplicaron los pesos orientativos de las cinco preguntas del curso. La implementación exige exactamente cinco respuestas booleanas y conserva todas las candidatas empatadas.

Los puntajes no son métricas de calidad ni resultados de entrenamientos. Si todas las respuestas son False, las tres técnicas empatan en cero; el método no favorece ninguna.

Las prácticas muestran un empate, cambios al invertir una respuesta y un caso con una única candidata. En el caso propio, RAG obtiene 2 puntos, PEFT 1 y fine-tuning completo 0.

El requisito de iterar en menos de un día fue adoptado para el laboratorio. No representa un plazo contractual ni un presupuesto declarado.

## Evaluación real del clasificador

Se prepararon 20 mensajes ficticios, cinco por categoría, separados del dataset de entrenamiento del bloque 29. Las categorías esperadas y los criterios se fijaron antes de consultar.

El evaluador utiliza las instrucciones existentes del clasificador. No ejecuta las rutas de atención ni exige el JSON propuesto en el bloque 29: el clasificador actual solicita una etiqueta de una palabra.

Se distinguen dos comprobaciones:

- Formato: la salida original, quitando espacios exteriores, debe ser una etiqueta permitida en minúsculas y sin puntuación.
- Clasificación: la etiqueta normalizada debe coincidir con la categoría esperada.

La normalización puede recuperar una etiqueta sin convertir el formato original en correcto.

Resultados observados:

- 20 respuestas guardadas.
- 20 categorías correctas.
- 0 incumplimientos de formato.
- 1 error de ejecución conservado por separado.

La muestra es pequeña, preparada y equilibrada. No representa necesariamente la distribución de mensajes reales ni demuestra precisión general del 100 %.

## Interrupción y reanudación

La primera ejecución completó 15 casos y se detuvo en C16 por un error 429. El proveedor indicó un límite de 15 solicitudes por minuto para el proyecto y modelo utilizados.

Después de esperar, se reanudaron únicamente C16 a C20. El historial del error permanece en el registro y no cuenta como una respuesta incorrecta.

El programa no espera automáticamente ante una cuota agotada: registra el error y se detiene. Antes de reanudar debe revisarse su causa y el tiempo de espera indicado. Ese límite observado no se presenta como un valor universal para todas las cuentas.

El guardado utiliza un archivo temporal antes de reemplazar el registro. Los casos y la configuración, incluido el código del clasificador y de la normalización, deben coincidir para reanudar.

## Reproducción

Desde la raíz, con el entorno virtual activo y las dependencias instaladas:

```powershell
python -m laboratorio.practicas.modulo_02.unidad_2_6.bloque_30.practica_costo_etiquetado
python -m laboratorio.practicas.modulo_02.unidad_2_6.bloque_30.practica_estadisticas_tuning
python -m laboratorio.practicas.modulo_02.unidad_2_6.bloque_30.practica_decision_estrategia
python -m laboratorio.practicas.modulo_02.unidad_2_6.bloque_30.practica_decision_laboratorio
python -m src.casos_clasificacion
python -m src.evaluar_clasificacion
```

Estos comandos no consultan Gemini. El último solamente muestra la preparación.

La ejecución real requiere `GEMINI_API_KEY`:

```powershell
python -m src.evaluar_clasificacion --ejecutar
```

Consulta los casos pendientes y crea o actualiza `evaluacion_clasificacion.json`. Si el registro está completo y es compatible, no repite las consultas. `--registro` permite seleccionar otro archivo para una evaluación distinta.

## Verificación

```powershell
python -m pytest tests/test_decision_personalizacion.py tests/test_evaluar_clasificacion.py -v
```

Las 30 pruebas utilizan cálculos locales, respuestas simuladas y archivos temporales. Comprueban puntajes, empates, validación de entradas, formato, clasificación, guardado, reanudación y preparación sin consultas.

La comprobación completa del proyecto terminó con 168 pruebas pasadas y dos advertencias conocidas de dependencias: `_UnionGenericAlias` en `google-genai` y `asyncio.iscoroutinefunction` en Chroma. `python -m pip check` no encontró dependencias incompatibles.

## Aplicación al proyecto principal

El procedimiento reutilizable consiste en delimitar la tarea, fijar criterios, reunir evidencia, distinguir requisitos adoptados de hechos observados y contrastar los puntajes con las necesidades reales.

La decisión de mantener prompting pertenece a este clasificador y a esta revisión. Otro proyecto requiere su propia evaluación; ni los puntajes ni esta muestra sustituyen esa comprobación.