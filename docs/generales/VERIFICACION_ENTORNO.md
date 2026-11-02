# Verificación de reconstrucción del entorno

## Entorno y versión revisada

| Dato | Valor |
| --- | --- |
| Fecha | 11 de octubre de 2026 |
| Repositorio | https://github.com/Lagnay/especializacion-ia |
| Commit de dependencias | `eca92a9c3efca3ad3038225a8892bd38c9801863` |
| Sistema | Windows, PowerShell |
| Python | 3.14.7 |
| Método | Comprobación local automatizada con asistencia de IA |

## Procedimiento

1. Obtener una copia nueva del repositorio publicado.
2. Crear un entorno virtual vacío, separado del entorno original.
3. Instalar los requisitos del commit revisado mediante `python -m pip install -r requirements.txt`, utilizando el Python del entorno nuevo.
4. Comprobar el ejecutable, la consistencia de dependencias y las importaciones principales.

No se copiaron el entorno original ni su configuración local. Para ejecutar los comandos se utilizó la ruta al Python del entorno nuevo, sin activarlo en la terminal.

## Resultados

| Comprobación | Resultado |
| --- | --- |
| Instalación de los 26 paquetes registrados | Correcta |
| Python dentro del entorno nuevo | Confirmado |
| `sys.prefix != sys.base_prefix` | `True` |
| `pip check` | `No broken requirements found.` |
| Importación de requests, google.genai y load_dotenv desde dotenv | `Importaciones OK` |

## Alcance

La prueba acredita la reconstrucción de las dependencias en el sistema indicado. Se aprovechó la caché local de paquetes de pip; no se comprobó su descarga completa sin caché. No se probaron otros sistemas operativos ni solicitudes autenticadas al proveedor.

La revisión se realizó en el mismo computador, sin participación de otro revisor. Las instrucciones de instalación del README se redactaron después de esta prueba; no han sido seguidas por un lector independiente.
