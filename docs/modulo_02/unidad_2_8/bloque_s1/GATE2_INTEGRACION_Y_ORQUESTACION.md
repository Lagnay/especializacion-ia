# Gate 2 — Integración y orquestación

Fecha de revisión: 17 de noviembre de 2026.

## Objetivo y alcance

Reunir el flujo RAG del laboratorio en un ejecutable que utilice un índice persistido, filtre el contexto, genere respuestas con referencias, registre consumo y tiempos, y utilice una versión de instrucciones previamente aprobada.

Se comprobaron consultas simuladas, una consulta real y una instalación en una copia con entorno nuevo. El alcance corresponde al laboratorio; no acredita preparación general para producción.

## Componentes integrados

| Componente | Responsabilidad |
|---|---|
| [cli_servicio_rag.py](../../../../src/cli_servicio_rag.py) | Preparación, revisión del prompt y ejecución por consola. |
| [componentes_servicio_rag.py](../../../../src/componentes_servicio_rag.py) | Apertura y cierre de componentes simulados o reales. |
| [servicio_rag.py](../../../../src/servicio_rag.py) | Comprobación de aprobación, consulta, medición y costo de referencia. |
| [indexar_corpus.py](../../../../src/indexar_corpus.py) | Indexación explícita de los fragmentos pendientes. |
| [logging_rag.py](../../../../src/logging_rag.py) | Eventos JSON, identificadores, consumo y validación de referencias. |
| [seguridad_rag.py](../../../../src/seguridad_rag.py) | Filtrado y construcción de mensajes con roles separados. |
| [registro_prompts.py](../../../../src/registro_prompts.py) y [grafo_supervision.py](../../../../src/grafo_supervision.py) | Registro de instrucciones y aprobación vinculada a su huella. |
| [matriz_riesgos.py](../../../../src/matriz_riesgos.py) | Cinco riesgos propios, estimaciones y controles. |

Se reutiliza el constructor de componentes del Bloque 28, ampliado para recibir un cliente Chroma administrado por el nuevo flujo.

## Funcionamiento

La aprobación del prompt se guarda en SQLite y puede reutilizarse entre procesos. Cada consulta comprueba que la solicitud esté aprobada y finalizada, que la versión exista en el registro y que el texto coincida con su huella.

La instrucción aprobada se incorpora al `SystemMessage`. La aprobación no se solicita nuevamente por cada respuesta ordinaria.

La consulta:

1. Abre el índice correspondiente al modo elegido.
2. Recupera documentos y filtra patrones sospechosos.
3. Numera únicamente los fragmentos aceptados.
4. Genera la respuesta usando el texto aprobado.
5. Comprueba que las referencias citadas existan en ese contexto.
6. Devuelve fuentes, consumo, tiempos y costo de referencia.

Si no queda contexto aceptado, se omite el modelo y se devuelve información insuficiente. Si una respuesta generada carece de referencias válidas o mezcla referencias existentes e inexistentes, se bloquea con un error controlado.

Validar la numeración no demuestra por sí solo que todas las afirmaciones estén respaldadas: la correspondencia con las fuentes también requiere revisión.

## Modos y persistencia

- Sin argumentos: preparación, sin consultas ni escritura de estados.
- `--aprobar-prompt`: revisión humana de una propuesta.
- `--ver-prompt`: consulta del estado guardado.
- `--simular`: ensayo local con una pregunta fija, seis fragmentos, embeddings deterministas de 16 dimensiones y respuesta preparada.
- `--ejecutar`: consulta a Gemini usando el índice real y `k=3` por defecto.
- `--pregunta` y `--k`: configuración de la consulta real.
- `--solicitud`: identifica la aprobación que debe utilizarse.
- `--registro`: selecciona el archivo de eventos.

El modo simulado comprueba conexiones e indexación; no mide calidad semántica. Su costo queda sin determinar porque la respuesta preparada no informa consumo.

El índice simulado se guarda en `vectorstore/gate2_simulado`. El real utiliza la colección del corpus en `vectorstore`. Los estados se guardan en `checkpoints/gate2.sqlite`. Ambas carpetas están excluidas de Git.

Las consultas añaden eventos a [trazas_servicio.jsonl](trazas_servicio.jsonl). El archivo conserva 24 eventos de dos consultas simuladas y 12 eventos de una consulta real. Sus campos `origen` distinguen ambas clases de evidencia.

Una solicitud resuelta no admite otra decisión. Para revisar una propuesta nueva debe utilizarse otro identificador y seleccionarlo también al consultar.

## Corrida real observada

Ejecutada manualmente el 16 de noviembre de 2026.

