# Bloque 21 — Agente con dos herramientas propias

## Objetivo e implementación

Construir un agente para una tienda ficticia, con dos herramientas
de propósitos distintos, y verificar su elección mediante
`intermediate_steps`.

Archivos:

- [Herramientas reutilizables](../../../../src/herramientas_tienda.py).
- [Construcción y ejecución del agente](../../../../src/agente_con_herramientas.py).
- [Prácticas previas](../../../../laboratorio/practicas/modulo_02/unidad_2_4/bloque_21/).

Las herramientas son:

- `consultar_stock(producto)`: consulta existencias ficticias.
- `consultar_estado_pedido(pedido_id)`: consulta estados ficticios
  y devuelve un mensaje controlado si no encuentra el identificador.

Ambas utilizan `@tool`, argumentos tipados y descripciones que
explican cuándo utilizarlas.

`construir_agente(modelo)` recibe el modelo y devuelve un
`AgentExecutor` sin realizar consultas durante la construcción.
Se utilizan `create_tool_calling_agent`, `ChatPromptTemplate`
y `MessagesPlaceholder("agent_scratchpad")`.

La implementación sigue la interfaz solicitada por la actividad,
disponible en `langchain-classic`.

## Configuración y reproducción

Desde la raíz, con el entorno virtual activo, las dependencias
instaladas y `GEMINI_API_KEY` configurada en `.env`:

```powershell
python -m src.agente_con_herramientas
```

Ejecuta cuatro entradas reales al agente. Cada entrada puede
producir varias llamadas al modelo y consume cuota.

Para ejecutar solamente un caso:

```powershell
python -m src.agente_con_herramientas pedido
```

Casos disponibles: `stock`, `pedido`, `combinado` y `saludo`.

Configuración utilizada:

- Modelo: `gemini-3.5-flash-lite`.
- Timeout: 30 segundos por solicitud.
- Reintentos automáticos del modelo desactivados.
- Máximo de cuatro iteraciones del ejecutor.
- `verbose=True`.
- `return_intermediate_steps=True`.

Los datos de las herramientas son ficticios y locales.
No se consulta un inventario ni un sistema de pedidos real.

## Criterios definidos antes de ejecutar

| Caso | Herramientas esperadas | Datos esperados |
| --- | --- | --- |
| Stock | `consultar_stock` | Arroz: 12 unidades. |
| Pedido | `consultar_estado_pedido` | P-301: en preparación. |
| Combinado | Ambas herramientas | Leche: 8 unidades; P-302: despachado. |
| Saludo | Ninguna | Respuesta directa y traza vacía. |

La comparación automática de selección utiliza conjuntos de nombres.
No comprueba argumentos, repeticiones ni corrección factual.
Estos aspectos se revisaron sobre las trazas y respuestas observadas.

## Resultados reales observados

### Caso stock

Entrada:

> ¿Cuántas unidades de arroz quedan en el catálogo ficticio?

Traza:

- Herramienta: `consultar_stock`.
- Argumentos: `{"producto": "arroz"}`.
- Observación: `Stock ficticio de arroz: 12 unidades.`

Respuesta completa:

> Quedan 12 unidades de arroz en el catálogo.

La selección coincidió con la esperada y la respuesta respetó
el resultado de la herramienta.

### Caso pedido

Entrada:

> ¿Cuál es el estado del pedido P-301 del registro ficticio?

Traza:

- Herramienta: `consultar_estado_pedido`.
- Argumentos: `{"pedido_id": "P-301"}`.
- Observación: `Estado ficticio de P-301: en preparación.`

Respuesta completa:

> El pedido P-301 se encuentra actualmente en preparación.

La selección coincidió con la esperada y la respuesta conservó
el identificador y el estado consultado.

### Caso combinado

Entrada:

> ¿Cuántas unidades de leche quedan y cuál es el estado del pedido P-302? Consulta los datos ficticios disponibles.

Traza observada:

1. `consultar_stock`, con `{"producto": "leche"}`.
   Observación: `Stock ficticio de leche: 8 unidades.`
2. `consultar_estado_pedido`, con `{"pedido_id": "P-302"}`.
   Observación: `Estado ficticio de P-302: despachado.`

Respuesta completa:

> Quedan 8 unidades de leche y el pedido P-302 está despachado.

Utilizó ambas herramientas y conservó los dos resultados.
Las consultas son independientes, por lo que no se exige
un orden determinado para futuras ejecuciones.

### Caso saludo

Entrada:

> Hola, buenos días.

No hubo acciones intermedias: `intermediate_steps` quedó vacío.

Respuesta completa:

> ¡Hola! Buenos días, ¿en qué puedo ayudarte hoy?

Respondió directamente sin utilizar herramientas.

## Presentación de la salida

En la ejecución observada, `output` contenía bloques de texto
con metadatos. Las respuestas anteriores transcriben íntegramente
su texto visible.

Después se añadió `extraer_texto_agente` para obtener ese texto
mediante `AIMessage` y `StrOutputParser`, tanto si la salida original
es texto como si contiene bloques. La extracción se comprobó
localmente, sin repetir las consultas reales.

La traza automática de `verbose=True` puede seguir mostrando
la estructura original.

## Verificación y límites

Los cuatro casos observados seleccionaron las herramientas esperadas.
Se revisaron los argumentos, las observaciones y las respuestas completas.

Esto verifica estas entradas concretas, no garantiza la elección
correcta ante cualquier mensaje.

La traza muestra acciones y observaciones; no expone todo el
razonamiento interno del modelo. Tampoco permite deducir por sí sola
el consumo de tokens o el costo de la ejecución.

`agent_scratchpad` conserva información intermedia de una ejecución;
no se implementó memoria persistente entre consultas.

Los errores no controlados por una herramienta se registran
en la ejecución principal y se continúa con el siguiente caso.
El límite de iteraciones puede detener al agente antes de resolver
una entrada.

El agente consulta datos ficticios y redacta respuestas.
No modifica stock, no despacha pedidos y no envía mensajes externos.

Las pruebas de regresión del proyecto pueden ejecutarse sin Gemini:

```powershell
python -m pytest tests -q
```

La elección real de herramientas de este bloque se verificó mediante
las cuatro ejecuciones manuales anteriores.