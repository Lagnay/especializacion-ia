# Bloque 22 — Herramientas estructuradas y memoria de conversación

## Objetivo

Integrar una herramienta con argumentos definidos mediante Pydantic
y un agente que conserve el contexto entre turnos de una misma
conversación, manteniendo separadas las sesiones.

Todos los pedidos y existencias utilizados son ficticios.

## Implementación

- `src/herramientas_pedidos.py`: herramienta para consultar el estado
  de un pedido y, opcionalmente, su historial de estados.
- `src/agente_con_memoria.py`: construcción reutilizable del agente
  y demostración de dos conversaciones independientes.
- `tests/test_agente_con_memoria.py`: comprobaciones automatizadas.
- `laboratorio/practicas/modulo_02/unidad_2_4/bloque_22/`:
  ejercicios realizados durante el aprendizaje.

Pydantic define y valida los argumentos de la herramienta:
`pedido_id` es obligatorio e `incluir_historial` tiene el valor
predeterminado `False`. Un argumento obligatorio ausente o un valor
booleano no interpretable produce `ValidationError`.

La existencia del pedido se comprueba dentro de la herramienta.
Un identificador válido para el esquema puede corresponder a un pedido
inexistente; en ese caso se devuelve un mensaje de pedido no encontrado.

## Adaptación de la guía

Se conservó la práctica con `InMemoryChatMessageHistory` como
referencia didáctica. Para la implementación integrada se eligió
la API recomendada y actualizada, debido al aviso de deprecación
y retirada anunciada de esa clase.

El agente utiliza `create_agent`, un `InMemorySaver` y un `thread_id`
distinto para cada conversación. El checkpointer conserva el estado
del agente, incluidos sus mensajes; no es simplemente un cambio
de nombre de la clase anterior.

El agente del Bloque 21 conserva su implementación original.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo
y las dependencias instaladas:

```powershell
python -m src.agente_con_memoria
```

Este comando muestra el modo de preparación y no realiza consultas.

Para ejecutar los tres turnos con Gemini, se necesita configurar
`GEMINI_API_KEY` en `.env`:

```powershell
python -m src.agente_con_memoria --ejecutar
```

Esta ejecución consume cuota. Un turno puede requerir varias llamadas
al modelo cuando intervienen herramientas. Las respuestas pueden variar.

## Evaluación real observada

La evaluación se realizó con
`practica_conversacion_memoria`, antes de trasladar la demostración
al módulo reutilizable. No se repitieron las consultas para documentar
la integración.

Modelo configurado: `gemini-3.5-flash-lite`.

### Cliente 1 — Primer turno

Entrada:

> ¿Cuál es el estado del pedido P-301? Incluye su historial de estados.

Mensajes previos: 0.

Herramienta: `consultar_pedido_con_historial`.

Argumentos:

```python
{'incluir_historial': True, 'pedido_id': 'P-301'}
```

Observación:

```text
Estado ficticio de P-301: en preparación. Historial: recibido -> en preparación.
```

Respuesta:

```text
El estado actual del pedido P-301 es **en preparación**.

**Historial de estados:**
* Recibido
* En preparación
```

### Cliente 1 — Segundo turno

Entrada:

> ¿Y ese mismo pedido ya fue entregado?

Mensajes previos: 4.

El agente recuperó P-301 del contexto y volvió a consultar
`consultar_pedido_con_historial` con los mismos argumentos.

Respuesta:

```text
No, el pedido P-301 aún no ha sido entregado; su estado actual es "en preparación".
```

### Cliente 2 — Conversación nueva

Entrada:

> ¿Qué pedido te mencioné antes?

Mensajes previos: 0. No se utilizaron herramientas.

Respuesta:

```text
No me has mencionado ningún pedido anteriormente en esta conversación. Por favor, indícame el identificador del pedido que deseas consultar.
```

### Estado final observado

- `cliente_1`: 8 mensajes, con sus dos preguntas.
- `cliente_2`: 2 mensajes, con su única pregunta.

El estado incluye mensajes del usuario, del modelo y de herramientas.
Estas cantidades no equivalen al número de consultas del usuario
ni a un conteo de tokens.

En los casos observados, el agente recuperó el pedido en el segundo
turno y mantuvo separadas las dos conversaciones.

## Pruebas automatizadas

```powershell
python -m pytest tests/test_agente_con_memoria.py -v
python -m pytest tests -q
```

Resultados observados:

- 6 casos pasados en el archivo del agente con memoria.
- 69 casos pasados en el conjunto completo.
- Una advertencia de `google-genai` sobre `_UnionGenericAlias`.

Las pruebas comprueban la opción de historial, argumentos inválidos,
pedidos inexistentes, conservación de mensajes y separación de sesiones.

Utilizan respuestas de modelo simuladas. Verifican la integración
del código; la comprensión del segundo turno se examinó por separado
en la evaluación real.

La advertencia procede de una dependencia. No se añadió un filtro
para ocultarla ni se modificó el paquete instalado.

## Límites y observaciones

El historial de estados del pedido es información del registro
ficticio. La memoria de conversación conserva los mensajes intercambiados.
Son conceptos diferentes.

`InMemorySaver` conserva el estado únicamente durante la vida del
proceso. Esta implementación no guarda conversaciones entre reinicios.

El aislamiento depende de asignar correctamente los identificadores
de conversación; `thread_id` no constituye un mecanismo de autenticación.

El historial se incorpora al contexto de los turnos posteriores y puede
aumentar el consumo de tokens. No se midieron tokens ni costos en esta
evaluación, y no se afirma que el cambio de API reduzca el consumo.

En el segundo turno se solicitó nuevamente el historial completo del
pedido, aunque su estado actual habría bastado. La respuesta fue
correcta; queda como oportunidad de optimización, sin modificar
la evidencia obtenida.

No se implementaron almacenamiento persistente, recorte ni resumen
automático del historial. `recursion_limit` limita pasos del grafo,
no una cantidad exacta de llamadas al modelo.