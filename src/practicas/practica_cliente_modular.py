from unittest.mock import patch

from src.consumir_gemini import armar_peticion, extraer_texto
from src.practicas.practica_envio_clasificado import (
    enviar_peticion_clasificada,
)
from src.practicas.practica_reintento_reutilizable import (
    con_reintento,
)
from src.practicas.practica_envio_con_reintento import (
    crear_respuesta_simulada,
)


def consultar_modelo(pregunta, system_instruction=None):
    url, headers, body = armar_peticion(
        pregunta,
        system_instruction=system_instruction,
    )

    try:
        datos = con_reintento(
            lambda: enviar_peticion_clasificada(
                url,
                headers,
                body,
            )
        )

    except TimeoutError as error:
        raise RuntimeError(
            "El servicio no pudo completar la consulta "
            "tras varios intentos. Intenta más tarde."
        ) from error

    return extraer_texto(datos)


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