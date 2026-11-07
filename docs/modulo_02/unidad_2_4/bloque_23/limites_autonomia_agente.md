# Límites de autonomía del agente supervisado

## Alcance

El agente consulta existencias y pedidos ficticios, conserva contexto
durante la ejecución y permite simular un reembolso sujeto
a aprobación humana.

No transfiere dinero ni modifica pedidos o inventario.
Las respuestas del modelo se apoyan en herramientas locales,
pero siguen requiriendo revisión cuando corresponda.

## Herramientas y nivel de riesgo

| Herramienta | Riesgo y justificación |
| --- | --- |
| `consultar_stock` | Bajo: consulta existencias ficticias, sin modificarlas. |
| `consultar_pedido_con_historial` | Bajo: consulta el estado y, opcionalmente, el historial de un pedido ficticio. |
| `simular_reembolso` | Simula una operación económica de riesgo alto. En esta implementación no mueve dinero; su escritura efectiva es un registro local reversible. |

La simulación no se presenta como un reembolso real. Si se conectara
a un sistema de pagos, sería necesario revisar nuevamente su riesgo,
permisos y controles antes de habilitarla.

## Herramientas que requieren aprobación humana

`simular_reembolso` exige aprobación explícita para practicar
el control previo que requeriría una operación económica.

La comprobación está dentro de la herramienta. Las instrucciones
del prompt orientan al modelo, pero no conceden autorización.

Controles implementados:

- Monto obligatorio, entero estricto y mayor que cero.
- Presentación del pedido y del monto antes de decidir.
- Plazo de 30 segundos en la herramienta integrada.
- Solo una respuesta afirmativa permite devolver el estado `simulado`.
- Rechazo, tiempo agotado o ausencia de terminal interactiva
  producen una decisión no aprobada.
- Registro de la decisión antes de devolver el resultado.
- Si falla la escritura del registro, la herramienta propaga el error
  y no devuelve una confirmación de simulación aprobada.

No se aplica aprobación a las consultas de stock y pedidos.

La consola es una demostración local: no autentica al supervisor.
El registro conserva qué se decidió y cuándo, pero no acredita
la identidad de una persona.

El rechazo explícito y el tiempo agotado se guardan actualmente
como `aprobado: false`; el archivo no distingue ambos motivos.

## Adaptación para Windows, Linux y macOS

Se amplió el ejemplo de la guía para contemplar diferentes sistemas:

- Windows: `msvcrt`, lectura de una tecla sin Enter y comprobación
  del plazo mediante `monotonic`.
- Linux/macOS: `select` sobre la terminal, con respuesta seguida
  de Enter y descarte de entradas pendientes mediante `termios`.

Los imports específicos se realizan dentro de la rama correspondiente.
Se utilizan exclusivamente dependencias ya instaladas y módulos
de la biblioteca estándar.

La implementación fue comprobada en Windows.
Las ramas de Linux y macOS están pendientes de ejecución
en esos sistemas; no se afirma compatibilidad verificada en ellos.

## Trazas y decisiones guardadas

- [Trazas del agente](trazas_agente.jsonl): entrada, sesión,
  modelo configurado, llamadas, argumentos, observaciones,
  estado técnico y respuesta final.
- [Decisiones de aprobación](aprobaciones.jsonl): argumentos,
  decisión y momento, guardados dentro de la herramienta.
- [Trazas de la práctica directa](trazas_supervision.jsonl):
  ejercicios sin intervención del modelo.

Cada línea es un objeto JSON independiente, escrito en UTF-8.
Las nuevas ejecuciones añaden registros sin sustituir los anteriores.

Las solicitudes y resultados de herramientas se relacionan mediante
el identificador de llamada. El listado de acciones no pretende
medir el orden temporal exacto de ejecuciones paralelas.

La traza del agente se escribe al completar la interacción.
Un fallo de conexión puede impedir que se genere esa traza.
Si una herramienta ya guardó una aprobación antes de un fallo posterior,
su decisión permanece en el archivo de aprobaciones.

`success` indica que la herramienta terminó correctamente;
no significa que el reembolso haya sido autorizado.

## Revisión de trazas

Frecuencia propuesta:

