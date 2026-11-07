# Laboratorio de integración con IA

Repositorio de práctica de la Especialización en Desarrollo con
IA Generativa. Incluye un cliente Python para Gemini con validación,
manejo de errores, reintentos y estimación de costos; un pipeline
de procesamiento y comparación léxica de texto; pruebas unitarias
y ejercicios de aprendizaje.

Incluye una cadena de tres etapas con LangChain para
analizar reclamos, preparar un plan interno y generar un borrador
de respuesta sujeto a revisión. E incorpora un flujo que clasifica
mensajes y selecciona tratamientos para preguntas, quejas,
sugerencias y entradas sin una categoría reconocida.

También incluye agentes que consultan stock y estados de pedidos
ficticios mediante herramientas, con una implementación que incorpora
argumentos estructurados y memoria de conversación por sesión.

## Requisitos

- Git y acceso a Internet para obtener el repositorio y sus dependencias.
- Python instalado. Entorno comprobado: Windows con Python 3.14.7. La compatibilidad con otros sistemas y versiones está pendiente de comprobación.

## Instalación en Windows — PowerShell

Requiere Git y Python instalados. Entorno comprobado:
Windows con Python 3.14.7.

Los siguientes comandos crean una carpeta de trabajo dentro
del perfil del usuario. La carpeta de destino del clon
`especializacion-ia` no debe existir previamente.
Si se elige otro nombre, debe utilizarse también al entrar
en ella.

```powershell
if (Get-Command deactivate -ErrorAction SilentlyContinue) {
    deactivate
}

New-Item -ItemType Directory -Path "$env:USERPROFILE\proyectos-ia" -Force
Set-Location -LiteralPath "$env:USERPROFILE\proyectos-ia"

git clone https://github.com/Lagnay/especializacion-ia.git especializacion-ia
Set-Location -LiteralPath ".\especializacion-ia"

python --version
python -m venv venv

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

La política de ejecución se configura solamente para esta
sesión de PowerShell. Al abrir otra terminal puede ser
necesario repetir ese comando antes de activar el entorno.

Continúa con «Configuración de Gemini» y después con «Uso».

## Instalación en macOS / Linux / WSL

Procedimiento de referencia, pendiente de comprobación.
Requiere Git y Python 3 con soporte para entornos virtuales.

El entorno verificado utiliza Python 3.14.7 en Windows;
no se garantiza compatibilidad con cualquier versión
de Python ni se ha comprobado esta instalación en otros sistemas.

En WSL, trabajar dentro del sistema de archivos de Linux
y crear un entorno propio, separado del de Windows.

La carpeta de destino `especializacion-ia` no debe existir.
Si se elige otro nombre al clonar, utilizarlo también al entrar.

```bash
if command -v deactivate >/dev/null 2>&1; then
    deactivate
fi

mkdir -p "$HOME/proyectos-ia"
cd "$HOME/proyectos-ia"

git clone https://github.com/Lagnay/especializacion-ia.git especializacion-ia
cd especializacion-ia

python3 --version
python3 -m venv venv
source venv/bin/activate

python -m pip install -r requirements.txt
```

Continúa con «Configuración de Gemini» y después con «Uso».
Los comandos que comienzan con `python` en las secciones
siguientes se ejecutan con este entorno virtual activo.

## Configuración de Gemini

Se necesita una credencial propia de Gemini API.

Desde la raíz del repositorio, crear `.env` a partir de
la plantilla, únicamente si todavía no existe.

En Windows — PowerShell:

```powershell
if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}
```

En macOS / Linux / WSL, si `.env` todavía no existe:

```bash
cp .env.example .env
```

Abrir `.env` con un editor y reemplazar el valor ficticio
de `GEMINI_API_KEY` por la credencial propia. Guardar el archivo.

En Windows puede abrirse con `notepad .env`. Si el comando
de Visual Studio Code está disponible, también puede
utilizarse `code .env`.

La credencial real permanece únicamente en la configuración
local. `.env.example` conserva un valor ficticio.

## Uso

Desde la raíz del repositorio, con el entorno virtual activo
y la credencial configurada en `.env`, ejecutar:

```powershell
python -m src.main
```

El programa envía la pregunta de ejemplo definida en `src/main.py`
y muestra el texto generado, el consumo de tokens y una estimación
a tarifas de pago. Esta estimación no representa necesariamente
un cargo: depende del nivel de servicio utilizado.

Las funciones reutilizables se encuentran en `src/consumir_gemini.py`.
La respuesta y su consumo pueden variar entre ejecuciones.

### Cliente modular con reintentos

Para ejecutar el cliente que clasifica errores y reintenta
ante fallos considerados temporales:

```powershell
python -m src.cliente
```

Realiza una consulta real a Gemini y muestra el texto generado.
Permite hasta tres intentos, con esperas exponenciales y una
pequeña variación aleatoria (jitter), limitadas a 30 segundos
por pausa. Los errores de entrada y los estados
HTTP 401 y 403 se comunican sin reintentar.

Cada respuesta recibida con datos de consumo permite calcular
y mostrar un costo de referencia, acumulado durante el proceso
actual. El acumulado se reinicia al ejecutar nuevamente el
programa. Se utilizan tarifas de referencia del laboratorio
fechadas el 16-10-2026; el importe no representa necesariamente
un cargo real.

Para utilizarlo desde otro módulo:

```python
from src.cliente import consultar_modelo

respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
```
Para comprobar el cliente con respuestas simuladas, desde
la raíz del repositorio y con el entorno virtual activo:

```powershell
python -m tests.comprobar_cliente
```

Esta comprobación verifica éxito inmediato, recuperación,
agotamiento de intentos, estados HTTP 401 y 403 y rechazo
de preguntas inválidas. Muestra el resultado de cada escenario
y la cantidad de peticiones realizadas, sin conectarse a Gemini.

### Cadena de reclamos con LangChain

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y la credencial configurada:

```powershell
python -m src.cadena_reclamos
```

Utiliza el mensaje ficticio definido en el módulo y realiza tres
consultas a `gemini-3.5-flash-lite`: análisis, planificación y redacción.
Muestra únicamente el borrador final en la terminal.

`construir_cadena(modelo)` devuelve la cadena sin ejecutarla.
La entrada es un diccionario con la clave `mensaje`; la salida
es texto. El mensaje original se conserva mediante
`RunnablePassthrough.assign` para utilizarlo también en la redacción.

El ejemplo configura un timeout de 30 segundos por solicitud
y desactiva los reintentos automáticos. Esta cadena no utiliza
los reintentos ni el registro de costos de `src/cliente.py`.

No envía mensajes ni registra reclamos en un sistema de atención.
El resultado requiere revisión humana: puede omitir detalles
o introducir afirmaciones y compromisos sin respaldo.
Las respuestas pueden variar.

La ejecución y su revisión están documentadas en el índice
de documentación y evidencias.

### Atención de mensajes con enrutamiento condicional

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y la credencial configurada:

```powershell
python -m src.enrutamiento
```

Ejecuta cuatro mensajes ficticios mediante el modelo
`gemini-3.5-flash-lite`. Clasifica cada mensaje, normaliza la etiqueta
y selecciona un tratamiento para pregunta, queja o sugerencia.
Las etiquetas restantes utilizan una ruta fija de aclaración.

La ruta de quejas reutiliza `src/cadena_reclamos.py`.

El programa muestra el mensaje, la categoría esperada,
la etiqueta normalizada, su coincidencia y la respuesta.
La categoría esperada no se envía al modelo.

`construir_flujo_atencion(modelo)` recibe el modelo y devuelve
el flujo sin ejecutarlo. El flujo acepta un diccionario con
la clave `mensaje` y devuelve `mensaje`, `categoria` y `respuesta`.
`categoria` conserva la etiqueta normalizada, incluso si no es
reconocida.

Para ejecutarlo con protección general se utiliza
`procesar_mensaje_seguro(flujo, mensaje)`. La ruta de quejas tiene
un respaldo propio con `with_fallbacks`: registra el fallo y devuelve
un mensaje fijo, conservando la categoría `queja`.

Si una excepción llega al manejador general, este registra
el error y su traceback, y devuelve las mismas tres claves,
con `categoria: None` y una respuesta controlada.
La ruta desconocida atiende etiquetas no reconocidas;
no sustituye al manejo de excepciones.

Los registros se muestran en la consola; no se guardan en un archivo.
La validación de la credencial y la construcción del modelo ocurren
antes de la ejecución protegida.

Una ejecución exitosa requiere dos invocaciones al modelo para
una pregunta o sugerencia, cuatro para una queja y una para
una entrada enviada a la ruta desconocida. Los cuatro casos
prevén nueve invocaciones si reciben las categorías esperadas.

Configura un timeout de 30 segundos por solicitud y desactiva
los reintentos automáticos. No incorpora el registro de costos
ni los reintentos de `src/cliente.py`.

Muestra borradores en la terminal, sin enviar mensajes ni ejecutar
gestiones de atención. Las respuestas pueden variar y requieren
revisión humana. Una respuesta incorrecta sin excepción no activa
automáticamente el respaldo.

La ejecución, las pruebas y sus límites están disponibles en el índice
de documentación y evidencias.

### Agente con herramientas

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y la credencial configurada:

```powershell
python -m src.agente_con_herramientas
```

Ejecuta cuatro casos: stock, pedido, una consulta combinada y un saludo.
Para ejecutar solamente uno:

```powershell
python -m src.agente_con_herramientas pedido
```

También se aceptan `stock`, `combinado` y `saludo`.
Estos comandos consultan Gemini y consumen cuota.

El agente elige entre dos herramientas con datos locales ficticios.
Muestra herramientas utilizadas, argumentos, observaciones y respuesta
final. No modifica inventario ni realiza gestiones sobre pedidos.

La construcción reutilizable está en `src/agente_con_herramientas.py`
y las herramientas en `src/herramientas_tienda.py`.
La verificación manual y sus límites están disponibles en el índice
de documentación y evidencias.

### Agente con memoria de conversación

Desde la raíz del repositorio, con el entorno virtual activo
y las dependencias instaladas:

```powershell
python -m src.agente_con_memoria
```

Muestra el modo de preparación y no realiza consultas.

Con la credencial configurada, para ejecutar la demostración:

```powershell
python -m src.agente_con_memoria --ejecutar
```

Realiza dos turnos en una conversación y uno en otra independiente.
Muestra herramientas, argumentos, observaciones, respuestas y mensajes
guardados. Consulta Gemini y consume cuota.

La construcción reutilizable está en `src/agente_con_memoria.py`.
La herramienta de pedidos con argumentos validados mediante Pydantic
está en `src/herramientas_pedidos.py`; también se reutiliza
la herramienta de stock.

Utiliza `create_agent`, `InMemorySaver` y conversaciones identificadas
mediante `thread_id`. El estado se conserva durante la ejecución
del proceso y no se guarda entre reinicios. El historial puede aumentar
el consumo de tokens en turnos posteriores.

Se adaptó la guía a la API recomendada y actualizada debido
a la deprecación de `InMemoryChatMessageHistory`. La práctica original
se conserva como referencia y el agente del Bloque 21 mantiene
su implementación.

Para explorar la memoria con respuestas simuladas, sin consultar Gemini:

```powershell
python -m laboratorio.practicas.modulo_02.unidad_2_4.bloque_22.practica_memoria_actual
```

La evaluación real, las pruebas y los límites están documentados
en el índice de documentación y evidencias.

### Agente con supervisión humana y trazas

Desde la raíz, con el entorno virtual activo y las dependencias instaladas:

```powershell
python -m src.agente_supervisado
```

Muestra el modo de preparación, sin consultar Gemini.

Con la credencial configurada, ejecutar por separado:

```powershell
python -m src.agente_supervisado --ejecutar --caso stock
python -m src.agente_supervisado --ejecutar --caso reembolso
```

El primer caso consulta existencias ficticias. El segundo solicita
aprobación humana para simular un reembolso en pesos enteros;
no mueve dinero. Ambos consultan Gemini y consumen cuota.

La aprobación dispone de 30 segundos. En Windows se pulsa `s` o `n`
sin Enter; en Linux/macOS se confirma con Enter.
La ejecución fue comprobada en Windows; los otros sistemas
están pendientes de comprobación.

Cada comando inicia una conversación nueva. Las interacciones
completadas se añaden a
`docs/modulo_02/unidad_2_4/bloque_23/trazas_agente.jsonl`
y las decisiones a `aprobaciones.jsonl` dentro de la misma carpeta.

Para revisar repeticiones consecutivas sin consultar Gemini:

```powershell
python -c "from pathlib import Path; from src.trazas_agente import revisar_trazas; revisar_trazas(Path('docs/modulo_02/unidad_2_4/bloque_23/trazas_agente.jsonl'))"
```

Los límites de autonomía, la evaluación y las restricciones del registro
están disponibles en el índice de documentación y evidencias.

### Procesamiento y evaluación de texto

`src/pipeline_texto.py` contiene las funciones de limpieza,
tokenización, conteo de palabras y coincidencia léxica.

`src/metricas_texto.py` calcula coincidencias conservando las
repeticiones, precisión, cobertura, F1 y promedios por caso.
Precisión divide las coincidencias entre los tokens de respuesta;
cobertura, entre los de referencia. F1 combina ambas mediante su
media armónica. Si cualquiera de los textos procesados queda vacío,
las tres métricas devuelven 0.0.

Para evaluar tres respuestas reales de Gemini, desde la raíz
del repositorio, con el entorno activo y la credencial configurada:

```powershell
python -m src.evaluar_texto
```

Las consultas y referencias del grupo original se definen en
`CASOS_ORIGINALES`, dentro de `src/casos_evaluacion.py`.
`src/evaluar_texto.py` utiliza esos tres casos, conserva la respuesta
original y compara la coincidencia antes y después de procesar
ambos textos.

Esta ejecución realiza tres consultas reales y consume cuota.
Los reintentos pueden añadir peticiones. Las respuestas y los
porcentajes pueden variar entre ejecuciones.

La referencia actual de C01 es `el cielo es azul`, coherente con
la instrucción de responder en minúsculas y sin puntuación.

Las evidencias de los Bloques 15 y 16 conservan la referencia
utilizada entonces: `El cielo es azul.`. Para la respuesta
`el cielo es azul`, aquella referencia produce una coincidencia
cruda de 50 %, mientras que la actual produce 100 %.
La coincidencia procesada y el F1 son 100 % en ambos casos.

Los registros históricos conservan sus datos originales;
no se actualizan al modificar el catálogo.

La evaluación también calcula precisión, cobertura y F1, y guarda
un registro JSON nuevo en `docs/modulo_02/unidad_2_2/bloque_16`, con fecha y hora en el
nombre. Crea la carpeta si no existe y conserva registros anteriores.
El archivo incluye consultas, referencias, respuestas completas,
métricas, configuración y errores registrados.

Para resumir un registro guardado, sin consultar la API ni modificarlo:

```powershell
python -m src.resumir_evaluacion "docs/modulo_02/unidad_2_2/bloque_16/resultados_metricas_20261027_202048_949209.json"
```

El comando muestra los promedios y ordena los casos por F1 ascendente.
Para analizar otra ejecución, sustituye la ruta por la de su registro.
El resumen local no requiere una credencial de Gemini.

Estas métricas miden coincidencia léxica, no calidad semántica ni
veracidad. Un F1 alto no garantiza una respuesta correcta.

Los porcentajes de coincidencia cruda y procesada utilizan:

palabras únicas compartidas / palabras únicas de la referencia

Si la referencia queda vacía, esta coincidencia devuelve 0.0.
Esta medida de palabras únicas no evalúa significado, orden ni
veracidad, y no penaliza palabras adicionales.
Un 100 % no garantiza que la respuesta sea correcta.

La limpieza convierte a minúsculas, elimina caracteres distintos
de los alfanuméricos, guion bajo y espacios en blanco, y normaliza
los espacios. Puede unir fragmentos separados por puntuación.

Los tokens de este pipeline son unidades separadas por espacios
en blanco; no equivalen necesariamente a los tokens contabilizados
por la API.

Para probar el procesamiento local desde la terminal, en la raíz
del repositorio y con el entorno virtual activo:

```powershell
python -c "from src.pipeline_texto import procesar_texto; print(procesar_texto('El Cielo, es AZUL!'))"
```

Salida esperada:

```text
['el', 'cielo', 'es', 'azul']
```

Este comando no consulta Gemini ni requiere credenciales.

La estructura adapta los ejemplos del curso: los módulos están
en `src`, las pruebas en `tests` y los comandos se ejecutan desde
la raíz del repositorio.

### Evaluación de un lote de veinte casos

El catálogo completo se define en `src/casos_evaluacion.py`.
Incluye preguntas, referencias y aspectos esperados para orientar
la revisión humana.

Desde la raíz del repositorio, con el entorno virtual activo,
para comprobar el modo de preparación:

```powershell
python -m src.evaluar_lote
```

Este comando muestra los casos preparados y la ruta del registro,
sin consultar Gemini ni crear archivos.

Para ejecutar el lote, con la credencial configurada:

```powershell
python -m src.evaluar_lote --ejecutar
```

Una evaluación nueva realiza veinte consultas previstas.
Los reintentos del cliente pueden añadir peticiones.
Se introducen cinco segundos entre casos y se guarda el progreso
en `docs/modulo_02/unidad_2_2/bloque_17/resultados_metricas.json`.

Si falla un caso, el lote guarda el avance y se detiene.
Después de resolver la causa, el mismo comando continúa únicamente
con los casos pendientes. Si ya hay veinte resultados completados,
no repite las consultas.

El archivo conserva el catálogo, las instrucciones, las respuestas,
las referencias, los criterios, las fechas y las métricas.
Los errores registrados corresponden a los casos actualmente fallidos.

Para iniciar otra evaluación independiente, utiliza `--registro`
seguido de la ruta de un archivo nuevo.

Ejemplo opcional, que realiza nuevas consultas y consume cuota:

```powershell
python -m src.evaluar_lote --ejecutar --registro "docs/modulo_02/unidad_2_2/bloque_17/resultados_metricas_otra_ejecucion.json"
```

Para reanudar esa evaluación, repite el comando con la misma ruta.
Si cambian el catálogo o la instrucción, el programa rechaza
continuar el registro existente.

El repositorio incluye un lote ya completado. Ejecutar el comando
sobre ese registro no genera respuestas nuevas.

Para resumir el lote guardado sin consultar la API:

```powershell
python -m src.resumir_evaluacion "docs/modulo_02/unidad_2_2/bloque_17/resultados_metricas.json"
```

La revisión humana y los límites observados están disponibles
en el índice de documentación y evidencias.

## Pruebas locales del módulo

Desde la raíz del repositorio y con el entorno virtual activo:

```powershell
python -m tests.comprobar_extraccion
python -m tests.comprobar_json_invalido
python -m tests.comprobar_timeout
```

Estas pruebas comprueban extracción y manejo de fallos preparados
o simulados; no envían peticiones a Gemini. La ejecución indicada
en «Uso» comprueba la conexión real.

## Pruebas unitarias

Desde la raíz del repositorio, con el entorno virtual activo
y las dependencias instaladas, para ejecutar todas las pruebas:

```powershell
python -m pytest tests -v
```

Para ejecutar únicamente las pruebas del cliente:

```powershell
python -m pytest tests/test_cliente.py -v
```

Para ejecutar únicamente las pruebas del pipeline:

```powershell
python -m pytest tests/test_pipeline_texto.py -v
```

Para ejecutar únicamente las pruebas de las métricas:

```powershell
python -m pytest tests/test_metricas_texto.py -v
```

Comprueban coincidencias con repeticiones, cálculo de métricas,
entradas vacías, ausencia de coincidencias y promedios por caso.

Para ejecutar únicamente las pruebas del lote:

```powershell
python -m pytest tests/test_evaluar_lote.py -v
```

Comprueban el guardado, la conservación del avance, la reanudación
sin repetir resultados y el rechazo de cambios de catálogo o
instrucción. Simulan las respuestas del modelo y las esperas.

Para ejecutar únicamente la prueba de la cadena de reclamos:

```powershell
python -m pytest tests/test_cadena_reclamos.py -v
```

Comprueba tres llamadas simuladas, el paso del análisis y del plan,
la conservación del mensaje original y la salida final.
No consulta Gemini ni evalúa la calidad de sus respuestas.

Para ejecutar únicamente las pruebas de enrutamiento:

```powershell
python -m pytest tests/test_enrutamiento.py -v
```

Comprueban selección de una sola ruta, etiquetas desconocidas,
normalización e integración del flujo. También verifican el respaldo
de quejas, la protección general ante fallos de clasificación y de
otras rutas, los registros de diagnóstico y la conservación del
formato de salida. Los mensajes vacíos o ambiguos se prueban con
una clasificación simulada. No consultan Gemini.

Para ejecutar únicamente las pruebas del agente con memoria:

```powershell
python -m pytest tests/test_agente_con_memoria.py -v
```

Comprueban argumentos de la herramienta, pedidos inexistentes,
conservación del historial y separación de sesiones mediante
respuestas simuladas. No consultan Gemini.

Para ejecutar únicamente las pruebas del agente supervisado:

```powershell
python -m pytest tests/test_agente_supervisado.py -v
```

Comprueban aprobación y rechazo, montos inválidos, registro de decisiones,
fallos de escritura e integración y extracción de acciones.
Utilizan respuestas simuladas y archivos temporales, sin consultar Gemini.

En el entorno probado puede aparecer un `DeprecationWarning`
de `google-genai`, relacionado con `_UnionGenericAlias`.
La ejecución verificada terminó con todas las pruebas pasadas.

Las pruebas del cliente comprueban estados HTTP, reintentos,
costos y coordinación mediante respuestas simuladas.

El jitter hace variables las esperas reales del cliente.
Las pruebas de reintento verifican la cantidad de intentos
y pausas solicitadas, sin exigir un valor aleatorio exacto.
Sustituyen `time.sleep`, por lo que no esperan realmente.

La fixture aísla el acumulado de costos entre casos.

Las pruebas del pipeline comprueban normalización, entradas
inválidas, texto vacío, conteos y coincidencia léxica.

Estas pruebas no consultan Gemini ni requieren una credencial
válida. Cada caso debe aparecer como `PASSED`.

## Comprobación

Con el entorno activo:

```sh
python -c "import sys; print(sys.executable); print('Entorno virtual:', sys.prefix != sys.base_prefix)"
python -m pip check
python -c "import requests; from google import genai; from dotenv import load_dotenv; print('Importaciones OK')"
```

El ejecutable debe pertenecer al entorno creado. Se esperan `Entorno virtual: True`, `No broken requirements found.` e `Importaciones OK`.

Estas comprobaciones no requieren credenciales ni envían solicitudes al proveedor. `python-dotenv` es el paquete instalado, `dotenv` el módulo importado y `load_dotenv` una de sus funciones.

## Banco de prompts

Desde la raíz del repositorio, con el entorno activo
y la credencial configurada:

```powershell
python -m prompts.test_consistencia
```

Realiza nueve consultas reales y actualiza
`prompts/registro_resultados.json`.

Para probar solamente el resumen:

```powershell
python -m prompts.test_consistencia resumir_mensaje
```

Realiza tres consultas y actualiza
`prompts/registro_resultados_parcial.json`.

Estas ejecuciones modifican los registros guardados.
Los resultados pueden variar entre pruebas.

## Comprobación de seguridad

Desde la raíz del repositorio:

```powershell
git ls-files -- .env .env.example requirements.txt
git check-ignore -v -- .env venv/Scripts/python.exe
git --no-pager log --all --oneline -- .env
git status -sb
```

Deben aparecer `.env.example` y `requirements.txt` como
versionados, pero no `.env`. Las reglas de exclusión deben
cubrir `.env` y `venv`. La consulta del historial de `.env`
no debe devolver commits.

Si se parte de una copia limpia, la instalación y la ejecución
de `python -m src.main` deben mantener limpio el estado de Git.

Reejecutar el banco de prompts puede modificar sus registros.
Ejecutar `python -m src.evaluar_texto` crea un registro nuevo
en `docs/modulo_02/unidad_2_2/bloque_16`, que aparecerá como archivo sin seguimiento
hasta incorporarlo a Git.

Ejecutar `python -m src.evaluar_lote --ejecutar` puede crear o
actualizar el registro del lote en `docs/modulo_02/unidad_2_2/bloque_17`, por lo que
pueden aparecer cambios esperados en Git.

Ejecutar `python -m src.resumir_evaluacion` solamente lee
el registro seleccionado y muestra su análisis.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `src/` | Módulos de la aplicación y programa principal |
| `laboratorio/practicas/` | Ejercicios y versiones didácticas organizados por módulo, unidad y bloque |
| `tests/` | Pruebas unitarias y scripts de comprobación local |
| `prompts/` | Banco de prompts, validación y registros de resultados |
| `docs/` | Documentación y evidencias organizadas por módulo, unidad y bloque, además de documentos generales |
| `requirements.txt` | Paquetes y versiones del entorno |
| `.env.example` | Plantilla de configuración sin credenciales reales |

Las prácticas se conservan en `laboratorio/practicas`, separadas
de los módulos de la aplicación. Sus carpetas identifican el módulo,
la unidad y el bloque del curso.

Se ejecutan desde la raíz del repositorio, con el entorno virtual
activo, mediante `python -m`. Por ejemplo, esta práctica local
interpreta un JSON sin consultar Gemini:

```powershell
python -m laboratorio.practicas.modulo_01.unidad_1_3.bloque_05.practica_json
```

Otras prácticas sí realizan consultas reales o ensayos de varias
peticiones; debe revisarse su contenido antes de ejecutarlas.

El entorno `venv/` y la configuración local `.env` están excluidos de Git. Cada instalación debe crear su propio entorno; las credenciales no se publican.

## Documentación y evidencias

[Consultar el índice de documentación y evidencias](docs/INDICE_README.md).