# Bloque 29 — Dataset validado para personalización

## Objetivo y alcance

Preparar y validar un dataset propio para estudiar la personalización de un clasificador de mensajes de clientes.

La actividad se realiza localmente. No se creó un cliente de Gemini, no se envió un trabajo de entrenamiento ni se generó un modelo personalizado.

## Técnicas revisadas

| Técnica | Qué cambia o incorpora | Aplicación principal |
|---|---|---|
| RAG | Añade documentos recuperados al contexto, sin entrenar el modelo | Consultar información externa o cambiante |
| Fine-tuning completo | Ajusta los parámetros del modelo | Adaptar su comportamiento mediante ejemplos |
| PEFT mediante adapters | Entrena un conjunto reducido de parámetros adicionales | Adaptar una tarea con menos parámetros entrenables |
| Soft prompting | Entrena vectores que se incorporan a la entrada | Guiar una tarea mediante un prefijo aprendido |

Soft prompting también pertenece a la familia PEFT; se presenta por separado para comparar los mecanismos.

Estas técnicas pueden combinarse. Entrenar un modelo no garantiza respuestas correctas ni sustituye la evaluación con ejemplos independientes.

## Prácticas realizadas

Los ejercicios están en
[laboratorio del bloque 29](../../../../laboratorio/practicas/modulo_02/unidad_2_6/bloque_29/):

- `practica_tipos_personalizacion.py`: inspección de modos y tamaños de adapter definidos en el SDK.
- `practica_ejemplos_tuning.py`: construcción de pares de entrada y salida mediante `TuningExample`.
- `practica_validacion_tuning.py`: detección de entradas vacías, duplicados y salidas incorrectas.
- `practica_balance_tuning.py`: comparación de conjuntos equilibrados, desbalanceados y sin una categoría.
- `practica_configuracion_tuning.py`: construcción local de una configuración e inspección de hiperparámetros y estados.

Los ejemplos iniciales clasifican errores técnicos. El dataset definitivo utiliza mensajes de clientes del proyecto.

También se revisó el ciclo conceptual de un trabajo remoto: creación, consulta de su estado y comprobación del resultado. Cerrar la terminal no equivale a cancelar un trabajo remoto.

La configuración local utiliza cinco épocas y `ADAPTER_SIZE_FOUR`. Son valores didácticos, no parámetros optimizados ni una recomendación para producción.

## Dataset del proyecto

Implementación: [src/dataset_tuning.py](../../../../src/dataset_tuning.py).

Contiene 16 mensajes ficticios redactados para el ejercicio:

| Categoría | Ejemplos |
|---|---:|
| desconocida | 4 |
| pregunta | 4 |
| queja | 4 |
| sugerencia | 4 |
| **Total** | **16** |

Cada entrada incluye la instrucción de clasificación y el mensaje. La salida esperada es una cadena con un objeto JSON de una sola clave:

```json
{"categoria": "queja"}
```

Los criterios distinguen la intención del mensaje de su forma:

- Un problema concreto se clasifica como queja, aunque esté formulado como pregunta.
- Una propuesta de mejora sin un problema concreto que requiera atención se clasifica como sugerencia.
- Una solicitud de información se clasifica como pregunta.
- Un saludo, agradecimiento o mensaje insuficiente se clasifica como desconocida.
- Si se combina un problema concreto con una mejora, se prioriza queja.

El enrutador existente utiliza etiquetas de texto. Este dataset propone una salida JSON para estudiar una posible adaptación futura; no se ha conectado al enrutador ni sustituye su funcionamiento.

## Validación

El validador comprueba:

- Un mínimo de diez ejemplos, establecido para esta actividad.
- La presencia de la instrucción y de un mensaje no vacío.
- Mensajes duplicados, ignorando diferencias de mayúsculas y espacios.
- Salidas textuales que puedan interpretarse como JSON.
- Un objeto con exactamente la clave `categoria`.
- Una categoría permitida y escrita en minúsculas.
- La presencia de ejemplos válidos de las cuatro categorías.

Los ejemplos inválidos no cuentan para cubrir una categoría.

El mínimo de diez ejemplos es un requisito del ejercicio, no un mínimo de entrenamiento confirmado para un servicio. El validador exige cobertura de categorías, pero no cantidades idénticas por categoría.

## Reproducción y resultados

Desde la raíz del repositorio, con el entorno virtual activo y las dependencias instaladas:

```powershell
python -m src.dataset_tuning
python -m pytest tests/test_dataset_tuning.py -v
```

Resultado del dataset:

```text
16 ejemplos, 0 problemas.
desconocida: 4
pregunta: 4
queja: 4
sugerencia: 4

Dataset validado localmente, sin entrenamiento.
```

Las 18 pruebas del dataset pasaron. Comprueban el conjunto válido, la conservación de los datos y el rechazo de entradas, salidas y coberturas incorrectas.

La comprobación completa del proyecto terminó con 138 pruebas pasadas y dos advertencias de dependencias: `_UnionGenericAlias` en `google-genai` y `asyncio.iscoroutinefunction` en Chroma. No se ocultaron las advertencias.

`python -m pip check` no encontró dependencias incompatibles.

## Disponibilidad del entrenamiento y límites

Consulta de disponibilidad: 13 de noviembre de 2026.

La documentación oficial indica que Gemini API y AI Studio no disponen de un modelo compatible con fine-tuning. Google remite a Gemini Enterprise Agent Platform como alternativa. Por ello, la presencia de tipos y opciones de tuning en el SDK no demuestra que puedan utilizarse con la cuenta y el servicio empleados en este proyecto.

Además, la documentación local de `TuningExample` indica que ese tipo no está soportado en Vertex AI. El dataset preparado no se presenta como una solicitud lista para enviarse a ese servicio.

La validación confirma las reglas implementadas, no la calidad de un modelo entrenado. Antes de entrenar habría que comprobar el servicio, modelo, formato, permisos y costos aplicables, y preparar datos independientes para evaluar la generalización.

Con estos 16 ejemplos no se ha demostrado una mejora frente al clasificador actual ni la necesidad de entrenarlo.

## Fuentes técnicas

- [Google: disponibilidad de fine-tuning](https://aistudio.google.com/docs/model-tuning).
- [Hugging Face: métodos de PEFT](https://huggingface.co/docs/peft/main/methods/overview).