| Dato | Resultado |
|---|---|
| Pregunta | ¿Cuántos intentos permite el cliente REST? |
| Respuesta | El cliente REST permite hasta tres intentos por consulta [1]. |
| Fuente citada | `src/cliente.py` |
| `trace_id` | `trace-5929e6253c93436c9720993eb68461b9` |
| Colección | `proyecto-09ca32e294f70044`, reutilizada |
| Fragmentos del índice / recuperados | 6 / 3 |
| Embeddings | `models/gemini-embedding-001`, 3072 dimensiones |
| Generación | `gemini-3.5-flash-lite` |
| Tokens de entrada / salida / total | 204 / 12 / 216 |
| Tokens de entrada en caché | 0 |
| Recuperación | 758.3879 ms |
| Generación | 4710.0371 ms |
| Total de consulta mostrado | 5479.76 ms |
| Costo de generación de referencia | 0.000091200 USD |
| Fecha de las tarifas | 2026-11-12 |
| Código de salida | 0 |

La huella utilizada fue `7f32d8c7857fc7e0e38c70d660b88cc0d94654f2e41cb71747a99d630b8adf79`.

Esta tabla transcribe la salida de consola. El JSONL conserva las etapas, las fuentes de los fragmentos aceptados, la cantidad de referencias validadas y el consumo; no guarda la respuesta completa, el tiempo total ni el importe calculado.

El tiempo total corresponde a `ejecutar_servicio`; no incluye el arranque del programa, la apertura de componentes, la indexación ni la revisión humana previa. Recuperación agrupa la generación del embedding de la pregunta y la búsqueda vectorial.

El importe es una estimación de generación a tarifas de referencia. No incluye embeddings ni acredita un cargo real.

La instantánea del Bloque 32 conserva su procedencia histórica de validación simulada. Esta corrida aporta evidencia posterior del uso de la misma instrucción con Gemini; no convierte aquel registro histórico en una evaluación general de robustez.

## Evidencia por dimensión de la rúbrica

| Dimensión | Peso | Evidencia |
|---|---:|---|
| Pipeline funcional | 25 % | Consulta integrada real, código de salida 0 y reutilización del índice. |
| Recuperación y citación | 15 % | [Evaluación del Bloque 27](../../unidad_2_5/bloque_27/EVALUACION_RECUPERACION.md), referencias comprobadas y fuente en la respuesta real. |
| Costo y latencia | 10 % | Medición por etapas, consumo y costo de referencia de la corrida anterior. |
| Personalización | 15 % | [Decisión fundamentada del Bloque 30](../../unidad_2_6/bloque_30/decision_personalizacion.md). |
| Observabilidad | 15 % | Eventos JSON correlacionados mediante `trace_id`, con origen y huella del prompt. |
| Seguridad y gobernanza | 20 % | Filtrado, aprobación persistente, registro de versiones y matriz de riesgos. |

La evaluación histórica de recuperación con `k=3` obtuvo precisión macro de 0.333, recall de 1.000 y F1 de 0.527 en su conjunto preparado. No son métricas de exactitud de las respuestas generadas.

La decisión del Bloque 30 corresponde al **clasificador de mensajes**: mantiene prompting y normalización, y pospone el entrenamiento. Su muestra de 20 casos no mostró un fallo que justificara entrenar. No se aplica esa decisión automáticamente a todas las funciones del laboratorio.

El **servicio de consulta documental del Gate 2** utiliza RAG porque necesita recuperar información del corpus técnico y mostrar sus fuentes. Su elección se apoya en ese objetivo y en la evaluación de recuperación del Bloque 27. Actualizar el corpus e indexarlo permite cambiar la información disponible sin entrenar los parámetros del modelo.

El fine-tuning completo ajustaría los parámetros del modelo; PEFT ajustaría una parte pequeña de los parámetros o parámetros adicionales, según la técnica. Aquí no se ha demostrado una necesidad de entrenamiento para el servicio documental ni se dispone de un modelo entrenado propio. Ambas alternativas exigirían datos, evaluación y una justificación adicional; entrenar no sustituye por sí solo la recuperación y citación de las fuentes. Por eso se conserva RAG para las consultas documentales y la decisión del Bloque 30 para el clasificador.

La calificación oficial corresponde al instructor y se distingue de la autoevaluación del estudiante.

## Cuatro criterios obligatorios

[tests/test_gate2.py](../../../../tests/test_gate2.py) comprueba:

1. Flujo completo y reutilización del índice entre aperturas.
2. Referencia en la respuesta y correspondencia con la fuente devuelta.
3. Ausencia de la consulta, correo sintético, respuesta y documentos completos en los logs del caso preparado.
4. Interrupción real del grafo, aprobación, rechazo y bloqueo de consultas sin autorización.

Los tests usan componentes simulados y archivos temporales. La aprobación humana por consola y la corrida con Gemini se comprobaron por separado.

Resultados: cuatro autochequeos pasados, 19 pruebas del servicio pasadas y 277 pruebas en la suite completa. La suite también pasó en el [ensayo de instalación limpia](ENSAYO_INSTALACION_LIMPIA.md).

## Autoevaluación del estudiante: 100/100

Fecha de autoevaluación: 17 de noviembre de 2026.