- Revisar cada invocación de la herramienta de reembolso simulado.
- Revisar una muestra semanal de consultas de solo lectura
  si el agente continúa utilizándose.
- Revisar inmediatamente cualquier ejecución con errores
  o resultados inesperados.

Comprobar:

- Correspondencia entre solicitud, herramienta y argumentos.
- Existencia y valor de la aprobación del reembolso.
- Correspondencia entre observación y respuesta final.
- Ausencia de afirmaciones sobre transferencias reales.
- Ausencia de nuevos intentos autónomos después de un rechazo.
- Repeticiones consecutivas de herramientas que puedan ser innecesarias.

El detector compara nombres de herramientas dentro de una interacción.
No compara argumentos ni decide si la repetición es incorrecta.
Una traza sin repeticiones tampoco garantiza una respuesta correcta.

## Qué hacer ante un comportamiento inesperado

1. Detener nuevas ejecuciones y conservar los registros disponibles.
2. Si afecta al reembolso, retirarlo temporalmente de la lista
   de herramientas del constructor.
3. Revisar entrada, argumentos, aprobación, observación y respuesta;
   identificar en qué etapa ocurrió el problema.
4. Corregir según la causa: validación, comprobación de aprobación,
   descripción de herramienta, prompt o manejo de errores.
5. Incorporar una prueba simulada que reproduzca el fallo y ejecutar
   las pruebas antes de habilitar nuevamente la herramienta.
6. Realizar una comprobación controlada y documentar el resultado.

Ante un fallo de conexión, revisar la conectividad antes de repetir
consultas. No interpretar ese fallo como una aprobación o un rechazo.

## Evaluación real observada

Modelo configurado: `gemini-3.5-flash-lite`.

Al cierre de esta evaluación quedaron cinco interacciones completadas:

1. Stock de arroz: una llamada a `consultar_stock`; informó 12 unidades.
2. Reembolso aprobado: `aprobado: true`; informó simulación sin mover dinero.
3. Reembolso rechazado: `aprobado: false`; informó que no se ejecutó.
4. Segunda aprobación: confirmó nuevamente la simulación sin mover dinero.
5. Tiempo agotado: `aprobado: false`; informó que no se ejecutó.

Las respuestas completas y sus argumentos se conservan
en las trazas enlazadas. La revisión no detectó repeticiones
consecutivas en las cinco interacciones.

El tiempo agotado se identificó por la salida de consola
«Tiempo agotado: acción no aprobada», no por un motivo específico
dentro del registro.

También se observó un `httpx.ConnectError` con `WinError 10013`
antes de solicitar aprobación. Ese intento no produjo una interacción
completada ni una decisión de aprobación. Un intento posterior funcionó,
sin que se determinara la causa concreta del fallo anterior.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo
y las dependencias instaladas:

```powershell
python -m src.agente_supervisado
```

Muestra el modo de preparación y no realiza consultas.

Con `GEMINI_API_KEY` configurada en `.env`:

```powershell
python -m src.agente_supervisado --ejecutar --caso stock
python -m src.agente_supervisado --ejecutar --caso reembolso
```

Ejecutar los comandos por separado. Consumen cuota de Gemini.
Para comprobar aprobación y rechazo, ejecutar el caso de reembolso
una vez por decisión. Cada comando inicia una conversación nueva.

Revisión local de las trazas:

```powershell
python -c "from pathlib import Path; from src.trazas_agente import revisar_trazas; revisar_trazas(Path('docs/modulo_02/unidad_2_4/bloque_23/trazas_agente.jsonl'))"
```

## Pruebas y límites pendientes

Se observaron 10 casos pasados en `tests/test_agente_supervisado.py`.
El conjunto completo alcanzó 79 casos pasados.

Las pruebas utilizan un modelo y aprobaciones simulados, y escriben
en carpetas temporales. Comprueban autorización, validación de montos,
persistencia de la decisión, fallo de escritura, integración
y extracción de acciones.

No prueban la elección autónoma de Gemini ni ejecutan
las ramas de terminal de otros sistemas operativos.

La memoria del agente permanece en el proceso y no se recupera
entre ejecuciones. Esta demostración no implementa autenticación,
protección contra modificación de registros ni coordinación
de múltiples solicitudes simultáneas de aprobación.