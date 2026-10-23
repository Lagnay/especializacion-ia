from unittest.mock import Mock, patch

from src.consumir_gemini import extraer_texto
from src.practicas.practica_envio_clasificado import (
    enviar_peticion_clasificada,
)
from src.practicas.practica_reintento_reutilizable import (
    con_reintento,
)


def crear_respuesta_simulada(codigo):
    respuesta = Mock(status_code=codigo)

    respuesta.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Respuesta simulada recibida."}
                    ]
                }
            }
        ]
    }

    return respuesta


def hacer_consulta():
    return enviar_peticion_clasificada(
        "https://ejemplo.invalid",
        {},
        {},
    )


if __name__ == "__main__":
    escenarios = [
        ("ÉXITO INMEDIATO", [200]),
        ("RECUPERACIÓN", [503, 429, 200]),
        ("FALLO PERSISTENTE DEL PROVEEDOR", [503, 503, 503]),
        ("LÍMITE PERSISTENTE", [429, 429, 429]),
        ("CREDENCIAL", [401, 200]),
        ("PERMISOS", [403, 200]),
        ("PETICIÓN INCORRECTA", [400, 200]),
        ("RECURSO NO ENCONTRADO", [404, 200]),
    ]

    for nombre, codigos in escenarios:
        print(f"\n=== {nombre} ===")

        respuestas = []

        for codigo in codigos:
            respuesta = crear_respuesta_simulada(codigo)
            respuestas.append(respuesta)

        with patch(
            "requests.post",
            side_effect=respuestas,
        ) as post_simulado:
            try:
                datos = con_reintento(
                    hacer_consulta,
                    intentos=3,
                    espera_segundos=1,
                )

                print("Texto:", extraer_texto(datos))

            except ValueError as error:
                print("Error sin reintento automático:", error)

            except TimeoutError as error:
                print("Intentos agotados:", error)

            except RuntimeError as error:
                print("Error que requiere revisión:", error)

            print("Peticiones realizadas:", post_simulado.call_count)

    print("\nEl programa llegó al final.")