El estudiante se asigna **100/100** por el cumplimiento de los requisitos de la entrega del Gate 2, al cierre del Módulo 2. La valoración se fundamenta en las evidencias siguientes y en los cuatro criterios obligatorios. No incorpora requisitos del Módulo 3 ni descuenta puntos por ampliaciones de producción que esta actividad no exige.

El puntaje expresa la autoevaluación del cumplimiento de la consigna. No significa que el recuperador tenga una precisión de 1.000, que todas las respuestas futuras sean correctas o que los controles eliminen todos los riesgos. Las métricas y los límites observados se conservan sin modificarlos.

| Dimensión | Peso | Autoevaluación | Fundamento del cumplimiento |
|---|---:|---:|---|
| Pipeline funcional | 25 % | 100 | Se integraron indexación, recuperación y generación. El índice persiste y se reutiliza; el indexador incorpora los fragmentos pendientes. Hay una corrida real completada y un ensayo con entorno nuevo, sin reutilizar índices ni aprobaciones del entorno original. |
| Recuperación y citación | 15 % | 100 | Se midieron precisión y exhaustividad sobre el corpus propio, se compararon `k=3` y `k=5` y se justificó conservar `k=3` para ese conjunto. La respuesta real cita su fuente; el servicio comprueba las referencias y bloquea las ausentes o inexistentes. Se documenta que esta comprobación no acredita por sí sola el respaldo semántico de cada afirmación. |
| Costo y latencia | 10 % | 100 | Se instrumentaron las etapas y el consumo por consulta, con corrida real documentada. El costo se calcula con tarifas de referencia fechadas y explicita su alcance de generación, sin atribuir costos de embeddings ni cargos reales no comprobados. |
| Personalización | 15 % | 100 | La matriz del Bloque 30 se aplicó al caso propio y se fundamentó mantener prompting y normalización del clasificador con la evidencia disponible. Para la consulta documental se justifica RAG y se explica por qué no se añade fine-tuning completo ni PEFT sin una necesidad demostrada. No entrenar un modelo es una decisión fundamentada dentro de la actividad. |
| Observabilidad | 15 % | 100 | El logging estructurado correlaciona las etapas y el consumo mediante `trace_id`, y distingue origen real o simulado y huella del prompt. Se documenta qué guarda el JSONL y qué resultados se transcribieron desde consola. |
| Seguridad y gobernanza | 20 % | 100 | Se verificaron el filtro con documentos reales de la aplicación, la separación de roles y la omisión de generación sin contexto aceptado. Hay registro de versiones, aprobación humana ejecutable y persistente mediante interrupción y reanudación, y cinco riesgos propios con puntos de supervisión. Las pruebas comprueban la ausencia de contenido crudo sensible en los logs de los casos preparados. |

Promedio ponderado: `100×0.25 + 100×0.15 + 100×0.10 + 100×0.15 + 100×0.15 + 100×0.20 = 100`.

Los criterios no compensables se comprueban por separado:

| Criterio obligatorio | Autoevaluación | Evidencia |
|---|---|---|
| Pipeline de punta a punta sin excepciones no capturadas | Cumplido | Consulta real con código de salida 0, reutilización del índice y tests del flujo integrado. |
| Respuestas con referencia y fuente de respaldo | Cumplido | Respuesta real sobre los intentos del cliente, fuente `src/cliente.py`, test de correspondencia y bloqueo de referencias inválidas. |
| Logs sin PII ni contenido crudo sensible | Cumplido en los casos comprobados | Test del archivo JSONL y de la salida del logger, con consulta, correo sintético, respuesta y documentos completos ausentes. |
| Supervisión humana que pausa y retoma | Cumplido | Aprobación y rechazo por consola, estado persistente en SQLite, interrupción del grafo y bloqueo de consultas sin aprobación. |

Resultado de la autoevaluación: **100/100 y cuatro criterios obligatorios cumplidos dentro del alcance comprobado del laboratorio**. La calificación oficial corresponde al instructor. Los límites de la solución se mantienen en la sección siguiente como información sobre su alcance.

## Riesgos y límites

La matriz conserva cinco riesgos propios y los puntos de supervisión del Bloque 32. Se actualiza el control de R02 para reflejar que el servicio integrado ya utiliza el texto aprobado. No se presenta una nueva valoración del riesgo residual.

R01 mantiene la revisión manual del corpus contra el código antes de actualizarlo e indexarlo. La huella del índice no detecta por sí sola cambios en los archivos mencionados como fuentes.

El filtro conserva sus limitaciones conocidas: falsos positivos y falsos negativos. Los controles de privacidad se comprobaron con el corpus técnico y los datos preparados; no acreditan anonimización universal.

La supervisión no implementa autenticación de revisores ni coordinación de decisiones concurrentes para producción.

## Reproducción y continuidad

Los comandos de instalación, aprobación, indexación y consulta están en el [README](../../../../README.md#servicio-rag-integrado-gate-2).

La entrega reúne las piezas del Módulo 2. Su publicación y calificación formal se identifican por el commit entregado y el resultado del instructor.

Antes de comenzar el Módulo 3 se realizará el repaso conceptual completo del Módulo 2.