# Bloque 26 — Recuperación semántica y respuestas con citas

## Implementación

`src/recuperacion.py` abre la colección del corpus del bloque 24,
genera el embedding de la pregunta y recupera hasta `k` fragmentos.
El valor predeterminado es 3.

Reutiliza el modelo, las dimensiones, la ruta absoluta y el nombre
de colección definidos en `src/indexar_corpus.py`.

Los fragmentos forman un contexto numerado. Un diccionario relaciona
cada número con la fuente conservada en sus metadatos.
Los números corresponden a la posición dentro de cada consulta.

Con `--responder`, el prompt se envía al cliente Gemini del proyecto.
Las instrucciones solicitan citar cada afirmación y reconocer
cuando el contexto resulta insuficiente.

El corpus contiene resúmenes redactados a partir del código.
La metadata `fuente` identifica el archivo que respalda cada resumen.

## Comprobaciones reales

Se utilizó `gemini-embedding-001` para recuperar fragmentos,
con `k=3`, y el cliente de generación configurado en el proyecto.

### Consulta sobre memoria

Pregunta:

> ¿Se mantienen las conversaciones del agente si cierro el programa?

El primer fragmento recuperado explicó que la memoria se pierde
al terminar el proceso. Los siguientes correspondieron al costo
de sesión y a las esperas entre intentos.

Mapa de citas observado:

```python
{
    1: "src/agente_con_memoria.py",
    2: "src/cliente.py",
    3: "src/cliente.py",
}
```

Este ensayo imprimió el contexto y el prompt preparado.

### Respuesta sobre tiempos de espera

Pregunta:

> ¿Qué hace el programa cuando la conexión tarda demasiado?

El contexto recuperado incluyó, en este orden:

1. Espera creciente, variación aleatoria y límite de treinta segundos.
2. Hasta tres intentos y condiciones que pueden activar un reintento.
3. Aprobación del reembolso simulado.

Respuesta completa observada:

> Cuando se agotan los tiempos de espera, se puede activar un reintento [2].

La cita `[2]` correspondió a `src/cliente.py`.
El segundo fragmento respaldaba la afirmación. El código del cliente
convierte los tiempos de espera agotados en errores reintentables.

Costo de referencia mostrado para la generación: `0.000103000 USD`.

### Pregunta fuera del alcance del corpus

Pregunta:

> ¿Cuántos días tiene un cliente para devolver un producto en esta tienda?

El contexto incluyó la aprobación del reembolso simulado y dos
fragmentos sobre reintentos. Carecía de una política que estableciera
el plazo de devolución.

Respuesta completa observada:

> No tengo información suficiente [1, 2, 3].

Mapa de citas observado:

```python
{
    1: "src/herramientas_supervisadas.py",
    2: "src/cliente.py",
    3: "src/cliente.py",
}
```

La respuesta reconoció la insuficiencia del contexto.
La política ficticia de la réplica del bloque 25 pertenece
a otra colección.

Costo de referencia mostrado para la generación: `0.000089200 USD`.

Los importes proceden del cliente de generación.
El cálculo mostrado no incorpora el consumo del modelo de embeddings.

## Ajustes derivados de las pruebas

### Desconexión durante la recuperación

Se observó un `RemoteProtocolError` encapsulado por el conector
de Gemini durante la primera consulta sobre tiempos de espera.

Se añadió manejo alrededor de la recuperación para detectar
`TransportError`, directamente o mediante `__cause__`,
y comunicarlo como `ConnectionError`.

El programa conserva la causa técnica y finaliza con código de error.
La transformación se comprobó localmente con una desconexión simulada.
Una ejecución posterior completó la consulta real.

### Citas agrupadas

La primera versión del lector reconocía `[2]`, pero omitía
`[1, 2, 3]`. Por ello imprimió erróneamente
«La respuesta no incluye citas» en el ensayo fuera de alcance.

Se corrigió `resolver_citas` para admitir referencias individuales
y grupos separados por comas, con espacios opcionales.
Conserva una entrada por número y señala las referencias
que quedan fuera del contexto.

## Pruebas y límites

Los seis casos de `tests/test_recuperacion.py` comprueban citas
individuales, agrupadas, repetidas, con espacios, fuera de contexto
y respuestas sin citas.

El conjunto completo terminó con 85 pruebas pasadas.
Se observaron advertencias de deprecación de `google-genai`
y de la telemetría de Chroma.

La existencia de un número en el mapa permite localizar la fuente.
El respaldo de cada afirmación requiere comparar la respuesta
con el fragmento citado, como se hizo en el ensayo de reintentos.

Los resultados observados cubren estas consultas.
La evaluación con un conjunto etiquetado corresponde al bloque 27.

## Reproducción

Desde la raíz, con el entorno virtual activo, las dependencias,
la credencial y el índice configurados:

```powershell
python -m src.recuperacion "¿Qué hace el programa cuando la conexión tarda demasiado?"
python -m src.recuperacion "¿Qué hace el programa cuando la conexión tarda demasiado?" --responder
```

El primer comando consulta el modelo de embeddings e imprime el prompt.
El segundo añade la generación y el listado de fuentes citadas.
Ambos consumen cuota.

Pruebas locales:

```powershell
python -m pytest tests/test_recuperacion.py -v
```