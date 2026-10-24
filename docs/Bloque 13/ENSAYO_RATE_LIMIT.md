# Bloque 13 — Ensayo de consultas y límites de uso

## Objetivo

Comprobar el cliente con consultas reales, observar los estados
HTTP y registrar el costo acumulado de referencia. Intentar
observar un HTTP 429 para comprobar los reintentos en ese caso.

## Configuración

Esta configuración corresponde al primer ensayo secuencial
de diez consultas. Las ampliaciones posteriores se describen
más adelante.

- Fecha: 23-10-2026.
- Modelo: gemini-3.5-flash-lite.
- Máximo de consultas del ensayo: 10.
- Máximo de intentos por consulta: 3.
- Backoff exponencial con base de 2 segundos, jitter de hasta
  un 10 % adicional y límite final de 30 segundos por pausa.
- Tarifas de referencia del laboratorio fechadas el 16-10-2026.
- Credencial cargada desde `.env`, excluido de Git.

## Ejecución

Desde la raíz del repositorio, con el entorno virtual activo:

```powershell
python -m src.practicas.practica_ensayo_rate_limit
```

Este comando realiza consultas reales y consume cuota del proveedor.

## Resultado observado

- Consultas completadas: 10 de 10.
- Estados HTTP: 200 en las diez consultas.
- Reintentos observados: ninguno.
- HTTP 429 observado: no.
- Respuestas generadas: `OK` u `OK.`
- Costo acumulado de referencia: 0.000071800 USD.

El importe es una estimación a las tarifas de referencia
configuradas, no una confirmación de cargos.

## Alcance y limitación

El ensayo confirma la conexión real y la acumulación del costo
estimado de las respuestas recibidas.

Este primer ensayo no permitió observar un HTTP 429 ni una
recuperación posterior a ese estado. La búsqueda del límite
continuó con las ampliaciones documentadas más adelante.

La recuperación, el agotamiento de intentos y la ausencia de
reintentos ante errores de entrada o estados HTTP 401 y 403
se comprobaron por separado con respuestas simuladas mediante:

```powershell
python -m tests.comprobar_cliente
```

## Salida de terminal

```
=== CONSULTA 1 ===
Costo de referencia de la operación: 0.000008900 USD
Acumulado de la sesión: 0.000008900 USD
Respuesta: OK.
Estados HTTP observados: [200]

=== CONSULTA 2 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000015300 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 3 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000021700 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 4 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000028100 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 5 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000034500 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 6 ===
Costo de referencia de la operación: 0.000008900 USD
Acumulado de la sesión: 0.000043400 USD
Respuesta: OK.
Estados HTTP observados: [200]

=== CONSULTA 7 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000049800 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 8 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000056200 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 9 ===
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000062600 USD
Respuesta: OK
Estados HTTP observados: [200]

=== CONSULTA 10 ===
Costo de referencia de la operación: 0.000009200 USD
Acumulado de la sesión: 0.000071800 USD
Respuesta: OK.
Estados HTTP observados: [200]

No se observó un HTTP 429 en este ensayo.

Costo acumulado de referencia: 0.000071800 USD
El ensayo llegó al final.
```

## Ampliación del ensayo: consultas concurrentes

### Motivo y preparación

El primer ensayo de diez consultas secuenciales terminó
únicamente con respuestas HTTP 200. Posteriormente amplié
el envío secuencial a dieciséis consultas, también sin
observar un HTTP 429.

Revisé los límites publicados para mi proyecto y modelo
en Google AI Studio. El panel indicaba un límite de
15 solicitudes por minuto para Gemini 3.5 Flash Lite.

Como las consultas secuenciales esperaban la respuesta
anterior antes de iniciar la siguiente, aumentar solamente
su cantidad no aseguraba concentrarlas en una misma ventana
de uso. No medí la duración de aquellos ensayos, por lo
que no puedo confirmar que esa fuera la causa de no
observar el límite.

Para concentrar las solicitudes y medir el resultado,
creé una práctica adicional con concurrencia limitada.

### Configuración del ensayo concurrente

- Fecha: 23-10-2026.
- Modelo: gemini-3.5-flash-lite.
- Script: `src/practicas/practica_ensayo_concurrente.py`.
- Máximo de peticiones: 20.
- Máximo de peticiones simultáneas: 5.
- Organización: cuatro lotes de cinco peticiones.
- Cada lote comienza cuando termina el anterior,
  sin añadir una pausa.
- Cada petición se envía una sola vez, sin reintentos
  automáticos en este script.
- Los tiempos se miden con `time.perf_counter()`.
- Los costos se registran desde el hilo principal.
- Si aparece un HTTP 429, se termina de procesar el
  lote en curso y no se inician lotes adicionales.

### Ejecución

