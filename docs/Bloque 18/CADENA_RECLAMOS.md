# Bloque 18 — Cadena de tres etapas con LangChain

Autor: Slaven Matkovic Baricic.

## Objetivo y funcionamiento

Implementé una cadena que transforma un mensaje de reclamo en un
borrador de respuesta mediante tres etapas:

1. Analizar los hechos informados, las solicitudes, las preferencias
   y el estado de verificación.
2. Preparar un plan interno de atención.
3. Redactar un borrador contrastando el plan con el mensaje original.

Utilicé un caso ficticio de atención de pedidos con retraso,
un producto faltante y una solicitud de factura.

Cada etapa tiene su propio `PromptTemplate` y utiliza el modelo
seguido de `StrOutputParser`.

Las etapas se conectan mediante `|`. `RunnablePassthrough.assign`
conserva el mensaje original y añade el análisis y el plan.

El segundo paso utiliza el análisis del primero. El tercero recibe
el plan y el mensaje original. Por tanto, las llamadas dependen
de los resultados anteriores.

## Archivos y reproducción

- Módulo: `src/cadena_reclamos.py`.
- Prueba: `tests/test_cadena_reclamos.py`.
- Prácticas conservadas: `src/practicas/`.
- Dependencias y versiones: `requirements.txt`.

La función `construir_cadena(modelo)` recibe el modelo y devuelve
la cadena sin ejecutarla. Esto permite sustituir el modelo real
por uno simulado durante las pruebas.

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y `GEMINI_API_KEY` configurada en `.env`:

```powershell
python -m src.cadena_reclamos
```

El ejemplo utiliza `gemini-3.5-flash-lite`, con timeout configurado
en 30 segundos por solicitud y reintentos automáticos desactivados.

Una ejecución completa exitosa realiza tres consultas al modelo.
Muestra el borrador en la terminal; no envía mensajes al cliente
ni registra el reclamo en un sistema de atención.

## Entrada utilizada

```text
El lunes hice el pedido P-104 con cuatro paquetes de arroz y dos
cartones de leche. La entrega estaba programada para el martes
entre las 16 y las 18, pero llegó el miércoles a las 11. Recibí
los cuatro paquetes de arroz y solamente un cartón de leche.
Los productos recibidos están en buen estado. Según mi comprobante,
pagué el pedido completo. Escribí a soporte el miércoles y todavía
no recibo respuesta. Necesito que revisen la leche faltante y que
me envíen la factura por correo. Prefiero recibir el producto
faltante antes que un reembolso. Puedo recibir entregas entre
las 18 y las 20, pero necesito que me confirmen antes. Prefiero
que me contacten por escrito.
```

## Resultado completo de la ejecución

Comando:

```powershell
python -m src.cadena_reclamos
```

Salida:

```text
=== BORRADOR PARA REVISIÓN ===
Estimado/a cliente,

Muchas gracias por ponerse en contacto con nosotros y por escribirnos por este medio. Lamentamos la falta de respuesta a su mensaje del miércoles y los inconvenientes presentados con su pedido P-104.

Hemos tomado nota de su reporte sobre la entrega recibida el miércoles, en la cual constata que recibió los cuatro paquetes de arroz en buen estado, pero únicamente un cartón de leche de los dos solicitados. Asimismo, registramos su solicitud de revisión respecto al cartón de leche faltante y el envío de su factura por correo electrónico, así como su preferencia por recibir el producto en lugar de un reembolso.

Tomamos en cuenta que su disponibilidad para recibir entregas es de 18:00 a 20:00 previa confirmación, y que prefiere que nos comuniquemos con usted por escrito.

Para poder avanzar con una solución, necesitamos verificar internamente los registros de despacho, inventario y facturación, así como contrastar la información sobre el pago y el estado de su pedido.

Nos pondremos en contacto con usted por este medio en cuanto hayamos completado las verificaciones necesarias para informarle los pasos siguientes.

Atentamente,
El equipo de atención al cliente
```

## Revisión del contenido

| Criterio | Observación |
| --- | --- |
| Identificar el pedido y el faltante | Cumple: menciona P-104 y el cartón de leche faltante. |
| Reconocer el retraso | Parcial: menciona la entrega del miércoles, pero no explicita que estaba prevista para el martes. |
| Incluir la solicitud de factura | Cumple. |
| Conservar las preferencias | Cumple: producto antes que reembolso, contacto escrito y disponibilidad de 18 a 20 con confirmación previa. |
| Evitar gestiones presentadas como realizadas | No cumple completamente: dice «registramos su solicitud», aunque el programa no realiza ese registro. |
| Evitar compromisos sin respaldo operativo | Añade un compromiso de contacto futuro que el programa no ejecuta. |

La cadena completó las tres etapas, pero el borrador requiere
revisión humana. Las instrucciones no garantizan por sí solas
que el modelo conserve todos los detalles o evite todas las
afirmaciones sin respaldo.

## Pruebas realizadas

Prueba específica:

```powershell
python -m pytest tests/test_cadena_reclamos.py -v
```

Resultado: una prueba pasada.

Comprueba que:

- Construir la cadena no llama al modelo.
- Ejecutarla realiza tres llamadas simuladas.
- El primer paso recibe el mensaje.
- El segundo recibe el análisis.
- El tercero recibe el mensaje original y el plan.
- La salida corresponde al texto de la tercera respuesta simulada.

Se utilizan `MagicMock` y respuestas `AIMessage`.
Estas pruebas verifican las conexiones, no la calidad del texto
generado por Gemini.

Pruebas completas:

```powershell
python -m pytest tests -v
```

Resultado observado: 40 pruebas pasadas y una advertencia.

Comprobación de dependencias:

```powershell
python -m pip check
```

Resultado:

```text
No broken requirements found.
```

## Entorno y límites

Entorno comprobado: Windows, Python 3.14.7 y pytest 9.1.1.

Versiones utilizadas:

- langchain: 1.4.7.
- langchain-core: 1.7.3.
- langchain-google-genai: 4.4.2.
- google-genai: 2.29.0.

Durante las pruebas apareció un `DeprecationWarning` procedente
de `google/genai/types.py`, relacionado con `_UnionGenericAlias`.
No impidió que las pruebas pasaran.

Esta cadena utiliza directamente la integración de LangChain.
No incorpora el registro de costos ni la política de reintentos
de `src/cliente.py`.

Las respuestas pueden variar entre ejecuciones. La ejecución
documentada corresponde a un caso; no demuestra fiabilidad general.