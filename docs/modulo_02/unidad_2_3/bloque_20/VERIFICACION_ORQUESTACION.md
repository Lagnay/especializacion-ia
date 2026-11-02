# Bloque 20 — Manejo de errores y verificación de la orquestación

## Objetivo

Extender el flujo de enrutamiento del Bloque 19 para que las
excepciones durante su ejecución tengan una respuesta controlada
y dejen información de diagnóstico.

Se conserva la clasificación, la selección de rutas y el formato
de salida del flujo.

## Implementación

Archivo principal: [src/enrutamiento.py](../../../../src/enrutamiento.py).

La ruta de quejas utiliza `construir_cadena_queja_segura` para
envolver la cadena de análisis, planificación y redacción con
`with_fallbacks`.

Si esa cadena lanza una excepción de tipo `Exception`, el respaldo:

- Registra la causa mediante `logger.warning`.
- Devuelve un mensaje fijo que indica que no se pudo completar
  el análisis y permite intentar nuevamente más tarde.
- No promete contacto humano, creación de un ticket ni gestiones
  que el programa no realiza.

`exception_key="_error_queja"` permite que el respaldo reciba
la excepción. Antes de ejecutar el componente protegido se crea
una copia superficial del diccionario, para evitar que esa clave
interna se añada al estado original.

La función `procesar_mensaje_seguro(flujo, mensaje)` ejecuta el flujo
completo dentro de un `try/except`. Si una excepción no fue resuelta
por el respaldo de una ruta, registra el error y su traceback
mediante `logger.exception`, y devuelve una respuesta general.

Las rutas de pregunta y sugerencia están cubiertas por esta
protección exterior. La ruta desconocida devuelve un texto fijo.

## Contrato de salida

Cuando el flujo termina correctamente, devuelve un diccionario con:

- `mensaje`: entrada original.
- `categoria`: etiqueta normalizada del clasificador.
- `respuesta`: texto de la ruta seleccionada.

Si se activa el respaldo de quejas, se conserva la categoría
`queja` y el mensaje de respaldo ocupa `respuesta`.

Si interviene el manejador general, devuelve las mismas tres
claves, pero `categoria` contiene `None`. Este resultado de error
no recupera automáticamente la clasificación de un estado
intermedio, aunque el fallo haya ocurrido después de clasificar.

`None` es diferente de `desconocida`: esta última sí es una
etiqueta producida por la clasificación.

## Registro de errores

La ejecución principal configura los registros para mostrarlos
en la consola. No se crea un archivo de logs.

- `WARNING`: fallo de la ruta de quejas resuelto por su respaldo.
- `ERROR` con traceback: excepción atendida por el manejador general.

Un traceback emitido por `logger.exception` es información de
diagnóstico. No significa que la excepción haya quedado sin manejar.

## Prácticas realizadas

Antes de integrar la protección al módulo se realizaron estas
prácticas, conservadas en `	laboratorio/practicas/modulo_02/unidad_2_3/bloque_20`:

- `practica_fallback_basico.py`: éxito principal y activación del respaldo.
- `practica_fallback_multiple.py`: alternativas en orden y detención
  en la primera que funciona.
- `practica_fallback_logging.py`: registro del error que activa el respaldo.
- `practica_ejecucion_segura.py`: fallo anterior al componente protegido
  y captura mediante un manejador exterior.

Estas prácticas utilizan operaciones simuladas y no consultan Gemini.

## Checklist de verificación

| Área | Comprobación |
| --- | --- |
| Clasificación | Normalización de espacios, mayúsculas y punto final; tratamiento de etiquetas no reconocidas. |
| Bifurcación | Selección de una sola ruta para queja, pregunta y sugerencia; ruta por defecto comprobada. |
| Camino normal | Integración de clasificación y cadena de reclamos mediante respuestas simuladas. |
| Respaldo de quejas | Activación ante una excepción, registro de la causa y conservación de la entrada. |
| Respaldo integrado | El flujo completo conserva la categoría `queja` y devuelve su respuesta de respaldo. |
| Protección general | Fallos de clasificación, pregunta y sugerencia devuelven una respuesta controlada y registran la causa. |
| Entradas vacías o ambiguas | Recorrido hacia la ruta desconocida cuando el clasificador simulado devuelve esa etiqueta. |

Las etiquetas no reconocidas se conservan normalizadas y seleccionan
la ruta por defecto; no se convierten automáticamente en una etiqueta
canónica.

Las pruebas de mensajes vacíos o ambiguos verifican el recorrido
del programa bajo una salida simulada del clasificador. No demuestran
que el modelo real vaya a clasificarlos siempre de esa manera.

## Reproducción de las pruebas

Desde la raíz del repositorio, con el entorno virtual activo
y las dependencias instaladas:

```powershell
python -m pytest tests/test_enrutamiento.py -v
python -m pytest tests -q
```

Las pruebas están en
[tests/test_enrutamiento.py](	../../../../tests/test_enrutamiento.py).
Utilizan componentes simulados y no requieren una credencial válida
ni realizan consultas a Gemini.

Resultados observados al finalizar el bloque:

```text
23 passed, 1 warning in 0.87s
63 passed, 1 warning in 1.03s
```

Los 23 casos de enrutamiento están incluidos en los 63 del proyecto;
no son cantidades que deban sumarse.

La advertencia procede de `google-genai`, en `google/genai/types.py`,
por el uso de `_UnionGenericAlias`, cuya eliminación está anunciada
para Python 3.17. No impidió completar las pruebas en el entorno
utilizado: Windows, Python 3.14.7 y pytest 9.1.1.

## Alcance y límites

- Se verifican los escenarios simulados descritos; esto no garantiza
  disponibilidad del proveedor ni calidad semántica de sus respuestas.
- Una respuesta incorrecta que no lance una excepción no activa
  automáticamente un fallback.
- El respaldo de quejas sustituye la salida de toda esa ruta:
  no reanuda desde el paso fallido. Los pasos anteriores pueden
  haber consumido llamadas.
- Los respaldos no añaden reintentos ni crean un timeout.
  El modelo mantiene el timeout de 30 segundos por solicitud
  y los reintentos automáticos desactivados.
- Capturar `Exception` también puede atender errores de programación.
  Los registros deben revisarse para investigar su causa.
- La protección general cubre la ejecución mediante
  `procesar_mensaje_seguro`; la validación de la credencial y
  la construcción del modelo ocurren antes de esa llamada.
- El programa muestra borradores; no envía mensajes ni realiza
  operaciones en un sistema de atención.

Las respuestas reales del Bloque 19 se conservan como evidencia
histórica. En este bloque los nuevos fallos se comprobaron mediante
simulación, sin provocar fallos adicionales en la API.