# Gate 2 — Ensayo de instalación limpia

Fecha: 16 de noviembre de 2026.

## Entorno y copia

- Sistema: Windows, PowerShell.
- Python: 3.14.7.
- Carpeta: `C:\Users\Dell\AppData\Local\Temp\gate2-limpio-2nu1modi`.
- Código: subcarpeta `repositorio`.
- Entorno nuevo: subcarpeta `venv`.
- `include-system-site-packages = false`.

La copia se preparó con los archivos versionables del trabajo actual, incluidos los cambios pendientes. No incluyó `.git`, `.env`, el entorno original, los índices ni los estados de supervisión.

Se utilizó directamente el ejecutable del entorno nuevo. También se comprobó que `src.servicio_rag` se importara desde la copia.

## Procedimiento y resultados

1. Se creó la copia en una carpeta temporal.
2. Se inició la creación del entorno virtual. La primera ejecución se interrumpió manualmente durante `ensurepip`, con `KeyboardInterrupt`.
3. Se repitió la creación del entorno y se instalaron las dependencias mediante `requirements.txt`.
4. La instalación terminó con `Successfully installed` y aprovechó la caché local de pip.
5. `pip check` devolvió `No broken requirements found.`
6. La suite terminó con **277 passed, 2 warnings**, en 70.26 segundos.
7. El ejecutable mostró correctamente el modo de preparación.
8. Se revisó y aprobó el prompt en la copia, creando su propia base de supervisión.
9. Se ejecutó una consulta simulada, que creó su propio índice de seis fragmentos.
10. La consulta devolvió una respuesta con fuente y registró sus etapas.

La interrupción inicial fue una cancelación del proceso; no se identificó como incompatibilidad de dependencias.

## Consulta simulada en la copia

| Dato | Resultado |
|---|---|
| Solicitud | `gate2-prompt-01`, aprobada en la copia |
| `trace_id` | `trace-0bf6c1572da54768944ba17414f6c6f5` |
| Colección | `simulado-8a8308d68a5fd321` |
| Estado del índice | Creado |
| Fragmentos / dimensiones | 6 / 16 |
| Respuesta | El cliente REST permite hasta tres intentos por consulta [5]. |
| Fuente | `src/cliente.py` |
| Recuperación | 142.3610 ms |
| Generación simulada | 1.0124 ms |
| Total de consulta mostrado | 350.64 ms |
| Consumo / costo | No informado / N/D |

El registro quedó en la carpeta de documentación de la copia. No se añadió esta consulta al JSONL del repositorio original.

## Alcance

Se comprobó la instalación de dependencias, la suite y el arranque del flujo simulado sin reutilizar índices o aprobaciones del entorno original.

No se copió la credencial ni se realizaron consultas a Gemini durante este ensayo. La corrida real se documenta por separado en el [informe del Gate 2](GATE2_INTEGRACION_Y_ORQUESTACION.md).

El ensayo se realizó en el mismo computador y aprovechó la caché de pip. No verifica una descarga completa sin caché, otro sistema operativo ni otro equipo.

Se probó una copia del trabajo en preparación, no un clon del commit final publicado. El commit de entrega se identificará al publicar la versión revisada.