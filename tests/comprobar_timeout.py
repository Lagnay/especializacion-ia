from unittest.mock import patch

import requests

from src.consumir_gemini import obtener_dato_de_prueba


mensaje_esperado = (
    "El servicio no respondió dentro del tiempo de espera."
)

with patch(
    "src.consumir_gemini.requests.post",
    side_effect=requests.exceptions.Timeout(
        "Tiempo de espera agotado durante la prueba."
    )
):
    try:
        obtener_dato_de_prueba("¿Cuál es la capital de Escocia?")
    except RuntimeError as error:
        assert str(error) == mensaje_esperado, (
            "El mensaje recibido no coincide con el esperado."
        )
        print("Prueba correcta:", error)
    else:
        raise AssertionError(
            "El módulo no comunicó el fallo de tiempo de espera."
        )

print("La prueba terminó.")