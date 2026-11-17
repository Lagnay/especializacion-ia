# Bloque 32 — Versionado de prompts, supervisión y matriz de riesgos

Fecha de revisión: 15 de noviembre de 2026.

## Objetivo y alcance

Registrar versiones propias de las instrucciones RAG, revisar sus diferencias y exigir una decisión humana antes de seleccionar una versión en el estado local de una solicitud.

La matriz identifica cinco riesgos del laboratorio, sus estimaciones, controles existentes y puntos de supervisión.

Este bloque no realiza consultas nuevas a Gemini. La activación demostrada no modifica automáticamente la instrucción del flujo RAG existente ni constituye un despliegue.

Nota de continuidad, 16 de noviembre de 2026: el
[Gate 2](../../unidad_2_8/bloque_s1/GATE2_INTEGRACION_Y_ORQUESTACION.md)
integra después la aprobación persistente con el servicio RAG y utiliza
el texto aprobado en sus consultas. Este documento conserva el alcance
y los resultados históricos del Bloque 32, revisados el 15 de noviembre.

## Componentes

| Componente | Función |
|---|---|
| [registro_prompts.py](../../../../src/registro_prompts.py) | Texto, huella, autor del registro, fecha, nota y procedencia de validación de cada versión. |
| [grafo_supervision.py](../../../../src/grafo_supervision.py) | Propuesta, interrupción, decisión y selección de la versión activa en el estado local. |
| [matriz_riesgos.py](../../../../src/matriz_riesgos.py) | Cinco riesgos propios, puntajes, categorías, controles y sensibilidad. |
| [versiones_prompts.json](versiones_prompts.json) | Instantánea de las dos versiones registradas y sus metadatos. |
| [Prácticas del bloque](../../../../laboratorio/practicas/modulo_02/unidad_2_7/bloque_32/) | Ejercicios de versionado, interrupción, persistencia SQLite y cálculo de riesgos. |

## Versiones propias registradas

| Huella abreviada | Procedencia | Validación conservada |
|---|---|---|
| `91c5b827469d` | Instrucciones incluidas en el prompt del Bloque 28. | Consulta real, con fecha y configuración recuperadas de su evidencia. |
| `7f32d8c7857f` | Constante `INSTRUCCION_SISTEMA` del Bloque 31. | Simulación local; no se atribuye validación con un modelo real. |

La versión anterior se extrae del primer registro del JSONL del Bloque 28, antes del contexto. En ese flujo formaba parte de un prompt de texto; no era un `SystemMessage` separado.

La versión del Bloque 31 añade la instrucción de tratar el contexto como datos no confiables y modifica la frase para responder cuando falta información. Se utiliza como instrucción de sistema en la construcción de mensajes de ese bloque.

Las huellas completas están en la instantánea. SHA-256 identifica el texto exacto, incluidos espacios y saltos de línea; no identifica por sí solo el modelo, sus parámetros o los demás metadatos.

La comparación por palabras permite revisar cambios de contenido, pero omite diferencias exclusivamente de espacios. Los tests conservan un ejemplo de esa limitación.

El campo `autor` identifica al registrante como `laboratorio`. La fecha corresponde al registro realizado en este bloque; la fecha de la consulta histórica se conserva por separado.

`ultima()` devuelve la última versión registrada de un nombre. Registrar una versión no la activa.

El registro se mantiene en memoria. Sus lecturas devuelven copias independientes, incluidos los metadatos anidados. La instantánea JSON conserva la evidencia, pero no se carga automáticamente como catálogo ni guarda decisiones de aprobación.

## Supervisión humana

El grafo copia el catálogo disponible al construirse e identifica las versiones mediante nombre y huella completa.

El flujo:

1. Comprueba que la versión propuesta esté registrada y que su texto coincida con la huella.
2. Se interrumpe mostrando el texto, la huella, la nota y la procedencia de validación.
3. Espera una decisión booleana.
4. Si se aprueba, selecciona la huella propuesta en el estado local.
5. Si se rechaza, conserva la versión previamente activa.

Se bloquean las decisiones no booleanas, las huellas abreviadas o diferentes y la resolución de solicitudes sin aprobación pendiente. La función de creación también impide sobrescribir una solicitud existente con el mismo `thread_id`.

Estas comprobaciones corresponden al uso secuencial del laboratorio. No implementan autenticación de revisores ni control de concurrencia para un servicio de producción.

### Resultados observados

Se ejecutó el comando interactivo dos veces, con identificadores nuevos:

| Decisión humana | Estado inicial | Resultado | Huella activa final |
|---|---|---|---|
| Aprobar con `s` | Sin versión activa. | `activada_en_estado_local` | `7f32d8c7857f…` |
| Rechazar con `n` | Sin versión activa. | `rechazada` | `None` |

En ambos casos se comprobó la interrupción antes de decidir. Los tests también verifican que rechazar conserve una versión anterior cuando ya existe.

La demostración usa `InMemorySaver`: su estado se pierde al terminar el proceso. La práctica SQLite conserva una solicitud entre procesos separados; el test del grafo propio comprueba la recuperación de una pausa al cerrar y reabrir la conexión a una base temporal.

Las bases locales se excluyen de Git mediante `/checkpoints/`. La persistencia no equivale por sí sola a un historial completo de auditoría ni a un despliegue.