Desde la raíz del repositorio, con el entorno virtual activo:

```powershell
python -m src.practicas.practica_ensayo_concurrente
```

Este comando realiza peticiones reales y consume cuota
del proveedor.

### Resultados observados

- Peticiones intentadas: 20.
- Respuestas HTTP 200: 17.
- Respuestas HTTP 429: 3.
- Consultas identificadas con HTTP 429: 16, 19 y 20.
- Errores de transporte: 0.
- Duración total: 21.442 segundos.
- Encabezado `Retry-After` en las respuestas 429:
  no informado.
- Costo acumulado de referencia: 0.000121200 USD.

Los resultados se muestran por número de consulta;
no representan necesariamente el orden de llegada
de las respuestas.

### Alcance de la comprobación

Este ensayo permitió observar tres respuestas HTTP 429
reales del proveedor al concentrar veinte peticiones
en aproximadamente veintiún segundos.

El objetivo de este script fue observar y registrar
el límite de uso. No ejecuta el mecanismo de reintento
del cliente, por lo que esta salida no demuestra una
recuperación real mediante backoff después de un 429.

La clasificación, la recuperación simulada y el
agotamiento de intentos se comprobaron por separado
mediante `python -m tests.comprobar_cliente`.

El costo registrado corresponde a la estimación obtenida
de los metadatos de las respuestas HTTP 200 procesadas.
No representa una factura ni permite concluir que
cualquier petición fallida tenga necesariamente costo cero.

### Salida de terminal del ensayo concurrente

```
=== LOTE: CONSULTAS 1 A 5 ===
Consulta 1: HTTP 200; tiempo: 4.219 s
Costo de referencia de la operación: 0.000008900 USD
Acumulado de la sesión: 0.000008900 USD
Respuesta: OK.
Consulta 2: HTTP 200; tiempo: 5.188 s
Costo de referencia de la operación: 0.000008900 USD
Acumulado de la sesión: 0.000017800 USD
Respuesta: OK.
Consulta 3: HTTP 200; tiempo: 5.148 s
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000024200 USD
Respuesta: OK
Consulta 4: HTTP 200; tiempo: 4.932 s
Costo de referencia de la operación: 0.000008900 USD
Acumulado de la sesión: 0.000033100 USD
Respuesta: OK.
Consulta 5: HTTP 200; tiempo: 5.415 s
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000039500 USD
Respuesta: OK

=== LOTE: CONSULTAS 6 A 10 ===
Consulta 6: HTTP 200; tiempo: 3.923 s
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000045900 USD
Respuesta: OK
Consulta 7: HTTP 200; tiempo: 4.620 s
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000052300 USD
Respuesta: OK
Consulta 8: HTTP 200; tiempo: 3.859 s
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000058700 USD
Respuesta: OK
Consulta 9: HTTP 200; tiempo: 5.057 s
Costo de referencia de la operación: 0.000006400 USD
Acumulado de la sesión: 0.000065100 USD
Respuesta: OK
Consulta 10: HTTP 200; tiempo: 4.530 s
Costo de referencia de la operación: 0.000009200 USD
Acumulado de la sesión: 0.000074300 USD
Respuesta: OK.

=== LOTE: CONSULTAS 11 A 15 ===
Consulta 11: HTTP 200; tiempo: 2.672 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000081000 USD
Respuesta: OK
Consulta 12: HTTP 200; tiempo: 5.161 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000087700 USD
Respuesta: OK
Consulta 13: HTTP 200; tiempo: 5.006 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000094400 USD
Respuesta: OK
Consulta 14: HTTP 200; tiempo: 4.948 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000101100 USD
Respuesta: OK
Consulta 15: HTTP 200; tiempo: 4.633 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000107800 USD
Respuesta: OK

=== LOTE: CONSULTAS 16 A 20 ===
Consulta 16: HTTP 429; tiempo: 1.325 s
Retry-After: No informado
Consulta 17: HTTP 200; tiempo: 4.370 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000114500 USD
Respuesta: OK
Consulta 18: HTTP 200; tiempo: 5.781 s
Costo de referencia de la operación: 0.000006700 USD
Acumulado de la sesión: 0.000121200 USD
Respuesta: OK
Consulta 19: HTTP 429; tiempo: 1.327 s
Retry-After: No informado
Consulta 20: HTTP 429; tiempo: 1.326 s
Retry-After: No informado
HTTP 429 observado; no se iniciarán más lotes.

=== RESUMEN ===
Peticiones intentadas: 20
Estados HTTP: [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 429, 200, 200, 429, 429]
Respuestas HTTP 429: 3
Errores de transporte: 0
Duración total: 21.442 segundos
Costo acumulado de referencia: 0.000121200 USD
El ensayo llegó al final.
```