import requests
from unittest.mock import Mock, patch

from src.consumir_gemini import extraer_texto
from src.practicas.practica_clasificacion_errores import (
    clasificar_estado,
)


def enviar_peticion_clasificada(url, headers, body):
    try:
        respuesta_http = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30,
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ) as error:
        raise TimeoutError(
            "No se pudo completar la conexión con el proveedor."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            "Ocurrió otro problema al enviar la petición."
        ) from error

    clasificar_estado(respuesta_http.status_code)

    try:
        return respuesta_http.json()

    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del proveedor no contiene JSON válido."
        ) from error


if __name__ == "__main__":
    datos_simulados = {
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

    for codigo in (
        200, 201,
        401, 403,
        429,
        500, 502, 503, 504,
        400, 404,
    ):
        print(f"\nProbando HTTP {codigo}")

        respuesta_simulada = Mock(status_code=codigo)
        respuesta_simulada.json.return_value = datos_simulados

        with patch(
            "requests.post",
            return_value=respuesta_simulada,
        ):
            try:
                datos = enviar_peticion_clasificada(
                    "https://ejemplo.invalid",
                    {},
                    {},
                )
                print("Texto:", extraer_texto(datos))

            except ValueError as error:
                print("Sin reintento automático:", error)

            except TimeoutError as error:
                print("Candidato a reintento:", error)

            except RuntimeError as error:
                print("Requiere revisión:", error)

    print("\nEl programa llegó al final.")