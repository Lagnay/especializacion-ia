from unittest.mock import Mock, patch

from src.cliente import consultar_modelo


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


if __name__ == "__main__":
    escenarios = [
        ("ÉXITO INMEDIATO", "Hola", [200]),
        ("RECUPERACIÓN", "Hola", [503, 429, 200]),
        ("INTENTOS AGOTADOS", "Hola", [503, 503, 503]),
        ("CREDENCIAL", "Hola", [401, 200]),
        ("PERMISOS", "Hola", [403, 200]),
        ("PREGUNTA VACÍA", "   ", [200]),
        ("PREGUNTA NO TEXTUAL", 42, [200]),
    ]

    for nombre, pregunta, codigos in escenarios:
        print(f"\n=== {nombre} ===")

        respuestas = []

        for codigo in codigos:
            respuestas.append(
                crear_respuesta_simulada(codigo)
            )

        with patch(
            "requests.post",
            side_effect=respuestas,
        ) as post_simulado:
            try:
                texto = consultar_modelo(
                    pregunta,
                    system_instruction=(
                        "Responde brevemente en español."
                    ),
                )
                print("Texto:", texto)

            except (TypeError, ValueError) as error:
                print("Error de entrada o configuración:", error)

            except RuntimeError as error:
                print("No se pudo completar la consulta:", error)

            print("Peticiones realizadas:", post_simulado.call_count)

    print("\nEl programa llegó al final.")