## Matriz de riesgos

Las estimaciones consideran el laboratorio y los controles existentes. Probabilidad e impacto utilizan escalas ordinales de 1 a 5; no son porcentajes ni frecuencias medidas.

La probabilidad va de muy poco probable a muy probable. El impacto va de inconveniente menor a consecuencia grave dentro del alcance evaluado.

Se aplica `probabilidad × impacto` y la convención del curso:

- BAJO: 1 a 3.
- MEDIO: 4 a 8.
- ALTO: 9 a 14.
- CRITICO: 15 a 25.

| ID | Riesgo | P | I | Puntaje | Categoría |
|---|---|---:|---:|---:|---|
| R01 | Responder con un resumen desactualizado del código. | 3 | 3 | 9 | ALTO |
| R02 | Usar un prompt modificado sin revisar sus cambios. | 3 | 3 | 9 | ALTO |
| R05 | Interrumpir una evaluación al superar la cuota. | 4 | 2 | 8 | MEDIO |
| R03 | Obedecer instrucciones incluidas en un documento. | 2 | 3 | 6 | MEDIO |
| R04 | Guardar datos personales al reutilizar el registro detallado con consultas reales de clientes. | 2 | 3 | 6 | MEDIO |

Las justificaciones completas y las condiciones de cada fila están en `MIS_RIESGOS`.

R05 tiene un antecedente observado: el error de cuota del Bloque 30 interrumpió el caso C16. Se conservaron quince respuestas y se completaron las cinco restantes al reanudar.

R04 es condicional: las evidencias actuales utilizan datos ficticios. No se afirma que haya ocurrido una filtración de datos personales.

### Controles existentes y límites

- **R01 — Bloque 24:** la colección identifica el contenido y la configuración indexados. No detecta cambios en los archivos de código mencionados como fuentes si sus resúmenes no se actualizan.
- **R02 — Bloque 32:** registro, comparación y aprobación vinculada a la huella completa. Su alcance actual es la selección local, sin imponer automáticamente ese control al flujo RAG existente.
- **R03 — Bloque 31:** filtrado de patrones, roles separados, contexto delimitado y omisión de generación si no queda contexto aceptado. Las pruebas muestran falsos positivos y falsos negativos; no es una garantía contra inyección.
- **R04 — Bloque 31:** el logger instrumentado conserva metadatos seleccionados en lugar del contenido completo. Esto no cambia el registro detallado histórico del Bloque 28.
- **R05 — Bloque 30:** guardado por caso, registro del error y reanudación sin repetir respuestas completadas.

### Supervisión de los riesgos ALTO

**R01:** antes de modificar el corpus, quien mantiene el laboratorio debe comparar los resúmenes con los archivos indicados como fuentes, revisar las diferencias y corregir las divergencias. Si cambia el corpus, debe indexar su nueva versión y verificarla antes de utilizarla. La revisión debe repetirse cuando cambien las fuentes; no existe una comprobación automática de equivalencia.

**R02:** antes de autorizar una propuesta, debe revisar el texto completo, sus diferencias y la procedencia de validación. El grafo exige una decisión antes de seleccionar la versión local. La integración de esa selección con el flujo RAG existente queda pendiente.

Estas revisiones no requieren aprobar cada respuesta ordinaria del RAG.

### Sensibilidad

Los cinco riesgos quedan al límite según `esta_en_el_limite`: variar un punto en una sola dimensión puede cambiar su categoría.

Esto recomienda revisar las estimaciones, no demuestra que sean incorrectas ni que haya ocurrido un incidente. Tampoco se presupone una revisión por otra persona que no se haya realizado.

## Reproducción local

Desde la raíz del repositorio, con el entorno activo:

```powershell
python -m src.registro_prompts
python -m src.matriz_riesgos
python -m src.grafo_supervision
```

El tercer comando muestra la propuesta y solicita `s` o `n`, seguido de Enter. Cada ejecución crea una solicitud nueva en memoria.

Estos comandos no consultan APIs ni escriben automáticamente la instantánea JSON. Si cambian las instrucciones, las huellas mostradas pueden diferir de las conservadas en la evidencia histórica.

## Validación

```powershell
python -m pytest tests/test_registro_prompts.py tests/test_grafo_supervision.py tests/test_matriz_riesgos.py -v
python -m pytest tests -q
python -m pip check
```

Resultados comprobados:

| Grupo | Casos pasados |
|---|---:|
| Registro de prompts | 16 |
| Grafo de supervisión | 13 |
| Matriz de riesgos | 23 |
| Suite completa del repositorio | 254 |

Las pruebas del bloque utilizan datos locales y bases temporales, sin consultar APIs. `pip check` no encontró dependencias incompatibles.

Persisten dos advertencias de deprecación de dependencias: `_UnionGenericAlias` en `google-genai` y `asyncio.iscoroutinefunction` en Chroma. No se ocultaron.

Se incorporaron `langgraph-checkpoint-sqlite==3.1.3` y sus dependencias nuevas `aiosqlite==0.22.1` y `sqlite-vec==0.1.9`.

## Continuidad

Este bloque cierra el trabajo de la Unidad 2.7. La integración funcional del Módulo 2 continúa en el Gate 2, Unidad 2.8.

El repaso conceptual completo del módulo se realizará antes de comenzar el Módulo 3.