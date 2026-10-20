from unittest.mock import Mock, patch

import requests

from src.consumir_gemini import enviar_peticion


respuesta_simulada = Mock()
respuesta_simulada.status_code = 200
respuesta_simulada.raise_for_status.return_value = None

respuesta_simulada.json.side_effect = (
    requests.exceptions.JSONDecodeError(
        "Contenido no válido",
        "<html>Hola</html>",
        0
    )
)

with patch(
    "src.consumir_gemini.requests.post",
    return_value=respuesta_simulada
):
    try:
        enviar_peticion("https://ejemplo.invalid", {}, {})
    except RuntimeError as error:
        print("Error detectado:", error)
    else:
        print("ATENCIÓN: no se detectó el fallo esperado.")

print("La prueba terminó.")