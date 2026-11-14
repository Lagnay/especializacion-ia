# Bloque 31 — Logging estructurado y mitigación de inyección de prompt

Fecha de revisión: 14 de noviembre de 2026.

## Objetivo y alcance

Instrumentar una consulta RAG para registrar sus etapas, relacionarlas mediante un identificador y observar el filtrado del contexto y el consumo informado por el modelo.

La evidencia utiliza fragmentos del corpus propio, recuperación preparada y respuestas simuladas. No ejecuta embeddings ni consultas a Gemini.

## Componentes

- [src/logging_rag.py](../../../../src/logging_rag.py): configuración del logger, eventos JSON, contexto de ejecución, consumo y coordinación del flujo.
- [src/seguridad_rag.py](../../../../src/seguridad_rag.py): patrones sospechosos, filtrado y construcción de mensajes.
- [Prácticas del bloque](../../../../laboratorio/practicas/modulo_02/unidad_2_7/bloque_31/): ocho ejercicios que conservan el desarrollo gradual.
- [trazas_rag_simuladas.jsonl](trazas_rag_simuladas.jsonl): evidencia de dos consultas simuladas.

Se reutilizan el corpus y las funciones existentes para numerar fragmentos y resolver citas.

## Conceptos practicados

| Elemento | Para qué sirve |
|---|---|
| Logger | Recibe los eventos de la aplicación. |
| Handler de logging | Envía los eventos a una salida, como terminal o archivo. |
| Formatter JSON | Convierte cada evento en una línea con campos definidos. |
| `trace_id` | Relaciona los eventos de una consulta completa. |
| `ContextVar` | Mantiene valores asociados al contexto de ejecución y permite restaurarlos al finalizar. |
| Callback | Recibe avisos de LangChain sobre eventos de sus componentes. |
| `run_id` y `parent_run_id` | Identifican una ejecución de componente y su relación con la ejecución que la contiene. |
| Huella SHA-256 | Permite comparar contenidos sin copiar el texto completo al evento. |
| `usage_metadata` | Contiene los datos de consumo que informa una respuesta del modelo. |

Las prácticas de callbacks comprobaron la propagación de metadatos y la relación entre cadena, recuperador y modelo mediante componentes simulados. La transformación intermedia a texto no se incluyó entre los eventos mostrados.

El módulo reutilizable registra explícitamente las etapas del flujo mediante `trace_id`; su JSONL no guarda el árbol de `run_id` de LangChain.

## Flujo instrumentado

`procesar_consulta` recibe una pregunta, una función de recuperación, un modelo y el origen declarado de la ejecución.

El flujo:

1. Valida la entrada y establece un identificador nuevo.
2. Recupera documentos y registra su cantidad.
3. Filtra patrones sospechosos.
4. Numera el contexto aceptado y prepara las fuentes.
5. Construye mensajes con roles separados y contexto delimitado.
6. Genera la respuesta y registra el consumo disponible.
7. Devuelve el resultado y restaura el contexto anterior.

Si no queda contexto aceptado, devuelve una respuesta de información insuficiente y omite la llamada al modelo.

Ante errores registra la etapa y el tipo de excepción, propaga el error y restaura el contexto mediante `finally`.

La interfaz permite proporcionar `recuperar_fragmentos` y un modelo que devuelva `AIMessage`. La conexión con servicios reales es opcional y no se ejecutó para esta evidencia.

Las mitigaciones corresponden a este flujo instrumentado. Los comandos históricos de recuperación y medición conservan sus implementaciones y no pasan automáticamente por este filtro.

## Mitigaciones y límites

Se combinan tres capas:

- Detección de patrones sospechosos antes de construir los mensajes.
- Delimitación explícita mediante `<contexto>` y `</contexto>`.
- Separación entre `SystemMessage` y `HumanMessage`.

También se escapan las etiquetas procedentes de los documentos antes de insertarlas.

La práctica del detector mostró:

| Ejemplo preparado | Coincidencias |
|---|---:|
| Documento informativo | 0 |
| Intento con frases contempladas | 3 |
| Intento con una instrucción diferente | 0 |
| Documento legítimo que cita una frase de ataque | 1 |

Esto conserva visibles un falso negativo y un falso positivo del detector actual. Tres coincidencias en un documento no equivalen a tres ataques.

Las capas no garantizan seguridad. Las comprobaciones locales demuestran el filtrado y armado de mensajes para los casos preparados; no miden la resistencia de un modelo real ante ataques.

## Política de los eventos

El logger del módulo registra longitudes, cantidades, fuentes declaradas, huellas y datos de consumo. No incorpora el texto completo de la pregunta, los documentos, la respuesta ni el mensaje de las excepciones.

Las fuentes incluidas en este corpus son identificadores de archivos del proyecto. En otra aplicación habría que revisar qué información contienen esos metadatos antes de registrarlos.

Una huella no cifra ni anonimiza el documento: alguien con un texto candidato puede calcularla y compararla.

Cada evento del flujo incluye `origen`, para distinguir ejecuciones simuladas y reales. Los valores de tokens de esta evidencia fueron preparados para el ejercicio, no medidos por un proveedor.

Cuando falta `usage_metadata`, se registra consumo no disponible con valores `null`. Eso no equivale a consumo cero. El módulo no calcula importes monetarios ni consumo de embeddings.

## Evidencia observada

| Consulta simulada | Eventos | Documentos recuperados | Descartados | Entrada | Salida | Total |
|---|---:|---:|---:|---:|---:|---:|
| Intentos del cliente REST | 9 | 2 | 1 | 210 | 18 | 228 |
| Memoria al cerrar el proceso | 8 | 1 | 0 | 120 | 12 | 132 |
| **Total simulado** | **17** | **3** | **1** | **330** | **30** | **360** |

Las consultas tienen identificadores distintos. Todos los eventos están marcados como simulados. Al terminar, tanto el identificador activo como el origen vuelven a `None`.

Las fuentes aceptadas fueron `src/cliente.py` y `src/agente_con_memoria.py`, respectivamente. El documento sospechoso quedó registrado mediante su fuente de prueba, tres coincidencias y su huella.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo y las dependencias instaladas:

```powershell
python -m laboratorio.practicas.modulo_02.unidad_2_7.bloque_31.practica_flujo_rag_instrumentado
```

Este comando muestra la preparación sin ejecutar el flujo ni guardar eventos.

Para ejecutar las dos consultas simuladas y añadir sus eventos al JSONL:

```powershell
python -m laboratorio.practicas.modulo_02.unidad_2_7.bloque_31.practica_flujo_rag_instrumentado --guardar
```

Repetir `--guardar` añade otras dos trazas. `--registro` permite seleccionar una ruta alternativa.

Estos comandos no consultan APIs.

## Verificación

```powershell
python -m pytest tests/test_seguridad_rag.py tests/test_logging_rag.py -v
```

Las 34 pruebas comprueban filtrado, roles, citas, conservación de documentos, datos inválidos, consumo ausente o cero, omisión de generación, errores, restauración del contexto y persistencia JSONL.

Se verificaron consultas secuenciales y la restauración de un contexto padre; no se realizó una prueba de carga concurrente.

La comprobación completa del proyecto terminó con 202 pruebas pasadas y dos advertencias conocidas: `_UnionGenericAlias` en `google-genai` y `asyncio.iscoroutinefunction` en Chroma. `python -m pip check` no encontró dependencias incompatibles.